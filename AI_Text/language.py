from enum import Enum


class LanguageChoice(str, Enum):
    ENGLISH = "English"
    DANISH = "Danish"


class Language:
    def __init__(self):
        self.languages = {
            LanguageChoice.ENGLISH: "From now on you will only speak English no matter what input you get.",
            LanguageChoice.DANISH: "Fra nu af vil du kun tale dansk lige meget hvilket input du får."
        }
        self.current_language = None

    def set_language(self, language_choice: LanguageChoice):
        if language_choice not in self.languages:
            raise ValueError(f"Invalid language choice: {language_choice}")
        self.current_language = language_choice

    def get_language(self) -> str:
        if not self.current_language:
            return "No language set."
        return self.languages[self.current_language]