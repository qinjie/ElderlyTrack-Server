from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

CONN = 'mysql://root:Soe7014Ece@iot-centre-rds.crqhd2o1amcg.ap-southeast-1.rds.amazonaws.com/elderly_track'
connection_string = CONN
engine = create_engine(connection_string)

Session = sessionmaker(bind=engine)

Base = declarative_base()
