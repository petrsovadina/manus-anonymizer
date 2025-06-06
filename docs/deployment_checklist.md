# Checklist pro produkční nasazení MedDocAI Anonymizer

## Příprava prostředí

- [ ] Ověření hardwarových požadavků
  - [ ] CPU: Minimálně 4 jádra (doporučeno 8+ pro produkční prostředí)
  - [ ] RAM: Minimálně 8 GB (doporučeno 16+ GB pro produkční prostředí)
  - [ ] Úložiště: Minimálně 100 GB (závisí na objemu zpracovávaných dat)

- [ ] Ověření softwarových požadavků
  - [ ] OS: Linux (Ubuntu 20.04+, CentOS 8+)
  - [ ] Python: 3.8+
  - [ ] Docker: 20.10+ (pro kontejnerizované nasazení)
  - [ ] Docker Compose: 2.0+ (pro kontejnerizované nasazení)

- [ ] Příprava síťového prostředí
  - [ ] Izolovaná síť pro zpracování citlivých dat
  - [ ] Firewall pro omezení přístupu k API
  - [ ] HTTPS certifikáty pro zabezpečenou komunikaci

## Instalace a konfigurace

- [ ] Klonování repozitáře
  - [ ] `git clone https://github.com/stapro/meddocai-anonymizer.git`

- [ ] Vytvoření virtuálního prostředí
  - [ ] `python -m venv venv`
  - [ ] `source venv/bin/activate` (Linux/Mac) nebo `venv\Scripts\activate` (Windows)

- [ ] Instalace závislostí
  - [ ] `pip install --upgrade pip`
  - [ ] `pip install -r requirements.txt`

- [ ] Instalace jazykových modelů
  - [ ] `python -m spacy download cs_core_news_sm`
  - [ ] `python -m spacy download en_core_web_sm`

- [ ] Konfigurace prostředí
  - [ ] Vytvoření souboru `.env` s konfigurací
  - [ ] Nastavení adresářů pro dávkové zpracování
  - [ ] Nastavení API parametrů

## Testování instalace

- [ ] Spuštění jednotkových testů
  - [ ] `python -m pytest tests/`

- [ ] Spuštění integračních testů
  - [ ] `python -m pytest tests/integration/`

- [ ] Spuštění end-to-end testů
  - [ ] `python -m pytest tests/e2e/`

- [ ] Ověření API
  - [ ] Spuštění API serveru: `python -m src.api.main`
  - [ ] Test API endpointu: `curl -X POST "http://localhost:8000/api/v1/anonymize" -H "Content-Type: application/json" -d '{"text": "Testovací text s osobními údaji"}'`

- [ ] Ověření dávkového zpracování
  - [ ] Příprava testovacích dat
  - [ ] Spuštění dávkového zpracování: `python -m src.batch.run_batch --input-dir ./test_data/input --output-dir ./test_data/output`
  - [ ] Kontrola výstupních souborů a auditních záznamů

## Nastavení monitoringu a logování

- [ ] Konfigurace logování
  - [ ] Nastavení úrovně logování v `.env`
  - [ ] Nastavení rotace logů
  - [ ] Nastavení formátu logů

- [ ] Konfigurace monitoringu
  - [ ] Nastavení alertingu pro kritické chyby
  - [ ] Nastavení monitoringu výkonu
  - [ ] Nastavení monitoringu dostupnosti API

- [ ] Konfigurace auditních záznamů
  - [ ] Nastavení formátu auditních záznamů
  - [ ] Nastavení retence auditních záznamů
  - [ ] Nastavení přístupových práv k auditním záznamům

## Zabezpečení

- [ ] Ověření zabezpečení API
  - [ ] Nastavení autentizace pro API
  - [ ] Nastavení rate limitingu
  - [ ] Nastavení CORS

- [ ] Ověření zabezpečení dat
  - [ ] Šifrování dat v klidu
  - [ ] Šifrování dat při přenosu
  - [ ] Nastavení přístupových práv k datům

- [ ] Ověření zabezpečení systému
  - [ ] Aktualizace OS a balíčků
  - [ ] Nastavení firewallu
  - [ ] Nastavení uživatelských účtů a oprávnění

## Školení a dokumentace

- [ ] Školení administrátorů
  - [ ] Instalace a konfigurace
  - [ ] Monitoring a údržba
  - [ ] Řešení problémů

- [ ] Školení uživatelů
  - [ ] Základní použití API
  - [ ] Dávkové zpracování
  - [ ] Interpretace výsledků

- [ ] Předání dokumentace
  - [ ] Instalační příručka
  - [ ] Uživatelská příručka
  - [ ] API dokumentace
  - [ ] Vývojářská dokumentace

## Pilotní provoz

- [ ] Příprava pilotního provozu
  - [ ] Definice rozsahu pilotního provozu
  - [ ] Definice kritérií úspěchu
  - [ ] Definice plánu eskalace problémů

- [ ] Spuštění pilotního provozu
  - [ ] Postupný náběh produkčního provozu
  - [ ] Monitoring a vyhodnocování
  - [ ] Sběr zpětné vazby od uživatelů

- [ ] Vyhodnocení pilotního provozu
  - [ ] Analýza výkonu a stability
  - [ ] Analýza zpětné vazby
  - [ ] Identifikace oblastí pro zlepšení

## Přechod do plného provozu

- [ ] Optimalizace na základě pilotního provozu
  - [ ] Implementace identifikovaných zlepšení
  - [ ] Ladění konfigurace
  - [ ] Aktualizace dokumentace

- [ ] Plánování kapacity
  - [ ] Odhad budoucích potřeb
  - [ ] Plánování škálování
  - [ ] Plánování zálohování a obnovy

- [ ] Nastavení provozních procesů
  - [ ] Proces pro aktualizace a údržbu
  - [ ] Proces pro řešení incidentů
  - [ ] Proces pro správu změn

## Finální kontrola

- [ ] Kontrola dokumentace
  - [ ] Aktuálnost dokumentace
  - [ ] Úplnost dokumentace
  - [ ] Dostupnost dokumentace

- [ ] Kontrola zdrojového kódu
  - [ ] Aktuálnost kódu v repozitáři
  - [ ] Kompletnost kódu
  - [ ] Správa verzí

- [ ] Kontrola infrastruktury
  - [ ] Dostupnost všech komponent
  - [ ] Správná konfigurace
  - [ ] Zabezpečení

- [ ] Předání projektu
  - [ ] Formální předání projektu
  - [ ] Podpis akceptačního protokolu
  - [ ] Zahájení podpory a údržby
