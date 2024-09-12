"""
- AUTHENTICATION
- EDIT MARKETS RETURN NULL INSTEAD OF EMPTY STRING
- EDIT PROFILE OPTION

"""



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from router import router
import models
from database import engine


app = FastAPI()

# update database:
models.Base.metadata.create_all(bind=engine)

app.include_router(router, tags=['gm router'])

# CORS section #NOTE: DOES NOT WORK
# ===========================
# Do not use http://localhost!
# origins = [
#     "http://127.0.0.1:8080",
#     "http://localhost:8080",
#     "https://hny6y5.deta.dev",
#     "https://vigorous-goldwasser-89e64d.netlify.app/",
#     "https://neue.grimm-mueller.de/",
#     "https://grimm-mueller.de/",
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

