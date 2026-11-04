import json
from app.database import db

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

batch = db.batch()
col = db.collection("data")
for item in data:
    batch.set(col.document(), item)   # 자동 ID로 문서 생성
batch.commit()
print(f"{len(data)}개 데이터 업로드 완료")