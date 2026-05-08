import base64
import json
import requests

from .model.verification_result import VerificationResult
from .model.verification_token import VerificationToken

LIBRARY_VERSION = "3.0.0"
LIBRARY_LANGUAGE = "python"
DEFAULT_API_HOST = "https://api.trustcomponent.com"
DEFAULT_CONNECT_TIMEOUT_S = 3.0
DEFAULT_READ_TIMEOUT_S = 5.0


class TrustCaptcha:

    def __init__(self, api_key, *, api_host=DEFAULT_API_HOST,
                 connect_timeout_s=DEFAULT_CONNECT_TIMEOUT_S,
                 read_timeout_s=DEFAULT_READ_TIMEOUT_S,
                 proxy=None):
        if not api_key:
            raise ValueError("api_key must not be empty")
        self._api_key = api_key.strip()
        self._api_host = api_host
        self._connect_timeout_s = connect_timeout_s
        self._read_timeout_s = read_timeout_s
        self._proxy = proxy  # Either a string ("http://host:port") or a dict like {"http": "...", "https": "..."}

    def get_verification_result(self, base64_verification_token):
        verification_token = self._parse_verification_token(base64_verification_token)
        params = {"clientFailover": "true"} if verification_token.client_failover else None
        url = f"{self._api_host}/v2/verifications/{verification_token.verification_id}/results"

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": self._build_user_agent(),
        }

        proxies = None
        if isinstance(self._proxy, str):
            proxies = {"http": self._proxy, "https": self._proxy}
        elif isinstance(self._proxy, dict):
            proxies = self._proxy

        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=(self._connect_timeout_s, self._read_timeout_s),
                allow_redirects=False,
                proxies=proxies,
            )
            response.raise_for_status()
            return VerificationResult.from_json(response.json())

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            if status == 403:
                raise ApiKeyInvalidException() from e
            elif status == 404:
                raise VerificationNotFoundException() from e
            elif status == 423:
                raise VerificationNotFinishedException() from e
            elif status == 410:
                raise VerificationResultExpiredException() from e
            elif status == 412:
                raise ClientReportedServerUnreachableException() from e
            elif status == 429:
                raise VerificationResultRetrievalLimitReachedException() from e
            else:
                raise RuntimeError(f"Failed to retrieve verification result, response code: {status}") from e

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            raise ServerUnreachableException() from e

        except Exception as e:
            raise RuntimeError("Failed to retrieve verification result") from e

    @staticmethod
    def _parse_verification_token(verification_token):
        try:
            decoded_bytes = base64.b64decode(verification_token, validate=True)
            decoded_string = decoded_bytes.decode("utf-8")
            return VerificationToken.from_json(decoded_string)
        except Exception as e:
            raise VerificationTokenInvalidException() from e

    @staticmethod
    def _build_user_agent():
        payload = {"language": LIBRARY_LANGUAGE, "version": LIBRARY_VERSION}
        encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
        return f"Trustcaptcha/{encoded}"


class ApiKeyInvalidException(Exception):
    def __init__(self, message="The provided api key is invalid. Please verify the api key from your captcha settings."):
        super().__init__(message)


class VerificationTokenInvalidException(Exception):
    def __init__(self, message="The verification token is malformed or could not be parsed."):
        super().__init__(message)


class VerificationNotFoundException(Exception):
    def __init__(self, message="No verification could be found for the given verification token."):
        super().__init__(message)


class VerificationNotFinishedException(Exception):
    def __init__(self, message="The verification is not yet completed. Please wait until the user has finished solving the captcha before requesting the result."):
        super().__init__(message)


class VerificationResultExpiredException(Exception):
    def __init__(self, message="The verification result has expired and can no longer be retrieved."):
        super().__init__(message)


class VerificationResultRetrievalLimitReachedException(Exception):
    def __init__(self, message="The verification result has reached its maximum retrieval count and can no longer be retrieved."):
        super().__init__(message)


class FailoverException(Exception):
    pass


class ServerUnreachableException(FailoverException):
    def __init__(self, message="Could not reach the TrustCaptcha server. Please check your network connection and consider implementing a failover mechanism."):
        super().__init__(message)


class ClientReportedServerUnreachableException(FailoverException):
    def __init__(self, message="The client reported it could not reach the TrustCaptcha server, but the gateway has no record of a recent outage. Treat this with caution: a malicious client may be claiming a failover that did not happen."):
        super().__init__(message)
