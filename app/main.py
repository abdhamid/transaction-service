from typing import Union
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, mapper
from .database import get_db, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/transaction", response_model=schemas.Transaction)
def create_transaction(transaction_request: schemas.TransactionCreate,
                       db: Session = Depends(get_db)):
    customer = crud.get_customer_by_phone_number(
        db, transaction_request.customer_phone)
    # if customer is None:
    #     raise HTTPException(status_code=404, detail="User not found")
    return crud.create_transaction(
        db, transaction_request=transaction_request, customer_id=customer.id)


@app.get("/transactions", response_model=Union[list[schemas.TransactionDetail], schemas.TransactionDetail])
def get_transactions(transaction_id: int = None,
                     limit: int = 100,
                     offset: int = 0,
                     sort_by: str = None,
                     db: Session = Depends(get_db)):
    if transaction_id is not None:
        transaction = crud.get_transaction_by_id(
            db, transaction_id=transaction_id)
        latest_status = crud.get_latest_transaction_history(
            db, transaction_id=transaction_id)
        return mapper.transaction_to_transaction_detail(transaction, latest_status)

    transactions = crud.get_transactions(
        db, limit=limit, offset=offset, sort_by=sort_by)
    transactions_detail = []
    for i in transactions:
        latest_status = crud.get_latest_transaction_history(
            db, transaction_id=i.id)
        transactions_detail.append(
            mapper.transaction_to_transaction_detail(i, latest_status))
    return transactions_detail


@app.put("/transaction/submit", response_model=schemas.Transaction)
def submit_transaction(transaction_id: int,
                       amount_requested: float = None,
                       db: Session = Depends(get_db)):
    return crud.submit_transaction(db=db, transaction_id=transaction_id, amount_requested=amount_requested)


@app.put("/transaction/approve", response_model=schemas.Transaction)
def approve_transaction(transaction_id: int,
                        amount_approved: float,
                        db: Session = Depends(get_db)):
    is_approved_or_rejected = crud.get_transaction_history_by_id_and_status(db, transaction_id)
    if is_approved_or_rejected:
        raise HTTPException(status_code=400, detail=f"Transaction with id: \'{transaction_id}\' has been approved/rejected before")
    return crud.approve_transaction(db=db, transaction_id=transaction_id, amount_approved=amount_approved)


@app.put("/transaction/reject", response_model=schemas.Transaction)
def reject_transaction(transaction_id: int,
                       db: Session = Depends(get_db)):
    is_approved_or_rejected = crud.get_transaction_history_by_id_and_status(db, transaction_id)
    if is_approved_or_rejected:
        raise HTTPException(status_code=400, detail=f"Transaction with id: \'{transaction_id}\' has been approved/rejected before")
    return crud.reject_transaction(db=db, transaction_id=transaction_id)


@app.get("/transaction-history", response_model=list[schemas.TransactionHistory])
def get_transaction_history(transaction_id: int, is_unique: bool = False, db: Session = Depends(get_db)):
    return crud.get_transaction_history(transaction_id=transaction_id, is_unique=is_unique, db=db)