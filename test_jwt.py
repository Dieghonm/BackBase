"""
Script para testar a funcionalidade JWT
Execute: python test_jwt.py
"""
import sys
import os
sys.path.append('app')

from utils.jwt_auth import (
    create_access_token, 
    verify_token, 
    get_user_from_token,
    create_user_token_data,
    hash_password,
    verify_password
)

def test_password_hashing():
    """Testa hash e verificação de senhas"""
    print("🔐 Testando hash de senhas...")
    
    senha = "minhasenha123"
    hashed = hash_password(senha)
    
    print(f"Senha original: {senha}")
    print(f"Hash: {hashed}")
    print(f"Verificação: {verify_password(senha, hashed)}")
    print(f"Senha errada: {verify_password('senhaerrada', hashed)}")
    print()

def test_jwt_creation_and_verification():
    """Testa criação e verificação de JWT"""
    print("🎯 Testando JWT...")
    
    # Dados do usuário
    token_data = create_user_token_data(
        user_id=1,
        email="test@example.com",
        login="testuser",
        tag="admin"
    )
    
    # Cria token
    token = create_access_token(data=token_data)
    print(f"Token criado: {token[:50]}...")
    
    # Verifica token
    try:
        payload = verify_token(token)
        print(f"Token válido! Payload: {payload}")
        
        # Extrai dados do usuário
        user_data = get_user_from_token(token)
        print(f"Dados do usuário: {user_data}")
        
    except Exception as e:
        print(f"Erro ao verificar token: {e}")
    
    print()

def test_invalid_token():
    """Testa token inválido"""
    print("❌ Testando token inválido...")
    
    try:
        invalid_token = "token.invalido.aqui"
        verify_token(invalid_token)
    except Exception as e:
        print(f"Erro esperado: {e}")
    
    print()

if __name__ == "__main__":
    print("🧪 Iniciando testes JWT...")
    print("=" * 50)
    
    test_password_hashing()
    test_jwt_creation_and_verification()
    test_invalid_token()
    
    print("✅ Testes concluídos!")
    print("\n📝 Como usar na API:")
    print("1. POST /cadastro - cadastrar usuário")
    print("2. POST /login - fazer login e receber token")
    print("3. GET /me - usar token para acessar dados")
    print("4. Header: Authorization: Bearer <token>")