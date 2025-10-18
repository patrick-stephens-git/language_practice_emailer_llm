from utils.date import today
from utils.logging_config import setup_logging
from config import sender_email_account, sender_email_password, email_recipients
import smtplib
from email.mime.text import MIMEText

def emailer(word, translation, example_sentence, word_country_match) -> None:
    #####################################
    ## Logging:
    logger = setup_logging()
    
    #####################################
    ## Setup Recipients:
    recipients: list[str] = email_recipients.split(",") # Convert email_recipients string to a list

    #####################################
    ## Check for empty variables; if empty then fail, else continue:
    try:
        empty_vars = [var_name for var_name, var in [("sender_email_account", sender_email_account), ("sender_email_password", sender_email_password), ("email_recipients", email_recipients)] if not var]
        if empty_vars:
            raise ValueError(f"Fail: Missing the following email authentication variables: {empty_vars}")
        else:
            logger.info("Pass: All email authentication variables exist.")
    except ValueError as e:
        logger.error(e)  # Logs the error message
        return

    #####################################
    ## Setup Email Content:
    email_subject_line: str = f"{today}: {word}" 
    logger.info(f"Email subject line: {email_subject_line}")
    email_body: str = f"""
    Translation: {translation}<br>
    Used in a sentence: {example_sentence}<br>
    <br>
    Locally spoken? {word_country_match}
    """
    logger.info(f"Email body: {email_body}")

    #####################################
    ## Email configuration:
    message = MIMEText(email_body, "html")
    message["Subject"] = email_subject_line
    message["From"] = sender_email_account
    message["To"] = ','.join(recipients)

    #####################################
    ## Authentication:
    server = smtplib.SMTP_SSL(host = "smtp.gmail.com", port = 465)
    server.login(user = sender_email_account, password = sender_email_password) # The App Password Needed AFTER the Google Update for Less Secure Apps: https://support.google.com/accounts/answer/6010255?hl=en&visit_id=637902943692838375-3915028692&p=less-secure-apps&rd=1#zippy=%2Cif-less-secure-app-access-is-on-for-your-account%2Cupdate-your-app-or-operating-system%2Cuse-more-secure-apps%2Cuse-an-app-password

    #####################################
    ## Send Email:
    server.sendmail(from_addr = sender_email_account, 
                    to_addrs = recipients, 
                    msg = message.as_string())
    server.quit()
    logger.info("Email successfully sent.")

if __name__ == '__main__':
    word: str = "enseñar"
    translation: str = "to teach, to show"
    example_sentence: str = "Me gusta enseñar español a mis amigos porque quiero que aprendan la lengua y la cultura."
    word_country_match: str = "Yes - 'enseñar' is commonly used in Spanish-speaking countries like Spain and Latin America."

    emailer(word, translation, example_sentence, word_country_match)