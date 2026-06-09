from config import target_country, target_language, student_primary_language


def factual_system_prompt() -> str:
    return f"""
You are an expert {target_language} teacher and a native speaker from {target_country}.
Answer questions about vocabulary usage concisely and accurately.
Always respond with valid JSON only — no extra text, no markdown.
""".strip()


def factual_user_prompt(word: str) -> str:
    return f"""
The student is learning the {target_language} word or phrase: '{word}'.

Answer both questions below. Respond ONLY with a JSON object matching this exact schema:
{{"location": "...", "is_common": "..."}}

Question 1 — Where is '{word}' most commonly spoken? Choose exactly one of:
"all Spanish-speaking countries", "Mexico", "Spain", "Colombia", "Argentina",
"Venezuela", "Chile", "Guatemala", "Ecuador", "Costa Rica", "Puerto Rico", "Other".
Assign your answer to the "location" key.

Question 2 — Is '{word}' commonly used in everyday speech in {target_country}?
'Commonly used' means native speakers use it in casual conversations, on the street,
at home, or among friends in {target_country}, OR it is common slang or informal expression there.
Assign exactly "Yes", "No", or "Unsure" to the "is_common" key.

Do NOT explain your reasoning. Do NOT include any text outside the JSON object.
""".strip()


def generative_system_prompt() -> str:
    return f"""
You are a {target_language} teacher born and raised in {target_country}.
You help language students learn {target_language} through practical examples.
Always respond with valid JSON only — no extra text, no markdown.
""".strip()


def generative_user_prompt(
    word: str,
    word_country_match_location: str,
    is_common: str,
    sample_sentence_subject: str | None,
    sample_verb_tense: str,
    target_focus: str,
    apply_focus: bool,
    use_passive_se: bool,
) -> str:
    focus_instruction = f"Write the sample sentence to demonstrate: {target_focus}. " if apply_focus else ""
    location = word_country_match_location if word_country_match_location else "unknown"
    fallback_region = word_country_match_location if word_country_match_location else "its primary region"

    if use_passive_se:
        task4_instruction = (
            f"Write the sentence as a passive se construction (e.g., 'se + verb + noun'). "
            f"Do not use a personal pronoun as the subject. "
            f"The sentence must use the {sample_verb_tense} tense."
        )
    else:
        task4_instruction = (
            f"The subject must be: '{sample_sentence_subject}'. "
            f"The sentence must use the {sample_verb_tense} tense. "
            f"{focus_instruction}"
        )

    return f"""
The language student is learning the {target_language} word or phrase: '{word}'.

Context already established:
- This word is most commonly spoken in: {location}.
- This word is commonly used in everyday speech in {target_country}: {is_common}.

Complete all four tasks below. Respond ONLY with a JSON object matching this exact schema:
{{"translation": "...", "where_to_hear": "...", "synonyms": "...", "sample_sentence": "..."}}

Task 1 (translation): Provide the {student_primary_language} meaning of '{word}' as used in {target_country}. One short phrase only.

Task 2 (where_to_hear): Write 1 short sentence in {student_primary_language} describing where a person living in {target_country} is most likely to see or hear '{word}'.
If it IS common in {target_country}, describe the context there.
If it is NOT common in {target_country}, describe the context in {fallback_region}.

Task 3 (synonyms): List synonyms for '{word}' commonly used in {target_country}, ranked most-to-least common. Comma-separated list only.

Task 4 (sample_sentence): Write one example sentence using '{word}' in {target_language} as used in normal conversation in {target_country}.
{task4_instruction}
Do NOT explain your reasoning. Do NOT include any text outside the JSON object.
""".strip()
