import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from .models import Base, Answers
from .settings import db_name, db_location

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///'+ db_location + '//' + db_name, connect_args={'check_same_thread': False})


if not db_name in os.listdir(db_location):
		print('Not db found, creating one')
		# Create all tables in the engine. This is equivalent to "Create Table"
		# statements in raw SQL.
		Base.metadata.create_all(engine)
else:
		# Bind the engine to the metadata of the Base class so that the
		# declaratives can be accessed through a DBSession instance
		Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. 
s = DBSession()

def has_answered(tgid):
	uin = s.query(Answers).filter(Answers.tgid == tgid).count()
	return uin == 1

def add_answer(tgid, guess):
	if not has_answered(tgid):
		s.add(Answers(tgid=tgid, guess=guess))
		s.commit()

def get_answers():
	res = s.query(Answers.guess, func.count(Answers.guess)).group_by(Answers.guess).all()
	return res

def get_random_with_guess(guess):
	res = s.query(Answers.tgid).filter(Answers.guess == guess).order_by(func.random()).first()
	return res