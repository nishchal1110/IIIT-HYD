# Week 01 Progress Log

Date: 2026-04-25

## Task 01
- Downloaded short YouTube video: https://www.youtube.com/watch?v=jNQXAC9IVRw
- Extracted sample frames with ffmpeg:
  - frames/frame_01.jpg
  - frames/frame_02.jpg
  - frames/frame_03.jpg

## Task 02
- Source video: https://www.youtube.com/watch?v=aqz-KE-bpKQ
- Generated exactly 1800 images at 30 fps for a continuous 60 second segment.
- Reconstructed 60 second video at 30 fps from image sequence:
  - task2_output/reconstructed_from_frames.mp4

## Task 03
- Public song source used: https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3
- Clipped audio to exactly 60 seconds:
  - task3_output/public_song_60s.wav
- Merged clipped audio with Task 02 reconstructed video:
  - task3_output/task3_video_with_audio.mp4
- Compressed version prepared for hosting size limits:
  - task3_output/task3_video_with_audio_compressed.mp4
- Public uploaded video link:
  - https://files.catbox.moe/fr1knb.mp4

Notes:
- Direct Pixabay automation was blocked in this environment by anti-bot protection, so an alternate public portal track was used to complete the pipeline.