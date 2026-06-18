import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = "sqlite:///payload.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AT_USERNAME = os.getenv("AT_USERNAME")

    AT_API_KEY = os.getenv("AT_API_KEY")

    AT_PRODUCT_NAME = os.getenv("AT_PRODUCT_NAME")

    AT_CURRENCY = os.getenv(
        "AT_CURRENCY",
        "KES"
    )