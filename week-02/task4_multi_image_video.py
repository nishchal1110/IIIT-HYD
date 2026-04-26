from __future__ import annotations

import math
import shutil
import subprocess
import wave
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


def generate_music_wav(audio_path: Path, duration_sec: float, sample_rate: int = 44100) -> None:
    """Generate a simple tone-based background track as a WAV file."""
    melody = [261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 261.63, 196.00]
    note_duration = 0.5
    total_samples = int(duration_sec * sample_rate)

    with wave.open(str(audio_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(total_samples):
            t = i / sample_rate
            note_idx = int((t / note_duration) % len(melody))
            freq = melody[note_idx]
            envelope = 0.5 + 0.5 * math.sin(2 * math.pi * 0.5 * t)
            value = int(12000 * envelope * math.sin(2 * math.pi * freq * t))
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
    input_dir = workspace_root / "week-01" / "frames"
    output_root = Path(__file__).resolve().parent / "task4_output"
    annotated_dir = output_root / "annotated_frames"
    output_root.mkdir(parents=True, exist_ok=True)
    annotated_dir.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(input_dir.glob("*.jpg"))
    if not image_paths:
        raise FileNotFoundError(f"No JPG images found in {input_dir}")

    model_name = "yolo11n.pt"
    model = YOLO(model_name)

    summary_lines: list[str] = []
    first_shape: tuple[int, int] | None = None
    fps = 2

    for idx, image_path in enumerate(image_paths, start=1):
        results = model.predict(source=str(image_path), save=False, conf=0.25, verbose=False)
        result = results[0]

        plotted = result.plot()
        if first_shape is None:
            first_shape = (plotted.shape[1], plotted.shape[0])

        if plotted.shape[1] != first_shape[0] or plotted.shape[0] != first_shape[1]:
            plotted = cv2.resize(plotted, first_shape)

        out_img_path = annotated_dir / f"frame_{idx:02d}.jpg"
        cv2.imwrite(str(out_img_path), plotted)

        frame_detections: list[str] = []
        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls.item())
                conf = float(box.conf.item())
                frame_detections.append(f"{model.names[cls_id]}:{conf:.3f}")

        if frame_detections:
            summary_lines.append(f"{image_path.name}: {', '.join(frame_detections)}")
        else:
            summary_lines.append(f"{image_path.name}: no detections")

    if first_shape is None:
        raise RuntimeError("Could not determine frame size for video generation")

    silent_video = output_root / "annotated_video_silent.mp4"
    writer = cv2.VideoWriter(
        str(silent_video),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        first_shape,
    )
    for annotated_img in sorted(annotated_dir.glob("*.jpg")):
        frame = cv2.imread(str(annotated_img))
        writer.write(frame)
    writer.release()

    duration_sec = max(len(image_paths) / fps, 2.0)
    bgm_path = output_root / "background_music.wav"
    generate_music_wav(bgm_path, duration_sec=duration_sec)

    final_video = output_root / "annotated_video_with_music.mp4"
    music_added = mux_audio_with_ffmpeg(silent_video, bgm_path, final_video)
    if not music_added:
        music_added = mux_audio_with_moviepy(silent_video, bgm_path, final_video)

    if not music_added:
        final_video = silent_video

    summary_path = output_root / "task4_summary.txt"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write("Task 4: Multi-image object detection and video creation\n")
        f.write(f"Model: {model_name}\n")
        f.write(f"Input directory: {input_dir}\n")
        f.write(f"Images processed: {len(image_paths)}\n")
        f.write(f"Annotated frames directory: {annotated_dir}\n")
        f.write(f"Final video: {final_video}\n")
        f.write(f"Background music added: {'yes' if music_added else 'no'}\n")
        f.write("\nPer-image detections:\n")
        for line in summary_lines:
            f.write(f"- {line}\n")

    print(f"Processed {len(image_paths)} images")
    print(f"Annotated frames saved to: {annotated_dir}")
    print(f"Video saved to: {final_video}")
    print(f"Music added: {'yes' if music_added else 'no'}")
    print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
