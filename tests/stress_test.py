# Zátěžový test pro MedDocAI Anonymizer

import os
import sys
import json
import logging
import argparse
import time
from pathlib import Path
import multiprocessing

# Nastavení cesty k projektu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.detection.presidio_service import PresidioService
from src.common.models import Document, BatchProcessingConfig
from src.batch.parallel_batch_processor import ParallelBatchProcessor

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def generate_large_test_dataset(output_dir: str, num_files: int = 100, file_size_kb: int = 10):
    """
    Generuje velký testovací dataset pro zátěžové testování.
    
    Args:
        output_dir: Adresář pro výstupní soubory
        num_files: Počet souborů k vygenerování
        file_size_kb: Přibližná velikost každého souboru v KB
    """
    logger.info(f"Generating {num_files} test files (approx. {file_size_kb} KB each) in {output_dir}")
    
    # Vytvoření adresáře, pokud neexistuje
    os.makedirs(output_dir, exist_ok=True)
    
    # Základní testovací data s různými typy českých entit
    test_data_templates = [
        "Pacient {name}, rodné číslo {birth_number}, narozen {birth_date}, bytem {address}, "
        "byl přijat do {hospital} s diagnózou {diagnosis_code} ({diagnosis_name}). "
        "Číslo pojištěnce: {insurance_number}, pojišťovna: {insurance_company}.",
        
        "Pacientka {name}, r.č. {birth_number}, bytem {address}, "
        "byla odeslána do {hospital} k vyšetření. "
        "Diagnóza: {diagnosis_code}, {diagnosis_code2}. Kontakt: {email}, tel: {phone}.",
        
        "Propouštěcí zpráva: Pacient {name} (r.č. {birth_number}) byl hospitalizován "
        "v {hospital} od {admission_date} do {discharge_date} s diagnózou {diagnosis_code}. "
        "Adresa: {address}. Ošetřující lékař: {doctor}.",
        
        "Žádanka o vyšetření pro pacienta {name}, číslo pojištěnce {insurance_number}, "
        "trvalé bydliště {address}. Diagnóza: {diagnosis_code}, {diagnosis_code2}. "
        "Odesílající lékař: {doctor}, {hospital}.",
        
        "Výsledky laboratorního vyšetření pacienta {name} ({birth_number}), "
        "bytem {address}. Diagnóza: {diagnosis_code}. "
        "Vyšetření provedeno v {lab} dne {test_date}.",
    ]
    
    # Data pro nahrazení v šablonách
    replacements = {
        "name": [
            "Jan Novák", "Marie Svobodová", "Josef Dvořák", "Tomáš Procházka", "Jiří Kučera",
            "Eva Nováková", "Petr Černý", "Jana Bílá", "Martin Veselý", "Lucie Horáková"
        ],
        "birth_number": [
            "760506/1234", "895623/1234", "590728/1122", "880417/3344", "760812/5566",
            "655302/7788", "920714/9900", "780203/1122", "850609/3344", "710405/5566"
        ],
        "birth_date": [
            "6.5.1976", "23.6.1989", "28.7.1959", "17.4.1988", "12.8.1976",
            "2.3.1965", "14.7.1992", "3.2.1978", "9.6.1985", "5.4.1971"
        ],
        "address": [
            "Dlouhá 123, Praha 1, 110 00", "náměstí Míru 45, Brno, 602 00", "Krátká 7, Olomouc, 779 00",
            "Polní 56, Ostrava, 702 00", "Lipová 789, Plzeň, 301 00", "Školní 42, Liberec, 460 01",
            "Hlavní 321, České Budějovice, 370 01", "Nádražní 654, Hradec Králové, 500 03",
            "Zahradní 987, Pardubice, 530 02", "Lesní 159, Zlín, 760 01"
        ],
        "hospital": [
            "Fakultní nemocnice v Motole", "Nemocnice Na Bulovce", "Ústřední vojenská nemocnice",
            "Fakultní nemocnice Ostrava", "Fakultní nemocnice Plzeň", "Krajská nemocnice Liberec",
            "Nemocnice České Budějovice", "Fakultní nemocnice Hradec Králové",
            "Nemocnice Pardubice", "Krajská nemocnice T. Bati ve Zlíně"
        ],
        "diagnosis_code": [
            "J45.0", "C50.1", "I21.0", "F20.0", "E10.5", "G40.3", "K29.7", "M54.4", "H40.1", "D25.0"
        ],
        "diagnosis_code2": [
            "E11.9", "G40.3", "I10", "J06.9", "K76.0", "M17.1", "N39.0", "R10.4", "S82.6", "Z03.8"
        ],
        "diagnosis_name": [
            "Astma", "Karcinom prsu", "Akutní infarkt myokardu", "Schizofrenie", "Diabetes mellitus",
            "Epilepsie", "Gastritida", "Lumbago", "Glaukom", "Myom dělohy"
        ],
        "insurance_number": [
            "7605061234", "8956231234", "5907281122", "8804173344", "7608125566",
            "6553027788", "9207149900", "7802031122", "8506093344", "7104055566"
        ],
        "insurance_company": [
            "111", "201", "205", "207", "209", "211", "213", "217", "333", "999"
        ],
        "email": [
            "novak@email.cz", "svobodova@email.cz", "dvorak@email.cz", "prochazka@email.cz",
            "kucera@email.cz", "novakova@email.cz", "cerny@email.cz", "bila@email.cz",
            "vesely@email.cz", "horakova@email.cz"
        ],
        "phone": [
            "+420 777 888 999", "+420 666 555 444", "+420 555 444 333", "+420 444 333 222",
            "+420 333 222 111", "+420 222 111 000", "+420 111 000 999", "+420 000 999 888",
            "+420 999 888 777", "+420 888 777 666"
        ],
        "admission_date": [
            "15.3.2025", "10.4.2025", "5.5.2025", "20.6.2025", "15.7.2025",
            "10.8.2025", "5.9.2025", "20.10.2025", "15.11.2025", "10.12.2025"
        ],
        "discharge_date": [
            "28.3.2025", "25.4.2025", "20.5.2025", "5.7.2025", "30.7.2025",
            "25.8.2025", "20.9.2025", "5.11.2025", "30.11.2025", "25.12.2025"
        ],
        "doctor": [
            "MUDr. Petr Černý", "MUDr. Jana Bílá", "MUDr. Martin Veselý", "MUDr. Lucie Horáková",
            "MUDr. Jan Novotný", "MUDr. Eva Malá", "MUDr. Josef Velký", "MUDr. Marie Krátká",
            "MUDr. Tomáš Dlouhý", "MUDr. Alena Široká"
        ],
        "lab": [
            "Centrální laboratoři FN Motol", "Laboratoři Na Bulovce", "Laboratoři ÚVN",
            "Centrální laboratoři FN Ostrava", "Laboratoři FN Plzeň", "Laboratoři KN Liberec",
            "Laboratoři Nemocnice České Budějovice", "Centrální laboratoři FN Hradec Králové",
            "Laboratoři Nemocnice Pardubice", "Laboratoři KNTB ve Zlíně"
        ],
        "test_date": [
            "5.4.2025", "10.5.2025", "15.6.2025", "20.7.2025", "25.8.2025",
            "30.9.2025", "5.10.2025", "10.11.2025", "15.12.2025", "20.1.2026"
        ]
    }
    
    import random
    
    # Generování souborů
    for i in range(num_files):
        # Výběr šablony (cyklicky)
        template_index = i % len(test_data_templates)
        template = test_data_templates[template_index]
        
        # Vytvoření obsahu souboru
        content = ""
        while len(content.encode('utf-8')) < file_size_kb * 1024:
            # Nahrazení proměnných v šabloně
            paragraph = template
            for key, values in replacements.items():
                placeholder = "{" + key + "}"
                if placeholder in paragraph:
                    paragraph = paragraph.replace(placeholder, random.choice(values))
            
            # Přidání odstavce do obsahu
            content += paragraph + "\n\n"
        
        # Vytvoření názvu souboru
        file_name = f"stress_test_{i+1:04d}.txt"
        file_path = os.path.join(output_dir, file_name)
        
        # Uložení souboru
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        if (i + 1) % 10 == 0:
            logger.info(f"Generated {i+1}/{num_files} test files")

def run_stress_test(input_dir: str, output_dir: str, error_dir: str, audit_dir: str, workers: int = None):
    """
    Spustí zátěžový test paralelního zpracování.
    
    Args:
        input_dir: Adresář se vstupními soubory
        output_dir: Adresář pro výstupní soubory
        error_dir: Adresář pro soubory s chybou
        audit_dir: Adresář pro auditní záznamy
        workers: Počet paralelních pracovníků (výchozí: počet CPU jader)
    """
    # Pokud není zadán počet pracovníků, použijeme počet CPU jader
    if workers is None:
        workers = multiprocessing.cpu_count()
    
    logger.info(f"Starting stress test with {workers} workers")
    
    # Inicializace Presidio service
    logger.info("Initializing Presidio service")
    presidio_service = PresidioService()
    
    # Inicializace paralelního batch procesoru
    logger.info(f"Initializing parallel batch processor with {workers} workers")
    batch_processor = ParallelBatchProcessor(
        presidio_service=presidio_service,
        input_dir=input_dir,
        output_dir=output_dir,
        error_dir=error_dir,
        audit_dir=audit_dir,
        batch_size=20,
        max_workers=workers,
    )
    
    # Spuštění zpracování
    logger.info("Starting batch processing")
    start_time = time.time()
    
    stats = batch_processor.process_batch(BatchProcessingConfig(
        file_pattern="*.txt",
        max_files=0,  # Zpracovat všechny soubory
    ))
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Výpis výsledků
    logger.info("Stress test completed")
    logger.info(f"Total files: {stats['total_files']}")
    logger.info(f"Successful: {stats['successful_files']}")
    logger.info(f"Failed: {stats['failed_files']}")
    logger.info(f"Total entities detected: {stats['total_entities_detected']}")
    logger.info(f"Total processing time: {total_time:.2f} seconds")
    logger.info(f"Average throughput: {stats['total_files'] / total_time:.2f} files/second")
    
    if 'performance' in stats:
        perf = stats['performance']
        logger.info(f"Documents per second: {perf.get('documents_per_second', 0):.2f}")
        logger.info(f"Entities per second: {perf.get('entities_per_second', 0):.2f}")
        logger.info(f"Average document processing time: {perf.get('avg_document_time_ms', 0):.2f} ms")
    
    # Uložení výsledků testu
    results_file = os.path.join(audit_dir, f"stress_test_results_{workers}_workers.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Test results saved to {results_file}")
    
    return stats

def main():
    """
    Hlavní funkce pro spuštění zátěžového testu.
    """
    parser = argparse.ArgumentParser(description="Stress Test MedDocAI Anonymizer")
    parser.add_argument("--generate", action="store_true", help="Generate test data")
    parser.add_argument("--num-files", type=int, default=100, help="Number of test files to generate")
    parser.add_argument("--file-size", type=int, default=10, help="Approximate size of each file in KB")
    parser.add_argument("--workers", type=int, default=None, help="Number of parallel workers (default: CPU count)")
    parser.add_argument("--input-dir", default="./test_data/stress_test/input", help="Input directory")
    parser.add_argument("--output-dir", default="./test_data/stress_test/output", help="Output directory")
    parser.add_argument("--error-dir", default="./test_data/stress_test/error", help="Error directory")
    parser.add_argument("--audit-dir", default="./test_data/stress_test/audit", help="Audit directory")
    
    args = parser.parse_args()
    
    # Vytvoření adresářů
    for directory in [args.input_dir, args.output_dir, args.error_dir, args.audit_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # Generování testovacích dat, pokud je požadováno
    if args.generate:
        generate_large_test_dataset(args.input_dir, args.num_files, args.file_size)
    
    # Spuštění zátěžového testu
    run_stress_test(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        error_dir=args.error_dir,
        audit_dir=args.audit_dir,
        workers=args.workers,
    )

if __name__ == "__main__":
    main()
