# 🎥 智能视频识别系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

这是一个基于**FastAPI**的智能视频识别系统，集成了**Ollama大模型**，能够实时处理RTSP视频流并提供AI驱动的内容识别功能。系统采用现代化的Web界面设计，支持多终端访问，为视频监控和内容分析提供了强大的解决方案。

## ✨ 核心特性

### � 核心功能
- **实时视频流处理**：支持RTSP协议视频流的实时捕获和展示
- **AI智能识别**：集成Ollama Qwen2.5-VL大模型，提供精准的图像内容识别
- **实时通信**：基于WebSocket的实时数据推送，零延迟获取识别结果
- **历史记录**：智能存储和管理识别历史，支持数据回溯

### 🖥️ 用户界面
- **响应式设计**：完美适配桌面端和移动端设备
- **现代化UI**：采用毛玻璃效果和渐变设计，提供优雅的视觉体验
- **实时状态显示**：连接状态指示器，实时监控系统运行状态
- **Markdown渲染**：支持富文本格式的识别结果展示

### ⚡ 性能特点
- **异步处理**：基于asyncio和ThreadPoolExecutor的高并发架构
- **智能跳帧**：可配置的帧处理策略，优化系统资源使用
- **队列管理**：缓冲队列机制，确保视频流的稳定性
- **自动重连**：网络异常时自动重连RTSP流，保证服务稳定性

## 📸 系统截图
[bilibili](https://www.bilibili.com/video/BV13ANazuEYq/)
![效果图](界面.png)

### 主界面
- **左侧**：实时视频流展示区域，支持全屏查看
- **右侧**：AI识别结果展示区域，支持Markdown格式渲染
- **顶部**：系统状态栏，显示连接状态和系统信息

### 功能特点
- 实时视频流畅播放，支持多种分辨率自适应
- 识别结果按时间倒序排列，便于查看最新内容
- 支持移动端触控操作，响应式布局优化

## 🛠️ 技术架构

### 后端技术栈
- **Web框架**：FastAPI - 高性能异步Web框架
- **视频处理**：OpenCV - 专业级视频处理库
- **AI模型**：Ollama + Qwen2.5-VL - 多模态大语言模型
- **实时通信**：WebSocket - 双向实时数据传输
- **异步处理**：asyncio + ThreadPoolExecutor - 高并发处理

### 前端技术栈
- **基础技术**：HTML5 + CSS3 + JavaScript
- **UI设计**：现代化毛玻璃效果，渐变背景
- **响应式布局**：支持移动端和桌面端适配
- **Markdown渲染**：marked.js + highlight.js

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RTSP摄像头    │───▶│   视频处理模块   │───▶│   AI识别模块    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web界面展示   │◀───│   WebSocket     │◀───│   结果处理模块   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 快速开始

### 📋 环境要求

- **Python版本**：3.8 或更高版本
- **操作系统**：Windows / Linux / macOS
- **内存要求**：建议8GB以上（运行大模型需要）
- **网络要求**：支持RTSP协议的网络摄像头或视频源

### 🔧 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd vision_describe
```

#### 2. 创建虚拟环境（推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装Python依赖

```bash
pip install -r requirements.txt
```

#### 4. 安装和配置Ollama

**安装Ollama：**
```bash
# Windows
# 下载安装包：https://ollama.ai/download

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama
```

**启动Ollama服务：**
```bash
ollama serve
```

**下载所需模型：**

```bash
# 下载Qwen2.5-VL模型（约4.5GB）
ollama pull qwen2.5vl:7b
```

#### 5. 配置RTSP视频源

在`main.py`文件中修改RTSP地址为您的摄像头地址：

```python
# 第21行附近
rtsp_url = "rtsp://用户名:密码@IP地址:端口/路径"

# 示例：
rtsp_url = "rtsp://admin:123456@192.168.1.100:554/h264/ch1/main/av_stream"
```

#### 6. 启动应用

**方式一：直接运行**
```bash
python main.py
```

**方式二：使用uvicorn（推荐生产环境）**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 7. 访问应用

打开浏览器访问：
- **本地访问**：http://localhost:8000
- **局域网访问**：http://您的IP地址:8000

## 📁 项目结构

```
vision_describe/
├── 📄 main.py                 # FastAPI主应用程序
├── 📄 version_llm.py          # 基于tkinter的桌面版本（原型）
├── 📄 requirements.txt        # Python依赖包列表
├── 📄 README.md              # 项目说明文档
├── 📁 templates/             # Jinja2模板文件夹
│   └── 📄 index.html         # 主页面模板
└── 📁 static/                # 静态资源文件夹
    ├── 📄 style.css          # 主样式文件
    ├── 📁 css/               # CSS样式文件夹
    │   └── 📄 markdown.css   # Markdown渲染样式
    └── 📁 js/                # JavaScript文件夹
        └── 📄 markdown-utils.js # Markdown工具函数
```

### 📝 关键文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | 核心应用程序，包含FastAPI路由、WebSocket处理、视频流处理等 |
| `version_llm.py` | 原始桌面版本，基于tkinter和OpenCV的简单实现 |
| `templates/index.html` | Web界面模板，包含响应式布局和实时通信逻辑 |
| `static/` | 静态资源目录，包含CSS样式和JavaScript脚本 |

## ⚙️ 配置参数

### 系统参数配置

您可以在`main.py`中调整以下关键参数：

```python
# 视频处理参数
frame_skip = 10                    # 跳帧参数，控制处理频率
frame_queue = queue.Queue(maxsize=10)  # 视频帧队列大小

# 识别参数
recognition_frequency = 30         # 每30帧进行一次AI识别
max_recognition_results = 50       # 最大历史记录数量

# 服务器参数
host = "0.0.0.0"                  # 服务器监听地址
port = 8000                       # 服务器端口
```

### RTSP配置示例

```python
# 海康威视摄像头
rtsp_url = "rtsp://admin:password@192.168.1.100:554/h264/ch1/main/av_stream"

# 大华摄像头
rtsp_url = "rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0"

# 通用RTSP流
rtsp_url = "rtsp://username:password@ip:port/path"
```

## 🎯 使用指南

### 🖥️ Web界面操作

1. **视频区域**（左侧）
   - 实时显示RTSP视频流
   - 支持全屏查看模式
   - 自动适应窗口大小

2. **识别结果区域**（右侧）
   - 显示AI识别的图像内容描述
   - 按时间倒序排列，最新结果在顶部
   - 支持Markdown格式渲染
   - 自动滚动显示新结果

3. **状态指示器**（顶部）
   - 绿色：系统正常运行
   - 红色：连接异常或系统错误
   - 黄色：正在重连或处理中

### 📱 移动端支持

- **响应式布局**：自动适配手机和平板屏幕
- **触控优化**：支持滑动查看历史记录
- **性能优化**：针对移动设备优化视频播放

## 🔧 高级配置

### 性能优化建议

1. **硬件要求**
   ```
   CPU: 4核心以上（推荐8核心）
   内存: 8GB以上（推荐16GB）
   GPU: 可选，但建议使用NVIDIA GPU加速大模型推理
   网络: 千兆以太网，低延迟
   ```

2. **系统优化参数**
   ```python
   # 针对高分辨率视频流
   frame_skip = 15  # 增加跳帧数，降低CPU占用
   
   # 针对低性能设备
   frame_queue_size = 5  # 减少队列大小，降低内存占用
   
   # 针对网络不稳定环境
   reconnect_interval = 3  # 设置重连间隔
   ```

### Docker部署（可选）

创建`Dockerfile`：
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

构建和运行：
```bash
docker build -t vision-describe .
docker run -p 8000:8000 vision-describe
```

## 🐛 常见问题解决

### 问题1：无法连接RTSP流
**解决方案：**
- 检查RTSP URL格式是否正确
- 确认摄像头网络连接正常
- 验证用户名和密码
- 检查防火墙设置

### 问题2：AI识别响应慢
**解决方案：**
- 增加`frame_skip`参数值
- 减少识别频率（调整识别间隔）
- 确保Ollama服务正常运行
- 考虑使用GPU加速

### 问题3：Web界面无法访问
**解决方案：**
- 检查端口8000是否被占用
- 确认防火墙允许8000端口
- 尝试使用不同的端口号

### 问题4：视频画面卡顿
**解决方案：**
- 调整视频分辨率设置
- 增加帧队列大小
- 检查网络带宽是否充足

## 🤝 开发贡献

### 贡献指南

1. **Fork项目**
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **创建Pull Request**

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8

# 运行测试
pytest tests/

# 代码格式化
black main.py
flake8 main.py
```

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 技术支持

- **问题反馈**：请在GitHub Issues中提交
- **功能建议**：欢迎提交Feature Request
- **技术交流**：欢迎Star⭐和Fork🍴

## 🔮 未来规划

- [ ] 支持多路视频流同时处理
- [ ] 添加用户认证和权限管理
- [ ] 集成更多AI模型选择
- [ ] 支持视频录制和回放功能
- [ ] 添加报警和通知功能
- [ ] 支持云端存储集成
- [ ] 移动端APP开发

---

<div align="center">
  <p>🌟 如果这个项目对您有帮助，请给它一个Star！ 🌟</p>
  <p>📧 有任何问题或建议，随时联系我们</p>
</div>
