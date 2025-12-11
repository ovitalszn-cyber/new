"""
Secure API Key Management System
Handles all bookmaker API keys and authentication securely.
"""

import os
import json
import base64
from typing import Dict, Any, Optional
import structlog
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = structlog.get_logger()


class SecureKeyManager:
    """
    Secure key management system that can work with environment variables
    and optionally encrypted storage for production environments.
    """

    def __init__(self):
        self.encryption_key = self._generate_encryption_key()
        self.cipher = Fernet(self.encryption_key)

    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key from environment or create a default one."""
        # In production, this should come from a secure environment variable
        key_seed = os.getenv("KASHROCK_ENCRYPTION_KEY", "default_kashrock_key_seed")

        # Use PBKDF2 to derive a proper Fernet key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"kashrock_salt_2025",  # Should be configurable in production
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(key_seed.encode()))

    def get_bookmaker_credentials(self, bookmaker: str) -> Dict[str, Any]:
        """
        Get all credentials for a specific bookmaker from environment variables.

        Args:
            bookmaker: Name of the bookmaker (e.g., 'fliff', 'rebet', 'hardrock')

        Returns:
            Dict of credential key -> value
        """
        credentials = {}

        # Define credential mappings for each bookmaker
        credential_mappings = {
            'pinnacle': {
                'x_api_key': 'PINNACLE_X_API_KEY',
                'device_uuid': 'PINNACLE_DEVICE_UUID'
            },
            # Real working values extracted from curl files
            'pinnacle_defaults': {
                'x_api_key': 'CmX2KcMrXuFmNg6YFbmTxE0y9CIrOi0R',
                'device_uuid': ''
            },
            'hardrock': {
                'cookie': 'HARDROCK_COOKIE',
                'sessiontoken': 'HARDROCK_SESSIONTOKEN',
                'sentry_trace': 'HARDROCK_SENTRY_TRACE',
                'baggage': 'HARDROCK_BAGGAGE',
                'user_agent': 'HARDROCK_USER_AGENT'
            },
            # Real working values extracted from curl files
            'hardrock_defaults': {
                'cookie': '_ga_YNVSXM82RX=GS2.1.s1759065631$o1$g1$t1759065716$j52$l0$h0; _ga=GA1.1.620930274.1759065632',
                'sessiontoken': '',
                'sentry_trace': '',
                'baggage': '',
                'user_agent': ''
            },
            'propscash': {
                'token': 'PROPSCASH_TOKEN'
            },
            # Real working values extracted from curl files
            'propscash_defaults': {
                'token': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjF0dUkybDZSQjBjWlF2MHM1M28yNSJ9.eyJzdWJzY3JpcHRpb24iOiJ0cmlhbCIsImlzcyI6Imh0dHBzOi8vcHJvcHMtaGVscGVyLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDExMzIwMjk2MjY5NjI4NTA2NTUwMSIsImF1ZCI6WyJodHRwczovL3Byb3BzLWRvdC1jYXNoL2FwaSIsImh0dHBzOi8vcHJvcHMtaGVscGVyLnVzLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE3NjAxNTIyNTksImV4cCI6MTc2Mjc0NDI1OSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBvZmZsaW5lX2FjY2VzcyIsImF6cCI6ImtJNzZQWWs5QTNnN3lVdHloWTNBaEttcjlvdmlIQXp3In0.lS4pr4KG0UwFJbXRHBuA2-VpIfZbuI0LdYjwY6y_u10u45BMKn7lNJG2IW_UvxKwbdIZgHk1EG11kObMnUwKbMeYqtXKZxQkCpdf2i4BmKdxKrCuy1rvhPiAC7R7YH5z9WrGbz8-A6UdnJpW20pAtT1-txc6WoW4DM6nYV-ejI7O4UrxU9MTnBRt88VDLnrWZeSoRLVTFXGlJxMomzJOIhOIPhp72R5ZITiqTruslmy65csVualcDf6yXiqjuQzzAmQYT5_UG-_clqtP9f11DCEeFOVi49Lsrvnhl-9lY25fWrHAfnvzLjZLeGDKhTZKo5FuLZnW_CgrB0ihg3O-JQ'
            },
            'rebet': {
                'api_key': 'REBET_API_KEY',
                'bearer': 'REBET_BEARER',
                'jwt_token': 'REBET_JWT_TOKEN'
            },
            # Real working values for Rebet
            'rebet_defaults': {
                'api_key': 'J9xowBQZM980G97zv9VoB9Ylady1pVtS5Ix9tuL1',
                'bearer': 'eyJraWQiOiI3WkdkV1Y5THJucmdIY25QUWdMNWd0VzJXSGlpV2o3K2VBQ1FsR2FQeGlVPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIxNDA1MTQxZi0yYmJkLTQ0MTEtODM5NS1lNjIzZGI0ODdkYmYiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYWRkcmVzcyI6eyJmb3JtYXR0ZWQiOiJGbG9yaWRhIn0sImJpcnRoZGF0ZSI6IjIwMDQtMDctMjUiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0yLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMl9lcHo2ZEF4UXUiLCJwaG9uZV9udW1iZXJfdmVyaWZpZWQiOmZhbHNlLCJjb2duaXRvOnVzZXJuYW1lIjoiZHJheCIsIm9yaWdpbl9qdGkiOiJjYWI3NDEzNi02NGYzLTQyNmUtYmEyOS0xNTJiNTI3MWZmNzUiLCJhdWQiOiI3M3Z2dmxja2RyampvdmJpc3MzaWhiZDI2byIsImV2ZW50X2lkIjoiN2RjOTQ5ODUtMzU0My00ZGQ0LTkxNGItNDJiZTRmZjAyYmQ0IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTE2MTAzMjksInBob25lX251bWJlciI6IisxNzI4MjA2MjMzOCIsImV4cCI6MTc1NDA4ODE2MCwiaWF0IjoxNzU0MDg0NTYwLCJqdGkiOiJiZWIxNTU3OS1iZjAwLTRlOTMtOGE2Zi1hMmY0NTUwMmExMjYiLCJlbWFpbCI6Imphdmllb240MUBnbWFpbC5jb20ifQ.AlLFzBgxZBD4mUZNRfmmTPUz5q8V2vCjEiU-NaSdmIceRpOPejffBbhNlehhtVSNVVCr9vlXOgl4jpAwLuoHEIxOWrOJu2sLfE5GvEWem_MNXoTjKOTGnRYp7clskxJxbGzZpns4JURbVqQK4ytx79kd0gyhuB8nLlVBoZk7a8ee7Yr8XW5Z6bOHewxeq9eYuwN0LIw7z5aM88Eqlnd-LwTHJ8UBzuw03aTattaz5uevB2ZLYXTfgy7DORUS3dF0hI9fYqmML0mnbpyfCgsjZUtXmO06rJCsjyexuxiysex5aa495MjGFjO2cHXfbEJ3kNPEAn9Mh0e3GDHzoPkGug',
                'jwt_token': ''
            },
            'fliff': {
                'device_x_id': 'FLIFF_DEVICE_X_ID',
                'app_x_version': 'FLIFF_APP_X_VERSION',
                'app_install_token': 'FLIFF_APP_INSTALL_TOKEN',
                'auth_token': 'FLIFF_AUTH_TOKEN',
                'conn_id': 'FLIFF_CONN_ID',
                'platform': 'FLIFF_PLATFORM',
                'usa_state_code': 'FLIFF_USA_STATE_CODE',
                'usa_state_code_source': 'FLIFF_USA_STATE_CODE_SOURCE',
                'xtag': 'FLIFF_XTAG',
                'country_code': 'FLIFF_COUNTRY_CODE',
                'cookie': 'FLIFF_COOKIE'
            },
            # Real working values extracted from curl files (for development when env vars not set)
            'fliff_defaults': {
                'device_x_id': 'ios.A0C89328-2F3C-453A-8D31-551DAC179B6B',
                'app_x_version': '5.8.4.258',
                'app_install_token': 'pr9qlSazL8',
                'auth_token': 'fobj__sb_user_profile__541050',
                'conn_id': '18',
                'platform': 'prod',
                'usa_state_code': 'FL',
                'usa_state_code_source': 'ipOrigin=radar|regionCode=FL|meta=successGetRegionCode|geocodeOrigin=radar|regionCode=FL|meta=successGetRegionCode',
                'xtag': 'meta_18',
                'country_code': 'US',
                'cookie': 'afUserId=8d91d74e-488c-4e20-85bc-26358ba07089-p'
            },
            'betr': {
                'auth_token': 'BETR_AUTH_TOKEN'
            },
            # Real working values extracted from curl files (for development when env vars not set)
            'betr_defaults': {
                'auth_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJXZWFZbzF6WTZHWEJITVBLaXhiWWR2TTI5S2dZVWE5S0VVSk1ublIzZ2JJIn0.eyJleHAiOjE3NjIxMjA0ODksImlhdCI6MTc1OTUyODQ4OSwiYXV0aF90aW1lIjoxNzU5MDY1NzE3LCJqdGkiOiI3ODZhNTBlYy01N2RiLTQ0ZjctODQ1Ny05NThmMWFiNDVjNjkiLCJpc3MiOiJodHRwczovL2FjY291bnQuYmV0ci5hcHAvcmVhbG1zL2JldHIiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiZTlhZWI0NzQtOTIxYy00YmRmLWE1ZmItZDlkODlkYzk5ZDA5IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiYmV0ci1ybiIsInNpZCI6IjkyNzQwOWFjLTNmNzktNGViMS05ZDM3LWVmZmM2NTI4ZmRjNCIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiKiJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsImRlZmF1bHQtcm9sZXMtYmV0ciJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgb2ZmbGluZV9hY2Nlc3MiLCJmYWNlX2lkX2VuYWJsZWQiOnRydWUsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibWZhIjp0cnVlLCJwcm9tb19jb2RlIjoiQkVUUlBST01PMjIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ1bmlzb25zbm93cGxvd3RpbGluZyIsIm1vYmlsZV9udW1iZXIiOiI3MjgyMDYyMzM4IiwiZmFjZV9pZF92ZXJpZmllZCI6dHJ1ZSwiZW1haWwiOiJqYXZpZW9uMjAyNUBnbWFpbC5jb20iLCJtb2JpbGVfbnVtYmVyX3ZlcmlmaWVkIjp0cnVlfQ.WrNASIz1yOnhErVMc5uxJYdUtAaKdRYK56O5DIULKtfkqP_qIUs1GYHLCNwAqvwgLJNA6fMBgW2dl89sf0mnW5_nZWqEqB7UkKU4O6Nb3wJ8XdhmYSDIzbuMrPVTd0zzXiWHVEF3yQB3q0xN6grdoRY6V6pWXMDtsQ1lD00KLC4Sai4gRM6xA3MxjQRNmuotqCsw9iQX-ZuqAP0DLoKoWI-A9pdUQu2yl65fjzkq_ZcVkPPO3URUO4LeG_oq8NAN14Rw67yanACNBzDV_7C3LY-sBSsDonFxcOiBvlX7sICnEgayzrhZjfNmUTxoMIeieYGbUOw47f0If3MDS8113g'
            },
            'parlayplay': {
                'bearer': 'PARLAYPLAY_BEARER',
                'session': 'PARLAYPLAY_SESSION'
            },
            # Real working values extracted from curl files
            'parlayplay_defaults': {
                'bearer': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwNzM1NDkwLCJpYXQiOjE3NTk1MjU4OTAsImp0aSI6IjQwZjUxMjAyZTIxYjRjM2JiMjY2MjlhNDZmZGNkYzk5IiwidXNlcl9pZCI6Ijc4MDc0In0.iFl8S4wxLJeRFYSUV1RgcVAgT5PZ-IphVaXwnu7Fljg',
                'session': 'ri2k1np6eli1ag5wnjkatvr1zml5tdw'
            },
            'betonline': {
                'cookies': 'BETONLINE_COOKIES'
            },
            'fanatics': {
                'cookie': 'FANATICS_COOKIE'
            },
            'bet365': {
                'sync_term': 'BET365_SYNC_TERM',
                'cookies': 'BET365_COOKIES'
            },
            # Real working values extracted from curl files
            'bet365_defaults': {
                'sync_term': 'QkhhQW92NUJiY2NCQmI5RnZCalY3VFZqcXVCWlhVWjBOVlo2UzRxa2dFeDUrbWJyVVd4eXhhUVFHcVoxN0piSzJEcFo4MkdrSGR3cTUycGgxRFYyVTJJOXl6bWk0WGRXK0tiVWZnazIyN0Yza2xNWHkwS0NQL3BaNGFlWFJGRlZhb0FnOEJCV0hENmpHMERGY1pUK21NOFpLeExqUVFKODVyVVFDaHZMeldGUm81S0tVR1NGbmJKbUE5WTY2ZE95ZXNsN21JZTdLdS8zbmJjK29ENkRyRzVBeFVITm5FN3NYMzU0MGljREZxb1VNUUx5WU1mZTlwV29Kc3RnNDI4bGhZZFVkYk13QkhaUHpselFqMDJQbnZKM2owRC9FaWtWL2x5VjluTGgvSzFjbk92dW5PYW5kNU93MnRVcy8wTE9HNEtnV2hyOWV6am53WWlQVk9acE52cWdCaU8vYUNXYVZLMFkrWlhjdkJNclRQQUNYU0NtZERDZ1ZTTllERldaQ0wxMEs1TnN1U213WVNFdUF2UVdQT0pVM2QvLzM5d3ZmSm42R2FSSC8vYWFobHlHUXpBU2NoYm5YVGUrU0VBTWdFcFB2c2dLcXJHTGY3WXZmQUFNeDRDYmp2QmJIR1hBM1RVZ25NdmxrU1lzM3U2bHBQeVZkRjN4QXNJTVJtUlpza3lkKyszYU9YbkppMTl2TzVIUzBwSG9LUXNwaFVFR1FlMS9nSEJYVExZa0d1SXRDZmMxN3lyNm9SOVZQQjZBRWE3SG1KZGRUOXVsb2tnbi9uODZPSDBLSW5LbU94Qm9JS01Ec1F2aEIrVGdZRlk5Q0ljbVZrQ01KQzBqWHF5czI1SUVDd0JPdzlLYzhqbjlBa2RuVE8yWUs2UGlLOVlRenpVV0N6Wjhv',
                'cookies': '__cf_bm=kGK.HgA3JE4bHqGe_uE0yJYcRoN7kIjYjZYpkZ5O59A-1764766957-1.0.1.1-8OPlHjyqiioaBfHRcsnpZjxrH1DX0XOj_7eOnvDAaV5SX_K_Z64V.YLSa_pkcEXzkGhLkdezPlSvn87xyeRBr.a43XlJIZVDisbVCD5w_qM;swt=AdYIcCz234cZV4axP+8zf08DFZXA7dBMOxmy5Dd4b3CHgegVKFIp8M2sXL5JXQbzhMChC6dbqzeEc/6flmYnYhirlMo+gvfaYcLJwO6vVIr6zlckyc4ETHpDL46xW2ub90dtd7gh4HMIjIcmDIBJS1Rdt82qLz6i8ujFjxDYU9ialrvzwAKq+6bqDasOlYsyjNLGcQQ=;aps03=ao=1&cf=E&cg=3&cst=36&ct=198&hd=N&lng=32&oty=3&tt=1 bytes&tzi=2;session=lgs=1&ntfr=1;aaat=di=343bc72f-f548-4acc-9619-4bbfe204286b&ts=03-12-2026 12:44:54&v=2&am=0&at=340c263e-076e-4181-88f2-bc9aa432b589&un=luciiferr365&ue=luciiferr365;pstk=BE8998B36A5B4871B744359B6F4E9FD4000004;_cs_id=fd2efe0e-2217-acc3-ead0-7d0ca60e2ca0.1764765796.1.1764765802.1764765796.1684334019.1798929796477;_cs_s=2.0.0.1764767602518;rmbs=3;_cs_c=1;usdi=uqid=79CDAC78-FF81-459A-AE3D-C17CA9E8E32A'
            },
            'fanduel': {
                'x_px_authorization': 'FANDUEL_X_PX_AUTHORIZATION',
                'x_px_uuid': 'FANDUEL_X_PX_UUID',
                'x_px_mobile_sdk_version': 'FANDUEL_X_PX_MOBILE_SDK_VERSION',
                'cookies': 'FANDUEL_COOKIES'
            },
            # Real working values extracted from curl files
            'fanduel_defaults': {
                'x_px_authorization': '3:421de323f9b30faed1e93bb15a7b7b5999a94440739f23e088e0b5a31034ada7:ktGXFCCdwZsEipVJzv7kR2k6f4xIEcsOh88MVLp9xasATV+Rrx7FDRJtGI4qDQpxZcQl353MjGWcG3E/Pu8JAQ==:1000:QPPSuby3X9A9ZoAGBfyl531GET5XdNQrjPJvp4PIcMr5sKgV2EOkfaOCUUDmwG1bR6H5wqGrGwHcIJ3kQ96ohQnPV1Cd/O8J7iZFs9W1GjhgGxu793/ZyUKl9DoUbhkBOHi6wN+dPJEIsCHvutawrJW8k9HNthhSu6ENFR2j47JJEtuazxwBUI1yx27+tmz8wqVmOYp/SM1l3AJ4MhYB6EKkubPOVJxEy6B5R49grnY=',
                'x_px_uuid': 'ce65bc2a-a476-11f0-97aa-8966379e1fe8',
                'x_px_mobile_sdk_version': '3.2.6',
                'cookies': '_gcl_au=1.1.2000388436.1755290453; amp_device_id=ca91b871-b819-4789-958e-c5a76fe191e3; __ssid=e2099952c9cb29e08ac0a5025721502; __pxvid=f13f1274-7a17-11f0-8bbc-a6dd854b44ac; _pxvid=f0ebf760-7a17-11f0-9658-b3fdd6e896eb'
            },
            'draftkings': {
                'cookies': 'DRAFTKINGS_COOKIES'
            },
            # Real working values extracted from curl files
            'draftkings_defaults': {
                'cookies': 'bm_sv=6591D62A6510B69C8D6751469A5D3F07~YAAQZavWF6Wk4JeZAQAAOIAXth1CAgEepZ0bmE/QHZNI575IKqijGMg9w8DDKtTTqXn67Tkn/E+HgCVHVEQueEoH5OMEcIfiBydLpP35mfNCzC1wdXMc/3wT/sYcEITSyXRNt88A0JxqVO0Pj0/ecHqDudkaPJWVPdnb//SPjMbiFMeNekz/vFhPQTGfxjsXdWHUxT+s8kYrrrDBVGAt90TyQRa62NsYqFP/wO/lIXJOfLpD4YdVjyUY8gOmRf4NH7TBmp4=~1; STE=2025-10-05T21:06:54.3492184Z; ak_bmsc=B5793E25283AE09F1984D31FB117EA2D~000000000000000000000000000000~YAAQZavWFxl54JeZAQAAkX0Wth3PvyvtCTXWZdnC0UMggGWCHMo+QExSCRHEIKV1vRjXrs0vFetYjcPafh22WYy7fu7LtO/XwHwePDXw2JieKyjoJtPQ40oW/fZyQBaWlgU0bU+L0W8xJZBbfM1XDU9pvlqE1UrKOf6D4bl41rZB0L7AebAsg3EybpTNmKRDohnjTLom8PzwZtohSxn6cg0SzFJlzNRW9taHEksxI4JuGRX8iV5hnGLz5Ycz13G764vU7c+D7VIZhalda30wdCJ7c2TsosyTzyDDQzj5QAymykW3DHhb8f116mzYWVP/EN2hc4aiY+LUtfE1qTZsYcRLY4Xirlzbh0VLaiu3QrfBtv4HjBrLFlfmK/avrJCVBaZgJRGJpdOIswxcR/JzW6zSRbnAL1wNxA3IMO9/7mNmrV9mZv3WV0nxOfL2rRLlzK0/IO7B7hg=; _abck=BB2348FA26AF00C89537180F4F73116D~-1~YAAQZKvWF1C0VJaZAQAAY3gWtg5fKKcDk7hT2jB6FLNmmgGXNLycdWM'
            },
            'bovada': {
                'cookies': 'BOVADA_COOKIES'
            },
            # Real working values extracted from curl files
            'bovada_defaults': {
                'cookies': 'TS01890ddd=014b5d5d07ee8fa07fc06df7f93ea847e8efc75fcbf1b6c70bc42bd5113af4669d0ebdbc0810a2d538f61c2997122b8b26470c21aac4e3687d4aa82383c4010eca5358c39ee05970c23cbeaff61945658a38b6ac7a26a7d64612d06d9628c6d4aba69f3fe32d2a93f42411052021805c40c75f62f5; JSESSIONID=59290CD56CDDC14323EAE3E977747667; variant=v:1|lgn:0|dt:m|os:ns|cntry:US|cur:USD|jn:1|rt:o|pb:0; wt_rla=205099820688534%2C4%2C1759518156689; ln_grp=2; odds_format=AMERICAN'
            },
            'novig': {
                # NoVig uses GraphQL, no special auth needed
            },
            'prizepicks': {
                # PrizePicks uses standard API, no special auth needed
            },
            'underdog': {
                # Underdog uses standard API, no special auth needed
            }
        }

        if bookmaker not in credential_mappings:
            logger.warning(f"No credential mapping found for bookmaker: {bookmaker}")
            return {}

        mapping = credential_mappings[bookmaker]
        defaults_key = f"{bookmaker}_defaults"
        defaults = credential_mappings.get(defaults_key, {})

        for cred_key, env_var in mapping.items():
            value = os.getenv(env_var)
            if value:
                credentials[cred_key] = value
            elif cred_key in defaults:
                # Use default value for development
                credentials[cred_key] = defaults[cred_key]
                logger.debug(f"Using default value for {bookmaker}.{cred_key}")
            else:
                logger.debug(f"Missing environment variable for {bookmaker}.{cred_key}: {env_var}")

        return credentials

    def validate_credentials(self, bookmaker: str) -> bool:
        """
        Validate that all required credentials are present for a bookmaker.

        Args:
            bookmaker: Name of the bookmaker

        Returns:
            True if all required credentials are present
        """
        credentials = self.get_bookmaker_credentials(bookmaker)

        # Define required credentials for each bookmaker
        required_credentials = {
            'pinnacle': ['x_api_key'],  # device_uuid optional
            'hardrock': ['cookie'],  # sessiontoken optional
            'propscash': ['token'],
            'rebet': ['api_key', 'bearer'],
            'fliff': ['auth_token', 'cookie'],
            'betr': ['auth_token'],
            'parlayplay': ['bearer'],
            'betonline': ['cookies'],
            'fanatics': ['cookie'],
            'bet365': ['sync_term'],
            'fanduel': ['x_px_authorization', 'x_px_uuid'],  # cookies optional
            'draftkings': ['cookies'],
            'bovada': ['cookies']
        }

        required = required_credentials.get(bookmaker, [])
        missing = [cred for cred in required if cred not in credentials or not credentials[cred]]

        if missing:
            logger.warning(f"Missing required credentials for {bookmaker}: {missing}")
            return False

        return True

    def encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """
        Encrypt credentials for secure storage.

        Args:
            credentials: Dict of credentials to encrypt

        Returns:
            Base64 encoded encrypted string
        """
        json_str = json.dumps(credentials)
        encrypted = self.cipher.encrypt(json_str.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_credentials(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt credentials.

        Args:
            encrypted_data: Base64 encoded encrypted string

        Returns:
            Decrypted credentials dict
        """
        try:
            encrypted = base64.b64decode(encrypted_data)
            decrypted = self.cipher.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"Failed to decrypt credentials: {e}")
            return {}


# Global instance
key_manager = SecureKeyManager()


def get_bookmaker_credentials(bookmaker: str) -> Dict[str, Any]:
    """
    Convenience function to get bookmaker credentials.

    Args:
        bookmaker: Name of the bookmaker

    Returns:
        Dict of credential key -> value
    """
    return key_manager.get_bookmaker_credentials(bookmaker)


def validate_bookmaker_credentials(bookmaker: str) -> bool:
    """
    Convenience function to validate bookmaker credentials.

    Args:
        bookmaker: Name of the bookmaker

    Returns:
        True if all required credentials are present
    """
    return key_manager.validate_credentials(bookmaker)
