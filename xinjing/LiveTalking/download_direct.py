#!/usr/bin/env python3
"""
直接下载模型文件（使用 requests）
"""
import os
import requests
from pathlib import Path
from tqdm import tqdm

def download_file(url, target_path, desc="Downloading"):
    """下载单个文件并显示进度"""
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"正在下载: {desc}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=300)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(target_path, 'wb') as f:
            if total_size > 0:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=desc) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            else:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        
        print(f"✅ 下载完成: {target_path}")
        return True
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        if target_path.exists():
            target_path.unlink()
        return False

def main():
    print("=" * 60)
    print("LiveTalking 模型直接下载工具")
    print("=" * 60)
    
    # 使用 hf-mirror 镜像
    base_url = "https://hf-mirror.com"
    
    files_to_download = [
        # SD-VAE 模型文件
        (f"{base_url}/stabilityai/sd-vae-ft-mse/resolve/main/config.json", 
         "models/sd-vae/config.json", "sd-vae config"),
        (f"{base_url}/stabilityai/sd-vae-ft-mse/resolve/main/diffusion_pytorch_model.bin", 
         "models/sd-vae/diffusion_pytorch_model.bin", "sd-vae model (335MB)"),
        
        # MuseTalk 模型文件 (在子目录中)
        (f"{base_url}/TMElyralab/MuseTalk/resolve/main/musetalkV15/musetalk.json", 
         "models/musetalkV15/musetalk.json", "musetalk config"),
        (f"{base_url}/TMElyralab/MuseTalk/resolve/main/musetalkV15/unet.pth", 
         "models/musetalkV15/unet.pth", "musetalk unet (1.1GB)"),
    ]
    
    success_count = 0
    for url, path, desc in files_to_download:
        if download_file(url, path, desc):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"下载完成: {success_count}/{len(files_to_download)} 个文件")
    print("=" * 60)
    
    if success_count < len(files_to_download):
        print("\n部分文件下载失败，建议手动下载:")
        print("1. 访问 https://hf-mirror.com/stabilityai/sd-vae-ft-mse")
        print("2. 访问 https://hf-mirror.com/TMElyralab/MuseTalk")
        print("3. 下载所需文件并放入对应目录")

if __name__ == "__main__":
    main()
