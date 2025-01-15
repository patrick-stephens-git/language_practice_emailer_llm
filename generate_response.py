from config import openai_api_key
from utils.logging_config import setup_logging
from langchain_openai import ChatOpenAI


def get_sample_sentence(word, translation):
    # Logging
    logger = setup_logging()

    # Initialize the LLM
    llm = ChatOpenAI(model="gpt-4o-mini", 
                     api_key=openai_api_key,
                     temperature=0.5, # Temp used for response creativity
                     max_tokens=50, # Max tokens of response length
                     timeout=30, # Max time (in secs) for a response from OpenAI API
                     max_retries=2, # Max retry attempts if request fails (Default is 2)
                     n=1, # Max num of responses to generate (default is 1)
                     presence_penalty=-2.0, # Encourage/Discourage inclusion of new topics in response (default is 0.0; range is -2.0 to 2.0)
                     frequency_penalty=0.0, # Encourage/Discourage inclusion of the same tokens in response (default is 0.0; range is -2.0 to 2.0)
                     streaming=False # stream response back from OpenAI API (default is False)
                     )

    # LLM Prompt
    input = f"You are a Mexican national who is helping a non-native student of the Spanish language from the United States to learn how to speak Spanish. The student is focused on learning the word: '{word}'. Please provide the student with a sample sentence in Spanish that uses '{word}' in a way you would use it in a normal conversation. Only respond with the example sentence. Do not provide any additional information."
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