"""
Multi-Provider LLM Client.

Supports:
- Groq (Llama 3)
- OpenAI (GPT-4)
- Anthropic (Claude)

Auto-detects based on available environment variables.
"""
import os
import logging
from typing import List, Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


# Provider-specific models
PROVIDER_MODELS = {
    LLMProvider.GROQ: "llama-3.3-70b-versatile",
    LLMProvider.OPENAI: "gpt-4o",
    LLMProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
}


class LLMClient:
    """
    Unified client for LLM interactions.
    Supports multiple providers with auto-detection.
    """
    
    def __init__(self, preferred_provider: Optional[str] = None):
        """
        Initialize the LLM client.
        
        Args:
            preferred_provider: Force a specific provider ("groq", "openai", "anthropic").
                               If None, auto-detects based on available env vars.
        """
        self.provider: Optional[LLMProvider] = None
        self.client = None
        self.async_client = None
        self.model: Optional[str] = None
        
        # Load .env if available (ensures keys are present even if not in environment yet)
        self._load_dotenv()
        
        # Try to initialize in priority order (or use preferred)
        if preferred_provider:
            self._init_provider(preferred_provider)
        else:
            self._auto_detect()
            
        if not self.client:
            logger.warning("⚠️ No LLM API key found. Expert agents will not function.")
            logger.warning("   Set one of: GROQ_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY")

    def _load_dotenv(self):
        """Load environment variables from .env file if it exists."""
        from pathlib import Path
        
        # Find backend root (where .env typically lives)
        this_file = Path(__file__).resolve()
        # side/llm/client.py -> side/llm/ -> side/ -> src/ -> backend/
        backend_dir = this_file.parent.parent.parent.parent
        project_root = backend_dir.parent
        
        possible_paths = [
            backend_dir / ".env",
            project_root / ".env",
            Path.cwd() / ".env",
        ]
        
        for env_path in possible_paths:
            if env_path.exists():
                try:
                    with open(env_path) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"').strip("'")
                                # Use same logic as ArchitectureAdvisor
                                if key and value and (key not in os.environ or not os.environ.get(key)):
                                    os.environ[key] = value
                    break
                except Exception:
                    pass

            
    def _auto_detect(self):
        """Try providers in order until one works."""
        # Priority: Groq (fast) > OpenAI (popular) > Anthropic (smart)
        for provider in ["groq", "openai", "anthropic"]:
            if self._init_provider(provider):
                break
                
    def _init_provider(self, provider_name: str) -> bool:
        """Initialize a specific provider. Returns True on success."""
        try:
            if provider_name == "groq":
                api_key = os.getenv("GROQ_API_KEY")
                if api_key:
                    from groq import Groq, AsyncGroq
                    self.client = Groq(api_key=api_key)
                    self.async_client = AsyncGroq(api_key=api_key)
                    self.provider = LLMProvider.GROQ
                    self.model = PROVIDER_MODELS[LLMProvider.GROQ]
                    logger.info(f"✅ LLM: Groq ({self.model})")
                    return True
                    
            elif provider_name == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    from openai import OpenAI, AsyncOpenAI
                    self.client = OpenAI(api_key=api_key)
                    self.async_client = AsyncOpenAI(api_key=api_key)
                    self.provider = LLMProvider.OPENAI
                    self.model = PROVIDER_MODELS[LLMProvider.OPENAI]
                    logger.info(f"✅ LLM: OpenAI ({self.model})")
                    return True
                    
            elif provider_name == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    from anthropic import Anthropic, AsyncAnthropic
                    self.client = Anthropic(api_key=api_key)
                    self.async_client = AsyncAnthropic(api_key=api_key)
                    self.provider = LLMProvider.ANTHROPIC
                    self.model = PROVIDER_MODELS[LLMProvider.ANTHROPIC]
                    logger.info(f"✅ LLM: Anthropic ({self.model})")
                    return True
                    
        except ImportError as e:
            logger.debug(f"Provider {provider_name} not installed: {e}")
        except Exception as e:
            logger.debug(f"Provider {provider_name} init failed: {e}")
            
        return False
    
    def is_available(self) -> bool:
        """Check if LLM is configured and available."""
        return self.client is not None
        
    def complete(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096
    ) -> str:
        """
        Get a completion from the LLM.
        Unified interface across all providers.
        """
        if not self.client:
            raise RuntimeError("LLM Client not initialized. Missing API Key.")
            
        # Safety: Truncate extremely large prompts
        if len(system_prompt) + sum(len(m['content']) for m in messages) > 40000:
            logger.warning("Extremely large prompt detected. Truncating for economy.")
            # Simple truncation of the last message content if needed
            if messages:
                last_msg = messages[-1]
                last_msg['content'] = last_msg['content'][:30000] + "\n[CONTEXT TRUNCATED]"
        
        logger.info(f"🧠 Invoking {self.provider.value}/{self.model}...")
        
        try:
            if self.provider == LLMProvider.ANTHROPIC:
                # Anthropic has different API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=messages
                )
                return response.content[0].text
                
            else:
                # OpenAI and Groq share the same API format
                all_messages = [{"role": "system", "content": system_prompt}] + messages
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=all_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"❌ {self.provider.value} API Error: {e}")
            raise

    async def complete_async(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        model_override: Optional[str] = None
    ) -> str:
        """
        Get an asynchronous completion from the LLM.
        """
        if not self.async_client:
            raise RuntimeError("Async LLM Client not initialized.")
            
        # Safety: Truncate extremely large prompts
        if len(system_prompt) + sum(len(m['content']) for m in messages) > 40000:
            logger.warning("Extremely large prompt detected (Async). Truncating for economy.")
            if messages:
                last_msg = messages[-1]
                last_msg['content'] = last_msg['content'][:30000] + "\n[CONTEXT TRUNCATED]"

        actual_model = model_override or self.model
        logger.info(f"🧠 Invoking (Async) {self.provider.value}/{actual_model}...")
        
        try:
            if self.provider == LLMProvider.ANTHROPIC:
                response = await self.async_client.messages.create(
                    model=actual_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=messages
                )
                return response.content[0].text
            else:
                all_messages = [{"role": "system", "content": system_prompt}] + messages
                response = await self.async_client.chat.completions.create(
                    model=actual_model,
                    messages=all_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ {self.provider.value} Async API Error: {e}")
            raise
