"""
PDF Parsing Module
High-precision extraction of text and tables from PDF files using pdfplumber
Supports encrypted PDFs, large files with progress tracking
"""
import pdfplumber
import PyPDF2
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger
from tqdm import tqdm
import io


class PDFParser:
    """PDF parsing and content extraction class"""
    
    def __init__(self, pdf_path: str, password: Optional[str] = None):
        """
        Initialize PDF parser
        
        Args:
            pdf_path: Path to PDF file
            password: Password for encrypted PDFs
        """
        self.pdf_path = Path(pdf_path)
        self.password = password
        self.metadata = {}
        self.pages_data = []
        
        # Validate file
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not self.pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File must be a PDF: {pdf_path}")
        
        logger.info(f"Initialized PDF parser for: {self.pdf_path.name}")
    
    def check_encryption(self) -> bool:
        """
        Check if PDF is encrypted
        
        Returns:
            True if encrypted, False otherwise
        """
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return pdf_reader.is_encrypted
        except Exception as e:
            logger.error(f"Error checking encryption: {e}")
            return False
    
    def extract_metadata(self) -> Dict:
        """
        Extract PDF metadata
        
        Returns:
            Dictionary containing metadata
        """
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Handle encrypted PDFs
                if pdf_reader.is_encrypted:
                    if self.password:
                        pdf_reader.decrypt(self.password)
                    else:
                        logger.warning("PDF is encrypted but no password provided")
                        return {}
                
                metadata = pdf_reader.metadata
                self.metadata = {
                    'title': metadata.get('/Title', 'Unknown'),
                    'author': metadata.get('/Author', 'Unknown'),
                    'subject': metadata.get('/Subject', 'Unknown'),
                    'creator': metadata.get('/Creator', 'Unknown'),
                    'producer': metadata.get('/Producer', 'Unknown'),
                    'creation_date': metadata.get('/CreationDate', 'Unknown'),
                    'num_pages': len(pdf_reader.pages)
                }
                
                logger.info(f"Extracted metadata: {self.metadata['num_pages']} pages")
                return self.metadata
                
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}
    
    def extract_text_from_page(self, page) -> Dict:
        """
        Extract text from a single page with position information
        
        Args:
            page: pdfplumber page object
            
        Returns:
            Dictionary with text content and metadata
        """
        try:
            # Extract full text
            text = page.extract_text() or ""
            
            # Extract text with position information
            words = page.extract_words(
                x_tolerance=3,
                y_tolerance=3,
                keep_blank_chars=True
            )
            
            # Group words by paragraphs based on y-position
            paragraphs = []
            current_para = []
            last_y = None
            line_threshold = 10  # pixels
            
            for word in words:
                current_y = word['top']
                
                if last_y is None or abs(current_y - last_y) < line_threshold:
                    current_para.append(word['text'])
                else:
                    if current_para:
                        paragraphs.append(' '.join(current_para))
                    current_para = [word['text']]
                
                last_y = current_y
            
            # Add last paragraph
            if current_para:
                paragraphs.append(' '.join(current_para))
            
            return {
                'page_number': page.page_number,
                'text': text,
                'paragraphs': paragraphs,
                'word_count': len(words),
                'width': page.width,
                'height': page.height
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from page {page.page_number}: {e}")
            return {
                'page_number': page.page_number,
                'text': '',
                'paragraphs': [],
                'word_count': 0,
                'width': 0,
                'height': 0
            }
    
    def extract_tables_from_page(self, page) -> List[Dict]:
        """
        Extract tables from a single page
        Supports complex structures including merged cells
        
        Args:
            page: pdfplumber page object
            
        Returns:
            List of table dictionaries
        """
        try:
            tables_data = []
            tables = page.extract_tables()
            
            for idx, table in enumerate(tables):
                if not table:
                    continue
                
                # Clean and process table data
                cleaned_table = []
                for row in table:
                    cleaned_row = [cell.strip() if cell else '' for cell in row]
                    cleaned_table.append(cleaned_row)
                
                tables_data.append({
                    'table_number': idx + 1,
                    'data': cleaned_table,
                    'rows': len(cleaned_table),
                    'columns': len(cleaned_table[0]) if cleaned_table else 0
                })
            
            return tables_data
            
        except Exception as e:
            logger.error(f"Error extracting tables from page {page.page_number}: {e}")
            return []
    
    def parse(self, progress_callback=None) -> Dict:
        """
        Parse entire PDF with progress tracking
        
        Args:
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary containing all extracted content
        """
        try:
            # Extract metadata first
            self.extract_metadata()
            
            result = {
                'metadata': self.metadata,
                'pages': [],
                'all_text': '',
                'all_tables': [],
                'statistics': {
                    'total_pages': 0,
                    'total_words': 0,
                    'total_tables': 0,
                    'total_paragraphs': 0
                }
            }
            
            # Open PDF with pdfplumber
            with pdfplumber.open(self.pdf_path, password=self.password) as pdf:
                total_pages = len(pdf.pages)
                result['statistics']['total_pages'] = total_pages
                
                logger.info(f"Starting to parse {total_pages} pages...")
                
                # Process each page with progress tracking
                for page_num, page in enumerate(tqdm(pdf.pages, desc="Parsing PDF", disable=progress_callback is not None), 1):
                    # Extract text
                    page_text_data = self.extract_text_from_page(page)
                    
                    # Extract tables
                    page_tables = self.extract_tables_from_page(page)
                    
                    # Combine page data
                    page_data = {
                        **page_text_data,
                        'tables': page_tables
                    }
                    
                    result['pages'].append(page_data)
                    result['all_text'] += page_text_data['text'] + '\n\n'
                    result['all_tables'].extend(page_tables)
                    
                    # Update statistics
                    result['statistics']['total_words'] += page_text_data['word_count']
                    result['statistics']['total_tables'] += len(page_tables)
                    result['statistics']['total_paragraphs'] += len(page_text_data['paragraphs'])
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback(page_num, total_pages)
            
            logger.info(f"Successfully parsed PDF: {result['statistics']}")
            self.pages_data = result['pages']
            return result
            
        except PyPDF2.errors.FileNotDecryptedError:
            logger.error("PDF is encrypted and requires a password")
            raise ValueError("PDF is encrypted. Please provide the correct password.")
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise
    
    def get_page_count(self) -> int:
        """Get total number of pages in PDF"""
        try:
            with pdfplumber.open(self.pdf_path, password=self.password) as pdf:
                return len(pdf.pages)
        except Exception as e:
            logger.error(f"Error getting page count: {e}")
            return 0
    
    def extract_page_range(self, start_page: int, end_page: int) -> Dict:
        """
        Extract content from a specific page range
        
        Args:
            start_page: Starting page number (1-indexed)
            end_page: Ending page number (1-indexed)
            
        Returns:
            Dictionary containing extracted content from page range
        """
        try:
            result = {
                'pages': [],
                'text': '',
                'tables': []
            }
            
            with pdfplumber.open(self.pdf_path, password=self.password) as pdf:
                for page_num in range(start_page - 1, min(end_page, len(pdf.pages))):
                    page = pdf.pages[page_num]
                    
                    page_text_data = self.extract_text_from_page(page)
                    page_tables = self.extract_tables_from_page(page)
                    
                    result['pages'].append({
                        **page_text_data,
                        'tables': page_tables
                    })
                    result['text'] += page_text_data['text'] + '\n\n'
                    result['tables'].extend(page_tables)
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting page range: {e}")
            raise


def parse_pdf_file(
    pdf_path: str,
    password: Optional[str] = None,
    progress_callback=None
) -> Dict:
    """
    Convenience function to parse a PDF file
    
    Args:
        pdf_path: Path to PDF file
        password: Optional password for encrypted PDFs
        progress_callback: Optional callback for progress updates
        
    Returns:
        Dictionary containing all extracted content
    """
    parser = PDFParser(pdf_path, password)
    return parser.parse(progress_callback)
