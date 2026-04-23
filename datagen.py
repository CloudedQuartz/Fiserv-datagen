import json
import random
import argparse
from datetime import datetime, timedelta

def generate_normal_transactions(base_time, payer_id=None):
    """Generate normal background transactions."""
    transactions = []
    merchants = ["AMAZON", "FLIPKART", "ZOMATO", "UBER", "LOCAL_STORE"]
    locations = ["Delhi", "Mumbai", "Bangalore", "Pune"]
    
    # 5 normal users doing normal things over an hour
    for _ in range(50):
        t = {
            "payer_id": payer_id if payer_id else f"USER_{random.randint(100, 105)}",
            "payee_id": random.choice(merchants),
            "amount": random.randint(100, 2000),
            "timestamp": (base_time + timedelta(minutes=random.randint(0, 60))).isoformat(),
            "location": random.choice(locations),
            "device_id": "DEVICE_NORMAL"
        }
        transactions.append(t)
    return transactions

def inject_fraud_type_1(base_time):
    """Chain A: Velocity & High Value Attack.
    Rule Trigger: > 10 tx in 5 mins AND ₹10,000+ in < 1 min window.
    """
    transactions = []
    attack_time = base_time + timedelta(minutes=15)
    for i in range(12):
        amt = 15000 if i == 11 else random.randint(10, 50)  # The 12th tx is the massive one
        t = {
            "payer_id": "HACKED_USER_999",
            "payee_id": "SHADY_MERCHANT_XYZ",
            "amount": amt,
            "timestamp": (attack_time + timedelta(seconds=i*20)).isoformat(),  # Every 20 seconds
            "location": "Delhi",
            "device_id": "DEVICE_999"
        }
        transactions.append(t)
    return transactions

def inject_fraud_type_2(base_time):
    """Chain B: Device Change + New Merchant + High Amount.
    Normal transaction first to establish baseline state, then attack 20 mins later.
    """
    transactions = []
    # Normal transaction first to establish baseline state
    transactions.append({
        "payer_id": "USER_777",
        "payee_id": "ZOMATO",
        "amount": 300,
        "timestamp": (base_time + timedelta(minutes=10)).isoformat(),
        "location": "Mumbai",
        "device_id": "IPHONE_OLD"
    })
    # The attack: 20 minutes later, new device, huge amount, unknown merchant
    transactions.append({
        "payer_id": "USER_777",
        "payee_id": "UNKNOWN_CRYPTO_EXCHANGE",
        "amount": 45000,
        "timestamp": (base_time + timedelta(minutes=30)).isoformat(),
        "location": "Mumbai",
        "device_id": "ANDROID_NEW_THIEF"
    })
    return transactions

def inject_fraud_type_3(base_time):
    """Chain C: The Midnight Run.
    Rule Trigger: Unusual hour.
    """
    return [{
        "payer_id": "USER_444",
        "payee_id": "GAMING_SITE",
        "amount": 8000,
        "timestamp": "2026-02-11T03:15:00",  # 3:15 AM
        "location": "Bangalore",
        "device_id": "DEVICE_444"
    }]

def generate_dataset(fraud_types=None, payer_id=None):
    transactions = []
    base_time = datetime(2026, 2, 10, 12, 0, 0)
    
    # Generate normal background transactions
    transactions.extend(generate_normal_transactions(base_time, payer_id))
    
    # Inject fraudulent transactions based on selected types
    if fraud_types:
        if 1 in fraud_types:
            transactions.extend(inject_fraud_type_1(base_time))
        if 2 in fraud_types:
            transactions.extend(inject_fraud_type_2(base_time))
        if 3 in fraud_types:
            transactions.extend(inject_fraud_type_3(base_time))
    
    # Sort chronologically so the heuristic engine processes them in order
    transactions.sort(key=lambda x: x["timestamp"])
    return transactions

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fraud-type-1", action="store_true", help="Velocity & High Value Attack")
    parser.add_argument("--fraud-type-2", action="store_true", help="Device Change + New Merchant")
    parser.add_argument("--fraud-type-3", action="store_true", help="Midnight Run")
    parser.add_argument("--payer-id", type=str, help="Generate transactions for a specific payer only")
    args = parser.parse_args()
    
    fraud_types = []
    if args.fraud_type_1:
        fraud_types.append(1)
    if args.fraud_type_2:
        fraud_types.append(2)
    if args.fraud_type_3:
        fraud_types.append(3)
    
    # Generate dataset: if no fraud flags, only normal transactions
    dataset = generate_dataset(fraud_types=fraud_types if fraud_types else None, payer_id=args.payer_id)
    for tx in dataset:
        print(json.dumps(tx))