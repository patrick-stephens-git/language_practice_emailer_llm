from config import openai_api_key, target_country, target_language, target_focus, focus_weight, subject_list, subject_usted_list
from utils.logging_config import setup_logging
from langchain_openai import ChatOpenAI
import random


# Determine if responses contain "Yes", "No", or "Unsure"
def extract_commonality(text):
    text_clean = text.strip().capitalize() # Removes leading/trailing whitespace and newlines, then capitalize first letter; Example: "  yes\n" -> "Yes"
    if text_clean.startswith("Yes"): # Check if the normalized text starts with the substring "Yes"
        return "Yes"
    elif text_clean.startswith("No"): # Check if the normalized text starts with the substring "No"
        return "No"
    else:
        return "Unsure"

def get_sample_sentence(word):
    # Logging
    logger = setup_logging()

    # Get subject of the sample sentence
    sample_sentence_subject = random.choice(subject_list) # Randomly select an item from the list
    # print(sample_sentence_subject)
    if sample_sentence_subject == 'usted':
        usted_subject = random.choice(subject_usted_list)
        sample_sentence_subject = f"{sample_sentence_subject} (who is a {usted_subject})"
        # print(sample_sentence_subject)
    else:
        pass
    

    # Initialize the LLM
    llm = ChatOpenAI(model="gpt-4o-mini", 
                     api_key=openai_api_key,
                     temperature=1.2, # Temp used for response creativity (Range is 0.0 to 2.0); Low temp (0.0 to 0.4); responses become more focused, deterministic, and repetitive. The model is less likely to explore creative or diverse options and will often produce the "most likely" response. This is ideal for factual or predictable outputs; Moderate temp (0.5 to 0.7) responses balance creativity and coherence. The model generates more varied responses while still maintaining some predictability. This range is commonly used for conversational or creative tasks; High temp (0.8 to 2.0) responses become highly creative and diverse but may lose coherence or relevance to the input. This is useful for brainstorming or generating unexpected ideas.
                     max_tokens=70, # Max tokens of response length
                     timeout=30, # Max time (in secs) for a response from OpenAI API
                     max_retries=2, # Max retry attempts if request fails (Default is 2)
                     n=1, # Max num of responses to generate (default is 1)
                     presence_penalty=-2.0, # Encourage/Discourage inclusion of new topics in response (default is 0.0; range is -2.0 to 2.0)
                     frequency_penalty=0.0, # Encourage/Discourage inclusion of the same tokens in response (default is 0.0; range is -2.0 to 2.0)
                     streaming=False # stream response back from OpenAI API (default is False)
                     )

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
    # Extract the assistant's reply and add to the conversation history
    logger.info(f"{sample_sentence_response}")
    example_sentence = sample_sentence_response.content

    # LLM Prompt for Understanding if Word is common in Target Country
    word_country_match_input = f"""
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
        - Task 1: Determine if the Target Word is commonly used in {target_country}

        # Tasks:
        ## Task 1: Determine if the Target Word is commonly used in {target_country}
        - Determine if the Target Word '{word}' is commonly used in {target_country}.
        - Answer with 'Yes' if it is commonly used, 'No' if it is NOT commonly used, or 'Unsure' if you are uncertain.
        - Provide ONLY the following context depending on your answer:
        -- IF Yes THEN "Yes - the word 'word' refers to 'meaning'."
        -- IF No THEN "No - the word 'word' refers to 'meaning'."
        -- IF Unsure THEN "Unsure - the word 'word' refers to 'meaning'."
        - Replace 'word' with '{word}'.
        - Replace 'meaning' with the appropriate meaning of the word in {target_country}.
        - Do NOT provide any other information in your response beyond what is specified above.
        - Do NOT explain your reasoning.
        ---
        # Output Template:
        - Yes/No/Unsure - the word 'word' refers to 'meaning'.
        """
    logger.info(f"{word_country_match_input}")
    
    # Generate LLM response for Word-Country Match:
    word_country_match_response = llm.invoke(word_country_match_input)
    # Extract the assistant's reply and add to the conversation history
    logger.info(f"{word_country_match_response}")
    word_country_match = word_country_match_response.content

    # LLM Prompt for Understanding if Word is common in Target Country
    word_country_match_check_input = f"""
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
        - Task 1: Determine if the Target Word is commonly used in {target_country}

        # Tasks:
        ## Task 1: Determine if the Target Word is commonly used in {target_country}
        - Determine if the Target Word '{word}' is commonly used in {target_country}.
        - Answer with 'Yes' if it is commonly used, 'No' if it is NOT commonly used, or 'Unsure' if you are uncertain.
        - Provide ONLY the following context depending on your answer:
        -- IF Yes THEN "Yes"
        -- IF No THEN "No"
        -- IF Unsure THEN "Unsure"
        - Do NOT provide any other information in your response beyond what is specified above.
        - Do NOT explain your reasoning.
        ---
        # Output Template:
        - Yes/No/Unsure
        """
    logger.info(f"{word_country_match_check_input}")

    # Generate LLM response for Word-Country Match Checker:
    word_country_match_check_response = llm.invoke(word_country_match_check_input)
    # Extract the assistant's reply and add to the conversation history
    logger.info(f"{word_country_match_check_response}")
    word_country_match_check = word_country_match_check_response.content

    word_country_match_commonality = extract_commonality(word_country_match)
    word_country_match_check_commonality = extract_commonality(word_country_match_check)

    if word_country_match_commonality == word_country_match_check_commonality:
        word_country_match = word_country_match
    else:
        word_country_match = "Unsure"

    return example_sentence, word_country_match

if __name__ == '__main__':
    word: str = "coger" # Example for "Not common in Mexico"
    # word: str = "ordenador" # Example for "Not common in Mexico"
    # word: str = "patata" # Example for "Not common in Mexico"
    # word: str = "choclo" # Example for "Not common in Mexico"
    # word: str = "pileta" # Example for "Not common in Mexico"
    # word: str = "recoger" # Example for "Common in Mexico"
    # word: str = "sudor" # Example for "Common in Mexico"
    # word: str = "cima" # Example for "Common in Mexico"
    # word: str = "acechar" # Example for "Common in Mexico"
    # word: str = "verga"  # Example for "Unsure in Mexico"
    example_sentence, word_country_match = get_sample_sentence(word)
    print(example_sentence)
    print(word_country_match)