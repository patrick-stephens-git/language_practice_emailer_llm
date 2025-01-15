import pandas as pd
from config import sheet_id
from utils.logging_config import setup_logging

def get_word() -> tuple[str, str]:
    #####################################
    ## Logging:
    logger = setup_logging()
    
    #####################################
    ## Get Sensitive Data:
    logger.info(f"Sheet ID: {sheet_id}")
    
    #####################################
    ## Read File:
    input_url: str = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(input_url)

    #####################################
    ## Sanity Check Code:
    df_head = df.head()
    logger.info(f"DataFrame head after import:\n{df_head}")
    num_rows = len(df)
    logger.info(f"How many rows in df: {num_rows}")
    num_unique_words = df["Word"].nunique() # Get count of unique words in the dataframe
    logger.info(f"How many unique words in df: {num_unique_words}")
    
    #####################################
    ## Data Prep:
    df = df[df["Lookup Count"] != 1] # Remove any strings that are looked up 1x (do this to only return words that are struggled with)
    df = df.loc[df.index.repeat(df["Lookup Count"])] # Expand count of rows by the number in the "Lookup Count" column so that it's more likely to send words that are often reviewed
    df = df.drop(columns=["Lookup Count"]) # Drop the "Lookup Count" column
    df = df.sample(frac=1).reset_index(drop=True) # Shuffle the dataframe
    df_head = df.head()
    logger.info(f"DataFrame head after shuffle:\n{df_head}")
    df_sample = df.sample(n=1) # Randomly select 1 row in the dataframe
    sample_word = df_sample.iloc[0,0] # Get word
    logger.info(f"Word: {sample_word}")
    sample_translation = df_sample.iloc[0,1] # Get translation
    logger.info(f"Translation: {sample_translation}")

    #####################################
    logger.info("Word & translation successfully collected.")
    return sample_word, sample_translation

if __name__ == '__main__':
    sample_word, sample_translation = get_word()