import logging
from typing import Dict, List, Optional, Union

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer.analyzer_engine import RecognizerResult

from src.common.models import Document, AnonymizedDocument, DetectedEntity, AnonymizedEntity
from src.detection.recognizers.czech_registry import CzechRecognizerRegistry

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class PresidioService:
    """
    Služba pro anonymizaci dokumentů pomocí Microsoft Presidio.
    """
    
    def __init__(self):
        """
        Inicializace služby Presidio.
        """
        # Inicializace NLP enginu (spaCy)
        # Použití pouze anglického modelu jako fallback, protože český model není dostupný pro spaCy 3.8.7
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [
                {"lang_code": "en", "model_name": "en_core_web_sm"}
            ]
        }
        self.nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
        
        # Inicializace registru rozpoznávačů
        self.registry = RecognizerRegistry()
        
        # Registrace specializovaných českých rozpoznávačů
        CzechRecognizerRegistry.register_czech_recognizers(self.registry)
        
        # Inicializace analyzeru
        self.analyzer = AnalyzerEngine(
            nlp_engine=self.nlp_engine,
            registry=self.registry
        )
        
        # Inicializace anonymizeru
        self.anonymizer = AnonymizerEngine()
        
        logger.info("Presidio service initialized with English model (fallback) and Czech recognizers")
    
    def analyze_text(self, text: str, language: str = "en") -> List[DetectedEntity]:
        """
        Analyzuje text a detekuje entity.
        
        Args:
            text: Text k analýze
            language: Jazyk textu (výchozí: angličtina jako fallback)
            
        Returns:
            Seznam detekovaných entit
        """
        logger.info(f"Analyzing text (length: {len(text)}) using language: {language}")
        
        # Seznam entit k detekci (standardní + české specializované)
        entities = None  # Všechny podporované entity
        
        # Analýza textu pomocí Presidio Analyzer
        results = self.analyzer.analyze(
            text=text,
            language=language,
            entities=entities,
            allow_list=None,
            score_threshold=0.3  # Nižší práh pro vyšší recall
        )
        
        # Konverze výsledků na DetectedEntity
        detected_entities = []
        for result in results:
            entity = DetectedEntity(
                entity_type=result.entity_type,
                start=result.start,
                end=result.end,
                score=result.score,
                text=text[result.start:result.end],
                context=self._get_context(text, result.start, result.end)
            )
            detected_entities.append(entity)
        
        logger.info(f"Detected {len(detected_entities)} entities")
        return detected_entities, results  # Vracíme i původní výsledky pro anonymizaci
    
    def anonymize_text(
        self, 
        text: str, 
        entities: List[DetectedEntity],
        analyzer_results: List[RecognizerResult]
    ) -> tuple[str, List[AnonymizedEntity]]:
        """
        Anonymizuje text na základě detekovaných entit.
        
        Args:
            text: Text k anonymizaci
            entities: Seznam detekovaných entit
            analyzer_results: Původní výsledky z analyzeru
            
        Returns:
            Tuple obsahující anonymizovaný text a seznam anonymizovaných entit
        """
        logger.info(f"Anonymizing text with {len(entities)} entities")
        
        # Anonymizace textu s použitím původních výsledků analyzeru
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results
        )
        
        # Vytvoření seznamu anonymizovaných entit
        anonymized_entities = []
        for i, entity in enumerate(entities):
            if i < len(anonymized_result.items):
                anonymized_entity = AnonymizedEntity(
                    original_entity=entity,
                    anonymized_text=anonymized_result.items[i].text,
                    operator_name=anonymized_result.items[i].operator,
                    metadata={}
                )
                anonymized_entities.append(anonymized_entity)
        
        logger.info(f"Text anonymized successfully")
        return anonymized_result.text, anonymized_entities
    
    def process_document(self, document: Document) -> AnonymizedDocument:
        """
        Zpracuje dokument - detekuje entity a anonymizuje text.
        
        Args:
            document: Dokument ke zpracování
            
        Returns:
            Anonymizovaný dokument
        """
        logger.info(f"Processing document: {document.id}")
        
        # Detekce entit - použití angličtiny jako fallback
        detected_entities, analyzer_results = self.analyze_text(document.content, language="en")
        
        # Anonymizace textu
        anonymized_text, anonymized_entities = self.anonymize_text(
            document.content, 
            detected_entities,
            analyzer_results
        )
        
        # Vytvoření anonymizovaného dokumentu
        anonymized_document = AnonymizedDocument(
            content=anonymized_text,
            content_type=document.content_type,
            original_document_id=document.id,
            entities=anonymized_entities,
            metadata=document.metadata,
            statistics={
                "total_entities_detected": len(detected_entities),
                "entities_by_type": self._count_entities_by_type(detected_entities),
                "processing_time_ms": 0  # Toto by mělo být měřeno
            }
        )
        
        logger.info(f"Document processed successfully")
        return anonymized_document
    
    def _get_context(self, text: str, start: int, end: int, window: int = 20) -> str:
        """
        Získá kontext kolem entity.
        
        Args:
            text: Celý text
            start: Počáteční pozice entity
            end: Koncová pozice entity
            window: Velikost okna pro kontext
            
        Returns:
            Kontext kolem entity
        """
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def _count_entities_by_type(self, entities: List[DetectedEntity]) -> Dict[str, int]:
        """
        Spočítá entity podle typu.
        
        Args:
            entities: Seznam entit
            
        Returns:
            Slovník s počty entit podle typu
        """
        counts = {}
        for entity in entities:
            if entity.entity_type in counts:
                counts[entity.entity_type] += 1
            else:
                counts[entity.entity_type] = 1
        return counts
