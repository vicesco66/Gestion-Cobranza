from datetime import date

from .models import EstadoFactura, Factura


ALERT_DAYS = {
    -15: "Primer aviso",
    -7: "Segundo aviso",
    -3: "Tercer aviso",
    0: "Cuarto aviso",
    5: "Quinto aviso",
    15: "Sexto aviso",
}


def calcular_estado_factura(factura: Factura, hoy: date | None = None) -> str:
    hoy = hoy or date.today()
    if factura.saldo <= 0:
        return EstadoFactura.pagada.value
    if factura.estado in {EstadoFactura.en_gestion.value, EstadoFactura.castigada.value}:
        return factura.estado
    if factura.fecha_vencimiento < hoy:
        return EstadoFactura.vencida.value
    if (factura.fecha_vencimiento - hoy).days <= 15:
        return EstadoFactura.por_vencer.value
    return EstadoFactura.pendiente.value


def construir_mensaje_recordatorio(cliente_nombre: str, numero: str, valor: float, fecha: date) -> str:
    return (
        f"Estimado {cliente_nombre}\n\n"
        f"Le informamos que la factura No. {numero} por un valor de USD {valor:,.2f} "
        f"vence el dia {fecha.isoformat()}.\n\n"
        "Por favor ignore este mensaje si ya realizo el pago.\n\n"
        "Atentamente,\nDepartamento de Cobranza."
    )


def construir_mensaje_mora(cliente_nombre: str, numero: str, valor: float, fecha: date) -> str:
    return (
        f"Estimado {cliente_nombre}\n\n"
        f"Registramos pendiente de pago la factura No. {numero} por USD {valor:,.2f}, "
        f"vencida el {fecha.isoformat()}.\n\n"
        "Agradecemos regularizar su situacion o contactarnos para coordinar un acuerdo de pago."
    )
