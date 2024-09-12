from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DB_USER = 'root'
# DB_PASSWORD = 'admin'
# DB_HOST='localhost'
# DB_DATABASE='grimue'

DB_DATABASE = "db_nu5r8t2x1qj8" 
DB_USER = "db_nu5r8t2x1qj8" 
DB_PASSWORD = "CTSySQTbwyTKCwX2SSYRwCzh" 
DB_HOST = "up-de-fra1-mysql-1.db.run-on-seenode.com "
DB_PORT = 11550

#SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:admin@localhost/seddb' 
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:OkbsUVxCBXECKxHkCJDgkmDtbkvWFVEB@autorack.proxy.rlwy.net:34297/railway"
#SQLALCHEMY_DATABASE_URL = "mysql+pymysql://{}:{}@{}:{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
#print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
