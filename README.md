
# Batch Image Background Removal & Sharpening

A lightweight **Python** utility that scans an *input* folder, removes the background from every image with **rembg**, sharpens printed text with **OpenCV** (`unsharp mask`), optionally **centers the detected object**, and saves a transparent **PNG** to an *output* folder – all while displaying a real‑time progress bar.

---

## 📁 Directory Layout

```
remove_bg_batch/
├── input/        # drop your JPEG/PNG/WEBP/TIFF images here
├── output/       # processed files will be written here
├── process_images.py
├── requirements.txt
└── README.md
```

---

## 1  Prerequisites

| Software | Recommended Version | Notes |
|----------|--------------------|-------|
| **Python** | 3.8 or newer | Windows · macOS · Linux |
| **Git** (optional) | 2.x | clone the repo quickly |

---

## 2  Installation

```bash
git clone https://github.com/your-user/remove_bg_batch.git
cd remove_bg_batch

python -m venv .venv          # create isolated env
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

`requirements.txt` lists the latest stable versions of:

```
rembg[pil]   # background removal
opencv-python
numpy
pillow
tqdm         # progress bar
```

---

## 3  Running the script

```bash
# basic run (no centering)
python process_images.py -i input -o output

# center each detected object in the frame
python process_images.py -i input -o output --center
```

### Command‑line options

| Flag | Description | Default |
|------|-------------|---------|
| `-i, --input`  | Path to folder with source images | `input` |
| `-o, --output` | Path where transparent PNGs are saved | `output` |
| `--center`     | If present, crops the foreground object and pastes it dead‑center in the original canvas size | _off_ |

A successful run shows something like:

```
Processing images: 100%|██████████| 25/25 [00:04<00:00,  6.18img/s]
✅  Done! Results in: C:\absolute\path\output
```

---

## 4  How it works

| Step | Description |
|------|-------------|
| 1 | Read the source image bytes |
| 2 | **rembg** returns a PNG with alpha |
| 3 | Ensure the image has an alpha channel |
| 4 | Apply **unsharp mask** on colour channels to enhance printed text |
| 5 | **Optional:** If `--center` is set, find the smallest bounding box of non‑transparent pixels and paste that region in the middle of a blank canvas |
| 6 | Save `{name}_transparent.png` to the output folder |
| 7 | Repeat with a **tqdm** progress bar |

---

## 5  Tips & Customization

* **Process sub‑folders:** swap `input_dir.iterdir()` with `input_dir.rglob('*')` in `main()`.* **Sharper edges:** raise `strength` or lower `blur_sigma` inside `unsharp_mask()`.* **Silent mode:** comment out `tqdm.write(...)` lines.

---

## 6  Updating dependencies

```bash
pip list --outdated
pip install --upgrade --upgrade-strategy eager -r requirements.txt
```

---

## 7  License

Released under the **MIT License**. Feel free to use, modify, and share.
