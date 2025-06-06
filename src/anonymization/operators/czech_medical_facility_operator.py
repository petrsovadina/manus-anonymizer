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

class CzechMedicalFacilityOperator(OperatorType):
    """
    Vlastní operátor pro anonymizaci názvů českých zdravotnických zařízení.
    
    Tento operátor zachovává typ zdravotnického zařízení (nemocnice, klinika, atd.),
    ale anonymizuje konkrétní název, což umožňuje zachovat kontext při současné
    anonymizaci konkrétního zařízení.
    """
    
    def operate(self, text: str = None, params: Optional[Dict] = None) -> str:
        """
        Anonymizuje název zdravotnického zařízení se zachováním typu.
        
        Args:
            text: Název zdravotnického zařízení k anonymizaci
            params: Další parametry pro anonymizaci
            
        Returns:
            Anonymizovaný název zdravotnického zařízení
        """
        if not text:
            return ""
        
        # Klíčová slova pro detekci typu zdravotnického zařízení
        facility_types = {
            "nemocnice": "NEMOCNICE",
            "fakultní nemocnice": "FAKULTNÍ NEMOCNICE",
            "fn ": "FAKULTNÍ NEMOCNICE",
            "fn,": "FAKULTNÍ NEMOCNICE",
            "klinika": "KLINIKA",
            "poliklinika": "POLIKLINIKA",
            "zdravotní středisko": "ZDRAVOTNÍ STŘEDISKO",
            "zdravotnické zařízení": "ZDRAVOTNICKÉ ZAŘÍZENÍ",
            "léčebna": "LÉČEBNA",
            "sanatorium": "SANATORIUM",
            "ordinace": "ORDINACE",
            "ambulance": "AMBULANCE",
            "ústav": "ÚSTAV",
            "centrum": "CENTRUM",
            "oddělení": "ODDĚLENÍ",
            "lékařský dům": "LÉKAŘSKÝ DŮM",
            "lékařské centrum": "LÉKAŘSKÉ CENTRUM",
            "zdravotní centrum": "ZDRAVOTNÍ CENTRUM",
            "rehabilitační ústav": "REHABILITAČNÍ ÚSTAV",
            "hospic": "HOSPIC"
        }
        
        text_lower = text.lower()
        
        # Hledání typu zařízení v textu
        for keyword, replacement in facility_types.items():
            if keyword in text_lower:
                return f"[{replacement}]"
        
        # Pokud nebyl nalezen konkrétní typ, použijeme obecný
        return "[ZDRAVOTNICKÉ ZAŘÍZENÍ]"
    
    def validate(self, params: Optional[Dict] = None) -> None:
        """
        Validace parametrů operátoru.
        
        Args:
            params: Parametry k validaci
        """
        # Tento operátor nemá žádné povinné parametry
        pass

    def operator_name(self) -> str:
        """
        Vrátí název operátoru.
        
        Returns:
            Název operátoru
        """
        return "czech_medical_facility"
