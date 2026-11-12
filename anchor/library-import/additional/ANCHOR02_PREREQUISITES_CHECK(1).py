from pathlib import Path
import csv, hashlib, json, re
root=Path('/mnt/data')
corpus=root/'ZL3b-n(8).txt'
heads=root/'ANCHOR02_HEAD_INVENTORY_EXPLORATORY.csv'
triage=root/'ANCHOR02_TEXT_REGION_TRIAGE_V2.csv'
sha=hashlib.sha256(corpus.read_bytes()).hexdigest()
assert sha=='bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'
text=corpus.read_text()
section=text.split('<f70v2>')[1].split('\n<f71',1)[0]
label_rows=re.findall(r'^<f70v2\.\d+,[^>]+>',section,re.M)
with heads.open(newline='') as f: head_rows=list(csv.DictReader(f))
with triage.open(newline='') as f: region_rows=list(csv.DictReader(f))
validated_labels=[r for r in region_rows if r['token_eligible'].strip().upper()=='YES']
validated_heads=[r for r in head_rows if 'validated' in r['status'].lower() and 'nonblind' not in r['status'].lower()]
result={'input_sha256':sha,'f70v2_transcription_loci':len(label_rows),'figure_candidates':len(head_rows),'validated_figure_coordinates':len(validated_heads),'reviewed_text_regions':len(region_rows),'token_eligible_regions':len(validated_labels),'validated_figure_label_links':0,'test':'BLOCKED_MISSING_VALIDATED_GEOMETRIC_LINKS','baseline':'NOT_RUN'}
print(json.dumps(result,indent=2))