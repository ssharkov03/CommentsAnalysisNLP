import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
SECRET_KEY = os.getenv("SECRET_KEY")
USERNAME = os.getenv("USER_NAME")
PASSWORD = os.getenv("PASS_WORD")
