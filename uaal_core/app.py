from fastapi import FastAPI
from pydantic import BaseModel
from uaal.uaal_middleware import uaal_gate

app = FastAPI()

class PriceUpdate(BaseModel):
    new_price: int

@app.post("/price/update")
def update_price(req: PriceUpdate):
    decision = uaal_gate(
        agent="pricing-agent",
        action="update_price",
        payload={"new_price": req.new_price},
        model_info={"model": "gpt-4.1", "version": "2025-12-01"},
    )

    return {
        "status": "updated",
        "decision_id": decision.id,
    }
