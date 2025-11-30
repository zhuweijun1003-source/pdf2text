"""
DeepSeek API Integration Module
Provides AI-powered text optimization with error handling and retry logic
Supports grammar correction, semantic optimization, and logical refinement
"""
import time
import requests
from typing import List, Dict, Optional
from loguru import logger
from config import Config
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


class DeepSeekClient:
    """DeepSeek API client for text optimization"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize DeepSeek API client
        
        Args:
            api_key: DeepSeek API key (uses config if not provided)
            base_url: API base URL (uses config if not provided)
        """
        self.api_key = api_key or Config.DEEPSEEK_API_KEY
        self.base_url = base_url or Config.DEEPSEEK_BASE_URL
        self.model = Config.DEEPSEEK_MODEL
        
        if not self.api_key:
            raise ValueError("DeepSeek API key is required")
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        logger.info("DeepSeek API client initialized")
    
    def _make_request(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> Optional[str]:
        """
        Make a request to DeepSeek Chat Completions API
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            API response text or None if failed
        """
        endpoint = f"{self.base_url}/chat/completions"
        
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'stream': False
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=Config.TIMEOUT
            )
            
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            raise
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                logger.warning("Rate limit exceeded")
                raise ValueError("API rate limit exceeded. Please try again later.")
            elif response.status_code == 401:
                logger.error("Invalid API key")
                raise ValueError("Invalid API key")
            else:
                logger.error(f"HTTP error: {e}")
                raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def _retry_request(
        self,
        messages: List[Dict[str, str]],
        max_retries: Optional[int] = None,
        **kwargs
    ) -> Optional[str]:
        """
        Make API request with retry logic
        
        Args:
            messages: List of message dictionaries
            max_retries: Maximum retry attempts
            **kwargs: Additional arguments for _make_request
            
        Returns:
            API response text or None
        """
        max_retries = max_retries or Config.MAX_RETRIES
        
        for attempt in range(max_retries):
            try:
                return self._make_request(messages, **kwargs)
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = Config.RETRY_DELAY * (attempt + 1)
                    logger.warning(f"Timeout, retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached due to timeout")
                    raise
                    
            except ValueError as e:
                # Don't retry for rate limit or auth errors
                if "rate limit" in str(e).lower() or "invalid" in str(e).lower():
                    raise
                
                if attempt < max_retries - 1:
                    wait_time = Config.RETRY_DELAY * (attempt + 1)
                    logger.warning(f"Error occurred, retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached")
                    raise
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = Config.RETRY_DELAY * (attempt + 1) * 2  # Exponential backoff
                    logger.warning(f"Unexpected error, retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries reached: {e}")
                    raise
        
        return None
    
    def optimize_text(
        self,
        text: str,
        optimization_type: str = 'general',
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Optimize text using DeepSeek API
        
        Args:
            text: Input text to optimize
            optimization_type: Type of optimization (general, grammar, semantic, terminology)
            custom_instructions: Custom optimization instructions
            
        Returns:
            Optimized text
        """
        if not text or not text.strip():
            return text
        
        # Build system prompt based on optimization type
        system_prompts = {
            'general': """You are an expert text editor. Improve the following text by:
1. Correcting grammar and spelling errors
2. Improving sentence structure and readability
3. Enhancing logical flow
4. Maintaining the original meaning and tone
Return only the improved text without explanations.""",
            
            'grammar': """You are a professional proofreader. Correct all grammar, spelling, and punctuation errors in the following text.
Maintain the original structure and meaning. Return only the corrected text.""",
            
            'semantic': """You are a content optimizer. Enhance the following text by:
1. Improving clarity and coherence
2. Strengthening logical connections
3. Refining word choices
4. Ensuring smooth transitions
Return only the optimized text.""",
            
            'terminology': """You are a terminology specialist. Ensure consistent use of technical terms and standardize terminology throughout the text.
Return only the text with unified terminology."""
        }
        
        system_prompt = system_prompts.get(optimization_type, system_prompts['general'])
        
        if custom_instructions:
            system_prompt += f"\n\nAdditional instructions: {custom_instructions}"
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': text}
        ]
        
        try:
            logger.info(f"Optimizing text (type: {optimization_type}, length: {len(text)} chars)")
            optimized = self._retry_request(messages)
            
            if optimized:
                logger.info(f"Text optimization complete (output length: {len(optimized)} chars)")
                return optimized
            else:
                logger.warning("Optimization failed, returning original text")
                return text
                
        except Exception as e:
            logger.error(f"Text optimization error: {e}")
            return text
    
    def summarize_text(
        self,
        text: str,
        length: str = 'medium',
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Generate a summary of the text using DeepSeek API
        
        Args:
            text: Input text to summarize
            length: Summary length (short, medium, long)
            custom_instructions: Custom summarization instructions
            
        Returns:
            Summary text
        """
        if not text or not text.strip():
            return text
        
        # Build system prompt based on summary length
        length_instructions = {
            'short': '请用100-200字概括以下文本的核心内容和要点。',
            'medium': '请用300-500字总结以下文本的主要内容、关键观点和重要细节。',
            'long': '请用500-800字详细总结以下文本的完整内容，包括主要观点、支撑论据和重要细节。'
        }
        
        system_prompt = f"""你是一个专业的文本摘要专家。{length_instructions.get(length, length_instructions['medium'])}

要求：
1. 保留关键信息和主要观点
2. 使用清晰简洁的语言
3. 保持逻辑连贯
4. 不添加原文中没有的信息
5. 使用中文输出

只返回摘要内容，不要添加任何解释或说明。"""
        
        if custom_instructions:
            system_prompt += f"\n\n补充要求: {custom_instructions}"
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': text}
        ]
        
        try:
            logger.info(f"Generating summary (length: {length}, input length: {len(text)} chars)")
            summary = self._retry_request(messages, max_tokens=2000)
            
            if summary:
                logger.info(f"Summary generation complete (output length: {len(summary)} chars)")
                return summary
            else:
                logger.warning("Summary generation failed, returning original text")
                return text
                
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return text
    
    def summarize_text_chunks(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        length: str = 'medium',
        custom_instructions: Optional[str] = None,
        max_workers: int = 3,
        progress_callback=None
    ) -> str:
        """
        Summarize long text by splitting into chunks and processing in parallel
        
        Args:
            text: Input text
            chunk_size: Size of each chunk (characters)
            length: Summary length
            custom_instructions: Custom instructions
            max_workers: Maximum parallel workers
            progress_callback: Callback for progress updates
            
        Returns:
            Summary text
        """
        chunk_size = chunk_size or Config.CHUNK_SIZE * 5  # Larger chunks for summarization
        
        if len(text) <= chunk_size:
            return self.summarize_text(text, length, custom_instructions)
        
        # Split text into chunks (by paragraphs to maintain context)
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            if current_size + para_size > chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        logger.info(f"Split text into {len(chunks)} chunks for summarization")
        
        # Summarize each chunk
        chunk_summaries = [''] * len(chunks)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(
                    self.summarize_text,
                    chunk,
                    'short' if len(chunks) > 1 else length,  # Use short summaries for multi-chunk
                    custom_instructions
                ): idx
                for idx, chunk in enumerate(chunks)
            }
            
            completed = 0
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    chunk_summaries[idx] = future.result()
                    completed += 1
                    
                    if progress_callback:
                        progress_callback(completed, len(chunks))
                        
                except Exception as e:
                    logger.error(f"Error summarizing chunk {idx}: {e}")
                    chunk_summaries[idx] = chunks[idx][:500] + "..."  # Use truncated original on error
        
        # Combine chunk summaries
        combined_summary = '\n\n'.join(chunk_summaries)
        
        # If we had multiple chunks, generate a final summary of the summaries
        if len(chunks) > 1 and len(combined_summary) > chunk_size:
            logger.info("Generating final summary from chunk summaries")
            final_summary = self.summarize_text(combined_summary, length, custom_instructions)
            return final_summary
        
        return combined_summary
    
    def optimize_table_content(self, table_data: List[List[str]]) -> List[List[str]]:
        """
        Optimize table cell contents
        
        Args:
            table_data: 2D list of table data
            
        Returns:
            Optimized table data
        """
        try:
            optimized_table = []
            
            for row in table_data:
                optimized_row = []
                for cell in row:
                    if cell and len(cell.strip()) > 10:  # Only optimize longer cells
                        optimized_cell = self.optimize_text(cell, optimization_type='grammar')
                        optimized_row.append(optimized_cell)
                    else:
                        optimized_row.append(cell)
                
                optimized_table.append(optimized_row)
            
            return optimized_table
            
        except Exception as e:
            logger.error(f"Error optimizing table: {e}")
            return table_data


def optimize_text_with_deepseek(
    text: str,
    api_key: Optional[str] = None,
    optimization_type: str = 'general',
    **kwargs
) -> str:
    """
    Convenience function to optimize text
    
    Args:
        text: Input text
        api_key: DeepSeek API key
        optimization_type: Type of optimization
        **kwargs: Additional arguments
        
    Returns:
        Optimized text
    """
    client = DeepSeekClient(api_key=api_key)
    return client.optimize_text(text, optimization_type=optimization_type, **kwargs)
