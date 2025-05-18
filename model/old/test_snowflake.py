import os
from dotenv import load_dotenv
from snowflake.snowpark.session import Session
from snowflake.cortex import Summarize, Complete, ExtractAnswer, Sentiment, Translate


load_dotenv()

connection_params = {
    "account": os.environ['SNOWFLAKE_ACCOUNT'],
    "user": os.environ['SNOWFLAKE_USER'],
    "password": os.environ['SNOWFLAKE_USER_PASSWORD'],
    "role": 'ACCOUNTADMIN',
    #"database": 'SNOWFLAKE_LEARNING_DB',
    "warehouse": 'COMPUTE_WH'
    #"schema": 'PUBLIC',
    }

snowflake_session = Session.builder.configs(connection_params).create()

def summarize(user_text):
    summary = Summarize(text=user_text, session=snowflake_session)
    return summary


# def complete_test(user_text):
#     completion = Complete(
#         model='snowflake-llama3.3-70b',
#         prompt=f"create a short summary of the given python code. limit your output to the relevant parts and answer in natural language: {user_text}",
#         session=snowflake_session,
#     )
#     return completion


def extract_answer(user_text):
    answer = ExtractAnswer(
        from_text=user_text,
        question="What are some of the ethical concerns associated with unicorns?",
        session=snowflake_session,
    )
    return answer


def sentiment(user_text):
    sentiment = Sentiment(text=user_text, session=snowflake_session)
    return sentiment


def translate(user_text):
    translation = Translate(
        text=user_text, from_language="en", to_language="de", session=snowflake_session
    )
    return translation


def main():
    user_text = """
        Crocodiles—ancient reptiles that have ruled the waters for millions of years with their sheer power and stealth! 🐊

These formidable creatures are nature’s perfect predators, equipped with armored scales, powerful jaws, and a bite force that rivals any in the animal kingdom. Lurking beneath the surface, they wait patiently, ready to strike with lightning speed when their prey least expects it. Despite their fearsome reputation, crocodiles are highly intelligent and capable of remarkable cooperation, especially when hunting or caring for their young.

Their prehistoric lineage dates back over 200 million years, making them living relics of the dinosaur age. Whether basking in the sun to regulate their body temperature or gliding effortlessly through murky waters, crocodiles command respect in every ecosystem they inhabit.
    """

    try:
        summary_result = summarize(user_text)
        print(
            f"Summarize() Snowflake Cortex LLM function result:\n{summary_result.strip()}\n"
        )

        # completion_result = complete_test(user_text)
        # print(
        #     f"Complete() Snowflake Cortex LLM function result:\n{completion_result.strip()}\n"
        # )

        answer_result = extract_answer(user_text)
        print(
            f"ExtractAnswer() Snowflake Cortex LLM function result:\n{answer_result}\n"
        )

        sentiment_result = sentiment(user_text)
        print(
            f"Sentiment() Snowflake Cortex LLM function result:\n{sentiment_result}\n"
        )

        translation_result = translate(user_text)
        print(
            f"Translate() Snowflake Cortex LLM function result:\n{translation_result.strip()}\n"
        )

    finally:
        if snowflake_session:
            # Close the Snowflake session
            snowflake_session.close()


if __name__ == "__main__":
    # Run the main function
    main()