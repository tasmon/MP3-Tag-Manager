# Running MP3 Tag Manager on Android

## Recommended method: Pydroid 3

1. Install **Pydroid 3** (Python 3 IDE) from the Play Store or F-Droid.
2. Open Pydroid 3 → Menu → Pip → Install:
   - `mutagen`
   - `customtkinter`
   - `pillow`
3. Copy `mp3_tag_manager.py` to your phone (e.g. Download folder).
4. In Pydroid 3 open the file and press the Run (▶) button.

The GUI will appear and you can use all features (file picker works with Android storage permissions).

## Alternative: Termux

```bash
pkg update && pkg install python python-tkinter
pip install mutagen customtkinter pillow
# Then run under Termux:X11 or similar X server
python mp3_tag_manager.py
```

## Native APK (advanced)

You can package the same Python code into an APK using **Buildozer** + **Kivy** (or BeeWare), but that requires a Linux machine with the Android NDK/SDK. The current CustomTkinter version is the most practical for most users.
