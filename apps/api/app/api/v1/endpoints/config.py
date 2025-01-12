from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from app.core.deps import get_current_user
from app.agents.llm_config import switch_llm_provider, DEFAULT_CONFIGS

router = APIRouter()

class LLMProviderUpdate(BaseModel):
    """Schema for updating LLM provider"""
    provider: str

@router.get("/llm/providers", response_model=List[str])
async def list_llm_providers(
    current_user = Depends(get_current_user)
) -> List[str]:
    """List available LLM providers"""
    return list(DEFAULT_CONFIGS.keys())

@router.post("/llm/switch")
async def update_llm_provider(
    provider_update: LLMProviderUpdate,
    current_user = Depends(get_current_user)
):
    """Switch the active LLM provider"""
    try:
        switch_llm_provider(provider_update.provider)
        return {"message": f"Successfully switched to {provider_update.provider}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 