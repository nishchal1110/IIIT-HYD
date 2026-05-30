from __future__ import annotations

import csv
import math
import shutil
import subprocess
import wave
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


CLASS_PALETTE: list[tuple[int, int, int]] = [
    (255, 99, 71),
    (54, 162, 235),
    (255, 206, 86),
    (75, 192, 192),
    (153, 102, 255),
    (255, 159, 64),
    (46, 204, 113),
    (231, 76, 60),
    (52, 152, 219),
    (241, 196, 15),
    (155, 89, 182),
    (26, 188, 156),
]


def color_for_class(class_id: int) -> tuple[int, int, int]:
    return CLASS_PALETTE[class_id % len(CLASS_PALETTE)]


def render_semantic_overlay(
    frame: np.ndarray,
    result,
    class_names: dict[int, str],
) -> tuple[np.ndarray, int]:
    overlay = frame.copy()
    if result.masks is None or result.masks.data is None:
        return overlay, 0

    class_ids: list[int] = []
    confidences: list[float] = []
    if result.boxes is not None:
        for box in result.boxes:
            class_ids.append(int(box.cls.item()))
            confidences.append(float(box.conf.item()))

    mask_pixels = 0
    alpha = 0.45
    polygons = result.masks.xy or []

    for idx, polygon in enumerate(polygons):
        if polygon is None or len(polygon) == 0:
            continue

        class_id = class_ids[idx] if idx < len(class_ids) else 0
        color = np.array(color_for_class(class_id), dtype=np.float32)

        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [np.asarray(polygon, dtype=np.int32)], 1)
        mask_bool = mask.astype(bool)
        if not np.any(mask_bool):
            continue

        mask_pixels += int(mask_bool.sum())
        region = overlay[mask_bool].astype(np.float32)
        blended = region * (1.0 - alpha) + color * alpha
        overlay[mask_bool] = blended.astype(np.uint8)

        ys, xs = np.where(mask_bool)
        if len(xs) and len(ys):
            center_x = int(xs.mean())
            center_y = int(ys.mean())
            label = class_names.get(class_id, f"class_{class_id}")
            if idx < len(confidences):
                label = f"{label}:{confidences[idx]:.2f}"

            cv2.putText(
                overlay,
                label,
                (center_x, center_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

    return overlay, mask_pixels


def collect_previous_detection_metrics(workspace_root: Path) -> list[str]:
    summaries: list[str] = []
    for results_csv in sorted(workspace_root.glob("week-*/**/runs/detect/**/results.csv")):
        try:
            with results_csv.open("r", encoding="utf-8", newline="") as csv_file:
                rows = list(csv.DictReader(csv_file))
        except Exception:
            continue

        if not rows:
            continue

        latest = rows[-1]
        parts: list[str] = [str(results_csv.parent)]
        for key in (
            "metrics/precision(B)",
            "metrics/recall(B)",
            "metrics/mAP50(B)",
            "metrics/mAP50-95(B)",
        ):
            if key in latest and latest[key]:
                parts.append(f"{key.split('/')[-1]}={float(latest[key]):.4f}")

        summaries.append(" | ".join(parts))

    return summaries


def generate_new_music_wav(audio_path: Path, duration_sec: float, sample_rate: int = 44100) -> None:
    """Generate a fresh background track for Week 3 outputs."""
    chord_progression = [
        (220.00, 277.18, 329.63),
        (246.94, 311.13, 369.99),
        (261.63, 329.63, 392.00),
        (196.00, 246.94, 293.66),
    ]
    beat_duration = 0.40
    total_samples = int(duration_sec * sample_rate)

    with wave.open(str(audio_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(total_samples):
            t = i / sample_rate
            chord_idx = int((t / beat_duration) % len(chord_progression))
            f1, f2, f3 = chord_progression[chord_idx]

            # Smooth envelope avoids clicks while keeping a punchy groove.
            attack = min(1.0, (t % beat_duration) / 0.05)
            release = min(1.0, (beat_duration - (t % beat_duration)) / 0.08)
            envelope = min(attack, release)

            bass = math.sin(2 * math.pi * (f1 / 2.0) * t)
            mid = math.sin(2 * math.pi * f2 * t)
            high = math.sin(2 * math.pi * f3 * t)
            rhythmic = 0.25 * math.sin(2 * math.pi * 3.0 * t)

            value = int(9000 * envelope * (0.45 * bass + 0.35 * mid + 0.20 * high + rhythmic))
            wav_file.writeframesraw(value.to_bytes(2, byteorder="little", signed=True))


def mux_audio_with_ffmpeg(video_path: Path, audio_path: Path, output_path: Path) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False

    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(video_path),
        "-i",
        str(audio_path),
        "-shortest",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        str(output_path),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    return completed.returncode == 0


def mux_audio_with_moviepy(video_path: Path, audio_path: Path, output_path: Path) -> bool:
    try:
        from moviepy import AudioFileClip, VideoFileClip
    except Exception:
        return False

    try:
        with VideoFileClip(str(video_path)) as clip:
            with AudioFileClip(str(audio_path)) as audio:
                final = clip.with_audio(audio)
                final.write_videofile(str(output_path), codec="libx264", audio_codec="aac", logger=None)
        return True
    except Exception:
        return False


def main() -> None:
    workspace_root = Path(__file__).resolve().parents[1]
    input_dir = workspace_root / "week-01" / "task2_output" / "frames60"
    output_root = Path(__file__).resolve().parent / "task1_output"
    segmented_dir = output_root / "segmented_frames"

    output_root.mkdir(parents=True, exist_ok=True)
    segmented_dir.mkdir(parents=True, exist_ok=True)

    for stale_frame in segmented_dir.glob("seg_*.jpg"):
        stale_frame.unlink(missing_ok=True)

    for stale_file in (
        output_root / "segmented_video_silent.mp4",
        output_root / "segmented_video_with_music.mp4",
        output_root / "new_background_music.wav",
        output_root / "segmentation_metrics.txt",
        Path(__file__).resolve().parent / "WEEK3_TASK1_REPORT.md",
    ):
        stale_file.unlink(missing_ok=True)

    image_paths = sorted(input_dir.glob("*.jpg")) + sorted(input_dir.glob("*.png"))
    if not image_paths:
        raise FileNotFoundError(f"No input images found in {input_dir}")

    model_name = "yolo11n-seg.pt"
    model = YOLO(model_name)
    prior_detection_metrics = collect_previous_detection_metrics(workspace_root)

    first_shape: tuple[int, int] | None = None
    fps = 30

    total_detections = 0
    total_masks = 0
    total_mask_pixels = 0
    class_counter: Counter[str] = Counter()
    confidence_values: list[float] = []
    preprocess_ms: list[float] = []
    inference_ms: list[float] = []
    postprocess_ms: list[float] = []

    for idx, image_path in enumerate(image_paths, start=1):
        frame = cv2.imread(str(image_path))
        if frame is None:
            raise ValueError(f"Could not read image: {image_path}")

        results = model.predict(source=str(image_path), save=False, conf=0.25, verbose=False)
        result = results[0]

        plotted, mask_pixels = render_semantic_overlay(frame, result, model.names)
        if first_shape is None:
            first_shape = (plotted.shape[1], plotted.shape[0])

        if plotted.shape[1] != first_shape[0] or plotted.shape[0] != first_shape[1]:
            plotted = cv2.resize(plotted, first_shape)

        out_img_path = segmented_dir / f"seg_{idx:04d}.jpg"
        cv2.imwrite(str(out_img_path), plotted)

        if result.boxes is not None:
            total_detections += len(result.boxes)
            for box in result.boxes:
                cls_id = int(box.cls.item())
                conf = float(box.conf.item())
                class_counter[model.names[cls_id]] += 1
                confidence_values.append(conf)

        if result.masks is not None and result.masks.data is not None:
            total_masks += int(result.masks.data.shape[0])
            total_mask_pixels += mask_pixels

        speed = result.speed or {}
        if "preprocess" in speed:
            preprocess_ms.append(float(speed["preprocess"]))
        if "inference" in speed:
            inference_ms.append(float(speed["inference"]))
        if "postprocess" in speed:
            postprocess_ms.append(float(speed["postprocess"]))

    if first_shape is None:
        raise RuntimeError("Could not determine frame size for video generation")

    silent_video = output_root / "segmented_video_silent.mp4"
    writer = cv2.VideoWriter(
        str(silent_video),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        first_shape,
    )

    for segmented_img in sorted(segmented_dir.glob("seg_*.jpg")):
        frame = cv2.imread(str(segmented_img))
        writer.write(frame)
    writer.release()

    duration_sec = len(image_paths) / fps
    bgm_path = output_root / "new_background_music.wav"
    generate_new_music_wav(bgm_path, duration_sec=duration_sec)

    final_video = output_root / "segmented_video_with_music.mp4"
    music_added = mux_audio_with_ffmpeg(silent_video, bgm_path, final_video)
    if not music_added:
        music_added = mux_audio_with_moviepy(silent_video, bgm_path, final_video)

    if not music_added:
        final_video = silent_video

    avg_conf = float(np.mean(confidence_values)) if confidence_values else 0.0
    avg_preprocess = float(np.mean(preprocess_ms)) if preprocess_ms else 0.0
    avg_inference = float(np.mean(inference_ms)) if inference_ms else 0.0
    avg_postprocess = float(np.mean(postprocess_ms)) if postprocess_ms else 0.0
    approx_fps = 1000.0 / avg_inference if avg_inference > 0 else 0.0
    mask_coverage = (
        (total_mask_pixels / (len(image_paths) * first_shape[0] * first_shape[1]))
        if first_shape is not None and image_paths
        else 0.0
    )

    metrics_txt = output_root / "segmentation_metrics.txt"
    with metrics_txt.open("w", encoding="utf-8") as f:
        f.write("Week 03 Task 1: Semantic Segmentation Metrics\n")
        f.write(f"Model: {model_name}\n")
        f.write(f"Input directory: {input_dir}\n")
        f.write(f"Images processed: {len(image_paths)}\n")
        f.write(f"Total detected objects: {total_detections}\n")
        f.write(f"Total segmented masks: {total_masks}\n")
        f.write(f"Average confidence: {avg_conf:.4f}\n")
        f.write(f"Average preprocess time (ms/image): {avg_preprocess:.3f}\n")
        f.write(f"Average inference time (ms/image): {avg_inference:.3f}\n")
        f.write(f"Average postprocess time (ms/image): {avg_postprocess:.3f}\n")
        f.write(f"Approx inference FPS: {approx_fps:.2f}\n")
        f.write(f"Average mask coverage: {mask_coverage:.4f}\n")
        f.write("\nClass distribution:\n")

        for label, count in class_counter.most_common():
            f.write(f"- {label}: {count}\n")

        f.write("\nOutputs:\n")
        f.write(f"- Segmented frames: {segmented_dir}\n")
        f.write(f"- Silent video: {silent_video}\n")
        f.write(f"- Final video: {final_video}\n")
        f.write(f"- Music added: {'yes' if music_added else 'no'}\n")

        f.write("\nPrevious detection metrics found under runs/detect:\n")
        if prior_detection_metrics:
            for line in prior_detection_metrics:
                f.write(f"- {line}\n")
        else:
            f.write("- No runs/detect results.csv files were found in this workspace.\n")

    report_md = Path(__file__).resolve().parent / "WEEK3_TASK1_REPORT.md"
    with report_md.open("w", encoding="utf-8") as f:
        f.write("# Week 03 Task 1 Report\n\n")
        f.write("Date: 2026-04-25\n\n")
        f.write("## Objective\n")
        f.write("Perform semantic segmentation on all images in the training frame folder and create a final video with music.\n\n")
        f.write("## Ultralytics Segmentation Reference\n")
        f.write("- https://www.ultralytics.com/glossary/image-segmentation\n\n")
        f.write("## Implementation\n")
        f.write("- Script: week-03/task1_semantic_segmentation.py\n")
        f.write(f"- Model: {model_name}\n")
        f.write(f"- Input folder: {input_dir}\n")
        f.write(f"- Total images segmented: {len(image_paths)}\n")
        f.write("\n## Key Performance Metrics\n")
        f.write(f"- Average confidence: {avg_conf:.4f}\n")
        f.write(f"- Average preprocess time: {avg_preprocess:.3f} ms/image\n")
        f.write(f"- Average inference time: {avg_inference:.3f} ms/image\n")
        f.write(f"- Average postprocess time: {avg_postprocess:.3f} ms/image\n")
        f.write(f"- Approx inference FPS: {approx_fps:.2f}\n")
        f.write(f"- Average mask coverage: {mask_coverage:.4f}\n")
        f.write(f"- Total segmented masks: {total_masks}\n")
        f.write("\n## Previous Detection Metrics Found\n")
        if prior_detection_metrics:
            for line in prior_detection_metrics:
                f.write(f"- {line}\n")
        else:
            f.write("- No runs/detect results.csv files were found in this workspace.\n")
        f.write("\n## Artifacts\n")
        f.write("- Segmented frames: week-03/task1_output/segmented_frames/\n")
        f.write("- Silent video: week-03/task1_output/segmented_video_silent.mp4\n")
        f.write("- New music: week-03/task1_output/new_background_music.wav\n")
        f.write("- Final video with music: week-03/task1_output/segmented_video_with_music.mp4\n")
        f.write("- Detailed metrics: week-03/task1_output/segmentation_metrics.txt\n")

    print(f"Processed images: {len(image_paths)}")
    print(f"Segmented masks: {total_masks}")
    print(f"Average confidence: {avg_conf:.4f}")
    print(f"Average inference time (ms): {avg_inference:.3f}")
    print(f"Final video: {final_video}")
    print(f"Metrics file: {metrics_txt}")
    print(f"Report file: {report_md}")


if __name__ == "__main__":
    main()
