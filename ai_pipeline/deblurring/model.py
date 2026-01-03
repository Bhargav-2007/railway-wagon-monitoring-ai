"""
NAFNet - Nonlinear Activation Free Network for Image Deblurring
Simplified implementation for railway wagon monitoring
Based on: https://arxiv.org/abs/2204.04676
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List


class LayerNormFunction(torch.autograd.Function):
    """Custom Layer Normalization"""
    
    @staticmethod
    def forward(ctx, x, weight, bias, eps):
        ctx.eps = eps
        N, C, H, W = x.size()
        mu = x.mean(1, keepdim=True)
        var = (x - mu).pow(2).mean(1, keepdim=True)
        y = (x - mu) / (var + eps).sqrt()
        ctx.save_for_backward(y, var, weight)
        y = weight.view(1, C, 1, 1) * y + bias.view(1, C, 1, 1)
        return y
    
    @staticmethod
    def backward(ctx, grad_output):
        eps = ctx.eps
        N, C, H, W = grad_output.size()
        y, var, weight = ctx.saved_variables
        g = grad_output * weight.view(1, C, 1, 1)
        mean_g = g.mean(dim=1, keepdim=True)
        
        mean_gy = (g * y).mean(dim=1, keepdim=True)
        gx = 1. / torch.sqrt(var + eps) * (g - y * mean_gy - mean_g)
        return gx, (grad_output * y).sum(dim=3).sum(dim=2).sum(dim=0), \
               grad_output.sum(dim=3).sum(dim=2).sum(dim=0), None


class LayerNorm2d(nn.Module):
    """2D Layer Normalization"""
    
    def __init__(self, channels, eps=1e-6):
        super(LayerNorm2d, self).__init__()
        self.register_parameter('weight', nn.Parameter(torch.ones(channels)))
        self.register_parameter('bias', nn.Parameter(torch.zeros(channels)))
        self.eps = eps
    
    def forward(self, x):
        return LayerNormFunction.apply(x, self.weight, self.bias, self.eps)


class SimpleGate(nn.Module):
    """Simple Gate mechanism (replaces nonlinear activations)"""
    
    def forward(self, x):
        x1, x2 = x.chunk(2, dim=1)
        return x1 * x2


class NAFBlock(nn.Module):
    """NAF Block - core building block"""
    
    def __init__(self, channels, dw_expansion=2, ffn_expansion=2, drop_out_rate=0.):
        super(NAFBlock, self).__init__()
        dw_channels = channels * dw_expansion
        
        self.conv1 = nn.Conv2d(channels, dw_channels, 1, padding=0, stride=1, groups=1, bias=True)
        self.conv2 = nn.Conv2d(dw_channels, dw_channels, 3, padding=1, stride=1, groups=dw_channels, bias=True)
        self.conv3 = nn.Conv2d(dw_channels // 2, channels, 1, padding=0, stride=1, groups=1, bias=True)
        
        # Simplified Channel Attention
        self.sca = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(dw_channels // 2, dw_channels // 2, 1, padding=0, stride=1, groups=1, bias=True),
        )
        
        # SimpleGate
        self.sg = SimpleGate()
        
        ffn_channels = channels * ffn_expansion
        self.conv4 = nn.Conv2d(channels, ffn_channels, 1, padding=0, stride=1, groups=1, bias=True)
        self.conv5 = nn.Conv2d(ffn_channels // 2, channels, 1, padding=0, stride=1, groups=1, bias=True)
        
        self.norm1 = LayerNorm2d(channels)
        self.norm2 = LayerNorm2d(channels)
        
        self.dropout1 = nn.Dropout(drop_out_rate) if drop_out_rate > 0. else nn.Identity()
        self.dropout2 = nn.Dropout(drop_out_rate) if drop_out_rate > 0. else nn.Identity()
        
        self.beta = nn.Parameter(torch.zeros((1, channels, 1, 1)), requires_grad=True)
        self.gamma = nn.Parameter(torch.zeros((1, channels, 1, 1)), requires_grad=True)
    
    def forward(self, x):
        inp = x
        
        x = self.norm1(x)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.sg(x)
        x = x * self.sca(x)
        x = self.conv3(x)
        x = self.dropout1(x)
        
        y = inp + x * self.beta
        
        x = self.conv4(self.norm2(y))
        x = self.sg(x)
        x = self.conv5(x)
        x = self.dropout2(x)
        
        return y + x * self.gamma


class NAFNet(nn.Module):
    """
    NAFNet for Motion Deblurring
    Lightweight version optimized for edge deployment
    """
    
    def __init__(
        self,
        img_channels=3,
        width=32,
        middle_blk_num=1,
        enc_blk_nums=[1, 1, 1, 28],
        dec_blk_nums=[1, 1, 1, 1]
    ):
        super(NAFNet, self).__init__()
        
        self.intro = nn.Conv2d(img_channels, width, 3, padding=1, stride=1, groups=1, bias=True)
        self.ending = nn.Conv2d(width, img_channels, 3, padding=1, stride=1, groups=1, bias=True)
        
        self.encoders = nn.ModuleList()
        self.decoders = nn.ModuleList()
        self.middle_blks = nn.ModuleList()
        self.ups = nn.ModuleList()
        self.downs = nn.ModuleList()
        
        chan = width
        for num in enc_blk_nums:
            self.encoders.append(
                nn.Sequential(
                    *[NAFBlock(chan) for _ in range(num)]
                )
            )
            self.downs.append(
                nn.Conv2d(chan, 2*chan, 2, 2)
            )
            chan = chan * 2
        
        self.middle_blks = \
            nn.Sequential(
                *[NAFBlock(chan) for _ in range(middle_blk_num)]
            )
        
        for num in dec_blk_nums:
            self.ups.append(
                nn.Sequential(
                    nn.Conv2d(chan, chan * 2, 1, bias=False),
                    nn.PixelShuffle(2)
                )
            )
            chan = chan // 2
            self.decoders.append(
                nn.Sequential(
                    *[NAFBlock(chan) for _ in range(num)]
                )
            )
        
        self.padder_size = 2 ** len(self.encoders)
    
    def forward(self, inp):
        B, C, H, W = inp.shape
        inp = self.check_image_size(inp)
        
        x = self.intro(inp)
        
        encs = []
        
        for encoder, down in zip(self.encoders, self.downs):
            x = encoder(x)
            encs.append(x)
            x = down(x)
        
        x = self.middle_blks(x)
        
        for decoder, up, enc_skip in zip(self.decoders, self.ups, encs[::-1]):
            x = up(x)
            x = x + enc_skip
            x = decoder(x)
        
        x = self.ending(x)
        x = x + inp
        
        return x[:, :, :H, :W]
    
    def check_image_size(self, x):
        _, _, h, w = x.size()
        mod_pad_h = (self.padder_size - h % self.padder_size) % self.padder_size
        mod_pad_w = (self.padder_size - w % self.padder_size) % self.padder_size
        x = F.pad(x, (0, mod_pad_w, 0, mod_pad_h))
        return x


def create_nafnet_deblur(model_size="small"):
    """
    Factory function to create NAFNet models
    
    Args:
        model_size: "tiny", "small", "medium", or "large"
        
    Returns:
        NAFNet model
    """
    if model_size == "tiny":
        # Ultra-lightweight for edge devices
        model = NAFNet(
            width=16,
            middle_blk_num=1,
            enc_blk_nums=[1, 1, 1, 1],
            dec_blk_nums=[1, 1, 1, 1]
        )
    elif model_size == "small":
        # Balanced for Jetson
        model = NAFNet(
            width=32,
            middle_blk_num=1,
            enc_blk_nums=[2, 2, 4, 8],
            dec_blk_nums=[2, 2, 2, 2]
        )
    elif model_size == "medium":
        model = NAFNet(
            width=48,
            middle_blk_num=2,
            enc_blk_nums=[2, 2, 4, 12],
            dec_blk_nums=[2, 2, 2, 2]
        )
    else:  # large
        model = NAFNet(
            width=64,
            middle_blk_num=2,
            enc_blk_nums=[2, 2, 4, 16],
            dec_blk_nums=[2, 2, 2, 2]
        )
    
    return model


# Test
if __name__ == "__main__":
    print("Testing NAFNet models...\n")
    
    sizes = ["tiny", "small", "medium"]
    input_tensor = torch.randn(1, 3, 256, 256)
    
    for size in sizes:
        print(f"Testing {size} model:")
        model = create_nafnet_deblur(size)
        model.eval()
        
        # Count parameters
        params = sum(p.numel() for p in model.parameters())
        print(f"  Parameters: {params:,}")
        
        # Test forward pass
        with torch.no_grad():
            output = model(input_tensor)
        
        print(f"  Input shape: {input_tensor.shape}")
        print(f"  Output shape: {output.shape}")
        print(f"  Output range: [{output.min():.3f}, {output.max():.3f}]")
        print()
    
    print("✅ All models tested successfully!")
