import json
from personality import PersonalityType
from language import LanguageChoice
from services import call_text_generator_service, call_answer_evaluator_service, call_tts_service


class MessageProcessor:
    @staticmethod
    def question_generator(body):
        try:
            message = json.loads(body)
            category = message.get("category")
            points = message.get("points")
            preferences = message.get("preferences", {})

            if not category or points is None:
                return {"error": "Missing 'category' or 'points'"}

            personality_type = preferences.get("personality", "Friendly").upper()
            language_choice = preferences.get("language", "English").upper()

            try:
                preferences = {
                    "personality": PersonalityType[personality_type],
                    "language": LanguageChoice[language_choice],
                }
            except KeyError:
                return {"error": "Invalid personality or language"}

            text_response = call_text_generator_service(
                category, points, preferences
            )
            if "error" in text_response:
                return text_response

            tts_response = call_tts_service(text_response)
            if "error" in tts_response:
                return tts_response

            return {"text": text_response, "audio_url": tts_response}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def evaluate_answer(body):
        print("Received answer evaluation request")
        try:
            message = json.loads(body)
            answer = message.get("answer")
            question = message.get("question", {})
            preferences = message.get("preferences", {})

            if not answer or not question:
                return {"error": "Missing 'answer' or 'question'"}

            personality_type = preferences.get("personality", "Friendly").upper()
            language_choice = preferences.get("language", "English").upper()

            try:
                preferences = {
                    "personality": PersonalityType[personality_type],
                    "language": LanguageChoice[language_choice],
                }
            except KeyError:
                return {"error": "Invalid personality or language"}

            print("Calling answer evaluator service...")
            text_response = call_answer_evaluator_service(answer, question, preferences)
            print("Answer evaluator service response:", text_response)
            if "error" in text_response:
                return text_response

            print("Calling TTS service...")
            tts_response = call_tts_service(text_response)
            print("TTS service response:", tts_response)
            if "error" in tts_response:
                return tts_response

            return {"text": text_response, "audio_url": tts_response}
        except Exception as e:
            return {"error": str(e)}
