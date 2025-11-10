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
            "trial": "Teste Grátis (15 dias)",
            "mensal": "Mensal",
            "trimestral": "Trimestral", 
            "semestral": "Semestral",
            "anual": "Anual",
            "admin": "Administrador"
        }
        
        plano_nome = planos_nomes.get(plan.lower(), plan)
        
        assunto = f"Bem-vindo ao Eden Map, {login}! 🌿"
        
        corpo_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bem-vindo ao Eden Map</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif; background: linear-gradient(135deg, #1a1d29 0%, #2d3748 100%); min-height: 100vh;">
    
    <!-- Container Principal -->
    <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #1a1d29 0%, #2d3748 100%); padding: 40px 20px;">
        <tr>
            <td align="center">
                
                <!-- Card do Email -->
                <table width="600" cellpadding="0" cellspacing="0" style="background: rgba(42, 46, 66, 0.95); border-radius: 20px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5); overflow: hidden; max-width: 100%;">
                    
                    <!-- Header com Logo -->
                    <tr>
                        <td align="center" style="background: linear-gradient(135deg, #0a84ff 0%, #8a4aed 100%); padding: 50px 40px;">
                            <!-- LOGO PLACEHOLDER - Substituir pela imagem real quando disponível -->
                            <div style="width: 200px; height: 60px; background: rgba(255,255,255,0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                                <span style="color: #ffffff; font-size: 28px; font-weight: bold; letter-spacing: 2px;">EDEN MAP</span>
                            </div>
                            
                            <h1 style="margin: 20px 0 0 0; color: #ffffff; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;">
                                Bem-vindo! 🌿
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Conteúdo -->
                    <tr>
                        <td style="padding: 50px 40px;">
                            
                            <!-- Mensagem de Boas-vindas -->
                            <p style="color: #e2e8f0; font-size: 18px; line-height: 1.8; margin: 0 0 30px 0; text-align: center;">
                                Olá <strong style="color: #ffffff; font-size: 20px;">{login}</strong>,
                            </p>
                            
                            <p style="color: #cbd5e0; font-size: 16px; line-height: 1.8; margin: 0 0 30px 0; text-align: center;">
                                É com grande satisfação que damos as boas-vindas ao <strong style="color: #8a4aed;">Eden Map</strong>! 
                                Sua conta foi criada com sucesso e você já pode começar a explorar todas as funcionalidades da nossa plataforma.
                            </p>
                            
                            <!-- Card de Confirmação -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, rgba(10, 132, 255, 0.15) 0%, rgba(138, 74, 237, 0.15) 100%); border-radius: 16px; border: 2px solid rgba(138, 74, 237, 0.3); margin: 30px 0;">
                                <tr>
                                    <td style="padding: 30px; text-align: center;">
                                        <div style="font-size: 48px; margin-bottom: 15px;">✓</div>
                                        <h2 style="color: #ffffff; font-size: 22px; margin: 0 0 15px 0; font-weight: 600;">
                                            Cadastro Confirmado
                                        </h2>
                                        <p style="color: #cbd5e0; font-size: 15px; margin: 0 0 15px 0;">
                                            Você está no plano:
                                        </p>
                                        <div style="display: inline-block; background: linear-gradient(135deg, #0a84ff 0%, #8a4aed 100%); color: #ffffff; padding: 12px 30px; border-radius: 25px; font-weight: 600; font-size: 16px;">
                                            {plano_nome}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Informações da Conta -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background: rgba(26, 29, 41, 0.5); border-radius: 12px; margin: 30px 0; border: 1px solid rgba(138, 74, 237, 0.2);">
                                <tr>
                                    <td style="padding: 25px;">
                                        <h3 style="color: #ffffff; font-size: 18px; margin: 0 0 20px 0; font-weight: 600;">
                                            📋 Informações da Conta
                                        </h3>
                                        <table width="100%" cellpadding="8" cellspacing="0">
                                            <tr>
                                                <td style="color: #94a3b8; font-size: 14px; padding: 8px 0;">Login:</td>
                                                <td style="color: #ffffff; font-size: 14px; font-weight: 600; text-align: right; padding: 8px 0;">{login}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #94a3b8; font-size: 14px; padding: 8px 0;">Email:</td>
                                                <td style="color: #ffffff; font-size: 14px; font-weight: 600; text-align: right; padding: 8px 0;">{email}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #94a3b8; font-size: 14px; padding: 8px 0;">Plano:</td>
                                                <td style="color: #8a4aed; font-size: 14px; font-weight: 600; text-align: right; padding: 8px 0;">{plano_nome}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Recursos -->
                            <div style="margin: 30px 0;">
                                <h3 style="color: #ffffff; font-size: 18px; margin: 0 0 20px 0; font-weight: 600; text-align: center;">
                                    🚀 O que você pode fazer agora
                                </h3>
                                
                                <table width="100%" cellpadding="10" cellspacing="0">
                                    <tr>
                                        <td style="padding: 10px 0;">
                                            <div style="display: flex; align-items: center;">
                                                <span style="color: #0a84ff; font-size: 20px; margin-right: 12px;">✓</span>
                                                <span style="color: #cbd5e0; font-size: 15px;">Acessar sua conta com seu login e senha</span>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px 0;">
                                            <div style="display: flex; align-items: center;">
                                                <span style="color: #0a84ff; font-size: 20px; margin-right: 12px;">✓</span>
                                                <span style="color: #cbd5e0; font-size: 15px;">Explorar todas as funcionalidades da API</span>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px 0;">
                                            <div style="display: flex; align-items: center;">
                                                <span style="color: #0a84ff; font-size: 20px; margin-right: 12px;">✓</span>
                                                <span style="color: #cbd5e0; font-size: 15px;">Gerenciar seu perfil e configurações</span>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px 0;">
                                            <div style="display: flex; align-items: center;">
                                                <span style="color: #0a84ff; font-size: 20px; margin-right: 12px;">✓</span>
                                                <span style="color: #cbd5e0; font-size: 15px;">Acessar a documentação completa em /docs</span>
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Aviso de Segurança -->
                            <div style="background: rgba(255, 170, 46, 0.1); border-left: 4px solid #ffaa2e; padding: 20px; border-radius: 8px; margin: 30px 0;">
                                <p style="color: #ffaa2e; font-size: 15px; margin: 0; line-height: 1.6;">
                                    <strong>💡 Dica de Segurança:</strong><br>
                                    Mantenha suas credenciais seguras e nunca compartilhe com terceiros. Seu token de acesso é pessoal e intransferível.
                                </p>
                            </div>
                            
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background: rgba(26, 29, 41, 0.8); padding: 30px 40px; text-align: center; border-top: 1px solid rgba(138, 74, 237, 0.2);">
                            <p style="color: #94a3b8; font-size: 14px; margin: 0 0 10px 0;">
                                <strong style="color: #ffffff;">Eden Map</strong>
                            </p>
                            <p style="color: #64748b; font-size: 13px; margin: 0 0 15px 0;">
                                © 2025 Eden Map. Todos os direitos reservados.
                            </p>
                            <p style="color: #64748b; font-size: 12px; margin: 0; line-height: 1.6;">
                                Este é um email automático, não responda.<br>
                                Se você não criou esta conta, ignore este email.
                            </p>
                            <div style="margin-top: 20px;">
                                <a href="#" style="color: #8a4aed; text-decoration: none; font-size: 13px; margin: 0 10px;">Documentação</a>
                                <span style="color: #475569;">•</span>
                                <a href="#" style="color: #8a4aed; text-decoration: none; font-size: 13px; margin: 0 10px;">Suporte</a>
                                <span style="color: #475569;">•</span>
                                <a href="#" style="color: #8a4aed; text-decoration: none; font-size: 13px; margin: 0 10px;">Privacidade</a>
                            </div>
                        </td>
                    </tr>
                    
                </table>
                
            </td>
        </tr>
    </table>
    
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
        
        # Separar os 4 dígitos para exibir em boxes individuais
        digito1, digito2, digito3, digito4 = list(tempkey)
        
        corpo_html = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Eden Map - Recuperação de Senha</title>
            <style>
                * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                }}

                body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #212224 0%, #2a1833 50%, #212224 100%);
                color: #fff;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                }}

                .email-recovery {{
                width: 100%;
                max-width: 600px;
                background: rgba(42, 46, 66, 0.95);
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                overflow: hidden;
                }}
                .header {{
                background: linear-gradient(135deg, #1a1d29 0%, #2d3748 100%);
                padding: 50px 40px;
                text-align: center;
                }}

                .logo-box {{
                width: 200px;
                height: 60px;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0 16px 20px 200px;
                }}

                .logo-box p {{
                font-size: 28px;
                font-weight: 700;
                margin-right: 50px;
                }}

                .header h1 {{
                font-size: 28px;
                font-weight: 700;
                letter-spacing: -0.5px;
                }}

                .content {{
                padding: 50px 40px;
                }}

                .alert {{
                background: rgba(255, 170, 46, 0.1);
                border-left: 4px solid #ffaa2e;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                margin-bottom: 30px;
                color: #ffaa2e;
                font-size: 15px;
                line-height: 1.6;
                }}

                .greeting,
                .instructions {{
                color: #cbd5e0;
                font-size: 16px;
                line-height: 1.8;
                text-align: center;
                margin-bottom: 30px;
                }}

                .instructions {{
                margin-bottom: 40px;
                }}

                .code-card {{
                background: linear-gradient(-145deg, #1d1e20 0%, #746d7740 38%, #ffffff3b 50%, #746d7740 62%, #1d1e20 100%);
                border-radius: 16px;
                padding: 40px 30px;
                text-align: center;
                margin-bottom: 30px;
                }}

                .code-label {{
                color: #94a3b8;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 15px;
                }}

                .code-boxes {{
                display: flex;
                justify-content: center;
                gap: 15px;
                margin-bottom: 20px;
                }}

                .code-box {{
                width: 70px;
                height: 90px;
                background: #d9d9d98c;
                display: flex;
                justify-content: center;
                align-items: center;
                }}

                .code-box span {{
                color: #ffffff;
                font-size: 48px;
                font-weight: 700;
                font-family: 'Courier New', monospace;
                }}

                .expire {{
                color: #ff6b6b;
                font-size: 15px;
                font-weight: 600;
                }}

                .how-to {{
                background: rgba(26, 29, 41, 0.5);
                border-radius: 12px;
                border: 1px solid rgba(138, 74, 237, 0.2);
                padding: 25px;
                margin-bottom: 30px;
                }}

                .how-to h3 {{
                color: #ffffff;
                font-size: 18px;
                margin-bottom: 20px;
                font-weight: 600;
                }}

                .how-to ol {{
                color: #cbd5e0;
                font-size: 15px;
                line-height: 1.8;
                padding-left: 20px;
                }}

                .warning {{
                background: rgba(255, 107, 107, 0.1);
                border-left: 4px solid #ff6b6b;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 30px;
                color: #ff6b6b;
                font-size: 15px;
                line-height: 1.6;
                }}

                .help {{
                color: #94a3b8;
                font-size: 14px;
                text-align: center;
                line-height: 1.6;
                }}

                .help a {{
                color: #8a4aed;
                text-decoration: none;
                }}

                .help a:hover {{
                text-decoration: underline;
                }}

                .footer {{
                background: rgba(26, 29, 41, 0.8);
                border-top: 1px solid rgba(138, 74, 237, 0.2);
                padding: 30px 40px;
                text-align: center;
                font-size: 13px;
                color: #64748b;
                }}

                .footer strong {{
                color: #ffffff;
                }}

                .footer p {{
                margin-bottom: 10px;
                }}
            </style>
            </head>
            <body>
            <div id="email-recovery" class="email-recovery">
                <div class="header">
                <img src="https://raw.githubusercontent.com/Dieghonm/Eden-Map/refs/heads/main/assets/Logo2.png" alt="Logo Eden Map">
                <h1>Seu código de recuperação de senha</h1>
                </div>

                <div class="content">
                <div class="alert">
                    <strong>Se você <span style="color:#ff6b6b;">não solicitou</span> o token, <span style="color:#ff6b6b;">basta ignorar</span> esse email.</strong>
                </div>

                <p class="greeting">Olá <strong style="color:#fff;">{login}</strong>,</p>
                <p class="instructions">Use o código abaixo para redefinir sua senha:</p>

                <div class="code-card">
                    <p class="code-label">Seu Código</p>
                    <div class="code-boxes">
                    <div class="code-box"><span>{digito1}</span></div>
                    <div class="code-box"><span>{digito2}</span></div>
                    <div class="code-box"><span>{digito3}</span></div>
                    <div class="code-box"><span>{digito4}</span></div>
                    </div>
                    <p class="expire">⏱️ Expira em 15 minutos</p>
                </div>

                <div class="warning">
                    <strong>⚠️ Importante:</strong><br>
                    Nunca compartilhe este código com ninguém. A equipe do Eden Map nunca pedirá este código por email ou telefone.
                </div>

                <p class="help">
                    Precisa de ajuda?<br>
                    Entre em contato: <a href="mailto:duo.estudio.tech@gmail.com">duo.estudio.tech@gmail.com</a>
                </p>
                </div>

                <div class="footer">
                <p><strong>Eden Map</strong></p>
                <p>© 2025 Eden Map. Todos os direitos reservados.</p>
                <p>Este é um email automático, não responda.<br>Se você não solicitou esta recuperação, ignore este email.</p>
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
