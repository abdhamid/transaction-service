from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.mapper import *
from . import models, schemas


def get_customer_by_phone_number(db: Session, phone_number: str):
    res = db.query(models.Customer).filter(models.Customer.phone == phone_number).first()
    if res is None:
        raise HTTPException(status_code=400, detail="User not found")
    return res

def get_transaction_by_id(db: Session, transaction_id: int):
    res = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if res is None:
        raise HTTPException(status_code=400, detail="Transaction not found")
    return res


def get_latest_transaction_history(db: Session, transaction_id: int):
    return db.query(models.TransactionHistory).filter(models.TransactionHistory.transaction_id == transaction_id).order_by(models.TransactionHistory.created_date.desc()).first()

def create_transaction_history(db: Session, transaction_history: schemas.TransactionHistoryCreate):
    transaction_history = transaction_history_schema_to_model(transaction_history=transaction_history)
    
    db.add(transaction_history)
    db.commit()
    db.refresh(transaction_history)

def create_transaction(db: Session, transaction_request: schemas.TransactionCreate, customer_id: int):
    has_active_transaction = db.query(models.Transaction).filter(models.Transaction.customer_id == customer_id).filter(models.Transaction.is_active == True).all()
    if has_active_transaction:
        raise HTTPException(status_code=400, detail="Customer has an ongoing transaction")
    
    # create transaction
    transaction = models.Transaction(
        amount_requested=transaction_request.amount_requested, customer_id=customer_id, is_active=True)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # create transaction history
    transaction_history_create = transaction_history_create = transaction_to_transaction_history_create(transaction, models.StatusEnum.CREATED)
    create_transaction_history(db, transaction_history_create)
    return transaction


def submit_transaction(db: Session, transaction_id: int, amount_requested: float = None):
    transaction = get_transaction_by_id(db, transaction_id=transaction_id)
    if amount_requested is not None:
        transaction.amount_requested = amount_requested
    
    transaction_history_create = transaction_history_create = transaction_to_transaction_history_create(transaction, models.StatusEnum.SUBMITTED)
    
    create_transaction_history(db, transaction_history_create)
    return transaction


def get_transaction_history_by_id_and_status(db: Session, transaction_id: int):
    return db.query(models.TransactionHistory).filter(models.TransactionHistory.transaction_id == transaction_id).filter(models.TransactionHistory.status.in_((models.StatusEnum.APPROVED, models.StatusEnum.REJECTED))).all()

def approve_transaction(db: Session, transaction_id: int, amount_approved: float):
    transaction = get_transaction_by_id(db, transaction_id=transaction_id)
    transaction.amount_approved = amount_approved
    transaction.is_active = False

    transaction_history_create = transaction_history_create = transaction_to_transaction_history_create(transaction, models.StatusEnum.APPROVED)
    
    
    create_transaction_history(db, transaction_history_create)
    return transaction


def reject_transaction(db: Session, transaction_id: int):
    transaction = get_transaction_by_id(db, transaction_id=transaction_id)
    transaction.is_active = False

    transaction_history_create = transaction_to_transaction_history_create(transaction, models.StatusEnum.REJECTED)
    
    create_transaction_history(db, transaction_history_create)
    return transaction


def get_transactions(db: Session, limit: int = 100, offset: int = 0, sort_by: str = None):
    if sort_by == "desc":
        return db.query(models.Transaction).order_by(models.Transaction.id.desc()).offset(offset).limit(limit).all()
    else:
        return db.query(models.Transaction).order_by(models.Transaction.id.asc()).offset(offset).limit(limit).all()


def get_transaction_history(db: Session, transaction_id: int, is_unique: bool):
    if is_unique:
        subq = db.query(models.TransactionHistory.transaction_id,
                        func.max(models.TransactionHistory.created_date).label('maxdate')
                        ).group_by(models.TransactionHistory.status, models.TransactionHistory.transaction_id).subquery('t2')
        
        query = db.query(models.TransactionHistory).join(
            subq, and_(
            models.TransactionHistory.transaction_id == subq.c.transaction_id,
            models.TransactionHistory.created_date == subq.c.maxdate
            )
        ).filter(models.TransactionHistory.transaction_id == transaction_id).all()
        
        return query
    return db.query(models.TransactionHistory).filter(models.TransactionHistory.transaction_id == transaction_id).order_by(models.TransactionHistory.created_date.asc()).all()
