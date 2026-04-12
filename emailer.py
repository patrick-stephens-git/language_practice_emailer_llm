from utils.date import today
from utils.logging_config import setup_logging
from config import sender_email_account, sender_email_password, email_recipients, target_country
import smtplib
from email.mime.text import MIMEText
import random # Import random module for randomly selecting subject format

def emailer(word: str, translation: str, ai_translation: str, example_sentence: str, example_synonyms: str, word_country_match: str, is_common: str, where_to_hear: str) -> None:
    #####################################
    ## Logging:
    logger = setup_logging()

    #####################################
    ## Setup Recipients:
    recipients: list[str] = email_recipients.split(",") # Convert email_recipients string to a list

    #####################################
    ## Check for empty variables; if empty then fail, else continue:
    try:
        empty_vars = [var_name for var_name, var in [("sender_email_account", sender_email_account), ("sender_email_password", sender_email_password), ("email_recipients", email_recipients)] if not var] # Collect names of any missing auth variables
        if empty_vars:
            raise ValueError(f"Fail: Missing the following email authentication variables: {empty_vars}") # Raise error listing missing variables
        else:
            logger.info("Pass: All email authentication variables exist.")
    except ValueError as e:
        logger.error(e) # Log the error message
        return

    #####################################
    ## Setup Subject Line:
    show_translation_in_subject: bool = random.choice([True, False]) # Randomly decide whether to show word or translation in subject
    logger.info(f"Show translation in subject: {show_translation_in_subject}") # Log which format was selected
    if show_translation_in_subject: # If True, use the English translation as the subject
        email_subject_line: str = f"{today}: {translation}" # Use English translation as the subject
    else: # If False, use the target language word as the subject
        email_subject_line: str = f"{today}: {word}" # Use target language word as the subject
    logger.info(f"Email subject line: {email_subject_line}")

    #####################################
    ## Setup Email Body:
    email_body: str = f"""
    My Translation: {translation}<br>
    AI Translation: {ai_translation}<br>
    Is it common in everyday speech in {target_country}? {is_common}<br>
    Where are you most likely to see or hear {word}? {where_to_hear}<br>
    {word_country_match}<br>
    {target_country} Synonyms: {example_synonyms}<br>
    Ex: {example_sentence}<br>
    """ # Single unified email body format
    logger.info(f"Email body: {email_body}")

    #####################################
    ## Email configuration:
    message = MIMEText(email_body, "html") # Create HTML email message
    message["Subject"] = email_subject_line # Set subject line
    message["From"] = sender_email_account # Set sender address
    message["To"] = ','.join(recipients) # Set recipient addresses

    #####################################
    ## Authentication:
    server = smtplib.SMTP("smtp.gmail.com", 587, local_hostname="localhost") # Connect to Gmail SMTP server
    server.ehlo() # Identify client to server
    server.starttls() # Upgrade connection to TLS
    server.ehlo() # Re-identify after TLS upgrade
    server.login(user = sender_email_account, password = sender_email_password) # Authenticate with App Password

    #####################################
    ## Send Email:
    server.sendmail(from_addr = sender_email_account,
                    to_addrs = recipients,
                    msg = message.as_string()) # Send the email
    server.quit() # Close the SMTP connection
    logger.info("Email successfully sent.")

if __name__ == '__main__':
    word: str = "enseñar" # Target language word
    translation: str = "to teach, to show" # Spreadsheet translation
    ai_translation: str = "to teach" # AI-generated translation
    example_sentence: str = "Me gusta enseñar español a mis amigos." # Example sentence
    example_synonyms: str = "instruir, educar, mostrar." # Example synonyms
    word_country_match: str = "The word or phrase 'enseñar' is most common in all Spanish-speaking countries." # Country match sentence
    is_common: str = "Yes" # Commonality answer
    where_to_hear: str = "You are most likely to hear it in classrooms and educational settings." # Where to hear answer

    emailer(word, translation, ai_translation, example_sentence, example_synonyms, word_country_match, is_common, where_to_hear)
