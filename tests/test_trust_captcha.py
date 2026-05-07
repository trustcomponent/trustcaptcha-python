import base64
import json
import unittest
from uuid import UUID

from trustcaptcha.trust_captcha import TrustCaptcha, VerificationTokenInvalidException, \
    VerificationNotFoundException, ApiKeyInvalidException, VerificationNotFinishedException, \
    VerificationResultExpiredException, VerificationResultRetrievalLimitReachedException, \
    ServerUnreachableException

VERIFICATION_VALID = "eyJ2ZXJpZmljYXRpb25JZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCJ9"
VERIFICATION_NOT_FOUND = "eyJ2ZXJpZmljYXRpb25JZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMSJ9"
VERIFICATION_LOCKED = "eyJ2ZXJpZmljYXRpb25JZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMiJ9"
VERIFICATION_EXPIRED = "eyJ2ZXJpZmljYXRpb25JZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMyJ9"
VERIFICATION_LIMIT_REACHED = "eyJ2ZXJpZmljYXRpb25JZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwNCJ9"
VERIFICATION_WITH_UNKNOWN_FIELDS = "eyJ2ZXJpZmljYXRpb25JZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsInVua25vd25GaWVsZCI6ImZvbyIsImFub3RoZXJKdW5rIjo0MiwibmVzdGVkIjp7IngiOjF9fQ=="


VALID_API_KEY = "ak_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


class TestTrustCaptcha(unittest.TestCase):

    def setUp(self):
        self.tc = TrustCaptcha(VALID_API_KEY)

    def test_run_get_verification_result(self):
        result = self.tc.get_verification_result(VERIFICATION_VALID)
        self.assertEqual(result.verification_id, UUID('00000000-0000-0000-0000-000000000000'))

    def test_throw_verification_token_invalid_exception(self):
        with self.assertRaises(VerificationTokenInvalidException):
            self.tc.get_verification_result("invalid-base64")

    def test_throw_verification_token_invalid_when_base64_but_not_json(self):
        # base64("not-a-json")
        with self.assertRaises(VerificationTokenInvalidException):
            self.tc.get_verification_result("bm90LWEtanNvbg==")

    def test_throw_verification_token_invalid_when_json_missing_verification_id(self):
        # base64('{"foo":"bar"}')
        with self.assertRaises(VerificationTokenInvalidException):
            self.tc.get_verification_result("eyJmb28iOiJiYXIifQ==")

    def test_throw_verification_not_found_exception(self):
        with self.assertRaises(VerificationNotFoundException):
            self.tc.get_verification_result(VERIFICATION_NOT_FOUND)

    def test_throw_api_key_invalid_exception(self):
        tc = TrustCaptcha("invalid-key")
        with self.assertRaises(ApiKeyInvalidException):
            tc.get_verification_result(VERIFICATION_VALID)

    def test_throw_verification_not_finished_exception(self):
        with self.assertRaises(VerificationNotFinishedException):
            self.tc.get_verification_result(VERIFICATION_LOCKED)

    def test_throw_verification_result_expired_exception(self):
        with self.assertRaises(VerificationResultExpiredException):
            self.tc.get_verification_result(VERIFICATION_EXPIRED)

    def test_throw_verification_result_retrieval_limit_reached_exception(self):
        with self.assertRaises(VerificationResultRetrievalLimitReachedException):
            self.tc.get_verification_result(VERIFICATION_LIMIT_REACHED)

    def test_tolerates_unknown_fields_in_verification_token(self):
        result = self.tc.get_verification_result(VERIFICATION_WITH_UNKNOWN_FIELDS)
        self.assertEqual(result.verification_id, UUID('00000000-0000-0000-0000-000000000000'))

    def test_throw_server_unreachable_exception(self):
        tc = TrustCaptcha(VALID_API_KEY, api_host="http://localhost:1", connect_timeout_s=0.5, read_timeout_s=0.5)
        with self.assertRaises(ServerUnreachableException):
            tc.get_verification_result(VERIFICATION_VALID)

    def test_user_agent_format(self):
        ua = TrustCaptcha._build_user_agent()
        self.assertTrue(ua.startswith("Trustcaptcha/"))
        decoded = json.loads(base64.b64decode(ua.split("/", 1)[1]))
        self.assertEqual(decoded["language"], "python")
        self.assertEqual(decoded["version"], "3.0.0")


if __name__ == "__main__":
    unittest.main()
