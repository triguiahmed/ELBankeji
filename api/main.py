from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://admin:admin@host.docker.internal:5432/bank_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
from sqlalchemy import or_

app = FastAPI()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rib = Column(Integer, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, nullable=False)
    owner = Column(String, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    emitter = Column(String, nullable=False)
    receiver = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)

# Pydantic models
class LoanRequest(BaseModel):
    user: str
    amount: float
    date: datetime
class SendMoneyRequest(BaseModel):
    emitter: str
    receiver: str
    amount: float  
    date: datetime


# APIs
@app.post("/request-loan")
def request_loan(loan: LoanRequest):
    db = SessionLocal()
    db_loan = Loan(user_name=loan.user, amount=loan.amount, creation_date=loan.date, status="pending")
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return {"message": "Loan request submitted", "loan_id": db_loan.id}

@app.post("/send-money")
def send_money(transaction: SendMoneyRequest):
    db = SessionLocal()
    
    emitter_account = db.query(Account).filter(Account.owner == transaction.emitter).first()
    if not emitter_account or emitter_account.balance < transaction.amount:
        raise HTTPException(status_code=400, detail=f"Insufficient balance, you can't send the ammount of {transaction.amount} to {transaction.receiver} , You have only {emitter_account.balance}")
    
    emitter_account.balance -= transaction.amount
    receiver_account = db.query(Account).filter(Account.owner == transaction.receiver).first()
    if not receiver_account:
        raise HTTPException(status_code=404, detail="Receiver account not found in the banking system, please check the account name")
    receiver_account.balance += transaction.amount
    
    db_transaction = Transaction(
        emitter=transaction.emitter,
        receiver=transaction.receiver,
        amount=transaction.amount,
        date=transaction.date
    )
    db.add(db_transaction)
    db.commit()
    
    emitter_account = db.query(Account).filter(Account.owner == transaction.emitter).first()
    
    return {
        "message": f"Transaction successful, the ammount of {transaction.amount} has been sent to {transaction.receiver} on  {transaction.date}, Your new balance is {emitter_account.balance}",
    }

@app.get("/balance")
def get_balance(account: str = Header(...)):
    db = SessionLocal()
    account_data = db.query(Account).filter(Account.owner == account).first()
    if not account_data:
        raise HTTPException(status_code=404, detail="Account not found, please check the account name or make sure you are registered in the banking system")
    return {"balance": account_data.balance}

@app.get("/transactions-history")
def get_transactions_history(emitter: str = Header(...)):
    db = SessionLocal()

    transactions = db.query(Transaction).filter(
        or_(
            Transaction.emitter == emitter,
            Transaction.receiver == emitter
        )
    ).all()
    return {"transactions": transactions,
            "count": len(transactions),
            "message": f"Here is the transactions history for {emitter} account, you can check the emitter and receiver names in the transactions"
            }