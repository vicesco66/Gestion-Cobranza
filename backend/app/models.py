from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class RolUsuario(str, Enum):
    administrador = "Administrador"
    supervisor = "Supervisor"
    gestor = "Gestor"


class EstadoFactura(str, Enum):
    pendiente = "Pendiente"
    por_vencer = "Por vencer"
    vencida = "Vencida"
    en_gestion = "En gestion"
    pagada = "Pagada"
    castigada = "Castigada"


class TipoGestion(str, Enum):
    llamada = "Llamada"
    whatsapp = "WhatsApp"
    correo = "Correo"
    visita = "Visita"
    carta = "Carta"
    reunion = "Reunion"


class EstadoPromesa(str, Enum):
    pendiente = "Pendiente"
    cumplida = "Cumplida"
    incumplida = "Incumplida"


class CanalNotificacion(str, Enum):
    whatsapp = "WhatsApp"
    correo = "Correo"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    correo: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(40), default=RolUsuario.gestor.value)

    gestiones: Mapped[list["Gestion"]] = relationship(back_populates="usuario")


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(180), index=True)
    razon_social: Mapped[str | None] = mapped_column(String(180), nullable=True)
    ruc: Mapped[str] = mapped_column(String(30), index=True)
    direccion: Mapped[str | None] = mapped_column(String(240), nullable=True)
    ciudad: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provincia: Mapped[str | None] = mapped_column(String(80), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(40), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(40), nullable=True)
    correo: Mapped[str | None] = mapped_column(String(160), nullable=True)

    facturas: Mapped[list["Factura"]] = relationship(back_populates="cliente", cascade="all, delete-orphan")
    gestiones: Mapped[list["Gestion"]] = relationship(back_populates="cliente", cascade="all, delete-orphan")
    contactos: Mapped[list["Contacto"]] = relationship(back_populates="cliente", cascade="all, delete-orphan")
    notificaciones: Mapped[list["Notificacion"]] = relationship(back_populates="cliente", cascade="all, delete-orphan")


class Contacto(Base):
    __tablename__ = "contactos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    nombre: Mapped[str] = mapped_column(String(120))
    cargo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(40), nullable=True)
    correo: Mapped[str | None] = mapped_column(String(160), nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    cliente: Mapped[Cliente] = relationship(back_populates="contactos")


class Factura(Base):
    __tablename__ = "facturas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    numero: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    fecha_emision: Mapped[date] = mapped_column(Date)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, index=True)
    valor: Mapped[float] = mapped_column(Float)
    saldo: Mapped[float] = mapped_column(Float)
    estado: Mapped[str] = mapped_column(String(40), default=EstadoFactura.pendiente.value)

    cliente: Mapped[Cliente] = relationship(back_populates="facturas")
    promesas: Mapped[list["PromesaPago"]] = relationship(back_populates="factura", cascade="all, delete-orphan")


class Gestion(Base):
    __tablename__ = "gestiones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    tipo: Mapped[str] = mapped_column(String(40))
    observacion: Mapped[str] = mapped_column(Text)
    resultado: Mapped[str | None] = mapped_column(String(160), nullable=True)

    cliente: Mapped[Cliente] = relationship(back_populates="gestiones")
    usuario: Mapped[Usuario] = relationship(back_populates="gestiones")


class PromesaPago(Base):
    __tablename__ = "promesas_pago"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    factura_id: Mapped[int] = mapped_column(ForeignKey("facturas.id"))
    fecha_compromiso: Mapped[date] = mapped_column(Date)
    monto: Mapped[float] = mapped_column(Float)
    estado: Mapped[str] = mapped_column(String(40), default=EstadoPromesa.pendiente.value)

    factura: Mapped[Factura] = relationship(back_populates="promesas")


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    canal: Mapped[str] = mapped_column(String(40))
    mensaje: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(40), default="Pendiente")

    cliente: Mapped[Cliente] = relationship(back_populates="notificaciones")
