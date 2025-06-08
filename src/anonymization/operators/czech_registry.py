import logging
from typing import Dict, List, Optional, Union

from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer.operators import OperatorType

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class CzechOperatorRegistry:
    """
    Registr vlastních českých operátorů pro anonymizaci.
    """
    
    @staticmethod
    def get_operator_config() -> Dict[str, OperatorConfig]:
        """
        Vrátí konfiguraci operátorů pro různé typy entit.
        
        Returns:
            Slovník s konfigurací operátorů
        """
        logger.info("Configuring Czech operators")
        
        # Konfigurace operátorů pro různé typy entit
        operator_config = {
            # Standardní entity
            "PERSON": OperatorConfig("replace", {"new_value": "[OSOBA]"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[TELEFON]"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "[LOKACE]"}),
            "DATE_TIME": OperatorConfig("replace", {"new_value": "[DATUM]"}),
            
            # České specializované entity
            "CZECH_BIRTH_NUMBER": OperatorConfig("czech_birth_number", {}),
            "CZECH_HEALTH_INSURANCE_NUMBER": OperatorConfig("replace", {"new_value": "[ČÍSLO POJIŠTĚNCE]"}),
            "CZECH_DIAGNOSIS_CODE": OperatorConfig("czech_medical_diagnosis", {}),
            "CZECH_MEDICAL_FACILITY": OperatorConfig("czech_medical_facility", {}),
            "CZECH_ADDRESS": OperatorConfig("czech_address", {}),
        }
        
        logger.info(f"Configured {len(operator_config)} operators")
        return operator_config
    
    @staticmethod
    def register_operators(anonymizer_engine) -> None:
        """
        Registruje vlastní operátory do anonymizačního enginu.
        
        Args:
            anonymizer_engine: Instance AnonymizerEngine
        """
        logger.info("Registering custom Czech operators")
        
        # Import operátorů
        from src.anonymization.operators.czech_birth_number_operator import CzechBirthNumberOperator
        from src.anonymization.operators.czech_medical_diagnosis_operator import CzechMedicalDiagnosisOperator
        from src.anonymization.operators.czech_medical_facility_operator import CzechMedicalFacilityOperator
        from src.anonymization.operators.czech_address_operator import CzechAddressOperator
        
        # Registrace operátorů
        anonymizer_engine.registry.add_operator(CzechBirthNumberOperator())
        anonymizer_engine.registry.add_operator(CzechMedicalDiagnosisOperator())
        anonymizer_engine.registry.add_operator(CzechMedicalFacilityOperator())
        anonymizer_engine.registry.add_operator(CzechAddressOperator())
        
        logger.info("All Czech operators registered successfully")
