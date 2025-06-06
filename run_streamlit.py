# Spouštěcí skript pro Streamlit rozhraní MedDocAI Anonymizer

import os
import sys
import argparse

# Přidání cesty k projektu do PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """
    Spustí Streamlit aplikaci MedDocAI Anonymizer.
    """
    parser = argparse.ArgumentParser(description="Spustí Streamlit rozhraní pro MedDocAI Anonymizer")
    parser.add_argument("--port", type=int, default=8501, help="Port pro Streamlit aplikaci (výchozí: 8501)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host pro Streamlit aplikaci (výchozí: 0.0.0.0)")
    args = parser.parse_args()
    
    # Nastavení proměnných prostředí pro Streamlit
    os.environ["STREAMLIT_SERVER_PORT"] = str(args.port)
    os.environ["STREAMLIT_SERVER_ADDRESS"] = args.host
    
    # Cesta k Streamlit aplikaci
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "streamlit", "app.py")
    
    # Spuštění Streamlit aplikace
    os.system(f"streamlit run {app_path} --server.port {args.port} --server.address {args.host}")

if __name__ == "__main__":
    main()
