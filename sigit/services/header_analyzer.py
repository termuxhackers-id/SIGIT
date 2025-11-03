from typing import Dict

from ..core.client import AsyncClient

class HeaderAnalyzer:
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'HSTS',
        'Content-Security-Policy': 'CSP',
        'X-Frame-Options': 'Clickjacking Protection',
        'X-Content-Type-Options': 'MIME Sniffing Protection',
        'X-XSS-Protection': 'XSS Protection',
        'Referrer-Policy': 'Referrer Policy',
        'Permissions-Policy': 'Permissions Policy'
    }

    @staticmethod
    async def analyze(url: str) -> Dict:
        async with AsyncClient() as client:
            async with client.session.get(url) as resp: # type: ignore
                headers = resp.headers
                score = sum(1 for h in HeaderAnalyzer.SECURITY_HEADERS if h in headers)
                return {
                    'headers': dict(headers),
                    'score': score,
                    'total': len(HeaderAnalyzer.SECURITY_HEADERS),
                    'percentage': (score / len(HeaderAnalyzer.SECURITY_HEADERS)) * 100
                }