import json
from dataclasses import dataclass, asdict
from uuid import UUID

@dataclass
class VerificationResult:
    captcha_id: UUID
    verification_id: UUID
    verification_passed: bool
    score: float
    decision_type: str
    decision_action: str
    gateway_failover_active: bool
    risk_scoring_enabled: bool
    minimal_data_mode_enabled: bool
    origin: str
    ip_address: str
    country_code: str
    device_family: str
    operating_system: str
    browser: str
    verification_started_at: str
    verification_finished_at: str
    result_expires_at: str
    result_first_fetched_at: str
    result_last_fetched_at: str

    def to_json(self):
        return json.loads(json.dumps(asdict(self), default=str))

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
        return cls(
            captcha_id=UUID(data['captchaId']),
            verification_id=UUID(data['verificationId']),
            verification_passed=data['verificationPassed'],
            score=data['score'],
            decision_type=data['decisionType'],
            decision_action=data['decisionAction'],
            gateway_failover_active=data['gatewayFailoverActive'],
            risk_scoring_enabled=data['riskScoringEnabled'],
            minimal_data_mode_enabled=data['minimalDataModeEnabled'],
            origin=data['origin'],
            ip_address=data['ipAddress'],
            country_code=data['countryCode'],
            device_family=data['deviceFamily'],
            operating_system=data['operatingSystem'],
            browser=data['browser'],
            verification_started_at=data['verificationStartedAt'],
            verification_finished_at=data['verificationFinishedAt'],
            result_expires_at=data['resultExpiresAt'],
            result_first_fetched_at=data['resultFirstFetchedAt'],
            result_last_fetched_at=data['resultLastFetchedAt'],
        )
