from app.database import SessionLocal, engine
from app.models import Base, Place
import sys

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

session = SessionLocal()

# Delete places with suspicious names
suspicious_patterns = [
    '국호',  # 국호 37호선 같은 항목
    '급치산',  # 급치산 같은 항목
    '037',  # 라인 번호 같은 항목
    '9999',  # 플레이스홀더
]

deleted_count = 0
for pattern in suspicious_patterns:
    count = session.query(Place).filter(Place.name.like(f'%{pattern}%')).delete()
    if count > 0:
        print(f"패턴 '{pattern}' 삭제: {count}개")
        deleted_count += count

session.commit()
session.close()

print(f"\n총 {deleted_count}개 레코드 삭제 완료")
