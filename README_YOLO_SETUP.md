Overview

This folder contains helper templates and scripts to prepare a YOLO-style dataset.

Steps

1) Labeling (Label Studio)
- Create and activate a virtualenv and install label-studio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install label-studio
label-studio start
```
- Open https://localhost:8080 in Chrome, create a project, add 2 classes, and export annotations in YOLO format.

2) Place files
- Images: `images/train`, `images/val`
- Labels: `labels/train`, `labels/val` (each image has a corresponding `.txt`)
- Copy `data_template.yaml` to `data.yaml` and edit paths and `names`.

3) Resize images (optional, recommended)
- Using ffmpeg (PowerShell):

```powershell
.\scripts\resize_images.ps1 -InputDir images -OutputDir images_resized -Width 384
```

4) Generate train/val lists

```powershell
python .\scripts\generate_data_files.py
```

5) Validate dataset

```powershell
pip install -r requirements.txt
python .\scripts\validate_dataset.py
```

If you want, I can run the validation scripts on any dataset path you provide, or create train/val files automatically from your images. Please tell me which action to take next.