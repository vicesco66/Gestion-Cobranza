from datetime import date, datetime

from pydantic import BaseModel, EmailStr


class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    rol: str = "Gestor"


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioOut(UsuarioBase):
    id: int

    class Config:
        from_attributes = True


class ClienteBase(BaseModel):
    codigo: str
    nombre: str
    razon_social: str | None = None
    ruc: str
    direccion: str | None = None
    ciudad: str | None = None
    provincia: str | None = None
    telefono: str | None = None
    whatsapp: str | None = None
    correo: EmailStr | None = None


class ClienteCreate(ClienteBase):
    pass


class ClienteOut(ClienteBase):
    id: int

    class Config:
        from_attributes = True


class FacturaBase(BaseModel):
    cliente_id: int
    numero: str
    fecha_emision: date
    fecha_vencimiento: date
    valor: float
    saldo: float
    estado: str | None = None


class FacturaCreate(FacturaBase):
    pass


class FacturaOut(FacturaBase):
    id: int
    estado: str
    cliente: ClienteOut | None = None

    class Config:
        from_attributes = True


class GestionBase(BaseModel):
    cliente_id: int
    usuario_id: int
    tipo: str
    observacion: str
    resultado: str | None = None


class GestionCreate(GestionBase):
    pass


class GestionOut(GestionBase):
    id: int
    fecha: datetime

    class Config:
        from_attributes = True


class PromesaPagoBase(BaseModel):
    factura_id: int
    fecha_compromiso: date
    monto: float
    estado: str = "Pendiente"


class PromesaPagoCreate(PromesaPagoBase):
    pass


class PromesaPagoOut(PromesaPagoBase):
    id: int

    class Config:
        from_attributes = True


class NotificacionBase(BaseModel):
    cliente_id: int
    canal: str
    mensaje: str
    estado: str = "Pendiente"


class NotificacionCreate(NotificacionBase):
    pass


class NotificacionOut(NotificacionBase):
    id: int
    fecha: datetime

    class Config:
        from_attributes = True
