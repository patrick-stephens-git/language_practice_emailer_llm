from datetime import datetime, time
from pull_data import get_word
from generate_response import response_generation
from emailer import emailer
from utils.logging_config import setup_logging

ACTIVE_WINDOW_START: time = time(7, 0) # 7:00 AM local
ACTIVE_WINDOW_END: time = time(23, 5) # 10:05 PM local

def main() -> None:
    now: time = datetime.now().time() # Local machine time; checked before any other work, including logging setup
    if not (ACTIVE_WINDOW_START <= now <= ACTIVE_WINDOW_END):
        print(f"Outside active window ({ACTIVE_WINDOW_START}-{ACTIVE_WINDOW_END}); current local time is {now}. Skipping.")
        return

    setup_logging() # Initialize logging
    sample_word, sample_translation = get_word() # Fetch a random word and its spreadsheet translation
    ai_translation, example_synonyms, example_sentence, word_country_match, is_common, where_to_hear = response_generation(sample_word) # Generate all AI responses
    emailer(sample_word, sample_translation, ai_translation, example_sentence, example_synonyms, word_country_match, is_common, where_to_hear) # Send the email

if __name__ == '__main__':
    main()
