from config import openai_api_key, target_country, target_language, student_primary_language, target_focus, focus_weight, subject_list, subject_usted_list
from utils.logging_config import setup_logging
from langchain_openai import ChatOpenAI
import random
import re

def extract_commonality(text: str) -> str:
    # Extract the location name from "is most common in X" regardless of whether X is quoted
    # e.g., "The word or phrase 'no mames' is most common in Mexico."       -> "mexico"
    # e.g., "The word or phrase 'no mames' is most common in 'Mexico'."     -> "mexico"
    match = re.search(r"is most common in '?([^'.]+)'?\.?\s*$", text.strip(), re.IGNORECASE) # Match location after "is most common in", with or without quotes
    if match:
        text_clean = match.group(1).strip().lower() # Extract and normalize the matched location name
    else:
        text_clean = text.strip().lower() # Fallback: normalize the whole text
    return text_clean

def get_sample_sentence_subject() -> str:
    sample_sentence_subject: str = random.choice(subject_list) # Randomly select an item from the list
    if sample_sentence_subject == 'usted':
        usted_subject: str = random.choice(subject_usted_list) # Randomly select a profession for usted
        sample_sentence_subject = f"{sample_sentence_subject} (who is a {usted_subject})" # Append profession to subject
    return sample_sentence_subject


def response_generation(word: str) -> tuple[str, str, str, str, str, str]:
    # Logging
    logger = setup_logging()

    sample_sentence_subject: str = get_sample_sentence_subject() # Get a random sentence subject

    # Initialize the LLM
    llm = ChatOpenAI(model="gpt-4o-mini",
                     api_key=openai_api_key,
                     temperature=1.2, # Creativity of response (0.0 to 2.0)
                     max_tokens=70, # Max tokens of response length
                     timeout=30, # Max time (in secs) for a response from OpenAI API
                     max_retries=2, # Max retry attempts if request fails (Default is 2)
                     n=1, # Max num of responses to generate (default is 1)
                     presence_penalty=-2.0, # Encourage/Discourage inclusion of new topics in response (default is 0.0; range is -2.0 to 2.0)
                     frequency_penalty=0.0, # Encourage/Discourage inclusion of the same tokens in response (default is 0.0; range is -2.0 to 2.0)
                     streaming=False # stream response back from OpenAI API (default is False)
                     )

    ###############################################
    ###############################################
    # LLM Prompt to determine if word is commonly spoken in all Spanish-speaking countries or Mexico, or Spain, etc...
    word_country_match_input: str = f"""
        # Role:
        - You are a teacher of the {target_language} language.
        - You are helping a student learn {target_language}.

        # Goal Completion Guidelines:
        - You will be given a Target Word or Phrase. Use the Target Word or Phrase to complete your tasks.

        # Target Word or Phrase:
        - The student is learning the Target Word or Phrase: '{word}'.

        # Goal:
        Your goal is to complete the following tasks:

        ## Task 1: Determine where the Target Word or Phrase is commonly spoken
        - Determine if the Target Word or Phrase '{word}' is more commonly spoken in:
        -- all Spanish-speaking countries
        -- Mexico
        -- Spain
        -- Columbia
        -- Argentina
        -- Venezuela
        -- Chile
        -- Guatemala
        -- Ecuador
        -- Costa Rica
        -- Puerto Rico
        -- Other
        - A word or phrase is 'commonly spoken' if:
        -- '{word}' is frequently used in everyday conversations by native speakers.
        -- The media (TV, newspapers, radio, internet) frequently uses '{word}'.
        - Answer with the country name or 'Other' if you are uncertain.
        - Provide ONLY the following context depending on your answer: "The word or phrase '{word}' is most common in locationName."
        - Replace 'locationName' with the answer: 'all Spanish-speaking countries' OR an individual country name (e.g: 'Mexico', 'Spain') OR 'Other'.
        - Do NOT provide any other information in your response beyond what is specified above.
        - Do NOT explain your reasoning.
        ---
        # Output Template:
        The word or phrase '{word}' is most common in locationName.
        """
    logger.info(f"{word_country_match_input}")

    word_country_match_response = llm.invoke(word_country_match_input) # Generate LLM response for Word-Country Match
    logger.info(f"{word_country_match_response}")
    word_country_match: str = word_country_match_response.content # Extract text content from response

    ###############################################
    ###############################################
    # LLM Prompt for Double Checking if Word or Phrase is common in Target Country
    word_country_match_check_input: str = f"""
        # Role:
        - You are a teacher of the {target_language} language.
        - You are helping a student learn {target_language}.

        # Goal Completion Guidelines:
        - You will be given a Target Word or Phrase. Use the Target Word or Phrase to complete your tasks.

        # Target Word or Phrase:
        - The student is learning the Target Word or Phrase: '{word}'.

        # Goal:
        Your goal is to complete the following tasks:

        ## Task 1: Determine where the Target Word or Phrase is commonly spoken
        - Determine if the Target Word or Phrase '{word}' is more commonly spoken in:
        -- All Spanish-speaking countries
        -- Mexico
        -- Spain
        -- Columbia
        -- Argentina
        -- Venezuela
        -- Chile
        -- Guatemala
        -- Ecuador
        -- Costa Rica
        -- Puerto Rico
        -- Other
        - A word or phrase is 'commonly spoken' if:
        -- '{word}' is frequently used in everyday conversations by native speakers.
        -- The media (TV, newspapers, radio, internet) frequently uses '{word}'.
        - Answer with the country name or 'Other' if you are uncertain.
        - Provide ONLY the following context depending on your answer: "The word or phrase '{word}' is most common in 'locationName'."
        - Replace 'locationName' with the answer: 'All Spanish-speaking countries' OR an individual country name (e.g: 'Mexico', 'Spain') OR 'Other'.
        - Do NOT provide any other information in your response beyond what is specified above.
        - Do NOT explain your reasoning.
        ---
        # Output Template:
        The word or phrase '{word}' is most common in 'locationName'.
        """
    logger.info(f"{word_country_match_check_input}")

    word_country_match_check_response = llm.invoke(word_country_match_check_input) # Generate LLM response for Word-Country Match Checker
    logger.info(f"{word_country_match_check_response}")
    word_country_match_check: str = word_country_match_check_response.content # Extract text content from response

    ###############################################
    ###############################################
    # Run consistency check immediately so all downstream prompts use the finalized value
    word_country_match_commonality: str = extract_commonality(word_country_match) # Normalize first country response
    word_country_match_check_commonality: str = extract_commonality(word_country_match_check) # Normalize second country response

    if word_country_match_commonality != word_country_match_check_commonality:
        word_country_match = "I am not sure where the word or phrase is most commonly spoken." # Use fallback if responses disagree

    # Extract the agreed location; empty string if uncertain so downstream prompts don't invent a country
    word_country_match_location: str = extract_commonality(word_country_match) if word_country_match != "I am not sure where the word or phrase is most commonly spoken." else "" # Only extract location when we have a confident answer

    ###############################################
    ###############################################
    # LLM Prompt to get the English translation of the word
    translation_input: str = f"""
        # Role:
        - You are a teacher of the {target_language} language.
        - You are helping a student learn {target_language}.

        # Goal Completion Guidelines:
        - You will be given a Target Word or Phrase. Use the Target Word or Phrase to complete your tasks.

        # Target Word or Phrase:
        - The student is learning the Target Word or Phrase: '{word}'.

        # Goal:
        Your goal is to complete the following tasks:

        ## Task 1: Provide the Meaning of the Target Word or Phrase
        - Provide an {student_primary_language} meaning of the Target Word or Phrase '{word}' in {target_country}.
        - Replace ai_translation with this {student_primary_language} meaning.
        - Limit your response to ONLY the {student_primary_language} meaning of the Target Word or Phrase.
        - Respond only with the ai_translation. Do not respond with any additional information.
        - Do NOT explain your reasoning.
        ---
        # Output Template:
        ai_translation
        """
    logger.info(f"{translation_input}")

    translation_response = llm.invoke(translation_input) # Generate LLM response for AI translation
    logger.info(f"{translation_response}")
    ai_translation: str = translation_response.content # Extract text content from response

    ###############################################
    ###############################################
    # LLM Prompt to determine if word is common in everyday speech in target country
    is_common_input: str = f"""
        # Role:
        - You are a teacher of the {target_language} language.
        - You are helping a student learn {target_language}.

        # Goal Completion Guidelines:
        - You will be given a Target Word or Phrase. Use the Target Word or Phrase to complete your tasks.

        # Target Word or Phrase:
        - The student is learning the Target Word or Phrase: '{word}'.

        # Goal:
        Your goal is to complete the following tasks:

        ## Task 1: Determine if the Target Word or Phrase is common in everyday speech in {target_country}
        - Determine if '{word}' is commonly used in everyday speech by native speakers in {target_country}.
        - A word or phrase is 'common in everyday speech' if ANY of the following are true:
        -- '{word}' is frequently used in casual conversations by native speakers in {target_country}.
        -- You would regularly hear '{word}' spoken on the street, at home, or among friends in {target_country}.
        -- '{word}' is a commonly used slang term or informal expression in {target_country}.
        - Respond ONLY with 'Yes' or 'No'.
        - Do NOT explain your reasoning.
        ---
        # Output Template:
        Yes/No
        """
    logger.info(f"{is_common_input}")

    is_common_response = llm.invoke(is_common_input) # Generate LLM response for everyday commonality check
    logger.info(f"{is_common_response}")
    is_common: str = is_common_response.content.strip() # Extract and trim text content from response

    ###############################################
    ###############################################
    # LLM Prompt for Double Checking if word is common in everyday speech in target country
    is_common_check_input: str = f"""
        # Role:
        - You are a native speaker of {target_language} from {target_country}.
        - You are helping a student learn {target_language}.

        # Goal Completion Guidelines:
        - You will be given a Target Word or Phrase. Use the Target Word or Phrase to complete your tasks.

        # Target Word or Phrase:
        - The student is learning the Target Word or Phrase: '{word}'.

        # Goal:
        Your goal is to complete the following tasks:

        ## Task 1: Determine if the Target Word or Phrase is common in everyday speech in {target_country}
        - Determine if '{word}' is commonly used in everyday speech by native speakers in {target_country}.
        - A word or phrase is 'common in everyday speech' if ANY of the following are true:
        -- '{word}' is frequently used in casual conversations by native speakers in {target_country}.
        -- You would regularly hear '{word}' spoken on the street, at home, or among friends in {target_country}.
        -- '{word}' is a commonly used slang term or informal expression in {target_country}.
        - Respond ONLY with 'Yes' or 'No'.
        - Do NOT explain your reasoning.
        ---
        # Output Template:
        Yes/No
        """
    logger.info(f"{is_common_check_input}")

    is_common_check_response = llm.invoke(is_common_check_input) # Generate LLM response for everyday commonality double-check
    logger.info(f"{is_common_check_response}")
    is_common_check: str = is_common_check_response.content.strip() # Extract and trim text content from response

    if is_common.lower() == is_common_check.lower():
        is_common = is_common # Keep original if both responses agree
    else:
        is_common = "Unsure" # Use fallback if responses disagree

    ###############################################
    ###############################################
    # LLM Prompt to determine where you are most likely to see or hear the word
    where_to_hear_input: str = f"""
        # Role:
        - You are a teacher of the {target_language} language.
        - You are helping a student learn {target_language}.

        # Goal Completion Guidelines:
        - You will be given a Target Word or Phrase. Use the Target Word or Phrase to complete your tasks.

        # Target Word or Phrase:
        - The student is learning the Target Word or Phrase: '{word}'.

        # Goal:
        Your goal is to complete the following tasks:

        ## Task 1: Describe where a student is most likely to see or hear '{word}'
        - You have already determined that '{word}' is common in everyday speech in {target_country}: {is_common}.
        - You have already determined that '{word}' is most commonly spoken in: {word_country_match_location}.
        - If '{word}' IS common in {target_country}: describe the most common context(s) where it is seen or heard there.
        - If '{word}' is NOT common in {target_country}: do NOT invent a {target_country} context. Instead, describe the context(s) where it is seen or heard in {word_country_match_location}.
        - Examples of contexts: 'in informal conversations with friends', 'in formal business settings', 'in written literature', 'on TV news broadcasts', 'in religious settings'.
        - Respond with 1 short sentence. Do NOT force a {target_country} context if the word is not used there.
        - Respond using ONLY {student_primary_language}.
        - Do NOT explain your reasoning.
        ---
        # Output Template:
        contextSentence
        """
    logger.info(f"{where_to_hear_input}")

    where_to_hear_response = llm.invoke(where_to_hear_input) # Generate LLM response for where to hear the word
    logger.info(f"{where_to_hear_response}")
    where_to_hear: str = where_to_hear_response.content # Extract text content from response

    ###############################################
    ###############################################
    # LLM Prompt for Synonym Generation
    sample_synonym_input: str = f"""
        # Role:
        - You were born and raised in {target_country}.
        - You are a teacher of the {target_language} language.
        - You are helping a student learn {target_language}.

        # Goal Completion Guidelines:
        - You will be given a Target Word or Phrase. Use the Target Word or Phrase to complete your tasks.

        # Target Word or Phrase:
        - The student is learning the Target Word or Phrase: '{word}'.

        # Goal:
        Your goal is to complete the following tasks:

        ## Task 1: Gather a list of Synonyms for the Target Word or Phrase more commonly used in the {target_country}.
        - Provide a list of Synonyms for the Target Word or Phrase '{word}' that are more commonly used in {target_country}.
        - Do NOT include Synonyms that are not commonly used in {target_country}.
        - Rank the Synonyms in order of most commonly used to least commonly used in {target_country}.
        - Respond only with the list of Synonyms. Do not respond with any additional information.
        ---
        # Output Template:
        Synonyms used in {target_country}: Synonym1, Synonym2, ... SynonymN.
        """
    logger.info(f"{sample_synonym_input}")

    sample_synonym_response = llm.invoke(sample_synonym_input) # Generate LLM Sample Synonym response
    logger.info(f"{sample_synonym_response}")
    example_synonyms: str = sample_synonym_response.content # Extract text content from response

    ###############################################
    ###############################################
    # LLM Prompt for Sample Sentence Generation
    focus_line: str = f"            - You have a {focus_weight} chance of writing a Sample Sentence that helps the student learn about {target_focus}.\n" if target_focus != "" else "" # Include focus instruction only when a focus topic is configured
    sample_sentence_input: str = f"""
            # Role:
            - You were born and raised in {target_country}.
            - You are a teacher of the {target_language} language.
            - You are helping a student learn {target_language}.

            # Goal Completion Guidelines:
            - You will be given a Target Word. Use the Target Word to complete your tasks.

            # Target Word:
            - The student is learning the Target Word: '{word}'.

            # Goal:
            Your goal is to complete the following tasks:

            ## Task 1: Write a Sample Sentence
            - Write the student a Sample Sentence using '{word}' in the {target_language} language as you would use it in a normal conversation.
            - Emphasize common use cases of '{word}' within {target_country}.
            - Make the Subject of the Sample Sentence: '{sample_sentence_subject}'.
            - The Sample Sentence should represent as if you were speaking directly to OR about the subject.
{focus_line}            - Respond only with the sample sentence. Do not respond with any additional information.
            ---
            # Output Template:
            - SampleSentence.
            """
    logger.info(f"{sample_sentence_input}")

    sample_sentence_response = llm.invoke(sample_sentence_input) # Generate LLM Sample Sentence response
    logger.info(f"{sample_sentence_response}")
    example_sentence: str = sample_sentence_response.content # Extract text content from response

    return ai_translation, example_synonyms, example_sentence, word_country_match, is_common, where_to_hear

if __name__ == '__main__':
    # word: str = "coger" # Example for "Most common in Spain"
    # word: str = "ordenador" # Example for "Most common in Spain"
    # word: str = "patata" # Example for "Most common in Spain"
    # word: str = "joder" # Example for "Most common in Spain"
    # word: str = "choclo" # Example for "Most common in Argentina"
    # word: str = "pileta" # Example for "Most common in Argentina"
    # word: str = "recoger" # Example for "Most common in All Spanish-speaking countries"
    # word: str = "sudor" # Example for "Most common in All Spanish-speaking countries"
    # word: str = "cima" # Example for "Most common in All Spanish-speaking countries"
    # word: str = "acechar" # Example for "Most common in All Spanish-speaking countries"
    # word: str = "embargar" # Example for "Most common in All Spanish-speaking countries"
    # word: str = "verga"  # Example for "Most common in Mexico"
    # word: str = "no mames" # Example for "Most common in Mexico"
    # word: str = "neta" # Example for "Most common in Mexico"
    # word: str = "chido" # Example for "Most common in Mexico"
    # word: str = "a menos que"
    # word: str = "al paracer"
    # word: str = "en cuanto"
    # word: str = "por cierto"
    # word: str = "así como"
    # word: str = "a más tardar"
    word: str = "daltónico"
    # word: str = "tajar" # Example for "Most common in Other"
    # word: str = "asdfsafsd" # Example for "Most common in Other"
    # word: str = "xxx" # Example for "Most common in Other"
    # word: str = "asolar"
    # word: str = "onza"
    # word: str = "en pos"
    # word = "qué anda"
    ai_translation, example_synonyms, example_sentence, word_country_match, is_common, where_to_hear = response_generation(word)
    print(ai_translation)
    print(example_synonyms)
    print(example_sentence)
    print(word_country_match)
    print(is_common)
    print(where_to_hear)
