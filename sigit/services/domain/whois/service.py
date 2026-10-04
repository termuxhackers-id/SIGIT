import asyncio

from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult


class WhoisInput(BaseModel):
    domain: str = Field(description="Target domain or IP address")


class WHOISLookup(BaseService):
    name = "WHOISLookup"
    description = "Query WHOIS domain registration records"
    category = Category.DOMAIN
    input_schema = WhoisInput

    async def execute(self, params: WhoisInput) -> ServiceResult:
        domain = params.domain.strip()
        try:
            process = await asyncio.create_subprocess_exec(
                "whois",
                domain,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()

            if process.returncode == 0:
                output = stdout.decode(errors="replace").strip()
                if output:
                    return ServiceResult.ok(output, render_type=RenderType.TEXT)

            return ServiceResult.fail(f"Could not retrieve WHOIS data for {domain}")
        except FileNotFoundError:
            return ServiceResult.fail("System 'whois' binary is not installed")
        except Exception as error:
            return ServiceResult.fail(f"WHOIS lookup error: {error}")
