from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://admin:admin@localhost:5432/bank_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    emitter_account.balance -= transaction.amount
    receiver_account = db.query(Account).filter(Account.owner == transaction.receiver).first()
    if not receiver_account:
        raise HTTPException(status_code=404, detail="Receiver account not found")
    receiver_account.balance += transaction.amount
    
    db_transaction = Transaction(
        emitter=transaction.emitter,
        receiver=transaction.receiver,
        amount=transaction.amount,
        date=transaction.date
    )
    db.add(db_transaction)
    db.commit()
    
    return {
        "message": "Money sent successfully",
        "transaction_id": db_transaction.id,
        "amount_tnd": transaction.amount  
    }

@app.get("/balance")
def get_balance(account: str = Header(...)):
    db = SessionLocal()
    account_data = db.query(Account).filter(Account.owner == account).first()
    if not account_data:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"balance": account_data.balance}

@app.get("/transactions-history")
def get_transactions_history(emitter: str = Header(...), receiver: str = Header(...), date: datetime = Header(...)):
    db = SessionLocal()
    transactions = db.query(Transaction).filter(
        Transaction.emitter == emitter,
        Transaction.receiver == receiver,
        Transaction.date == date
    ).all()
    return {"transactions": transactions}