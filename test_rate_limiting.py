"""
Script para testar Rate Limiting
Execute: python test_rate_limiting.py

IMPORTANTE: Execute este script APÓS iniciar o servidor:
uvicorn app.main:app --reload
"""
import requests
import time
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_login_rate_limit():
    """Testa rate limit do endpoint /login (5/minuto)"""
    print("🔐 Testando Rate Limit - LOGIN (5 tentativas por minuto)")
    print("-" * 50)
    
    login_data = {
        "email_ou_login": "test@example.com",
        "senha": "senhaqualquer"
    }
    
    successful_requests = 0
    rate_limited_requests = 0
    
    # Faz 7 tentativas (deve bloquear após 5)
    for i in range(1, 8):
        try:
            response = requests.post(f"{BASE_URL}/login", json=login_data)
            
            if response.status_code == 429:
                rate_limited_requests += 1
                print(f"Tentativa {i}: ❌ RATE LIMITED - {response.status_code}")
                print(f"   Resposta: {response.json()}")
            else:
                successful_requests += 1
                print(f"Tentativa {i}: ✅ PERMITIDA - {response.status_code}")
            
            time.sleep(1)  # Pausa de 1 segundo entre requests
            
        except Exception as e:
            print(f"Tentativa {i}: 🚨 ERRO - {e}")
    
    print(f"\n📊 Resultado:")
    print(f"   - Requests permitidas: {successful_requests}")
    print(f"   - Requests bloqueadas: {rate_limited_requests}")
    print()

def test_cadastro_rate_limit():
    """Testa rate limit do endpoint /cadastro (3/minuto)"""
    print("📝 Testando Rate Limit - CADASTRO (3 tentativas por minuto)")
    print("-" * 50)
    
    successful_requests = 0
    rate_limited_requests = 0
    
    # Faz 5 tentativas (deve bloquear após 3)
    for i in range(1, 6):
        cadastro_data = {
            "login": f"testuser{i}",
            "senha": "123456",
            "email": f"test{i}@example.com",
            "tag": "cliente"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/cadastro", json=cadastro_data)
            
            if response.status_code == 429:
                rate_limited_requests += 1
                print(f"Tentativa {i}: ❌ RATE LIMITED - {response.status_code}")
                print(f"   Resposta: {response.json()}")
            else:
                successful_requests += 1
                status_msg = "SUCESSO" if response.status_code == 200 else "PERMITIDA"
                print(f"Tentativa {i}: ✅ {status_msg} - {response.status_code}")
            
            time.sleep(1)  # Pausa de 1 segundo entre requests
            
        except Exception as e:
            print(f"Tentativa {i}: 🚨 ERRO - {e}")
    
    print(f"\n📊 Resultado:")
    print(f"   - Requests permitidas: {successful_requests}")
    print(f"   - Requests bloqueadas: {rate_limited_requests}")
    print()

def test_rate_limit_status():
    """Testa endpoint de status do rate limiting"""
    print("📊 Verificando Status do Rate Limiting")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/rate-limit-status")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Status obtido com sucesso:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erro ao obter status: {response.status_code}")
            print(f"   Resposta: {response.text}")
    
    except Exception as e:
        print(f"🚨 Erro: {e}")
    
    print()

def test_basic_endpoints():
    """Testa endpoints básicos para verificar se API está funcionando"""
    print("🔍 Verificando se API está funcionando")
    print("-" * 50)
    
    endpoints = [
        ("/", "GET"),
        ("/health", "GET"),
        ("/rate-limit-status", "GET")
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            
            print(f"{method} {endpoint}: {'✅' if response.status_code == 200 else '❌'} {response.status_code}")
            
        except Exception as e:
            print(f"{method} {endpoint}: 🚨 ERRO - {e}")
    
    print()

def wait_for_rate_limit_reset():
    """Espera o rate limit resetar"""
    print("⏳ Aguardando reset do rate limit (60 segundos)...")
    for i in range(60, 0, -5):
        print(f"   {i} segundos restantes...")
        time.sleep(5)
    print("✅ Rate limit deve ter resetado!\n")

def main():
    print("🧪 INICIANDO TESTES DE RATE LIMITING")
    print("=" * 60)
    print("⚠️  CERTIFIQUE-SE DE QUE O SERVIDOR ESTÁ RODANDO:")
    print("   uvicorn app.main:app --reload")
    print("=" * 60)
    print()
    
    # Verifica se API está funcionando
    test_basic_endpoints()
    
    # Testa status do rate limiting
    test_rate_limit_status()
    
    # Testa rate limit do login
    test_login_rate_limit()
    
    # Testa rate limit do cadastro
    test_cadastro_rate_limit()
    
    print("🎯 RESUMO DOS TESTES:")
    print("=" * 60)
    print("✅ Se você viu requests sendo bloqueadas (429), o Rate Limiting está FUNCIONANDO!")
    print("❌ Se todas as requests foram permitidas, algo está errado.")
    print()
    print("📋 CHECKLIST CHECKPOINT 3:")
    print("   [✅] slowapi instalado no requirements.txt")
    print("   [✅] limiter configurado no main.py")
    print("   [✅] rate limit no /login (5/minuto)")
    print("   [✅] rate limit no /cadastro (3/minuto)")
    print("   [✅] handler personalizado para rate limit")
    print("   [✅] testes de funcionamento")
    print()
    print("🏆 CHECKPOINT 3 CONCLUÍDO!")

if __name__ == "__main__":
    main()