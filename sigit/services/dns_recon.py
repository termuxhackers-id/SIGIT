from typing import Dict

import socket
import asyncio

from ..core.client import AsyncClient

class DNSRecon:
    
    @staticmethod
    async def lookup(domain: str) -> Dict:
        results = {}
        try:
            ip = await asyncio.get_event_loop().run_in_executor(None, socket.gethostbyname, domain)
            results['A'] = ip
        except:
            pass

        try:
            async with AsyncClient() as client:
                _, data = await client.get_json(f"https://dns.google/resolve?name={domain}&type=ANY")
                if 'Answer' in data:
                    for rec in data['Answer']:
                        t = rec.get('type')
                        d = rec.get('data', '')
                        if t == 15: results.setdefault('MX', []).append(d)
                        elif t == 2: results.setdefault('NS', []).append(d)
                        elif t == 16: results.setdefault('TXT', []).append(d)
        except:
            pass
        return results