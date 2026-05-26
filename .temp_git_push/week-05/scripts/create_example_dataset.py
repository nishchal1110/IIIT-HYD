from PIL import Image, ImageDraw
from pathlib import Path

TRAIN_IMG = Path('images/train/img_train.jpg')
VAL_IMG = Path('images/val/img_val.jpg')

TRAIN_LABEL = Path('labels/train/img_train.txt')
VAL_LABEL = Path('labels/val/img_val.txt')

for p in [TRAIN_IMG.parent, VAL_IMG.parent, TRAIN_LABEL.parent, VAL_LABEL.parent]:
    p.mkdir(parents=True, exist_ok=True)

# create train image 640x480 with a red rectangle
w,h = 640,480
img = Image.new('RGB',(w,h),(200,200,200))
draw = ImageDraw.Draw(img)
# object bbox in pixels
x1,y1,x2,y2 = 200,150,360,300
draw.rectangle([x1,y1,x2,y2], outline='red', width=4)
img.save(TRAIN_IMG)

# create val image 640x480 with a blue rectangle
img2 = Image.new('RGB',(w,h),(180,180,220))
draw2 = ImageDraw.Draw(img2)
xa,ya,xb,yb = 100,120,300,340
draw2.rectangle([xa,ya,xb,yb], outline='blue', width=4)
img2.save(VAL_IMG)

# write YOLO label files (class 0)
# normalize: x_center = (x1+x2)/2 / w, y_center = (y1+y2)/2 / h
def write_label(path, x1,y1,x2,y2):
    xc = (x1+x2)/2.0 / w
    yc = (y1+y2)/2.0 / h
    bw = (x2-x1)/w
    bh = (y2-y1)/h
    path.write_text(f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")

write_label(TRAIN_LABEL, x1,y1,x2,y2)
write_label(VAL_LABEL, xa,ya,xb,yb)

print('Example images and labels created:')
print(TRAIN_IMG, TRAIN_LABEL)
print(VAL_IMG, VAL_LABEL)
