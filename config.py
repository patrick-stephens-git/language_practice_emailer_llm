from dotenv import load_dotenv
import os

target_country: str = "Mexico City"
target_language: str = "Spanish"
student_primary_language: str = "English"

focus_weight: float = 0.4 # probability a focus concept is applied; 0.0 disables focus entirely
target_focus_list: list = ('subjunctive mood',)
passive_se_weight: float = 0.3 # probability the example sentence uses passive se; 0.0 disables it

subject_list: list = ('yo','tú','usted','ustedes','ella','nosotros')
subject_usted_list: list = ('waiter','cashier','bartender','doctor','teacher','manager','boss')
verb_tense_list: list = ('present','preterite','imperfect','future','conditional')

load_dotenv('.env')
sender_email_account: str = os.getenv("EMAIL_ACCOUNT")
sender_email_password: str = os.getenv("EMAIL_PASSWORD")
email_recipients: str =  os.getenv("EMAIL_RECIPIENTS")
sheet_id: str =  os.getenv("SHEET_ID")
openai_api_key: str = os.getenv("OPENAI_API_KEY")