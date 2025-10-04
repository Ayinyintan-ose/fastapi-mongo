from fastapi import FastAPI
from routes import users, documents

app = FastAPI()

app.include_router(users.router)
app.include_router(documents.router)
