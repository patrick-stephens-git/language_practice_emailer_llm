from dotenv import load_dotenv
import os

# Define the global variables
target_country = "Mexico"
target_language = "Spanish"

# If you have a focus on a specific language concept, you can set it here
target_focus = "subjunctive mood" # ex: "imperfect conjugation"; leave empty if no focus: ""
focus_weight = "15%" # ex: "20%" (always use N% format); leave empty if no focus: ""

# Load the environment variables
load_dotenv('.env')
sender_email_account: str = os.getenv("EMAIL_ACCOUNT")
sender_email_password: str = os.getenv("EMAIL_PASSWORD")
email_recipients: str =  os.getenv("EMAIL_RECIPIENTS")
sheet_id: str =  os.getenv("SHEET_ID")
openai_api_key: str = os.getenv("OPENAI_API_KEY")