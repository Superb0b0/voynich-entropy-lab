#!/usr/bin/env python3
"""COMPAT-014-01-A1 technical parser comparison; aggregate output only."""
import argparse
import collections
import csv
import hashlib
import importlib.util
import json
import re
from pathlib import Path

INPUT_SHA = "dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9"
RC12_SHA = "8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5"
M2_SHA = "c522868b488707d8fe87e5a1d78683e29de28e9663c6eb1144d232f773e0118e"
M2_COMMIT = "c27a149313ed6d809ec30f9e384011b21b299c63"
P_TAGS = {"*P0", "*Pb", "+P0", "+P1", "+Pb", "+Pc", "+Pr", "=P0", "=Pt", "@P0", "@P1", "@Pb"}
CLASSES = ["qo", "ch", "sh", "d", "o", "y", "s"]
PAGE_M2 = re.compile(r"^<(f\d+[rv]\d*)>")
LINE_M2 = re.compile(r"^<(f\d+[rv]\d*)\.(\d+),([^>]*)>\s*(.*)")
HEADER = re.compile(r"^<([^>]+)>\s*(.*)$")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def word_class(word):
    for i, prefix in enumerate(CLASSES):
        if word.startswith(prefix):
            return i
    return 7


def canonical_keyed(records):
    totals = collections.Counter(r["locus_id"] for r in records)
    seen = collections.Counter()
    out = []
    for r in records:
        lid = r["locus_id"]
        seen[lid] += 1
        key = lid if totals[lid] == 1 else f"{lid}#occurrence={seen[lid]}"
        out.append((key, r))
    return out, {k: n for k, n in totals.items() if n > 1}


def audit(input_path: Path, parser_path: Path, m2_path: Path, private_csv: Path):
    raw = input_path.read_bytes()
    input_sha = sha(raw)
    if input_sha != INPUT_SHA:
        raise SystemExit(f"FAIL CLOSED input SHA mismatch: {input_sha}")
    if sha(parser_path.read_bytes()) != RC12_SHA:
        raise SystemExit("FAIL CLOSED RC1.2 parser SHA mismatch")
    if sha(m2_path.read_bytes()) != M2_SHA:
        raise SystemExit("FAIL CLOSED M2 parser SHA mismatch")

    spec = importlib.util.spec_from_file_location("compat_rc12", parser_path)
    rc12 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rc12)
    parsed = rc12.parse_corpus(input_path, verify_source=False)
    rc_records, rc_duplicates = canonical_keyed(parsed["records"])
    rc_by_line = {r["physical_line"]: (key, r) for key, r in rc_records}

    # Reproduce the frozen 005 extraction and tokenization before tok[0].
    text = raw.decode()
    old_rows = collections.defaultdict(list)
    m2_all = []
    m2_candidate = 0
    page = ""
    leaf = 0
    para = 0
    page_lang = {}
    structural_rows = []
    p_headers = 0
    marker_opens = marker_closes = 0
    page_header_re = re.compile(r"^<(f(?:\d+[rv]\d*|Ros))>\s*(.*)$")
    for physical_line, line in enumerate(text.splitlines(), 1):
        mh = page_header_re.match(line)
        if mh and "," not in mh.group(1):
            page = mh.group(1)
            page_lang[page] = re.search(r"\$L=([^\s>]+)", mh.group(2)).group(1) if re.search(r"\$L=([^\s>]+)", mh.group(2)) else "UNKNOWN"
        # The structural block map follows the repository's published IVTFF audit:
        # P-tagged physical rows only, <%> opens, <$> closes, reset on page change.
        hs = HEADER.match(line)
        if hs and "," in hs.group(1):
            locus, tag = hs.group(1).split(",", 1)
            if tag in P_TAGS:
                p_headers += 1
                pg = locus.split(".")[0]
                try:
                    line_index = int(locus.rsplit(".", 1)[-1])
                except ValueError:
                    line_index = None
                body = hs.group(2)
                marker_opens += "<%>" in body
                marker_closes += "<$>" in body
                structural_rows.append({"physical": physical_line, "page": pg, "locus": locus,
                                        "line_index": line_index, "open": "<%>" in body,
                                        "close": "<$>" in body, "lang": page_lang.get(pg, "UNKNOWN")})

        mp = PAGE_M2.match(line)
        if mp:
            page = mp.group(1)
            leaf = int(re.match(r"f(\d+)", page)[1])
            para = 0
            continue
        mm = LINE_M2.match(line)
        if not mm or mm.group(1) != page:
            continue
        n, loc, body = int(mm.group(2)), mm.group(3), mm.group(4)
        if "P" not in loc:
            continue
        m2_candidate += 1
        if "*P" in loc or "@P" in loc:
            para += 1
        cleaned = re.sub(r"<!.*?>|<[^>]*>|\{[^}]*\}|\[[^]]*\]", "", body)
        tokens = [re.sub(r"[^a-z]", "", t.lower()) for t in re.split(r"[.,\s]+", cleaned.strip())]
        tokens = [t for t in tokens if t]
        if tokens:
            lid = f"{mm.group(1)}.{mm.group(2)}"
            rec = {"locus_id": lid, "physical_line": physical_line, "page": mm.group(1),
                   "line_index": n, "tokens": tokens, "first": tokens[0],
                   "lang": page_lang.get(mm.group(1), "UNKNOWN"), "unit": (leaf, mm.group(1), para)}
            m2_all.append(rec)
            old_rows[rec["unit"]].append(rec)

    for _, rec in rc_records:
        rec["lang"] = page_lang.get(rec["folio"], "UNKNOWN")

    # Assign canonical IVTFF blocks to every P physical row; report only aggregate diagnostics.
    block_rows = []
    row_to_block = {}
    active = None
    last_page = None
    block_diffs = collections.Counter()
    for row in structural_rows:
        if row["page"] != last_page:
            if active is not None:
                block_diffs["cross_page"] += 1
            active = None
            last_page = row["page"]
        if row["open"]:
            if active is not None:
                block_diffs["nested"] += 1
            active = {"rows": []}
        if active is not None:
            active["rows"].append(row)
        if row["close"]:
            if active is None:
                block_diffs["orphan_close"] += 1
            else:
                bid = len(block_rows)
                for member in active["rows"]:
                    row_to_block[member["physical"]] = bid
                block_rows.append(active["rows"])
            active = None
    if active is not None:
        block_diffs["unclosed_end"] += 1

    # Match the two token-bearing locus populations by full canonical locus ID,
    # adding an occurrence ordinal only when the source repeats an ID.
    m2_keyed, m2_duplicates = canonical_keyed(m2_all)
    m2_by_line = {r["physical_line"]: (key, r) for key, r in m2_keyed}
    rc_map = {k: r for k, r in rc_records}
    m2_map = {k: r for k, r in m2_keyed}
    rc_keys, m2_keys = set(rc_map), set(m2_map)
    common = rc_keys & m2_keys

    # Unit memberships over common loci. Out-of-block RC loci are singletons.
    m2_units = collections.defaultdict(set)
    for key, rec in m2_keyed:
        if key in common:
            m2_units[rec["unit"]].add(key)
    rc_units = collections.defaultdict(set)
    rc_block_ids = {}
    for key, rec in rc_records:
        bid = row_to_block.get(rec["physical_line"])
        rc_block_ids[key] = bid
        if key in common:
            rc_units[("block", bid) if bid is not None else ("outside-singleton", key)].add(key)

    def pairsets(units):
        out = set()
        for members in units.values():
            ordered = sorted(members)
            for i, left in enumerate(ordered):
                for right in ordered[i + 1:]:
                    out.add((left, right))
        return out

    m2_copairs = pairsets(m2_units)
    rc_copairs = pairsets(rc_units)
    co_union = m2_copairs | rc_copairs
    co_intersection = m2_copairs & rc_copairs
    m2_neighbors = {k: frozenset(b if a == k else a for a, b in m2_copairs if k in (a, b)) for k in common}
    rc_neighbors = {k: frozenset(b if a == k else a for a, b in rc_copairs if k in (a, b)) for k in common}

    # RC1.2 adjacency is strictly physical P-row adjacency inside the IVTFF block,
    # and consecutive numeric locus indices, per the repository structural audit.
    rc_edges = collections.Counter()
    rc_valid_units = 0
    rc_valid_pairs_by_page = collections.Counter()
    rc_block_count = len(block_rows)
    for bid, rows in enumerate(block_rows):
        ordered = sorted(rows, key=lambda r: r["physical"])
        valid_here = 0
        for left, right in zip(ordered, ordered[1:]):
            if (left["line_index"] is not None and right["line_index"] == left["line_index"] + 1
                    and right["physical"] == left["physical"] + 1):
                lk = rc_by_line.get(left["physical"])
                rk = rc_by_line.get(right["physical"])
                if lk and rk:
                    rc_edges[(lk[0], rk[0])] += 1
                    valid_here += 1
                    rc_valid_pairs_by_page[left["lang"]] += 1
        if valid_here:
            rc_valid_units += 1

    def split_summary(keys):
        out = {}
        for split in ("ALL", "A", "B", "UNKNOWN"):
            ks = set(keys) if split == "ALL" else {k for k in keys if (rc_map.get(k) or m2_map.get(k))["lang"] == split}
            common_split = ks & common
            result = {"loci_RC12": len(ks & rc_keys), "loci_M2": len(ks & m2_keys),
                      "loci_common": len(common_split), "loci_solo_RC12": len((ks & rc_keys) - m2_keys),
                      "loci_solo_005": len((ks & m2_keys) - rc_keys)}
            cats = collections.Counter()
            signs = collections.Counter()
            first_equal = first_class_equal = token_equal = 0
            for k in common_split:
                rr, mr = rc_map[k], m2_map[k]
                delta = len(rr["tokens"]) - len(mr["tokens"])
                signs["<0" if delta < 0 else ">0" if delta > 0 else "=0"] += 1
                token_equal += delta == 0
                cats["comune_token_uguali" if delta == 0 else "comune_token_RC12_maggiori" if delta > 0 else "comune_token_RC12_minori"] += 1
                first_equal += rr["tokens"][0] == mr["first"]
                first_class_equal += word_class(rr["tokens"][0]) == word_class(mr["first"])
            result["token_delta_signs"] = dict(signs)
            result["token_count_equal_pct"] = round(100 * token_equal / len(common_split), 6) if common_split else None
            result["first_token_equal_pct"] = round(100 * first_equal / len(common_split), 6) if common_split else None
            result["first_class_equal_pct"] = round(100 * first_class_equal / len(common_split), 6) if common_split else None
            result["categories_common_token"] = dict(cats)
            pair_m = {e for e in m2_edge_set if all(x in common_split for x in e)}
            pair_r = {e for e in rc_edge_set if all(x in common_split for x in e)}
            pu = pair_m | pair_r
            pi = pair_m & pair_r
            cm = {p for p in m2_copairs if all(x in common_split for x in p)}
            cr = {p for p in rc_copairs if all(x in common_split for x in p)}
            cu, ci = cm | cr, cm & cr
            result["arcs"] = {"M2": len(pair_m), "RC12": len(pair_r), "common": len(pi),
                              "solo_RC12": len(pair_r-pair_m), "solo_005": len(pair_m-pair_r),
                              "union_denominator": len(pu), "common_pct_of_union": round(100*len(pi)/len(pu),6) if pu else None}
            result["coassignment_pairs"] = {"M2": len(cm), "RC12": len(cr), "common": len(ci),
                                            "union_denominator": len(cu), "common_pct_of_union": round(100*len(ci)/len(cu),6) if cu else None}
            result["loci_same_coassignment_neighborhood"] = sum(m2_neighbors[k] == rc_neighbors[k] for k in common_split)
            out[split] = result
        return out

    # Assign stable keys to M2 records after canonical matching.
    for key, rec in m2_keyed:
        rec["key"] = key
    for key, rec in rc_records:
        rec["key"] = key

    # Rebuild M2 adjacency now that stable keys are assigned.
    m2_edges = collections.Counter()
    m2_valid_units = 0
    m2_valid_pairs_by_page = collections.Counter()
    for unit, rows in old_rows.items():
        ordered = sorted(rows, key=lambda r: (r["line_index"], r["first"]))
        valid_here = 0
        for left, right in zip(ordered, ordered[1:]):
            if right["line_index"] == left["line_index"] + 1:
                m2_edges[(left["key"], right["key"])] += 1
                valid_here += 1
                m2_valid_pairs_by_page[left["lang"]] += 1
        if valid_here: m2_valid_units += 1
    # Rebuild common edge maps after stable key assignment.
    m2_common_edges = collections.Counter({e:n for e,n in m2_edges.items() if e[0] in common and e[1] in common})
    rc_common_edges = collections.Counter({e:n for e,n in rc_edges.items() if e[0] in common and e[1] in common})
    m2_edge_set, rc_edge_set = set(m2_common_edges), set(rc_common_edges)
    arc_union, arc_common = m2_edge_set | rc_edge_set, m2_edge_set & rc_edge_set

    # Build a controlled, local per-locus diff without words or public folio lists.
    diff_rows = []
    for k in sorted(rc_keys | m2_keys):
        rr, mr = rc_map.get(k), m2_map.get(k)
        category = "solo_RC12" if rr and not mr else "solo_005" if mr and not rr else "common_token_uguali" if len(rr["tokens"]) == len(mr["tokens"]) else "common_token_RC12_maggiori" if len(rr["tokens"]) > len(mr["tokens"]) else "common_token_RC12_minori"
        same_first = bool(rr and mr and rr["tokens"][0] == mr["first"])
        same_class = bool(rr and mr and word_class(rr["tokens"][0]) == word_class(mr["first"]))
        lang = (rr or mr)["lang"]
        same_neighborhood = (k in common and m2_neighbors[k] == rc_neighbors[k])
        diff_rows.append([k, lang, category, len(rr["tokens"]) if rr else "", len(mr["tokens"]) if mr else "",
                          (len(rr["tokens"]) - len(mr["tokens"])) if rr and mr else "",
                          same_first if rr and mr else "", same_class if rr and mr else "", same_neighborhood if rr and mr else ""])
    private_csv.parent.mkdir(parents=True, exist_ok=True)
    with private_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["canonical_locus_key_private", "currier", "category", "tokens_RC12", "tokens_M2_full", "delta_RC12_minus_M2", "first_token_equal", "first_class_equal", "coassignment_neighborhood_equal"]); w.writerows(diff_rows)

    # Duplicate keys are disambiguated by source-order occurrence; retain counts explicitly.
    strict_set_equal = rc_keys == m2_keys
    token_equal = all(len(rc_map[k]["tokens"]) == len(m2_map[k]["tokens"]) for k in common)
    first_equal = all(rc_map[k]["tokens"][0] == m2_map[k]["first"] for k in common)
    first_class_equal = all(word_class(rc_map[k]["tokens"][0]) == word_class(m2_map[k]["first"]) for k in common)
    partition_equal = m2_copairs == rc_copairs
    arcs_equal = m2_common_edges == rc_common_edges
    secondary = {
        "token_counts_at_least_99pct": (sum(len(rc_map[k]["tokens"]) == len(m2_map[k]["tokens"]) for k in common) / len(common) >= .99) if common else False,
        "first_token_equal_at_least_99pct": (sum(rc_map[k]["tokens"][0] == m2_map[k]["first"] for k in common) / len(common) >= .99) if common else False,
        "first_class_equal_at_least_99pct": (sum(word_class(rc_map[k]["tokens"][0]) == word_class(m2_map[k]["first"]) for k in common) / len(common) >= .99) if common else False,
        "arcs_at_least_99pct_of_union": (len(arc_common) / len(arc_union) >= .99) if arc_union else False,
        "coassignment_pairs_at_least_99pct_of_union": (len(co_intersection) / len(co_union) >= .99) if co_union else False,
        "arc_union_denominator": len(arc_union), "coassignment_union_denominator": len(co_union),
    }
    second_status = ("NON_EQUIVALENT / CONCORDANZA PARZIALE ALTA" if all(secondary[k] for k in secondary if k.endswith("at_least_99pct")) else "NON_EQUIVALENT / CONCORDANZA INSUFFICIENTE")
    strict_status = "EQUIVALENTE" if strict_set_equal and token_equal and first_equal and first_class_equal and partition_equal and arcs_equal and not block_diffs else "NON_EQUIVALENTE"

    split = split_summary(rc_keys | m2_keys)
    sign_counts = {"<0": 0, "=0": 0, ">0": 0}
    for k in common:
        delta = len(rc_map[k]["tokens"]) - len(m2_map[k]["tokens"])
        sign_counts["<0" if delta < 0 else ">0" if delta > 0 else "=0"] += 1
    report = {
        "record_id": "COMPAT-014-01-A1",
        "status": strict_status,
        "secondary_status": second_status,
        "scope": "technical parser compatibility only; no M2 fitting",
        "audit_script_sha256": sha(Path(__file__).read_bytes()),
        "hashes": {"input_sha256": input_sha, "RC1.2_sha256": RC12_SHA,
                   "M2_source_sha256": M2_SHA, "M2_source_commit": M2_COMMIT},
        "input_bytes": len(raw),
        "P_candidates": {"RC12": parsed["counts"]["candidate_p_locus_lines"], "M2": m2_candidate,
                         "raw_allowed_structural_tags": p_headers},
        "accepted_loci": {"RC12": len(rc_records), "M2": len(m2_keyed), "common": len(common),
                           "solo_RC12": len(rc_keys-m2_keys), "solo_005": len(m2_keys-rc_keys)},
        "token_counts_complete": {"RC12": sum(len(r["tokens"]) for r in rc_map.values()),
                                  "M2_before_first_token": sum(len(r["tokens"]) for r in m2_map.values()),
                                  "RC12_types": parsed["counts"]["type_count"],
                                  "M2_full_types": len({t for r in m2_map.values() for t in r["tokens"]}),
                                  "M2_first_token_types": len({r["first"] for r in m2_map.values()})},
        "common_locus_comparison": {"denominator": len(common),
            "delta_signs_RC12_minus_M2": sign_counts,
            "total_token_delta_RC12_minus_M2": sum(len(rc_map[k]["tokens"]) - len(m2_map[k]["tokens"]) for k in common),
            "token_count_equal": sum(len(rc_map[k]["tokens"]) == len(m2_map[k]["tokens"]) for k in common),
            "first_token_equal": sum(rc_map[k]["tokens"][0] == m2_map[k]["first"] for k in common),
            "first_class_equal": sum(word_class(rc_map[k]["tokens"][0]) == word_class(m2_map[k]["first"]) for k in common)},
        "units": {"M2_tag_paragraphs": len(old_rows), "M2_units_with_valid_pair": m2_valid_units,
                  "RC12_IVTFF_blocks": rc_block_count, "RC12_blocks_with_valid_pair": rc_valid_units,
                  "RC12_start_markers": marker_opens, "RC12_end_markers": marker_closes,
                  "RC12_block_map_differences": dict(block_diffs)},
        "partition": {"M2_coassigned_pairs": len(m2_copairs), "RC12_coassigned_pairs": len(rc_copairs),
                      "common": len(co_intersection), "solo_RC12": len(rc_copairs-m2_copairs), "solo_005": len(m2_copairs-rc_copairs),
                      "union_denominator": len(co_union), "coassigned_pair_agreement_pct": round(100*len(co_intersection)/len(co_union),6) if co_union else None,
                      "loci_with_same_coassignment_neighborhood": sum(m2_neighbors[k] == rc_neighbors[k] for k in common)},
        "adjacency": {"M2_legacy_valid_arcs": len(m2_edge_set), "RC12_strict_valid_arcs": len(rc_edge_set),
                      "common": len(arc_common), "solo_RC12": len(rc_edge_set-m2_edge_set), "solo_005": len(m2_edge_set-rc_edge_set),
                      "union_denominator": len(arc_union), "common_pct_of_union": round(100*len(arc_common)/len(arc_union),6) if arc_union else None,
                      "M2_valid_units": m2_valid_units, "RC12_valid_units": rc_valid_units},
        "split_total_A_B": split,
        "duplicate_locus_ids_disambiguated_by_source_order": {"RC12": sum(rc_duplicates.values()), "M2": sum(m2_duplicates.values())},
        "strict_checks": {"locus_sets_equal": strict_set_equal, "per_locus_full_token_counts_equal": token_equal,
                          "first_token_equal": first_equal, "first_class_equal": first_class_equal,
                          "partition_equal": partition_equal, "valid_arcs_equal": arcs_equal,
                          "block_map_well_formed": not block_diffs},
        "secondary_thresholds": secondary,
        "private_locus_diff_sha256": sha(private_csv.read_bytes()),
        "private_locus_diff_rows": len(diff_rows),
        "epistemic_limit": "same manuscript and training subset; technical compatibility only, not independent scientific validation",
    }
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--parser", type=Path, required=True)
    ap.add_argument("--m2-source", type=Path, required=True)
    ap.add_argument("--private-diff", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    report = audit(a.input, a.parser, a.m2_source, a.private_diff)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "secondary_status": report["secondary_status"],
                      "input_sha256": report["hashes"]["input_sha256"], "accepted_loci": report["accepted_loci"],
                      "adjacency": report["adjacency"], "private_diff_sha256": report["private_locus_diff_sha256"]},
                     ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
