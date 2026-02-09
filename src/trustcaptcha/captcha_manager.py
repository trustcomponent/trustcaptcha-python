import base64
import requests

from .model.verification_result import VerificationResult
from .model.verification_token import VerificationToken


class CaptchaManager:

    @staticmethod
    def get_verification_result(secret_key, base64_verification_token):
        verification_token = CaptchaManager.__get_verification_token(base64_verification_token)
        return CaptchaManager.__fetch_verification_result(verification_token, secret_key)

    @staticmethod
    def __get_verification_token(verification_token):
        try:
            decoded_bytes = base64.b64decode(verification_token, validate=True)
            decoded_string = decoded_bytes.decode('utf-8')
            verification_token_model = VerificationToken.from_json(decoded_string)
            return verification_token_model
        except Exception as e:
            raise VerificationTokenInvalidException() from e

    @staticmethod
    def __fetch_verification_result(verification_token, secret_key):
        url = f"https://api.trustcomponent.com/verifications/{verification_token.verification_id}/assessments"

        headers = {
            "tc-authorization": secret_key,
            "tc-library-language": "python",
            "tc-library-version": "2.0"
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=(3, 5),
                allow_redirects=False
            )
            response.raise_for_status()
            return VerificationResult.from_json(response.json())

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            if status == 403:
                raise SecretKeyInvalidException() from e
            elif status == 404:
                raise VerificationNotFoundException() from e
            elif status == 423:
                raise VerificationNotFinishedException() from e
            else:
                raise RuntimeError(f"Failed to retrieve verification result, response code: {status}") from e

        except Exception as e:
            raise RuntimeError("Failed to retrieve verification result") from e


class SecretKeyInvalidException(Exception):
    pass


class VerificationTokenInvalidException(Exception):
    pass


class VerificationNotFoundException(Exception):
    pass


class VerificationNotFinishedException(Exception):
    pass
