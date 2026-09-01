import torch
import torch.nn as nn


class ResidualBlock(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        res = self.conv1(x)
        res = self.relu(res)
        res = self.conv2(res)
        return x + res


class SEN2SRModel(nn.Module):
    """
    SEN2SR (Sentinel-2 Super-Resolution) Model.
    A ResNet-based architecture for 4x super-resolution of 4-band Sentinel-2 imagery.
    """

    def __init__(
        self,
        in_channels: int = 4,
        out_channels: int = 4,
        num_features: int = 64,
        num_res_blocks: int = 16,
        scale: int = 4,
    ):
        super().__init__()
        
        # Initial feature extraction
        self.conv_initial = nn.Conv2d(in_channels, num_features, kernel_size=3, padding=1)

        # Residual blocks
        res_blocks = []
        for _ in range(num_res_blocks):
            res_blocks.append(ResidualBlock(num_features))
        self.res_blocks = nn.Sequential(*res_blocks)

        # Post-residual convolution
        self.conv_post = nn.Conv2d(num_features, num_features, kernel_size=3, padding=1)

        # Upsampling (PixelShuffle)
        assert scale in [2, 4], "Scale must be 2 or 4"
        self.upsample = nn.Sequential(
            nn.Conv2d(num_features, num_features * (scale ** 2), kernel_size=3, padding=1),
            nn.PixelShuffle(scale),
            nn.ReLU(inplace=True)
        )

        # Final reconstruction layer
        self.conv_final = nn.Conv2d(num_features, out_channels, kernel_size=3, padding=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Extract features
        feat = self.conv_initial(x)
        
        # Pass through residual blocks
        res = self.res_blocks(feat)
        res = self.conv_post(res)
        
        # Global residual connection
        feat = feat + res
        
        # Upsample
        upsampled = self.upsample(feat)
        
        # Reconstruct
        out = self.conv_final(upsampled)
        
        # Ensure output is in [0, 1] range (since reflectance is 0-1)
        out = torch.clamp(out, min=0.0, max=1.0)
        return out
