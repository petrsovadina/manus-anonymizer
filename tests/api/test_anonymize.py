import pytest
import requests
from fastapi.testclient import TestClient

from src.api.main import app
from src.common.models import Document, DocumentType

# Vytvoření test klienta
client = TestClient(app)

def test_health_check():
    """Test health check endpointu."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "components" in data
    assert data["components"]["api"] == "ok"
    assert data["components"]["presidio"] == "ok"

def test_anonymize_endpoint():
    """Test anonymizačního endpointu s jednoduchým dokumentem."""
    # Vytvoření testovacího dokumentu
    document = Document(
        content="Pacient Jan Novák, narozen 15.6.1980, rodné číslo 800615/1234, " +
                "bytem Pražská 123, Praha 1, byl přijat dne 1.5.2025 s diagnózou J45.0.",
        content_type="text/plain",
        document_type=DocumentType.MEDICAL_REPORT,
        metadata={"source": "test"}
    )
    
    # Vytvoření požadavku
    request_data = {
        "document": document.dict(),
        "configuration_id": None,
        "options": None
    }
    
    # Odeslání požadavku
    response = client.post("/api/v1/anonymize", json=request_data)
    
    # Kontrola odpovědi
    assert response.status_code == 200
    data = response.json()
    
    # Kontrola, že odpověď obsahuje anonymizovaný dokument
    assert "content" in data
    assert data["content"] != document.content  # Obsah by měl být změněn
    
    # Kontrola, že byly detekovány nějaké entity
    assert "entities" in data
    assert "statistics" in data
    assert "total_entities_detected" in data["statistics"]
    
    # Kontrola, že byly detekovány alespoň některé entity
    # (Presidio by mělo detekovat jméno, datum narození, rodné číslo a adresu)
    assert data["statistics"]["total_entities_detected"] > 0

if __name__ == "__main__":
    # Spuštění testů manuálně
    test_health_check()
    test_anonymize_endpoint()
    print("Všechny testy prošly úspěšně!")
