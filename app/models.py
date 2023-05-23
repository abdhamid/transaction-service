import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import relationship
from .database import Base


class StatusEnum(enum.Enum):
    CREATED = "Created"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.id"))
    customer = relationship("Customer", backref="transaction")
    amount_requested = Column(Numeric)
    amount_approved = Column(Numeric)
    is_active = Column(Boolean, default=False)
    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, onupdate=func.now())
    deleted_date = Column(DateTime, nullable=True)


class TransactionHistory(Base):
    __tablename__ = "transaction_history"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transaction.id"))
    transaction = relationship("Transaction", backref="transaction_history")
    status = Column(Enum(StatusEnum))
    amount_requested = Column(Numeric)
    amount_approved = Column(Numeric)
    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, onupdate=func.now())
    deleted_date = Column(DateTime, nullable=True)
