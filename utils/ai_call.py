
import openai
import os

def get_patient_result_from_ai(symptoms): 
    """ 
    Get the result from AI for a patient 
    """
    try:
        openai.api_key=""

        response = openai.Completion.create(
        model="text-davinci-003",
        prompt=symptoms,
        temperature=1,
        max_tokens=3028,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        return response.choices[0].text
    except Exception as e:
        print("####################################\n")
        print(e)
        return None
