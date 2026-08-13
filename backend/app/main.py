from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .database import Base, engine, get_db
from .models import Cliente, Factura, Gestion, Notificacion, PromesaPago, Usuario
from .schemas import (
    ClienteCreate,
    ClienteOut,
    FacturaCreate,
    FacturaOut,
    GestionCreate,
    GestionOut,
    NotificacionCreate,
    NotificacionOut,
    PromesaPagoCreate,
    PromesaPagoOut,
    UsuarioCreate,
    UsuarioOut,
)
from .services import ALERT_DAYS, calcular_estado_factura, construir_mensaje_mora, construir_mensaje_recordatorio

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SIGC API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/usuarios", response_model=UsuarioOut)
def crear_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = Usuario(**payload.model_dump())
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@app.get("/usuarios", response_model=list[UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).order_by(Usuario.nombre).all()


@app.post("/clientes", response_model=ClienteOut)
def crear_cliente(payload: ClienteCreate, db: Session = Depends(get_db)):
    cliente = Cliente(**payload.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@app.get("/clientes", response_model=list[ClienteOut])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).order_by(Cliente.nombre).all()


@app.get("/clientes/{cliente_id}", response_model=ClienteOut)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@app.post("/facturas", response_model=FacturaOut)
def crear_factura(payload: FacturaCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    factura = Factura(**data)
    factura.estado = payload.estado or calcular_estado_factura(factura)
    db.add(factura)
    db.commit()
    db.refresh(factura)
    return factura


@app.get("/facturas", response_model=list[FacturaOut])
def listar_facturas(db: Session = Depends(get_db)):
    facturas = db.query(Factura).options(joinedload(Factura.cliente)).order_by(Factura.fecha_vencimiento).all()
    for factura in facturas:
        nuevo_estado = calcular_estado_factura(factura)
        if factura.estado != nuevo_estado:
            factura.estado = nuevo_estado
    db.commit()
    return facturas


@app.post("/gestiones", response_model=GestionOut)
def crear_gestion(payload: GestionCreate, db: Session = Depends(get_db)):
    gestion = Gestion(**payload.model_dump())
    db.add(gestion)
    db.commit()
    db.refresh(gestion)
    return gestion


@app.get("/gestiones", response_model=list[GestionOut])
def listar_gestiones(db: Session = Depends(get_db)):
    return db.query(Gestion).order_by(Gestion.fecha.desc()).all()


@app.post("/promesas", response_model=PromesaPagoOut)
def crear_promesa(payload: PromesaPagoCreate, db: Session = Depends(get_db)):
    promesa = PromesaPago(**payload.model_dump())
    db.add(promesa)
    db.commit()
    db.refresh(promesa)
    return promesa


@app.get("/promesas", response_model=list[PromesaPagoOut])
def listar_promesas(db: Session = Depends(get_db)):
    return db.query(PromesaPago).order_by(PromesaPago.fecha_compromiso).all()


@app.post("/notificaciones", response_model=NotificacionOut)
def crear_notificacion(payload: NotificacionCreate, db: Session = Depends(get_db)):
    notificacion = Notificacion(**payload.model_dump())
    db.add(notificacion)
    db.commit()
    db.refresh(notificacion)
    return notificacion


@app.get("/notificaciones", response_model=list[NotificacionOut])
def listar_notificaciones(db: Session = Depends(get_db)):
    return db.query(Notificacion).order_by(Notificacion.fecha.desc()).all()


@app.post("/notificaciones/generar-alertas", response_model=list[NotificacionOut])
def generar_alertas(db: Session = Depends(get_db)):
    hoy = date.today()
    creadas: list[Notificacion] = []
    facturas = db.query(Factura).options(joinedload(Factura.cliente)).filter(Factura.saldo > 0).all()
    for factura in facturas:
        dias = (hoy - factura.fecha_vencimiento).days
        if dias not in ALERT_DAYS:
            continue
        mensaje = (
            construir_mensaje_mora(factura.cliente.nombre, factura.numero, factura.saldo, factura.fecha_vencimiento)
            if dias > 0
            else construir_mensaje_recordatorio(factura.cliente.nombre, factura.numero, factura.saldo, factura.fecha_vencimiento)
        )
        notificacion = Notificacion(cliente_id=factura.cliente_id, canal="WhatsApp", mensaje=mensaje, estado="Pendiente")
        db.add(notificacion)
        creadas.append(notificacion)
    db.commit()
    for item in creadas:
        db.refresh(item)
    return creadas


@app.get("/reportes/dashboard")
def dashboard(db: Session = Depends(get_db)):
    hoy = date.today()
    total_cartera = db.query(func.coalesce(func.sum(Factura.saldo), 0)).scalar()
    vencida = db.query(func.coalesce(func.sum(Factura.saldo), 0)).filter(Factura.saldo > 0, Factura.fecha_vencimiento < hoy).scalar()
    por_vencer = db.query(func.coalesce(func.sum(Factura.saldo), 0)).filter(Factura.saldo > 0, Factura.fecha_vencimiento >= hoy).scalar()
    clientes_morosos = db.query(func.count(func.distinct(Factura.cliente_id))).filter(Factura.saldo > 0, Factura.fecha_vencimiento < hoy).scalar()
    alertas_pendientes = db.query(func.count(Notificacion.id)).filter(Notificacion.estado == "Pendiente").scalar()
    pagos_recibidos = db.query(func.coalesce(func.sum(Factura.valor - Factura.saldo), 0)).scalar()
    return {
        "total_cartera": total_cartera,
        "cartera_vencida": vencida,
        "cartera_por_vencer": por_vencer,
        "pagos_recibidos": pagos_recibidos,
        "clientes_morosos": clientes_morosos,
        "alertas_pendientes": alertas_pendientes,
    }


@app.get("/reportes/antiguedad")
def antiguedad(db: Session = Depends(get_db)):
    hoy = date.today()
    buckets = {"1 a 30 dias": 0, "31 a 60 dias": 0, "61 a 90 dias": 0, "Mas de 90 dias": 0}
    facturas = db.query(Factura).filter(Factura.saldo > 0, Factura.fecha_vencimiento < hoy).all()
    for factura in facturas:
        dias = (hoy - factura.fecha_vencimiento).days
        if dias <= 30:
            buckets["1 a 30 dias"] += factura.saldo
        elif dias <= 60:
            buckets["31 a 60 dias"] += factura.saldo
        elif dias <= 90:
            buckets["61 a 90 dias"] += factura.saldo
        else:
            buckets["Mas de 90 dias"] += factura.saldo
    return buckets
