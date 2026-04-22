from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# -----------------------
# 1. Request Schema
# -----------------------
class Transaction(BaseModel):
    user_id: str
    transaction_id: str
    amount: float
    country: str
    device_id: str
    timestamp: datetime


# -----------------------
# 2. Simple In-Memory State (MVP only)
# -----------------------
user_last_device = {}
user_txn_count = {}


# -----------------------
# 3. Fraud Scoring Logic (RULES v1)
# -----------------------
def score_transaction(txn: Transaction):
    score = 0.0
    reasons = []

    # Rule 1: new device
    if txn.user_id in user_last_device:
        if user_last_device[txn.user_id] != txn.device_id:
            score += 0.3
            reasons.append("new_device_detected")
    else:
        score += 0.1
        reasons.append("first_seen_user")

    # Rule 2: high amount
    if txn.amount > 1000:
        score += 0.4
        reasons.append("high_amount")

    # Rule 3: rapid usage
    user_txn_count[txn.user_id] = user_txn_count.get(txn.user_id, 0) + 1
    if user_txn_count[txn.user_id] > 3:
        score += 0.2
        reasons.append("high_frequency")

    # Rule 4: country risk (simple demo rule)
    risky_countries = ["XX", "YY"]
    if txn.country in risky_countries:
        score += 0.3
        reasons.append("risky_country")

    # update memory
    user_last_device[txn.user_id] = txn.device_id

    return min(score, 1.0), reasons


# -----------------------
# 4. API Endpoint
# -----------------------
@app.post("/score")
def score(txn: Transaction):
    risk_score, reasons = score_transaction(txn)

    if risk_score > 0.7:
        decision = "block"
    elif risk_score > 0.4:
        decision = "review"
    else:
        decision = "approve"

    return {
        "transaction_id": txn.transaction_id,
        "risk_score": risk_score,
        "decision": decision,
        "reasons": reasons
        
    }