"""
Module description: Audio transcription with Open AI Whisper package.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Optional GUI file picker
def pick_file_dialog() -> Path | None:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select audio/video file",
            filetypes=[
                ("Media files", "*.mkv *.mp4 *.mov *.m4a *.mp3 *.wav *.flac *.aac *.ogg *.wma"),
                ("All files", "*.*"),
            ],
        )
        return Path(file_path) if file_path else None
    except Exception:
        return None

def ensure_ffmpeg():
    if shutil.which("ffmpeg") is None:
        sys.exit("FFmpeg not found. Please install FFmpeg and ensure it is in your PATH.")

def extract_track_to_wav(src: Path, track_index: int) -> Path:
    """
    Extract a specific audio track (0-based) to a temporary WAV file using FFmpeg.
    """
    ensure_ffmpeg()
    tmpdir = Path(tempfile.mkdtemp(prefix="whisper_"))
    out_wav = tmpdir / "audio_track.wav"
    # -y overwrite, -vn drop video, -map 0:a:{index} select audio stream
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(src),
        "-vn", "-map", f"0:a:{track_index}",
        "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",  # mono 16k wav (efficient for Whisper)
        str(out_wav),
    ]
    subprocess.run(cmd, check=True)
    return out_wav

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio/video with OpenAI Whisper.")
    parser.add_argument("--input", "-i", type=str, help="Path to input media file. If omitted, a file picker will open.")
    parser.add_argument("--model", "-m", type=str, default="medium", help='Whisper model size (e.g. "small", "medium", "large").')
    parser.add_argument("--language", "-l", type=str, default=None, help="Force language code (e.g. 'en'); default auto-detect.")
    parser.add_argument("--audio-track", type=int, default=None, help="Audio track index to extract (0-based). If omitted, Whisper uses the default/first track.")
    parser.add_argument("--outdir", type=str, default=None, help="Optional output directory for the transcript.")
    parser.add_argument("--device", type=str, default=None, help="Force device, e.g. 'cuda' or 'cpu'.")
    args = parser.parse_args()

    # Get input path (CLI or picker)
    src_path = Path(args.input).expanduser() if args.input else pick_file_dialog()
    if not src_path or not src_path.exists():
        sys.exit("No valid input file selected/provided.")

    # Lazily import whisper to fail fast on missing deps
    try:
        import whisper
        import torch
    except ImportError:
        sys.exit("The 'whisper' package is not installed. Install via: pip install -U openai-whisper")

    # Choose device
    device = args.device if args.device else ("cuda" if torch.cuda.is_available() else "cpu")

    # Prepare input for Whisper: either direct container or extracted track
    media_for_whisper: Path
    tmp_to_cleanup: Path | None = None
    if args.audio_track is not None:
        try:
            media_for_whisper = extract_track_to_wav(src_path, args.audio_track)
            tmp_to_cleanup = media_for_whisper.parent
        except subprocess.CalledProcessError as e:
            sys.exit(f"FFmpeg failed to extract audio track {args.audio_track}: {e}")
    else:
        # Whisper can read containers directly via FFmpeg
        media_for_whisper = src_path

    # Load model
    model = whisper.load_model(args.model, device=device)

    # Transcribe
    result = model.transcribe(
        str(media_for_whisper),
        verbose=True,
        language=args.language,
        # You can add options such as temperature or vad/filtering here if desired
    )

    # Determine output path
    outdir = Path(args.outdir).expanduser() if args.outdir else src_path.parent
    outdir.mkdir(parents=True, exist_ok=True)
    out_txt = outdir / f"{src_path.stem}_transcript.txt"

    # Save transcript
    text = result.get("text", "").strip()
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(text + ("\n" if text and not text.endswith("\n") else ""))

    print(f"Transcript saved to: {out_txt}")

    # Cleanup temp
    if tmp_to_cleanup and tmp_to_cleanup.exists():
        try:
            shutil.rmtree(tmp_to_cleanup)
        except Exception:
            pass

if __name__ == "__main__":
    main()
