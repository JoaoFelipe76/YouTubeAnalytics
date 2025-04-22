"""
Script para agendar a execução do relatório do Slack
"""
import os
import time
import schedule
import subprocess
from datetime import datetime

def run_slack_report():
    """Executa o script de relatório do Slack"""
    print(f"[{datetime.now()}] Executando relatório do Slack...")
    try:
        result = subprocess.run(["python", "slack_reporter.py"], check=True)
        if result.returncode == 0:
            print(f"[{datetime.now()}] Relatório enviado com sucesso!")
        else:
            print(f"[{datetime.now()}] Erro ao enviar relatório.")
    except Exception as e:
        print(f"[{datetime.now()}] Exceção ao executar relatório: {e}")

def main():
    """Função principal para agendar o envio de relatórios"""
    print(f"[{datetime.now()}] Iniciando agendador de relatórios...")
    
    # Agenda o envio diário do relatório às 10h
    schedule.every().day.at("10:00").do(run_slack_report)
    
    # Também podemos agendar relatórios semanais
    schedule.every().monday.at("08:00").do(run_slack_report)
    
    print(f"[{datetime.now()}] Agendamento configurado!")
    print("Relatórios agendados para:")
    print("- Todos os dias às 10:00")
    print("- Todas as segundas-feiras às 08:00")
    
    # Executa imediatamente um relatório para teste
    print(f"[{datetime.now()}] Executando relatório inicial de teste...")
    run_slack_report()
    
    # Loop de verificação dos agendamentos
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verifica a cada minuto

if __name__ == "__main__":
    main() 