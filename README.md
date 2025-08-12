# 🎙 Whisper + FFmpeg Transcription Script

This project uses [OpenAI Whisper](https://github.com/openai/whisper) and FFmpeg to transcribe audio and video files (including `.mkv`) into text.  
It supports direct file selection via a dialog or a command-line argument, and will save the transcript using the same base filename as the input.

---

## ✅ Prerequisites (Windows, PyCharm)

1. **Install Python 3.10 or 3.11**  
   - Download: [python.org/downloads](https://www.python.org/downloads)  
   - Tick **"Add Python to PATH"** during install.  

2. **Create a Virtual Environment** (PyCharm or terminal)  
   ```bash
   python -m venv .venv_3.11
   ```

3. **Install Git**  
   - Download: [git-scm.com](https://git-scm.com)  
   - Tick **"Git from the command line"** during install.  

4. **Install Whisper**  
   ```bash
   pip install git+https://github.com/openai/whisper.git
   ```

5. **Install FFmpeg**  
   - Download static build: [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)  
   - Extract, add the **`bin/`** folder to system **PATH**.  
   - Verify:
     ```bash
     ffmpeg -version
     ```

6. **Install Tkinter** (for file picker, if not already installed)  
   ```bash
   pip install tk
   ```

7. **Place Your Media File**  
   - Any audio/video format supported by FFmpeg (`.mkv`, `.mp4`, `.wav`, `.m4a`, `.mp3`...)  
   - Select file via dialog or pass with `--input` in terminal.

8. **Run the Script**  
   ```bash
   python transcribe.py --input "path/to/file.mkv"
   ```
   - Transcript will be saved with the **same name** as the original file (but `.txt`).

---

## 💡 Notes
- FFmpeg is **mandatory** for all non-WAV formats.
- GPU acceleration is used automatically if CUDA is available.
- To avoid committing personal IDE settings, add `.idea/` to your `.gitignore`.
