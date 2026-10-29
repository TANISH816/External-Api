
from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel, Field
from typing import Optional
import asyncio
import time
import uuid

app = FastAPI(
    title="Mock External API",
    description="A dummy API server for integration testing",
    version="1.0.0",
)

# In-memory mock database
users = {
    1: {"id": 1, "name": "Aarav", "email": "aarav@example.com"},
    2: {"id": 2, "name": "Priya", "email": "priya@example.com"},
}

products = [
    {"id": 101, "name": "Laptop", "price": 55000},
    {"id": 102, "name": "Mouse", "price": 800},
]

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str

class PaymentRequest(BaseModel):
    amount: float = Field(gt=0)
    currency: str = "INR"
    customer_id: int

@app.get("/")
def home():
    return {
        "message": "Mock External API is running",
        "docs": "/docs",
        "version": "1.0.0",
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

# USERS API

@app.get("/api/users")
def get_users():
    return {"data": list(users.values()), "total": len(users)}

@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    user = users.get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return {"data": user}

@app.post("/api/users", status_code=201)
def create_user(user: UserCreate):
    new_id = max(users.keys(), default=0) + 1
    record = {"id": new_id, **user.model_dump()}
    users[new_id] = record
    return {"message": "User created", "data": record}

@app.put("/api/users/{user_id}")
def update_user(user_id: int, user: UserCreate):
    if user_id not in users:
        raise HTTPException(404, "User not found")
    users[user_id] = {"id": user_id, **user.model_dump()}
    return {"message": "User updated", "data": users[user_id]}

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    if user_id not in users:
        raise HTTPException(404, "User not found")
    deleted = users.pop(user_id)
    return {"message": "User deleted", "data": deleted}

# PRODUCTS API

@app.get("/api/products")
def get_products(
    search: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=100),
):
    result = products
    if search:
        result = [
            p for p in products
            if search.lower() in p["name"].lower()
        ]
    return {"data": result[:limit], "total": len(result)}

@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"data": product}
    raise HTTPException(404, "Product not found")

# SIMULATED PAYMENT API
# This does not process real money.

@app.post("/api/payments", status_code=201)
def create_payment(payment: PaymentRequest):
    return {
        "payment_id": str(uuid.uuid4()),
        "status": "succeeded",
        "amount": payment.amount,
        "currency": payment.currency,
        "customer_id": payment.customer_id,
        "created_at": int(time.time()),
    }

# MOCK AUTHENTICATION

@app.get("/api/private")
def private_endpoint(
    authorization: Optional[str] = Header(default=None)
):
    if authorization != "Bearer test-token":
        raise HTTPException(401, "Invalid or missing token")
    return {"message": "Authenticated successfully"}

# TESTING / FAILURE SCENARIOS

@app.get("/test/status/{status_code}")
def simulate_status(status_code: int):
    if status_code not in [200, 400, 401, 403, 404, 429, 500, 503]:
        raise HTTPException(400, "Unsupported test status code")

    if status_code != 200:
        raise HTTPException(
            status_code=status_code,
            detail=f"Simulated HTTP {status_code} error",
        )

    return {"status": "success", "simulated_code": 200}

@app.get("/test/delay")
async def simulate_delay(
    seconds: float = Query(default=2, ge=0, le=30)
):
    await asyncio.sleep(seconds)
    return {"message": "Delayed response", "delay_seconds": seconds}

@app.get("/test/timeout")
async def simulate_slow_response():
    await asyncio.sleep(60)
    return {"message": "Response after 60 seconds"}
