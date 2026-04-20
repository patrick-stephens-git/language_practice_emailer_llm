from config import openai_api_key, target_country, target_language, student_primary_language, target_focus, focus_weight, subject_list, subject_usted_list # Import all config values needed for prompts
from utils.logging_config import setup_logging # Import logger factory
import openai # OpenAI SDK for direct API calls
import json # For parsing structured JSON responses
import random # For random subject selection

def get_sample_sentence_subject() -> str:
    sample_sentence_subject: str = random.choice(subject_list) # Randomly select an item from the list
    if sample_sentence_subject == 'usted':
        usted_subject: str = random.choice(subject_usted_list) # Randomly select a profession for usted
        sample_sentence_subject = f"{sample_sentence_subject} (who is a {usted_subject})" # Append profession to subject
    return sample_sentence_subject


def response_generation(word: str) -> tuple[str, str, str, str, str, str]:
    logger = setup_logging() # Initialize the logger

    sample_sentence_subject: str = get_sample_sentence_subject() # Get a random sentence subject before any API calls

    client = openai.OpenAI(api_key=openai_api_key, max_retries=2, timeout=30) # Create a single reusable OpenAI client with retry and timeout config

    ###############################################
    # Call 1 — Factual Query: location + is_common (independent, no prior context)
    ###############################################
    factual_system: str = (
        f"You are an expert {target_language} teacher and a native speaker from {target_country}. "
        "Answer questions about vocabulary usage concisely and accurately. "
        "Always respond with valid JSON only — no extra text, no markdown." # Enforce JSON-only output
    )
    factual_user: str = (
        f"The student is learning the {target_language} word or phrase: '{word}'.\n\n"
        "Answer both questions below. Respond ONLY with a JSON object matching this exact schema: "
        '{"location": "...", "is_common": "..."}\n\n'
        f"Question 1 — Where is '{word}' most commonly spoken? Choose exactly one of: "
        '"all Spanish-speaking countries", "Mexico", "Spain", "Colombia", "Argentina", '
        '"Venezuela", "Chile", "Guatemala", "Ecuador", "Costa Rica", "Puerto Rico", "Other". '
        'Assign your answer to the "location" key.\n\n'
        f"Question 2 — Is '{word}' commonly used in everyday speech in {target_country}? "
        f"'Commonly used' means native speakers use it in casual conversations, on the street, "
        f"at home, or among friends in {target_country}, OR it is common slang or informal expression there. "
        'Assign exactly "Yes", "No", or "Unsure" to the "is_common" key.\n\n'
        "Do NOT explain your reasoning. Do NOT include any text outside the JSON object." # Prevent extra output
    )
    logger.info(f"Call 1 (factual) user prompt: {factual_user}") # Log the prompt for debugging

    call1_location: str = "" # Default location if Call 1 fails
    call1_is_common: str = "Unsure" # Default commonality if Call 1 fails
    try:
        call1_response = client.chat.completions.create( # Send Call 1 to the API
            model="gpt-4o-mini", # Use the fast and cost-effective model
            messages=[
                {"role": "system", "content": factual_system}, # System role for factual calls
                {"role": "user", "content": factual_user}, # User question for factual calls
            ],
            response_format={"type": "json_object"}, # Force structured JSON output
            temperature=1.2, # Creativity of response (0.0 to 2.0)
            max_tokens=60, # Sufficient for small JSON object with short values
        )
        call1_raw: str = call1_response.choices[0].message.content # Extract raw JSON string from response
        logger.info(f"Call 1 raw response: {call1_raw}") # Log raw response before parsing
        call1_data: dict = json.loads(call1_raw) # Parse JSON string into a Python dict
        call1_location = str(call1_data.get("location", "")).strip() # Extract location value, default empty
        call1_is_common = str(call1_data.get("is_common", "Unsure")).strip() # Extract is_common value, default Unsure
    except json.JSONDecodeError as e:
        logger.error(f"Call 1 JSON parse error: {e}") # Log parse failure with error details

    ###############################################
    # Call 2 — Factual Verification: same questions, fully independent (no Call 1 context)
    ###############################################
    logger.info(f"Call 2 (verification) user prompt: {factual_user}") # Log same prompt used independently

    call2_location: str = "" # Default location if Call 2 fails
    call2_is_common: str = "Unsure" # Default commonality if Call 2 fails
    try:
        call2_response = client.chat.completions.create( # Send Call 2 independently to the API
            model="gpt-4o-mini", # Use the fast and cost-effective model
            messages=[
                {"role": "system", "content": factual_system}, # Same system role, no Call 1 result included
                {"role": "user", "content": factual_user}, # Same question, no Call 1 result included
            ],
            response_format={"type": "json_object"}, # Force structured JSON output
            temperature=1.2, # Creativity of response (0.0 to 2.0)
            max_tokens=60, # Sufficient for small JSON object with short values
        )
        call2_raw: str = call2_response.choices[0].message.content # Extract raw JSON string from response
        logger.info(f"Call 2 raw response: {call2_raw}") # Log raw response before parsing
        call2_data: dict = json.loads(call2_raw) # Parse JSON string into a Python dict
        call2_location = str(call2_data.get("location", "")).strip() # Extract location value, default empty
        call2_is_common = str(call2_data.get("is_common", "Unsure")).strip() # Extract is_common value, default Unsure
    except json.JSONDecodeError as e:
        logger.error(f"Call 2 JSON parse error: {e}") # Log parse failure with error details

    ###############################################
    # Consistency check: compare Call 1 and Call 2 results
    ###############################################
    if call1_location.lower() == call2_location.lower() and call1_location != "": # Both calls agree on a non-empty location
        word_country_match_location: str = call1_location.title() # Normalize casing for display
        word_country_match: str = f"The word or phrase '{word}' is most common in {word_country_match_location}." # Build the sentence used in the email
    else:
        word_country_match_location = "" # No confident location; leave blank so generative prompt doesn't invent one
        word_country_match = "I am not sure where the word or phrase is most commonly spoken." # Fallback when calls disagree

    if call1_is_common.lower() == call2_is_common.lower(): # Both calls agree on commonality
        is_common: str = call1_is_common # Use the agreed-upon value
    else:
        is_common = "Unsure" # Fallback when calls disagree on commonality

    ###############################################
    # Call 3 — Generative Outputs: translation, where_to_hear, synonyms, sample_sentence
    ###############################################
    focus_line_text: str = f"You have a {focus_weight} chance of writing the sample sentence to demonstrate {target_focus}. " if target_focus != "" else "" # Include focus instruction only when a focus is configured

    generative_system: str = (
        f"You are a {target_language} teacher born and raised in {target_country}. "
        f"You help language students learn {target_language} through practical examples. "
        "Always respond with valid JSON only — no extra text, no markdown." # Enforce JSON-only output
    )
    generative_user: str = (
        f"The language student is learning the {target_language} word or phrase: '{word}'.\n\n"
        "Context already established:\n"
        f"- This word is most commonly spoken in: {word_country_match_location if word_country_match_location else 'unknown'}.\n" # Inject verified location
        f"- This word is commonly used in everyday speech in {target_country}: {is_common}.\n\n" # Inject verified commonality
        "Complete all four tasks below. Respond ONLY with a JSON object matching this exact schema: "
        '{"translation": "...", "where_to_hear": "...", "synonyms": "...", "sample_sentence": "..."}\n\n'
        f"Task 1 (translation): Provide the {student_primary_language} meaning of '{word}' as used in {target_country}. One short phrase only.\n\n"
        f"Task 2 (where_to_hear): Write 1 short sentence in {student_primary_language} describing where a person living in {target_country} is most likely to see or hear '{word}'. "
        f"If it IS common in {target_country}, describe the context there. "
        f"If it is NOT common in {target_country}, describe the context in {word_country_match_location if word_country_match_location else 'its primary region'}.\n\n"
        f"Task 3 (synonyms): List synonyms for '{word}' commonly used in {target_country}, ranked most-to-least common. Comma-separated list only.\n\n"
        f"Task 4 (sample_sentence): Write one example sentence using '{word}' in {target_language} as used in normal conversation in {target_country}. "
        f"The subject must be: '{sample_sentence_subject}'. {focus_line_text}"
        "Do NOT explain your reasoning. Do NOT include any text outside the JSON object." # Prevent extra output
    )
    logger.info(f"Call 3 (generative) user prompt: {generative_user}") # Log the prompt for debugging

    ai_translation: str = "[unavailable]" # Default if Call 3 fails
    where_to_hear: str = "[unavailable]" # Default if Call 3 fails
    example_synonyms: str = "[unavailable]" # Default if Call 3 fails
    example_sentence: str = "[unavailable]" # Default if Call 3 fails
    try:
        call3_response = client.chat.completions.create( # Send Call 3 to the API
            model="gpt-4o-mini", # Use the fast and cost-effective model
            messages=[
                {"role": "system", "content": generative_system}, # System role for generative call
                {"role": "user", "content": generative_user}, # User prompt for generative call
            ],
            response_format={"type": "json_object"}, # Force structured JSON output
            temperature=1.2, # Creativity of response (0.0 to 2.0)
            max_tokens=160, # Sufficient for four fields including a full example sentence
        )
        call3_raw: str = call3_response.choices[0].message.content # Extract raw JSON string from response
        logger.info(f"Call 3 raw response: {call3_raw}") # Log raw response before parsing
        call3_data: dict = json.loads(call3_raw) # Parse JSON string into a Python dict
        ai_translation = str(call3_data.get("translation", "[unavailable]")).strip() # Extract translation value
        where_to_hear = str(call3_data.get("where_to_hear", "[unavailable]")).strip() # Extract where_to_hear value
        example_synonyms = str(call3_data.get("synonyms", "[unavailable]")).strip() # Extract synonyms value
        example_sentence = str(call3_data.get("sample_sentence", "[unavailable]")).strip() # Extract sample_sentence value
    except json.JSONDecodeError as e:
        logger.error(f"Call 3 JSON parse error: {e}") # Log parse failure with error details

    return ai_translation, example_synonyms, example_sentence, word_country_match, is_common, where_to_hear # Return the same 6-tuple expected by main.py and emailer.py

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
