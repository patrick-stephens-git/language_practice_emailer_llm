from dotenv import load_dotenv
import os

load_dotenv('.env')
sender_email_account: str = os.getenv("EMAIL_ACCOUNT")
sender_email_password: str = os.getenv("EMAIL_PASSWORD")
email_recipients: str =  os.getenv("EMAIL_RECIPIENTS")
sheet_id: str =  os.getenv("SHEET_ID")
openai_api_key: str = os.getenv("OPENAI_API_KEY")