
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
        remetente_nome: str = "Eden Map"
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
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)

            if response.status_code in [200, 201]:
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
    
    def enviar_boas_vindas(
        self,
        email: str,
        login: str,
        plan: str = "trial"
    ) -> bool:
        """
        Envia email de boas-vindas para novo usuário
        
        Args:
            email: Email do usuário
            login: Login do usuário
            plan: Plano contratado
            
        Returns:
            True se enviado com sucesso
        """
        planos_nomes = {
            "trial": "Teste Grátis",
            "mensal": "Mensal",
            "trimestral": "Trimestral", 
            "semestral": "Semestral",
            "anual": "Anual",
            "admin": "Administrador"
        }
        
        plano_nome = planos_nomes.get(plan.lower(), plan)
        
        assunto = f"🎉 Bem-vindo ao Eden Map, {login}!"
        
        corpo_html = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f4f7fa;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 12px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 700;
                    }}
                    .header p {{
                        margin: 10px 0 0 0;
                        font-size: 16px;
                        opacity: 0.9;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .content p {{
                        color: #333;
                        line-height: 1.8;
                        margin: 15px 0;
                        font-size: 15px;
                    }}
                    .welcome-box {{
                        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                        border-radius: 8px;
                        padding: 25px;
                        text-align: center;
                        margin: 25px 0;
                    }}
                    .welcome-box h2 {{
                        color: #667eea;
                        margin: 0 0 15px 0;
                        font-size: 22px;
                    }}
                    .plan-badge {{
                        display: inline-block;
                        background-color: #667eea;
                        color: white;
                        padding: 8px 20px;
                        border-radius: 20px;
                        font-weight: 600;
                        font-size: 14px;
                        margin-top: 10px;
                    }}
                    .features {{
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 25px 0;
                    }}
                    .features h3 {{
                        color: #333;
                        margin: 0 0 15px 0;
                        font-size: 18px;
                    }}
                    .feature-item {{
                        display: flex;
                        align-items: center;
                        margin: 12px 0;
                        color: #555;
                    }}
                    .feature-icon {{
                        background-color: #667eea;
                        color: white;
                        width: 24px;
                        height: 24px;
                        border-radius: 50%;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 12px;
                        font-size: 14px;
                        flex-shrink: 0;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 15px 35px;
                        border-radius: 6px;
                        text-decoration: none;
                        font-weight: 600;
                        margin: 20px 0;
                        transition: transform 0.2s;
                    }}
                    .cta-button:hover {{
                        transform: translateY(-2px);
                    }}
                    .info-box {{
                        background-color: #e3f2fd;
                        border-left: 4px solid #2196f3;
                        padding: 15px;
                        margin: 20px 0;
                        color: #0d47a1;
                        border-radius: 4px;
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        padding: 25px;
                        text-align: center;
                        font-size: 13px;
                        color: #666;
                        border-top: 1px solid #e0e0e0;
                    }}
                    .footer a {{
                        color: #667eea;
                        text-decoration: none;
                    }}
                    .divider {{
                        height: 1px;
                        background: linear-gradient(to right, transparent, #ddd, transparent);
                        margin: 30px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Bem-vindo ao Eden Map!</h1>
                        <p>Sua conta foi criada com sucesso</p>
                    </div>
                    
                    <div class="content">
                        <p>Olá <strong>{login}</strong>,</p>
                        
                        <p>É com grande satisfação que damos as boas-vindas ao <strong>Eden Map</strong>! 
                        Sua conta foi criada com sucesso e você já pode começar a explorar todas as funcionalidades da nossa plataforma.</p>
                        
                        <div class="welcome-box">
                            <h2>✓ Cadastro Confirmado</h2>
                            <p style="margin: 10px 0; color: #555;">Você está no plano:</p>
                            <span class="plan-badge">{plano_nome}</span>
                        </div>
                        
                        <div class="features">
                            <h3>🚀 O que você pode fazer agora:</h3>
                            
                            <div class="feature-item">
                                <span class="feature-icon">✓</span>
                                <span>Acessar sua conta com seu login e senha</span>
                            </div>
                            
                            <div class="feature-item">
                                <span class="feature-icon">✓</span>
                                <span>Explorar todas as funcionalidades da API</span>
                            </div>
                            
                            <div class="feature-item">
                                <span class="feature-icon">✓</span>
                                <span>Gerenciar seu perfil e configurações</span>
                            </div>
                            
                            <div class="feature-item">
                                <span class="feature-icon">✓</span>
                                <span>Acessar a documentação completa em /docs</span>
                            </div>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="https://seu-app.onrender.com/docs" class="cta-button">
                                📚 Explorar Documentação
                            </a>
                        </div>
                        
                        <div class="divider"></div>
                        
                        <div class="info-box">
                            <strong>💡 Dica:</strong> Seu token de acesso tem validade baseada no seu plano. 
                            Mantenha suas credenciais seguras e nunca compartilhe com terceiros.
                        </div>
                        
                        <p><strong>Informações da sua conta:</strong></p>
                        <ul style="color: #555; line-height: 1.8;">
                            <li><strong>Login:</strong> {login}</li>
                            <li><strong>Email:</strong> {email}</li>
                            <li><strong>Plano:</strong> {plano_nome}</li>
                        </ul>
                        
                        <p style="margin-top: 30px;">Se você tiver alguma dúvida ou precisar de ajuda, nossa equipe está sempre disponível!</p>
                        
                        <p style="color: #888; font-size: 14px; margin-top: 30px;">
                            Não foi você que criou esta conta? Por favor, ignore este email ou entre em contato conosco imediatamente.
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>Eden Map API</strong></p>
                        <p>© 2025 Eden Map. Todos os direitos reservados.</p>
                        <p style="margin-top: 10px;">
                            <a href="#">Documentação</a> • 
                            <a href="#">Suporte</a> • 
                            <a href="#">Política de Privacidade</a>
                        </p>
                        <p style="margin-top: 15px; color: #999;">
                            Este é um email automático, não responda.
                        </p>
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
                            A Eden Map API nunca pedirá este código por email ou telefone.
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

