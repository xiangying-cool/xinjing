#!/usr/bin/env python3
"""
下载 LiveTalking 所需模型文件 (使用 ModelScope 国内源)
"""
import os
import sys
from pathlib import Path

def download_sd_vae():
    """下载 SD-VAE 模型"""
    from modelscope import snapshot_download
    
    target_dir = Path("models/sd-vae")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print("正在从 ModelScope 下载 sd-vae 模型...")
    snapshot_download(
        model_id="AI-ModelScope/sd-vae-ft-mse",
        local_dir=str(target_dir),
    )
    print(f"✅ sd-vae 模型已下载到 {target_dir}")

def download_musetalk():
    """下载 MuseTalk 模型"""
    from modelscope import snapshot_download
    
    target_dir = Path("models/musetalkV15")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print("正在从 ModelScope 下载 MuseTalk 模型...")
    snapshot_download(
        model_id="AI-ModelScope/MuseTalk",
        local_dir=str(target_dir),
    )
    print(f"✅ MuseTalk 模型已下载到 {target_dir}")

def main():
    print("=" * 50)
    print("LiveTalking 模型下载工具 (ModelScope 版)")
    print("=" * 50)
    
    try:
        from modelscope import snapshot_download
    except ImportError:
        print("❌ 请先安装 modelscope: pip install modelscope")
        sys.exit(1)
    
    try:
        download_sd_vae()
        download_musetalk()
        print("\n" + "=" * 50)
        print("✅ 所有模型下载完成！")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        print("\n你可以尝试:")
        print("1. 检查网络连接")
        print("2. 手动从 https://www.modelscope.cn 搜索下载")
        print("3. 或从 https://huggingface.co/TMElyralab/MuseTalk 下载")
        sys.exit(1)

if __name__ == "__main__":
    main()
