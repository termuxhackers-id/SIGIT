import re

from curl_cffi.requests import AsyncSession


async def check_instagram(email: str) -> bool | None:
    user_agent = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    )
    async with AsyncSession(impersonate="chrome") as session:
        try:
            res = await session.get(
                "https://www.instagram.com/",
                headers={"User-Agent": user_agent},
                timeout=7.0,
            )
            csrf = session.cookies.get("csrftoken")
            if not csrf:
                match = re.search(r'["\']csrf_token["\']\s*:\s*["\']([^"\']+)["\']', res.text or "")
                if match:
                    csrf = match.group(1)

            headers = {
                "x-csrftoken": csrf or "",
                "x-ig-app-id": "936619743392459",
                "x-requested-with": "XMLHttpRequest",
                "origin": "https://www.instagram.com",
                "referer": "https://www.instagram.com/",
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded",
            }
            resp = await session.post(
                "https://www.instagram.com/api/v1/users/check_email/",
                data={"email": email, "sign_up_code": ""},
                headers=headers,
                timeout=7.0,
            )
            if resp.status_code == 200:
                payload = resp.json()
                if (
                    payload.get("error_type") == "email_is_taken"
                    or payload.get("available") is False
                ):
                    return True
                if payload.get("available") is True:
                    return False
            return None
        except Exception:
            return None


async def check_threads(email: str) -> bool | None:
    return await check_instagram(email)


async def check_facebook(email: str) -> bool | None:
    async with AsyncSession(impersonate="chrome") as client:
        try:
            url1 = "https://m.facebook.com/login/"
            headers1 = {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/143.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            await client.get(url1, headers=headers1, timeout=6.0)

            url2 = "https://www.facebook.com"
            headers2 = {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/143.0.0.0 Safari/537.36"
                ),
                "referer": "https://www.google.com/",
            }
            res2 = await client.get(url2, params={"_rdr": ""}, headers=headers2, timeout=6.0)
            html = res2.text or ""

            lsd_match = (
                re.search(r'\["LSD",\[\],\{"token":"([^"]+)"\}', html)
                or re.search(r'name="lsd"\s+value="([^"]+)"', html)
                or re.search(r'"lsd":"([^"]+)"', html)
            )
            j_match = re.search(r"jazoest=(\d+)", html) or re.search(
                r'name="jazoest"\s+value="(\d+)"', html
            )

            lsd = lsd_match.group(1) if lsd_match else None
            jazoest = j_match.group(1) if j_match else None
            if not lsd or not jazoest:
                return None

            url3 = "https://www.facebook.com/ajax/login/help/identify.php"
            payload3 = {
                "jazoest": jazoest,
                "lsd": lsd,
                "email": email,
                "did_submit": "1",
                "__user": "0",
                "__a": "1",
                "__req": "7",
            }
            headers3 = {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/143.0.0.0 Safari/537.36"
                ),
                "x-fb-lsd": lsd,
                "origin": "https://www.facebook.com",
                "referer": "https://www.facebook.com/login/identify/?ctx=recover",
            }
            response = await client.post(
                url3,
                params={"ctx": "recover"},
                data=payload3,
                headers=headers3,
                timeout=7.0,
            )
            body = response.text or ""
            if "These accounts matched your search" in body or "redirectPageTo" in body:
                return True
            if "No search results" in body or "Your search did not return any results" in body:
                return False
            return None
        except Exception:
            return None


async def check_lespark(email: str) -> bool | None:
    async with AsyncSession(impersonate="chrome") as client:
        try:
            url = "https://api3.lespark.cn/login"
            payload = {
                "password": "d9bd8afc54ee5dc6c1ee6096e297ec31",
                "verion": "1",
                "email": email,
                "luid": "",
                "request-id": "req-probe",
            }
            headers = {
                "User-Agent": "okhttp-okgo/jeasonlzy",
                "lang": "en",
            }
            resp = await client.post(url, data=payload, headers=headers, timeout=6.0)
            if resp.status_code == 200:
                data = resp.json()
                msg = str(data.get("msg", "")).lower()
                if "password is wrong" in msg:
                    return True
                if "user does not exist" in msg:
                    return False
            return None
        except Exception:
            return None


async def check_meeff(email: str) -> bool | None:
    async with AsyncSession(impersonate="chrome") as client:
        try:
            url = "https://api.meeff.com/user/login/v4"
            payload = {
                "provider": "email",
                "providerId": email,
                "providerToken": "",
                "os": "Android v11",
                "platform": "android",
                "appVersion": "7.1.2",
                "locale": "en",
            }
            headers = {
                "content-type": "application/json; charset=utf-8",
                "User-Agent": "okhttp/5.3.2",
            }
            resp = await client.post(url, json=payload, headers=headers, timeout=6.0)
            if resp.status_code == 401:
                data = resp.json()
                error_msg = data.get("errorMessage", "").lower()
                if "passwords do not match" in error_msg:
                    return True
                if "hasn't been signed up yet" in error_msg:
                    return False
            return None
        except Exception:
            return None
