"""FastAPI application providing the runtime transport layer for Synapse."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .lifespan import lifespan
from .routers import websocket, demo, executions_api, mission_control_api

app = FastAPI(title="Synapse Mission Control API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "synapse-api"}

app.include_router(websocket.router)
app.include_router(demo.router)
app.include_router(executions_api.router)
app.include_router(mission_control_api.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
