from fastapi import FastAPI

app = FastAPI()

@app.get("/api/status")
def status():
    return {"ok": True, "message": "backend is running!"}
