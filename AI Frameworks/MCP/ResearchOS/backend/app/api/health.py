from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "free_tier_connectors": {
            "arxiv": settings.ARXIV_ENABLED,
            "openalex": bool(settings.OPENALEX_EMAIL),
            "semantic_scholar": bool(settings.SEMANTIC_SCHOLAR_API_KEY),
            "tavily": bool(settings.TAVILY_API_KEY),
            "brave": bool(settings.BRAVE_SEARCH_API_KEY)
        },
        "llm_inference": {
            "gemini_free_tier": bool(settings.GEMINI_API_KEY),
            "ollama_local": settings.OLLAMA_BASE_URL
        }
    }
