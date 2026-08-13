from fastapi import FastAPI
app = FastAPI()


@app.get("/")
async def hello():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
async def yaan():
    return {"status": "ok"}
