import re
from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts


class CzechBirthNumberRecognizer(EntityRecognizer):
    """
    Rozpoznávač pro česká rodná čísla.
    
    Formát rodného čísla: YYMMDD/XXXX, kde:
    - YY je rok narození (00-99)
    - MM je měsíc narození (01-12, případně +50 pro ženy)
    - DD je den narození (01-31)
    - / je oddělovač (může být vynechán u starších rodných čísel)
    - XXXX je čtyřmístné číslo, kde poslední číslice je kontrolní
    """
    
    def __init__(
        self,
        supported_language: str = "cs",
        supported_entity: str = "CZECH_BIRTH_NUMBER",
        name: str = "Czech Birth Number Recognizer",
        context: Optional[List[str]] = None,
    ):
        self.context = context if context else ["rodné číslo", "r.č.", "rč", "birth number"]
        super().__init__(
            supported_entities=[supported_entity],
            name=name,
            supported_language=supported_language,
        )
        
        # Regulární výraz pro české rodné číslo
        self.regex = r"\b(\d{6}/?[0-9]{3,4})\b"
        self.compiled_regex = re.compile(self.regex)
    
    def load(self) -> None:
        """Načtení rozpoznávače."""
        pass
    
    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """
        Analyzuje text a detekuje česká rodná čísla.
        
        Args:
            text: Text k analýze
            entities: Seznam entit k detekci
            nlp_artifacts: NLP artefakty
            
        Returns:
            Seznam detekovaných entit
        """
        results = []
        
        if not self.supported_entities or not entities:
            return results
        
        if not any(entity in self.supported_entities for entity in entities):
            return results
        
        matches = self.compiled_regex.finditer(text)
        for match in matches:
            birth_number = match.group(1)
            if self._is_valid_birth_number(birth_number):
                start, end = match.span()
                
                # Kontrola kontextu pro zvýšení přesnosti
                context_score = self._get_context_score(text, start, end)
                
                result = RecognizerResult(
                    entity_type="CZECH_BIRTH_NUMBER",
                    start=start,
                    end=end,
                    score=0.85 + context_score,  # Základní skóre + kontext
                    analysis_explanation=None,
                    recognition_metadata={
                        "match": birth_number,
                    },
                )
                results.append(result)
        
        return results
    
    def _is_valid_birth_number(self, birth_number: str) -> bool:
        """
        Ověří, zda je rodné číslo validní.
        
        Args:
            birth_number: Rodné číslo k ověření
            
        Returns:
            True, pokud je rodné číslo validní, jinak False
        """
        # Odstranění lomítka, pokud existuje
        birth_number = birth_number.replace("/", "")
        
        # Kontrola délky
        if len(birth_number) not in [9, 10]:
            return False
        
        # Kontrola formátu YY, MM, DD
        try:
            year = int(birth_number[0:2])
            month = int(birth_number[2:4])
            day = int(birth_number[4:6])
            
            # Kontrola měsíce (1-12 pro muže, 51-62 pro ženy)
            if not ((1 <= month <= 12) or (51 <= month <= 62)):
                return False
            
            # Kontrola dne (1-31)
            if not (1 <= day <= 31):
                return False
            
            # Kontrola modulo 11 pro rodná čísla po roce 1954
            if len(birth_number) == 10:
                # Kontrolní číslice je poslední číslice
                number = int(birth_number[:9])
                check_digit = int(birth_number[9])
                
                # Kontrola modulo 11
                if number % 11 != check_digit:
                    # Speciální případ pro modulo 10
                    if number % 11 == 10 and check_digit == 0:
                        return True
                    return False
            
            return True
        except ValueError:
            return False
    
    def _get_context_score(self, text: str, start: int, end: int, window: int = 35) -> float:
        """
        Získá skóre na základě kontextu kolem detekovaného rodného čísla.
        
        Args:
            text: Celý text
            start: Počáteční pozice rodného čísla
            end: Koncová pozice rodného čísla
            window: Velikost okna pro kontext
            
        Returns:
            Skóre kontextu (0.0 - 0.15)
        """
        # Získání kontextu před a za rodným číslem
        before_text = text[max(0, start - window):start].lower()
        after_text = text[end:min(len(text), end + window)].lower()
        
        # Kontrola, zda se v kontextu vyskytují klíčová slova
        for keyword in self.context:
            if keyword.lower() in before_text or keyword.lower() in after_text:
                return 0.15  # Zvýšení skóre při nalezení kontextu
        
        return 0.0  # Žádný kontext nenalezen
