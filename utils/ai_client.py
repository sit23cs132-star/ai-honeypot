"""AI client interface for multiple providers."""
import json
from typing import Dict, Any, List, Optional
from config import config


class AIClient:
    """Unified interface for AI providers (OpenAI and Anthropic)."""
    
    def __init__(self):
        self.provider = config.AI_PROVIDER
        
        if self.provider == "openai":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
            self.model = config.OPENAI_MODEL
        elif self.provider == "anthropic":
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
            self.model = config.ANTHROPIC_MODEL
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
        json_mode: bool = False
    ) -> str:
        """
        Generate a completion from the AI model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            json_mode: Whether to request JSON output
            
        Returns:
            Generated text response
        """
        try:
            if self.provider == "openai":
                response_format = {"type": "json_object"} if json_mode else None
                
                completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format
                )
                return completion.choices[0].message.content
                
            elif self.provider == "anthropic":
                # Convert messages format for Anthropic
                system_message = None
                converted_messages = []
                
                for msg in messages:
                    if msg["role"] == "system":
                        system_message = msg["content"]
                    else:
                        converted_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                
                kwargs = {
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": converted_messages
                }
                
                if system_message:
                    kwargs["system"] = system_message
                
                response = await self.client.messages.create(**kwargs)
                return response.content[0].text
                
        except Exception as e:
            raise Exception(f"AI generation error: {str(e)}")
    
    async def generate_json_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.5,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Generate a JSON completion from the AI model.
        
        Returns:
            Parsed JSON response as dictionary
        """
        response = await self.generate_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=(self.provider == "openai")
        )
        
        try:
            # Try to parse as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # If not valid JSON, try to extract JSON from markdown code blocks
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            else:
                # Return a default structure
                return {"error": "Failed to parse JSON", "raw_response": response}
