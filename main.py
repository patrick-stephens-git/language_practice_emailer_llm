from pull_data import get_word
from generate_response import get_sample_sentence
from emailer import emailer
from utils.logging_config import setup_logging

def main() -> None: 
    setup_logging()
    sample_word, sample_translation = get_word()
    example_sentence = get_sample_sentence(sample_word, sample_translation)
    emailer(sample_word, sample_translation, example_sentence)

if __name__ == '__main__':
    main()