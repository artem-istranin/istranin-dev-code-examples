from fastapi import FastAPI
from pydantic import BaseModel, Field


class ShippingQuote(BaseModel):
    order_total: int = Field(ge=0)


def shipping_cost(order_total: int) -> int:
    if order_total >= 50:
        return 0
    return 5


app = FastAPI()


@app.post("/shipping-quotes")
async def create_shipping_quote(quote: ShippingQuote) -> dict[str, int]:
    return {"shipping_cost": shipping_cost(quote.order_total)}
