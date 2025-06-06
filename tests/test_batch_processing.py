# Testovací skript pro MedDocAI Anonymizer

import os
import sys
import json
import logging
import argparse
from pathlib import Path

# Nastavení cesty k projektu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.detection.presidio_service import PresidioService
from src.common.models import Document, BatchProcessingConfig
from src.batch.batch_processor import BatchProcessor

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def generate_test_data(output_dir: str, num_files: int = 10):
    """
    Generuje testovací data pro anonymizaci.
    
    Args:
        output_dir: Adresář pro výstupní soubory
        num_files: Počet souborů k vygenerování
    """
    logger.info(f"Generating {num_files} test files in {output_dir}")
    
    # Vytvoření adresáře, pokud neexistuje
    os.makedirs(output_dir, exist_ok=True)
    
    # Testovací data s různými typy českých entit
    test_data = [
        "Pacient Jan Novák, rodné číslo 760506/1234, narozen 6.5.1976, bytem Dlouhá 123, Praha 1, 110 00, "
        "byl přijat do Fakultní nemocnice v Motole s diagnózou J45.0 (Astma). "
        "Číslo pojištěnce: 7605061234, pojišťovna: 111.",
        
        "Pacientka Marie Svobodová, r.č. 895623/1234, bytem náměstí Míru 45, Brno, 602 00, "
        "byla odeslána do Nemocnice Na Bulovce k vyšetření. "
        "Diagnóza: C50.1, E11.9. Kontakt: svobodova@email.cz, tel: +420 777 888 999.",
        
        "Propouštěcí zpráva: Pacient Josef Dvořák (r.č. 590728/1122) byl hospitalizován "
        "v Ústřední vojenské nemocnici od 15.3.2025 do 28.3.2025 s diagnózou I21.0. "
        "Adresa: Krátká 7, Olomouc, 779 00. Ošetřující lékař: MUDr. Petr Černý.",
        
        "Žádanka o vyšetření pro pacienta Tomáš Procházka, číslo pojištěnce 880417/3344, "
        "trvalé bydliště Polní 56, Ostrava, 702 00. Diagnóza: F20.0, G40.3. "
        "Odesílající lékař: MUDr. Jana Bílá, Poliklinika Jih, Ostrava.",
        
        "Výsledky laboratorního vyšetření pacienta Jiří Kučera (760812/5566), "
        "bytem Lipová 789, Plzeň, 301 00. Diagnóza: E10.5. "
        "Vyšetření provedeno v Centrální laboratoři FN Plzeň dne 5.4.2025.",
    ]
    
    # Generování souborů
    for i in range(num_files):
        # Výběr testovacích dat (cyklicky)
        data_index = i % len(test_data)
        content = test_data[data_index]
        
        # Vytvoření názvu souboru
        file_name = f"test_document_{i+1:03d}.txt"
        file_path = os.path.join(output_dir, file_name)
        
        # Uložení souboru
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Generated test file: {file_path}")

def run_batch_test(input_dir: str, output_dir: str, error_dir: str, audit_dir: str, batch_size: int = 5):
    """
    Spustí test dávkového zpracování.
    
    Args:
        input_dir: Adresář se vstupními soubory
        output_dir: Adresář pro výstupní soubory
        error_dir: Adresář pro soubory s chybou
        audit_dir: Adresář pro auditní záznamy
        batch_size: Velikost dávky
    """
    logger.info("Initializing Presidio service")
    presidio_service = PresidioService()
    
    logger.info(f"Initializing batch processor with batch size {batch_size}")
    batch_processor = BatchProcessor(
        presidio_service=presidio_service,
        input_dir=input_dir,
        output_dir=output_dir,
        error_dir=error_dir,
        audit_dir=audit_dir,
        batch_size=batch_size,
    )
    
    logger.info("Starting batch processing")
    config = BatchProcessingConfig(
        file_pattern="*.txt",
        max_files=0,  # Zpracovat všechny soubory
    )
    
    stats = batch_processor.process_batch(config)
    
    logger.info("Batch processing completed")
    logger.info(f"Total files: {stats['total_files']}")
    logger.info(f"Successful: {stats['successful_files']}")
    logger.info(f"Failed: {stats['failed_files']}")
    logger.info(f"Total entities detected: {stats['total_entities_detected']}")
    logger.info(f"Processing time: {stats['processing_time_ms']} ms")
    
    # Výpis detekovaných entit podle typu
    logger.info("Entities by type:")
    for entity_type, count in stats["entities_by_type"].items():
        logger.info(f"  {entity_type}: {count}")
    
    return stats

def main():
    """
    Hlavní funkce pro spuštění testů.
    """
    parser = argparse.ArgumentParser(description="Test MedDocAI Anonymizer")
    parser.add_argument("--generate", action="store_true", help="Generate test data")
    parser.add_argument("--num-files", type=int, default=10, help="Number of test files to generate")
    parser.add_argument("--batch-size", type=int, default=5, help="Batch size for processing")
    parser.add_argument("--input-dir", default="./test_data/input", help="Input directory")
    parser.add_argument("--output-dir", default="./test_data/output", help="Output directory")
    parser.add_argument("--error-dir", default="./test_data/error", help="Error directory")
    parser.add_argument("--audit-dir", default="./test_data/audit", help="Audit directory")
    
    args = parser.parse_args()
    
    # Vytvoření adresářů
    for directory in [args.input_dir, args.output_dir, args.error_dir, args.audit_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # Generování testovacích dat, pokud je požadováno
    if args.generate:
        generate_test_data(args.input_dir, args.num_files)
    
    # Spuštění testu dávkového zpracování
    stats = run_batch_test(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        error_dir=args.error_dir,
        audit_dir=args.audit_dir,
        batch_size=args.batch_size,
    )
    
    # Uložení výsledků testu
    results_file = os.path.join(args.audit_dir, "test_results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Test results saved to {results_file}")

if __name__ == "__main__":
    main()
