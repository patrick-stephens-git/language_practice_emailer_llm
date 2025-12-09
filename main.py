from pull_data import get_word
from generate_response import response_generation
from emailer import emailer
from utils.logging_config import setup_logging

def main() -> None: 
    setup_logging()
    sample_word, sample_translation = get_word()
    ai_translation, example_synonyms, example_sentence, word_country_match = response_generation(sample_word)
    emailer(sample_word, sample_translation, ai_translation, example_sentence, example_synonyms, word_country_match)

if __name__ == '__main__':
    main()