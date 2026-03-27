"""
YOLOv8 PPE Model Trainer
Trains YOLOv8 on the PPE dataset for 5-class detection:
  0: helmet, 1: gloves, 2: vest, 3: boots, 4: goggles
"""

from ultralytics import YOLO
import torch


class PPEModelTrainer:
    """Train YOLOv8 for PPE detection."""

    def __init__(self, model_size='m'):
        """
        Initialize trainer.

        Args:
            model_size: 'n' (nano), 's' (small), 'm' (medium), 'l' (large)
        """
        self.model = YOLO(f'yolov8{model_size}.pt')
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def train(self, data_yaml, epochs=100, batch_size=16, img_size=640):
        """
        Train YOLOv8 model.

        Args:
            data_yaml: Path to dataset YAML file
            epochs: Number of training epochs
            batch_size: Batch size for training
            img_size: Input image size
        """
        results = self.model.train(
            data=data_yaml,
            epochs=epochs,
            imgsz=img_size,
            batch=batch_size,
            device=self.device,
            patience=20,
            save=True,
            save_period=5,

            # Augmentation parameters
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=10,
            translate=0.1,
            scale=0.5,
            flipud=0.5,
            fliplr=0.5,
            mosaic=1.0,

            # Training parameters
            lr0=0.01,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,

            # Validation
            val=True,
            save_conf=True,

            # Output
            verbose=True,
            project='runs/detect',
            name='ppe_detection'
        )

        return results

    def validate(self, model_path, data_yaml):
        """Validate trained model."""
        model = YOLO(model_path)
        metrics = model.val(data=data_yaml)
        return metrics

    def test(self, model_path, test_images_dir):
        """Test on test images."""
        model = YOLO(model_path)
        results = model.predict(source=test_images_dir, conf=0.5)
        return results


if __name__ == '__main__':
    trainer = PPEModelTrainer(model_size='m')

    trainer.train(
        data_yaml='datasets/final_dataset/data.yaml',
        epochs=100,
        batch_size=16,
        img_size=640
    )
