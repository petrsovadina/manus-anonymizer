# Dokumentace Streamlit rozhraní MedDocAI Anonymizer

## Úvod

Streamlit rozhraní pro MedDocAI Anonymizer poskytuje uživatelsky přívětivý webový přístup k funkcím anonymizace zdravotnické dokumentace. Rozhraní umožňuje jak jednorázovou anonymizaci textu, tak dávkové zpracování souborů, a poskytuje přehledné zobrazení výsledků včetně detekovaných entit a statistik.

## Instalace a spuštění

### Požadavky

- Python 3.8+
- Nainstalovaný MedDocAI Anonymizer
- Streamlit (instalace: `pip install streamlit`)

### Spuštění rozhraní

Pro spuštění Streamlit rozhraní použijte připravený skript:

```bash
python run_streamlit.py
```

Volitelné parametry:
- `--port` - Port pro Streamlit aplikaci (výchozí: 8501)
- `--host` - Host pro Streamlit aplikaci (výchozí: 0.0.0.0)

Příklad:
```bash
python run_streamlit.py --port 8502 --host 127.0.0.1
```

Po spuštění bude rozhraní dostupné na adrese `http://localhost:8501` (nebo na jiném portu, pokud byl specifikován).

## Funkce rozhraní

### 1. Anonymizace textu

Tato funkce umožňuje anonymizovat zadaný text v reálném čase:

1. Zadejte text do textového pole
2. Vyberte jazyk (čeština nebo angličtina)
3. Volitelně můžete zapnout/vypnout zobrazení detekovaných entit
4. Klikněte na tlačítko "Anonymizovat"
5. Výsledek se zobrazí v textovém poli pod tlačítkem
6. Pokud je zapnuto zobrazení entit, zobrazí se tabulka s detekovanými entitami

### 2. Zpracování souboru

Tato funkce umožňuje anonymizovat celý soubor:

1. Nahrajte soubor pomocí tlačítka "Vyberte soubor"
2. Vyberte jazyk (čeština nebo angličtina)
3. Klikněte na tlačítko "Zpracovat"
4. Po zpracování se zobrazí anonymizovaný obsah
5. Můžete stáhnout anonymizovaný soubor pomocí tlačítka "Stáhnout anonymizovaný soubor"
6. Zobrazí se statistiky zpracování a metadata

Podporované formáty souborů:
- `.txt` - Textové soubory
- `.json` - JSON soubory
- `.xml` - XML soubory
- `.html` - HTML soubory

### 3. O aplikaci

Tato sekce poskytuje základní informace o MedDocAI Anonymizeru, jeho funkcích a typech rozpoznávaných entit.

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

## Statistiky a metriky

Rozhraní poskytuje následující statistiky a metriky:

- **Zpracované soubory** - Počet úspěšně zpracovaných souborů z celkového počtu
- **Detekované entity** - Celkový počet detekovaných entit
- **Doba zpracování** - Čas potřebný ke zpracování v milisekundách
- **Neúspěšné soubory** - Počet souborů, které se nepodařilo zpracovat
- **Entity podle typu** - Rozložení detekovaných entit podle typu

## Řešení problémů

### Aplikace se nespustí

- Zkontrolujte, zda je nainstalován Streamlit: `pip install streamlit`
- Zkontrolujte, zda je správně nainstalován MedDocAI Anonymizer
- Zkontrolujte, zda jsou nainstalované všechny závislosti: `pip install -r requirements.txt`

### Chyby při zpracování souborů

- Zkontrolujte, zda je soubor v podporovaném formátu
- Zkontrolujte, zda má soubor správné kódování (UTF-8)
- Zkontrolujte, zda má aplikace přístupová práva k adresářům pro dočasné soubory

### Pomalé zpracování

- Zvažte použití dávkového zpracování místo jednorázové anonymizace pro velké soubory
- Zkontrolujte dostupné systémové prostředky (CPU, RAM)

## Bezpečnostní poznámky

- Streamlit rozhraní je určeno pro interní použití v zabezpečené síti
- Pro produkční nasazení s přístupem z internetu je nutné implementovat dodatečné zabezpečení (HTTPS, autentizace)
- Dočasné soubory jsou ukládány v adresáři `temp/` a nejsou automaticky mazány

## Kontakt a podpora

Pro podporu a další informace kontaktujte:
- E-mail: support@stapro.cz
- Telefon: +420 XXX XXX XXX
