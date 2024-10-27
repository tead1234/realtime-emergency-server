from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# 서버 실행 명령어 (cmd에서):
# uvicorn main:app --reload