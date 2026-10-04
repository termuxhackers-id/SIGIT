import asyncio

from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult


class PortScannerInput(BaseModel):
    target: str = Field(description="Target domain or IP address")
    ports: str = Field(
        default="21,22,23,25,53,80,110,143,443,445,3306,3389,5432,8080,8443,27017",
        description="Comma-separated port numbers",
    )
    timeout: float = Field(default=1.5, description="Connection timeout in seconds")


class PortScanner(BaseService):
    name = "PortScanner"
    description = "Asynchronous TCP port scanner with service banner grabbing"
    category = Category.NETWORK
    input_schema = PortScannerInput

    PORT_NAMES: dict[int, str] = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        445: "SMB",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        8080: "HTTP-Proxy",
        8443: "HTTPS-Alt",
        27017: "MongoDB",
    }

    async def execute(self, params: PortScannerInput) -> ServiceResult:
        target = params.target.strip()
        port_numbers = [int(p.strip()) for p in params.ports.split(",") if p.strip().isdigit()]

        open_ports: list[dict[str, str | int]] = []

        async def _probe_port(port: int) -> None:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(target, port),
                    timeout=params.timeout,
                )
                service_label = self.PORT_NAMES.get(port, "Unknown")
                banner = ""

                try:
                    if port in (80, 8080):
                        writer.write(b"HEAD / HTTP/1.0\r\nHost: " + target.encode() + b"\r\n\r\n")
                        await writer.drain()
                    elif port not in (443, 8443):
                        writer.write(b"\r\n")
                        await writer.drain()

                    raw_data = await asyncio.wait_for(reader.read(256), timeout=1.0)
                    if raw_data:
                        lines = raw_data.decode(errors="replace").splitlines()
                        for line in lines:
                            clean_line = line.strip()
                            if clean_line:
                                banner = clean_line[:40]
                                break
                except Exception:
                    pass

                writer.close()
                await writer.wait_closed()

                open_ports.append(
                    {
                        "port": port,
                        "service": service_label,
                        "banner": banner or "-",
                        "status": "OPEN",
                    }
                )
            except (TimeoutError, OSError):
                pass

        await asyncio.gather(*[_probe_port(port) for port in port_numbers])

        if not open_ports:
            return ServiceResult.fail(f"No open ports detected on {target}")

        open_ports.sort(key=lambda item: int(item["port"]))
        return ServiceResult.ok(open_ports, render_type=RenderType.TABLE)
