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
from pathlib import Path

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


# Provider-specific models
PROVIDER_MODELS = {
    LLMProvider.GROQ: "llama-3.3-70b-versatile",
    LLMProvider.OPENAI: "gpt-4o",
    LLMProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
    LLMProvider.OLLAMA: "llama3",
}

# Fallback models for specific providers (Micro-Failover)
PROVIDER_FALLBACKS = {
    LLMProvider.GROQ: ["llama3-70b-8192", "mixtral-8x7b-32768"],
}


from .managed_pool import ManagedCreditPool

class LLMClient:
    """
    Unified client for LLM interactions.
    V1: Stable single-key mode.
    V2 (Next Week): Managed Credit Pool activation.
    V3 (Neural Link): Local Ollama Support.
    """
    
    def __init__(self, preferred_provider: Optional[str] = None):
        self.provider: Optional[LLMProvider] = None
        self.client = None
        self.async_client = None
        self.model: Optional[str] = None
        self.pool: Optional[ManagedCreditPool] = None
        
        self._load_dotenv()
        
        if preferred_provider:
            self._init_provider(preferred_provider)
        else:
            self._auto_detect()
            
        if not self.client:
            logger.warning("⚠️ No LLM API key found and Ollama not detected. Expert agents will not function.")
            
    def _init_provider(self, provider_name: str) -> bool:
        # Initialize Pool first
        try:
            self.pool = ManagedCreditPool(provider=provider_name)
        except Exception:
            self.pool = None

        try:
            # [OLLAMA] Special handling for local provider (No Key Needed)
            # [OLLAMA] Special handling for local provider (No Key Needed)
            if provider_name == "ollama":
                # AIRGAP TIER CHECK
                # We must query the DB to verify entitlement
                from side.storage.simple_db import SimplifiedDatabase
                db = SimplifiedDatabase()
                profile = db.get_profile(db.get_project_id("."))
                tier = profile.get("tier", "trial") if profile else "trial"
                
                # Only 'hitech' or 'enterprise' allowed
                if tier not in ["hitech", "enterprise"]:
                    logger.warning("🚫 [AIRGAP BLOCKED]: Ollama requires 'High Tech' tier. Falling back to Cloud.")
                    return False
                    
                from openai import OpenAI, AsyncOpenAI
                # Ollama is OpenAI-compatible!
                self.client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
                self.async_client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
                self.provider = LLMProvider.OLLAMA
                self.model = PROVIDER_MODELS[LLMProvider.OLLAMA]
                logger.info(f"✅ LLM: Neural Link (Ollama/{self.model}) [AIRGAP ACTIVE]")
                return True

            api_key = os.getenv(f"{provider_name.upper()}_API_KEY")
            # If no single key, check if pool has keys (Side Proxy Mode)
            if not api_key and self.pool and self.pool.is_healthy:
                api_key = self.pool.get_next_key()
                logger.info(f"Using Managed Pool Key for {provider_name}")

            if not api_key:
                return False
            
            # 3. Instantiate Provider
            if provider_name == "groq":
                from groq import Groq, AsyncGroq
                self.client = Groq(api_key=api_key)
                self.async_client = AsyncGroq(api_key=api_key)
            elif provider_name == "openai":
                from openai import OpenAI, AsyncOpenAI
                self.client = OpenAI(api_key=api_key)
                self.async_client = AsyncOpenAI(api_key=api_key)
            elif provider_name == "anthropic":
                from anthropic import Anthropic, AsyncAnthropic
                self.client = Anthropic(api_key=api_key)
                self.async_client = AsyncAnthropic(api_key=api_key)
            
            self.provider = LLMProvider(provider_name)
            self.model = PROVIDER_MODELS[self.provider]
            logger.info(f"✅ LLM: {provider_name.upper()} ({self.model})")
            return True
                
        except Exception as e:
            logger.debug(f"Provider {provider_name} init failed: {e}")
        return False

    def _load_dotenv(self):
        this_file = Path(__file__).resolve()
        backend_dir = this_file.parent.parent.parent.parent
        project_root = backend_dir.parent
        
        possible_paths = [
            backend_dir / ".env",
            project_root / ".env",
            Path.cwd() / ".env",
        ]
        
        ALLOWED_KEYS = ["SIDE_API_KEY", "SIDE_PROJECT_ID", "GROQ_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
        
        for env_path in possible_paths:
            if env_path.exists():
                try:
                    with open(env_path) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                if key.strip() in ALLOWED_KEYS:
                                     k = key.strip()
                                     v = value.strip().strip('"').strip("'")
                                     if k not in os.environ:
                                         os.environ[k] = v
                    break
                except Exception:
                    pass

    def _auto_detect(self):
        # [Sovereign Choice Strategy]
        from side.storage.simple_db import SimplifiedDatabase
        db = SimplifiedDatabase()
        project_id = db.get_project_id(".")
        profile = db.get_profile(project_id)
        tier = profile.get("tier", "trial") if profile else "trial"
        
        # 1. Global Airgap Check (The Master Switch)
        airgap = db.get_setting("airgap_enabled", "false") == "true"
        
        if airgap:
            logger.info("🛡️ [AIRGAP MODE]: Total isolation active. Enforcing local inference.")
            if self._init_provider("ollama"):
                return
            else:
                logger.critical("🚨 [AIRGAP FAILURE]: Airgap enabled but Ollama not available! System locked for privacy.")
                self.client = None
                return

        # 2. Tier-Based Default Routing
        # High Tech defaults to Local (Sovereign)
        # Others default to Cloud
        if tier == "hitech":
            logger.info(f"🏛️ [NEURAL ROUTING]: High Tech detected. Prioritizing Sovereign (Ollama).")
            if self._init_provider("ollama"):
                return
            logger.warning("⚠️ Sovereign Node unavailable. Sliding into Cloud Failover...")
        else:
            logger.info(f"🚀 [NEURAL ROUTING]: {tier.capitalize()} Tier detected. Prioritizing Cloud Performance.")

        # 3. Cloud Chain
        for provider in ["groq", "openai", "anthropic"]:
            if self._init_provider(provider):
                return
                
        # 4. Final Fallback to Ollama (if not already used)
        if tier != "hitech" and self._init_provider("ollama"):
            return
                
    def _init_provider_cloud(self, provider_name: str) -> bool: # Renamed older method to avoid conflict if I messed up replacement logic, but actually I am replacing the method body of _init_provider so I should correct myself. 
        # Wait, I am replacing the whole chunks. 
        # The logic in replacement chunk above handles both Ollama and Cloud.
        # But wait, looking at my replacement chunk, I included `_init_provider` implementation.
        # I need to be careful not to duplicate generic `_init_provider`.
        # The `replace_file_content` replaces a contiguous block. 
        # I see the target block starts at `GROQ = ...` (line 21) and ends at line 150 `return False`.
        # This covers the Enum, PROVIDER_MODELS, class def, __init__, _init_provider, _load_dotenv, _auto_detect, and the START of the second `_init_provider` (which is a duplicate in the original file?).
        # Ah, in the original file view, lines 62-81 are `_init_provider`, and 115-150 are ALSO `_init_provider`?
        # Let me re-read the original file.
        # Lines 62-81: `def _init_provider(self, provider_name: str) -> bool:` ... `logger.debug...` `return False`.
        # Lines 115-150: `def _init_provider(self, provider_name: str) -> bool:` ... logic for groq/openai/anthropic.
        # Yes, the original file has TWO `_init_provider` methods! The python class will uses the LAST one defined.
        # The first one (lines 62-81) seems to handle Pool logic but returns False at the end mostly? Or attempts to find key. 
        # The second one (lines 115-150) handles the actual client initialization.
        # My replacement supersedes BOTH if I capture the range correctly.
        # My replacement content defines a SINGLE `_init_provider` that handles Pool logic AND Client Init (including Ollama).
        # So I am cleaning up the duplicate method as well. Excellent.
        pass

    def is_available(self) -> bool:
        """Check if LLM is configured and available."""
        return self.client is not None

    def complete(self, messages, system_prompt, temperature=0.0, max_tokens=4096, model_override=None):
        try:
            actual_model = model_override or self.model
            
            if self.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model=actual_model, max_tokens=max_tokens, temperature=temperature,
                    system=system_prompt, messages=messages
                )
                return response.content[0].text
            else:
                all_messages = [{"role": "system", "content": system_prompt}] + messages
                response = self.client.chat.completions.create(
                    model=actual_model, messages=all_messages,
                    temperature=temperature, max_tokens=max_tokens,
                )
                return response.choices[0].message.content
        except Exception as e:
            return self._handle_error_sync(e, messages, system_prompt, temperature, max_tokens, model_override)

    def _handle_error_sync(self, e, messages, system_prompt, temperature, max_tokens, model_override):
        """Sync version of error handling (Basic)."""
        logger.error(f"❌ {self.provider.value} Sync Error: {e}")
        raise e

    async def complete_async(self, messages, system_prompt, temperature=0.0, max_tokens=4096, model_override=None):
        """
        Execute completion with Managed Credit Pool rotation and Circuit Breaking.
        """
        if not self.client:
            raise RuntimeError("LLM Client not initialized.")

        actual_model = model_override or self.model
        
        # [Phase 3] Managed Credit Pool Logic
        current_api_key = None
        if self.pool and self.pool.is_healthy:
            current_api_key = self.pool.get_next_key()
            if current_api_key:
                # Dynamically update the client's key for this request
                # Note: This is client-specific. For Groq/OpenAI, we might need to re-instantiate or set .api_key
                if self.provider == LLMProvider.GROQ:
                    self.async_client.api_key = current_api_key
                elif self.provider == LLMProvider.OPENAI:
                    self.async_client.api_key = current_api_key
                elif self.provider == LLMProvider.ANTHROPIC:
                    self.async_client.api_key = current_api_key
        
        try:
            if self.provider == LLMProvider.ANTHROPIC:
                response = await self.async_client.messages.create(
                    model=actual_model, max_tokens=max_tokens, temperature=temperature,
                    system=system_prompt, messages=messages
                )
                return response.content[0].text
            else:
                all_messages = [{"role": "system", "content": system_prompt}] + messages
                response = await self.async_client.chat.completions.create(
                    model=actual_model, messages=all_messages,
                    temperature=temperature, max_tokens=max_tokens,
                )
                return response.choices[0].message.content
                
        except Exception as e:
            error_str = str(e).lower()
            
            # --- SMART ERROR CLASSIFICATION ---
            if any(x in error_str for x in ["401", "unauthorized", "invalid api key", "authentication"]):
                logger.error(f"🚫 [AUTH ERROR]: Key for {self.provider.value} is invalid.")
                if self.pool and current_api_key:
                    self.pool.mark_as_cooling(current_api_key, duration=3600*24)
                return await self.complete_async(messages, system_prompt, temperature, max_tokens, model_override)

            if any(x in error_str for x in ["429", "rate limit", "quota", "too many requests"]):
                logger.warning(f"⚠️ [RATE LIMIT]: {self.provider.value} key exhausted. Rotating...")
                if self.pool and current_api_key:
                    self.pool.mark_as_cooling(current_api_key)
                if self.pool and not self.pool.is_healthy:
                    logger.warning(f"🚨 [POOL EXHAUSTED]: No healthy keys for {self.provider.value}.")
                else:
                    return await self.complete_async(messages, system_prompt, temperature, max_tokens, model_override)
            
            if any(x in error_str for x in ["500", "503", "502", "timeout", "connection", "deadline"]):
                logger.error(f"🔥 [PROVIDER INSTABILITY]: {self.provider.value}: {e}")
                if not model_override and self.provider in PROVIDER_FALLBACKS:
                    next_model = self._get_next_fallback_model(actual_model)
                    if next_model:
                        logger.warning(f"🛡️ [MICRO-FAILOVER]: {actual_model} -> {next_model}")
                        return await self.complete_async(messages, system_prompt, temperature, max_tokens, model_override=next_model)
                
            # --- MACRO-FAILOVER ---
            fallback_chain = {
               LLMProvider.GROQ: LLMProvider.OPENAI,
               LLMProvider.OPENAI: LLMProvider.ANTHROPIC,
               LLMProvider.OLLAMA: LLMProvider.GROQ
            }
            
            from side.storage.simple_db import SimplifiedDatabase
            db = SimplifiedDatabase()
            if db.get_setting("airgap_enabled", "false") == "true":
                logger.critical(f"❌ [AIRGAP ENFORCED]: Local failure but Cloud switch blocked.")
                raise e

            next_provider = fallback_chain.get(self.provider)
            if next_provider:
                logger.warning(f"🛡️ [NEURAL FAILOVER]: {self.provider.value} -> {next_provider.value}. Fluid Transition.")
                if self._init_provider(next_provider.value):
                    return await self.complete_async(messages, system_prompt, temperature, max_tokens, model_override)
            
            logger.critical(f"❌ [NEURAL COLLAPSE]: Total Provider Failure. {e}")
            raise e

    def _get_next_fallback_model(self, current_model: str) -> Optional[str]:
        """Circular model fallback within a provider."""
        fallbacks = PROVIDER_FALLBACKS.get(self.provider, [])
        if not fallbacks: return None
        if current_model == self.model: return fallbacks[0]
        try:
            idx = fallbacks.index(current_model)
            if idx + 1 < len(fallbacks): return fallbacks[idx + 1]
        except ValueError: pass
        return None
