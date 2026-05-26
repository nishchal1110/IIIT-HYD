from pathlib import Path
import sys

p = Path(__file__).resolve().parents[1] / 'outputs' / 'detections_annotated'
imgs = sorted(list(p.glob('*.jpg')))
if not imgs:
    print('No annotated images found')
    sys.exit(1)

try:
    import cv2
except Exception:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'opencv-python'])
    import cv2

first = cv2.imread(str(imgs[0]))
h,w = first.shape[:2]
out_path = Path(__file__).resolve().parents[1] / 'outputs' / 'detections_video.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(str(out_path), fourcc, 1.0, (w,h))
for img in imgs:
    frame = cv2.imread(str(img))
    writer.write(frame)
writer.release()
print('Video written to', out_path)
