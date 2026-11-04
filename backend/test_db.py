from app.database import db

# test 컬렉션에 문서 하나 써보기
db.collection("test").document("hello").set({"message": "Firestore 연결 성공!"})
print("쓰기 완료")

# 다시 읽어보기
doc = db.collection("test").document("hello").get()
print("읽기 결과:", doc.to_dict())