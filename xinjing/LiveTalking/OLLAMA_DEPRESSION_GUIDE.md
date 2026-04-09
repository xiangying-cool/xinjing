# Ollama 接入与抑郁沟通配置

## 1. 准备 Ollama

```bash
ollama serve
ollama pull qwen2.5:7b
```

确认服务可用：

```bash
curl http://127.0.0.1:11434/api/tags
```

## 2. 启动 LiveTalking（使用 Ollama）

```bash
python app.py \
  --transport webrtc \
  --model wav2lip \
  --avatar_id wav2lip256_avatar1 \
  --llm_provider ollama \
  --llm_model qwen2.5:7b \
  --ollama_url http://127.0.0.1:11434
```

## 3. 前端调用

前端发到 `/human`：

```json
{
  "sessionid": 123456,
  "type": "chat",
  "text": "我最近总是很难过，睡不着"
}
```

后端会：
- 调用 Ollama 流式生成
- 句级切分后推送给 TTS
- 保留每个 session 的短期多轮上下文
- 在检测到自伤/自杀关键词时触发安全兜底回复

## 4. 可调参数

- `--llm_max_history`：每个会话保留的上下文轮数，默认 `8`
- `--llm_temperature`：采样温度，默认 `0.7`

## 5. 说明

当前实现是“情绪支持”模式，不替代心理医生诊疗。
如遇到明确自伤风险，请在产品层面增加人工接管和紧急联系人流程。
