import httpx
from typing import List, Dict, Optional
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict
from app.core.config import settings, logger

# --- Data Models ---
class FileInfo(BaseModel):
    size: int
    raw_url: str
    type: str
    language: Optional[str] = None

class Gist(BaseModel):
    id: str
    url: str
    html_url: str
    files: Dict[str, FileInfo]
    description: Optional[str] = None
    created_at: str
    model_config = ConfigDict(from_attributes=True)

# --- Service Logic ---
async def fetch_user_gists(username: str, page: int = 1, per_page: int = 30) -> List[Gist]:
    """
    Fetches Gists from GitHub with Pagination.
    page: Page number (default 1)
    per_page: Items per page (default 30, max 100)
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # Query Parameters for GitHub
    params = {
        "page": page,
        "per_page": per_page
    }

    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Fetching gists for {username} (Page: {page}, Limit: {per_page})")
            
            response = await client.get(
                f"{settings.GITHUB_API_URL}/users/{username}/gists",
                headers=headers,
                params=params,  # <-- Pagination Params added here
                timeout=10.0
            )

            if response.status_code == 404:
                logger.warning(f"User {username} not found")
                raise HTTPException(status_code=404, detail="User not found")

            if response.status_code != 200:
                logger.error(f"GitHub API Error: {response.text}")
                raise HTTPException(status_code=502, detail="Error communicating with GitHub")

            data = response.json()
            return [Gist(**item) for item in data]

        except httpx.RequestError as exc:
            logger.error(f"Network error: {exc}")
            raise HTTPException(status_code=503, detail="Service unavailable")