from typing import Any

from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult
from sigit.core.http import HttpClient


class GitHubInput(BaseModel):
    username: str = Field(description="Target GitHub username")


class GitHubRecon(BaseService):
    name = "GitHubRecon"
    description = "Fetch GitHub user profile, exposed commit emails, keys, and repositories"
    category = Category.SOCIAL
    input_schema = GitHubInput

    async def execute(self, params: GitHubInput) -> ServiceResult:
        username = params.username.strip()
        user_url = f"https://api.github.com/users/{username}"
        repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5"
        events_url = f"https://api.github.com/users/{username}/events/public"
        keys_url = f"https://github.com/{username}.keys"

        try:
            user_response = await HttpClient.get(user_url)
            if user_response.status_code != 200:
                return ServiceResult.fail(f"User '{username}' not found on GitHub")

            user_data = user_response.json()

            repos_response = await HttpClient.get(repos_url)
            repos_data = repos_response.json() if repos_response.status_code == 200 else []

            events_response = await HttpClient.get(events_url)
            events_data = events_response.json() if events_response.status_code == 200 else []

            keys_response = await HttpClient.get(keys_url)
            public_keys = (
                [k.strip() for k in keys_response.text.splitlines() if k.strip()]
                if keys_response.status_code == 200
                else []
            )

            discovered_emails: set[str] = set()
            if isinstance(events_data, list):
                for event in events_data:
                    if event.get("type") == "PushEvent":
                        commits = event.get("payload", {}).get("commits", [])
                        for commit in commits:
                            author_email = commit.get("author", {}).get("email", "")
                            if author_email and "users.noreply.github.com" not in author_email:
                                discovered_emails.add(author_email)

            repo_summaries: list[str] = []
            if isinstance(repos_data, list):
                for repo in repos_data:
                    name = repo.get("name", "")
                    stars = repo.get("stargazers_count", 0)
                    lang = repo.get("language") or "N/A"
                    desc = repo.get("description") or "No description"
                    repo_summaries.append(f"[{stars} stars] {name} [{lang}] - {desc[:50]}")

            profile_fields = [
                "name",
                "bio",
                "location",
                "email",
                "company",
                "twitter_username",
                "followers",
                "following",
                "public_repos",
                "public_gists",
            ]
            clean_profile: dict[str, Any] = {
                field: user_data.get(field) or "N/A" for field in profile_fields
            }

            clean_profile["exposed_commit_emails"] = (
                list(discovered_emails) if discovered_emails else ["None detected"]
            )
            clean_profile["ssh_keys_count"] = len(public_keys)
            if repo_summaries:
                clean_profile["recent_repos"] = repo_summaries

            return ServiceResult.ok(clean_profile, render_type=RenderType.KEY_VALUE)
        except Exception as error:
            return ServiceResult.fail(f"GitHub lookup error: {error}")
