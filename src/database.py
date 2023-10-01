import os
import dotenv
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("postgresql://postgres:sebisdungeon123@db.tpydkxcvvrqbrruhzoaf.supabase.co:5432/postgres")

engine = create_engine(database_connection_url(), pool_pre_ping=True)