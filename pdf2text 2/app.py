"""
Streamlit Web Application
Beautiful UI for PDF processing with AI-powered optimization
"""
import streamlit as st
import tempfile
from pathlib import Path
import time
from datetime import datetime
import os

# Import custom modules
from config import Config
from pdf_parser import PDFParser
from text_preprocessor import TextPreprocessor
from deepseek_client import DeepSeekClient
from output_generator import WordGenerator, MarkdownGenerator, DataExporter
from utils import (
    validate_file_size, validate_file_format,
    PDFProcessingError, APIError, ValidationError,
    ProgressTracker
)

# Page configuration
st.set_page_config(
    page_title="PDF智能处理系统",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .upload-section {
        padding: 2rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 2rem;
    }
    .stats-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #e8f4f8;
        margin: 0.5rem 0;
    }
    div.stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #1557a0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'pdf_result' not in st.session_state:
        st.session_state.pdf_result = None
    if 'optimized_result' not in st.session_state:
        st.session_state.optimized_result = None
    if 'processing_stage' not in st.session_state:
        st.session_state.processing_stage = 'upload'
    if 'api_configured' not in st.session_state:
        st.session_state.api_configured = False
    if 'use_ai_optimization' not in st.session_state:
        st.session_state.use_ai_optimization = False
    if 'uploaded_pdf_data' not in st.session_state:
        st.session_state.uploaded_pdf_data = None


def check_api_configuration():
    """Check if API is configured"""
    try:
        Config.validate()
        st.session_state.api_configured = True
        return True
    except ValueError as e:
        st.session_state.api_configured = False
        return False


def sidebar():
    """Render sidebar with settings and info"""
    with st.sidebar:
        st.markdown("## ⚙️ 设置")
        
        # Processing Options
        st.markdown("### 🛠️ 处理选项")
        
        preprocessing = st.checkbox("启用AI总结", value=False)
        
        st.markdown("---")
        
        # Export Options
        st.markdown("### 📤 导出选项")
        
        include_metadata = st.checkbox("包含元数据", value=True)
        include_tables = st.checkbox("包含表格", value=True)
        
        st.markdown("---")
        
        # Statistics
        if st.session_state.pdf_result:
            st.markdown("### 📊 文档统计")
            stats = st.session_state.pdf_result.get('statistics', {})
            
            st.metric("总页数", stats.get('total_pages', 0))
            st.metric("总字数", stats.get('total_words', 0))
            st.metric("总表格数", stats.get('total_tables', 0))
            st.metric("总段落数", stats.get('total_paragraphs', 0))
        
        st.markdown("---")
        
        # QR Codes Section
        st.markdown("### 📱 关注我们")
        
        # Public Account QR Code
        try:
            from PIL import Image
            import os
            
            # Get the directory of the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Public Account QR Code
            gongzhonghao_path = os.path.join(current_dir, 'pic', 'gongzhonghao.jpg')
            if os.path.exists(gongzhonghao_path):
                st.markdown("**公众号**")
                gongzhonghao_img = Image.open(gongzhonghao_path)
                st.image(gongzhonghao_img, use_container_width=True)
            
            # Tip/Donation QR Code
            dashang_path = os.path.join(current_dir, 'pic', 'dashang.jpg')
            if os.path.exists(dashang_path):
                st.markdown("**打赏支持**")
                dashang_img = Image.open(dashang_path)
                st.image(dashang_img, use_container_width=True)
                
        except Exception as e:
            # Silently fail if images cannot be loaded
            pass
        
        return {
            'preprocessing': preprocessing,
            'include_metadata': include_metadata,
            'include_tables': include_tables
        }


def upload_section():
    """File upload section"""
    st.markdown('<div class="main-header">📄 PDF智能处理系统</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">提取、优化与转换PDF内容</div>', unsafe_allow_html=True)
    
    # Upload area
    uploaded_file = st.file_uploader(
        "拖拽或选择PDF文件",
        type=['pdf'],
        help=f"最大文件大小: {Config.MAX_FILE_SIZE_MB}MB"
    )
    
    # Password input
    password = None
    if uploaded_file:
        col1, col2 = st.columns([3, 1])
        with col1:
            password = st.text_input(
                "PDF密码（如果已加密）",
                type="password",
                help="如果PDF未加密请留空"
            )
    
    return uploaded_file, password


def process_pdf(uploaded_file, password, settings):
    """Process PDF file"""
    try:
        # Validate file
        file_size = uploaded_file.size
        validate_file_size(file_size)
        
        # Store original PDF data for direct conversion
        st.session_state.uploaded_pdf_data = uploaded_file.getvalue()
        
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🔄 正在处理PDF...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name
            
            try:
                # Step 1: Parse PDF
                status_text.text("📖 正在提取PDF内容...")
                progress_bar.progress(20)
                
                parser = PDFParser(tmp_path, password=password if password else None)
                
                def progress_callback(current, total):
                    progress = 20 + int((current / total) * 50)
                    progress_bar.progress(progress)
                    status_text.text(f"📖 正在解析第 {current}/{total} 页...")
                
                pdf_result = parser.parse(progress_callback=progress_callback)
                st.session_state.pdf_result = pdf_result
                
                # Step 2: Preprocess
                if settings['preprocessing']:
                    status_text.text("🧹 正在预处理文本...")
                    progress_bar.progress(80)
                    
                    preprocessor = TextPreprocessor()
                    pdf_result = preprocessor.preprocess_pdf_result(pdf_result)
                    st.session_state.pdf_result = pdf_result
                
                # Set optimized_result to pdf_result (AI optimization is now optional)
                st.session_state.optimized_result = pdf_result
                progress_bar.progress(100)
                status_text.text("✅ 处理完成！")
                
                time.sleep(0.5)
                st.session_state.processing_stage = 'preview'
                st.rerun()
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                
    except ValidationError as e:
        st.error(f"❌ 验证错误: {e.message}")
        if e.details:
            st.info(e.details)
    except PDFProcessingError as e:
        st.error(f"❌ PDF处理错误: {e.message}")
        if e.details:
            st.info(e.details)
    except APIError as e:
        st.error(f"❌ API错误: {e.message}")
        if e.details:
            st.info(e.details)
    except Exception as e:
        st.error(f"❌ 未知错误: {str(e)}")
        st.exception(e)


def preview_section(settings):
    """Preview extracted and optimized content"""
    st.markdown("### 👀 内容预览")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📝 文本内容", "📊 表格", "ℹ️ 元数据"])
    
    with tab1:
        if st.session_state.optimized_result:
            # Show only extracted text (AI optimization is optional)
            st.markdown("#### 提取的文本")
            extracted_text = st.session_state.pdf_result.get('all_text', '')
            st.text_area(
                "提取的文本",
                extracted_text[:5000] + ("..." if len(extracted_text) > 5000 else ""),
                height=400,
                label_visibility="collapsed"
            )
            
            # Show AI summarization option if text exists
            if extracted_text and not st.session_state.use_ai_optimization:
                st.markdown("---")
                if st.button("🤖 生成文本摘要", use_container_width=True):
                    st.session_state.use_ai_optimization = True
                    st.rerun()
    
    with tab2:
        if st.session_state.pdf_result:
            tables = st.session_state.pdf_result.get('all_tables', [])
            
            if tables:
                st.markdown(f"**找到 {len(tables)} 个表格**")
                
                # Add Excel download button
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("📥 下载Excel", use_container_width=True):
                        try:
                            import pandas as pd
                            from io import BytesIO
                            
                            # Create Excel file in memory
                            output = BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                for idx, table in enumerate(tables, 1):
                                    table_data = table.get('data', [])
                                    if table_data:
                                        df = pd.DataFrame(table_data[1:], columns=table_data[0] if len(table_data) > 0 else None)
                                        sheet_name = f'表格{idx}'
                                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                            
                            output.seek(0)
                            
                            st.download_button(
                                label="⬇️ 下载所有表格",
                                data=output,
                                file_name=f"tables_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                            st.success("✅ Excel文件已准备好！")
                        except Exception as e:
                            st.error(f"生成Excel时出错: {e}")
                
                for idx, table in enumerate(tables, 1):
                    with st.expander(f"表格 {idx}"):
                        table_data = table.get('data', [])
                        if table_data:
                            st.table(table_data[:10])  # Show first 10 rows
                            if len(table_data) > 10:
                                st.info(f"显示前10行，共{len(table_data)}行")
            else:
                st.info("文档中未发现表格")
    
    with tab3:
        if st.session_state.pdf_result:
            metadata = st.session_state.pdf_result.get('metadata', {})
            
            for key, value in metadata.items():
                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")


def ai_optimization_section():
    """AI summarization section"""
    st.markdown("### 🤖 AI文本摘要")
    
    # API Configuration
    st.markdown("#### 🔑 API配置")
    
    api_key = st.text_input(
        "DeepSeek API密钥",
        value=Config.DEEPSEEK_API_KEY,
        type="password",
        help="请输入您的DeepSeek API密钥"
    )
    
    if api_key:
        Config.DEEPSEEK_API_KEY = api_key
        st.session_state.api_configured = True
    
    # Summary length option
    summary_length = st.selectbox(
        "摘要长度",
        ["short", "medium", "long"],
        format_func=lambda x: {
            "short": "简短（约100-200字）",
            "medium": "中等（约300-500字）",
            "long": "详细（约500-800字）"
        }[x],
        help="选择摘要的详细程度"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ 生成摘要", use_container_width=True, disabled=not st.session_state.api_configured):
            if not st.session_state.api_configured:
                st.error("❌ 请先配置API密钥")
            else:
                with st.spinner("🤖 AI正在生成文本摘要..."):
                    try:
                        client = DeepSeekClient()
                        
                        # Generate summary
                        summary_text = client.summarize_text(
                            st.session_state.pdf_result['all_text'],
                            length=summary_length
                        )
                        
                        # Update optimized result with summary
                        optimized_result = st.session_state.pdf_result.copy()
                        optimized_result['all_text'] = summary_text
                        st.session_state.optimized_result = optimized_result
                        
                        st.success("✅ 摘要生成完成！")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ 摘要生成失败: {str(e)}")
    
    with col2:
        if st.button("🔄 重置为原文", use_container_width=True):
            st.session_state.optimized_result = st.session_state.pdf_result.copy()
            st.session_state.use_ai_optimization = False
            st.success("✅ 已重置为原始文本")
            st.rerun()
    
    # Show comparison if summarized
    if st.session_state.optimized_result.get('all_text') != st.session_state.pdf_result.get('all_text'):
        st.markdown("---")
        st.markdown("#### 📊 摘要对比")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**原始文本**")
            original_text = st.session_state.pdf_result.get('all_text', '')
            st.text_area(
                "原始",
                original_text[:3000] + ("..." if len(original_text) > 3000 else ""),
                height=300,
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**生成的摘要**")
            summary_text = st.session_state.optimized_result.get('all_text', '')
            st.text_area(
                "摘要",
                summary_text,
                height=300,
                label_visibility="collapsed"
            )


def export_section(settings):
    """Export options and download buttons"""
    st.markdown("### 📥 导出文档")
    
    if not st.session_state.optimized_result:
        st.warning("没有可导出的内容，请先处理PDF文件。")
        return
    
    # Add direct PDF to Word conversion button
    st.markdown("#### 🔄 直接转换")
    col_convert = st.columns(1)[0]
    
    if st.button("📄 PDF直接转Word（保持原样）", use_container_width=True):
        with st.spinner("正在转换PDF为Word..."):
            try:
                from pdf2docx import Converter
                import tempfile
                import os
                
                # Save the original PDF if we have it
                if hasattr(st.session_state, 'uploaded_pdf_data'):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
                        tmp_pdf.write(st.session_state.uploaded_pdf_data)
                        pdf_path = tmp_pdf.name
                    
                    output_path = Config.OUTPUT_DIR / f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                    
                    # Convert PDF to Word
                    cv = Converter(pdf_path)
                    cv.convert(str(output_path), start=0, end=None)
                    cv.close()
                    
                    # Clean up temp file
                    os.remove(pdf_path)
                    
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ 下载转换的Word",
                            data=f,
                            file_name=output_path.name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    
                    st.success("✅ PDF已转换为Word！")
                else:
                    st.error("❌ 未找到原始PDF文件，请重新上传处理。")
                    
            except ImportError:
                st.error("❌ 缺少pdf2docx库，请运行: pip install pdf2docx")
            except Exception as e:
                st.error(f"转换失败: {e}")
    
    st.markdown("---")
    st.markdown("#### 📤 导出处理后内容")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Export to Word
    with col1:
        if st.button("📄 导出为Word"):
            with st.spinner("正在生成Word文档..."):
                try:
                    word_gen = WordGenerator()
                    word_gen.generate_from_pdf_result(
                        st.session_state.optimized_result,
                        include_metadata=settings['include_metadata'],
                        include_tables=settings['include_tables']
                    )
                    
                    output_path = Config.OUTPUT_DIR / f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                    word_gen.save(str(output_path))
                    
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ 下载Word",
                            data=f,
                            file_name=output_path.name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    
                    st.success("✅ Word文档已生成！")
                    
                except Exception as e:
                    st.error(f"生成Word文档时出错: {e}")
    
    # Export to Markdown
    with col2:
        if st.button("📝 导出为Markdown"):
            with st.spinner("正在生成Markdown文档..."):
                try:
                    md_gen = MarkdownGenerator()
                    md_gen.generate_from_pdf_result(
                        st.session_state.optimized_result,
                        include_metadata=settings['include_metadata'],
                        include_tables=settings['include_tables']
                    )
                    
                    output_path = Config.OUTPUT_DIR / f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    md_gen.save(str(output_path))
                    
                    with open(output_path, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="⬇️ 下载Markdown",
                            data=f.read(),
                            file_name=output_path.name,
                            mime="text/markdown"
                        )
                    
                    st.success("✅ Markdown文档已生成！")
                    
                except Exception as e:
                    st.error(f"生成Markdown文档时出错: {e}")
    
    # Export to Text
    with col3:
        if st.button("📃 导出为文本"):
            try:
                text_content = st.session_state.optimized_result.get('all_text', '')
                
                st.download_button(
                    label="⬇️ 下载文本",
                    data=text_content,
                    file_name=f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
                
                st.success("✅ 文本已准备好下载！")
                
            except Exception as e:
                st.error(f"导出文本时出错: {e}")
    
    # Export Tables
    with col4:
        if st.button("📊 导出表格(JSON)"):
            try:
                tables = st.session_state.optimized_result.get('all_tables', [])
                
                if tables:
                    output_path = Config.OUTPUT_DIR / f"tables_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    DataExporter.export_tables_to_json(tables, str(output_path))
                    
                    with open(output_path, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="⬇️ 下载表格",
                            data=f.read(),
                            file_name=output_path.name,
                            mime="application/json"
                        )
                    
                    st.success("✅ 表格已导出！")
                else:
                    st.info("没有可导出的表格")
                    
            except Exception as e:
                st.error(f"导出表格时出错: {e}")


def main():
    """Main application logic"""
    initialize_session_state()
    check_api_configuration()
    
    # Render sidebar
    settings = sidebar()
    
    # Main content area
    if st.session_state.processing_stage == 'upload':
        uploaded_file, password = upload_section()
        
        if uploaded_file:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🚀 处理PDF", use_container_width=True):
                    process_pdf(uploaded_file, password, settings)
    
    elif st.session_state.processing_stage == 'preview':
        # Show preview
        preview_section(settings)
        
        # Show AI summarization section if user clicked the button
        if st.session_state.use_ai_optimization:
            st.markdown("---")
            ai_optimization_section()
        
        st.markdown("---")
        export_section(settings)
        
        st.markdown("---")
        
        # Reset button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 处理新的PDF", use_container_width=True):
                st.session_state.pdf_result = None
                st.session_state.optimized_result = None
                st.session_state.processing_stage = 'upload'
                st.session_state.use_ai_optimization = False
                st.rerun()


if __name__ == "__main__":
    main()
