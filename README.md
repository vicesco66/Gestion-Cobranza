# Sistema Integral de Gestion de Cobranza

Aplicacion web para administrar cartera de clientes, facturas por cobrar, gestiones, promesas de pago, alertas y reportes.

## Estructura

- `backend/`: API REST con FastAPI y SQLAlchemy.
- `frontend/`: interfaz React para dashboard, clientes, facturas, gestiones, promesas y notificaciones.

## Ejecucion local

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

La aplicacion queda disponible en `http://127.0.0.1:5173`.

## Alcance implementado

- Dashboard con indicadores de cartera.
- CRUD inicial de clientes, facturas, gestiones, promesas de pago y notificaciones.
- Calculo automatico de estado de factura segun vencimiento y saldo.
- Generacion de alertas de cobranza segun reglas del documento.
- Reporte de antiguedad de cartera.
- Plantillas base para mensajes de WhatsApp y mora.

## Siguientes pasos recomendados

- Conectar PostgreSQL en produccion.
- Agregar autenticacion JWT y control de roles.
- Integrar WhatsApp Business API.
- Integrar SMTP, Gmail Business o Microsoft 365.
- Agregar importacion Excel/CSV desde la interfaz.
