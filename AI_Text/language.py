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

    def get_language(self, language_choice: LanguageChoice) -> str:
        return self.languages.get(language_choice, "Language choice not found.")