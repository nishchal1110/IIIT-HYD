import yaml
from pathlib import Path


def validate_yaml(path='data.yaml'):
    p = Path(path)
    if not p.exists():
        print(f'YAML not found: {path}')
        return False
    d = yaml.safe_load(p.read_text())
    ok = True
    if 'nc' in d and 'names' in d:
        if d['nc'] != len(d['names']):
            print(f"Mismatch: nc={d['nc']} but len(names)={len(d['names'])}")
            ok = False
    else:
        print('YAML missing nc or names')
        ok = False
    return ok


def validate_labels(images_dir, labels_dir):
    img_dir = Path(images_dir)
    lbl_dir = Path(labels_dir)
    if not img_dir.exists() or not lbl_dir.exists():
        print(f'Missing dirs: {images_dir} or {labels_dir}')
        return False
    exts = ('.jpg','.jpeg','.png')
    ok = True
    for img in img_dir.rglob('*'):
        if img.suffix.lower() in exts:
            lbl = lbl_dir / (img.stem + '.txt')
            if not lbl.exists():
                print(f'Missing label for image: {img}')
                ok = False
            else:
                for i,line in enumerate(lbl.read_text().splitlines(), start=1):
                    parts = line.split()
                    if len(parts) != 5:
                        print(f'Bad format {lbl}:{i}: {line}')
                        ok = False
                        continue
                    try:
                        cls = int(parts[0])
                        vals = list(map(float, parts[1:]))
                        if any(v < 0 or v > 1 for v in vals):
                            print(f'Non-normalized coords {lbl}:{i}: {line}')
                            ok = False
                    except Exception as e:
                        print(f'Parse error {lbl}:{i}: {e}')
                        ok = False
    return ok

if __name__ == '__main__':
    ok = validate_yaml('data.yaml')
    v1 = validate_labels('images/train','labels/train')
    v2 = validate_labels('images/val','labels/val')
    if ok and v1 and v2:
        print('Dataset validation passed')
    else:
        print('Dataset validation failed')
