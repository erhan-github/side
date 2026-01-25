from typing import List, Dict, Any
import json
from side.intel.memory.persistence import MemoryPersistence
from side.llm.client import LLMClient
# from side.intelligence.graph_kernel import GraphKernel

class GraphKernel:
    def ingest_intent(self, *args, **kwargs):
        return "mock_uid"
    def link(self, *args, **kwargs):
        pass

class MemoryManager:
    """
    The brain of the File-Based Memory System.
    Orchestrates the 3-stage memory process:
    1. Save Resource (Conversation/Doc)
    2. Extract Items (Facts)
    3. Evolve Summaries (Categories)
    """

    def __init__(self, persistence: MemoryPersistence, llm_client: LLMClient, graph: GraphKernel = None):
        self.persistence = persistence
        self.llm = llm_client
        self.graph = graph or GraphKernel()

    async def memorize(self, user_id: str, content: str, meta: Dict[str, Any] = None, 
                       rationale: str = None, valid_until: str = None):
        """
        Main entry point. Save content and update the user's memory profile.
        """
        # 1. Save Resource (Source of Truth)
        resource_id = self.persistence.save_resource(user_id, content, meta)

        # 2. Extract Items (Atomic Facts)
        items = await self._extract_items(content)
        
        # 3. Batch updates by category
        updates_by_category = {}
        for item in items:
            category = await self._classify_item(item['content'])
            
            if category not in updates_by_category:
                updates_by_category[category] = []
            updates_by_category[category].append(item['content'])
            
            # Save item to inbox/log
            self.persistence.save_item(user_id, category, item['content'], resource_id, 
                                       rationale=rationale, valid_until=valid_until)
            
            # 🟢 PROACTIVE LOGIC: Ingest into Graph & Link to Focus Symbol
            intent_uid = self.graph.ingest_intent(
                f"{resource_id}_{category}", 
                item['content'], 
                {"category": category, "rationale": rationale}
            )
            
            # If meta contains a focus_symbol, link it
            if meta and "focus_symbol" in meta:
                # focus_symbol should be 'path/to/file.py:ClassName'
                symbol_uid = f"symbol:{meta['focus_symbol']}"
                self.graph.link(intent_uid, symbol_uid, "clarifies")

        # 4. Evolve Summaries & Update Index
        index_updates = {}
        for category, new_memories in updates_by_category.items():
            existing_summary = self.persistence.load_category(user_id, category)
            
            updated_summary = await self._evolve_summary(existing_summary, new_memories, category)
            
            self.persistence.save_category(user_id, category, updated_summary)
            
            # Generate search keywords for the new content
            keywords = await self._generate_keywords(category, updated_summary)
            index_updates[category] = keywords

        # 5. Persist Index
        if index_updates:
            current_index = self.persistence.load_index(user_id)
            current_index.update(index_updates)
            self.persistence.save_index(user_id, current_index)

    async def _extract_items(self, text: str) -> List[Dict[str, Any]]:
        """
        Use LLM to extract atomic facts from the conversation.
        """
        prompt = f"""Extract discrete facts from this conversation that are worth remembering for the long term.
Focus on:
- User preferences (tech stack, working style)
- Project details (names, architectures, rules)
- Explicit instructions ("Always use lowercase for JSON keys")

Conversation:
{text}

Return strictly a JSON list of objects, where each object has a 'content' field.
Example: [{{"content": "User prefers Python over Go"}}, {{"content": "Project uses FastAPI"}}]
"""
        response = await self.llm.complete_async(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a Memory Extraction Engine.",
            temperature=0.0
        )
        try:
            # Basic cleanup if the model wraps it in markdown blocks
            clean_resp = response.strip().replace("```json", "").replace("```", "")
            return json.loads(clean_resp)
        except Exception:
            # Fallback or error logging
            return []

    async def _classify_item(self, item_content: str) -> str:
        """
        Classify an item into a category filename.
        """
        prompt = f"""Classify this fact into a single lower_case_snake_case category filename (e.g., 'tech_stack', 'project_rules', 'user_profile').
        
        Fact: {item_content}
        
        Return ONLY the category name. No extension.
        """
        response = await self.llm.complete_async(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a Memory Classification Engine.",
            temperature=0.0
        )
        return response.strip().lower()

    async def _evolve_summary(self, existing: str, new_memories: List[str], category: str) -> str:
        """
        Update a category summary with a batch of new information.
        Handles conflict resolution.
        """
        memory_list_text = "\\n".join([f"- {m}" for m in new_memories])
        
        prompt = f"""You are a Memory Synchronization Specialist.
        
Topic: {category.replace('_', ' ').title()}

## Original Profile
{existing if existing else "No existing profile."}

## New Memory Items to Integrate
{memory_list_text}

# Task
1. Update: If new items conflict with the Original Profile, overwrite the old facts (Assume new items are more recent/true).
2. Add: If items are new, append them logically.
3. Output: Return ONLY the updated markdown profile. Do not include introductory text.
"""
        return await self.llm.complete_async(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a Memory Synchronization Specialist.",
            temperature=0.0
        )

    async def _generate_keywords(self, category_name: str, content: str) -> List[str]:
        """
        Generate search keywords for a category to allow index-based retrieval.
        """
        # Truncate content if too large to save tokens
        if len(content) > 2000:
            content = content[:2000] + "... (truncated)"
            
        prompt = f"""Generate 10-20 search keywords/phrases for this memory category.
        The goal is to allow a search engine to find this file based on a user's question.
        Include synonyms, related terms, and tech names found in the content.
        
        Category: {category_name}
        Content:
        {content}
        
        Return STRICTLY a JSON list of strings lowercased. Do not explain.
        Example: ["python", "fastapi", "backend", "web framework"]
        """
        response = await self.llm.complete_async(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a Search Indexer. Output only JSON.",
            temperature=0.0
        )
        try:
            # 1. Try direct parse
            clean_resp = response.strip()
            if "```json" in clean_resp:
                clean_resp = clean_resp.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_resp:
                clean_resp = clean_resp.split("```")[1].split("```")[0].strip()
            
            return json.loads(clean_resp)
        except Exception:
            # 2. Try regex as fallback
            try:
                import re
                match = re.search(r'\[.*\]', response, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            except Exception as e:
                print(f"Index Gen Error: {e}. Raw: {response}")
                
            return [category_name]
