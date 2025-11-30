"""
Example Usage of PDF2Text AI Application Modules

This file demonstrates how to use each module independently
for advanced customization or integration into other projects.
"""

# Example 1: PDF Parsing Only
def example_pdf_parsing():
    """Extract content from PDF without AI optimization"""
    from pdf_parser import PDFParser
    
    # Initialize parser
    parser = PDFParser('sample.pdf', password=None)
    
    # Check if encrypted
    is_encrypted = parser.check_encryption()
    print(f"PDF is encrypted: {is_encrypted}")
    
    # Extract metadata
    metadata = parser.extract_metadata()
    print(f"Metadata: {metadata}")
    
    # Parse entire document
    result = parser.parse()
    
    # Access extracted data
    print(f"Total pages: {result['statistics']['total_pages']}")
    print(f"Total words: {result['statistics']['total_words']}")
    print(f"Full text: {result['all_text'][:500]}...")
    
    # Access specific page
    first_page = result['pages'][0]
    print(f"Page 1 text: {first_page['text'][:200]}...")
    
    # Access tables
    for table in result['all_tables']:
        print(f"Table data: {table['data']}")


# Example 2: Text Preprocessing
def example_text_preprocessing():
    """Clean and normalize extracted text"""
    from text_preprocessor import TextPreprocessor
    
    preprocessor = TextPreprocessor()
    
    # Sample text with issues
    dirty_text = """This  is   a   sample\n\n\n\ntext with  issues.
    It has-\nbroken words and\fspecial\x00characters."""
    
    # Clean the text
    clean_text = preprocessor.clean_text(
        dirty_text,
        remove_special=True,
        normalize_space=True,
        normalize_encode=True,
        remove_artifacts=True,
        fix_words=True
    )
    
    print(f"Original: {dirty_text}")
    print(f"Cleaned: {clean_text}")
    
    # Clean table data
    table_data = [
        ['Header 1  ', '  Header 2', 'Header\n3'],
        ['Data   1', 'Data  2  ', '  Data 3']
    ]
    
    clean_table = preprocessor.clean_table_data(table_data)
    print(f"Cleaned table: {clean_table}")


# Example 3: DeepSeek API Integration
def example_deepseek_optimization():
    """Optimize text using DeepSeek API"""
    from deepseek_client import DeepSeekClient
    import os
    
    # Initialize client
    client = DeepSeekClient(api_key=os.getenv('DEEPSEEK_API_KEY'))
    
    # Sample text
    text = """This text have some grammar errors and could be improve.
    The sentence structure not very good and need optimization."""
    
    # Optimize with different types
    
    # 1. General optimization
    optimized = client.optimize_text(
        text,
        optimization_type='general'
    )
    print(f"General optimization: {optimized}")
    
    # 2. Grammar correction only
    grammar_fixed = client.optimize_text(
        text,
        optimization_type='grammar'
    )
    print(f"Grammar fixed: {grammar_fixed}")
    
    # 3. Semantic enhancement
    semantic = client.optimize_text(
        text,
        optimization_type='semantic'
    )
    print(f"Semantic enhancement: {semantic}")
    
    # 4. Custom instructions
    custom = client.optimize_text(
        text,
        optimization_type='general',
        custom_instructions='Make the text more formal and academic'
    )
    print(f"Custom optimization: {custom}")
    
    # 5. Process long text in chunks
    long_text = text * 100  # Simulate long text
    chunked_result = client.optimize_text_chunks(
        long_text,
        chunk_size=1000,
        optimization_type='grammar',
        max_workers=3
    )
    print(f"Chunked result length: {len(chunked_result)}")


# Example 4: Export to Word
def example_word_export():
    """Generate Word documents from content"""
    from output_generator import WordGenerator
    
    # Initialize generator
    word_gen = WordGenerator()
    
    # Add title
    word_gen.add_title('Sample Document')
    
    # Add headings
    word_gen.add_heading('Chapter 1', level=1)
    word_gen.add_heading('Section 1.1', level=2)
    
    # Add paragraphs
    word_gen.add_paragraph('This is the first paragraph.')
    word_gen.add_paragraph('This is the second paragraph.')
    
    # Add table
    table_data = [
        ['Header 1', 'Header 2', 'Header 3'],
        ['Data 1', 'Data 2', 'Data 3'],
        ['Data 4', 'Data 5', 'Data 6']
    ]
    word_gen.add_table(table_data, has_header=True)
    
    # Save document
    word_gen.save('output.docx')
    print('Word document saved!')


# Example 5: Export to Markdown
def example_markdown_export():
    """Generate Markdown documents from content"""
    from output_generator import MarkdownGenerator
    
    # Initialize generator
    md_gen = MarkdownGenerator()
    
    # Add title
    md_gen.add_title('Sample Document')
    
    # Add headings
    md_gen.add_heading('Chapter 1', level=2)
    md_gen.add_heading('Section 1.1', level=3)
    
    # Add paragraphs
    md_gen.add_paragraph('This is the first paragraph.')
    md_gen.add_paragraph('This is the second paragraph.')
    
    # Add table
    table_data = [
        ['Header 1', 'Header 2', 'Header 3'],
        ['Data 1', 'Data 2', 'Data 3'],
        ['Data 4', 'Data 5', 'Data 6']
    ]
    md_gen.add_table(table_data, has_header=True)
    
    # Add code block
    md_gen.add_code_block('print("Hello, World!")', language='python')
    
    # Save document
    md_gen.save('output.md')
    print('Markdown document saved!')


# Example 6: Complete Workflow
def example_complete_workflow():
    """Complete PDF processing workflow"""
    from pdf_parser import PDFParser
    from text_preprocessor import TextPreprocessor
    from deepseek_client import DeepSeekClient
    from output_generator import WordGenerator, MarkdownGenerator
    import os
    
    print("Starting complete workflow...")
    
    # Step 1: Parse PDF
    print("[1/5] Parsing PDF...")
    parser = PDFParser('sample.pdf')
    pdf_result = parser.parse()
    
    # Step 2: Preprocess text
    print("[2/5] Preprocessing text...")
    preprocessor = TextPreprocessor()
    pdf_result = preprocessor.preprocess_pdf_result(pdf_result)
    
    # Step 3: Optimize with AI
    print("[3/5] Optimizing with AI...")
    client = DeepSeekClient(api_key=os.getenv('DEEPSEEK_API_KEY'))
    optimized_text = client.optimize_text_chunks(
        pdf_result['all_text'],
        optimization_type='general'
    )
    
    # Update result with optimized text
    pdf_result['all_text'] = optimized_text
    
    # Step 4: Export to Word
    print("[4/5] Exporting to Word...")
    word_gen = WordGenerator()
    word_gen.generate_from_pdf_result(
        pdf_result,
        include_metadata=True,
        include_tables=True,
        title='Optimized Document'
    )
    word_gen.save('output_optimized.docx')
    
    # Step 5: Export to Markdown
    print("[5/5] Exporting to Markdown...")
    md_gen = MarkdownGenerator()
    md_gen.generate_from_pdf_result(
        pdf_result,
        include_metadata=True,
        include_tables=True,
        title='Optimized Document'
    )
    md_gen.save('output_optimized.md')
    
    print("Complete workflow finished!")
    print(f"Processed {pdf_result['statistics']['total_pages']} pages")
    print(f"Found {pdf_result['statistics']['total_tables']} tables")


# Example 7: Error Handling
def example_error_handling():
    """Demonstrate error handling"""
    from utils import (
        validate_file_size,
        validate_file_format,
        ValidationError,
        PDFProcessingError,
        handle_exceptions
    )
    
    # Validate file size
    try:
        validate_file_size(100 * 1024 * 1024)  # 100MB
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        print(f"Details: {e.details}")
    
    # Validate file format
    try:
        validate_file_format('document.txt')
    except ValidationError as e:
        print(f"Format error: {e.message}")
    
    # Using decorator for exception handling
    @handle_exceptions(default_return="Error occurred", log_error=True)
    def risky_function():
        raise Exception("Something went wrong!")
    
    result = risky_function()
    print(f"Result: {result}")


# Example 8: Progress Tracking
def example_progress_tracking():
    """Demonstrate progress tracking"""
    from utils import ProgressTracker
    import time
    
    # Create progress tracker
    tracker = ProgressTracker(total_steps=10)
    
    for i in range(10):
        # Simulate work
        time.sleep(0.1)
        
        # Update progress
        tracker.update(message=f"Processing step {i+1}")
        
        # Check percentage
        print(f"Progress: {tracker.get_percentage():.1f}%")
    
    # Check if complete
    if tracker.is_complete():
        print("All steps completed!")


# Example 9: Batch Processing
def example_batch_processing():
    """Process multiple PDFs in batch"""
    from pdf_parser import PDFParser
    from text_preprocessor import TextPreprocessor
    from output_generator import WordGenerator
    from pathlib import Path
    
    pdf_files = list(Path('pdfs').glob('*.pdf'))
    
    for pdf_path in pdf_files:
        print(f"Processing {pdf_path.name}...")
        
        try:
            # Parse
            parser = PDFParser(str(pdf_path))
            result = parser.parse()
            
            # Preprocess
            preprocessor = TextPreprocessor()
            result = preprocessor.preprocess_pdf_result(result)
            
            # Export
            word_gen = WordGenerator()
            word_gen.generate_from_pdf_result(result)
            output_name = f"output_{pdf_path.stem}.docx"
            word_gen.save(output_name)
            
            print(f"✓ Saved {output_name}")
            
        except Exception as e:
            print(f"✗ Error processing {pdf_path.name}: {e}")


# Example 10: Custom Configuration
def example_custom_configuration():
    """Use custom configuration"""
    from config import Config
    
    # Modify configuration
    Config.MAX_FILE_SIZE_MB = 100
    Config.CHUNK_SIZE = 2000
    Config.MAX_RETRIES = 5
    Config.TIMEOUT = 60
    
    print(f"Max file size: {Config.MAX_FILE_SIZE_MB}MB")
    print(f"Chunk size: {Config.CHUNK_SIZE} characters")
    print(f"Max retries: {Config.MAX_RETRIES}")
    print(f"Timeout: {Config.TIMEOUT}s")


if __name__ == "__main__":
    print("PDF2Text AI - Usage Examples")
    print("=" * 60)
    print()
    print("This file contains 10 usage examples.")
    print("Uncomment the example you want to run.")
    print()
    
    # Uncomment to run examples:
    # example_pdf_parsing()
    # example_text_preprocessing()
    # example_deepseek_optimization()
    # example_word_export()
    # example_markdown_export()
    # example_complete_workflow()
    # example_error_handling()
    # example_progress_tracking()
    # example_batch_processing()
    # example_custom_configuration()
