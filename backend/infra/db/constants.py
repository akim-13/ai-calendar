import os

db_name = os.getenv("POSTGRES_DB", "db")
db_user = os.getenv("POSTGRES_USER", "postgres")
db_password = os.getenv("POSTGRES_PASSWORD", "password")
db_host = os.getenv("POSTGRES_HOST", "postgres")
db_port = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
EVENT_POLYMORPHIC_IDENTITY = "event"
TASK_POLYMORPHIC_IDENTITY = "task"
