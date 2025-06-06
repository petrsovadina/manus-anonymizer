from src.detection.presidio_service import PresidioService
from src.common.models import Document, AnonymizedDocument

# Aktualizace API endpointu pro anonymizaci
import logging
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.common.models import Document, AnonymizedDocument
from src.detection.presidio_service import PresidioService

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Vytvoření FastAPI aplikace
app = FastAPI(
    title="MedDocAI Anonymizer",
    description="API pro anonymizaci zdravotnické dokumentace",
    version="0.1.0",
)

# Nastavení CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # V produkci by mělo být omezeno na konkrétní domény
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modely pro API
class HealthResponse(BaseModel):
    status: str
    version: str
    components: Dict[str, str]

class AnonymizeRequest(BaseModel):
    document: Document
    configuration_id: Optional[str] = None
    options: Optional[Dict] = None

# Dependency pro získání instance PresidioService
def get_presidio_service():
    return PresidioService()

# Endpointy
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Kontrola zdraví API a jeho komponent.
    """
    logger.info("Health check requested")
    return HealthResponse(
        status="ok",
        version="0.1.0",
        components={
            "api": "ok",
            "presidio": "ok",  # Toto by mělo být dynamicky ověřeno
        }
    )

@app.post("/api/v1/anonymize", response_model=AnonymizedDocument)
async def anonymize(request: AnonymizeRequest, presidio_service: PresidioService = Depends(get_presidio_service)):
    """
    Anonymizuje dokument podle zadané konfigurace.
    """
    logger.info(f"Anonymization requested for document type: {request.document.document_type}")
    
    try:
        # Použití Presidio service pro anonymizaci dokumentu
        anonymized_document = presidio_service.process_document(request.document)
        return anonymized_document
    except Exception as e:
        logger.error(f"Error during anonymization: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}")

# Pokud je tento soubor spuštěn přímo
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
