import argparse
import os
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split

from ml.datasets.dataset_loader import SentinelDataset, create_lr_hr_pairs
from ml.models.sen2sr.model import SEN2SRModel
from ml.validation.metrics import calculate_psnr, calculate_ssim


def finetune_sen2sr(
    raster_path: str,
    output_dir: str,
    epochs: int = 50,
    batch_size: int = 16,
    lr: float = 1e-4,
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
):
    print(f"Starting SEN2SR fine-tuning on {device}...")
    
    # 1. Prepare data pairs
    pairs_dir = Path(output_dir) / "pairs"
    pairs = create_lr_hr_pairs(raster_path=raster_path, output_dir=pairs_dir)
    
    if not pairs:
        print("No valid LR/HR pairs found. Exiting.")
        return

    # 2. Create Dataset and DataLoader
    full_dataset = SentinelDataset(pairs, augment=True)
    
    # 80/20 train/val split
    val_size = max(1, int(0.2 * len(full_dataset)))
    train_size = len(full_dataset) - val_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    
    # 3. Initialize Model, Optimizer, and Loss
    model = SEN2SRModel().to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.L1Loss() # L1 loss is standard for SR
    
    weights_dir = Path("ml/models/sen2sr/weights")
    weights_dir.mkdir(parents=True, exist_ok=True)
    
    best_psnr = 0.0

    # 4. Training Loop
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        
        for batch in train_loader:
            lr_img = batch["lr"].to(device)
            hr_img = batch["hr"].to(device)
            
            optimizer.zero_grad()
            sr_img = model(lr_img)
            
            loss = criterion(sr_img, hr_img)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * lr_img.size(0)
            
        train_loss /= len(train_loader.dataset)
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_psnr = 0.0
        val_ssim = 0.0
        
        with torch.no_grad():
            for batch in val_loader:
                lr_img = batch["lr"].to(device)
                hr_img = batch["hr"].to(device)
                
                sr_img = model(lr_img)
                loss = criterion(sr_img, hr_img)
                val_loss += loss.item() * lr_img.size(0)
                
                val_psnr += calculate_psnr(sr_img, hr_img) * lr_img.size(0)
                val_ssim += calculate_ssim(sr_img, hr_img) * lr_img.size(0)
                
        val_loss /= len(val_loader.dataset)
        val_psnr /= len(val_loader.dataset)
        val_ssim /= len(val_loader.dataset)
        
        print(f"Epoch [{epoch}/{epochs}] - Train Loss: {train_loss:.4f} - Val Loss: {val_loss:.4f} - PSNR: {val_psnr:.2f}dB - SSIM: {val_ssim:.4f}")
        
        # Save best weights
        if val_psnr > best_psnr:
            best_psnr = val_psnr
            torch.save(model.state_dict(), weights_dir / "sen2sr_best.pth")
            print(" -> Saved new best model weights.")

    print(f"Fine-tuning complete. Best Validation PSNR: {best_psnr:.2f}dB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune SEN2SR model")
    parser.add_argument("--raster_path", type=str, required=True, help="Path to the reference high-res Sentinel-2 raster")
    parser.add_argument("--output_dir", type=str, default="data/preprocessed", help="Directory to save LR/HR pairs")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    args = parser.parse_args()
    
    finetune_sen2sr(
        raster_path=args.raster_path,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr
    )
