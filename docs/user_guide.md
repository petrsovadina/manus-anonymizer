# Uživatelská příručka MedDocAI Anonymizer

## Úvod

MedDocAI Anonymizer je specializovaný nástroj pro anonymizaci zdravotnické dokumentace v českém jazyce. Nástroj je navržen pro zpracování strukturovaných i nestrukturovaných zdravotnických textů s důrazem na ochranu osobních údajů pacientů v souladu s GDPR a dalšími regulacemi.

## Základní funkce

- Detekce a anonymizace osobních údajů v českých zdravotnických textech
- Specializované rozpoznávače pro české formáty (rodná čísla, čísla pojištěnců, adresy)
- Specializované rozpoznávače pro zdravotnické kódy a terminologii
- Zachování klinické relevance dokumentů při anonymizaci
- Podpora dávkového a paralelního zpracování
- Komplexní audit a monitoring

## Použití API

### Anonymizace textu

#### Požadavek

```http
POST /api/v1/anonymize
Content-Type: application/json

{
  "text": "Pacient Jan Novák, rodné číslo 760506/1234, byl přijat do Fakultní nemocnice v Motole s diagnózou J45.0 (Astma).",
  "language": "cs",
  "return_entities": true
}
```

#### Odpověď

```json
{
  "anonymized_text": "Pacient [OSOBA], rodné číslo [RODNÉ ČÍSLO], byl přijat do [FAKULTNÍ NEMOCNICE] s diagnózou J45.0 (Astma).",
  "entities": [
    {
      "start": 8,
      "end": 17,
      "entity_type": "PERSON",
      "score": 0.95,
      "anonymized_value": "[OSOBA]"
    },
    {
      "start": 30,
      "end": 42,
      "entity_type": "CZECH_BIRTH_NUMBER",
      "score": 0.99,
      "anonymized_value": "[RODNÉ ČÍSLO]"
    },
    {
      "start": 57,
      "end": 82,
      "entity_type": "CZECH_MEDICAL_FACILITY",
      "score": 0.92,
      "anonymized_value": "[FAKULTNÍ NEMOCNICE]"
    }
  ]
}
```

### Analýza textu (bez anonymizace)

#### Požadavek

```http
POST /api/v1/analyze
Content-Type: application/json

{
  "text": "Pacient Jan Novák, rodné číslo 760506/1234, byl přijat do Fakultní nemocnice v Motole s diagnózou J45.0 (Astma).",
  "language": "cs"
}
```

#### Odpověď

```json
{
  "entities": [
    {
      "start": 8,
      "end": 17,
      "entity_type": "PERSON",
      "score": 0.95
    },
    {
      "start": 30,
      "end": 42,
      "entity_type": "CZECH_BIRTH_NUMBER",
      "score": 0.99
    },
    {
      "start": 57,
      "end": 82,
      "entity_type": "CZECH_MEDICAL_FACILITY",
      "score": 0.92
    }
  ]
}
```

## Dávkové zpracování

### Příprava vstupních souborů

Vstupní soubory umístěte do vstupního adresáře (výchozí: `./data/input/`). Podporované formáty:

- `.txt` - Textové soubory
- `.json` - JSON soubory
- `.xml` - XML soubory
- `.html` - HTML soubory

### Spuštění dávkového zpracování

```bash
python -m src.batch.run_batch --input-dir ./data/input --output-dir ./data/output
```

### Spuštění paralelního dávkového zpracování

```bash
python -m src.batch.run_parallel_batch --input-dir ./data/input --output-dir ./data/output --workers 4
```

### Výstupní soubory

Anonymizované soubory budou uloženy ve výstupním adresáři (výchozí: `./data/output/`). Pro každý vstupní soubor budou vytvořeny dva výstupní soubory:

1. Anonymizovaný obsah (stejný název jako vstupní soubor)
2. Metadata a statistiky (název vstupního souboru + `.meta.json`)

### Auditní záznamy

Auditní záznamy budou uloženy v auditním adresáři (výchozí: `./data/audit/`). Pro každý zpracovaný soubor bude vytvořen auditní záznam s informacemi o zpracování.

## Konfigurace

Konfigurace je možná prostřednictvím souboru `.env` v kořenovém adresáři projektu nebo prostřednictvím proměnných prostředí.

### Základní konfigurace

```
# Základní konfigurace
LOG_LEVEL=INFO
BATCH_SIZE=10
MAX_WORKERS=4
MAX_RETRIES=3
RETRY_DELAY=5

# Adresáře pro dávkové zpracování
INPUT_DIR=/path/to/input
OUTPUT_DIR=/path/to/output
ERROR_DIR=/path/to/error
AUDIT_DIR=/path/to/audit

# Konfigurace API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
```

### Pokročilá konfigurace

Pro pokročilou konfiguraci je možné upravit soubory:

- `src/config/settings.py` - Základní nastavení
- `src/detection/presidio_service.py` - Konfigurace detekce entit
- `src/anonymization/operators/czech_registry.py` - Konfigurace anonymizačních operátorů

## Typy rozpoznávaných entit

### Standardní entity

- `PERSON` - Jméno osoby
- `EMAIL_ADDRESS` - E-mailová adresa
- `PHONE_NUMBER` - Telefonní číslo
- `LOCATION` - Lokace
- `DATE_TIME` - Datum a čas

### České specializované entity

- `CZECH_BIRTH_NUMBER` - České rodné číslo
- `CZECH_HEALTH_INSURANCE_NUMBER` - Číslo pojištěnce
- `CZECH_DIAGNOSIS_CODE` - Kód diagnózy (MKN-10)
- `CZECH_MEDICAL_FACILITY` - Zdravotnické zařízení
- `CZECH_ADDRESS` - Česká adresa

## Řešení problémů

### Chyby při zpracování

Pokud se vyskytnou chyby při zpracování:

1. Zkontrolujte logy v adresáři `logs/`
2. Zkontrolujte auditní záznamy v adresáři `audit/`
3. Zkontrolujte chybové soubory v adresáři `error/`

### Problémy s výkonem

Pokud je výkon zpracování nízký:

1. Zvyšte počet pracovníků (`MAX_WORKERS`) podle dostupných CPU jader
2. Zvyšte velikost dávky (`BATCH_SIZE`) pro efektivnější zpracování
3. Zkontrolujte dostupnou paměť a případně zvyšte limit paměti pro Python

## Podpora a kontakt

Pro podporu a další informace kontaktujte:

- E-mail: support@stapro.cz
- Telefon: +420 XXX XXX XXX
