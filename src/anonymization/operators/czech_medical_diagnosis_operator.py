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

class CzechMedicalDiagnosisOperator(OperatorType):
    """
    Vlastní operátor pro anonymizaci českých kódů diagnóz.
    
    Tento operátor zachovává kategorii diagnózy (první písmeno a první číslice),
    ale anonymizuje detailní kód, což umožňuje zachovat klinickou relevanci
    při současné anonymizaci konkrétní diagnózy.
    """
    
    def operate(self, text: str = None, params: Optional[Dict] = None) -> str:
        """
        Anonymizuje kód diagnózy se zachováním kategorie.
        
        Args:
            text: Kód diagnózy k anonymizaci
            params: Další parametry pro anonymizaci
            
        Returns:
            Anonymizovaný kód diagnózy
        """
        if not text:
            return ""
        
        # Odstranění mezer
        text = text.strip()
        
        # Kontrola, zda text odpovídá formátu kódu diagnózy
        if not text or len(text) < 2:
            return "[DIAGNÓZA]"
        
        # Zachování kategorie diagnózy (první písmeno a první číslice)
        if len(text) >= 2:
            category = text[0:2]  # Např. "J4" z "J45.0"
            return f"{category}X.X"
        
        return "[DIAGNÓZA]"
    
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
        return "czech_medical_diagnosis"
