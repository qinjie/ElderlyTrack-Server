from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

CONN = 'mysql://root:Soe7014Ece@iot-centre-rds.crqhd2o1amcg.ap-southeast-1.rds.amazonaws.com/elderly_track'
connection_string = CONN
# Set echo to true to print all SQL statements
engine = create_engine(connection_string, echo=True)

session_factory = sessionmaker(bind=engine)

Base = declarative_base()
