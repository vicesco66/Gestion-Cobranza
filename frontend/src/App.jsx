import { useEffect, useState } from "react";
import { Bell, ClipboardList, FileText, HandCoins, LayoutDashboard, MessageCircle, Users } from "lucide-react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = "http://127.0.0.1:8000";

const tabs = [
  ["dashboard", "Dashboard", LayoutDashboard],
  ["clientes", "Clientes", Users],
  ["facturas", "Facturas", FileText],
  ["gestiones", "Gestiones", ClipboardList],
  ["promesas", "Promesas", HandCoins],
  ["notificaciones", "Alertas", Bell],
];

function money(value) {
  return new Intl.NumberFormat("es-EC", { style: "currency", currency: "USD" }).format(value || 0);
}

async function api(path, options) {
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function App() {
  const [tab, setTab] = useState("dashboard");
  const [data, setData] = useState({ clientes: [], facturas: [], gestiones: [], promesas: [], notificaciones: [], dashboard: {}, antiguedad: {} });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function refresh() {
    setLoading(true);
    setError("");
    try {
      const [clientes, facturas, gestiones, promesas, notificaciones, dashboard, antiguedad] = await Promise.all([
        api("/clientes"),
        api("/facturas"),
        api("/gestiones"),
        api("/promesas"),
        api("/notificaciones"),
        api("/reportes/dashboard"),
        api("/reportes/antiguedad"),
      ]);
      setData({ clientes, facturas, gestiones, promesas, notificaciones, dashboard, antiguedad });
    } catch (err) {
      setError("No se pudo conectar con la API. Inicia el backend en http://127.0.0.1:8000.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <MessageCircle size={24} />
          <div>
            <strong>SIGC</strong>
            <span>Gestion de cobranza</span>
          </div>
        </div>
        <nav>
          {tabs.map(([id, label, Icon]) => (
            <button className={tab === id ? "active" : ""} key={id} onClick={() => setTab(id)}>
              <Icon size={18} />
              {label}
            </button>
          ))}
        </nav>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p>Plataforma centralizada</p>
            <h1>{tabs.find(([id]) => id === tab)?.[1]}</h1>
          </div>
          <button className="primary" onClick={refresh} disabled={loading}>
            Actualizar
          </button>
        </header>

        {error && <div className="alert">{error}</div>}
        {tab === "dashboard" && <Dashboard data={data} />}
        {tab === "clientes" && <Clientes clientes={data.clientes} onSaved={refresh} />}
        {tab === "facturas" && <Facturas clientes={data.clientes} facturas={data.facturas} onSaved={refresh} />}
        {tab === "gestiones" && <Gestiones clientes={data.clientes} gestiones={data.gestiones} onSaved={refresh} />}
        {tab === "promesas" && <Promesas facturas={data.facturas} promesas={data.promesas} onSaved={refresh} />}
        {tab === "notificaciones" && <Notificaciones notificaciones={data.notificaciones} onSaved={refresh} />}
      </section>
    </main>
  );
}

function Dashboard({ data }) {
  const stats = [
    ["Total cartera", data.dashboard.total_cartera],
    ["Cartera vencida", data.dashboard.cartera_vencida],
    ["Cartera por vencer", data.dashboard.cartera_por_vencer],
    ["Pagos recibidos", data.dashboard.pagos_recibidos],
    ["Clientes morosos", data.dashboard.clientes_morosos, "count"],
    ["Alertas pendientes", data.dashboard.alertas_pendientes, "count"],
  ];
  return (
    <>
      <section className="stats">
        {stats.map(([label, value, type]) => (
          <article className="metric" key={label}>
            <span>{label}</span>
            <strong>{type === "count" ? value || 0 : money(value)}</strong>
          </article>
        ))}
      </section>
      <section className="panel">
        <h2>Antiguedad de cartera</h2>
        <div className="bars">
          {Object.entries(data.antiguedad).map(([label, value]) => (
            <div className="bar-row" key={label}>
              <span>{label}</span>
              <div><i style={{ width: `${Math.min((value / 10000) * 100, 100)}%` }} /></div>
              <b>{money(value)}</b>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

function Clientes({ clientes, onSaved }) {
  const [form, setForm] = useState({ codigo: "", nombre: "", ruc: "", whatsapp: "", correo: "", telefono: "", ciudad: "" });
  async function submit(event) {
    event.preventDefault();
    await api("/clientes", { method: "POST", body: JSON.stringify(form) });
    setForm({ codigo: "", nombre: "", ruc: "", whatsapp: "", correo: "", telefono: "", ciudad: "" });
    onSaved();
  }
  return <Crud title="Nuevo cliente" form={form} setForm={setForm} onSubmit={submit} fields={["codigo", "nombre", "ruc", "whatsapp", "correo", "telefono", "ciudad"]} rows={clientes} columns={["codigo", "nombre", "ruc", "whatsapp", "correo"]} />;
}

function Facturas({ clientes, facturas, onSaved }) {
  const [form, setForm] = useState({ cliente_id: "", numero: "", fecha_emision: "", fecha_vencimiento: "", valor: "", saldo: "" });
  async function submit(event) {
    event.preventDefault();
    await api("/facturas", { method: "POST", body: JSON.stringify({ ...form, cliente_id: Number(form.cliente_id), valor: Number(form.valor), saldo: Number(form.saldo) }) });
    setForm({ cliente_id: "", numero: "", fecha_emision: "", fecha_vencimiento: "", valor: "", saldo: "" });
    onSaved();
  }
  return (
    <section className="grid-two">
      <FormPanel title="Nueva factura" form={form} setForm={setForm} onSubmit={submit} fields={["cliente_id", "numero", "fecha_emision", "fecha_vencimiento", "valor", "saldo"]} clientes={clientes} />
      <Table rows={facturas} columns={["numero", "estado", "fecha_vencimiento", "valor", "saldo"]} />
    </section>
  );
}

function Gestiones({ clientes, gestiones, onSaved }) {
  const [form, setForm] = useState({ cliente_id: "", usuario_id: "1", tipo: "Llamada", observacion: "", resultado: "" });
  async function submit(event) {
    event.preventDefault();
    await ensureDefaultUser();
    await api("/gestiones", { method: "POST", body: JSON.stringify({ ...form, cliente_id: Number(form.cliente_id), usuario_id: Number(form.usuario_id) }) });
    setForm({ cliente_id: "", usuario_id: "1", tipo: "Llamada", observacion: "", resultado: "" });
    onSaved();
  }
  return (
    <section className="grid-two">
      <FormPanel title="Registrar gestion" form={form} setForm={setForm} onSubmit={submit} fields={["cliente_id", "tipo", "observacion", "resultado"]} clientes={clientes} />
      <Table rows={gestiones} columns={["fecha", "tipo", "observacion", "resultado"]} />
    </section>
  );
}

function Promesas({ facturas, promesas, onSaved }) {
  const [form, setForm] = useState({ factura_id: "", fecha_compromiso: "", monto: "", estado: "Pendiente" });
  async function submit(event) {
    event.preventDefault();
    await api("/promesas", { method: "POST", body: JSON.stringify({ ...form, factura_id: Number(form.factura_id), monto: Number(form.monto) }) });
    setForm({ factura_id: "", fecha_compromiso: "", monto: "", estado: "Pendiente" });
    onSaved();
  }
  return (
    <section className="grid-two">
      <FormPanel title="Nueva promesa" form={form} setForm={setForm} onSubmit={submit} fields={["factura_id", "fecha_compromiso", "monto", "estado"]} facturas={facturas} />
      <Table rows={promesas} columns={["factura_id", "fecha_compromiso", "monto", "estado"]} />
    </section>
  );
}

function Notificaciones({ notificaciones, onSaved }) {
  async function generar() {
    await api("/notificaciones/generar-alertas", { method: "POST" });
    onSaved();
  }
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Alertas automaticas</h2>
        <button className="primary" onClick={generar}>Generar alertas</button>
      </div>
      <Table rows={notificaciones} columns={["fecha", "canal", "estado", "mensaje"]} />
    </section>
  );
}

function Crud({ title, form, setForm, onSubmit, fields, rows, columns }) {
  return (
    <section className="grid-two">
      <FormPanel title={title} form={form} setForm={setForm} onSubmit={onSubmit} fields={fields} />
      <Table rows={rows} columns={columns} />
    </section>
  );
}

function FormPanel({ title, form, setForm, onSubmit, fields, clientes = [], facturas = [] }) {
  return (
    <form className="panel form" onSubmit={onSubmit}>
      <h2>{title}</h2>
      {fields.map((field) => {
        if (field === "cliente_id") {
          return <Select key={field} field={field} value={form[field]} onChange={setForm} options={clientes.map((c) => [c.id, c.nombre])} />;
        }
        if (field === "factura_id") {
          return <Select key={field} field={field} value={form[field]} onChange={setForm} options={facturas.map((f) => [f.id, f.numero])} />;
        }
        const type = field.includes("fecha") ? "date" : ["valor", "saldo", "monto"].includes(field) ? "number" : "text";
        return <input key={field} type={type} placeholder={label(field)} value={form[field]} required={["codigo", "nombre", "ruc", "numero"].includes(field)} onChange={(e) => setForm({ ...form, [field]: e.target.value })} />;
      })}
      <button className="primary">Guardar</button>
    </form>
  );
}

function Select({ field, value, onChange, options }) {
  return (
    <select value={value} required onChange={(e) => onChange((prev) => ({ ...prev, [field]: e.target.value }))}>
      <option value="">{label(field)}</option>
      {options.map(([id, text]) => <option value={id} key={id}>{text}</option>)}
    </select>
  );
}

function Table({ rows, columns }) {
  return (
    <section className="panel table-wrap">
      <table>
        <thead>
          <tr>{columns.map((column) => <th key={column}>{label(column)}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              {columns.map((column) => <td key={column}>{formatCell(row[column])}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
      {!rows.length && <p className="empty">Sin registros todavia.</p>}
    </section>
  );
}

function label(value) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatCell(value) {
  if (typeof value === "number") return value > 100 ? money(value) : value;
  return String(value ?? "");
}

async function ensureDefaultUser() {
  const users = await api("/usuarios");
  if (!users.length) {
    await api("/usuarios", { method: "POST", body: JSON.stringify({ nombre: "Administrador", correo: "admin@sigc.local", password: "admin", rol: "Administrador" }) });
  }
}

createRoot(document.getElementById("root")).render(<App />);
