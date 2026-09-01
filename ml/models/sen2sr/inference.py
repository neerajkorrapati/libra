import argparse
from pathlib import Path

import numpy as np
import rasterio
import torch

from ml.models.sen2sr.model import SEN2SRModel
from ml.preprocessing.rasterio_utils import read_bands


def run_inference(
    input_raster: str,
    output_raster: str,
    weights_path: str = "ml/models/sen2sr/weights/sen2sr_best.pth",
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
):
    print(f"Running SEN2SR Inference on {device}...")
    
    # 1. Load the trained model
    weights_path = Path(weights_path)
    if not weights_path.exists():
        raise FileNotFoundError(f"Model weights not found at {weights_path}. Please finetune the model first.")
        
    model = SEN2SRModel().to(device)
    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.eval()
    
    # 2. Load the low-resolution input tile (10m -> 2.5m assuming scale=4)
    lr_data = read_bands(input_raster) # shape: (4, H, W)
    
    # Add batch dimension and convert to tensor
    lr_tensor = torch.from_numpy(lr_data).unsqueeze(0).to(device)
    
    # 3. Run Inference
    with torch.no_grad():
        sr_tensor = model(lr_tensor)
        
    # Remove batch dimension and move to CPU
    sr_data = sr_tensor.squeeze(0).cpu().numpy()
    
    # 4. Save the super-resolved output
    # We need to construct the new raster metadata
    with rasterio.open(input_raster) as src:
        meta = src.meta.copy()
        
    # Update metadata for higher resolution (4x scale)
    scale = 4
    new_height = meta["height"] * scale
    new_width = meta["width"] * scale
    
    # Update the affine transform to represent the new pixel size
    new_transform = rasterio.Affine(
        meta["transform"].a / scale,
        meta["transform"].b,
        meta["transform"].c,
        meta["transform"].d,
        meta["transform"].e / scale,
        meta["transform"].f
    )
    
    meta.update({
        "height": new_height,
        "width": new_width,
        "transform": new_transform,
        "dtype": "float32"
    })
    
    output_path = Path(output_raster)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with rasterio.open(output_path, "w", **meta) as dest:
        dest.write(sr_data)
        
    print(f"Super-resolved image saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SEN2SR inference on a Sentinel-2 tile.")
    parser.add_argument("--input", type=str, required=True, help="Path to input Sentinel-2 GeoTIFF")
    parser.add_argument("--output", type=str, required=True, help="Path to save the super-resolved GeoTIFF")
    parser.add_argument("--weights", type=str, default="ml/models/sen2sr/weights/sen2sr_best.pth", help="Path to trained model weights")
    
    args = parser.parse_args()
    
    run_inference(
        input_raster=args.input,
        output_raster=args.output,
        weights_path=args.weights
    )
