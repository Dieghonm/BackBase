# app/services/email_service.py
import requests
import logging
from typing import Optional
from ..core.config import settings

logger = logging.getLogger('app.services.email_service')

class BrevoEmailService:
    """Serviço para enviar emails através da API do Brevo"""
    
    BASE_URL = "https://api.brevo.com/v3"
    
    def __init__(self, api_key: str):
        """
        Inicializa o serviço Brevo
        
        Args:
            api_key: Chave de API do Brevo
        """
        self.api_key = api_key
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": api_key
        }
    
    def enviar_email_simples(
        self,
        destinatario: str,
        assunto: str,
        corpo_html: str,
        remetente_email: str = "duo.estudio.tech@gmail.com",
        remetente_nome: str = "BackBase API"
    ) -> bool:
        """
        Envia um email simples através do Brevo
        
        Args:
            destinatario: Email do destinatário
            assunto: Assunto do email
            corpo_html: Corpo do email em HTML
            remetente_email: Email de origem
            remetente_nome: Nome de quem envia
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            print(destinatario,remetente_email, '<---------------------------------')
            url = f"{self.BASE_URL}/smtp/email"
            
            payload = {
                "sender": {
                    "name": remetente_nome,
                    "email": remetente_email
                },
                "to": [
                    {
                        "email": destinatario,
                        "name": destinatario.split("@")[0]
                    }
                ],
                "subject": assunto,
                "htmlContent": corpo_html
            }
            print(self.headers,'<----------------')
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)

            if response.status_code in [200, 201]:
                print('dentro')
                logger.info(f"✅ Email enviado com sucesso para {destinatario}")
                logger.debug(f"Response: {response.json()}")
                return True
            else:
                logger.error(f"❌ Erro ao enviar email: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro de conexão com Brevo: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email: {str(e)}")
            return False
    
    def enviar_tempkey(
        self,
        email: str,
        login: str,
        tempkey: str
    ) -> bool:
        """
        Envia o tempkey (senha temporária) por email
        
        Args:
            email: Email do usuário
            login: Login do usuário
            tempkey: Código de 4 dígitos
            
        Returns:
            True se enviado com sucesso
        """
        assunto = "🔐 Seu Código de Recuperação de Senha - Eden Map"
        print(email, tempkey, '<-----------------')
        corpo_html = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 24px;
                    }}
                    .content {{
                        padding: 30px;
                    }}
                    .content p {{
                        color: #333;
                        line-height: 1.6;
                        margin: 10px 0;
                    }}
                    .code-box {{
                        background-color: #f8f9fa;
                        border: 2px dashed #667eea;
                        border-radius: 6px;
                        padding: 20px;
                        text-align: center;
                        margin: 20px 0;
                    }}
                    .code {{
                        font-size: 36px;
                        font-weight: bold;
                        color: #667eea;
                        letter-spacing: 5px;
                        font-family: 'Courier New', monospace;
                    }}
                    .validity {{
                        color: #e74c3c;
                        font-size: 14px;
                        margin-top: 10px;
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        padding: 15px;
                        text-align: center;
                        font-size: 12px;
                        color: #666;
                        border-top: 1px solid #ddd;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 10px;
                        margin: 15px 0;
                        color: #856404;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Eden Map</h1>
                        <p>Recuperação de Senha</p>
                    </div>
                    
                    <div class="content">
                        <p>Olá <strong>{login}</strong>,</p>
                        
                        <p>Você solicitou uma recuperação de senha. Use o código abaixo para redefinir sua senha:</p>
                        
                        <div class="code-box">
                            <div class="code">{tempkey}</div>
                            <div class="validity">✓ Válido por 15 minutos</div>
                        </div>
                        
                        <div class="warning">
                            <strong>⚠️ Importante:</strong> Nunca compartilhe este código com ninguém. 
                            A BackBase API nunca pedirá este código por email ou telefone.
                        </div>
                        
                        <p><strong>Como usar:</strong></p>
                        <ol>
                            <li>Acesse o formulário de recuperação de senha</li>
                            <li>Insira o código: <strong>{tempkey}</strong></li>
                            <li>Defina sua nova senha</li>
                            <li>Faça login com suas novas credenciais</li>
                        </ol>
                        
                        <p>Se você não solicitou esta recuperação de senha, ignore este email.</p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2025 Eden Map API. Todos os direitos reservados.</p>
                        <p>Este é um email automático, não responda.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return self.enviar_email_simples(
            destinatario=email,
            assunto=assunto,
            corpo_html=corpo_html
        )


def get_email_service() -> Optional[BrevoEmailService]:
    """
    Cria uma instância do BrevoEmailService se a API key estiver configurada
    
    Returns:
        BrevoEmailService ou None se não configurado
    """
    api_key = settings.brevo_api_key
    
    if not api_key:
        logger.warning("⚠️  BREVO_API_KEY não configurada no .env")
        return None
    
    return BrevoEmailService(api_key)