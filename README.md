# 心镜 (Xinjing) - 心理健康智能陪伴系统

<p align="center">
  <img src="xinjing/xinjing-frontend/public/vite.svg" alt="心镜 Logo" width="100">
</p>

<p align="center">
  <b>AI驱动的数字人心理健康陪伴平台</b>
</p>

## 🌟 项目简介

心镜是一个基于人工智能的心理健康陪伴系统，集成了数字人对话、心理评估、情绪追踪和知识问答等功能，为用户提供温暖、专业的心理健康支持。

## 🏗️ 系统架构

本项目由四个核心服务组成：

| 服务 | 端口 | 技术栈 | 功能 |
|------|------|--------|------|
| **前端** | 5173 | Vue 3 + Vite + Tailwind CSS | 用户界面 |
| **后端 API** | 8000 | FastAPI + SQLAlchemy + MySQL | 业务逻辑 |
| **RAG 服务** | 8001 | Python + FAISS + BM25 | 知识问答 |
| **数字人** | 8010 | LiveTalking + MuseTalk | 数字人对话 |

## 📁 项目结构

```
xinjing/
├── xinjing-frontend/          # Vue 3 前端
│   ├── src/pages/             # 页面组件
│   ├── src/services/          # API 服务
│   └── vite.config.js         # 代理配置
├── xinjing-backend/           # FastAPI 后端
│   ├── app/api/               # API 路由
│   ├── app/models/            # 数据库模型
│   └── app/services/          # 业务逻辑
├── depression_rag_module/     # RAG 问答服务
│   ├── app/                   # 核心代码
│   ├── data/knowledge/        # 知识库文档
│   └── storage/               # 向量索引
├── LiveTalking/               # 数字人服务
│   ├── models/                # AI 模型
│   ├── data/avatars/          # 数字人资源
│   └── web/                   # 测试页面
└── depression_prediction/     # 抑郁预测模型
```

## 🚀 快速启动

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Conda (推荐)

### 1. 克隆项目

```bash
git clone https://github.com/xiangying-cool/xinjing.git
cd xinjing
```

### 2. 配置环境变量

创建各服务的 `.env` 文件：

**xinjing-backend/.env**
```env
DATABASE_URL=mysql+pymysql://user:password@localhost/xinjing
SECRET_KEY=your-secret-key
```

**depression_rag_module/.env**
```env
ENABLE_LLM_GENERATION=true
DASHSCOPE_API_KEY=your-dashscope-api-key
```

### 3. 启动服务

#### 方式一：手动启动

**终端 1 - RAG 服务 (8001)**
```bash
cd depression_rag_module
.venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

**终端 2 - 数字人服务 (8010)**
```bash
cd LiveTalking
conda activate nerfstream
$env:DASHSCOPE_API_KEY="your-api-key"
python app.py --avatar_id my_avatar --transport webrtc
```

**终端 3 - 后端 API (8000)**
```bash
cd xinjing-backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**终端 4 - 前端 (5173)**
```bash
cd xinjing-frontend
npm install
npm run dev
```

#### 方式二：使用启动脚本

```bash
./start.sh
```

### 4. 访问系统

打开浏览器访问：`http://localhost:5173`

## 🎯 核心功能

### 1. 数字人陪伴
- WebRTC 实时音视频通信
- Edge TTS 语音合成
- MuseTalk 唇形同步
- 基于 Qwen 大模型的智能对话

### 2. 心理评估
- PHQ-9 抑郁筛查量表
- SDS 抑郁自评量表
- AIS 失眠评估量表
- PSS 压力感知量表

### 3. RAG 知识问答
- FAISS + BM25 混合检索
- 心理健康知识库
- Markdown 格式回答
- 引用来源标注

### 4. 情绪追踪
- 情绪日历可视化
- 心情记录与分析
- 数据趋势图表

## 📦 模型文件说明

由于模型文件较大，Git 仓库中未包含以下文件，需要单独下载：

| 模型 | 大小 | 下载地址 | 放置位置 |
|------|------|----------|----------|
| sd-vae | ~335MB | HuggingFace | LiveTalking/models/sd-vae/ |
| musetalkV15 | ~1.1GB | HuggingFace | LiveTalking/models/musetalkV15/ |
| whisper | ~1.6GB | HuggingFace | LiveTalking/musetalk/whisper/ |
| wav2lip | ~??MB | - | LiveTalking/models/wav2lip.pth |

### 下载脚本

```bash
cd LiveTalking
python download_direct.py
```

### 生成数字人资源

```bash
cd LiveTalking
python genavatar.py --avatar_id my_avatar
```

## 🔧 配置说明

### 前端代理配置 (vite.config.js)

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
    '/livetalking': {
      target: 'http://localhost:8010',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/livetalking/, ''),
    },
  },
}
```

### 数据库配置

系统使用 SQLAlchemy 自动创建数据库表结构，无需手动迁移：

```python
# app/db/base.py
from app.db.base_class import Base
from app.models.user import User
from app.models.evaluation import Evaluation
# ... 其他模型

Base.metadata.create_all(bind=engine)
```

## 🛠️ 技术栈

### 前端
- **框架**: Vue 3 + Composition API
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **路由**: Vue Router
- **HTTP**: Axios
- **Markdown**: marked

### 后端
- **框架**: FastAPI
- **ORM**: SQLAlchemy
- **数据库**: MySQL
- **认证**: JWT + bcrypt
- **验证**: Pydantic

### AI 服务
- **LLM**: DashScope (qwen-plus)
- **向量检索**: FAISS
- **文本检索**: BM25 (rank-bm25)
- **嵌入模型**: BGE-Small
- **TTS**: Edge TTS
- **唇形同步**: MuseTalk

## 📝 API 文档

启动后端服务后访问：`http://localhost:8000/docs`

主要接口：
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `GET /api/v1/users/me` - 获取当前用户
- `POST /api/v1/evaluations` - 提交评估
- `GET /api/v1/evaluations/{id}` - 获取评估结果
- `POST /api/v1/mood` - 记录心情
- `GET /api/v1/mood/calendar` - 获取情绪日历

## 🐛 常见问题

### 1. 数字人无法显示
- 检查 LiveTalking 服务是否启动
- 确认模型文件已正确下载
- 检查浏览器控制台是否有 WebRTC 错误

### 2. RAG 服务返回"服务未启用"
- 检查 `.env` 中 `ENABLE_LLM_GENERATION=true`
- 确认 `DASHSCOPE_API_KEY` 已配置

### 3. 数据库连接失败
- 检查 MySQL 服务是否运行
- 确认 `DATABASE_URL` 配置正确
- 检查数据库用户权限

### 4. 前端代理失败
- 确认后端服务端口正确
- 检查 vite.config.js 代理配置
- 重启前端开发服务器

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请通过 GitHub Issues 联系。

---

<p align="center">
  Made with ❤️ for mental health
</p>
