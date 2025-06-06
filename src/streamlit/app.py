import streamlit as st
import pandas as pd
import os
import json
import time
import sys
from pathlib import Path

# Přidání cesty k projektu do PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import služeb z projektu
from src.detection.presidio_service import PresidioService
from src.common.models import Document, BatchProcessingConfig
from src.batch.parallel_batch_processor import ParallelBatchProcessor

# Konfigurace stránky
st.set_page_config(
    page_title="MedDocAI Anonymizer",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializace služeb
@st.cache_resource
def load_presidio_service():
    return PresidioService()

# Funkce pro anonymizaci textu
def anonymize_text(text, language="cs", return_entities=True):
    presidio_service = load_presidio_service()
    document = Document(
        id="streamlit_input",
        content=text,
        content_type="text/plain",
        language=language
    )
    
    start_time = time.time()
    anonymized_document = presidio_service.process_document(document)
    processing_time = (time.time() - start_time) * 1000  # v ms
    
    result = {
        "anonymized_text": anonymized_document.content,
        "processing_time_ms": processing_time,
        "entities": []
    }
    
    if return_entities and anonymized_document.entities:
        for entity in anonymized_document.entities:
            result["entities"].append({
                "start": entity.original_entity.start,
                "end": entity.original_entity.end,
                "entity_type": entity.original_entity.entity_type,
                "score": entity.original_entity.score,
                "anonymized_value": entity.anonymized_value
            })
    
    return result

# Funkce pro zpracování nahraného souboru
def process_uploaded_file(uploaded_file, language="cs"):
    # Vytvoření dočasného adresáře pro zpracování
    temp_dir = Path("./temp")
    input_dir = temp_dir / "input"
    output_dir = temp_dir / "output"
    error_dir = temp_dir / "error"
    audit_dir = temp_dir / "audit"
    
    for directory in [input_dir, output_dir, error_dir, audit_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Uložení nahraného souboru
    file_path = input_dir / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Zpracování souboru
    presidio_service = load_presidio_service()
    batch_processor = ParallelBatchProcessor(
        presidio_service=presidio_service,
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        error_dir=str(error_dir),
        audit_dir=str(audit_dir),
        batch_size=1,
        max_workers=1
    )
    
    stats = batch_processor.process_batch(BatchProcessingConfig(
        file_pattern="*.*",
        max_files=1
    ))
    
    # Načtení výsledku
    output_file = output_dir / uploaded_file.name
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            anonymized_content = f.read()
        
        # Načtení metadat
        metadata_file = Path(str(output_file) + ".meta.json")
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        return {
            "success": True,
            "anonymized_content": anonymized_content,
            "metadata": metadata,
            "stats": stats
        }
    else:
        return {
            "success": False,
            "error": "Zpracování souboru selhalo",
            "stats": stats
        }

# Funkce pro zobrazení statistik
def display_stats(stats):
    if not stats:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Zpracované soubory", f"{stats.get('successful_files', 0)}/{stats.get('total_files', 0)}")
        st.metric("Detekované entity", stats.get('total_entities_detected', 0))
    
    with col2:
        st.metric("Doba zpracování", f"{stats.get('processing_time_ms', 0):.2f} ms")
        st.metric("Neúspěšné soubory", stats.get('failed_files', 0))
    
    if "entities_by_type" in stats and stats["entities_by_type"]:
        st.subheader("Entity podle typu")
        entity_data = []
        for entity_type, count in stats["entities_by_type"].items():
            entity_data.append({"Typ entity": entity_type, "Počet": count})
        
        st.dataframe(pd.DataFrame(entity_data))

# Funkce pro zobrazení detekovaných entit
def display_entities(entities):
    if not entities:
        return
    
    st.subheader("Detekované entity")
    
    entity_data = []
    for entity in entities:
        entity_data.append({
            "Typ": entity["entity_type"],
            "Text": entity.get("text", ""),
            "Anonymizovaná hodnota": entity["anonymized_value"],
            "Skóre": f"{entity['score']:.2f}",
            "Pozice": f"{entity['start']}-{entity['end']}"
        })
    
    st.dataframe(pd.DataFrame(entity_data))

# Hlavní aplikace
def main():
    # Sidebar
    st.sidebar.title("MedDocAI Anonymizer")
    st.sidebar.image("https://www.stapro.cz/wp-content/uploads/2022/02/logo-stapro.png", width=200)
    
    app_mode = st.sidebar.selectbox(
        "Vyberte režim",
        ["Anonymizace textu", "Zpracování souboru", "O aplikaci"]
    )
    
    # Nastavení
    with st.sidebar.expander("Nastavení"):
        language = st.selectbox("Jazyk", ["cs", "en"], index=0)
        show_entities = st.checkbox("Zobrazit detekované entity", value=True)
    
    # Anonymizace textu
    if app_mode == "Anonymizace textu":
        st.title("Anonymizace zdravotnického textu")
        st.write("Zadejte text, který chcete anonymizovat:")
        
        text_input = st.text_area("Vstupní text", height=200, 
                                 value="Pacient Jan Novák, rodné číslo 760506/1234, byl přijat do Fakultní nemocnice v Motole s diagnózou J45.0 (Astma).")
        
        if st.button("Anonymizovat"):
            with st.spinner("Probíhá anonymizace..."):
                result = anonymize_text(text_input, language, show_entities)
                
                st.subheader("Anonymizovaný text")
                st.text_area("Výstup", result["anonymized_text"], height=200)
                
                st.metric("Doba zpracování", f"{result['processing_time_ms']:.2f} ms")
                
                if show_entities:
                    display_entities(result["entities"])
    
    # Zpracování souboru
    elif app_mode == "Zpracování souboru":
        st.title("Zpracování souboru")
        st.write("Nahrajte soubor, který chcete anonymizovat:")
        
        uploaded_file = st.file_uploader("Vyberte soubor", type=["txt", "json", "xml", "html"])
        
        if uploaded_file is not None:
            if st.button("Zpracovat"):
                with st.spinner("Probíhá zpracování souboru..."):
                    result = process_uploaded_file(uploaded_file, language)
                    
                    if result["success"]:
                        st.success("Soubor byl úspěšně zpracován")
                        
                        st.subheader("Anonymizovaný obsah")
                        st.text_area("Výstup", result["anonymized_content"], height=200)
                        
                        # Tlačítko pro stažení výsledku
                        st.download_button(
                            label="Stáhnout anonymizovaný soubor",
                            data=result["anonymized_content"],
                            file_name=f"anonymized_{uploaded_file.name}",
                            mime="text/plain"
                        )
                        
                        # Zobrazení statistik
                        st.subheader("Statistiky zpracování")
                        display_stats(result["stats"])
                        
                        # Zobrazení metadat
                        if "metadata" in result and result["metadata"]:
                            st.subheader("Metadata")
                            st.json(result["metadata"])
                    else:
                        st.error(result["error"])
                        st.subheader("Statistiky zpracování")
                        display_stats(result["stats"])
    
    # O aplikaci
    else:
        st.title("O aplikaci MedDocAI Anonymizer")
        
        st.markdown("""
        ## MedDocAI Anonymizer
        
        MedDocAI Anonymizer je specializovaný nástroj pro anonymizaci zdravotnické dokumentace v českém jazyce, vyvinutý společností STAPRO. Nástroj je navržen pro zpracování strukturovaných i nestrukturovaných zdravotnických textů s důrazem na ochranu osobních údajů pacientů v souladu s GDPR a dalšími regulacemi.
        
        ### Klíčové funkce
        
        - **Detekce a anonymizace osobních údajů** v českých zdravotnických textech
        - **Specializované rozpoznávače** pro české formáty (rodná čísla, čísla pojištěnců, adresy)
        - **Specializované rozpoznávače** pro zdravotnické kódy a terminologii
        - **Vlastní anonymizační operátory** zachovávající klinickou relevanci dokumentů
        - **Dávkové a paralelní zpracování** pro efektivní zpracování velkého množství dat
        - **Komplexní audit a monitoring** pro sledování a vyhodnocování procesu anonymizace
        
        ### Typy rozpoznávaných entit
        
        #### Standardní entity
        - `PERSON` - Jméno osoby
        - `EMAIL_ADDRESS` - E-mailová adresa
        - `PHONE_NUMBER` - Telefonní číslo
        - `LOCATION` - Lokace
        - `DATE_TIME` - Datum a čas
        
        #### České specializované entity
        - `CZECH_BIRTH_NUMBER` - České rodné číslo
        - `CZECH_HEALTH_INSURANCE_NUMBER` - Číslo pojištěnce
        - `CZECH_DIAGNOSIS_CODE` - Kód diagnózy (MKN-10)
        - `CZECH_MEDICAL_FACILITY` - Zdravotnické zařízení
        - `CZECH_ADDRESS` - Česká adresa
        
        ### Kontakt a podpora
        
        Pro podporu a další informace kontaktujte:
        - E-mail: support@stapro.cz
        - Telefon: +420 XXX XXX XXX
        """)

if __name__ == "__main__":
    main()
