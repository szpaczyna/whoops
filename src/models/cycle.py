from datetime import datetime
from typing import Dict

from src.ext.database import db


class WhoopCycle(db.Model):
    __tablename__ = "whoop_cycle"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    start = db.Column(db.DateTime(timezone=True), nullable=False)
    end = db.Column(db.DateTime(timezone=True), nullable=True)
    timezone_offset = db.Column(db.String(10), nullable=False)
    score_state = db.Column(db.String(15), nullable=False)

    # Score fields
    strain = db.Column(db.Float, nullable=False)
    kilojoule = db.Column(db.Float, nullable=False)
    avg_heart_rate = db.Column(db.Integer, nullable=False)
    max_heart_rate = db.Column(db.Integer, nullable=False)
    step_count = db.Column(db.Integer, nullable=True)

    @classmethod
    def from_json(cls, data: dict) -> "WhoopCycle":
        score = data.get("score") or {}

        return cls(
            id=data["id"],  # type: ignore
            user_id=data.get("user_id"),  # type: ignore
            timestamp=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),  # type: ignore
            updated_at=datetime.fromisoformat(  # type: ignore
                data["updated_at"].replace("Z", "+00:00")
            ),
            start=datetime.fromisoformat(data["start"].replace("Z", "+00:00")),  # type: ignore
            end=datetime.fromisoformat(data["end"].replace("Z", "+00:00"))  # type: ignore
            if data.get("end")
            else None,
            timezone_offset=data["timezone_offset"],  # type: ignore
            score_state=data["score_state"],  # type: ignore
            strain=score.get("strain", 0),  # type: ignore
            kilojoule=score.get("kilojoule", 0),  # type: ignore
            avg_heart_rate=score.get("average_heart_rate", 0),  # type: ignore
            max_heart_rate=score.get("max_heart_rate", 0),  # type: ignore
            step_count=data.get("step_count"),  # type: ignore
        )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.timestamp.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "start": self.start.isoformat(),
            "end": self.end.isoformat() if self.end else None,
            "timezone_offset": self.timezone_offset,
            "score_state": self.score_state,
            "score": {
                "strain": self.strain,
                "kilojoule": self.kilojoule,
                "average_heart_rate": self.avg_heart_rate,
                "max_heart_rate": self.max_heart_rate,
            },
            "step_count": self.step_count,
        }
