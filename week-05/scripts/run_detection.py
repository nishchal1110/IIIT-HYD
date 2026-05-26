import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='yolov8n.pt', help='weights path or name')
    parser.add_argument('--source', type=str, default='../images_resized', help='image/dir/video source')
    parser.add_argument('--output', type=str, default='../outputs/detections', help='output folder')
    parser.add_argument('--conf', type=float, default=0.25)
    args = parser.parse_args()

    try:
        from ultralytics import YOLO
    except Exception as e:
        print('ultralytics not installed. Please run: pip install ultralytics')
        raise

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(args.weights)
    print(f'Running detection with weights={args.weights} on source={args.source}')
    # predict: saves images with boxes to project/name
    results = model.predict(source=args.source, conf=args.conf, save=True, project=str(out_dir), name='run')
    print('Detection complete. Outputs saved under', out_dir)

if __name__ == '__main__':
    main()
