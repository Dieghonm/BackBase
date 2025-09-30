from datetime import datetime
from .session import SessionLocal
from ..utils.security import hash_password, gerar_credencial, verify_credencial_uniqueness
import logging

logger = logging.getLogger('app.database.seeds')

usuarios_iniciais = [
    {
        "login": "dieghonm", 
        "email": "dieghonm@gmail.com", 
        "tag": "admin", 
        "senha": "Admin123@",
        "plan": "anual"
    },
    {
        "login": "cavamaga", 
        "email": "cava.maga@gmail.com", 
        "tag": "admin",
        "senha": "Admin123@",
        "plan": "anual"
    },
    {
        "login": "tiaguetevital", 
        "email": "tiagovital999@gmail.com", 
        "tag": "admin",
        "senha": "Admin123@", 
        "plan": "anual" 
    },
    {
        "login": "pietro", 
        "email": "tester@gmail.com", 
        "tag": "tester",
        "senha": "Tester123@",
        "plan": "anual"
    },
    {
        "login": "demo_cliente", 
        "email": "cliente@demo.com", 
        "tag": "cliente", 
        "senha": "Cliente123@",
        "plan": "trial"
    }
]

def criar_usuarios_iniciais():
    """
    Cria usuários iniciais se eles não existirem
    """
    from ..models.user import Usuario
    
    db = SessionLocal()
    
    try:
        logger.info("🌱 Iniciando criação de usuários iniciais...")
        usuarios_criados = 0
        usuarios_existentes = 0
        
        for u in usuarios_iniciais:
            try:
                usuario_existente = db.query(Usuario).filter_by(email=u["email"]).first()
                
                if not usuario_existente:
                    senha_hashada = hash_password(u["senha"])
                    
                    max_attempts = 5
                    credencial = None
                    
                    for attempt in range(max_attempts):
                        credencial = gerar_credencial(u["email"], dias=365)
                        break
                    
                    if not credencial:
                        logger.error(f"Erro ao gerar credencial única para {u['email']}")
                        continue
                    
                    usuario = Usuario(
                        login=u["login"].lower().strip(),
                        email=u["email"].lower().strip(),
                        tag=u["tag"],
                        senha=senha_hashada,
                        plan=u["plan"],
                        plan_date=datetime.utcnow(),
                        credencial=credencial,
                        created_at=datetime.utcnow()
                    )
                    
                    db.add(usuario)
                    usuarios_criados += 1
                    logger.info(f"✅ Usuário inicial criado: {u['login']} ({u['email']}) - Tag: {u['tag']}")
                    
                else:
                    usuarios_existentes += 1
                    logger.info(f"👤 Usuário já existe: {u['login']} ({u['email']})")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao processar usuário {u.get('login', 'unknown')}: {str(e)}")
                continue
        
        if usuarios_criados > 0:
            db.commit()
            logger.info(f"✅ {usuarios_criados} usuários iniciais criados com sucesso!")
        
        if usuarios_existentes > 0:
            logger.info(f"👥 {usuarios_existentes} usuários já existiam no sistema")
        
        total_usuarios = db.query(Usuario).count()
        logger.info(f"📊 Total de usuários no sistema: {total_usuarios}")
        
        # ✅ TAGS PADRONIZADAS
        for tag in ['admin', 'tester', 'cliente']:
            count = db.query(Usuario).filter_by(tag=tag).count()
            if count > 0:
                logger.info(f"   - {tag.capitalize()}s: {count}")
        
    except Exception as e:
        logger.error(f"❌ Erro geral ao criar usuários iniciais: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def resetar_usuarios_iniciais():
    """
    CUIDADO: Remove todos os usuários e recria os iniciais
    Usar apenas em desenvolvimento/testes
    """
    from ..models.user import Usuario
    
    db = SessionLocal()
    
    try:
        logger.warning("⚠️  RESETANDO TODOS OS USUÁRIOS - OPERAÇÃO DESTRUTIVA!")
        usuarios_removidos = db.query(Usuario).count()
        db.query(Usuario).delete()
        
        logger.warning(f"🗑️  {usuarios_removidos} usuários removidos")
        
        db.commit()
        criar_usuarios_iniciais()
        
        logger.info("✅ Reset de usuários concluído")
        
    except Exception as e:
        logger.error(f"❌ Erro ao resetar usuários: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def listar_usuarios_sistema():
    """
    Lista todos os usuários do sistema (para debug/administração)
    """
    from ..models.user import Usuario
    
    db = SessionLocal()
    
    try:
        usuarios = db.query(Usuario).all()
        
        logger.info(f"👥 Usuários no sistema ({len(usuarios)}):")
        
        for user in usuarios:
            logger.info(f"   - ID: {user.id} | Login: {user.login} | Email: {user.email} | Tag: {user.tag} | Plan: {user.plan}")
        
        return usuarios
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar usuários: {str(e)}")
        return []
    finally:
        db.close()