import random
from typing import Dict, Any, List
import asyncio
import os
import aiohttp

# Import logging
from .logging_config import get_logger

# Import dotenv to load environment variables
from dotenv import load_dotenv

# Load environment variables from .env file
# Get the directory of the current file (ai_service.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up two levels to reach the backend directory, then to .env
env_path = os.path.join(current_dir, '..', '..', '.env')
load_dotenv(env_path)

logger = get_logger(__name__)

# Llama imports (optional - for local inference)
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    LLAMA_LOCAL_AVAILABLE = True
except ImportError:
    LLAMA_LOCAL_AVAILABLE = False
    logger.warning("Local Llama dependencies not installed. Will use API-based approach if available.")

# Global variables for Llama model (loaded once)
llama_tokenizer = None
llama_model = None
llama_loaded = False

# API keys from environment variables
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
together_api_key = os.getenv("TOGETHER_API_KEY")
hugging_face_api_key = os.getenv("HUGGING_FACE_API_KEY")

# Debug: Log the loaded API keys (without revealing the actual values)
logger.info(f"OpenRouter API Key loaded: {'Yes' if openrouter_api_key else 'No'}")
logger.info(f"Together API Key loaded: {'Yes' if together_api_key else 'No'}")
logger.info(f"Hugging Face API Key loaded: {'Yes' if hugging_face_api_key else 'No'}")


class AIService:
    def __init__(self):
        """
        Initialize the AI Service.
        """
        pass
    
    async def initialize_llama_model(self):
        """
        Initialize the Llama model (run once at startup)
        """
        global llama_tokenizer, llama_model, llama_loaded
        
        # Always skip model loading for testing purposes
        logger.info("Skipping Llama model loading for testing")
        return False

    async def generate_linkedin_post(self, topic: str, tone: str = "professional", audience: str = None, reference_url: str = None) -> str:
        """
        Generate LinkedIn post content using Llama model (either API or local).
        
        Args:
            topic: Topic for the post
            tone: Tone of the post (professional, casual, inspirational, etc.)
            audience: Target audience for the post
            url: Reference URL for content inspiration
        
        Returns:
            Generated post content as string
        """
        
        global openrouter_api_key, together_api_key, hugging_face_api_key, llama_loaded
        
        # Try OpenRouter API first if API key is available
        if openrouter_api_key:
            try:
                # Add timeout for API-based generation
                return await asyncio.wait_for(self._generate_with_openrouter(topic, tone, audience), timeout=30.0)
            except asyncio.TimeoutError:
                logger.warning("OpenRouter API generation timed out")
            except Exception as e:
                logger.error(f"OpenRouter API generation failed: {e}")
        
        # Try Together AI API if API key is available
        if together_api_key:
            try:
                # Add timeout for API-based generation
                return await asyncio.wait_for(self._generate_with_together_ai(topic, tone, audience), timeout=30.0)
            except asyncio.TimeoutError:
                logger.warning("Together AI API generation timed out")
            except Exception as e:
                logger.error(f"Together AI API generation failed: {e}")
        
        # Try Hugging Face API if API key is available
        if hugging_face_api_key:
            try:
                # Add timeout for API-based generation
                return await asyncio.wait_for(self._generate_with_hugging_face(topic, tone, audience), timeout=30.0)
            except asyncio.TimeoutError:
                logger.warning("Hugging Face API generation timed out")
            except Exception as e:
                logger.error(f"Hugging Face API generation failed: {e}")
        
        # Try local model if available
        if LLAMA_LOCAL_AVAILABLE and llama_loaded:
            try:
                # Add timeout for local model generation
                return await asyncio.wait_for(self._generate_with_local_model(topic, tone, audience), timeout=20.0)
            except asyncio.TimeoutError:
                logger.warning("Local model generation timed out")
            except Exception as e:
                logger.error(f"Local model generation failed: {e}")
        
        # Fallback to sample posts
        return self._get_sample_post(topic, tone, audience)

    async def _generate_with_openrouter(self, topic: str, tone: str, audience: str = None, reference_url: str = None) -> str:
        """
        Generate content using OpenRouter API.
        """
        global openrouter_api_key
        
        # Create prompt
        prompt = self._create_llama_prompt(topic, tone, audience, reference_url)
        
        # OpenRouter API endpoint
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "HTTP-Referer": "http://localhost:8080",  # Optional, for including your app on openrouter.ai rankings
            "X-Title": "LinkedIn AutoMarketer AI",  # Optional, shown in rankings
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mistralai/mistral-7b-instruct:free",  # Using free model
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    generated_text = result['choices'][0]['message']['content']
                    # Clean up the post content
                    return self._clean_generated_post(generated_text)
                else:
                    logger.error(f"OpenRouter API error: {response.status}")
                    raise Exception(f"OpenRouter API error: {response.status}")

    async def _generate_with_together_ai(self, topic: str, tone: str, audience: str = None, reference_url: str = None) -> str:
        """
        Generate content using Together AI API.
        """
        global together_api_key
        
        # Create prompt
        prompt = self._create_llama_prompt(topic, tone, audience, reference_url)
        
        # Together AI API endpoint
        api_url = "https://api.together.xyz/inference"
        
        headers = {
            "Authorization": f"Bearer {together_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",  # Using Mixtral model
            "prompt": prompt,
            "temperature": 0.7,
            "max_tokens": 500,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    generated_text = result['output']['choices'][0]['text']
                    # Clean up the post content
                    return self._clean_generated_post(generated_text)
                else:
                    logger.error(f"Together AI API error: {response.status}")
                    raise Exception(f"Together AI API error: {response.status}")

    async def _generate_with_hugging_face(self, topic: str, tone: str, audience: str = None, reference_url: str = None) -> str:
        """
        Generate content using Hugging Face API.
        """
        global hugging_face_api_key
        
        # Create prompt
        prompt = self._create_llama_prompt(topic, tone, audience, reference_url)
        
        # Hugging Face API endpoint for a popular model
        model = "mistralai/Mistral-7B-v0.1"
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        headers = {
            "Authorization": f"Bearer {hugging_face_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "inputs": prompt,
            "parameters": {
                "temperature": 0.7,
                "max_new_tokens": 500,
                "return_full_text": False
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    generated_text = result[0]['generated_text']
                    # Clean up the post content
                    return self._clean_generated_post(generated_text)
                else:
                    logger.error(f"Hugging Face API error: {response.status}")
                    raise Exception(f"Hugging Face API error: {response.status}")

    async def _generate_with_local_model(self, topic: str, tone: str, audience: str = None, reference_url: str = None) -> str:
        """
        Generate content using local Llama model.
        """
        global llama_tokenizer, llama_model
        
        # Create prompt for Llama model
        prompt = self._create_llama_prompt(topic, tone, audience, reference_url)
        
        # Tokenize input
        inputs = llama_tokenizer.encode(prompt, return_tensors="pt")
        
        # Move inputs to GPU if available
        if torch.cuda.is_available():
            inputs = inputs.to("cuda")
        
        # Generate text with optimized parameters for speed
        with torch.no_grad():
            outputs = llama_model.generate(
                inputs,
                max_length=200,  # Reduced length for faster generation
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=llama_tokenizer.eos_token_id,
                max_time=10.0  # Limit generation time to 10 seconds
            )
        
        # Decode generated text
        generated_text = llama_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the post content (remove the prompt)
        post_content = generated_text[len(prompt):].strip()
        
        # Ensure we have a reasonable length post
        if len(post_content) < 50:
            return self._get_sample_post(topic, tone, audience)
        
        # Clean up the post content
        post_content = self._clean_generated_post(post_content)
        
        return post_content

    def _create_llama_prompt(self, topic: str, tone: str, audience: str = None, reference_url: str = None) -> str:
        """
        Create a prompt for the Llama model to generate a LinkedIn post in proper format.
        
        Args:
            topic: Topic for the post
            tone: Tone of the post
            audience: Target audience
            reference_url: Reference URL for content inspiration
            
        Returns:
            Formatted prompt string
        """
        tone_descriptions = {
            "professional": "a professional tone suitable for business networking",
            "casual": "a friendly, conversational tone",
            "inspirational": "an uplifting and motivational tone",
            "educational": "an informative and educational tone"
        }
        
        audience_text = f" for {audience}" if audience else ""
        tone_text = tone_descriptions.get(tone, tone_descriptions["professional"])
        
        # Build the base prompt
        prompt_parts = [f"Write a LinkedIn post{audience_text} in {tone_text} about \"{topic}\"."]
        
        # Add URL reference if provided
        if reference_url:
            prompt_parts.append(f"Consider the content or insights from this reference URL: {reference_url}")
        
        prompt_parts.extend([
            "\nIMPORTANT: Respond ONLY with the LinkedIn post content. DO NOT include any introductory text, explanations, or formatting instructions. Start directly with the post content.",
            "\nFormat the post with the following structure:",
            "1. An engaging opening line with an emoji",
            "2. 2-3 paragraphs of valuable content with clear line breaks between paragraphs",
            "3. A thought-provoking question to encourage engagement",
            "4. 3-5 relevant hashtags at the end",
            "\nGuidelines:",
            "- Use clear paragraph breaks (double newlines) for readability",
            "- Include emojis sparingly for visual appeal",
            "- Make it actionable and valuable for professionals",
            "- End with a question that invites comments",
            "- Use 3-5 relevant hashtags",
            "- DO NOT include any text before or after the post content",
            "\nExample format:",
            "🚀 Opening line about the topic",
            "\nMain content paragraph 1 explaining the value...",
            "\nMain content paragraph 2 with examples or insights...",
            "\nThought-provoking question to encourage discussion?",
            "\n#Hashtag1 #Hashtag2 #Hashtag3"
        ])
        
        prompt = "\n".join(prompt_parts)
        
        return prompt

    def _clean_generated_post(self, post_content: str) -> str:
        """
        Clean up the generated post content to ensure proper LinkedIn formatting.
        Removes any explanatory text and returns only the post content.
        
        Args:
            post_content: Raw generated content
            
        Returns:
            Cleaned post content in proper LinkedIn format
        """
        # First, try to extract content between separators if they exist
        if '---' in post_content:
            parts = post_content.split('---')
            if len(parts) > 1:
                # Take the last part after the separator
                post_content = parts[-1].strip()
        
        # Split into lines
        lines = post_content.split('\n')
        
        # Find the start of actual post content by skipping introductory lines
        start_index = 0
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            # Skip lines that look like introductions
            if (line_lower.startswith('here') and 'post' in line_lower) or \
               (line_lower.startswith('below') and 'post' in line_lower) or \
               (line_lower.startswith('here') and 'linkedin' in line_lower) or \
               ('polished' in line_lower and 'post' in line_lower):
                start_index = i + 1
            else:
                # Once we find a line that doesn't look like an introduction, break
                break
        
        # Extract the actual post content
        actual_content_lines = lines[start_index:]
        cleaned_lines = []
        
        # Process lines to ensure proper spacing and formatting
        for i, line in enumerate(actual_content_lines):
            stripped_line = line.rstrip()  # Keep trailing spaces for formatting
            if stripped_line:
                # Add line with proper formatting
                cleaned_lines.append(stripped_line)
            elif cleaned_lines and i < len(actual_content_lines) - 1:
                # Only add empty lines if not at the beginning or end
                # And avoid multiple consecutive empty lines
                if cleaned_lines[-1] != '':
                    cleaned_lines.append('')
        
        # Join lines back together
        cleaned_post = '\n'.join(cleaned_lines)
        
        # Ensure the post ends with a newline for proper formatting
        if cleaned_post and not cleaned_post.endswith('\n'):
            cleaned_post += '\n'
            
        return cleaned_post

    def _get_sample_post(self, topic: str, tone: str, audience: str = None) -> str:
        """
        Generate a sample LinkedIn post when AI generation fails.
        
        Args:
            topic: Topic for the post
            tone: Tone of the post
            audience: Target audience
            
        Returns:
            Sample post content
        """
        sample_posts = [
            f"""🚀 The Future of {topic.title()} is Here!

Working with {audience or 'professionals'} has never been more exciting. Today's innovations in {topic} are reshaping how we approach challenges and create opportunities.

The power of {tone} communication can make all the difference in connecting with your audience.

What's your biggest challenge with {topic}? Let's discuss in the comments below! 👇

#{''.join(topic.split()).capitalize()} #{''.join((audience or 'Tech').split()).capitalize()} #Innovation""",
            
            f"""💡 New Insights on {topic.title()}

As {audience or 'professionals'}, we're constantly seeking ways to improve our skills and stay ahead. {topic.capitalize()} offers tremendous potential for growth and development.

Embracing a {tone} approach to {topic} can transform how we work and collaborate.

How are you incorporating {topic} into your workflow? Share your experiences below! 💬

#{''.join(topic.split()).capitalize()} #{'Professional' if tone == 'professional' else tone.capitalize()} #Growth""",
            
            f"""🌟 Transforming {topic.title()} Through Innovation

The landscape of {topic} continues to evolve rapidly. For {audience or 'industry professionals'}, staying informed and adaptable is crucial.

A {tone} perspective on {topic} reveals new opportunities for impact and success.

What trends in {topic} are you most excited about? I'd love to hear your thoughts! 🤔

#{''.join(topic.split()).capitalize()} #{''.join((audience or 'Business').split()).capitalize()} #Future""",
        ]
        
        # Return a random sample post
        return random.choice(sample_posts)

# Global instance
ai_service = AIService()