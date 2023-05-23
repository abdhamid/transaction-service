from . import models, schemas


def transaction_to_transaction_detail(transaction: models.Transaction, latest_status: schemas.TransactionHistory):
    return schemas.TransactionDetail(
        id=transaction.id,
        customer_id=transaction.customer_id,
        amount_requested=transaction.amount_requested,
        amount_approved=transaction.amount_approved,
        is_active=transaction.is_active,
        created_date=transaction.created_date,
        updated_date=transaction.updated_date,
        deleted_date=transaction.deleted_date,
        latest_status=latest_status
    )


def transaction_to_transaction_history_create(transaction: models.Transaction, status: models.StatusEnum):
    return schemas.TransactionHistoryCreate(
        amount_requested=transaction.amount_requested,
        amount_approved=transaction.amount_approved,
        transaction_id=transaction.id,
        status=status)

def transaction_history_schema_to_model(transaction_history: schemas.TransactionHistoryCreate):
    return models.TransactionHistory(
        amount_requested=transaction_history.amount_requested,
        amount_approved=transaction_history.amount_approved,
        transaction_id=transaction_history.transaction_id,
        status=transaction_history.status)