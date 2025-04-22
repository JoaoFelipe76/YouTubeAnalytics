"""
Análise de Canal do YouTube - Aplicação Principal
"""
import sys
import os
import streamlit.web.bootstrap as bootstrap
from streamlit.web.server import Server

def main():
    """Função principal para iniciar a aplicação"""
    print("Iniciando a aplicação de análise do canal Let's Media Oficia...")
    
    try:
        # Verificar se as dependências estão instaladas
        import streamlit
        import pandas as pd
        import numpy as np
        import plotly
        from googleapiclient.discovery import build
        
        print("Todas as dependências estão instaladas.")
        
        # Iniciar o servidor Streamlit
        print("Iniciando o dashboard Streamlit...")
        
        # Usar o arquivo streamlit_app.py como ponto de entrada
        bootstrap.run("streamlit_app.py", "", [], {})
        
    except ImportError as e:
        print(f"Erro: {e}")
        print("Algumas dependências estão faltando. Execute 'pip install -r requirements.txt' para instalar todas as dependências.")
        return 1
    except Exception as e:
        print(f"Erro ao iniciar a aplicação: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 