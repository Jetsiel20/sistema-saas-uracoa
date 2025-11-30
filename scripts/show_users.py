"""
Script para mostrar usuarios registrados en el sistema
J&S Software Inteligentes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from saas import create_app
from saas.models import Usuario

app = create_app()

with app.app_context():
    users = Usuario.query.all()
    
    print("\n" + "="*70)
    print(f"🔐 CREDENCIALES DEL SISTEMA - {len(users)} USUARIOS REGISTRADOS")
    print("="*70)
    
    for user in users:
        print(f"\n👤 {user.nombre_completo}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Rol: {user.rol.upper()}")
        print(f"   Cédula: {user.cedula}")
        print(f"   Teléfono: {user.telefono or 'N/A'}")
        print(f"   Estado: {'✅ ACTIVO' if user.activo else '❌ INACTIVO'}")
        if user.especialidad:
            print(f"   Especialidad: {user.especialidad}")
        print("-" * 70)
    
    print("\n📋 RESUMEN POR ROL:")
    print("-" * 70)
    roles = {}
    for user in users:
        roles[user.rol] = roles.get(user.rol, 0) + 1
    
    for rol, cantidad in sorted(roles.items()):
        print(f"   {rol.upper()}: {cantidad} usuario(s)")
    
    print("="*70)
    print("\n💡 CONTRASEÑAS POR DEFECTO:")
    print("-" * 70)
    print("   👨‍💼 ADMIN (uracoa2025.com): Uracoa245@")
    print("   👨‍⚕️ MÉDICO (dr.santos): Santos123")
    print("   📝 RECEPCIONISTA (recepcion): Recepcion123")
    print("   🎓 USUARIOS DEMO: Demo123")
    print("="*70 + "\n")
