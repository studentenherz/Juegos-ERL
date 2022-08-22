from sqlalchemy import Column, Integer, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Answers(Base):
	__tablename__ = 'answers'
	tgid = Column(BigInteger, primary_key=True)
	guess = Column(Integer, nullable=True)