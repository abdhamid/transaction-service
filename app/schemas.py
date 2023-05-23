from datetime import datetime
from typing import Union
from pydantic import BaseModel

from app.models import StatusEnum


class Transaction(BaseModel):
    id: int
    customer_id: int
    amount_requested: float
    amount_approved: Union[float, None]
    is_active: bool
    created_date: datetime
    updated_date: Union[datetime, None]
    deleted_date: Union[datetime, None]

    class Config:
        orm_mode = True


class TransactionCreate(BaseModel):
    customer_phone: str
    amount_requested: float


class TransactionSubmit(BaseModel):
    transaction_id: int
    amount_requested: Union[float, None]


class TransactionHistory(BaseModel):
    id: int
    transaction_id: int
    status: StatusEnum
    amount_requested: float
    amount_approved: Union[float, None]
    created_date: datetime
    updated_date: Union[datetime, None]
    deleted_date: Union[datetime, None]

    class Config:
        orm_mode = True


class TransactionDetail(Transaction):
    latest_status: TransactionHistory


class TransactionHistoryCreate(BaseModel):
    transaction_id: int
    amount_requested: Union[float, None]
    amount_approved: Union[float, None]
    status: Union[StatusEnum, None]


class Customer(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    created_date: datetime
    updated_date: datetime

    class Config:
        orm_mode = True
