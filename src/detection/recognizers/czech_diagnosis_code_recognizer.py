import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts


class CzechMedicalDiagnosisCodeRecognizer(EntityRecognizer):
    """
    Rozpoznávač pro české kódy diagnóz (MKN-10).
    
    Formát kódu MKN-10: Písmeno následované 2-3 číslicemi, případně s tečkou a dalšími číslicemi.
    Například: J45.0, C50, F20.0
    """
    
    def __init__(
        self,
        supported_language: str = "cs",
        supported_entity: str = "CZECH_DIAGNOSIS_CODE",
        name: str = "Czech Medical Diagnosis Code Recognizer",
        context: Optional[List[str]] = None,
    ):
        self.context = context if context else [
            "diagnóza", "dg.", "dg:", "diagnóza:", "MKN-10", "ICD-10", 
            "kód diagnózy", "kód dg", "kód MKN"
        ]
        super().__init__(
            supported_entities=[supported_entity],
            name=name,
            supported_language=supported_language,
        )
        
        # Regulární výraz pro kód diagnózy MKN-10
        self.regex = r"\b([A-Z][0-9]{2}(\.[0-9]{1,2})?)\b"
        self.compiled_regex = re.compile(self.regex)
    
    def load(self) -> None:
        """Načtení rozpoznávače."""
        pass
    
    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """
        Analyzuje text a detekuje kódy diagnóz.
        
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
            diagnosis_code = match.group(1)
            start, end = match.span()
            
            # Kontrola kontextu pro zvýšení přesnosti
            context_score = self._get_context_score(text, start, end)
            
            # Základní skóre je střední, protože formát je specifický, ale může být i falešně pozitivní
            base_score = 0.65
            
            result = RecognizerResult(
                entity_type="CZECH_DIAGNOSIS_CODE",
                start=start,
                end=end,
                score=base_score + context_score,
                analysis_explanation=None,
                recognition_metadata={
                    "match": diagnosis_code,
                },
            )
            results.append(result)
        
        return results
    
    def _get_context_score(self, text: str, start: int, end: int, window: int = 40) -> float:
        """
        Získá skóre na základě kontextu kolem detekovaného kódu diagnózy.
        
        Args:
            text: Celý text
            start: Počáteční pozice kódu diagnózy
            end: Koncová pozice kódu diagnózy
            window: Velikost okna pro kontext
            
        Returns:
            Skóre kontextu (0.0 - 0.3)
        """
        # Získání kontextu před a za kódem diagnózy
        before_text = text[max(0, start - window):start].lower()
        after_text = text[end:min(len(text), end + window)].lower()
        
        # Kontrola, zda se v kontextu vyskytují klíčová slova
        for keyword in self.context:
            if keyword.lower() in before_text or keyword.lower() in after_text:
                return 0.3  # Výrazné zvýšení skóre při nalezení kontextu
        
        return 0.0  # Žádný kontext nenalezen
