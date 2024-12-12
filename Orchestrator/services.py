import requests
from config import Config

def call_text_generator_service(category, points, preferences):
    try:
        payload = {
            "category": category,
            "points": points,
            "preferences": {
                "personality": preferences.get("personality").value,
                "language": preferences.get("language").value,
            },
        }
        service_url = f"{Config.TEXT_GENERATOR_URL}"
        response = requests.post(service_url, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json().get("response")
        return {"error": f"Text Generator failed with status {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Text Generator service error: {str(e)}"}


def call_answer_evaluator_service(answer, question, preferences):
    try:
        payload = {
            "answer": answer,
            "question": question,
            "preferences": {
                "personality": preferences.get("personality").value,
                "language": preferences.get("language").value,
            },
        }
        print(f"Calling answer evaluator service... {payload}")
        service_url = f"{Config.TEXT_GENERATOR_URL}/evaluate"
        response = requests.post(service_url, json=payload, timeout=60)
        print(f"Response from answer evaluator service: {response}")
        if response.status_code == 200:
            return response.json().get("evaluation")
        return {"error": f"Answer Evaluator failed with status {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Answer Evaluator service error: {str(e)}"}


def call_tts_service(text):
    try:
        response = requests.post(Config.TTS_SERVICE_URL, json={"text": text})
        if response.status_code == 200:
            return response.json().get("audio_url")
        return {"error": f"TTS service error: {response.text}"}
    except requests.RequestException as e:
        return {"error": f"TTS service error: {str(e)}"}
