"""
Merge fresh goggles, gloves & boots data from 3 datasets into existing dataset.

Datasets:
1. Ultralytics Construction-PPE (classes 0-4 match ours, filter out 5-10)
2. Kaggle PPE YOLOv8 (remap: 1→1 gloves, 2→4 goggles)
3. SH17 (remap: 8→4 goggles, 9→1 gloves)

Our class mapping:
  0: helmet, 1: gloves, 2: vest, 3: boots, 4: goggles
"""

import os
import shutil

EXISTING_DIR = "datasets/final_dataset"
TARGET_CLASSES = {1, 3, 4}  # gloves, boots, goggles — only copy images with these


def copy_image(base, src_img_dir, dst_img_dir):
    """Find and copy image file, return True if found."""
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        src = os.path.join(src_img_dir, base + ext)
        if os.path.exists(src):
            dst = os.path.join(dst_img_dir, base + ext)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
            return True
    return False


def merge_ultralytics():
    """Ultralytics Construction-PPE: classes 0-4 match, drop 5-10."""
    print("\n[1/3] Ultralytics Construction-PPE")
    FRESH = "datasets/fresh_ppe/construction-ppe"
    KEEP = {0, 1, 2, 3, 4}
    stats = {"images": 0, "goggles": 0, "gloves": 0, "boots": 0}

    split_map = {"train": "train", "val": "val", "test": "test"}
    for src_split, dst_split in split_map.items():
        lbl_dir = os.path.join(FRESH, "labels", src_split)
        img_dir = os.path.join(FRESH, "images", src_split)
        dst_lbl = os.path.join(EXISTING_DIR, "labels", dst_split)
        dst_img = os.path.join(EXISTING_DIR, "images", dst_split)
        os.makedirs(dst_lbl, exist_ok=True)
        os.makedirs(dst_img, exist_ok=True)

        if not os.path.isdir(lbl_dir):
            continue

        for fname in os.listdir(lbl_dir):
            if not fname.endswith('.txt'):
                continue
            lines = open(os.path.join(lbl_dir, fname)).readlines()
            filtered = []
            has_target = False
            for line in lines:
                parts = line.strip().split()
                if not parts:
                    continue
                cls = int(parts[0])
                if cls in KEEP:
                    filtered.append(line.strip())
                if cls in TARGET_CLASSES:
                    has_target = True

            if not has_target or not filtered:
                continue

            base = os.path.splitext(fname)[0]
            new_base = "ultra_" + base
            new_lbl = os.path.join(dst_lbl, new_base + ".txt")
            if os.path.exists(new_lbl):
                continue

            if copy_image(base, img_dir, dst_img):
                # Rename image too
                for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    old_img = os.path.join(dst_img, base + ext)
                    new_img = os.path.join(dst_img, new_base + ext)
                    if os.path.exists(old_img) and not os.path.exists(new_img):
                        os.rename(old_img, new_img)
                        break

                with open(new_lbl, 'w') as f:
                    f.write('\n'.join(filtered) + '\n')
                stats["images"] += 1
                for line in filtered:
                    c = int(line.split()[0])
                    if c == 4: stats["goggles"] += 1
                    elif c == 1: stats["gloves"] += 1
                    elif c == 3: stats["boots"] += 1

    print(f"  Added: {stats['images']} images | goggles: +{stats['goggles']}, gloves: +{stats['gloves']}, boots: +{stats['boots']}")
    return stats


def merge_kaggle():
    """Kaggle PPE YOLOv8: remap class 1→1(gloves), 2→4(goggles)."""
    print("\n[2/3] Kaggle PPE YOLOv8")
    FRESH = "datasets/fresh_ppe/kaggle_ppe/ppe_yolov8"
    # Kaggle classes: 1=Gloves, 2=Goggles
    REMAP = {1: 1, 2: 4}
    stats = {"images": 0, "goggles": 0, "gloves": 0}

    split_map = {"train": "train", "valid": "val", "test": "test"}
    for src_split, dst_split in split_map.items():
        lbl_dir = os.path.join(FRESH, src_split, "labels")
        img_dir = os.path.join(FRESH, src_split, "images")
        dst_lbl = os.path.join(EXISTING_DIR, "labels", dst_split)
        dst_img = os.path.join(EXISTING_DIR, "images", dst_split)
        os.makedirs(dst_lbl, exist_ok=True)
        os.makedirs(dst_img, exist_ok=True)

        if not os.path.isdir(lbl_dir):
            continue

        for fname in os.listdir(lbl_dir):
            if not fname.endswith('.txt'):
                continue
            try:
                lines = open(os.path.join(lbl_dir, fname)).readlines()
            except (FileNotFoundError, OSError):
                continue
            filtered = []
            has_target = False
            for line in lines:
                parts = line.strip().split()
                if not parts:
                    continue
                cls = int(parts[0])
                if cls in REMAP:
                    new_cls = REMAP[cls]
                    parts[0] = str(new_cls)
                    filtered.append(' '.join(parts))
                    if new_cls in TARGET_CLASSES:
                        has_target = True

            if not has_target or not filtered:
                continue

            base = os.path.splitext(fname)[0]
            # Truncate long names to avoid Windows path limits
            if len(base) > 80:
                base_short = base[:80]
            else:
                base_short = base
            new_base = "kag_" + base_short
            new_lbl = os.path.join(dst_lbl, new_base + ".txt")
            if os.path.exists(new_lbl):
                continue

            if copy_image(base, img_dir, dst_img):
                for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    old_img = os.path.join(dst_img, base + ext)
                    new_img = os.path.join(dst_img, new_base + ext)
                    if os.path.exists(old_img) and not os.path.exists(new_img):
                        os.rename(old_img, new_img)
                        break

                with open(new_lbl, 'w') as f:
                    f.write('\n'.join(filtered) + '\n')
                stats["images"] += 1
                for line in filtered:
                    c = int(line.split()[0])
                    if c == 4: stats["goggles"] += 1
                    elif c == 1: stats["gloves"] += 1

    print(f"  Added: {stats['images']} images | goggles: +{stats['goggles']}, gloves: +{stats['gloves']}")
    return stats


def merge_sh17():
    """SH17: remap class 8→4(goggles), 9→1(gloves). Single folder, split via txt files."""
    print("\n[3/3] SH17 Dataset")
    FRESH = "datasets/fresh_ppe/sh17/sh17_data"
    # SH17 classes: 8=glasses(→goggles), 9=gloves
    REMAP = {8: 4, 9: 1}
    stats = {"images": 0, "goggles": 0, "gloves": 0}

    lbl_dir = os.path.join(FRESH, "labels")
    img_dir = os.path.join(FRESH, "images")

    # Read train/val splits
    train_files = set()
    val_files = set()
    train_txt = os.path.join(FRESH, "train_files.txt")
    val_txt = os.path.join(FRESH, "val_files.txt")
    if os.path.exists(train_txt):
        train_files = {l.strip() for l in open(train_txt) if l.strip()}
    if os.path.exists(val_txt):
        val_files = {l.strip() for l in open(val_txt) if l.strip()}

    if not os.path.isdir(lbl_dir):
        print("  Labels dir not found!")
        return stats

    for fname in os.listdir(lbl_dir):
        if not fname.endswith('.txt'):
            continue
        lines = open(os.path.join(lbl_dir, fname)).readlines()
        filtered = []
        has_target = False
        for line in lines:
            parts = line.strip().split()
            if not parts:
                continue
            cls = int(parts[0])
            if cls in REMAP:
                new_cls = REMAP[cls]
                parts[0] = str(new_cls)
                filtered.append(' '.join(parts))
                if new_cls in TARGET_CLASSES:
                    has_target = True

        if not has_target or not filtered:
            continue

        base = os.path.splitext(fname)[0]

        # Determine split
        if base in val_files or base + ".jpg" in val_files:
            dst_split = "val"
        else:
            dst_split = "train"

        dst_lbl = os.path.join(EXISTING_DIR, "labels", dst_split)
        dst_img = os.path.join(EXISTING_DIR, "images", dst_split)
        os.makedirs(dst_lbl, exist_ok=True)
        os.makedirs(dst_img, exist_ok=True)

        new_base = "sh17_" + base
        new_lbl = os.path.join(dst_lbl, new_base + ".txt")
        if os.path.exists(new_lbl):
            continue

        if copy_image(base, img_dir, dst_img):
            for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                old_img = os.path.join(dst_img, base + ext)
                new_img = os.path.join(dst_img, new_base + ext)
                if os.path.exists(old_img) and not os.path.exists(new_img):
                    os.rename(old_img, new_img)
                    break

            with open(new_lbl, 'w') as f:
                f.write('\n'.join(filtered) + '\n')
            stats["images"] += 1
            for line in filtered:
                c = int(line.split()[0])
                if c == 4: stats["goggles"] += 1
                elif c == 1: stats["gloves"] += 1

    print(f"  Added: {stats['images']} images | goggles: +{stats['goggles']}, gloves: +{stats['gloves']}")
    return stats


if __name__ == "__main__":
    print("=" * 55)
    print("  Merging fresh data into existing dataset")
    print("=" * 55)

    s1 = merge_ultralytics()
    s2 = merge_kaggle()
    s3 = merge_sh17()

    total_imgs = s1["images"] + s2["images"] + s3["images"]
    total_goggles = s1["goggles"] + s2["goggles"] + s3["goggles"]
    total_gloves = s1["gloves"] + s2["gloves"] + s3["gloves"]
    total_boots = s1.get("boots", 0)

    print("\n" + "=" * 55)
    print(f"  TOTAL: +{total_imgs} images merged")
    print(f"  Goggles: +{total_goggles}")
    print(f"  Gloves:  +{total_gloves}")
    print(f"  Boots:   +{total_boots}")
    print("=" * 55)
    print("\nDone! Ready to retrain.")
