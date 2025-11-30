"""
Seed inicial del sistema SaaS Hospital Tipo 1 Uracoa
Empresa: J&S Software Inteligentes
Versión: Producción inicial
"""
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from saas import create_app
from saas.extensions import db
from saas.models import Usuario
from datetime import datetime


def init_production_users():
    """Crear usuarios de producción del Hospital Tipo 1 Uracoa"""
    app = create_app('development')
    
    with app.app_context():
        print("\n🏥 Hospital Tipo 1 Uracoa - J&S Software Inteligentes")
        print("🌱 Iniciando carga de datos base...\n")
        
        # Verificar si ya existe algún usuario
        existing_users = Usuario.query.count()
        if existing_users > 0:
            print(f"⚠️  Ya existen {existing_users} usuario(s) en el sistema.")
            respuesta = input("¿Deseas continuar de todas formas? (s/n): ").strip().lower()
            if respuesta != 's':
                print("❌ Operación cancelada.")
                return
        
        # Crear usuario principal de producción
        admin = Usuario.query.filter_by(username="uracoa2025.com").first()
        if not admin:
            admin = Usuario(
                username="uracoa2025.com",
                email="uracoa2025.com",
                nombre="Administrador",
                apellido="Principal",
                cedula="99999999",
                telefono="0000-000-0000",
                rol="admin",
                activo=True,
                fecha_registro=datetime.utcnow()
            )
            admin.set_password("Uracoa245@")
            db.session.add(admin)
            print("👤 Usuario de producción creado: uracoa2025.com / Uracoa245@")
        else:
            print("👤 Usuario de producción ya existe, omitiendo.")
        
        # Crear usuario médico de ejemplo
        medico = Usuario.query.filter_by(username="dr.santos").first()
        if not medico:
            medico = Usuario(
                username="dr.santos",
                email="santos@hospital-uracoa.com",
                nombre="Santos",
                apellido="Médico Principal",
                cedula="12345678",
                telefono="0424-123-4567",
                rol="medico",
                especialidad="Medicina General",
                codigo_profesional="MPPS-12345",
                activo=True,
                fecha_registro=datetime.utcnow()
            )
            medico.set_password("Santos123")
            db.session.add(medico)
            print("👨‍⚕️ Médico de ejemplo creado: dr.santos / Santos123")
        else:
            print("👨‍⚕️ Usuario médico ya existe, omitiendo.")
        
        # Crear recepcionista de ejemplo
        recepcionista = Usuario.query.filter_by(username="recepcion").first()
        if not recepcionista:
            recepcionista = Usuario(
                username="recepcion",
                email="recepcion@hospital-uracoa.com",
                nombre="María",
                apellido="Recepción",
                cedula="87654321",
                telefono="0414-765-4321",
                rol="recepcionista",
                activo=True,
                fecha_registro=datetime.utcnow()
            )
            recepcionista.set_password("Recepcion123")
            db.session.add(recepcionista)
            print("📝 Recepcionista creada: recepcion / Recepcion123")
        else:
            print("📝 Usuario recepcionista ya existe, omitiendo.")
        
        # Guardar todos los cambios
        try:
            db.session.commit()
            print("\n" + "="*60)
            print("✅ Seed completado correctamente para Hospital Tipo 1 Uracoa")
            print("="*60)
            print("\n🔐 CREDENCIALES DE ACCESO:")
            print("-" * 60)
            print("👨‍💼 ADMINISTRADOR:")
            print("   Usuario: uracoa2025.com")
            print("   Password: Uracoa245@")
            print("-" * 60)
            print("👨‍⚕️ MÉDICO:")
            print("   Usuario: dr.santos")
            print("   Password: Santos123")
            print("-" * 60)
            print("📝 RECEPCIONISTA:")
            print("   Usuario: recepcion")
            print("   Password: Recepcion123")
            print("-" * 60)
            print("\n🌐 Accede al sistema en: http://localhost:5000")
            print("="*60)
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al crear los datos: {str(e)}")


def create_sample_data():
    """Crear datos de ejemplo adicionales"""
    app = create_app('development')
    
    with app.app_context():
        print("\n📋 Creando usuarios adicionales de ejemplo...")
        
        usuarios_ejemplo = [
            {
                'username': 'dr.perez',
                'email': 'perez@hospital-uracoa.com',
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'cedula': '11111111',
                'telefono': '0424-111-1111',
                'rol': 'medico',
                'especialidad': 'Cardiología',
                'codigo_profesional': 'MPPS-11111'
            },
            {
                'username': 'enf.garcia',
                'email': 'garcia@hospital-uracoa.com',
                'nombre': 'María',
                'apellido': 'García',
                'cedula': '22222222',
                'telefono': '0414-222-2222',
                'rol': 'enfermera'
            },
            {
                'username': 'farm.lopez',
                'email': 'lopez@hospital-uracoa.com',
                'nombre': 'Ana',
                'apellido': 'López',
                'cedula': '33333333',
                'telefono': '0426-333-3333',
                'rol': 'farmacia'
            }
        ]
        
        for datos in usuarios_ejemplo:
            usuario = Usuario.query.filter_by(username=datos['username']).first()
            if not usuario:
                usuario = Usuario(**datos)
                usuario.set_password('Demo123')
                usuario.activo = True
                usuario.fecha_registro = datetime.utcnow()
                db.session.add(usuario)
                print(f"✅ Usuario creado: {datos['username']} / Demo123")
        
        db.session.commit()
        print("\n✅ Datos de ejemplo creados exitosamente\n")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏥 Sistema SaaS - Hospital Tipo 1 Uracoa")
    print("   J&S Software Inteligentes")
    print("="*60 + "\n")
    
    # Crear usuarios de producción
    init_production_users()
    
    # Preguntar si crear datos de ejemplo adicionales
    print("\n")
    respuesta = input("¿Deseas crear usuarios adicionales de ejemplo? (s/n): ").strip().lower()
    if respuesta == 's':
        create_sample_data()
    
    print("\n" + "="*60)
    print("✅ Inicialización completada")
    print("="*60)
    print("\n🚀 Para ejecutar el sistema: python run.py")
    print("🌐 URL: http://localhost:5000")
    print("="*60 + "\n")
