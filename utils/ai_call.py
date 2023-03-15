
import openai
import os

def get_patient_result_from_ai(symptoms): 
    """ 
    Get the result from AI for a patient 
    """
    try:
        openai.api_key = os.getenv("API_KEY")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = [
                {
                    "role":"system", "content":"Your are a good specialist doctor",
                    "role": "user", "content": symptoms,
                }
            ]
        )

        return str(response["choices"][0]["message"]["content"])
    except Exception as e:
        with open("ai_error.log", "a") as f:
            f.write('\n'+str(e))
        return None
