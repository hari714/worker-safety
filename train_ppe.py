"""
PPE Detection Model Training Script

Run options:
  python train_ppe.py          → YOLOv8n (nano, fast, ~4-6 hrs CPU)
  python train_ppe.py --small  → YOLOv8s (small, balanced, ~12-18 hrs CPU)
  python train_ppe.py --medium → YOLOv8m (medium, accurate, ~40-60 hrs CPU)
"""

import sys
import os
import argparse
sys.path.insert(0, os.path.dirname(__file__))

from ppe_detection.yolo_model import PPEModelTrainer


def main():
    parser = argparse.ArgumentParser(description='Train PPE Detection Model')
    parser.add_argument('--small', action='store_true', help='Use YOLOv8s (balanced speed/accuracy)')
    parser.add_argument('--medium', action='store_true', help='Use YOLOv8m (slower but more accurate)')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs (default: 50)')
    parser.add_argument('--batch', type=int, default=8, help='Batch size (default: 8)')
    args = parser.parse_args()

    data_yaml = 'datasets/final_dataset/data.yaml'

    if not os.path.exists(data_yaml):
        print(f"ERROR: Dataset not found at {data_yaml}")
        return

    if args.medium:
        model_size = 'm'
        model_name = 'YOLOv8m (medium)'
    elif args.small:
        model_size = 's'
        model_name = 'YOLOv8s (small)'
    else:
        model_size = 'n'
        model_name = 'YOLOv8n (nano)'

    print("=" * 60)
    print("PPE Detection Model Training")
    print("=" * 60)
    print(f"Dataset: {data_yaml}")
    print(f"Model: {model_name}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch: {args.batch}")
    print(f"Image size: 640x640")
    print("=" * 60)

    trainer = PPEModelTrainer(model_size=model_size)

    results = trainer.train(
        data_yaml=data_yaml,
        epochs=args.epochs,
        batch_size=args.batch,
        img_size=640
    )

    # Copy best model to models/
    best_model = 'runs/detect/ppe_detection/weights/best.pt'
    if os.path.exists(best_model):
        import shutil
        os.makedirs('models', exist_ok=True)
        shutil.copy2(best_model, 'models/ppe_detection_best.pt')
        print(f"\nBest model copied to: models/ppe_detection_best.pt")

    print("\nTraining complete!")


if __name__ == '__main__':
    main()
