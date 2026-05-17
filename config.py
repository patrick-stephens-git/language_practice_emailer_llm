from dotenv import load_dotenv
import os

# Define the global variables
target_country: str = "Mexico City"
target_language: str = "Spanish"
student_primary_language: str = "English"

# If you have a focus on a specific language concept, you can set it here
focus_weight: float = 0.4 # 0.0 to 1.0; ex: 0.20 = 20% chance; set to 0.0 if no focus
target_focus_list: list = ('subjunctive mood', 'passive se') # List of language concepts to randomly focus on each run

subject_list: list = ('yo','tú','usted','ustedes','ella','nosotros')
subject_usted_list: list = ('waiter','cashier','bartender','doctor','teacher','manager','boss')
verb_tense_list: list = ('present','preterite','imperfect','future','conditional')

# Load the environment variables
load_dotenv('.env')
sender_email_account: str = os.getenv("EMAIL_ACCOUNT")
sender_email_password: str = os.getenv("EMAIL_PASSWORD")
email_recipients: str =  os.getenv("EMAIL_RECIPIENTS")
sheet_id: str =  os.getenv("SHEET_ID")
openai_api_key: str = os.getenv("OPENAI_API_KEY")