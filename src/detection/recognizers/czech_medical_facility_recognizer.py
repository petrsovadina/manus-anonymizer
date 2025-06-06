import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts


class CzechMedicalFacilityRecognizer(EntityRecognizer):
    """
    Rozpoznávač pro názvy českých zdravotnických zařízení.
    
    Detekuje názvy nemocnic, klinik, zdravotních středisek a dalších zdravotnických zařízení.
    """
    
    def __init__(
        self,
        supported_language: str = "cs",
        supported_entity: str = "CZECH_MEDICAL_FACILITY",
        name: str = "Czech Medical Facility Recognizer",
        context: Optional[List[str]] = None,
    ):
        self.context = context if context else []
        
        # Klíčová slova pro detekci zdravotnických zařízení
        self.facility_keywords = [
            "nemocnice", "fakultní nemocnice", "fn ", "fn,", "klinika", "poliklinika",
            "zdravotní středisko", "zdravotnické zařízení", "léčebna", "sanatorium",
            "ordinace", "ambulance", "ústav", "centrum", "oddělení", "lékařský dům",
            "lékařské centrum", "zdravotní centrum", "rehabilitační ústav", "hospic"
        ]
        
        super().__init__(
            supported_entities=[supported_entity],
            name=name,
            supported_language=supported_language,
        )
    
    def load(self) -> None:
        """Načtení rozpoznávače."""
        pass
    
    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """
        Analyzuje text a detekuje názvy zdravotnických zařízení.
        
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
        
        # Použití NLP artefaktů pro detekci entit
        if not nlp_artifacts or not nlp_artifacts.entities:
            return results
        
        # Procházení vět v textu
        doc = nlp_artifacts.doc
        for sent in doc.sents:
            sent_text = sent.text.strip()
            
            # Kontrola, zda věta obsahuje klíčová slova pro zdravotnická zařízení
            for keyword in self.facility_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in sent_text.lower():
                    # Hledání názvu zařízení v okolí klíčového slova
                    keyword_index = sent_text.lower().find(keyword_lower)
                    start_index = max(0, keyword_index - 30)
                    end_index = min(len(sent_text), keyword_index + len(keyword) + 50)
                    
                    # Extrakce potenciálního názvu zařízení
                    facility_text = sent_text[start_index:end_index]
                    
                    # Výpočet absolutní pozice v textu
                    abs_start = sent.start_char + start_index
                    abs_end = sent.start_char + end_index
                    
                    # Vytvoření výsledku
                    result = RecognizerResult(
                        entity_type="CZECH_MEDICAL_FACILITY",
                        start=abs_start,
                        end=abs_end,
                        score=0.65,  # Střední skóre, protože detekce je založena na klíčových slovech
                        analysis_explanation=None,
                        recognition_metadata={
                            "keyword": keyword,
                            "facility_text": facility_text
                        },
                    )
                    results.append(result)
                    break  # Přeskočení dalších klíčových slov pro tuto větu
        
        return results
