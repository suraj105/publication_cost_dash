from sqlalchemy import create_engine

# cofig fod db
DB_NAME = "dashdb"
DB_USER = "dashuser"
DB_PASSWORD = "your_password"  # Replace with actual password
DB_HOST = "localhost"
DB_PORT = "5432"

def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
