from pull_data import get_word
from generate_response import response_generation
from emailer import emailer
from utils.logging_config import setup_logging

def main() -> None:
    setup_logging() # Initialize logging
    sample_word, sample_translation = get_word() # Fetch a random word and its spreadsheet translation
    ai_translation, example_synonyms, example_sentence, word_country_match, is_common, where_to_hear = response_generation(sample_word) # Generate all AI responses
    emailer(sample_word, sample_translation, ai_translation, example_sentence, example_synonyms, word_country_match, is_common, where_to_hear) # Send the email

if __name__ == '__main__':
    main()
