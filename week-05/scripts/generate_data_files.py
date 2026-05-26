import os
from pathlib import Path

def list_images(dir_path):
    p = Path(dir_path)
    if not p.exists():
        return []
    exts = ('.jpg', '.jpeg', '.png')
    return [str(x.as_posix()) for x in p.rglob('*') if x.suffix.lower() in exts]

if __name__ == '__main__':
    images_train = list_images('images/train')
    images_val = list_images('images/val')

    os.makedirs('lists', exist_ok=True)
    with open('lists/train.txt','w') as f:
        for p in images_train:
            f.write(p + '\n')
    with open('lists/val.txt','w') as f:
        for p in images_val:
            f.write(p + '\n')

    print(f'Wrote {len(images_train)} entries to lists/train.txt')
    print(f'Wrote {len(images_val)} entries to lists/val.txt')
