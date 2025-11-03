from typing import Dict

from ..core.client import AsyncClient

class TechStackDetector:
    
    PATTERNS = {
        'WordPress': ['wp-content', 'wp-includes'],
        'Joomla': ['joomla'], 'Drupal': ['drupal'],
        'React': ['react', '_reactRoot'], 'Vue.js': ['vue', '__vue__'],
        'Angular': ['ng-version', 'angular'], 'Bootstrap': ['bootstrap'],
        'jQuery': ['jquery']
    }

    @staticmethod
    async def detect(url: str) -> Dict:
        tech = {'servers': [], 'frameworks': [], 'analytics': [], 'cdn': []}
        async with AsyncClient() as client:
            status, html = await client.get(url)
            if status != 200:
                return tech
            async with client.session.get(url) as resp:  # type: ignore
                headers = resp.headers
                if 'Server' in headers:
                    tech['servers'].append(headers['Server'])
                html_lower = html.lower()
                for name, kws in TechStackDetector.PATTERNS.items():
                    if any(kw in html_lower for kw in kws):
                        tech['frameworks'].append(name)
                if 'google-analytics' in html_lower or 'gtag' in html_lower:
                    tech['analytics'].append('Google Analytics')
                cdn_map = {'cf-ray': 'Cloudflare', 'x-amz-cf-id': 'AWS CloudFront'}
                for h, name in cdn_map.items():
                    if h in headers:
                        tech['cdn'].append(name)
        return tech