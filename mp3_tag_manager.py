#!/usr/bin/env python3
"""
MP3 Tag Manager
A practical batch MP3 tag editor with album art support.
Works on Windows, Linux and macOS.

Author : Tasmon Islam <tasmon@outlook.com>
Version: 1.0.0
"""

import os
import sys
import io
from pathlib import Path
from typing import List, Optional, Dict

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from mutagen.mp3 import MP3
from mutagen.id3 import (
    ID3, ID3NoHeaderError, APIC, error as ID3Error,
    TIT2, TPE1, TALB, TPE2, TDRC, TCON, TRCK, COMM, TCOM, TYER
)
from mutagen.easyid3 import EasyID3

# ── Appearance ──────────────────────────────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

APP_NAME = "MP3 Tag Manager"
VERSION = "1.0.0"
AUTHOR = "Tasmon Islam"
AUTHOR_EMAIL = "tasmon@outlook.com"

# Common EasyID3 keys we support
TAG_FIELDS = [
    ("title", "Title"),
    ("artist", "Artist"),
    ("album", "Album"),
    ("albumartist", "Album Artist"),
    ("date", "Year / Date"),
    ("genre", "Genre"),
    ("tracknumber", "Track #"),
    ("composer", "Composer"),
    ("comment", "Comment"),
]


class MP3TagManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("1180x720")
        self.minsize(980, 620)

        self.files: List[str] = []
        self.current_index: Optional[int] = None
        self.album_art_path: Optional[str] = None
        self.album_art_data: Optional[bytes] = None

        self._build_ui()
        self._bind_events()

    # ── UI Construction ─────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left panel – file list
        left = ctk.CTkFrame(self, width=320, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_propagate(False)
        left.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(left, text="Files", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=16, pady=(16, 8), sticky="w"
        )

        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.grid(row=1, column=0, padx=12, pady=4, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_frame, text="Add Files", command=self.add_files, height=32).grid(
            row=0, column=0, padx=(0, 4), sticky="ew"
        )
        ctk.CTkButton(btn_frame, text="Add Folder", command=self.add_folder, height=32).grid(
            row=0, column=1, padx=(4, 0), sticky="ew"
        )

        self.file_listbox = ctk.CTkScrollableFrame(left, fg_color=("gray90", "gray17"))
        self.file_listbox.grid(row=2, column=0, padx=12, pady=8, sticky="nsew")

        clear_btn = ctk.CTkButton(
            left, text="Clear List", fg_color="transparent",
            border_width=1, command=self.clear_list, height=30
        )
        clear_btn.grid(row=3, column=0, padx=12, pady=(0, 12), sticky="ew")

        # Right panel – editor
        right = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        # Top bar
        topbar = ctk.CTkFrame(right, height=48, fg_color="transparent")
        topbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        topbar.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            topbar, text="No files loaded", anchor="w",
            font=ctk.CTkFont(size=13)
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            topbar, text="About", width=80, height=30,
            fg_color="transparent", border_width=1,
            command=self.show_about
        ).grid(row=0, column=1, sticky="e", padx=(8, 0))

        # Main content (tags + art)
        content = ctk.CTkFrame(right, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=0)
        content.grid_rowconfigure(0, weight=1)

        # Tag editor
        tag_frame = ctk.CTkFrame(content)
        tag_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tag_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            tag_frame, text="Tag Editor",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=16, pady=(14, 10), sticky="w")

        self.entries: Dict[str, ctk.CTkEntry] = {}
        for i, (key, label) in enumerate(TAG_FIELDS, start=1):
            ctk.CTkLabel(tag_frame, text=label, width=110, anchor="w").grid(
                row=i, column=0, padx=(16, 8), pady=5, sticky="w"
            )
            entry = ctk.CTkEntry(tag_frame, height=32)
            entry.grid(row=i, column=1, padx=(0, 16), pady=5, sticky="ew")
            self.entries[key] = entry

        # Batch note
        ctk.CTkLabel(
            tag_frame,
            text="Tip: Leave a field empty to keep existing value when applying to multiple files.",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).grid(row=len(TAG_FIELDS) + 1, column=0, columnspan=2, padx=16, pady=(8, 4), sticky="w")

        # Action buttons for tags
        tag_btn_frame = ctk.CTkFrame(tag_frame, fg_color="transparent")
        tag_btn_frame.grid(row=len(TAG_FIELDS) + 2, column=0, columnspan=2, padx=16, pady=12, sticky="ew")
        tag_btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            tag_btn_frame, text="Apply to Selected",
            command=self.apply_tags, height=36
        ).grid(row=0, column=0, padx=(0, 4), sticky="ew")

        ctk.CTkButton(
            tag_btn_frame, text="Remove All Tags",
            fg_color="#8B0000", hover_color="#A52A2A",
            command=self.remove_all_tags, height=36
        ).grid(row=0, column=1, padx=4, sticky="ew")

        ctk.CTkButton(
            tag_btn_frame, text="Clear Fields",
            fg_color="transparent", border_width=1,
            command=self.clear_fields, height=36
        ).grid(row=0, column=2, padx=(4, 0), sticky="ew")

        # Album Art panel
        art_frame = ctk.CTkFrame(content, width=260)
        art_frame.grid(row=0, column=1, sticky="nsew")
        art_frame.grid_propagate(False)
        art_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            art_frame, text="Album Art",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(14, 10), sticky="w")

        self.art_canvas = ctk.CTkLabel(
            art_frame, text="No cover", width=220, height=220,
            fg_color=("gray85", "gray20"), corner_radius=8
        )
        self.art_canvas.grid(row=1, column=0, padx=20, pady=8)

        art_btn_frame = ctk.CTkFrame(art_frame, fg_color="transparent")
        art_btn_frame.grid(row=2, column=0, padx=16, pady=10, sticky="ew")
        art_btn_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            art_btn_frame, text="Load Cover Image",
            command=self.load_album_art, height=34
        ).grid(row=0, column=0, sticky="ew", pady=(0, 6))

        ctk.CTkButton(
            art_btn_frame, text="Apply Cover to Selected",
            command=self.apply_album_art, height=34
        ).grid(row=1, column=0, sticky="ew", pady=3)

        ctk.CTkButton(
            art_btn_frame, text="Remove Cover from Selected",
            fg_color="#8B0000", hover_color="#A52A2A",
            command=self.remove_album_art, height=34
        ).grid(row=2, column=0, sticky="ew", pady=3)

        ctk.CTkLabel(
            art_frame,
            text="Supported: JPG / PNG\nApplied to all selected files.",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            justify="center"
        ).grid(row=3, column=0, padx=12, pady=(8, 16))

        # Bottom status bar
        self.bottom_status = ctk.CTkLabel(
            right, text="Ready", anchor="w",
            font=ctk.CTkFont(size=12), text_color="gray60"
        )
        self.bottom_status.grid(row=2, column=0, sticky="ew", pady=(8, 0))

    def _bind_events(self):
        self.bind("<Control-o>", lambda e: self.add_files())
        self.bind("<Control-s>", lambda e: self.apply_tags())

    # ── File Management ─────────────────────────────────────────────────────
    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select MP3 files",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        if paths:
            self._add_paths(list(paths))

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing MP3s")
        if folder:
            paths = []
            for root, _, files in os.walk(folder):
                for f in files:
                    if f.lower().endswith(".mp3"):
                        paths.append(os.path.join(root, f))
            if paths:
                self._add_paths(paths)
            else:
                messagebox.showinfo("Info", "No MP3 files found in the selected folder.")

    def _add_paths(self, paths: List[str]):
        added = 0
        for p in paths:
            if p not in self.files and os.path.isfile(p):
                self.files.append(p)
                added += 1
        self._refresh_file_list()
        self.status_label.configure(text=f"{len(self.files)} file(s) loaded")
        if added:
            self.bottom_status.configure(text=f"Added {added} file(s)")

    def clear_list(self):
        self.files.clear()
        self.current_index = None
        self._refresh_file_list()
        self.clear_fields()
        self._clear_art_preview()
        self.status_label.configure(text="No files loaded")
        self.bottom_status.configure(text="List cleared")

    def _refresh_file_list(self):
        for widget in self.file_listbox.winfo_children():
            widget.destroy()

        for i, path in enumerate(self.files):
            name = os.path.basename(path)
            btn = ctk.CTkButton(
                self.file_listbox,
                text=name,
                anchor="w",
                height=30,
                fg_color="transparent",
                hover_color=("gray75", "gray30"),
                command=lambda idx=i: self.select_file(idx)
            )
            btn.pack(fill="x", padx=4, pady=1)

    def select_file(self, index: int):
        if 0 <= index < len(self.files):
            self.current_index = index
            self._load_tags(self.files[index])
            self.bottom_status.configure(text=f"Selected: {os.path.basename(self.files[index])}")

    # ── Tag Reading / Writing ───────────────────────────────────────────────
    def _load_tags(self, filepath: str):
        self.clear_fields()
        try:
            audio = EasyID3(filepath)
        except ID3NoHeaderError:
            audio = EasyID3()
            audio.save(filepath)  # create empty tags
            audio = EasyID3(filepath)
        except Exception as e:
            self.bottom_status.configure(text=f"Error reading tags: {e}")
            return

        for key, _ in TAG_FIELDS:
            value = audio.get(key, [""])[0] if key in audio else ""
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, value)

        # Load existing album art
        self._load_existing_art(filepath)

    def _load_existing_art(self, filepath: str):
        self._clear_art_preview()
        try:
            tags = ID3(filepath)
            for key in tags.keys():
                if key.startswith("APIC"):
                    apic = tags[key]
                    data = apic.data
                    self._show_art_preview(data)
                    return
        except Exception:
            pass

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, "end")

    def apply_tags(self):
        if not self.files:
            messagebox.showwarning("No files", "Please add some MP3 files first.")
            return

        # Collect non-empty values
        updates = {}
        for key, entry in self.entries.items():
            val = entry.get().strip()
            if val:  # only apply non-empty
                updates[key] = val

        if not updates:
            messagebox.showinfo("Nothing to apply", "Fill at least one field to apply.")
            return

        success = 0
        errors = []
        for path in self.files:
            try:
                try:
                    audio = EasyID3(path)
                except ID3NoHeaderError:
                    audio = EasyID3()
                    audio.save(path)
                    audio = EasyID3(path)

                for k, v in updates.items():
                    audio[k] = v
                audio.save()
                success += 1
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")

        msg = f"Tags applied to {success}/{len(self.files)} file(s)."
        if errors:
            msg += "\n\nErrors:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                msg += f"\n... and {len(errors)-5} more"
        messagebox.showinfo("Done", msg)
        self.bottom_status.configure(text=msg.split(".")[0])

        # Refresh current if selected
        if self.current_index is not None:
            self._load_tags(self.files[self.current_index])

    def remove_all_tags(self):
        if not self.files:
            messagebox.showwarning("No files", "Please add some MP3 files first.")
            return

        if not messagebox.askyesno(
            "Confirm",
            f"Remove ALL tags (including album art) from {len(self.files)} file(s)?\n\nThis cannot be undone."
        ):
            return

        success = 0
        for path in self.files:
            try:
                audio = MP3(path, ID3=ID3)
                audio.delete()
                audio.save()
                success += 1
            except Exception:
                # try alternative
                try:
                    tags = ID3(path)
                    tags.delete()
                    tags.save()
                    success += 1
                except Exception:
                    pass

        messagebox.showinfo("Done", f"Removed all tags from {success}/{len(self.files)} file(s).")
        self.clear_fields()
        self._clear_art_preview()
        self.bottom_status.configure(text=f"Cleared tags from {success} file(s)")

    # ── Album Art ───────────────────────────────────────────────────────────
    def load_album_art(self):
        path = filedialog.askopenfilename(
            title="Select album cover",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "rb") as f:
                data = f.read()
            # Validate it's an image
            img = Image.open(io.BytesIO(data))
            img.verify()
            self.album_art_path = path
            self.album_art_data = data
            self._show_art_preview(data)
            self.bottom_status.configure(text=f"Cover loaded: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image:\n{e}")

    def _show_art_preview(self, data: bytes):
        try:
            img = Image.open(io.BytesIO(data))
            img.thumbnail((210, 210), Image.Resampling.LANCZOS)
            # Convert to CTkImage for high-DPI support
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.art_canvas.configure(image=ctk_img, text="")
            self.art_canvas.image = ctk_img  # keep reference
        except Exception:
            self.art_canvas.configure(image=None, text="Invalid image")

    def _clear_art_preview(self):
        self.art_canvas.configure(image=None, text="No cover")
        self.album_art_data = None
        self.album_art_path = None

    def apply_album_art(self):
        if not self.files:
            messagebox.showwarning("No files", "Please add some MP3 files first.")
            return
        if not self.album_art_data:
            messagebox.showwarning("No cover", "Please load a cover image first.")
            return

        mime = "image/jpeg"
        if self.album_art_path and self.album_art_path.lower().endswith(".png"):
            mime = "image/png"

        success = 0
        errors = []
        for path in self.files:
            try:
                try:
                    tags = ID3(path)
                except ID3NoHeaderError:
                    tags = ID3()

                # Remove existing APIC frames first (important!)
                tags.delall("APIC")

                tags.add(
                    APIC(
                        encoding=3,          # UTF-8
                        mime=mime,
                        type=3,              # Front cover
                        desc="Cover",
                        data=self.album_art_data
                    )
                )
                tags.save(path, v2_version=3)
                success += 1
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")

        msg = f"Cover applied to {success}/{len(self.files)} file(s)."
        if errors:
            msg += "\n\nSome errors occurred (first 3):\n" + "\n".join(errors[:3])
        messagebox.showinfo("Done", msg)
        self.bottom_status.configure(text=msg.split(".")[0])

        if self.current_index is not None:
            self._load_existing_art(self.files[self.current_index])

    def remove_album_art(self):
        if not self.files:
            messagebox.showwarning("No files", "Please add some MP3 files first.")
            return

        if not messagebox.askyesno(
            "Confirm",
            f"Remove album art from {len(self.files)} selected file(s)?"
        ):
            return

        success = 0
        for path in self.files:
            try:
                tags = ID3(path)
                tags.delall("APIC")
                tags.save(path)
                success += 1
            except Exception:
                pass

        messagebox.showinfo("Done", f"Removed album art from {success}/{len(self.files)} file(s).")
        self._clear_art_preview()
        self.bottom_status.configure(text=f"Removed covers from {success} file(s)")

    # ── About Dialog ─────────────────────────────────────────────────────────
    def show_about(self):
        about = ctk.CTkToplevel(self)
        about.title("About")
        about.geometry("420x340")
        about.resizable(False, False)
        about.transient(self)
        about.grab_set()

        # Center relative to main window
        about.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 420) // 2
        y = self.winfo_y() + (self.winfo_height() - 340) // 2
        about.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(about, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=30, pady=25)

        ctk.CTkLabel(
            frame, text=APP_NAME,
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(5, 2))

        ctk.CTkLabel(
            frame, text=f"Version {VERSION}",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        ).pack(pady=(0, 15))

        ctk.CTkLabel(
            frame,
            text="A practical batch MP3 tag editor\nwith album art support.",
            font=ctk.CTkFont(size=13),
            justify="center"
        ).pack(pady=(0, 18))

        info = ctk.CTkFrame(frame, corner_radius=8)
        info.pack(fill="x", pady=5)

        ctk.CTkLabel(
            info, text="Developer",
            font=ctk.CTkFont(size=12), text_color="gray60"
        ).pack(anchor="w", padx=16, pady=(12, 0))

        ctk.CTkLabel(
            info, text=AUTHOR,
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w", padx=16, pady=(2, 0))

        ctk.CTkLabel(
            info, text=AUTHOR_EMAIL,
            font=ctk.CTkFont(size=13),
            text_color="#3B8ED0"
        ).pack(anchor="w", padx=16, pady=(2, 14))

        ctk.CTkLabel(
            frame,
            text="Built with Python • mutagen • CustomTkinter",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        ).pack(pady=(18, 5))

        ctk.CTkButton(
            frame, text="Close", width=100, height=32,
            command=about.destroy
        ).pack(pady=(10, 0))


def main():
    app = MP3TagManager()
    app.mainloop()


if __name__ == "__main__":
    main()
