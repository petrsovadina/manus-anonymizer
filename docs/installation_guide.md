# Instalační příručka MedDocAI Anonymizer

## Požadavky na systém

### Hardware
- CPU: Minimálně 4 jádra (doporučeno 8+ pro produkční prostředí)
- RAM: Minimálně 8 GB (doporučeno 16+ GB pro produkční prostředí)
- Úložiště: Minimálně 100 GB (závisí na objemu zpracovávaných dat)

### Software
- Python 3.8+
- pip (aktuální verze)
- Git
- Docker a Docker Compose (volitelné, pro kontejnerizované nasazení)
- Virtuální prostředí (venv, conda)

## Instalace

### 1. Klonování repozitáře

```bash
git clone https://github.com/stapro/meddocai-anonymizer.git
cd meddocai-anonymizer
```

### 2. Vytvoření virtuálního prostředí

```bash
python -m venv venv
source venv/bin/activate  # Pro Linux/Mac
# nebo
venv\Scripts\activate  # Pro Windows
```

### 3. Instalace závislostí

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Instalace jazykových modelů

```bash
python -m spacy download cs_core_news_sm
python -m spacy download en_core_web_sm
```

### 5. Konfigurace

Vytvořte soubor `.env` v kořenovém adresáři projektu:

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

## Spuštění

### Spuštění API serveru

```bash
cd meddocai-anonymizer
source venv/bin/activate
python -m src.api.main
```

Server bude dostupný na adrese `http://localhost:8000`.

### Spuštění dávkového zpracování

```bash
cd meddocai-anonymizer
source venv/bin/activate
python -m src.batch.run_batch --input-dir /path/to/input --output-dir /path/to/output
```

### Spuštění paralelního dávkového zpracování

```bash
cd meddocai-anonymizer
source venv/bin/activate
python -m src.batch.run_parallel_batch --input-dir /path/to/input --output-dir /path/to/output --workers 4
```

## Kontejnerizované nasazení

### 1. Sestavení Docker image

```bash
docker build -t meddocai-anonymizer:latest .
```

### 2. Spuštění kontejneru

```bash
docker run -p 8000:8000 -v /path/to/data:/app/data meddocai-anonymizer:latest
```

### 3. Použití Docker Compose

```bash
docker-compose up -d
```

## Ověření instalace

### 1. Ověření API

```bash
curl -X POST "http://localhost:8000/api/v1/anonymize" \
     -H "Content-Type: application/json" \
     -d '{"text": "Pacient Jan Novák, rodné číslo 760506/1234, byl přijat do Fakultní nemocnice v Motole."}'
```

### 2. Spuštění testů

```bash
cd meddocai-anonymizer
source venv/bin/activate
python -m pytest tests/
```

### 3. Spuštění zátěžového testu

```bash
cd meddocai-anonymizer
source venv/bin/activate
python -m tests.stress_test --generate --num-files 100
```

## Řešení problémů

### Problém s instalací spaCy modelů

Pokud se vyskytnou problémy s instalací českého spaCy modelu, zkuste:

```bash
pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download cs_core_news_sm
```

### Problémy s výkonem

Pokud je výkon zpracování nízký:

1. Zvyšte počet pracovníků (`MAX_WORKERS`) podle dostupných CPU jader
2. Zvyšte velikost dávky (`BATCH_SIZE`) pro efektivnější zpracování
3. Zkontrolujte dostupnou paměť a případně zvyšte limit paměti pro Python

### Chyby při zpracování

Pokud se vyskytnou chyby při zpracování:

1. Zkontrolujte logy v adresáři `logs/`
2. Zkontrolujte auditní záznamy v adresáři `audit/`
3. Zkontrolujte chybové soubory v adresáři `error/`

## Další kroky

Po úspěšné instalaci a ověření funkčnosti je doporučeno:

1. Nastavit monitoring a alerting
2. Nastavit pravidelné zálohování konfigurace a auditních záznamů
3. Nastavit automatické restarty v případě pádů
4. Provést školení administrátorů a uživatelů
