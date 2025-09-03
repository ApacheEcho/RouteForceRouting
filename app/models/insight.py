from datetime import datetime
from app.models.database import db


class Insight(db.Model):
    """Insight associated with a Route"""
    __tablename__ = "insights"

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey("routes.id"), nullable=False)
    insight_type = db.Column(db.String(80), nullable=True)
    content = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "route_id": self.route_id,
            "insight_type": self.insight_type,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
