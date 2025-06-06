import logging
from typing import Dict, List, Optional, Union

from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer.operators import OperatorType
import random
import string

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class CzechAddressOperator(OperatorType):
    """
    Vlastní operátor pro anonymizaci českých adres.
    
    Tento operátor zachovává typ adresy (ulice, náměstí, atd.) a obecnou strukturu,
    ale anonymizuje konkrétní údaje, což umožňuje zachovat kontext při současné
    anonymizaci konkrétní adresy.
    """
    
    def operate(self, text: str = None, params: Optional[Dict] = None) -> str:
        """
        Anonymizuje adresu se zachováním typu a struktury.
        
        Args:
            text: Adresa k anonymizaci
            params: Další parametry pro anonymizaci
            
        Returns:
            Anonymizovaná adresa
        """
        if not text:
            return ""
        
        # Klíčová slova pro detekci typu adresy
        address_types = {
            "ulice": "ULICE",
            "ul.": "ULICE",
            "náměstí": "NÁMĚSTÍ",
            "nám.": "NÁMĚSTÍ",
            "třída": "TŘÍDA",
            "tř.": "TŘÍDA",
            "nábřeží": "NÁBŘEŽÍ",
            "sídliště": "SÍDLIŠTĚ",
            "sídl.": "SÍDLIŠTĚ",
            "bulvár": "BULVÁR",
            "alej": "ALEJ",
            "park": "PARK"
        }
        
        # Detekce PSČ
        zip_regex = r"\b([0-9]{3}\s?[0-9]{2})\b"
        import re
        zip_match = re.search(zip_regex, text)
        
        # Detekce typu adresy
        text_lower = text.lower()
        address_type = None
        for keyword, replacement in address_types.items():
            if keyword in text_lower:
                address_type = replacement
                break
        
        # Sestavení anonymizované adresy
        if address_type:
            if zip_match:
                return f"[{address_type} XXX, PSČ XXX XX]"
            else:
                return f"[{address_type} XXX]"
        else:
            if zip_match:
                return "[ADRESA, PSČ XXX XX]"
            else:
                return "[ADRESA]"
    
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
        return "czech_address"
