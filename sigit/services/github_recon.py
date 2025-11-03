from typing import Dict

from ..core.client import AsyncClient

class GitHubRecon:
    
    @staticmethod
    async def recon(username: str) -> Dict:
        async with AsyncClient() as client:
            _, user = await client.get_json(f"https://api.github.com/users/{username}")
            if 'message' in user:
                return {}
            _, repos = await client.get_json(f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5")
            user['recent_repos'] = repos[:5] if isinstance(repos, list) else []
            return user