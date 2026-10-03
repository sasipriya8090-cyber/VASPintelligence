import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

def get_utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    wallet_address = Column(String(100), index=True, nullable=False)
    blockchain = Column(String(50), default="ethereum", nullable=False)
    status = Column(String(50), default="Active", nullable=False)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="LOW")
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    investigations = relationship("Investigation", back_populates="case", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="case")

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(100), unique=True, index=True, nullable=False)
    blockchain = Column(String(50), default="ethereum", nullable=False)
    wallet_type = Column(String(50), default="Personal")
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=get_utc_now)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    tx_hash = Column(String(100), index=True, nullable=False)
    blockchain = Column(String(50), default="ethereum", nullable=False)
    from_address = Column(String(100), index=True, nullable=False)
    to_address = Column(String(100), index=True, nullable=False)
    amount = Column(Float, default=0.0)
    token = Column(String(20), default="ETH")
    timestamp = Column(DateTime, default=get_utc_now)
    direction = Column(String(20), default="OUTGOING")

    case = relationship("Case", back_populates="transactions")

class VASP(Base):
    __tablename__ = "vasps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(100), nullable=False)
    blockchain = Column(String(50), default="ethereum", nullable=False)
    address = Column(String(100), index=True, nullable=False)
    source = Column(String(100), default="DEMO Registry")
    confidence = Column(Float, default=0.0)

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=get_utc_now)

    case = relationship("Case", back_populates="investigations")
