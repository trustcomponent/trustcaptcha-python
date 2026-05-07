import json
from dataclasses import dataclass, field
from uuid import UUID

@dataclass
class VerificationToken:
    verification_id: UUID
    client_failover: bool = False

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
        return cls(
            verification_id=UUID(data['verificationId']),
            client_failover=bool(data.get('clientFailover', False)),
        )
