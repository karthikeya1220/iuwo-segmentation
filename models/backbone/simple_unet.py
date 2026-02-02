"""
Simple U-Net Architecture for Prototyping

INFERENCE ONLY - This is a placeholder architecture.

In production, replace this with a pretrained nnU-Net model.

Author: Research Prototype
Date: 2026-02-02
"""

import torch
import torch.nn as nn


class SimpleUNet(nn.Module):
    """
    Simple U-Net architecture for prototyping.
    
    This is a MINIMAL implementation for testing the inference pipeline.
    In production, use a pretrained nnU-Net model.
    
    Architecture:
    - Encoder: 4 downsampling blocks
    - Decoder: 4 upsampling blocks
    - Skip connections between encoder and decoder
    """
    
    def __init__(self, in_channels: int = 1, out_channels: int = 1):
        """
        Initialize Simple U-Net.
        
        Args:
            in_channels: Number of input channels (1 for grayscale)
            out_channels: Number of output channels (1 for binary segmentation)
        """
        super(SimpleUNet, self).__init__()
        
        # Encoder (downsampling)
        self.enc1 = self._conv_block(in_channels, 64)
        self.enc2 = self._conv_block(64, 128)
        self.enc3 = self._conv_block(128, 256)
        self.enc4 = self._conv_block(256, 512)
        
        # Bottleneck
        self.bottleneck = self._conv_block(512, 1024)
        
        # Decoder (upsampling)
        self.upconv4 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.dec4 = self._conv_block(1024, 512)
        
        self.upconv3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec3 = self._conv_block(512, 256)
        
        self.upconv2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec2 = self._conv_block(256, 128)
        
        self.upconv1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = self._conv_block(128, 64)
        
        # Output layer
        self.out = nn.Conv2d(64, out_channels, kernel_size=1)
        
        # Pooling
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
    
    def _conv_block(self, in_channels: int, out_channels: int) -> nn.Sequential:
        """
        Convolutional block: Conv -> ReLU -> Conv -> ReLU
        
        Args:
            in_channels: Number of input channels
            out_channels: Number of output channels
            
        Returns:
            Sequential block
        """
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor (B, C, H, W)
            
        Returns:
            Output logits (B, out_channels, H, W)
        """
        # Encoder
        enc1 = self.enc1(x)
        enc2 = self.enc2(self.pool(enc1))
        enc3 = self.enc3(self.pool(enc2))
        enc4 = self.enc4(self.pool(enc3))
        
        # Bottleneck
        bottleneck = self.bottleneck(self.pool(enc4))
        
        # Decoder with skip connections
        dec4 = self.upconv4(bottleneck)
        dec4 = torch.cat([dec4, enc4], dim=1)
        dec4 = self.dec4(dec4)
        
        dec3 = self.upconv3(dec4)
        dec3 = torch.cat([dec3, enc3], dim=1)
        dec3 = self.dec3(dec3)
        
        dec2 = self.upconv2(dec3)
        dec2 = torch.cat([dec2, enc2], dim=1)
        dec2 = self.dec2(dec2)
        
        dec1 = self.upconv1(dec2)
        dec1 = torch.cat([dec1, enc1], dim=1)
        dec1 = self.dec1(dec1)
        
        # Output
        out = self.out(dec1)
        
        return out


if __name__ == "__main__":
    # Test Simple U-Net
    print("Testing Simple U-Net...")
    
    model = SimpleUNet(in_channels=1, out_channels=1)
    model.eval()
    
    # Create dummy input
    dummy_input = torch.randn(1, 1, 256, 256)
    
    # Forward pass
    with torch.no_grad():
        output = model(dummy_input)
    
    print(f"✅ Forward pass successful!")
    print(f"   Input shape: {dummy_input.shape}")
    print(f"   Output shape: {output.shape}")
    print(f"   Parameters: {sum(p.numel() for p in model.parameters()):,}")
