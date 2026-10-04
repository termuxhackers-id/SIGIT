import json
import re

from curl_cffi.requests import AsyncSession


async def check_tinder_user(user: str) -> bool | None:
    async with AsyncSession(impersonate="chrome") as session:
        try:
            resp = await session.get(f"https://tinder.com/@{user}", timeout=7.0)
            if resp.status_code != 200:
                return False
            match = re.search(
                r"window\.__data\s*=\s*(\{.*?\})\s*;</script>",
                resp.text or "",
                re.DOTALL,
            )
            if not match:
                return False
            try:
                data = json.loads(match.group(1))
                profile = data.get("webProfile", {})
                if (
                    isinstance(profile, dict)
                    and profile.get("username")
                    and str(profile["username"]).lower() == user.lower()
                ):
                    return True
                return False
            except (json.JSONDecodeError, ValueError):
                return False
        except Exception:
            return None


async def check_facebook_user(user: str) -> bool | None:
    async with AsyncSession(impersonate="chrome") as session:
        try:
            resp = await session.get(
                f"https://www.facebook.com/{user}",
                allow_redirects=True,
                timeout=7.0,
            )
            if resp.status_code != 200:
                return False
            text = resp.text or ""
            if "This content isn't available" in text or "This content isn\\'t available" in text:
                return False
            if '<meta property="og:title"' in text and '<meta property="og:url"' in text:
                return True
            return False
        except Exception:
            return None


async def check_x_user(user: str) -> bool | None:
    if len(user) > 15:
        return False
    async with AsyncSession(impersonate="chrome") as session:
        try:
            resp = await session.get(
                "https://api.twitter.com/i/users/username_available.json",
                params={"username": user},
                timeout=7.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("reason") == "taken":
                    return True
                if data.get("valid") is True:
                    return False
            return False
        except Exception:
            return None


async def check_snapchat_user(user: str) -> bool | None:
    async with AsyncSession(impersonate="chrome") as session:
        try:
            resp = await session.get(
                f"https://www.snapchat.com/@{user}",
                allow_redirects=True,
                timeout=7.0,
            )
            if resp.status_code != 200:
                return False
            match = re.search(
                r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
                resp.text or "",
            )
            if not match:
                return False
            data = json.loads(match.group(1))
            user_profile = data.get("props", {}).get("pageProps", {}).get("userProfile")
            return bool(user_profile)
        except Exception:
            return None


async def check_linkedin_user(user: str) -> bool | None:
    async with AsyncSession(impersonate="chrome") as session:
        try:
            headers = {"User-Agent": "Twitterbot/1.0"}
            resp = await session.get(
                f"https://www.linkedin.com/in/{user}",
                headers=headers,
                allow_redirects=True,
                timeout=7.0,
            )
            if resp.status_code == 200 and 'property="og:type" content="profile"' in (
                resp.text or ""
            ):
                return True
            return False
        except Exception:
            return None
