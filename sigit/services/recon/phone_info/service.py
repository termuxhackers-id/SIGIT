import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from pydantic import BaseModel, Field

from sigit.core.base import BaseService, Category, RenderType, ServiceResult


class PhoneInput(BaseModel):
    phone_number: str = Field(description="Phone number with country code (e.g. +14155552671)")


class PhoneInfo(BaseService):
    name = "PhoneInfo"
    description = "Lookup country, carrier, line type, and national formatting"
    category = Category.RECON
    input_schema = PhoneInput

    TYPE_NAMES = {
        phonenumbers.PhoneNumberType.MOBILE: "Mobile",
        phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
        phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
        phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
        phonenumbers.PhoneNumberType.VOIP: "VoIP",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
        phonenumbers.PhoneNumberType.PAGER: "Pager",
        phonenumbers.PhoneNumberType.UAN: "Universal Access Number",
        phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail",
        phonenumbers.PhoneNumberType.UNKNOWN: "Unknown",
    }

    async def execute(self, params: PhoneInput) -> ServiceResult:
        raw_number = params.phone_number.strip()
        try:
            parsed = phonenumbers.parse(raw_number)
            is_valid = phonenumbers.is_valid_number(parsed)
            is_possible = phonenumbers.is_possible_number(parsed)

            country_name = geocoder.description_for_number(parsed, "en") or "Unknown"
            carrier_name = carrier.name_for_number(parsed, "en") or "Unknown"
            time_zones = list(timezone.time_zones_for_number(parsed))

            num_type = phonenumbers.number_type(parsed)
            line_type = self.TYPE_NAMES.get(num_type, "Unknown")

            formatted_e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            formatted_intl = phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            formatted_nat = phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.NATIONAL
            )

            result_data = {
                "e164_format": formatted_e164,
                "international": formatted_intl,
                "national_format": formatted_nat,
                "is_valid": "Yes" if is_valid else "No",
                "is_possible": "Yes" if is_possible else "No",
                "line_type": line_type,
                "country": country_name,
                "carrier": carrier_name,
                "timezones": time_zones or ["N/A"],
                "country_code": str(parsed.country_code),
            }

            return ServiceResult.ok(result_data, render_type=RenderType.KEY_VALUE)
        except phonenumbers.NumberParseException as error:
            return ServiceResult.fail(f"Invalid phone number format: {error}")
