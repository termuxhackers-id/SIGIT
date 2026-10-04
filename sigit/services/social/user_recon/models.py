import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PlatformRule:
    name: str
    category: str
    url_template: str
    check_url_template: str | None = None
    headers: dict[str, str] | None = None
    regex_pattern: str | None = None
    min_length: int = 1
    max_length: int = 100
    allow_redirects: bool = True
    taken_status_codes: tuple[int, ...] = (200,)
    available_status_codes: tuple[int, ...] = (404,)
    positive_markers: tuple[str, ...] = ()
    negative_markers: tuple[str, ...] = ()
    is_json: bool = False
    json_verify_key: str | None = None
    json_list_not_empty: bool = False
    details_extractor: Callable[[str, Any], str | None] | None = None
    custom_checker: Callable[[str], Any] | None = None

    def is_valid_username(self, username: str) -> bool:
        if not (self.min_length <= len(username) <= self.max_length):
            return False
        if self.regex_pattern and not re.match(self.regex_pattern, username):
            return False
        return True

    def get_profile_url(self, username: str) -> str:
        return self.url_template.format(username=username)

    def get_check_url(self, username: str) -> str:
        if self.check_url_template:
            return self.check_url_template.format(username=username)
        return self.get_profile_url(username)
