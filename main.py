"""
Análise de Canal do YouTube - Aplicação Principal
"""
import sys
import os
from analytics_dashboard import app

def main():
    """Função principal para iniciar a aplicação"""
    print("Iniciando a aplicação de análise do canal Let's Media Oficia...")
    
    try:
        # Verificar se as dependências estão instaladas
        import dash
        import pandas as pd
        import numpy as np
        import plotly
        from googleapiclient.discovery import build
        
        print("Todas as dependências estão instaladas.")
        
        # Configurar porta para o Heroku
        port = int(os.environ.get("PORT", 8050))
        
        # Iniciar o servidor
        print(f"Iniciando o dashboard em porta {port}")
        app.run_server(host="0.0.0.0", port=port, debug=False)
        
    except ImportError as e:
        print(f"Erro: {e}")
        print("Algumas dependências estão faltando. Execute 'pip install -r requirements.txt' para instalar todas as dependências.")
        return 1
    except Exception as e:
        print(f"Erro ao iniciar a aplicação: {e}")
        return 1
    
    return 0

# Disponibilizar app.server para Heroku
server = app.server

if __name__ == "__main__":
    sys.exit(main()) 