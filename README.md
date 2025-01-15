# Language Practice Emailer

## Overview
Language Practice Emailer is a Python project designed to help users practice a new language by sending them emails with words the user struggles with. The project fetches language content from a Google Sheet file (e.g: https://docs.google.com/spreadsheets/d/1e4xSr0ZxLaeDICGxBgR4zbNmDhrN-Yl7Cy7b5e4lT0w/edit?usp=sharing) and compiles it into a structured email format.

## Installation
1. Clone the repository:
    ```
    git clone https://github.com/patrick-stephens-git/language_practice_emailer_llm.git
    ```
2. Navigate to the project directory:
    ```
    cd language_practice_emailer_llm
    ```
3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

## Configuration
1. Create an environment file `.env` in the project root directory with the following structure:
    ```
    SHEET_ID={google_sheet_id}
    EMAIL_ACCOUNT={sending_email_address}
    EMAIL_PASSWORD={sending_email_password}
    EMAIL_RECIPIENTS={email_recipients}
    OPENAI_API_KEY={api_key}
    ```
2. Customize the configuration file with your email credentials and Google Sheet ID.

## Usage
Run the main script to start sending language practice emails.