from config import openai_api_key, target_country, target_language, target_focus, focus_weight, subject_list, subject_usted_list
from utils.logging_config import setup_logging
from langchain_openai import ChatOpenAI
import random
import re

def extract_commonality(text):
    
    # text_clean = text.strip().capitalize().replace("- ", "") # Removes leading/trailing whitespace and newlines, then capitalize first letter; 

    # Extract the quoted location name from the LLM response
    # e.g., "The word or phrase 'cima' is most common in 'all spanish-speaking countries'." 
    #       -> "all spanish-speaking countries"
    match = re.search(r"'([^']+)'\.?$", text.strip())
    if match:
        text_clean = match.group(1).strip().lower()
    else:
        # Fallback: just use the whole text normalized
        text_clean = text.strip().lower()
    # print(text_clean)
    return text_clean

def get_sample_sentence_subject():
    sample_sentence_subject = random.choice(subject_list) # Randomly select an item from the list
    # print(sample_sentence_subject)
    if sample_sentence_subject == 'usted':
        usted_subject = random.choice(subject_usted_list)
        sample_sentence_subject = f"{sample_sentence_subject} (who is a {usted_subject})"
        # print(sample_sentence_subject)
    else:
        pass
    return sample_sentence_subject


def response_generation(word):
    # Logging
    logger = setup_logging()
    
    sample_sentence_subject = get_sample_sentence_subject()

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
    word_country_match_input = f"""
        # Role:
        - You are a teacher of the {target_language} language.
        - You are helping a student learn {target_language}.

        # Goal Completion Guidelines:
        - You will be given a Target Word or Phrase. Use the Target Word or Phrase to complete your tasks.

        # Target Word or Phrase:
        - The student is learning the Target Word or Phrase: '{word}'.
        
        # Goal:
        Your goal is to complete the following tasks:
        - Task 1: Determine where the Target Word or Phrase is commonly spoken

        # Tasks:
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
    logger.info(f"{word_country_match_input}")
    
    # Generate LLM response for Word-Country Match:
    word_country_match_response = llm.invoke(word_country_match_input)
    logger.info(f"{word_country_match_response}") 
    word_country_match = word_country_match_response.content 

    ###############################################
    ###############################################
    # LLM Prompt for Double Checking if Word or Phrase is common in Target Country
    word_country_match_check_input = f"""
        # Role:
        - You are a teacher of the {target_language} language.
        - You are helping a student learn {target_language}.

        # Goal Completion Guidelines:
        - You will be given a Target Word or Phrase. Use the Target Word or Phrase to complete your tasks.

        # Target Word or Phrase:
        - The student is learning the Target Word or Phrase: '{word}'.
        
        # Goal:
        Your goal is to complete the following tasks:
        - Task 1: Determine where the Target Word or Phrase is commonly spoken

        # Tasks:
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

    # Generate LLM response for Word-Country Match Checker:
    word_country_match_check_response = llm.invoke(word_country_match_check_input)
    logger.info(f"{word_country_match_check_response}")
    word_country_match_check = word_country_match_check_response.content

    ###############################################
    ###############################################
    # LLM Prompt to get the English translation of the word
    translation_input = f"""
        # Role:
        - You are a teacher of the {target_language} language.
        - You are helping a student learn {target_language}.

        # Goal Completion Guidelines:
        - You will be given a Target Word or Phrase. Use the Target Word or Phrase to complete your tasks.

        # Target Word or Phrase:
        - The student is learning the Target Word or Phrase: '{word}'.
        
        # Goal:
        Your goal is to complete the following tasks:
        - Task 1: Provide the Meaning of the Target Word or Phrase

        # Tasks:
        ## Task 1: Provide the Meaning of the Target Word or Phrase
        - Provide an English meaning of the Target Word or Phrase '{word}' in {target_country}.
        - Replace englishMeaningText with this English meaning.
        - Limit your response to ONLY the English meaning of the Target Word or Phrase.
        - Respond only with the englishMeaningText. Do not respond with any additional information.
        - Do NOT explain your reasoning.
        ---
        # Output Template:
        englishMeaningText
        """
    logger.info(f"{translation_input}")
    
    # Generate LLM response for Word-Country Match:
    translation_response = llm.invoke(translation_input)
    logger.info(f"{translation_response}") 
    ai_translation = translation_response.content 

    ###############################################
    ###############################################
    skip_countries = [
        "All Spanish-speaking countries", 
        "all spanish-speaking countries", 
        "all spanish speaking countries", 
        "Mexico", 
        "mexico", 
        "Mexico City", 
        "mexico city"
        ]

    # normalize the input for consistent matching
    word_country_match_norm = word_country_match.lower()

    if not any(country in word_country_match_norm for country in skip_countries):
        # LLM Prompt for Synonym Generation
        sample_synonym_input = f"""
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
        - Task 1: Gather a list of Synonyms for the Target Word or Phrase more commonly used in the {target_country}.

        # Tasks:
        ## Task 1: Gather a list of Synonyms for the Target Word or Phrase more commonly used in the {target_country}.
        - Provide a list of Synonyms for the Target Word or Phrase '{word}' that are more commonly used in {target_country}.
        - Respond only with the list of Synonyms. Do not respond with any additional information.
        ---
        # Output Template:
        Synonyms used in {target_country}: Synonym1, Synonym2, ... SynonymN.
        """
        logger.info(f"{sample_synonym_input}")
        
        # Generate LLM Sample Synonym response:
        sample_synonym_response = llm.invoke(sample_synonym_input)
        logger.info(f"{sample_synonym_response}") 
        example_synonyms = sample_synonym_response.content 
        example_sentence = 0 # Pre-setting value because example_sentence is not generated in this branch
    else:
        ###############################################
        ###############################################
        # LLM Prompt for Sample Sentence Generation
        if target_focus != "":
            sample_sentence_input = f"""
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
            - Task 1: Write a Sample Sentence

            # Tasks:
            ## Task 1: Write a Sample Sentence
            - Write the student a Sample Sentence using '{word}' in the {target_language} language as you would use it in a normal conversation.
            - Emphasize common use cases of '{word}' within {target_country}.
            - Make the Subject of the Sample Sentence: '{sample_sentence_subject}'.
            - The Sample Sentence should represent as if you were speaking directly to OR about the subject.
            - You have a {focus_weight} chance of writing a Sample Sentence that helps the student learn about {target_focus}.
            - Respond only with the sample sentence. Do not respond with any additional information.
            ---
            # Output Template:
            - SampleSentence.
            """
        else:
            sample_sentence_input = f"""
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
            - Task 1: Write a Sample Sentence

            # Tasks:
            ## Task 1: Write a Sample Sentence
            - Write the student a Sample Sentence using '{word}' in the {target_language} language as you would use it in a normal conversation.
            - Emphasize common use cases of '{word}' within {target_country}.
            - Make the Subject of the Sample Sentence: '{sample_sentence_subject}'.
            - The Sample Sentence should represent as if you were speaking directly to OR about the subject.
            - Respond only with the sample sentence. Do not respond with any additional information.
            ---
            # Output Template:
            - SampleSentence.
            """
        logger.info(f"{sample_sentence_input}")
    
        # Generate LLM Sample Sentence response:
        sample_sentence_response = llm.invoke(sample_sentence_input)
        logger.info(f"{sample_sentence_response}") 
        example_sentence = sample_sentence_response.content 
        example_synonyms = 0 # Pre-setting value because example_synonyms are not generated in this branch
    ###############################################
    ###############################################
    # Compare both responses for consistency
    word_country_match_commonality = extract_commonality(word_country_match)
    # print(word_country_match_commonality)
    word_country_match_check_commonality = extract_commonality(word_country_match_check)
    # print(word_country_match_check_commonality)

    if word_country_match_commonality == word_country_match_check_commonality:
        word_country_match = word_country_match
    else:
        word_country_match = "I am not sure where the word or phrase is most commonly spoken."

    return ai_translation, example_synonyms, example_sentence, word_country_match

if __name__ == '__main__':
    # word: str = "coger" # Example for "Most common in Spain"
    # word: str = "ordenador" # Example for "Most common in Spain"
    # word: str = "patata" # Example for "Most common in Spain"
    # word: str = "joder" # Example for "Most common in Spain"
    # word: str = "choclo" # Example for "Most common in Argentina"
    # word: str = "pileta" # Example for "Most common in Argentina"
    # word: str = "onza" # Example for "Most common in All Spanish-speaking countries"
    # word: str = "recoger" # Example for "Most common in All Spanish-speaking countries"
    # word: str = "sudor" # Example for "Most common in All Spanish-speaking countries"
    # word: str = "cima" # Example for "Most common in All Spanish-speaking countries"
    # word: str = "acechar" # Example for "Most common in All Spanish-speaking countries"
    # word: str = "verga"  # Example for "Most common in All Spanish-speaking countries"
    # word: str = "embargar" # Example for "Most common in All Spanish-speaking countries"
    # word: str = "no mames" # Example for "Most common in Mexico"
    # word: str = "neta" # Example for "Most common in Mexico"
    # word: str = "chido" # Example for "Most common in Mexico"
    # word: str = "tajar" # Example for "Most common in Other"
    # word: str = "asdfsafsd" # Example for "Most common in Other"
    # word: str = "xxx" # Example for "Most common in Other"
    # word: str = "asolar" 
    # word: str = "onza" 
    # word: str = "en pos"
    # word = "qué anda"
    ai_translation, example_synonyms, example_sentence, word_country_match = response_generation(word)
    print(ai_translation)
    print(example_synonyms)
    print(example_sentence)
    print(word_country_match)