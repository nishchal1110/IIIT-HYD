from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    workspace_root = Path(__file__).resolve().parents[1]
    input_image = workspace_root / "week-01" / "frames" / "frame_01.jpg"
    output_dir = Path(__file__).resolve().parent / "task3_output"

    if not input_image.exists():
        raise FileNotFoundError(f"Input image not found: {input_image}")

    # Using the current Ultralytics pretrained detection model from the glossary examples.
    model_weights = "yolo11n.pt"
    model = YOLO(model_weights)

    results = model.predict(
        source=str(input_image),
        save=True,
        project=str(output_dir),
        name="predict",
        exist_ok=True,
        conf=0.25,
    )

    detections = []
    for result in results:
        boxes = result.boxes
        if boxes is None:
            continue
        for box in boxes:
            cls_id = int(box.cls.item())
            conf = float(box.conf.item())
            detections.append((model.names[cls_id], conf))

    summary_path = output_dir / "prediction_summary.txt"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write(f"Model: {model_weights}\n")
        f.write(f"Input: {input_image}\n")
        f.write(f"Total detections: {len(detections)}\n")
        for label, conf in detections:
            f.write(f"- {label}: {conf:.4f}\n")

    print(f"Saved prediction images to: {output_dir / 'predict'}")
    print(f"Saved summary to: {summary_path}")


if __name__ == "__main__":
    main()
