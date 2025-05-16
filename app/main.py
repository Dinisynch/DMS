from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.document import router as documents_router

app = FastAPI()

@app.get("/")
def home_page():
    return {"message": "DMS Project!"}


app.include_router(auth_router)
app.include_router(documents_router)