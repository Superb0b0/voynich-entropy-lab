#!/usr/bin/env python3
"""Independent RC1.2 candidate parser; fail-fast and non-mutating."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from collections import Counter
from pathlib import Path

EXPECTED_SHA256 = "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc"
EXPECTED_LINES = 8510
EXPECTED_BYTES = 411671
ALLOWED_P_TAGS = {"*P0", "*Pb", "+P0", "+P1", "+Pb", "+Pc", "+Pr", "=P0", "=Pt", "@P0", "@P1", "@Pb"}
HEADER_RE = re.compile(r"^<(?P<header>[^>]+)>[ \t]*(?P<body>.*)$")
NUMERIC_LOCUS_RE = re.compile(r"^(?P<folio>f[0-9]+[rv][0-9]*)\.(?P<line>[0-9]+)$")
ROSETTES_LOCUS_RE = re.compile(r"^(?P<folio>fRos)\.(?P<line>[0-9]+)$")
COMMENT_RE = re.compile(r"<![^>]*>")
UNKNOWN_ANGLE_RE = re.compile(r"<[^>]*>")
BRACE_RE = re.compile(r"\{([^{}]*)\}")
SQUARE_RE = re.compile(r"\[[^\[\]]*\]")
TOKEN_RE = re.compile(r"[A-Za-z]+")
STANDARD_MARKERS = ("<$>", "<%>", "<->", "<~>", "<d>")
LOCAL_NONSTANDARD_MARKERS = ("<@H=2>", "<@H=3>")

class ParseFailure(Exception):
    pass

def validate_balanced(body: str, opener: str, closer: str, label: str) -> None:
    depth = 0
    for ch in body:
        if ch == opener:
            depth += 1
            if depth > 1:
                raise ParseFailure(f"nested {label} block")
        elif ch == closer:
            depth -= 1
            if depth < 0:
                raise ParseFailure(f"unmatched closing {label}")
    if depth:
        raise ParseFailure(f"unclosed {label} block")

def clean_body(body: str, audit: Counter, local_markers: list[str]) -> str:
    if body.count("<!") != len(COMMENT_RE.findall(body)):
        raise ParseFailure("unclosed inline comment")
    body = COMMENT_RE.sub(" ", body)
    for marker in STANDARD_MARKERS:
        count = body.count(marker)
        audit[f"marker:{marker}"] += count
        body = body.replace(marker, " ")
    for marker in LOCAL_NONSTANDARD_MARKERS:
        count = body.count(marker)
        if count:
            audit[f"marker:{marker}"] += count
            local_markers.extend([marker] * count)
            body = body.replace(marker, " ")
    # Curly braces encode ligature groupings in this extraction profile.
    # Preserve their internal transcription characters and remove only delimiters.
    validate_balanced(body, "{", "}", "brace")
    brace_matches = list(BRACE_RE.finditer(body))
    audit["brace_blocks_preserved_internal_text"] += len(brace_matches)
    body = BRACE_RE.sub(lambda m: m.group(1), body)
    # Square-bracket alternatives are excluded as a whole, without selecting a reading.
    validate_balanced(body, "[", "]", "square-bracket")
    square_matches = list(SQUARE_RE.finditer(body))
    audit["square_blocks_excluded"] += len(square_matches)
    body = SQUARE_RE.sub(" ", body)
    m = UNKNOWN_ANGLE_RE.search(body)
    if m:
        raise ParseFailure(f"unknown angle marker {m.group(0)!r}")
    if "<" in body or ">" in body:
        raise ParseFailure("unmatched angle bracket in body")
    return body

def parse_corpus(path: Path, verify_source: bool = True) -> dict:
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if verify_source and sha != EXPECTED_SHA256:
        raise ParseFailure(f"source SHA-256 mismatch: {sha}")
    if verify_source and len(raw) != EXPECTED_BYTES:
        raise ParseFailure(f"source byte count mismatch: {len(raw)} != {EXPECTED_BYTES}")
    try:
        source_text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as e:
        raise ParseFailure(f"invalid UTF-8: {e}") from e
    lines = source_text.splitlines()
    if verify_source and len(lines) != EXPECTED_LINES:
        raise ParseFailure(f"physical line count mismatch: {len(lines)} != {EXPECTED_LINES}")

    physical_lines = len(lines)
    structural_header_lines = 0
    non_header_lines = 0
    non_locus_lines = 0
    non_p_locus_lines = 0
    candidate_count = 0
    tag_counts = Counter()
    audit_counts = Counter()
    records, empty_lines, errors, local_marker_audit = [], [], [], []

    for physical_line, line in enumerate(lines, 1):
        m = HEADER_RE.match(line)
        if not m or "," not in m.group("header"):
            non_header_lines += 1
            non_locus_lines += 1
            continue
        structural_header_lines += 1
        locus_id, tag = m.group("header").split(",", 1)
        if not re.match(r"^[+@=*/]P", tag):
            non_p_locus_lines += 1
            continue
        candidate_count += 1
        tag_counts[tag] += 1
        try:
            if tag not in ALLOWED_P_TAGS:
                raise ParseFailure(f"unclassified P tag {tag!r}")
            lm = NUMERIC_LOCUS_RE.fullmatch(locus_id) or ROSETTES_LOCUS_RE.fullmatch(locus_id)
            if not lm:
                raise ParseFailure(f"malformed locus identifier {locus_id!r}")
            local_markers: list[str] = []
            cleaned = clean_body(m.group("body"), audit_counts, local_markers)
            for marker in local_markers:
                local_marker_audit.append({"physical_line": physical_line, "locus_id": locus_id, "tag": tag, "marker": marker, "classification": "recognized_local_nonstandard_marker", "action": "replace_with_space"})
            tokens = [t.lower() for t in TOKEN_RE.findall(cleaned)]
            if not tokens:
                empty_lines.append({"physical_line": physical_line, "locus_id": locus_id, "tag": tag})
                continue
            records.append({"physical_line": physical_line, "locus_id": locus_id, "folio": lm.group("folio"), "line_index": int(lm.group("line")), "tag": tag, "tokens": tokens})
        except ParseFailure as e:
            errors.append({"physical_line": physical_line, "locus_id": locus_id, "tag": tag, "error": str(e)})
    if errors:
        detail = "; ".join(f"line {e['physical_line']} {e['locus_id']} [{e['tag']}]: {e['error']}" for e in errors[:30])
        tail = f"; ... {len(errors)-30} further errors" if len(errors) > 30 else ""
        raise ParseFailure(f"{len(errors)} validation error(s); no canonical counts emitted. {detail}{tail}")

    all_tokens = [t for rec in records for t in rec["tokens"]]
    types = sorted(set(all_tokens), key=lambda s: s.encode("ascii"))
    counts = {
        "physical_lines": physical_lines,
        "structural_header_lines_with_comma": structural_header_lines,
        "non_header_lines": non_header_lines,
        "non_locus_lines": non_locus_lines,
        "non_p_locus_header_lines": non_p_locus_lines,
        "candidate_p_locus_lines": candidate_count,
        "empty_after_cleaning": len(empty_lines),
        "canonical_loci": len(records),
        "token_count": len(all_tokens),
        "type_count": len(types),
        "folio_count": len({r['folio'] for r in records}),
    }
    return {
        "specification": "PARSER_SPEC_V1_RC1_2.md",
        "parser": "ivtff_parser_rc1_2.py",
        "status": "RELEASE_CANDIDATE_FREEZE_BLOCKED",
        "source": {"filename": path.name, "sha256": sha, "size_bytes": len(raw), "physical_lines": len(lines)},
        "counts": counts,
        "tag_counts": dict(sorted(tag_counts.items())),
        "transformation_counts": dict(sorted(audit_counts.items())),
        "empty_loci": empty_lines,
        "types": types,
        "records": records,
        "recognized_local_nonstandard_markers": local_marker_audit,
        "errors": [],
    }

def run_unit_tests() -> list[str]:
    failures=[]
    tests = [
        ("abc.def", ["abc", "def"]), ("abc,def", ["abc", "def"]),
        ("y,char", ["y", "char"]), ("a..b", ["a", "b"]),
        ("a,,b", ["a", "b"]), (".a,", ["a"]),
        ("abc<$>def", ["abc", "def"]), ("abc<%>def", ["abc", "def"]),
        ("abc<->def", ["abc", "def"]), ("abc<~>def", ["abc", "def"]),
        ("abc<d>def", ["abc", "def"]), ("abc<!corr?>def", ["abc", "def"]),
        ("abc{ykh}ey", ["abcykhey"]), ("a{cty}sh", ["actysh"]),
        ("abc[x:y]def", ["abc", "def"]), ("ABC.def", ["abc", "def"]),
        ("abc<@H=2>def", ["abc", "def"]), ("abc<@H=3>def", ["abc", "def"]),
    ]
    for body, expected in tests:
        try:
            got = [t.lower() for t in TOKEN_RE.findall(clean_body(body, Counter(), []))]
            if got != expected: failures.append(f"{body!r}: expected {expected!r}, got {got!r}")
        except Exception as e: failures.append(f"{body!r}: unexpected error {e}")
    bad = ["abc<unknown>def", "abc<@H=4>def", "abc{alt", "abc[x:y", "abc[one[two]three]def", "abc{one{two}}def"]
    for body in bad:
        try: clean_body(body, Counter(), []); failures.append(f"{body!r}: expected validation error, got success")
        except ParseFailure: pass
    for lid in ("fRos.39", "fRos.145"):
        if not (NUMERIC_LOCUS_RE.fullmatch(lid) or ROSETTES_LOCUS_RE.fullmatch(lid)): failures.append(f"expected valid locus ID {lid}")
    if NUMERIC_LOCUS_RE.fullmatch("fRos.x") or ROSETTES_LOCUS_RE.fullmatch("fRos.x"): failures.append("fRos.x unexpectedly valid")
    audit = Counter(); local = []
    try:
        clean_body("a<d>b<@H=2>c<@H=3>d", audit, local)
        if audit["marker:<d>"] != 1: failures.append(f"<d> count should be 1, got {audit['marker:<d>']}")
        if local != ["<@H=2>", "<@H=3>"]: failures.append(f"local marker audit mismatch: {local!r}")
    except Exception as e: failures.append(f"marker audit test raised unexpected error: {e}")
    # Explicitly assert that braces preserve inner text without inserting spaces.
    got = [t.lower() for t in TOKEN_RE.findall(clean_body("yshaiin.{ykh}ey", Counter(), []))]
    if got != ["yshaiin", "ykhey"]: failures.append(f"brace-preservation regression: {got!r}")
    return failures

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--skip-source-lock", action="store_true")
    ap.add_argument("--test-only", action="store_true")
    a=ap.parse_args()
    failures=run_unit_tests()
    if failures:
        print("UNIT TESTS FAILED:\n"+"\n".join(failures), file=sys.stderr); return 2
    print("UNIT TESTS PASS: 30 checks")
    if a.test_only: return 0
    try: report=parse_corpus(a.corpus, verify_source=not a.skip_source_lock)
    except ParseFailure as e: print(f"CORPUS VALIDATION BLOCKED: {e}", file=sys.stderr); return 3
    payload=json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2)+"\n"
    a.out.write_text(payload, encoding="utf-8", newline="\n")
    print(json.dumps(report["counts"], sort_keys=True)); print(f"REPORT: {a.out}"); return 0
if __name__ == "__main__": raise SystemExit(main())
