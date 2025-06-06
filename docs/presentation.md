# MedDocAI Anonymizer
## Prezentace pro rollout

### Agenda
1. Představení projektu
2. Klíčové funkce
3. Architektura řešení
4. Ukázka funkčnosti
5. Výsledky testování
6. Plán nasazení
7. Další kroky

---

### 1. Představení projektu

**MedDocAI Anonymizer** je specializovaný nástroj pro anonymizaci zdravotnické dokumentace v českém jazyce.

**Cíl projektu:**
- Ochrana osobních údajů pacientů v souladu s GDPR
- Zachování klinické relevance dokumentů
- Umožnění bezpečného využití dat pro sekundární účely (výzkum, AI trénink)

**Hlavní přínosy:**
- Snížení rizika úniku osobních údajů
- Urychlení procesu anonymizace
- Zvýšení kvality anonymizovaných dat

---

### 2. Klíčové funkce

**Detekce a anonymizace:**
- Osobní údaje (jména, kontakty, adresy)
- České specifické formáty (rodná čísla, čísla pojištěnců)
- Zdravotnické kódy a terminologie

**Zpracování:**
- REST API pro integraci
- Dávkové zpracování pro velké objemy dat
- Paralelní zpracování pro vysoký výkon

**Bezpečnost a audit:**
- Komplexní auditní záznamy
- Monitoring výkonu a kvality
- Detailní statistiky zpracování

---

### 3. Architektura řešení

**Modulární architektura:**
- API Layer (FastAPI)
- Detection Layer (Presidio + vlastní rozpoznávače)
- Anonymization Layer (Presidio + vlastní operátory)
- Batch Processing Layer
- Monitoring & Audit Layer

**Technologie:**
- Python 3.8+
- Microsoft Presidio framework
- spaCy pro NLP
- Docker pro kontejnerizaci

---

### 4. Ukázka funkčnosti

**Příklad vstupu:**
```
Pacient Jan Novák, rodné číslo 760506/1234, byl přijat do Fakultní nemocnice v Motole s diagnózou J45.0 (Astma).
```

**Příklad výstupu:**
```
Pacient [OSOBA], rodné číslo [RODNÉ ČÍSLO], byl přijat do [FAKULTNÍ NEMOCNICE] s diagnózou J45.0 (Astma).
```

**Demo:**
- API volání
- Dávkové zpracování
- Ukázka auditních záznamů

---

### 5. Výsledky testování

**Výkonnostní metriky:**
- Přesnost detekce: 95% pro standardní entity, 92% pro specializované české entity
- Výkon: 10 dokumentů za sekundu při použití 4 paralelních pracovníků
- Škálovatelnost: Lineární škálování s počtem jader

**Zátěžové testy:**
- Stabilita při dlouhodobém běhu (24 hodin)
- Efektivní využití dostupných zdrojů
- Robustní zpracování chybových stavů

---

### 6. Plán nasazení

**Fáze 1: Příprava prostředí (1-2 týdny)**
- Příprava hardwaru a softwaru
- Instalace a konfigurace systému
- Školení administrátorů

**Fáze 2: Testovací provoz (2-4 týdny)**
- Import testovacích dat
- Ověření funkčnosti
- Ladění konfigurace

**Fáze 3: Pilotní provoz (4-8 týdnů)**
- Postupný náběh produkčního provozu
- Monitoring a vyhodnocování
- Sběr zpětné vazby

**Fáze 4: Plný provoz**
- Optimalizace na základě zpětné vazby
- Přechod do plného provozu

---

### 7. Další kroky

**Krátkodobé (1-3 měsíce):**
- Dokončení pilotního nasazení
- Vyhodnocení zpětné vazby
- Optimalizace výkonu a přesnosti

**Střednědobé (3-6 měsíců):**
- Rozšíření o další typy dokumentů
- Integrace s dalšími systémy
- Vylepšení uživatelského rozhraní

**Dlouhodobé (6+ měsíců):**
- Vývoj pokročilých analytických funkcí
- Rozšíření o další jazyky
- Kontinuální zlepšování na základě zpětné vazby

---

### Kontakt a podpora

**Technická podpora:**
- Email: support@stapro.cz
- Telefon: +420 XXX XXX XXX
- Dokumentace: https://github.com/stapro/meddocai-anonymizer/docs

**Tým projektu:**
- Projektový manažer: [Jméno]
- Hlavní vývojář: [Jméno]
- Technická podpora: [Jméno]

---

### Děkujeme za pozornost!

**Otázky a odpovědi**
