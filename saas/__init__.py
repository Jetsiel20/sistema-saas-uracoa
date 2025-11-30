"""
Sistema SaaS - Hospital Tipo 1 Uracoa
J&S Software Inteligentes
Desarrollado por: Santos & Team
"""
from flask import Flask
from datetime import datetime
from saas.config import config
from saas.extensions import db, login_manager, migrate, mail, csrf, cache, compress


def create_app(config_name='default'):
    """Factory para crear la aplicación Flask"""
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configurar caché para rendimiento
    app.config['CACHE_TYPE'] = 'SimpleCache'  # En producción usar Redis/Memcached
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutos
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)
    compress.init_app(app)  # Compresión automática de respuestas HTTP
    
    # Configurar user_loader para Flask-Login
    from saas.models import Usuario
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Registrar blueprints - AUTH PRIMERO
    from saas.auth import auth_bp
    from saas.main import main_bp
    
    # Módulos médicos
    from saas.consultas import consultas_bp
    from saas.emergencias import emergencias_bp
    from saas.internados import bp as internados_bp
    from saas.especialidades import especialidades_bp
    from saas.enfermeros import enfermeros_bp
    from saas.laboratorio import laboratorio_bp
    from saas.medicamentos import medicamentos_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(consultas_bp, url_prefix='/consultas')
    app.register_blueprint(emergencias_bp, url_prefix='/emergencias')
    app.register_blueprint(internados_bp, url_prefix='/internados')
    app.register_blueprint(especialidades_bp, url_prefix='/especialidades')
    app.register_blueprint(enfermeros_bp, url_prefix='/enfermeros')
    app.register_blueprint(laboratorio_bp, url_prefix='/laboratorio')
    app.register_blueprint(medicamentos_bp, url_prefix='/medicamentos')
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    # Context processors
    @app.context_processor
    def inject_app_info():
        from saas.utils import get_menu_for, is_menu_active
        return {
            'app_name': 'Hospital Tipo 1 Uracoa',
            'company': 'J&S Software Inteligentes',
            'year': 2025,
            'now': datetime.now,
            'get_menu_for': get_menu_for,
            'is_menu_active': is_menu_active
        }
    
    return app
