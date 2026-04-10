import asyncio
import json
import os
import tempfile
import time
from io import BytesIO
from typing import Optional

import cv2
import numpy as np
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    WebSocket,
    WebSocketDisconnect,
    Request,
    HTTPException,
    Form,
)
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from starlette.concurrency import run_in_threadpool
from starlette.requests import ClientDisconnect

from src.serve.inferencer import process_video_with_model, process_image_with_model
from src.utils import setup_logger

logger = setup_logger()
router = APIRouter()


# === Utility Functions ===
def log_info(client: str, message: str):
    logger.info(f"[USER: {client}] {message}")

def validate_file(file: UploadFile, allowed_exts: set, max_mb: int):
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not allowed.")
    if hasattr(file, "size") and file.size:
        if (file.size / (1024 * 1024)) > max_mb:
            raise HTTPException(status_code=400, detail=f"File too large (>{max_mb} MB).")

# === Routes ===
@router.post("/predict/image")
async def predict_image(
    request: Request,
    file: UploadFile = File(...),
    emoji: Optional[bool] = Form(False)
):
    cfg = request.app.state.cfg
    client_ip = request.client.host

    try:
        log_info(client_ip, f"Image upload: {file.filename} | Emoji: {emoji}")
        validate_file(file, set(cfg.API.ALLOWED_IMAGE_EXT), cfg.API.MAX_IMAGE_SIZE_MB)

        contents = await file.read()
        npimg = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)

        if image is None:
            log_info(client_ip, "Invalid image data")
            return JSONResponse(status_code=400, content={"error": "Invalid image format"})
        else:
            if image.ndim == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        cfg.DISPLAY.EMOJI = emoji

        model = request.app.state.model
        processed = process_image_with_model(image, model, cfg)

        _, jpeg = cv2.imencode('.jpg', processed, [int(cv2.IMWRITE_JPEG_QUALITY), 75])

        log_info(client_ip, "Image processed")
        return StreamingResponse(BytesIO(jpeg.tobytes()), media_type="image/jpeg")

    except Exception as e:
        log_info(client_ip, f"Image processing failed: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/predict/video")
async def predict_video(request: Request, file: UploadFile = File(...), emoji: Optional[bool] = Form(False)):
    cfg = request.app.state.cfg
    client_ip = request.client.host
    try:
        log_info(client_ip, f"Video upload: {file.filename} | Emoji: {emoji}")
        validate_file(file, set(cfg.API.ALLOWED_VIDEO_EXT), cfg.API.MAX_VIDEO_SIZE_MB)

        video_bytes = await file.read()
        size_mb = len(video_bytes) / (1024 * 1024)
        if size_mb > cfg.API.MAX_VIDEO_SIZE_MB:
            raise HTTPException(status_code=400, detail="Video too large.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
            temp_input.write(video_bytes)
            input_path = temp_input.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output:
            output_path = temp_output.name

        log_info(client_ip, f"Processing video ({size_mb:.2f} MB)...")
        cfg.DISPLAY.EMOJI = emoji
        start = time.time()
        model = request.app.state.model
        await run_in_threadpool(process_video_with_model, input_path, output_path, model, cfg)
        log_info(client_ip, f"Video done in {time.time() - start:.2f} sec")

        return FileResponse(output_path, media_type="video/mp4", filename="processed_video.mp4")

    except Exception as e:
        log_info(client_ip, f"Video processing failed: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/json-result")
async def predict_image_json(
    request: Request,
    file: UploadFile = File(...)
):
    """返回 JSON 格式的情绪概率，供后端调用"""
    cfg = request.app.state.cfg
    model = request.app.state.model

    try:
        contents = await file.read()
        npimg = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)

        if image is None:
            return JSONResponse(status_code=400, content={"error": "Invalid image format"})

        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image.ndim == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        # YOLO 人脸检测
        yolo_result = model.Yolo(image, verbose=False)[0]
        face_images, _ = model.extract_faces_from_yolo(yolo_result, image)

        if len(face_images) == 0:
            # 未检测到人脸，返回以"中立"为主的分布
            return {"emotions": [0.05, 0.05, 0.05, 0.1, 0.05, 0.05, 0.65], "face_detected": False}

        # 确保维度正确（4D: batch, channel, H, W）
        if face_images.ndim != 4:
            return {"emotions": [0.05, 0.05, 0.05, 0.1, 0.05, 0.05, 0.65], "face_detected": False}

        # 直接从 ONNX 模型取 softmax 概率（不丢弃非最大值）
        from scipy.special import softmax as sp_softmax
        onnx_inputs = {model.FerNet.model.get_inputs()[0].name: face_images}
        raw = model.FerNet.model.run(None, onnx_inputs)[0]
        probs = sp_softmax(raw, axis=1)[0].tolist()  # 取第一张人脸

        # FER 类别顺序: {0:Surprise, 1:Fear, 2:Disgust, 3:Happy, 4:Sad, 5:Angry, 6:Neutral}
        # 前端期望顺序: {0:愤怒, 1:厌恶, 2:恐惧, 3:开心, 4:悲伤, 5:惊讶, 6:中立}
        emotions = [
            probs[5],  # 0: 愤怒 Angry
            probs[2],  # 1: 厌恶 Disgust
            probs[1],  # 2: 恐惧 Fear
            probs[3],  # 3: 开心 Happy
            probs[4],  # 4: 悲伤 Sad
            probs[0],  # 5: 惊讶 Surprise
            probs[6],  # 6: 中立 Neutral
        ]

        return {"emotions": emotions, "face_detected": True}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    cfg = websocket.app.state.cfg
    await websocket.accept()
    client_ip = websocket.client.host
    frame_id = 0

    log_info(client_ip, "WebSocket connected")

    try:
        while True:
            message = await websocket.receive()

            # === Handle config messages (text JSON)
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    if data.get("type") == "config":
                        cfg.DISPLAY.EMOJI = data.get("emoji", False)
                        log_info(client_ip, f"Emoji mode updated: {cfg.DISPLAY.EMOJI}")
                except json.JSONDecodeError:
                    log_info(client_ip, "Invalid JSON config received")
                continue

            # === Handle image frame (binary JPEG)
            elif "bytes" in message:
                data = message["bytes"]
                npimg = np.frombuffer(data, np.uint8)
                frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

                if frame is None:
                    log_info(client_ip, f"Invalid frame {frame_id}")
                    continue

                model = websocket.app.state.model

                # Single YOLO pass — annotate frame AND extract probabilities
                from scipy.special import softmax as sp_softmax

                yolo_result = model.Yolo(frame, verbose=False)[0]
                face_images, bbox = model.extract_faces_from_yolo(yolo_result, frame)

                emotion_payload = {
                    "type": "emotions",
                    "face_detected": False,
                    "emotions": [0.05, 0.05, 0.05, 0.1, 0.05, 0.05, 0.65],
                }
                detections = []

                if len(face_images) > 0 and face_images.ndim == 4:
                    onnx_inputs = {model.FerNet.model.get_inputs()[0].name: face_images}
                    raw = model.FerNet.model.run(None, onnx_inputs)[0]
                    all_probs = sp_softmax(raw, axis=1)  # shape: (n_faces, 7)
                    class_ids = all_probs.argmax(axis=1)

                    for i, (x1, y1, x2, y2, conf, class_label) in enumerate(bbox):
                        if float(conf) < cfg.INFERENCE.CONFIDENCE_THRESHOLD or class_label != "face":
                            continue
                        cid = int(class_ids[i])
                        detections.append({
                            "bbox": [int(x1), int(y1), int(x2), int(y2)],
                            "confidence": round(float(conf), 2),
                            "class_id": cid,
                            "class": "face",
                            "emotion_label": model.classes[cid],
                            "emoji": model.emotion_emojis[cid],
                        })

                    # FER order: {0:Surprise,1:Fear,2:Disgust,3:Happy,4:Sad,5:Angry,6:Neutral}
                    # Frontend: {0:愤怒,1:厌恶,2:恐惧,3:开心,4:悲伤,5:惊讶,6:中立}
                    probs = all_probs[0].tolist()
                    emotion_payload = {
                        "type": "emotions",
                        "face_detected": True,
                        "emotions": [probs[5], probs[2], probs[1], probs[3], probs[4], probs[0], probs[6]],
                    }

                annotated = model.plot({"detections": detections, "image": yolo_result.orig_img}, cfg, fps=0)
                _, jpeg = cv2.imencode('.jpg', annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
                await websocket.send_bytes(jpeg.tobytes())
                await websocket.send_text(json.dumps(emotion_payload))

                if frame_id % 10 == 0:
                    log_info(client_ip, f"Sent frame {frame_id}")
                frame_id += 1

                await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        log_info(client_ip, "WebSocket disconnected")
    except ClientDisconnect:
        log_info(client_ip, "Client forcefully closed")
    except Exception as e:
        log_info(client_ip, f"WebSocket error: {str(e)}")
