# Run full pipeline: inference -> annotate -> video -> add audio
# Usage: Right-click and Run in PowerShell, or execute `./run_pipeline.ps1` from PowerShell

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host "Working folder: $root"

# Paths
$venvPy = Join-Path $root '..\.venv\Scripts\python.exe'
if (!(Test-Path $venvPy)) { $venvPy = Join-Path $root '.venv\Scripts\python.exe' }
$imagesResized = Join-Path $root 'images_resized'
$outputDet = Join-Path $root 'outputs\detections_ultralytics'
$outputAnnot = Join-Path $root 'outputs\detections_annotated'
$videoOut = Join-Path $root 'outputs\detections_video.mp4'
$finalOut = Join-Path $root 'outputs\detections_video_audio.mp4'
$silent = Join-Path $root 'silent.wav'

if (!(Test-Path $venvPy)) {
    Write-Host "Virtualenv python not found at $venvPy" -ForegroundColor Red
    Write-Host "Run from project root where .venv exists, or adjust script." -ForegroundColor Yellow
    exit 1
}

# 1) Run detection (ultralytics)
Write-Host "Running detection with ultralytics using $venvPy"
& $venvPy (Join-Path $root 'scripts\run_detection.py') --weights yolov8n.pt --source $imagesResized --output $outputDet

# 2) Annotate from label files
Write-Host "Annotating from label files"
& $venvPy (Join-Path $root 'scripts\annotate_from_labels.py')

# 3) Create MP4 from annotated images
Write-Host "Creating MP4 from annotated images"
$img1 = Join-Path $outputAnnot 'img_train.jpg'
$img2 = Join-Path $outputAnnot 'img_val.jpg'
if (!(Test-Path $img1) -or !(Test-Path $img2)) {
    Write-Host "Annotated images not found at $outputAnnot. Listing files:"; Get-ChildItem $outputAnnot
    exit 1
}

# create video: 1 second per image
& ffmpeg -y -loop 1 -t 1 -i $img1 -loop 1 -t 1 -i $img2 -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0,format=yuv420p" -c:v libx264 $videoOut

# 4) Create silent audio and mux
Write-Host "Adding silent audio and muxing"
& ffmpeg -y -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -t 2 $silent
& ffmpeg -y -i $videoOut -i $silent -c:v copy -c:a aac -shortest $finalOut

Write-Host "Pipeline complete. Final file: $finalOut" -ForegroundColor Green
