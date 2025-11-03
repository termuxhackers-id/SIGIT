import ssl
import socket
import certifi

from typing import Dict
from datetime import datetime

class SSLChecker:
    
    @staticmethod
    async def check(domain: str) -> Dict:
        try:
            context = ssl.create_default_context(cafile=certifi.where())
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    subject = dict(x[0] for x in cert.get('subject', [])) # type: ignore
                    issuer = dict(x[0] for x in cert.get('issuer', [])) # type: ignore
                    return {
                        'subject': subject,
                        'issuer': issuer,
                        'not_before': cert.get('notBefore'), # type: ignore
                        'not_after': cert.get('notAfter'), # type: ignore
                        'expired': datetime.strptime(cert.get('notAfter'), '%b %d %H:%M:%S %Y %Z') < datetime.now() # type: ignore
                    }
        except:
            return {}