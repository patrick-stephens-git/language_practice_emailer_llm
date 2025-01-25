from config import openai_api_key
from utils.logging_config import setup_logging
from langchain_openai import ChatOpenAI


def get_sample_sentence(word, translation):
    # Logging
    logger = setup_logging()

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

    # LLM Prompt
    input = f"You're a Mexican national helping a student learn the Spanish language, emphasizing Mexican use cases. The student is learning the word: '{word}'. Give the student a sample Spanish sentence using '{word}' as you would use it in normal conversation. Respond with the example sentence. Do not provide any additional information. There is a 15% chance of using examples in the subjunctive mood."
    logger.info(f"{input}")
    
    # Generate LLM response
    response = llm.invoke(input)
    # Extract the assistant's reply and add to the conversation history
    logger.info(f"{response}")
    example_sentence = response.content
    return example_sentence

if __name__ == '__main__':
    word: str = "enseñar"
    translation: str = "to teach, to show"
    example_sentence = get_sample_sentence(word, translation)
    print(example_sentence)