import logging
from typing import List, Optional

from presidio_analyzer import RecognizerRegistry
from src.detection.recognizers.czech_birth_number_recognizer import CzechBirthNumberRecognizer
from src.detection.recognizers.czech_health_insurance_recognizer import CzechHealthInsuranceNumberRecognizer
from src.detection.recognizers.czech_diagnosis_code_recognizer import CzechMedicalDiagnosisCodeRecognizer
from src.detection.recognizers.czech_medical_facility_recognizer import CzechMedicalFacilityRecognizer

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class CzechRecognizerRegistry:
    """
    Registr specializovaných českých rozpoznávačů pro Presidio.
    """
    
    @staticmethod
    def register_czech_recognizers(registry: RecognizerRegistry) -> None:
        """
        Registruje specializované české rozpoznávače do Presidio registru.
        
        Args:
            registry: Presidio registr rozpoznávačů
        """
        logger.info("Registering specialized Czech recognizers")
        
        # Vytvoření a registrace rozpoznávače českých rodných čísel
        birth_number_recognizer = CzechBirthNumberRecognizer()
        registry.add_recognizer(birth_number_recognizer)
        logger.info(f"Registered: {birth_number_recognizer.name}")
        
        # Vytvoření a registrace rozpoznávače českých čísel pojištěnce
        health_insurance_recognizer = CzechHealthInsuranceNumberRecognizer()
        registry.add_recognizer(health_insurance_recognizer)
        logger.info(f"Registered: {health_insurance_recognizer.name}")
        
        # Vytvoření a registrace rozpoznávače českých kódů diagnóz
        diagnosis_code_recognizer = CzechMedicalDiagnosisCodeRecognizer()
        registry.add_recognizer(diagnosis_code_recognizer)
        logger.info(f"Registered: {diagnosis_code_recognizer.name}")
        
        # Vytvoření a registrace rozpoznávače českých zdravotnických zařízení
        medical_facility_recognizer = CzechMedicalFacilityRecognizer()
        registry.add_recognizer(medical_facility_recognizer)
        logger.info(f"Registered: {medical_facility_recognizer.name}")
        
        # Zde budou přidány další specializované české rozpoznávače
        
        logger.info("All Czech recognizers registered successfully")
    
    @staticmethod
    def get_supported_entities() -> List[str]:
        """
        Vrátí seznam všech podporovaných entit českými rozpoznávači.
        
        Returns:
            Seznam podporovaných entit
        """
        return [
            "CZECH_BIRTH_NUMBER",
            "CZECH_HEALTH_INSURANCE_NUMBER",
            "CZECH_DIAGNOSIS_CODE",
            "CZECH_MEDICAL_FACILITY",
            # Zde budou přidány další entity
        ]
