import re

from spacy import Language
from spacy.lang.hu import Hungarian
from spacy.pipeline import Pipe
from spacy.tokens import Token
from spacy.tokens.doc import Doc


@Hungarian.component(
    "lemma_case_smoother",
    assigns=["token.lemma"],
    requires=["token.lemma", "token.pos"],
)
def lemma_case_smoother(doc: Doc) -> Doc:
    """Smooth lemma casing by POS.

    DEPRECATED: This is not needed anymore, as the lemmatizer is now case-insensitive.

    Args:
        doc (Doc): Input document.

    Returns:
        Doc: Output document.
    """
    for token in doc:
        if token.is_sent_start and token.tag_ != "PROPN":
            token.lemma_ = token.lemma_.lower()

    return doc


class LemmaSmoother(Pipe):
    """Smooths lemma by applying rules."""

    _DATE_PATTERN = re.compile(r"(\d+)-[j]?[éá]?n?a?(t[őó]l)?")
    _NUMBER_PATTERN = re.compile(r"(\d+([-,/_.:]?(._)?\d+)*[%]?(_km/h)?)")

    @staticmethod
    @Hungarian.factory("lemma_smoother", assigns=["token.lemma"], requires=["token.lemma", "token.pos"])
    def create_lemma_smoother(nlp: Hungarian, name: str) -> "LemmaSmoother":
        return LemmaSmoother()

    def __call__(self, doc: Doc) -> Doc:
        rules = [
            self._remove_exclamation_marks,
            self._remove_question_marks,
            self._remove_date_suffixes,
            self._remove_suffix_after_numbers,
        ]

        for token in doc:
            for rule in rules:
                rule(token)

        return doc

    @classmethod
    def _remove_exclamation_marks(cls, token: Token) -> None:
        """Removes exclamation marks from the lemma.

        Args:
            token (Token): The original token.
        """

        if "!" != token.lemma_:
            exclamation_mark_index = token.lemma_.find("!")
            if exclamation_mark_index != -1:
                token.lemma_ = token.lemma_[:exclamation_mark_index]

    @classmethod
    def _remove_question_marks(cls, token: Token) -> None:
        """Removes question marks from the lemma.

        Args:
            token (Token): The original token.
        """

        if "?" != token.lemma_:
            question_mark_index = token.lemma_.find("?")
            if question_mark_index != -1:
                token.lemma_ = token.lemma_[:question_mark_index]

    @classmethod
    def _remove_date_suffixes(cls, token: Token) -> None:
        """Fixes the suffixes of dates.

        Args:
            token (Token): The original token.
        """

        try:
            if token.pos_ == "NOUN":
                token.lemma_ = cls._DATE_PATTERN.search(token.lemma_).group(1) + "."
        except (AttributeError):
            pass

    @classmethod
    def _remove_suffix_after_numbers(cls, token: Token) -> None:
        """Removes suffixes after numbers.

        Args:
            token (str): The original token.
        """

        try:
            if token.pos_ == "NUM":
                token.lemma_ = cls._NUMBER_PATTERN.search(token.text).group(0)
        except (AttributeError):
            pass


class RomanToArabic(Pipe):
    """Converts roman numerals to arabic numerals."""

    @staticmethod
    @Language.factory("roman_to_arabic", assigns=["token.lemma"], requires=["token.text"])
    def create_component(nlp: Language, name: str):
        return RomanToArabic()

    def __init__(self):
        self._regex = re.compile(r"^([IVXLCDM]+(-[IVXLCDM]+)*)[.]?$")
        self._rom_val = {
            "I": 1,
            "V": 5,
            "X": 10,
            "L": 50,
            "C": 100,
            "D": 500,
            "M": 1000,
        }

    def __call__(self, doc: Doc) -> Doc:
        for token in doc:
            try:
                if token.pos_ == "ADJ":
                    roman = self._regex.search(token.text).group(0)
                    romans = roman.split("-")
                    values = []

                    for r in romans:
                        dot = "." if "." == r[-1] else ""
                        r = r[:-1] if dot else r

                        int_val = 0
                        for i in range(len(r)):
                            if i > 0 and self._rom_val[r[i]] > self._rom_val[r[i - 1]]:
                                int_val += self._rom_val[r[i]] - 2 * self._rom_val[r[i - 1]]
                            else:
                                int_val += self._rom_val[r[i]]

                        values.append(str(int_val) + dot)

                    token.lemma_ = "-".join(values)
            except (AttributeError):
                pass
        return doc
