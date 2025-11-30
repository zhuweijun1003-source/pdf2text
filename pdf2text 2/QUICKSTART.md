# 🚀 Quick Start Guide - PDF2Text AI

Get your PDF processing application running in minutes!

## Prerequisites

- Python 3.11+ installed
- DeepSeek API key ([Get one here](https://platform.deepseek.com))

## Installation (3 Steps)

### Step 1: Setup Environment

**Windows:**
```cmd
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh run.sh
./setup.sh
```

This will:
- ✅ Install all dependencies
- ✅ Create necessary directories
- ✅ Set up configuration file

### Step 2: Configure API Key

Edit the `.env` file and add your DeepSeek API key:

```env
DEEPSEEK_API_KEY=your_actual_api_key_here
```

### Step 3: Run the Application

**Windows:**
```cmd
run.bat
```

**Linux/Mac:**
```bash
./run.sh
```

**Or directly:**
```bash
streamlit run app.py
```

The application will open automatically at: http://localhost:8501

## Using the Application

### 1. Upload PDF
- Drag & drop your PDF file
- Or click "Browse files" to select
- Enter password if PDF is encrypted

### 2. Configure Settings (Sidebar)
- **API Configuration**: Enter your DeepSeek API key
- **Processing Options**:
  - ✅ Enable Text Preprocessing (recommended)
  - ✅ Enable AI Optimization
  - Choose optimization type (general/grammar/semantic/terminology)
- **Export Options**:
  - Include/exclude metadata
  - Include/exclude tables

### 3. Process
- Click **"🚀 Process PDF"**
- Watch the progress bar
- Wait for completion

### 4. Preview & Export
- View extracted content in tabs:
  - 📝 Text Content (original vs optimized)
  - 📊 Tables
  - ℹ️ Metadata
- Click export buttons:
  - 📄 Export to Word (.docx)
  - 📝 Export to Markdown (.md)
  - 📃 Export to Text (.txt)
  - 📊 Export Tables (JSON)

## Docker Deployment

### Quick Start with Docker

```bash
# Build the image
docker build -t pdf2text-ai .

# Run the container
docker run -p 8501:8501 \
  -e DEEPSEEK_API_KEY=your_key_here \
  -v $(pwd)/outputs:/app/outputs \
  pdf2text-ai
```

### Using Docker Compose

1. Create/edit `.env` file with your API key
2. Run:
```bash
docker-compose up -d
```

Access the app at: http://localhost:8501

## Troubleshooting

### Dependencies Not Installing
```bash
pip install -r requirements.txt --upgrade
```

### API Key Not Working
- Check if key is correct in `.env`
- Verify no extra spaces
- Ensure key has proper permissions

### PDF Won't Process
- Check file size (max 50MB by default)
- Verify PDF is not corrupted
- Enter password if encrypted
- Check logs in `logs/app.log`

### Docker Issues
```bash
# Check logs
docker logs pdf2text-ai

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Features Overview

✅ **PDF Parsing**
- High-precision text extraction
- Table detection and parsing
- Encrypted PDF support
- Large file handling

✅ **AI Optimization**
- Grammar correction
- Semantic enhancement
- Terminology standardization
- Batch processing

✅ **Multiple Export Formats**
- Word (.docx) with formatting
- Markdown (.md) with tables
- Plain text (.txt)
- Table data (JSON/CSV)

✅ **User-Friendly Interface**
- Drag-and-drop upload
- Real-time progress tracking
- Before/after comparison
- Dark/Light theme support

## Next Steps

1. **Customize Settings**: Adjust `config.py` for your needs
2. **Batch Processing**: See `examples.py` for batch operations
3. **API Integration**: Use modules independently in your code
4. **Advanced Features**: Check `README.md` for detailed docs

## Support

- 📖 Full documentation: `README.md`
- 💡 Usage examples: `examples.py`
- 🔍 Check setup: `python check_setup.py`
- 📝 Logs location: `logs/app.log`

## Project Structure

```
pdf2text/
├── app.py                  # Main Streamlit app
├── config.py               # Configuration
├── pdf_parser.py           # PDF extraction
├── text_preprocessor.py    # Text cleaning
├── deepseek_client.py      # AI integration
├── output_generator.py     # Export functions
├── utils.py                # Utilities
├── requirements.txt        # Dependencies
├── Dockerfile             # Container config
└── .env                   # Your settings
```

---

**Ready to process PDFs?** Just run `run.bat` (Windows) or `./run.sh` (Linux/Mac)!
