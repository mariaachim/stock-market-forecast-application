import sqlalchemy
import sqlalchemy_utils
from dotenv import load_dotenv
import os # standard library

load_dotenv()

username = os.getenv("DBUSER")
password = os.getenv("DBPASSWORD")
print(username)

engine = sqlalchemy.create_engine(f"mariadb+mariadbconnector://{username}:{password}@127.0.0.1/")

if not sqlalchemy_utils.database_exists(f"mariadb+mariadbconnector://{username}:{password}@127.0.0.1/cs-nea"):
  sqlalchemy_utils.create_database(f"mariadb+mariadbconnector://{username}:{password}@127.0.0.1/cs-nea")
else:
  print("database exists")