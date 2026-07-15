import json
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Place


SEED_FILE = Path(__file__).parent / "data" / "seoul_places.json"


def seed_places(session: Session) -> None:
    if session.scalar(select(func.count()).select_from(Place)):
        return

    records = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    session.add_all(Place(**record) for record in records)
    session.commit()

