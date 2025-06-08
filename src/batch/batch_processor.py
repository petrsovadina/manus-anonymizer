import logging
import os
import json
import time
from typing import Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

from src.common.models import Document, AnonymizedDocument, BatchProcessingConfig

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class BatchProcessor:
    """
    Služba pro dávkové zpracování dokumentů.
    
    Umožňuje zpracování většího množství dokumentů v dávkách,
    s podporou pro zotavení z chyb, monitoring a audit.
    """
    
    def __init__(
        self,
        presidio_service,
        input_dir: str,
        output_dir: str,
        error_dir: str,
        audit_dir: str,
        batch_size: int = 10,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        """
        Inicializace služby pro dávkové zpracování.
        
        Args:
            presidio_service: Instance PresidioService pro anonymizaci
            input_dir: Adresář se vstupními dokumenty
            output_dir: Adresář pro výstupní anonymizované dokumenty
            error_dir: Adresář pro dokumenty s chybou zpracování
            audit_dir: Adresář pro auditní záznamy
            batch_size: Velikost dávky (počet dokumentů zpracovaných najednou)
            max_retries: Maximální počet pokusů o zpracování dokumentu
            retry_delay: Prodleva mezi pokusy o zpracování (v sekundách)
        """
        self.presidio_service = presidio_service
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.error_dir = error_dir
        self.audit_dir = audit_dir
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Vytvoření adresářů, pokud neexistují
        for directory in [input_dir, output_dir, error_dir, audit_dir]:
            os.makedirs(directory, exist_ok=True)
        
        logger.info(f"Batch processor initialized with batch size {batch_size}")
    
    def process_batch(self, config: Optional[BatchProcessingConfig] = None) -> Dict:
        """
        Zpracuje dávku dokumentů.
        
        Args:
            config: Konfigurace dávkového zpracování
            
        Returns:
            Statistiky o zpracování dávky
        """
        start_time = time.time()
        
        # Použití výchozí konfigurace, pokud není poskytnuta
        if not config:
            config = BatchProcessingConfig()
        
        # Získání seznamu souborů ke zpracování
        input_files = self._get_input_files(config.file_pattern)
        
        # Omezení počtu souborů podle velikosti dávky
        if config.max_files and config.max_files > 0:
            input_files = input_files[:config.max_files]
        
        # Inicializace statistik
        stats = {
            "total_files": len(input_files),
            "processed_files": 0,
            "successful_files": 0,
            "failed_files": 0,
            "total_entities_detected": 0,
            "entities_by_type": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "processing_time_ms": 0,
        }
        
        # Zpracování souborů v dávkách
        for i, file_path in enumerate(input_files):
            logger.info(f"Processing file {i+1}/{len(input_files)}: {file_path}")
            
            try:
                # Načtení dokumentu
                document = self._load_document(file_path)
                
                # Anonymizace dokumentu
                anonymized_document = self._process_document_with_retry(document)
                
                # Uložení anonymizovaného dokumentu
                output_path = self._save_anonymized_document(anonymized_document)
                
                # Aktualizace statistik
                stats["processed_files"] += 1
                stats["successful_files"] += 1
                stats["total_entities_detected"] += len(anonymized_document.entities)
                
                # Aktualizace počtu entit podle typu
                for entity in anonymized_document.entities:
                    entity_type = entity.original_entity.entity_type
                    if entity_type in stats["entities_by_type"]:
                        stats["entities_by_type"][entity_type] += 1
                    else:
                        stats["entities_by_type"][entity_type] = 1
                
                # Vytvoření auditního záznamu
                self._create_audit_record(document, anonymized_document, True)
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
                
                # Přesun souboru do adresáře s chybami
                self._move_to_error_dir(file_path)
                
                # Aktualizace statistik
                stats["processed_files"] += 1
                stats["failed_files"] += 1
                
                # Vytvoření auditního záznamu pro chybu
                self._create_audit_record(document if 'document' in locals() else None, None, False, str(e))
        
        # Dokončení statistik
        end_time = time.time()
        stats["end_time"] = datetime.now().isoformat()
        stats["processing_time_ms"] = int((end_time - start_time) * 1000)
        
        # Uložení souhrnných statistik
        self._save_batch_stats(stats)
        
        logger.info(f"Batch processing completed: {stats['successful_files']} successful, {stats['failed_files']} failed")
        return stats
    
    def _get_input_files(self, file_pattern: str = "*.txt") -> List[str]:
        """
        Získá seznam souborů ke zpracování.
        
        Args:
            file_pattern: Vzor pro filtrování souborů
            
        Returns:
            Seznam cest k souborům
        """
        input_path = Path(self.input_dir)
        return [str(f) for f in input_path.glob(file_pattern) if f.is_file()]
    
    def _load_document(self, file_path: str) -> Document:
        """
        Načte dokument ze souboru.
        
        Args:
            file_path: Cesta k souboru
            
        Returns:
            Načtený dokument
        """
        file_name = os.path.basename(file_path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Určení typu obsahu podle přípony souboru
        content_type = "text/plain"
        if file_path.endswith(".json"):
            content_type = "application/json"
        elif file_path.endswith(".xml"):
            content_type = "application/xml"
        elif file_path.endswith(".html"):
            content_type = "text/html"
        
        # Vytvoření dokumentu
        document = Document(
            id=file_name,
            content=content,
            content_type=content_type,
            metadata={
                "source_file": file_path,
                "file_size": os.path.getsize(file_path),
                "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                "modified_at": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            }
        )
        
        return document
    
    def _process_document_with_retry(self, document: Document) -> AnonymizedDocument:
        """
        Zpracuje dokument s možností opakování při chybě.
        
        Args:
            document: Dokument ke zpracování
            
        Returns:
            Anonymizovaný dokument
            
        Raises:
            Exception: Pokud se zpracování nezdaří ani po maximálním počtu pokusů
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return self.presidio_service.process_document(document)
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt+1}/{self.max_retries} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        # Pokud se dostaneme sem, všechny pokusy selhaly
        raise last_exception or Exception("Failed to process document after multiple attempts")
    
    def _save_anonymized_document(self, document: AnonymizedDocument) -> str:
        """
        Uloží anonymizovaný dokument.
        
        Args:
            document: Anonymizovaný dokument k uložení
            
        Returns:
            Cesta k uloženému souboru
        """
        # Vytvoření cesty k výstupnímu souboru
        output_file = os.path.join(self.output_dir, document.original_document_id)
        
        # Uložení obsahu dokumentu
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(document.content)
        
        # Uložení metadat a statistik do doprovodného JSON souboru
        metadata_file = f"{output_file}.meta.json"
        metadata = {
            "original_document_id": document.original_document_id,
            "content_type": document.content_type,
            "metadata": document.metadata,
            "statistics": document.statistics,
            "anonymized_at": datetime.now().isoformat(),
        }
        
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def _move_to_error_dir(self, file_path: str) -> str:
        """
        Přesune soubor do adresáře s chybami.
        
        Args:
            file_path: Cesta k souboru
            
        Returns:
            Nová cesta k souboru
        """
        file_name = os.path.basename(file_path)
        error_file = os.path.join(self.error_dir, file_name)
        
        # Pokud soubor s tímto názvem již existuje, přidáme časové razítko
        if os.path.exists(error_file):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name_parts = os.path.splitext(file_name)
            error_file = os.path.join(
                self.error_dir, f"{file_name_parts[0]}_{timestamp}{file_name_parts[1]}"
            )
        
        # Přesun souboru
        os.rename(file_path, error_file)
        
        return error_file
    
    def _create_audit_record(
        self,
        original_document: Optional[Document],
        anonymized_document: Optional[AnonymizedDocument],
        success: bool,
        error_message: Optional[str] = None,
    ) -> str:
        """
        Vytvoří auditní záznam o zpracování dokumentu.
        
        Args:
            original_document: Původní dokument
            anonymized_document: Anonymizovaný dokument
            success: Příznak úspěšného zpracování
            error_message: Chybová zpráva v případě neúspěchu
            
        Returns:
            Cesta k auditnímu záznamu
        """
        # Vytvoření základních informací pro audit
        audit_data = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "document_id": original_document.id if original_document else None,
        }
        
        # Přidání informací o zpracování
        if success and anonymized_document:
            audit_data.update({
                "entities_detected": len(anonymized_document.entities),
                "entities_by_type": anonymized_document.statistics.get("entities_by_type", {}),
                "processing_time_ms": anonymized_document.statistics.get("processing_time_ms", 0),
            })
        elif error_message:
            audit_data["error_message"] = error_message
        
        # Vytvoření názvu auditního souboru
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        document_id = original_document.id if original_document else "unknown"
        audit_file = os.path.join(
            self.audit_dir, f"audit_{document_id}_{timestamp}.json"
        )
        
        # Uložení auditního záznamu
        with open(audit_file, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)
        
        return audit_file
    
    def _save_batch_stats(self, stats: Dict) -> str:
        """
        Uloží statistiky o zpracování dávky.
        
        Args:
            stats: Statistiky o zpracování
            
        Returns:
            Cesta k souboru se statistikami
        """
        # Vytvoření názvu souboru se statistikami
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        stats_file = os.path.join(
            self.audit_dir, f"batch_stats_{timestamp}.json"
        )
        
        # Uložení statistik
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        return stats_file
