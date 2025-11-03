import socket

from typing import List, Dict, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..core.config import config

class PortScanner:
    
    COMMON_PORTS = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
        3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
        8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 27017: "MongoDB"
    }

    @staticmethod
    async def scan(target: str, ports: List[int] | None = None) -> List[Dict]:
        if ports is None:
            ports = list(PortScanner.COMMON_PORTS.keys())
        
        results = []

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(PortScanner._check, target, p): p for p in ports}
            for future in as_completed(futures):
                res = future.result()
                if res:
                    results.append(res)
        return results

    @staticmethod
    def _check(target: str, port: int) -> Union[Dict, None]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            if sock.connect_ex((target, port)) == 0:
                return {"port": port, "status": "open"}
        except:
            sock = socket.socket()
            pass
        finally:
            sock.close()
        return None