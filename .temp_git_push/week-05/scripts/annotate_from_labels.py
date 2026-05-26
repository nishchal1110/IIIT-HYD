from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_YAML = ROOT / 'data.yaml'
IMG_DIR = ROOT / 'images_resized'
OUT_DIR = ROOT / 'outputs' / 'detections_annotated'
LABELS_DIRS = [ROOT / 'labels' / 'train', ROOT / 'labels' / 'val']

OUT_DIR.mkdir(parents=True, exist_ok=True)

# load class names
if DATA_YAML.exists():
    with open(DATA_YAML, 'r') as f:
        data = yaml.safe_load(f)
    names = data.get('names', [])
else:
    names = []

# simple font fallback
try:
    font = ImageFont.truetype('arial.ttf', 16)
except Exception:
    font = ImageFont.load_default()

for img_path in IMG_DIR.glob('*.jpg'):
    img = Image.open(img_path).convert('RGB')
    w,h = img.size
    draw = ImageDraw.Draw(img)
    stem = img_path.stem
    # look for label in labels/train or labels/val
    label_path = None
    for ld in LABELS_DIRS:
        p = ld / (stem + '.txt')
        if p.exists():
            label_path = p
            break
    if label_path is None:
        # skip if no label
        continue
    lines = label_path.read_text().splitlines()
    for line in lines:
        parts = line.split()
        if len(parts) < 5:
            continue
        cls = int(parts[0])
        xc, yc, bw, bh = map(float, parts[1:5])
        # convert to pixel coords
        box_w = bw * w
        box_h = bh * h
        cx = xc * w
        cy = yc * h
        x1 = cx - box_w/2
        y1 = cy - box_h/2
        x2 = cx + box_w/2
        y2 = cy + box_h/2
        draw.rectangle([x1,y1,x2,y2], outline='red', width=3)
        label = names[cls] if cls < len(names) else str(cls)
        text = f"{label} {cls}"
        try:
            tw,th = font.getsize(text)
        except Exception:
            tw,th = (len(text)*6, 12)
        draw.rectangle([x1, y1-th-4, x1+tw+4, y1], fill='red')
        draw.text((x1+2, y1-th-2), text, fill='white', font=font)
    out_path = OUT_DIR / img_path.name
    img.save(out_path)
    print('Wrote', out_path)

print('Annotation complete. Annotated images in', OUT_DIR)
