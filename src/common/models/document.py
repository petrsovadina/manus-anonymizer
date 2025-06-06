from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Typy dokumentů podporované systémem."""
    DISCHARGE_SUMMARY = "discharge_summary"  # Propouštěcí zpráva
    EPICRISIS = "epicrisis"  # Epikríza
    MEDICAL_REPORT = "medical_report"  # Lékařská zpráva
    LABORATORY_RESULT = "laboratory_result"  # Laboratorní výsledek
    RADIOLOGY_REPORT = "radiology_report"  # Radiologická zpráva
    OPERATION_PROTOCOL = "operation_protocol"  # Operační protokol
    ANAMNESIS = "anamnesis"  # Anamnéza
    OTHER = "other"  # Ostatní


class ProcessingStatus(str, Enum):
    """Stavy zpracování dokumentu."""
    PENDING = "pending"  # Čeká na zpracování
    PROCESSING = "processing"  # Zpracovává se
    COMPLETED = "completed"  # Zpracování dokončeno
    FAILED = "failed"  # Zpracování selhalo
    VALIDATED = "validated"  # Zpracování dokončeno a validováno


class DetectedEntity(BaseModel):
    """Model pro detekovanou entitu v textu."""
    entity_type: str = Field(..., description="Typ entity (např. PERSON, CZECH_BIRTH_NUMBER)")
    start: int = Field(..., description="Počáteční pozice entity v textu")
    end: int = Field(..., description="Koncová pozice entity v textu")
    score: float = Field(..., description="Skóre jistoty detekce (0-1)")
    text: str = Field(..., description="Původní text entity")
    context: Optional[str] = Field(None, description="Kontext kolem entity")
    metadata: Optional[Dict] = Field(None, description="Další metadata entity")


class AnonymizedEntity(BaseModel):
    """Model pro anonymizovanou entitu."""
    original_entity: DetectedEntity = Field(..., description="Původní detekovaná entita")
    anonymized_text: str = Field(..., description="Anonymizovaný text")
    operator_name: str = Field(..., description="Název použitého operátoru")
    metadata: Optional[Dict] = Field(None, description="Metadata anonymizace")


class Document(BaseModel):
    """Model pro dokument ke zpracování."""
    id: Optional[str] = Field(None, description="Unikátní identifikátor dokumentu")
    content: str = Field(..., description="Obsah dokumentu")
    content_type: str = Field("text/plain", description="MIME typ obsahu")
    document_type: Optional[DocumentType] = Field(None, description="Typ dokumentu")
    source: Optional[str] = Field(None, description="Zdroj dokumentu")
    metadata: Optional[Dict] = Field(None, description="Metadata dokumentu")
    status: ProcessingStatus = Field(ProcessingStatus.PENDING, description="Stav zpracování")


class AnonymizedDocument(BaseModel):
    """Model pro anonymizovaný dokument."""
    id: Optional[str] = Field(None, description="Unikátní identifikátor anonymizovaného dokumentu")
    original_document_id: Optional[str] = Field(None, description="ID původního dokumentu")
    content: str = Field(..., description="Anonymizovaný obsah")
    content_type: str = Field("text/plain", description="MIME typ obsahu")
    entities: List[AnonymizedEntity] = Field([], description="Seznam anonymizovaných entit")
    metadata: Optional[Dict] = Field(None, description="Metadata anonymizace")
    statistics: Optional[Dict] = Field(None, description="Statistiky anonymizace")
