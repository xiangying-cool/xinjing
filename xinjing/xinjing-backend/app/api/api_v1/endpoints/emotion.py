"""
面部表情识别接口
调用 facial_expression 服务 (端口 8002)
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
import httpx
import base64
from io import BytesIO
from PIL import Image

router = APIRouter()

FER_SERVICE_URL = "http://localhost:8002"


@router.post("/detect")
async def detect_emotion(file: UploadFile = File(...)):
    """
    检测图片中的面部表情
    返回情绪分类结果
    """
    # 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")
    
    try:
        # 读取图片内容
        contents = await file.read()
        
        # 调用 FER 服务
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, BytesIO(contents), file.content_type)}
            response = await client.post(
                f"{FER_SERVICE_URL}/predict/json-result",
                files=files,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"FER服务错误: {response.text}"
                )
            
            return response.json()
    
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="面部表情识别服务未启动 (端口 8002)"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-base64")
async def detect_emotion_base64(image_data: dict):
    """
    通过 base64 编码的图片检测表情
    {"image": "base64encodedstring"}
    """
    try:
        base64_str = image_data.get("image", "")
        if not base64_str:
            raise HTTPException(status_code=400, detail="缺少 image 字段")
        
        # 解码 base64
        image_bytes = base64.b64decode(base64_str)
        
        # 调用 FER 服务
        async with httpx.AsyncClient() as client:
            files = {"file": ("image.jpg", BytesIO(image_bytes), "image/jpeg")}
            response = await client.post(
                f"{FER_SERVICE_URL}/predict/json-result",
                files=files,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"FER服务错误: {response.text}"
                )
            
            return response.json()
    
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="面部表情识别服务未启动 (端口 8002)"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def fer_status():
    """检查 FER 服务状态"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FER_SERVICE_URL}/",
                timeout=5.0
            )
            return {
                "status": "running" if response.status_code == 200 else "error",
                "service": "facial_expression_recognition",
                "port": 8002
            }
    except:
        return {
            "status": "stopped",
            "service": "facial_expression_recognition",
            "port": 8002
        }


# 情绪标签映射
EMOTION_LABELS = {
    0: {"name": "愤怒", "emoji": "😠", "color": "#FF4444"},
    1: {"name": "厌恶", "emoji": "😧", "color": "#8B4513"},
    2: {"name": "恐惧", "emoji": "😨", "color": "#800080"},
    3: {"name": "开心", "emoji": "😃", "color": "#FFD700"},
    4: {"name": "悲伤", "emoji": "😞", "color": "#4169E1"},
    5: {"name": "惊讶", "emoji": "😮", "color": "#FF8C00"},
    6: {"name": "中立", "emoji": "😐", "color": "#808080"}
}


@router.get("/labels")
async def get_emotion_labels():
    """获取情绪标签列表"""
    return EMOTION_LABELS
