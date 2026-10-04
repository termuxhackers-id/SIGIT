import hashlib
import urllib.parse
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from curl_cffi.requests.session import HttpMethod


@dataclass(frozen=True)
class EmailPlatformRule:
    name: str
    category: str
    url: str
    check_url_template: str = ""
    method: HttpMethod = "GET"
    headers: dict[str, str] | None = None
    json_payload: dict[str, Any] | None = None
    data_payload: dict[str, str] | None = None
    params: dict[str, str] | None = None
    hash_method: str | None = None
    positive_markers: tuple[str, ...] = ()
    negative_markers: tuple[str, ...] = ()
    taken_codes: tuple[int, ...] = (200,)
    available_codes: tuple[int, ...] = (404,)
    validator: Callable[[int, str, Any], bool | None] | None = None
    custom_checker: Callable[[str], Any] | None = None

    def build_request(
        self, email: str
    ) -> tuple[
        HttpMethod,
        str,
        dict[str, str],
        dict[str, Any] | None,
        dict[str, str] | None,
        dict[str, str] | None,
    ]:
        clean_email = email.strip().lower()
        encoded_email = urllib.parse.quote(clean_email)
        email_hash = ""
        if self.hash_method == "md5":
            email_hash = hashlib.md5(clean_email.encode()).hexdigest()
        elif self.hash_method == "sha256":
            email_hash = hashlib.sha256(clean_email.encode()).hexdigest()

        check_url = self.check_url_template.format(
            email=clean_email,
            encoded_email=encoded_email,
            email_hash=email_hash,
        )

        headers = dict(self.headers) if self.headers else {}

        json_data = None
        if self.json_payload:
            json_data = {}
            for k, v in self.json_payload.items():
                if isinstance(v, str):
                    json_data[k] = v.format(
                        email=clean_email,
                        encoded_email=encoded_email,
                        email_hash=email_hash,
                    )
                else:
                    json_data[k] = v

        data_data = None
        if self.data_payload:
            data_data = {}
            for k, v in self.data_payload.items():
                data_data[k] = v.format(
                    email=clean_email,
                    encoded_email=encoded_email,
                    email_hash=email_hash,
                )

        params_data = None
        if self.params:
            params_data = {}
            for k, v in self.params.items():
                params_data[k] = v.format(
                    email=clean_email,
                    encoded_email=encoded_email,
                    email_hash=email_hash,
                )

        return self.method, check_url, headers, json_data, data_data, params_data

    def evaluate(self, status_code: int, text: str, json_data: Any) -> bool | None:
        if self.validator is not None:
            return self.validator(status_code, text, json_data)

        if self.positive_markers and any(m in text for m in self.positive_markers):
            return True

        if self.negative_markers and any(m in text for m in self.negative_markers):
            return False

        if status_code in self.taken_codes and not self.positive_markers:
            return True

        if status_code in self.available_codes and not self.negative_markers:
            return False

        return None
