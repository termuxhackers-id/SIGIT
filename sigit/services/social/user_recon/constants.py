from sigit.services.social.user_recon.platforms import PLATFORMS as PLATFORM_RULES

PLATFORMS: list[str] = [p.url_template for p in PLATFORM_RULES]
