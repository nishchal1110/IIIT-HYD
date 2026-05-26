from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'outputs' / 'detections_annotated'
files = sorted(list(p.glob('*.jpg')))
for i,f in enumerate(files, start=1):
    out = p / f'img_{i:03d}.jpg'
    out.write_bytes(f.read_bytes())
print('copied', len(files), 'files')
