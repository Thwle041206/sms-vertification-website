'''
Key features of this implementation:

Transaction Enums:

TransactionType: deposit, withdrawal, purchase
TransactionStatus: pending, completed, failed
TransactionSchema:

Validates amount is positive and rounds to 2 decimals
Requires order_id for purchase transactions
Includes payment details as flexible dictionary
Automatic timestamp management
Transaction Class Methods:

create_transaction: Creates new transaction with validation
update_transaction_status: Updates status and timestamp
get_user_transactions: Retrieves transactions with pagination and filtering
get_transactions_by_order: Gets all transactions for an order
get_total_deposits: Calculates total deposits for a user
get_balance: Computes current user balance from transactions
process_failed_transactions: Auto-fails stale pending transactions
Example Usage:

# Create a deposit transaction
deposit_data = {
    "user_id": "507f1f77bcf86cd799439011",
    "amount": 100.00,
    "type": TransactionType.DEPOSIT,
    "payment_method": "bank_transfer",
    "payment_details": {
        "reference": "BANK-REF-12345",
        "bank_name": "Chase"
    }
}
transaction_id = Transaction.create_transaction(deposit_data)

# Complete the transaction
Transaction.update_transaction_status(transaction_id, TransactionStatus.COMPLETED)

# Get user balance
balance = Transaction.get_balance("507f1f77bcf86cd799439011")

# Get purchase transactions
purchases = Transaction.get_user_transactions(
    user_id="507f1f77bcf86cd799439011",
    transaction_type=TransactionType.PURCHASE
)
'''
from typing import Optional, Dict, Any, List
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
from app.config.database import db

class TransactionType(str, Enum):
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'
    PURCHASE = 'purchase'

class TransactionStatus(str, Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'

class TransactionSchema(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    user_id: str
    amount: float = Field(..., gt=0)
    type: TransactionType
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    payment_method: str = Field(..., min_length=2, max_length=50)
    payment_details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    order_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "amount": 50.00,
                "type": "deposit",
                "payment_method": "credit_card",
                "payment_details": {
                    "card_last4": "4242",
                    "processor": "stripe"
                }
            }
        }

    @validator('amount')
    def round_amount(cls, v):
        """Round amount to 2 decimal places"""
        return round(v, 2)

    @validator('order_id', always=True)
    def validate_order_id(cls, v, values):
        """Validate order_id is required for purchase transactions"""
        if values.get('type') == TransactionType.PURCHASE and not v:
            raise ValueError('order_id is required for purchase transactions')
        return v

class Transaction:
    collection = db['transactions']

    @staticmethod
    def create_transaction(transaction_data: dict) -> str:
        """Create a new transaction record"""
        transaction_data['created_at'] = datetime.now()
        transaction_data['updated_at'] = datetime.now()
        result = Transaction.collection.insert_one(transaction_data)
        return str(result.inserted_id)

    @staticmethod
    def get_transaction_by_id(transaction_id: str) -> Optional[dict]:
        """Get transaction by ID"""
        return Transaction.collection.find_one({'_id': ObjectId(transaction_id)})

    @staticmethod
    def update_transaction_status(transaction_id: str, status: TransactionStatus) -> bool:
        """Update transaction status"""
        result = Transaction.collection.update_one(
            {'_id': ObjectId(transaction_id)},
            {
                '$set': {
                    'status': status.value,
                    'updated_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0

    @staticmethod
    def get_user_transactions(
        user_id: str,
        limit: int = 100,
        skip: int = 0,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None
    ) -> List[dict]:
        """Get transactions for a user with optional filters"""
        query = {'user_id': ObjectId(user_id)}
        
        if transaction_type:
            query['type'] = transaction_type.value
        
        if status:
            query['status'] = status.value

        return list(Transaction.collection.find(query)
            .sort('timestamp', -1)
            .skip(skip)
            .limit(limit))

    @staticmethod
    def get_transactions_by_order(order_id: str) -> List[dict]:
        """Get all transactions associated with an order"""
        return list(Transaction.collection.find({
            'order_id': ObjectId(order_id)
        }).sort('timestamp', -1))

    @staticmethod
    def get_total_deposits(user_id: str) -> float:
        """Get total deposited amount for a user"""
        pipeline = [
            {'$match': {
                'user_id': ObjectId(user_id),
                'type': TransactionType.DEPOSIT.value,
                'status': TransactionStatus.COMPLETED.value
            }},
            {'$group': {
                '_id': None,
                'total': {'$sum': '$amount'}
            }}
        ]
        result = list(Transaction.collection.aggregate(pipeline))
        return result[0]['total'] if result else 0.0

    @staticmethod
    def get_balance(user_id: str) -> float:
        """Calculate current user balance"""
        pipeline = [
            {'$match': {
                'user_id': ObjectId(user_id),
                'status': TransactionStatus.COMPLETED.value
            }},
            {'$group': {
                '_id': '$type',
                'total': {'$sum': '$amount'}
            }}
        ]
        results = list(Transaction.collection.aggregate(pipeline))
        
        deposits = next((r['total'] for r in results if r['_id'] == TransactionType.DEPOSIT.value), 0.0)
        withdrawals = next((r['total'] for r in results if r['_id'] == TransactionType.WITHDRAWAL.value), 0.0)
        purchases = next((r['total'] for r in results if r['_id'] == TransactionType.PURCHASE.value), 0.0)
        
        return deposits - withdrawals - purchases

    @staticmethod
    def process_failed_transactions(hours: int = 24) -> int:
        """Mark pending transactions older than X hours as failed"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        result = Transaction.collection.update_many(
            {
                'status': TransactionStatus.PENDING.value,
                'created_at': {'$lt': cutoff_time}
            },
            {
                '$set': {
                    'status': TransactionStatus.FAILED.value,
                    'updated_at': datetime.now()
                }
            }
        )
        return result.modified_count
