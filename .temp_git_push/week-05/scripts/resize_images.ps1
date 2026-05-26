param(
  [string]$InputDir = "images",
  [string]$OutputDir = "images_resized",
  [int]$Width = 384
)

if (!(Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }

Get-ChildItem -Path $InputDir -Recurse -Include *.jpg,*.jpeg,*.png | ForEach-Object {
  $rel = $_.FullName
  $outPath = Join-Path $OutputDir $_.Name
  $vf = "scale=${Width}:-1"
  & ffmpeg -hide_banner -loglevel error -y -i "$rel" -vf $vf "$outPath"
}
