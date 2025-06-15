import json
from dataclasses import dataclass, asdict
from uuid import UUID

@dataclass
class VerificationResult:
    captchaId: UUID
    verificationId: UUID
    score: float
    reason: str
    mode: str
    origin: str
    ipAddress: str
    deviceFamily: str
    operatingSystem: str
    browser: str
    creationTimestamp: str
    releaseTimestamp: str
    retrievalTimestamp: str
    verificationPassed: bool

    def to_json(self):
        return json.loads(json.dumps(asdict(self), default=str))  # Konvertiert UUIDs zu Strings

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
        return cls(
            captchaId=UUID(data['captchaId']),
            verificationId=UUID(data['verificationId']),
            score=data['score'],
            reason=data['reason'],
            mode=data['mode'],
            origin=data['origin'],
            ipAddress=data['ipAddress'],
            deviceFamily=data['deviceFamily'],
            operatingSystem=data['operatingSystem'],
            browser=data['browser'],
            creationTimestamp=data['creationTimestamp'],
            releaseTimestamp=data['releaseTimestamp'],
            retrievalTimestamp=data['retrievalTimestamp'],
            verificationPassed=data['verificationPassed'],
        )
