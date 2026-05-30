# Week 02 Tasks 1, 2, 3 Report

Date: 2026-04-25

## Task (a): Python virtual environment using venv

Virtual environment location:

- `C:\Users\NISHCHAL\OneDrive\Desktop\IIIT-HYD INTERNSHIP\.venv`

Activation command used on Windows PowerShell:

```powershell
Set-Location "C:\Users\NISHCHAL\OneDrive\Desktop\IIIT-HYD INTERNSHIP"
. .\.venv\Scripts\Activate.ps1
```

Verification:

- Python version in venv: `Python 3.13.13`

## Task (b): Install ultralytics package

Installation command used:

```powershell
python -m pip install -U ultralytics
```

Verification:

```powershell
python -c "import ultralytics; print(ultralytics.__version__)"
```

- Installed version: `8.4.41`

## Task (c): Object detection with pretrained YOLO model

Script used:

- `week-02/task3_yolo_detection.py`

Run command:

```powershell
python .\week-02\task3_yolo_detection.py
```

Input image:

- `week-01/frames/frame_01.jpg`

Model used from current Ultralytics glossary examples:

- `yolo11n.pt` (pretrained)

Key output summary:

- Inference: `1 person` detected
- Confidence: `0.9295`

Generated output files:

- `week-02/task3_output/predict/frame_01.jpg`
- `week-02/task3_output/prediction_summary.txt`
- `week-02/task3_output_run.log`

## Notes for submission

Push the Week 2 files to GitHub so staff can verify timely submission.

## Early completion challenge: multi-image detection + video + music

Script used:

- `week-02/task4_multi_image_video.py`

Run command:

```powershell
python .\week-02\task4_multi_image_video.py
```

Input images (created in Week 1):

- `week-01/frames/frame_01.jpg`
- `week-01/frames/frame_02.jpg`
- `week-01/frames/frame_03.jpg`
- `week-01/frames/frame_04.jpg`

Output artifacts:

- `week-02/task4_output/annotated_frames/` (annotated images)
- `week-02/task4_output/annotated_video_silent.mp4`
- `week-02/task4_output/background_music.wav`
- `week-02/task4_output/annotated_video_with_music.mp4`
- `week-02/task4_output/task4_summary.txt`
- `week-02/task4_output_run.log`

Run status:

- Images processed: `4`
- Music added: `yes`
- Final post-ready video: `week-02/task4_output/annotated_video_with_music.mp4`
