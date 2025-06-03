
#!/usr/bin/env python
"""
process_images.py
Batch‑remove image backgrounds with rembg, sharpen edges via OpenCV,
optionally center the detected object, and write transparent PNGs
to an output folder while showing a live tqdm progress bar.

Usage
-----
python process_images.py --input input --output output [--center]
"""

import argparse
from pathlib import Path

import cv2
import numpy as np
from rembg import remove
from tqdm import tqdm


def unsharp_mask(img_bgr: np.ndarray,
                 strength: float = 1.5,
                 blur_sigma: float = 3.0) -> np.ndarray:
    """Return a BGR image sharpened via un‑sharp mask."""
    blurred = cv2.GaussianBlur(img_bgr, (0, 0),
                               sigmaX=blur_sigma,
                               sigmaY=blur_sigma)
    return cv2.addWeighted(img_bgr, strength,
                           blurred, -(strength - 1), 0)


def center_object(rgba: np.ndarray) -> np.ndarray:
    """Center the non‑transparent region in the original canvas size."""
    alpha = rgba[:, :, 3]
    if not np.any(alpha):            # fully transparent image
        return rgba

    ys, xs = np.where(alpha > 0)
    x_min, x_max = xs.min(), xs.max()
    y_min, y_max = ys.min(), ys.max()

    roi = rgba[y_min:y_max + 1, x_min:x_max + 1]
    H, W = rgba.shape[:2]
    h, w = roi.shape[:2]

    canvas = np.zeros_like(rgba)     # transparent canvas
    offset_x = (W - w) // 2
    offset_y = (H - h) // 2
    canvas[offset_y:offset_y + h, offset_x:offset_x + w] = roi
    return canvas


def process_image(src: Path, dst: Path, center: bool = False) -> None:
    """Remove background, sharpen, (optionally) center, and save PNG."""
    # background removal
    img_bytes = src.read_bytes()
    rgba_bytes = remove(img_bytes)

    # decode to RGBA array
    img_rgba = cv2.imdecode(np.frombuffer(rgba_bytes, np.uint8),
                            cv2.IMREAD_UNCHANGED)

    # ensure alpha channel
    if img_rgba.shape[2] == 3:
        b, g, r = cv2.split(img_rgba)
        alpha = np.full_like(b, 255)
        img_rgba = cv2.merge([b, g, r, alpha])

    # sharpen colour channels
    b, g, r, a = cv2.split(img_rgba)
    sharpened_bgr = unsharp_mask(cv2.merge([b, g, r]))
    b_s, g_s, r_s = cv2.split(sharpened_bgr)
    final_rgba = cv2.merge([b_s, g_s, r_s, a])

    # optional centering
    if center:
        final_rgba = center_object(final_rgba)

    # ensure target folder exists and save
    dst.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(dst), final_rgba)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch‑remove image backgrounds and sharpen text."
    )
    parser.add_argument("-i", "--input", default="input",
                        help="Input folder containing images (default: ./input)")
    parser.add_argument("-o", "--output", default="output",
                        help="Output folder for transparent PNGs (default: ./output)")
    parser.add_argument("--center", action="store_true",
                        help="Center the detected object in the output frame")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    center = args.center

    # create input folder if it doesn't exist
    input_dir.mkdir(parents=True, exist_ok=True)

    # supported extensions
    exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}

    images = sorted(p for p in input_dir.iterdir()
                    if p.suffix.lower() in exts)

    if not images:
        print(f"[INFO] Drop images into '{input_dir.resolve()}' and rerun.")
        return

    for img_path in tqdm(images, desc="Processing images", unit="img"):
        out_name = f"{img_path.stem}_transparent.png"
        out_path = output_dir / out_name
        try:
            process_image(img_path, out_path, center=center)
        except Exception as exc:
            tqdm.write(f"⚠️  Error processing {img_path.name}: {exc}")

    print(f"\n✅  Finished. Files saved to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
