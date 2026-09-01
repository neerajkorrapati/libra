import torch
import torch.nn.functional as F
import math


def calculate_psnr(img1: torch.Tensor, img2: torch.Tensor, max_val: float = 1.0) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR).
    img1, img2: Tensors of shape (B, C, H, W) or (C, H, W).
    max_val: Maximum possible pixel value of the images (1.0 for reflectance).
    """
    mse = F.mse_loss(img1, img2)
    if mse == 0:
        return float('inf')
    return 20 * math.log10(max_val) - 10 * math.log10(mse.item())


def calculate_ssim_channel(img1: torch.Tensor, img2: torch.Tensor, window_size: int = 11, max_val: float = 1.0) -> float:
    """
    Calculate Structural Similarity Index (SSIM) for a single channel.
    Simplified PyTorch implementation.
    """
    C1 = (0.01 * max_val) ** 2
    C2 = (0.03 * max_val) ** 2

    mu1 = F.avg_pool2d(img1, window_size, stride=1, padding=window_size//2)
    mu2 = F.avg_pool2d(img2, window_size, stride=1, padding=window_size//2)

    mu1_sq = mu1 ** 2
    mu2_sq = mu2 ** 2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = F.avg_pool2d(img1 ** 2, window_size, stride=1, padding=window_size//2) - mu1_sq
    sigma2_sq = F.avg_pool2d(img2 ** 2, window_size, stride=1, padding=window_size//2) - mu2_sq
    sigma12 = F.avg_pool2d(img1 * img2, window_size, stride=1, padding=window_size//2) - mu1_mu2

    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
    return ssim_map.mean().item()


def calculate_ssim(img1: torch.Tensor, img2: torch.Tensor, max_val: float = 1.0) -> float:
    """
    Calculate Structural Similarity Index (SSIM) across all channels.
    img1, img2: Tensors of shape (B, C, H, W).
    """
    if img1.dim() == 3:
        img1 = img1.unsqueeze(0)
    if img2.dim() == 3:
        img2 = img2.unsqueeze(0)
        
    _, C, _, _ = img1.shape
    ssims = []
    for i in range(C):
        ssims.append(calculate_ssim_channel(img1[:, i:i+1, :, :], img2[:, i:i+1, :, :], max_val=max_val))
    return sum(ssims) / len(ssims)


def calculate_sam(img1: torch.Tensor, img2: torch.Tensor) -> float:
    """
    Calculate Spectral Angle Mapper (SAM) in degrees.
    img1, img2: Tensors of shape (B, C, H, W).
    """
    # Dot product over channels
    dot_product = (img1 * img2).sum(dim=1)
    
    # Norms
    norm1 = torch.norm(img1, p=2, dim=1)
    norm2 = torch.norm(img2, p=2, dim=1)
    
    # Calculate cosine of the angle
    cos_theta = dot_product / (norm1 * norm2 + 1e-8)
    
    # Clamp for numerical stability
    cos_theta = torch.clamp(cos_theta, -1.0, 1.0)
    
    # Calculate angle in radians, then convert to degrees
    sam_map = torch.acos(cos_theta)
    sam_degrees = sam_map * (180.0 / math.pi)
    
    return sam_degrees.mean().item()
