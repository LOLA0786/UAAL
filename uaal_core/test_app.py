from fastapi import FastAPI
from uaal.uaal_middleware import uaal_gate

app = FastAPI()
app.middleware("http")(uaal_gate)

print("UAAL middleware attached successfully")
