#!/usr/bin/env python3
"""
Script para executar testes do BackBase API
Fornece diferentes opções de execução de testes
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Executa um comando e mostra o resultado"""
    print(f"\n🔥 {description}")
    print(f"📌 Executando: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"✅ {description} - SUCESSO")
    else:
        print(f"❌ {description} - FALHOU")
    
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="Execute testes do BackBase API")
    parser.add_argument(
        '--type', 
        choices=['all', 'unit', 'integration', 'auth', 'crud', 'security', 'performance', 'stress'],
        default='all',
        help='Tipo de testes para executar'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Gerar relatório de cobertura'
    )
    parser.add_argument(
        '--html',
        action='store_true',
        help='Gerar relatório HTML'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Output verboso'
    )
    parser.add_argument(
        '--fast',
        action='store_true',
        help='Execução rápida (pula testes lentos)'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Execução paralela'
    )
    
    args = parser.parse_args()
    
    # Configurar comando base do pytest
    pytest_cmd = ['python', '-m', 'pytest']
    
    # Configurar verbose
    if args.verbose:
        pytest_cmd.extend(['-v', '-s'])
    
    # Configurar cobertura
    if args.coverage:
        pytest_cmd.extend([
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov'
        ])
    
    # Configurar relatório HTML
    if args.html:
        pytest_cmd.extend(['--html=reports/report.html', '--self-contained-html'])
    
    # Configurar execução paralela
    if args.parallel:
        pytest_cmd.extend(['-n', 'auto'])
    
    # Configurar tipo de teste
    if args.type == 'unit':
        pytest_cmd.extend(['-m', 'unit'])
    elif args.type == 'integration':
        pytest_cmd.extend(['-m', 'integration'])
    elif args.type == 'auth':
        pytest_cmd.extend(['tests/test_auth.py'])
    elif args.type == 'crud':
        pytest_cmd.extend(['tests/test_users.py'])
    elif args.type == 'security':
        pytest_cmd.extend(['tests/test_security.py'])
    elif args.type == 'performance':
        pytest_cmd.extend(['tests/test_performance.py'])
    elif args.type == 'stress':
        pytest_cmd.extend(['-m', 'stress'])
    
    # Configurar execução rápida
    if args.fast:
        pytest_cmd.extend(['-m', 'not slow'])
    
    # Criar diretório de reports se não existir
    os.makedirs('reports', exist_ok=True)
    
    # Executar testes
    print("🚀 INICIANDO EXECUÇÃO DOS TESTES DO BACKBASE API")
    print(f"📝 Tipo: {args.type}")
    print(f"📊 Cobertura: {'Sim' if args.coverage else 'Não'}")
    print(f"📋 Relatório HTML: {'Sim' if args.html else 'Não'}")
    print(f"⚡ Execução Rápida: {'Sim' if args.fast else 'Não'}")
    print(f"🔀 Paralelo: {'Sim' if args.parallel else 'Não'}")
    
    # Executar testes
    return_code = run_command(pytest_cmd, f"TESTES {args.type.upper()}")
    
    # Mostrar relatórios gerados
    if args.coverage and return_code == 0:
        print(f"\n📊 Relatório de cobertura gerado em: htmlcov/index.html")
    
    if args.html and return_code == 0:
        print(f"📋 Relatório HTML gerado em: reports/report.html")
    
    return return_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)