from dotenv import load_dotenv
import os

load_dotenv()

print("DB_HOST =", os.getenv('DB_HOST'))
print("DB_PORT =", os.getenv('DB_PORT'))
print("DB_USER =", os.getenv('DB_USER'))
print("DB_NAME =", os.getenv('DB_NAME'))
print("DB_PASS =", "*" * len(os.getenv('DB_PASS') or ''))