"""
Text Preprocessing Module
Clean and normalize extracted text from PDFs
Remove special characters, normalize spaces and encoding
"""
import re
import unicodedata
from typing import List, Dict
from loguru import logger


class TextPreprocessor:
    """Text preprocessing and cleaning class"""
    
    def __init__(self):
        """Initialize text preprocessor with cleaning patterns"""
        # Special character patterns to remove
        self.special_char_pattern = re.compile(r'[^\w\s\u4e00-\u9fff.,!?;:()\[\]{}\-\'"/@#$%&*+=<>|\\~`]')
        
        # Multiple space pattern
        self.multi_space_pattern = re.compile(r'\s+')
        
        # Multiple newline pattern
        self.multi_newline_pattern = re.compile(r'\n{3,}')
        
        # Common PDF artifacts to remove
        self.pdf_artifacts = [
            r'\f',  # Form feed
            r'\r',  # Carriage return
            r'\x00',  # Null character
        ]
    
    def remove_special_characters(self, text: str, preserve_punctuation: bool = True) -> str:
        """
        Remove special characters while optionally preserving punctuation
        
        Args:
            text: Input text
            preserve_punctuation: Whether to preserve common punctuation marks
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        try:
            if preserve_punctuation:
                # Remove only truly special characters, keep punctuation
                cleaned = self.special_char_pattern.sub('', text)
            else:
                # Remove all non-alphanumeric characters except spaces
                cleaned = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error removing special characters: {e}")
            return text
    
    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace by replacing multiple spaces with single space
        and multiple newlines with double newline
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized whitespace
        """
        if not text:
            return ""
        
        try:
            # Replace multiple spaces with single space
            text = self.multi_space_pattern.sub(' ', text)
            
            # Replace multiple newlines with double newline
            text = self.multi_newline_pattern.sub('\n\n', text)
            
            # Remove leading/trailing whitespace from each line
            lines = [line.strip() for line in text.split('\n')]
            text = '\n'.join(lines)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error normalizing whitespace: {e}")
            return text
    
    def normalize_encoding(self, text: str, target_encoding: str = 'utf-8') -> str:
        """
        Normalize text encoding and handle problematic characters
        
        Args:
            text: Input text
            target_encoding: Target encoding (default: utf-8)
            
        Returns:
            Text with normalized encoding
        """
        if not text:
            return ""
        
        try:
            # Normalize unicode characters (NFC normalization)
            text = unicodedata.normalize('NFC', text)
            
            # Try to encode/decode to ensure valid encoding
            text = text.encode(target_encoding, errors='ignore').decode(target_encoding)
            
            return text
            
        except Exception as e:
            logger.error(f"Error normalizing encoding: {e}")
            return text
    
    def remove_pdf_artifacts(self, text: str) -> str:
        """
        Remove common PDF extraction artifacts
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        try:
            for artifact in self.pdf_artifacts:
                text = re.sub(artifact, '', text)
            
            return text
            
        except Exception as e:
            logger.error(f"Error removing PDF artifacts: {e}")
            return text
    
    def fix_broken_words(self, text: str) -> str:
        """
        Fix words broken by hyphens at line ends
        
        Args:
            text: Input text
            
        Returns:
            Text with fixed broken words
        """
        if not text:
            return ""
        
        try:
            # Fix hyphenated words at line breaks
            text = re.sub(r'-\s*\n\s*', '', text)
            
            return text
            
        except Exception as e:
            logger.error(f"Error fixing broken words: {e}")
            return text
    
    def remove_headers_footers(self, text: str, remove_page_numbers: bool = True) -> str:
        """
        Attempt to remove common headers, footers, and page numbers
        
        Args:
            text: Input text
            remove_page_numbers: Whether to remove page numbers
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        try:
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Skip if line is just a number (page number)
                if remove_page_numbers and line.strip().isdigit():
                    continue
                
                # Skip very short lines at beginning/end (likely headers/footers)
                if len(line.strip()) < 5 and (not cleaned_lines or line == lines[-1]):
                    continue
                
                cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
            
        except Exception as e:
            logger.error(f"Error removing headers/footers: {e}")
            return text
    
    def clean_text(
        self,
        text: str,
        remove_special: bool = True,
        normalize_space: bool = True,
        normalize_encode: bool = True,
        remove_artifacts: bool = True,
        fix_words: bool = True,
        remove_headers: bool = False
    ) -> str:
        """
        Apply all cleaning operations to text
        
        Args:
            text: Input text
            remove_special: Remove special characters
            normalize_space: Normalize whitespace
            normalize_encode: Normalize encoding
            remove_artifacts: Remove PDF artifacts
            fix_words: Fix broken words
            remove_headers: Remove headers and footers
            
        Returns:
            Fully cleaned text
        """
        if not text:
            return ""
        
        logger.info("Starting text preprocessing...")
        
        # Apply cleaning operations in order
        if remove_artifacts:
            text = self.remove_pdf_artifacts(text)
        
        if normalize_encode:
            text = self.normalize_encoding(text)
        
        if fix_words:
            text = self.fix_broken_words(text)
        
        if remove_special:
            text = self.remove_special_characters(text, preserve_punctuation=True)
        
        if normalize_space:
            text = self.normalize_whitespace(text)
        
        if remove_headers:
            text = self.remove_headers_footers(text)
        
        logger.info(f"Text preprocessing complete. Length: {len(text)} characters")
        
        return text
    
    def clean_table_data(self, table_data: List[List[str]]) -> List[List[str]]:
        """
        Clean table data by normalizing cell contents
        
        Args:
            table_data: 2D list representing table data
            
        Returns:
            Cleaned table data
        """
        try:
            cleaned_table = []
            
            for row in table_data:
                cleaned_row = []
                for cell in row:
                    # Clean each cell
                    cleaned_cell = self.clean_text(
                        str(cell),
                        remove_special=False,
                        normalize_space=True,
                        normalize_encode=True,
                        remove_artifacts=True,
                        fix_words=False,
                        remove_headers=False
                    )
                    cleaned_row.append(cleaned_cell)
                
                cleaned_table.append(cleaned_row)
            
            return cleaned_table
            
        except Exception as e:
            logger.error(f"Error cleaning table data: {e}")
            return table_data
    
    def preprocess_pdf_result(self, pdf_result: Dict) -> Dict:
        """
        Preprocess entire PDF parsing result
        
        Args:
            pdf_result: Dictionary from PDF parser
            
        Returns:
            Dictionary with preprocessed content
        """
        try:
            logger.info("Preprocessing PDF extraction result...")
            
            # Clean all text
            pdf_result['all_text'] = self.clean_text(pdf_result['all_text'])
            
            # Clean page-by-page text
            for page in pdf_result['pages']:
                page['text'] = self.clean_text(page['text'])
                
                # Clean paragraphs
                page['paragraphs'] = [
                    self.clean_text(para) for para in page['paragraphs']
                ]
                
                # Clean tables
                for table in page['tables']:
                    table['data'] = self.clean_table_data(table['data'])
            
            # Clean all tables
            for table in pdf_result['all_tables']:
                table['data'] = self.clean_table_data(table['data'])
            
            logger.info("PDF result preprocessing complete")
            
            return pdf_result
            
        except Exception as e:
            logger.error(f"Error preprocessing PDF result: {e}")
            return pdf_result


def preprocess_text(text: str, **kwargs) -> str:
    """
    Convenience function to preprocess text
    
    Args:
        text: Input text
        **kwargs: Additional arguments for clean_text
        
    Returns:
        Cleaned text
    """
    preprocessor = TextPreprocessor()
    return preprocessor.clean_text(text, **kwargs)
