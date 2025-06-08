from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts
import re


class CzechHealthInsuranceNumberRecognizer(EntityRecognizer):
    """
    Rozpoznávač pro česká čísla pojištěnce zdravotní pojišťovny.
    
    Číslo pojištěnce je obvykle shodné s rodným číslem, ale může mít
    i jiný formát, zejména u cizinců nebo v případě náhradních identifikátorů.
    """
    
    def __init__(
        self,
        supported_language: str = "cs",
        supported_entity: str = "CZECH_HEALTH_INSURANCE_NUMBER",
        name: str = "Czech Health Insurance Number Recognizer",
        context: Optional[List[str]] = None,
    ):
        self.context = context if context else [
            "číslo pojištěnce", "č.p.", "pojištěnec", "zdravotní pojišťovna", 
            "pojištění", "insurance", "insured"
        ]
        super().__init__(
            supported_entities=[supported_entity],
            name=name,
            supported_language=supported_language,
        )
        
        # Regulární výraz pro číslo pojištěnce (podobné rodnému číslu)
        self.regex = r"\b(\d{6}/?[0-9]{3,4})\b"
        self.compiled_regex = re.compile(self.regex)
    
    def load(self) -> None:
        """Načtení rozpoznávače."""
        pass
    
    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """
        Analyzuje text a detekuje česká čísla pojištěnce.
        
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
            insurance_number = match.group(1)
            start, end = match.span()
            
            # Kontrola kontextu pro zvýšení přesnosti
            context_score = self._get_context_score(text, start, end)
            
            # Základní skóre je nižší než u rodného čísla, protože formát je méně specifický
            base_score = 0.7
            
            result = RecognizerResult(
                entity_type="CZECH_HEALTH_INSURANCE_NUMBER",
                start=start,
                end=end,
                score=base_score + context_score,
                analysis_explanation=None,
                recognition_metadata={
                    "match": insurance_number,
                },
            )
            results.append(result)
        
        return results
    
    def _get_context_score(self, text: str, start: int, end: int, window: int = 50) -> float:
        """
        Získá skóre na základě kontextu kolem detekovaného čísla pojištěnce.
        
        Args:
            text: Celý text
            start: Počáteční pozice čísla pojištěnce
            end: Koncová pozice čísla pojištěnce
            window: Velikost okna pro kontext
            
        Returns:
            Skóre kontextu (0.0 - 0.25)
        """
        # Získání kontextu před a za číslem pojištěnce
        before_text = text[max(0, start - window):start].lower()
        after_text = text[end:min(len(text), end + window)].lower()
        
        # Kontrola, zda se v kontextu vyskytují klíčová slova
        for keyword in self.context:
            if keyword.lower() in before_text or keyword.lower() in after_text:
                return 0.25  # Výrazné zvýšení skóre při nalezení kontextu
        
        return 0.0  # Žádný kontext nenalezen
