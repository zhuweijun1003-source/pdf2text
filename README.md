# PDF智能处理系统

一个强大的Python Web应用程序，可以从PDF中提取内容，使用DeepSeek AI进行优化，并导出为多种格式。
<img width="1279" height="874" alt="image" src="https://github.com/user-attachments/assets/f9f226ff-8705-4aaf-b771-913479b035f1" />


## 功能特点

- **高精度PDF解析**：从PDF中提取带有位置信息的文本和表格
- **AI智能摘要**：使用DeepSeek API改进文本质量
- **多种导出格式**：Word (.docx)、Markdown (.md)、Text (.txt)、JSON、Excel (.xlsx)
- **美观的Web界面**：使用Streamlit构建，易于交互
- **高级功能**：
  - 加密PDF支持
  - 大文件处理，带进度跟踪
  - 文本预处理和清理
  - 前后对比视图
  - 批处理并行优化
  - Excel表格导出

## 快速开始

### 1. 安装

```bash
# 克隆或下载此仓库
cd pdf2text

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置

在项目根目录创建`.env`文件：

```env
DEEPSEEK_API_KEY=你的API密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
MAX_FILE_SIZE_MB=50
ENABLE_LOGGING=true
LOG_LEVEL=INFO
```

### 3. 运行应用

```bash
streamlit run app.py
```

应用将在浏览器中打开，地址为 `http://localhost:8501`

# Docker部署

### 构建和运行

```bash
# 构建Docker镜像
docker build -t pdf2text-ai .

# 运行容器
docker run -p 8501:8501 \
  -e DEEPSEEK_API_KEY=你的密钥 \
  -v $(pwd)/outputs:/app/outputs \
  pdf2text-ai
```

### 使用Docker Compose

```bash
docker-compose up -d
```

## 使用指南

### 1. 上传PDF
- 拖放PDF文件或点击浏览
- 如果PDF已加密，输入密码

### 2. 配置设置
- **启用AI总结**：启用文本预处理（可选）
- **导出选项**：包含/排除元数据和表格

### 3. 处理
- 点击"处理PDF"开始提取
- 查看进度条和状态更新

### 4. 预览和导出
- 在预览面板中查看提取的内容
- 如需要，生成AI摘要
- 导出为您喜欢的格式
- 下载表格为Excel格式

## 项目结构

```
pdf2text/
├── app.py                  # Streamlit Web应用
├── config.py               # 配置管理
├── pdf_parser.py           # PDF提取模块
├── text_preprocessor.py    # 文本清理模块
├── deepseek_client.py      # DeepSeek API集成
├── output_generator.py     # 导出模块
├── utils.py                # 工具函数和错误处理
├── requirements.txt        # Python依赖
├── Dockerfile              # Docker配置
├── .env.example            # 环境变量模板
└── README.md               # 本文件
```

## API文档

### DeepSeek API

本应用使用DeepSeek Chat Completions API。在此获取API密钥：https://platform.deepseek.com

支持的摘要长度：
- **简短**：约100-200字的核心内容
- **中等**：约300-500字的详细总结
- **详细**：约500-800字的完整摘要

## 错误处理

应用包含全面的错误处理：
- 文件验证（大小、格式）
- PDF加密处理
- API超时和重试逻辑
- 速率限制回退
- 详细的错误消息和日志

## 性能优化

- **分块处理**：大文本分割以提高处理效率
- **并行优化**：多线程API调用
- **进度跟踪**：实时状态更新
- **内存管理**：分页PDF解析

## 日志

日志存储在`logs/`目录中：
- 文件大小达到10MB时自动轮转
- 保留7天
- 压缩（zip）

## 故障排除

### 常见问题

**1. 运行时导入错误**
```bash
pip install -r requirements.txt --upgrade
```

**2. API密钥无效**
- 验证`.env`文件中的API密钥
- 检查API配额和限制

**3. 大型PDF处理失败**
- 在`.env`中增加MAX_FILE_SIZE_MB
- 如果PDF已加密，使用密码

**4. Docker容器无法启动**
```bash
docker logs <容器ID>
```

## 系统要求

- Python 3.11+
- DeepSeek API密钥
- 推荐2GB+内存
- API调用需要互联网连接

## 许可证

本项目用于教育和开发目的。

## 支持

如有问题，请查看`logs/app.log`中的错误日志
