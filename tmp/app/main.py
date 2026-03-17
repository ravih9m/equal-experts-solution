from fastapi import FastAPI, Query
from typing import List, Annotated
from cachetools import TTLCache

from app.core.config import settings, logger
from app.services.github import fetch_user_gists, Gist

app = FastAPI(title=settings.APP_NAME)

# In-Memory Caching (Updated for Pagination)
# Max 1000 items (taaki alag-alag pages store ho sakein)
# TTL: 300 seconds (5 minutes)
cache = TTLCache(maxsize=1000, ttl=300)

@app.get("/health/live")
def liveness():
    return {"status": "alive"}

@app.get("/health/ready")
def readiness():
    return {"status": "ready"}

# Route: GET /<USER>?page=1&per_page=30
@app.get("/{username}", response_model=List[Gist])
async def get_gists(
    username: str,
    # Query Params (Default: Page 1, 30 items)
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 30
):
    # 1. Create a Unique Cache Key (User + Page Info)
    cache_key = f"{username}:{page}:{per_page}"

    # 2. Check Cache
    if cache_key in cache:
        logger.info(f"Cache HIT for {cache_key}")
        return cache[cache_key]

    # 3. Fetch from Service (GitHub)
    gists = await fetch_user_gists(username, page, per_page)

    # 4. Store in Cache
    cache[cache_key] = gists
    return gists

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )