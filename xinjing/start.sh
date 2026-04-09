#打开一个终端
cd depression_rag_module
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --host 0.0.0.0 --port 8001
#打开另外一个终端
cd LiveTalking
conda activate nerfstream
python app.py --transport webrtc --model wav2lip --avatar_id my_avatar --llm_provider ollama --llm_model qwen2.5:3b
