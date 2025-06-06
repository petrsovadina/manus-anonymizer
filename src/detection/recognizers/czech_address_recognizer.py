import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts


class CzechAddressRecognizer(EntityRecognizer):
    """
    Rozpoznávač pro české adresy.
    
    Detekuje adresy v českém formátu, včetně ulic, čísel popisných, měst a PSČ.
    """
    
    def __init__(
        self,
        supported_language: str = "cs",
        supported_entity: str = "CZECH_ADDRESS",
        name: str = "Czech Address Recognizer",
        context: Optional[List[str]] = None,
    ):
        self.context = context if context else [
            "adresa", "bydliště", "trvalé bydliště", "přechodné bydliště",
            "ulice", "náměstí", "třída", "nábřeží", "sídliště"
        ]
        
        super().__init__(
            supported_entities=[supported_entity],
            name=name,
            supported_language=supported_language,
        )
        
        # Regulární výraz pro PSČ
        self.zip_regex = r"\b([0-9]{3}\s?[0-9]{2})\b"
        self.compiled_zip_regex = re.compile(self.zip_regex)
        
        # Regulární výraz pro číslo popisné/orientační
        self.house_number_regex = r"\b(\d+[a-zA-Z]?(/\d+[a-zA-Z]?)?)\b"
        self.compiled_house_number_regex = re.compile(self.house_number_regex)
        
        # Klíčová slova pro detekci ulic
        self.street_keywords = [
            "ulice", "ul.", "náměstí", "nám.", "třída", "tř.", "nábřeží", 
            "sídliště", "sídl.", "bulvár", "alej", "park"
        ]
    
    def load(self) -> None:
        """Načtení rozpoznávače."""
        pass
    
    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """
        Analyzuje text a detekuje české adresy.
        
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
        
        # Detekce PSČ jako kotvy pro adresy
        zip_matches = self.compiled_zip_regex.finditer(text)
        for zip_match in zip_matches:
            zip_code = zip_match.group(1)
            zip_start, zip_end = zip_match.span()
            
            # Hledání adresy v okolí PSČ
            address_start = max(0, zip_start - 100)  # Hledáme až 100 znaků před PSČ
            address_end = min(len(text), zip_end + 30)  # A až 30 znaků za PSČ
            
            # Extrakce potenciální adresy
            address_text = text[address_start:address_end]
            
            # Kontrola kontextu pro zvýšení přesnosti
            context_score = self._get_context_score(text, address_start, address_end)
            
            # Vytvoření výsledku
            result = RecognizerResult(
                entity_type="CZECH_ADDRESS",
                start=address_start,
                end=address_end,
                score=0.7 + context_score,  # Základní skóre + kontext
                analysis_explanation=None,
                recognition_metadata={
                    "zip_code": zip_code,
                    "address_text": address_text
                },
            )
            results.append(result)
        
        # Detekce adres podle klíčových slov pro ulice
        if nlp_artifacts and nlp_artifacts.tokens:
            for i, token in enumerate(nlp_artifacts.tokens):
                token_text = token.text.lower()
                
                # Kontrola, zda token je klíčové slovo pro ulici
                if token_text in self.street_keywords or any(token_text.startswith(kw) for kw in self.street_keywords):
                    # Hledání čísla popisného v okolí
                    surrounding_text_start = max(0, token.idx - 10)
                    surrounding_text_end = min(len(text), token.idx + 100)
                    surrounding_text = text[surrounding_text_start:surrounding_text_end]
                    
                    house_number_match = self.compiled_house_number_regex.search(surrounding_text)
                    if house_number_match:
                        # Extrakce potenciální adresy
                        address_start = surrounding_text_start
                        address_end = surrounding_text_start + house_number_match.end()
                        address_text = text[address_start:address_end]
                        
                        # Kontrola kontextu pro zvýšení přesnosti
                        context_score = self._get_context_score(text, address_start, address_end)
                        
                        # Vytvoření výsledku
                        result = RecognizerResult(
                            entity_type="CZECH_ADDRESS",
                            start=address_start,
                            end=address_end,
                            score=0.65 + context_score,  # Nižší základní skóre než u PSČ
                            analysis_explanation=None,
                            recognition_metadata={
                                "street_keyword": token_text,
                                "address_text": address_text
                            },
                        )
                        results.append(result)
        
        return results
    
    def _get_context_score(self, text: str, start: int, end: int, window: int = 50) -> float:
        """
        Získá skóre na základě kontextu kolem detekované adresy.
        
        Args:
            text: Celý text
            start: Počáteční pozice adresy
            end: Koncová pozice adresy
            window: Velikost okna pro kontext
            
        Returns:
            Skóre kontextu (0.0 - 0.2)
        """
        # Získání kontextu před a za adresou
        before_text = text[max(0, start - window):start].lower()
        after_text = text[end:min(len(text), end + window)].lower()
        
        # Kontrola, zda se v kontextu vyskytují klíčová slova
        for keyword in self.context:
            if keyword.lower() in before_text or keyword.lower() in after_text:
                return 0.2  # Zvýšení skóre při nalezení kontextu
        
        return 0.0  # Žádný kontext nenalezen
