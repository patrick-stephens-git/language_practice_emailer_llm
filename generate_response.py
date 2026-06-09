from config import openai_api_key, target_focus_list, focus_weight, passive_se_weight, subject_list, subject_usted_list, verb_tense_list
from utils.logging_config import setup_logging
from prompts import factual_system_prompt, factual_user_prompt, generative_system_prompt, generative_user_prompt
import openai
import json
import random


def get_target_focus() -> str:
    return random.choice(target_focus_list)


def get_verb_tense() -> str:
    return random.choice(verb_tense_list)


def get_sample_sentence_subject() -> str:
    sample_sentence_subject: str = random.choice(subject_list)
    if sample_sentence_subject == 'usted':
        usted_subject: str = random.choice(subject_usted_list)
        sample_sentence_subject = f"{sample_sentence_subject} (who is a {usted_subject})"
    return sample_sentence_subject


def response_generation(word: str) -> tuple[str, str, str, str, str, str]:
    logger = setup_logging()

    use_passive_se: bool = random.random() < passive_se_weight
    sample_sentence_subject: str | None = None if use_passive_se else get_sample_sentence_subject()
    sample_verb_tense: str = get_verb_tense() # sampled before API calls so the same tense is used across all three calls

    client = openai.OpenAI(api_key=openai_api_key, max_retries=2, timeout=30) # one client reused for all three calls; retries and timeout guard against transient API errors

    ###############################################
    # Call 1 — Factual Query: location + is_common (independent, no prior context)
    ###############################################
    factual_system: str = factual_system_prompt()
    factual_user: str = factual_user_prompt(word)
    logger.info(f"Call 1 (factual) user prompt: {factual_user}")

    call1_location: str = ""
    call1_is_common: str = "Unsure"
    try:
        call1_response = client.chat.completions.create(
            model="gpt-4o-mini", # fast and cost-effective; sufficient for structured factual JSON
            messages=[
                {"role": "system", "content": factual_system},
                {"role": "user", "content": factual_user},
            ],
            response_format={"type": "json_object"}, # enforced so json.loads never receives free-form text
            temperature=1.2, # 0.0–2.0; higher value adds variety to responses
            max_tokens=60, # Sufficient for small JSON object with short values
        )
        call1_raw: str = call1_response.choices[0].message.content
        logger.info(f"Call 1 raw response: {call1_raw}")
        call1_data: dict = json.loads(call1_raw)
        call1_location = str(call1_data.get("location", "")).strip()
        call1_is_common = str(call1_data.get("is_common", "Unsure")).strip()
    except json.JSONDecodeError as e:
        logger.error(f"Call 1 JSON parse error: {e}")

    ###############################################
    # Call 2 — Factual Verification: same questions, fully independent (no Call 1 context)
    ###############################################
    logger.info(f"Call 2 (verification) user prompt: {factual_user}")

    call2_location: str = ""
    call2_is_common: str = "Unsure"
    try:
        call2_response = client.chat.completions.create(
            model="gpt-4o-mini", # fast and cost-effective; sufficient for structured factual JSON
            messages=[
                {"role": "system", "content": factual_system},
                {"role": "user", "content": factual_user},
            ],
            response_format={"type": "json_object"}, # enforced so json.loads never receives free-form text
            temperature=1.2, # 0.0–2.0; higher value adds variety to responses
            max_tokens=60, # Sufficient for small JSON object with short values
        )
        call2_raw: str = call2_response.choices[0].message.content
        logger.info(f"Call 2 raw response: {call2_raw}")
        call2_data: dict = json.loads(call2_raw)
        call2_location = str(call2_data.get("location", "")).strip()
        call2_is_common = str(call2_data.get("is_common", "Unsure")).strip()
    except json.JSONDecodeError as e:
        logger.error(f"Call 2 JSON parse error: {e}")

    ###############################################
    # Consistency check: compare Call 1 and Call 2 results
    ###############################################
    if call1_location.lower() == call2_location.lower() and call1_location != "": # non-empty prevents two unknown responses from counting as agreement
        word_country_match_location: str = call1_location.title() # Normalize casing for display
        word_country_match: str = f"The word or phrase '{word}' is most common in {word_country_match_location}."
    else:
        word_country_match_location = "" # No confident location; leave blank so generative prompt doesn't invent one
        word_country_match = "I am not sure where the word or phrase is most commonly spoken."

    if call1_is_common.lower() == call2_is_common.lower():
        is_common: str = call1_is_common
    else:
        is_common = "Unsure" # Fallback when calls disagree on commonality

    ###############################################
    # Call 3 — Generative Outputs: translation, where_to_hear, synonyms, sample_sentence
    ###############################################
    target_focus: str = get_target_focus()
    apply_focus: bool = (not use_passive_se) and (random.random() < focus_weight) # passive se and focus are mutually exclusive; applying focus requires a subject
    generative_system: str = generative_system_prompt()
    generative_user: str = generative_user_prompt(
        word=word,
        word_country_match_location=word_country_match_location,
        is_common=is_common,
        sample_sentence_subject=sample_sentence_subject,
        sample_verb_tense=sample_verb_tense,
        target_focus=target_focus,
        apply_focus=apply_focus,
        use_passive_se=use_passive_se,
    )
    logger.info(f"Call 3 (generative) user prompt: {generative_user}")

    ai_translation: str = "[unavailable]"
    where_to_hear: str = "[unavailable]"
    example_synonyms: str = "[unavailable]"
    example_sentence: str = "[unavailable]"
    try:
        call3_response = client.chat.completions.create(
            model="gpt-4o-mini", # fast and cost-effective; sufficient for structured factual JSON
            messages=[
                {"role": "system", "content": generative_system},
                {"role": "user", "content": generative_user},
            ],
            response_format={"type": "json_object"}, # enforced so json.loads never receives free-form text
            temperature=1.2, # 0.0–2.0; higher value adds variety to responses
            max_tokens=160, # Sufficient for four fields including a full example sentence
        )
        call3_raw: str = call3_response.choices[0].message.content
        logger.info(f"Call 3 raw response: {call3_raw}")
        call3_data: dict = json.loads(call3_raw)
        ai_translation = str(call3_data.get("translation", "[unavailable]")).strip()
        where_to_hear = str(call3_data.get("where_to_hear", "[unavailable]")).strip()
        example_synonyms = str(call3_data.get("synonyms", "[unavailable]")).strip()
        example_sentence = str(call3_data.get("sample_sentence", "[unavailable]")).strip()
    except json.JSONDecodeError as e:
        logger.error(f"Call 3 JSON parse error: {e}")

    return ai_translation, example_synonyms, example_sentence, word_country_match, is_common, where_to_hear # order must match the tuple signature expected by main.py and emailer.py

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
