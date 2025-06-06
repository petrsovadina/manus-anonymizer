import logging
from typing import Dict, List, Optional, Union

from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer.operators import OperatorType
import random

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class CzechBirthNumberOperator(OperatorType):
    """
    Vlastní operátor pro anonymizaci českých rodných čísel.
    
    Tento operátor zachovává strukturu rodného čísla a základní demografické informace
    (rok, měsíc a den narození, pohlaví), ale mění konkrétní hodnoty, aby nebylo možné
    identifikovat konkrétní osobu.
    """
    
    def operate(self, text: str = None, params: Optional[Dict] = None) -> str:
        """
        Anonymizuje rodné číslo se zachováním struktury.
        
        Args:
            text: Rodné číslo k anonymizaci
            params: Další parametry pro anonymizaci
            
        Returns:
            Anonymizované rodné číslo
        """
        if not text:
            return ""
        
        # Odstranění mezer a lomítka
        text = text.strip().replace("/", "")
        
        # Kontrola, zda text odpovídá formátu rodného čísla
        if not text or len(text) not in [9, 10]:
            return "[RODNÉ ČÍSLO]"
        
        try:
            # Extrakce roku, měsíce a dne z rodného čísla
            year = text[0:2]
            month = int(text[2:4])
            day = int(text[4:6])
            
            # Zachování informace o pohlaví (měsíc > 50 pro ženy)
            is_female = month > 50
            
            # Generování nového rodného čísla se zachováním struktury
            new_year = year  # Zachování roku
            new_month = random.randint(1, 12) + (50 if is_female else 0)  # Zachování pohlaví
            new_day = random.randint(1, 28)  # Bezpečný rozsah dnů
            
            # Generování náhodného koncového čísla
            if len(text) == 10:
                # Pro 10místná rodná čísla generujeme náhodné číslo, které splňuje kontrolu modulo 11
                while True:
                    new_end = random.randint(1000, 9999)
                    number = int(f"{new_year}{new_month:02d}{new_day:02d}{new_end // 10}")
                    check_digit = new_end % 10
                    if number % 11 == check_digit or (number % 11 == 10 and check_digit == 0):
                        break
            else:
                # Pro 9místná rodná čísla (před rokem 1954) generujeme náhodné 3místné číslo
                new_end = random.randint(100, 999)
            
            # Sestavení nového rodného čísla
            if len(text) == 10:
                return f"{new_year}{new_month:02d}{new_day:02d}/{new_end:04d}"
            else:
                return f"{new_year}{new_month:02d}{new_day:02d}/{new_end:03d}"
            
        except (ValueError, IndexError):
            return "[RODNÉ ČÍSLO]"
    
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
        return "czech_birth_number"
