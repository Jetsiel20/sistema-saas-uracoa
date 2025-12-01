from saas import create_app
from saas.extensions import db
from saas.models import Usuario
from datetime import datetime

app = create_app('production')

with app.app_context():
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
        print("✅ Usuario admin creado")
    else:
        admin.set_password("Uracoa245@")
        admin.activo = True
        admin.rol = "admin"
        print("✅ Usuario admin actualizado")
    db.session.commit()
    print("\nUsuario: uracoa2025.com\nPassword: Uracoa245@\nRol: admin\n")
