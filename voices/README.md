# Voice Samples Guide

## Requirements

For best results, voice samples should be:

- **Duration**: 3-10 seconds
- **Format**: WAV (16-bit PCM)
- **Sample Rate**: 16kHz or higher
- **Quality**: Clear audio, minimal background noise
- **Content**: Natural speech (not singing)

## Recommended Sources

| Celebrity | Best Source |
|-----------|-------------|
| Modi | Mann Ki Baat clips (YouTube) |
| Amitabh | KBC clips, interviews |
| SRK | Movie dialogues, interviews |
| Jethalal | TMKOC episodes |
| Morgan Freeman | Documentary narrations |
| Trump | Rally speeches, interviews |

## How to Extract Audio

### Using yt-dlp (Recommended)

```bash
# Download audio from YouTube
yt-dlp -x --audio-format wav "VIDEO_URL"

# Trim to specific duration using ffmpeg
ffmpeg -i input.wav -ss 00:00:10 -t 00:00:05 -c copy output.wav
```

### Audio Cleanup Tips

1. Remove background music/noise
2. Ensure only one speaker
3. Trim silence from start/end
4. Normalize volume levels

## File Naming

Use these exact filenames:

- `modi.wav`
- `amitabh.wav`
- `srk.wav`
- `jethalal.wav`
- `morgan_freeman.wav`
- `trump.wav`

## Transcripts (Optional)

For better cloning quality, create a `transcripts.json`:

```json
{
  "modi": "Mitron, aaj main aapke saath...",
  "amitabh": "Computer ji, yeh sawaal...",
  "srk": "Kuch kuch hota hai...",
  "jethalal": "Ae ma mataji...",
  "morgan_freeman": "In the beginning...",
  "trump": "Let me tell you..."
}
```
