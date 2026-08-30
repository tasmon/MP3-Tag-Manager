# MP3 Tag Manager

**A practical batch MP3 tag editor with album art support**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android-lightgrey)]()
![Version](https://img.shields.io/badge/Version-1.0.0-blueviolet)

A clean, modern desktop application for editing MP3 metadata and embedding album art — designed for real-world batch use.

---

## Features

| Feature | Description |
|---------|-------------|
| **Batch file selection** | Add individual MP3s or entire folders (recursive scan) |
| **Edit tags** | Title, Artist, Album, Album Artist, Year, Genre, Track #, Composer, Comment |
| **Smart batch apply** | Empty fields are left unchanged — only filled fields are written |
| **Remove all tags** | Completely strip ID3 tags from multiple files |
| **Album art** | Load JPG/PNG and embed as front cover on all selected files |
| **Remove album art only** | Delete embedded covers while keeping other tags |
| **Live preview** | View current cover art when selecting a file |
| **Modern dark UI** | Built with CustomTkinter |

---

## Screenshots

> *Add your own screenshots here after running the app*

---

## Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements.txt`

```
mutagen>=1.47.0
customtkinter>=5.2.0
Pillow>=10.0.0
```

---

## Installation & Running

### Windows (easiest)

1. Install [Python 3.10+](https://www.python.org/downloads/) (check **Add Python to PATH**).
2. Download or clone this repository.
3. Double-click `Run_MP3_Tag_Manager.bat`  
   **or** open a terminal in the project folder and run:

```bash
pip install -r requirements.txt
python mp3_tag_manager.py
```

### Create a standalone Windows executable

```bash
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "MP3_Tag_Manager" mp3_tag_manager.py
```

The `.exe` will be created in the `dist/` folder.

### Linux / macOS

```bash
pip install -r requirements.txt
python3 mp3_tag_manager.py
```

### Android

See [ANDROID.md](ANDROID.md) for instructions using **Pydroid 3** (recommended) or Termux.

---

## How to Use

1. Click **Add Files** or **Add Folder**.
2. Select a file in the left list to load its current tags and cover.
3. Edit the fields you want to change.
4. Click **Apply to Selected** — changes are written to **all** files in the list.  
   *Leave a field empty to keep the original value.*
5. **Album Art**
   - Click **Load Cover Image** and choose a JPG or PNG.
   - Click **Apply Cover to Selected**.
   - Or use **Remove Cover from Selected** to delete only the embedded art.
6. **Remove All Tags** strips every ID3 tag (including cover) from the selected files.

**Keyboard shortcuts**
- `Ctrl + O` → Add Files  
- `Ctrl + S` → Apply Tags  

Click the **About** button in the top-right corner for version and developer information.

---

## Project Structure

```
MP3_Tag_Manager/
├── mp3_tag_manager.py      # Main application
├── requirements.txt
├── Run_MP3_Tag_Manager.bat # Windows launcher
├── README.md
├── ANDROID.md
└── LICENSE
```

---

## Technical Notes

- Uses **mutagen** for reliable ID3v2 reading and writing.
- Album art is stored as an `APIC` frame (type 3 – Front Cover).
- Existing covers are removed before adding a new one to avoid duplicate frames.
- Only metadata is modified — the audio stream is never touched.

---

## Author

**Tasmon Islam**  
Email: [tasmon@outlook.com](mailto:tasmon@outlook.com)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Contributing

Pull requests and suggestions are welcome. Feel free to open an issue if you find a bug or have a feature request.
