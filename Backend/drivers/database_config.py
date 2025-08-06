from db.supabase_client import Supabase
from os import getenv
from dotenv import load_dotenv

load_dotenv()
class DatabaseConfig:
    def __init__(self):
        self.database_url=getenv("DATABASE_URL")
        self.database_key=getenv("DATABASE_KEY")

    def get_client(self):
        return Supabase(self.database_url, self.database_key).get_client()