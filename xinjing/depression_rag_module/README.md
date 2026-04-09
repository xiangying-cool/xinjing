# Depression RAG Module (Local, Open Source, Low Latency)

这是一个面向“抑郁症评估/疏导数字人”项目的本地 RAG 模块示例实现。它优先满足：

- 国内可开发、可下载模型
- 全开源
- 本地独立调试
- 成本低、依赖少
- 实时性优先
- 能无缝接到你们现有“用户输入 -> LLM”链路中间

## 1. 目录结构

```text
.
├── app/
│   ├── chunker.py
│   ├── config.py
│   ├── embeddings.py
│   ├── indexer.py
│   ├── internal_types.py
│   ├── llm.py
│   ├── loader.py
│   ├── prompting.py
│   ├── reranker.py
│   ├── retriever.py
│   ├── safety.py
│   ├── schemas.py
│   ├── service.py
│   ├── tokenizer.py
│   └── utils.py
├── data/
│   ├── knowledge/
│   └── eval/
├── scripts/
├── storage/
├── .env.example
├── download_models.sh
├── main.py
└── requirements.txt
```

## 2. 默认技术路线

- API: FastAPI
- 向量索引: FAISS
- 稀疏检索: BM25 (rank-bm25 + jieba)
- 向量模型: `BAAI/bge-small-zh-v1.5`
- 重排模型: `maidalun1020/bce-reranker-base_v1`
- 可选本地生成模型: Ollama + `qwen2.5:3b` / `qwen2.5:7b`

## 3. 安装

### 3.1 创建环境

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env
```

### 3.2 下载模型（推荐 ModelScope）

```bash
bash download_models.sh
```

下载完成后，把 `.env` 中这两个路径改成本地路径：

```env
EMBEDDING_MODEL=./models/bge-small-zh-v1.5
RERANK_MODEL=./models/bce-reranker-base_v1
```

### 3.3 启动 Ollama（如果你要本地生成答案）

```bash
ollama pull qwen2.5:3b
ollama serve
```

如果只做“检索 + 给上游 LLM 返回 prompt_bundle”，可以先不启用本地生成。

## 4. 重建索引

```bash
python -m scripts.rebuild_index
```

## 5. 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

打开：

- `http://127.0.0.1:8001/docs`
- `http://127.0.0.1:8001/health`

## 6. 核心接口

### 6.1 检索接口（推荐给你们现有网站接入）

```bash
curl -X POST 'http://127.0.0.1:8001/v1/rag/retrieve' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "我最近总是睡不好，情绪也很低落，我该怎么办？",
    "chat_history": [
      {"role": "user", "content": "我最近状态很差。"},
      {"role": "assistant", "content": "能多说一点吗？"}
    ],
    "debug": true
  }'
```

返回里最重要的是：

- `risk`: 风险级别和是否需要人工接管
- `contexts`: 检索到的片段
- `prompt_bundle.system_prompt`
- `prompt_bundle.user_prompt`
- `prompt_bundle.citation_map`

你们现有数字人模块只需要把 `prompt_bundle` 拼给当前 LLM 即可。

### 6.2 本地直接回答接口（用于你独立调试）

先在 `.env` 中打开：

```env
ENABLE_LLM_GENERATION=true
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=qwen2.5:3b
```

然后调用：

```bash
curl -X POST 'http://127.0.0.1:8001/v1/rag/answer' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "我最近觉得什么都提不起兴趣，还总睡不好。",
    "debug": true
  }'
```

## 7. 如何接进你们现有网站

你当前负责的模块只需要插在：

```text
用户输入(文本/ASR转写) -> RAG模块 -> 现有LLM -> TTS/数字人表现层
```

推荐集成方式：

1. 前端或数字人中台把用户语音/视频先转成文本。
2. 把文本和最近几轮对话发给 `/v1/rag/retrieve`。
3. 拿到 `prompt_bundle` 后，交给你们原本已经在用的 LLM。
4. 如果 `risk.handoff_required=true`，则前端直接弹危机提示，并触发人工接管或更强告警流程。

## 8. 如何扩展知识库

你真正上线前，建议把知识分成几类文件：

- `crisis/` 危机干预与紧急资源
- `professional_help/` 就医与转介
- `self_help/` 睡眠、活动、节律、求助表达
- `family_support/` 家属陪伴
- `policy/` 数字人边界与拒答策略
- `faq/` 项目内固定问答

推荐每篇文档都带 frontmatter：

```md
---
title: 示例标题
category: self_help
source_name: WHO
source_url: https://example.com
priority: 6
---

正文...
```

## 9. 评测

```bash
python -m scripts.eval_retrieval
```

输出包含：

- `hit_rate_at_k`
- `avg_latency_ms`

## 10. 建议的调参顺序

先保实时性，再加复杂度：

1. 先只用 dense + BM25，不开 query rewrite
2. 再开 rerank
3. 最后尝试 multi-query rewrite
4. 如果知识库变大，再考虑换 Qdrant 或更重模型

## 11. 生产前必须补上的规则

- 高风险内容必须优先走危机流程
- 明确“非诊断、非处方、非急救替代”边界
- 药物问题只能给通用提醒，不给剂量和停药指令
- PHQ-9 等量表分数解释尽量做成显式规则，不要全交给 LLM
- 日志要脱敏，不存原始敏感个人信息

