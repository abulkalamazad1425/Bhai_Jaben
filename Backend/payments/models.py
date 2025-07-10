from sqlalchemy import Column, String, Numeric, Enum, ForeignKey
from db import Base
import enum

class StatusEnum(str, enum.Enum):
    initiated="initiated"; success="success"; failed="failed"; canceled="canceled"

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True)
    tran_id = Column(String, unique=True)
    user_id = Column(String, ForeignKey("auth.users.id"))
    amount = Column(Numeric)
    status = Column(Enum(StatusEnum))
