"""
#╔══════════════════════════════════════════════════════════════════╗
# ║          LATAM ASSISTANT - BOT OFICIAL DE DISCORD               ║
#║          Versión 1.0 | Desarrollado para LATAM Airlines RP      ║
#╚══════════════════════════════════════════════════════════════════╝

Funciones:
  - /menu            → Menú principal interactivo
  - /vuelo           → Estado de vuelo en tiempo real
  - /reserva         → Buscar reserva por código
  - /checkin         → Check-in online y tarjeta de embarque
  - /servicios       → Servicios a bordo (nacional/internacional)
  - /misvuelos       → Listar todos los vuelos de una reserva
  - /aeropuerto      → Info de aeropuerto por código IATA
  - /operaciones     → Estado operacional de LATAM
  - /roles           → Asignación de roles de tripulación
  - /ayuda           → Guía de comandos
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import string
import datetime
import asyncio
import os
from typing import Optional

# ══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DEL BOT
# ══════════════════════════════════════════════════════════════

TOKEN = "TU_TOKEN_AQUI"          # <-- Reemplaza con tu token de Discord
GUILD_ID = None                   # <-- Pon tu Guild ID aquí para sync rápido (int) o None para global

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ══════════════════════════════════════════════════════════════
#  PALETA DE COLORES LATAM
# ══════════════════════════════════════════════════════════════

COLOR_LATAM_RED   = 0xE8002D    # Rojo LATAM
COLOR_LATAM_BLUE  = 0x1B1464    # Azul oscuro LATAM
COLOR_SUCCESS     = 0x00B050    # Verde éxito
COLOR_WARNING     = 0xFFAA00    # Naranja advertencia
COLOR_DANGER      = 0xCC0000    # Rojo peligro
COLOR_INFO        = 0x4EABF0    # Azul información
COLOR_GREY        = 0x95A5A6    # Gris neutro

# ══════════════════════════════════════════════════════════════
#  BASE DE DATOS LOCAL (JSON simulado para RP)
# ══════════════════════════════════════════════════════════════

DB_FILE = "latam_db.json"

DEFAULT_DB = {
    "reservas": {
        "ABC123": {
            "pasajero": "Juan Pérez",
            "vuelo": "LA457",
            "asiento": "12A",
            "clase": "Economy",
            "equipaje": "1 maleta 23kg",
            "fecha": "14/06/2026",
            "origen": "SCL",
            "destino": "LIM",
            "checkin_done": False,
            "boarding_group": None,
            "gate": None
        },
        "DEF456": {
            "pasajero": "María González",
            "vuelo": "LA800",
            "asiento": "5C",
            "clase": "Business",
            "equipaje": "2 maletas 23kg",
            "fecha": "15/06/2026",
            "origen": "SCL",
            "destino": "MIA",
            "checkin_done": False,
            "boarding_group": None,
            "gate": None
        },
        "GHI789": {
            "pasajero": "Carlos Rodríguez",
            "vuelo": "LA231",
            "asiento": "22B",
            "clase": "Economy",
            "equipaje": "Solo equipaje de mano",
            "fecha": "14/06/2026",
            "origen": "SCL",
            "destino": "PMC",
            "checkin_done": False,
            "boarding_group": None,
            "gate": None
        },
        "JKL012": {
            "pasajero": "Ana Torres",
            "vuelo": "LA502",
            "asiento": "8D",
            "clase": "Economy",
            "equipaje": "1 maleta 23kg",
            "fecha": "16/06/2026",
            "origen": "LIM",
            "destino": "GRU",
            "checkin_done": False,
            "boarding_group": None,
            "gate": None
        }
    },
    "vuelos": {
        "LA457": {
            "numero": "LA457",
            "origen": "SCL",
            "destino": "LIM",
            "salida": "14:30",
            "llegada": "16:10",
            "estado": "En horario",
            "puerta": "15",
            "terminal": "2",
            "aeronave": "Boeing 767-300",
            "tipo": "internacional",
            "fecha": "14/06/2026",
            "embarque": "14:00",
            "fin_embarque": "14:20"
        },
        "LA800": {
            "numero": "LA800",
            "origen": "SCL",
            "destino": "MIA",
            "salida": "22:15",
            "llegada": "06:45+1",
            "estado": "En horario",
            "puerta": "22",
            "terminal": "2",
            "aeronave": "Boeing 787-9 Dreamliner",
            "tipo": "internacional",
            "fecha": "15/06/2026",
            "embarque": "21:30",
            "fin_embarque": "22:00"
        },
        "LA231": {
            "numero": "LA231",
            "origen": "SCL",
            "destino": "PMC",
            "salida": "08:45",
            "llegada": "10:20",
            "estado": "Demorado",
            "demora": "20 min",
            "puerta": "7",
            "terminal": "1",
            "aeronave": "Airbus A320",
            "tipo": "nacional",
            "fecha": "14/06/2026",
            "embarque": "08:15",
            "fin_embarque": "08:35"
        },
        "LA502": {
            "numero": "LA502",
            "origen": "LIM",
            "destino": "GRU",
            "salida": "11:30",
            "llegada": "17:45",
            "estado": "En horario",
            "puerta": "B4",
            "terminal": "Internacional",
            "aeronave": "Boeing 767-300",
            "tipo": "internacional",
            "fecha": "16/06/2026",
            "embarque": "11:00",
            "fin_embarque": "11:20"
        },
        "LA100": {
            "numero": "LA100",
            "origen": "SCL",
            "destino": "JFK",
            "salida": "01:10",
            "llegada": "12:30",
            "estado": "En horario",
            "puerta": "24",
            "terminal": "2",
            "aeronave": "Boeing 787-9 Dreamliner",
            "tipo": "internacional",
            "fecha": "14/06/2026",
            "embarque": "00:30",
            "fin_embarque": "01:00"
        },
        "LA521": {
            "numero": "LA521",
            "origen": "SCL",
            "destino": "ARI",
            "salida": "07:05",
            "llegada": "08:30",
            "estado": "Cancelado",
            "puerta": "-",
            "terminal": "1",
            "aeronave": "Airbus A319",
            "tipo": "nacional",
            "fecha": "14/06/2026",
            "embarque": "-",
            "fin_embarque": "-"
        },
        "LA380": {
            "numero": "LA380",
            "origen": "GRU",
            "destino": "SCL",
            "salida": "13:00",
            "llegada": "17:30",
            "estado": "En horario",
            "puerta": "C12",
            "terminal": "Internacional",
            "aeronave": "Airbus A320neo",
            "tipo": "internacional",
            "fecha": "14/06/2026",
            "embarque": "12:30",
            "fin_embarque": "12:50"
        }
    },
    "aeropuertos": {
        "SCL": {
            "nombre": "Aeropuerto Internacional Arturo Merino Benítez",
            "ciudad": "Santiago",
            "pais": "Chile",
            "iata": "SCL",
            "icao": "SCEL",
            "lat": "-33.3928",
            "lon": "-70.7856",
            "terminales": ["Terminal 1 (Nacional)", "Terminal 2 (Internacional)"],
            "hub": True,
            "web": "www.nuevopudahuel.cl"
        },
        "LIM": {
            "nombre": "Aeropuerto Internacional Jorge Chávez",
            "ciudad": "Lima",
            "pais": "Perú",
            "iata": "LIM",
            "icao": "SPJC",
            "lat": "-12.0219",
            "lon": "-77.1143",
            "terminales": ["Terminal Principal"],
            "hub": True,
            "web": "www.lap.com.pe"
        },
        "GRU": {
            "nombre": "Aeropuerto Internacional de Guarulhos",
            "ciudad": "São Paulo",
            "pais": "Brasil",
            "iata": "GRU",
            "icao": "SBGR",
            "lat": "-23.4356",
            "lon": "-46.4731",
            "terminales": ["Terminal 1", "Terminal 2", "Terminal 3"],
            "hub": True,
            "web": "www.gru.com.br"
        },
        "MIA": {
            "nombre": "Miami International Airport",
            "ciudad": "Miami",
            "pais": "Estados Unidos",
            "iata": "MIA",
            "icao": "KMIA",
            "lat": "25.7959",
            "lon": "-80.2870",
            "terminales": ["North Terminal", "Central Terminal", "South Terminal"],
            "hub": False,
            "web": "www.miami-airport.com"
        },
        "JFK": {
            "nombre": "John F. Kennedy International Airport",
            "ciudad": "Nueva York",
            "pais": "Estados Unidos",
            "iata": "JFK",
            "icao": "KJFK",
            "lat": "40.6413",
            "lon": "-73.7781",
            "terminales": ["T1", "T2", "T4", "T5", "T7", "T8"],
            "hub": False,
            "web": "www.jfkairport.com"
        },
        "PMC": {
            "nombre": "Aeropuerto El Tepual",
            "ciudad": "Puerto Montt",
            "pais": "Chile",
            "iata": "PMC",
            "icao": "SCTE",
            "lat": "-41.4389",
            "lon": "-73.0940",
            "terminales": ["Terminal Único"],
            "hub": False,
            "web": "www.aeropuertopuertomontt.cl"
        },
        "ARI": {
            "nombre": "Aeropuerto Internacional Chacalluta",
            "ciudad": "Arica",
            "pais": "Chile",
            "iata": "ARI",
            "icao": "SCAR",
            "lat": "-18.3485",
            "lon": "-70.3386",
            "terminales": ["Terminal Único"],
            "hub": False,
            "web": "www.aeropuertoarearica.cl"
        },
        "IQQ": {
            "nombre": "Aeropuerto Diego Aracena",
            "ciudad": "Iquique",
            "pais": "Chile",
            "iata": "IQQ",
            "icao": "SCDA",
            "lat": "-20.5352",
            "lon": "-70.1813",
            "terminales": ["Terminal Único"],
            "hub": False,
            "web": "www.aeropuertoiquique.cl"
        },
        "CJC": {
            "nombre": "Aeropuerto El Loa",
            "ciudad": "Calama",
            "pais": "Chile",
            "iata": "CJC",
            "icao": "SCCF",
            "lat": "-22.4982",
            "lon": "-68.9036",
            "terminales": ["Terminal Único"],
            "hub": False,
            "web": ""
        },
        "ANF": {
            "nombre": "Aeropuerto Andrés Sabella Gálvez",
            "ciudad": "Antofagasta",
            "pais": "Chile",
            "iata": "ANF",
            "icao": "SCFA",
            "lat": "-23.4444",
            "lon": "-70.4451",
            "terminales": ["Terminal Único"],
            "hub": False,
            "web": ""
        },
        "BOG": {
            "nombre": "Aeropuerto Internacional El Dorado",
            "ciudad": "Bogotá",
            "pais": "Colombia",
            "iata": "BOG",
            "icao": "SKBO",
            "lat": "4.7016",
            "lon": "-74.1469",
            "terminales": ["Terminal 1", "Terminal 2 (Puente Aéreo)"],
            "hub": False,
            "web": "www.aerocivil.gov.co"
        },
        "EZE": {
            "nombre": "Aeropuerto Internacional Ministro Pistarini",
            "ciudad": "Buenos Aires",
            "pais": "Argentina",
            "iata": "EZE",
            "icao": "SAEZ",
            "lat": "-34.8222",
            "lon": "-58.5358",
            "terminales": ["Terminal A", "Terminal B", "Terminal C", "Terminal D", "Terminal E"],
            "hub": False,
            "web": "www.aa2000.com.ar"
        }
    },
    "operaciones": {
        "LATAM Chile": {"estado": "Normal", "color": "verde"},
        "LATAM Perú": {"estado": "Normal", "color": "verde"},
        "LATAM Brasil": {"estado": "Demoras menores", "color": "amarillo"},
        "LATAM Colombia": {"estado": "Normal", "color": "verde"},
        "LATAM Argentina": {"estado": "Normal", "color": "verde"},
        "LATAM Ecuador": {"estado": "Normal", "color": "verde"},
        "LATAM Cargo": {"estado": "Operaciones normales", "color": "verde"}
    }
}

# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE BASE DE DATOS
# ══════════════════════════════════════════════════════════════

def cargar_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DB, f, ensure_ascii=False, indent=2)
        return DEFAULT_DB.copy()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# ══════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════

def estado_emoji(estado: str) -> str:
    estados = {
        "En horario":      "🟢",
        "Demorado":        "🟡",
        "Cancelado":       "🔴",
        "Aterrizado":      "🛬",
        "En vuelo":        "✈️",
        "Embarcando":      "🚶",
        "Cerrado":         "🔒",
    }
    return estados.get(estado, "⚪")

def color_estado(estado: str) -> int:
    colores = {
        "En horario":  COLOR_SUCCESS,
        "Demorado":    COLOR_WARNING,
        "Cancelado":   COLOR_DANGER,
        "Aterrizado":  COLOR_INFO,
        "En vuelo":    COLOR_LATAM_BLUE,
        "Embarcando":  COLOR_SUCCESS,
    }
    return colores.get(estado, COLOR_GREY)

def generar_codigo_reserva() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def hora_actual() -> str:
    return datetime.datetime.now().strftime("%H:%M")

def fecha_actual() -> str:
    return datetime.datetime.now().strftime("%d/%m/%Y")

def timestamp_footer() -> str:
    return datetime.datetime.now().strftime("LATAM Assistant • %d/%m/%Y %H:%M UTC")

def nombre_pais_bandera(destino: str, db: dict) -> str:
    aeropuerto = db["aeropuertos"].get(destino, {})
    pais = aeropuerto.get("pais", "")
    banderas = {
        "Chile": "🇨🇱",
        "Perú": "🇵🇪",
        "Brasil": "🇧🇷",
        "Colombia": "🇨🇴",
        "Argentina": "🇦🇷",
        "Ecuador": "🇪🇨",
        "Estados Unidos": "🇺🇸",
        "Bolivia": "🇧🇴",
        "Paraguay": "🇵🇾",
        "Uruguay": "🇺🇾",
        "Venezuela": "🇻🇪",
        "México": "🇲🇽",
        "España": "🇪🇸",
    }
    bandera = banderas.get(pais, "🌍")
    return f"{bandera} {pais}" if pais else "🌍 Internacional"

def es_vuelo_nacional(vuelo_data: dict) -> bool:
    return vuelo_data.get("tipo", "nacional") == "nacional"

# ══════════════════════════════════════════════════════════════
#  EMBEDS REUTILIZABLES
# ══════════════════════════════════════════════════════════════

def embed_base(titulo: str, descripcion: str = "", color: int = COLOR_LATAM_BLUE) -> discord.Embed:
    embed = discord.Embed(title=titulo, description=descripcion, color=color)
    embed.set_footer(text=timestamp_footer())
    return embed

def embed_error(mensaje: str) -> discord.Embed:
    embed = discord.Embed(
        title="❌ Error del Sistema",
        description=f"```{mensaje}```",
        color=COLOR_DANGER
    )
    embed.set_footer(text=timestamp_footer())
    return embed

# ══════════════════════════════════════════════════════════════
#  VISTA: MENÚ PRINCIPAL
# ══════════════════════════════════════════════════════════════

class MenuPrincipalView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="✈️ Estado de Vuelo", style=discord.ButtonStyle.primary, row=0)
    async def estado_vuelo_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = VueloModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🎫 Buscar Reserva", style=discord.ButtonStyle.secondary, row=0)
    async def reserva_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ReservaModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="✅ Check-in", style=discord.ButtonStyle.success, row=0)
    async def checkin_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CheckinModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🍽️ Servicios a Bordo", style=discord.ButtonStyle.secondary, row=1)
    async def servicios_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ServiciosModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🛫 Mis Vuelos", style=discord.ButtonStyle.secondary, row=1)
    async def misvuelos_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MisVuelosModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="📍 Aeropuertos", style=discord.ButtonStyle.secondary, row=1)
    async def aeropuerto_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AeropuertoModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="📢 Operaciones", style=discord.ButtonStyle.danger, row=2)
    async def operaciones_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await mostrar_operaciones(interaction)

    @discord.ui.button(label="❓ Ayuda", style=discord.ButtonStyle.grey, row=2)
    async def ayuda_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await mostrar_ayuda(interaction)

# ══════════════════════════════════════════════════════════════
#  MODALES
# ══════════════════════════════════════════════════════════════

class VueloModal(discord.ui.Modal, title="🛫 Consultar Estado de Vuelo"):
    numero = discord.ui.TextInput(
        label="Número de Vuelo",
        placeholder="Ej: LA457, LA800, LA231...",
        min_length=3,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        await procesar_estado_vuelo(interaction, self.numero.value.upper().strip())


class ReservaModal(discord.ui.Modal, title="🎫 Buscar Reserva"):
    codigo = discord.ui.TextInput(
        label="Código de Reserva",
        placeholder="Ej: ABC123",
        min_length=5,
        max_length=8
    )

    async def on_submit(self, interaction: discord.Interaction):
        await procesar_reserva(interaction, self.codigo.value.upper().strip())


class CheckinModal(discord.ui.Modal, title="✅ Realizar Check-in"):
    codigo = discord.ui.TextInput(
        label="Código de Reserva",
        placeholder="Ej: ABC123",
        min_length=5,
        max_length=8
    )

    async def on_submit(self, interaction: discord.Interaction):
        await procesar_checkin(interaction, self.codigo.value.upper().strip())


class ServiciosModal(discord.ui.Modal, title="🍽️ Servicios a Bordo"):
    vuelo = discord.ui.TextInput(
        label="Número de Vuelo o Código de Reserva",
        placeholder="Ej: LA457 o ABC123",
        min_length=3,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        await procesar_servicios(interaction, self.vuelo.value.upper().strip())


class MisVuelosModal(discord.ui.Modal, title="🛫 Mis Vuelos"):
    codigo = discord.ui.TextInput(
        label="Código de Reserva",
        placeholder="Ej: ABC123",
        min_length=5,
        max_length=8
    )

    async def on_submit(self, interaction: discord.Interaction):
        await procesar_mis_vuelos(interaction, self.codigo.value.upper().strip())


class AeropuertoModal(discord.ui.Modal, title="📍 Información de Aeropuerto"):
    iata = discord.ui.TextInput(
        label="Código IATA del Aeropuerto",
        placeholder="Ej: SCL, LIM, GRU, MIA...",
        min_length=3,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        await procesar_aeropuerto(interaction, self.iata.value.upper().strip())

# ══════════════════════════════════════════════════════════════
#  VISTA: CONFIRMAR CHECK-IN
# ══════════════════════════════════════════════════════════════

class ConfirmarCheckinView(discord.ui.View):
    def __init__(self, codigo: str, vuelo_data: dict, reserva_data: dict):
        super().__init__(timeout=120)
        self.codigo = codigo
        self.vuelo_data = vuelo_data
        self.reserva_data = reserva_data

    @discord.ui.button(label="✅ Confirmar Check-in", style=discord.ButtonStyle.success)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        db = cargar_db()

        asiento = self.reserva_data.get("asiento", "")
        if not asiento:
            fila = random.randint(10, 35)
            col = random.choice(["A", "B", "C", "D", "E", "F"])
            asiento = f"{fila}{col}"

        grupo = random.randint(1, 5)
        puerta = self.vuelo_data.get("puerta", str(random.randint(1, 30)))
        hora_emb = self.vuelo_data.get("embarque", "Consultar pantallas")

        db["reservas"][self.codigo]["checkin_done"] = True
        db["reservas"][self.codigo]["boarding_group"] = grupo
        db["reservas"][self.codigo]["gate"] = puerta
        guardar_db(db)

        embed = discord.Embed(
            title="✅ CHECK-IN COMPLETADO",
            description=(
                f"```\n"
                f"══════════════════════════════════\n"
                f"   ✈  TARJETA DE EMBARQUE LATAM  ✈\n"
                f"══════════════════════════════════\n"
                f"  PASAJERO : {self.reserva_data['pasajero']}\n"
                f"  VUELO    : {self.reserva_data['vuelo']}\n"
                f"  RUTA     : {self.reserva_data['origen']} → {self.reserva_data['destino']}\n"
                f"  FECHA    : {self.reserva_data['fecha']}\n"
                f"  ASIENTO  : {asiento}     CLASE: {self.reserva_data['clase']}\n"
                f"  PUERTA   : {puerta}     GRUPO: {grupo}\n"
                f"  EMBARQUE : {hora_emb}\n"
                f"══════════════════════════════════\n"
                f"   [■■■■■■■■■■■ BOARDING PASS ■■]\n"
                f"══════════════════════════════════\n"
                f"```"
            ),
            color=COLOR_SUCCESS
        )
        embed.add_field(
            name="📌 Instrucciones",
            value=(
                f"• Preséntese en la puerta **{puerta}** con **30 min** de anticipación\n"
                f"• Embarque grupo **{grupo}** — {hora_emb}\n"
                f"• Tenga su identificación lista para revisión"
            ),
            inline=False
        )
        embed.add_field(
            name="🧳 Equipaje",
            value=self.reserva_data.get("equipaje", "Consultar con agente"),
            inline=True
        )
        embed.set_footer(text=timestamp_footer())

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.danger)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = embed_base("❌ Check-in Cancelado", "El proceso de check-in fue cancelado. Puede reiniciarlo cuando desee.", COLOR_GREY)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

# ══════════════════════════════════════════════════════════════
#  LÓGICA: ESTADO DE VUELO
# ══════════════════════════════════════════════════════════════

async def procesar_estado_vuelo(interaction: discord.Interaction, numero: str):
    await interaction.response.defer(ephemeral=False)
    db = cargar_db()

    vuelo = db["vuelos"].get(numero)
    if not vuelo:
        await interaction.followup.send(
            embed=embed_error(
                f"Vuelo '{numero}' no encontrado en el sistema.\n"
                f"Verifique el número e intente nuevamente.\n"
                f"Ejemplo: LA457, LA800, LA231"
            )
        )
        return

    emoji = estado_emoji(vuelo["estado"])
    color = color_estado(vuelo["estado"])
    tipo_ruta = "🌍 Internacional" if vuelo["tipo"] == "internacional" else "🇨🇱 Nacional"
    db_ap = db.get("aeropuertos", {})

    origen_nombre = db_ap.get(vuelo["origen"], {}).get("nombre", vuelo["origen"])
    destino_nombre = db_ap.get(vuelo["destino"], {}).get("nombre", vuelo["destino"])

    embed = discord.Embed(
        title=f"✈️ VUELO {vuelo['numero']} — {vuelo['origen']} → {vuelo['destino']}",
        description=f"{emoji} **Estado:** {vuelo['estado']}  |  {tipo_ruta}",
        color=color
    )

    embed.add_field(
        name="🛫 Origen",
        value=f"**{vuelo['origen']}** — {origen_nombre}\n🕒 Salida: **{vuelo['salida']}**",
        inline=True
    )
    embed.add_field(
        name="🛬 Destino",
        value=f"**{vuelo['destino']}** — {destino_nombre}\n🕒 Llegada: **{vuelo['llegada']}**",
        inline=True
    )
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.add_field(name="✈️ Aeronave", value=vuelo.get("aeronave", "—"), inline=True)
    embed.add_field(name="🚪 Puerta/Gate", value=f"**{vuelo.get('puerta', '—')}**", inline=True)
    embed.add_field(name="🏢 Terminal", value=vuelo.get("terminal", "—"), inline=True)

    embed.add_field(
        name="⏰ Horario de Embarque",
        value=(
            f"Apertura: **{vuelo.get('embarque', '—')}**\n"
            f"Cierre: **{vuelo.get('fin_embarque', '—')}**"
        ),
        inline=True
    )
    embed.add_field(name="📅 Fecha", value=vuelo.get("fecha", "—"), inline=True)

    if vuelo["estado"] == "Demorado":
        embed.add_field(
            name="⚠️ Demora",
            value=f"Retraso estimado: **{vuelo.get('demora', 'Por determinar')}**",
            inline=False
        )
    elif vuelo["estado"] == "Cancelado":
        embed.add_field(
            name="🔴 Vuelo Cancelado",
            value="Este vuelo ha sido cancelado. Contáctese con LATAM para reprogramar.",
            inline=False
        )

    embed.set_author(name="LATAM Airlines — Estado de Vuelo", icon_url="https://i.imgur.com/7kqQnV2.png")
    embed.set_footer(text=timestamp_footer())

    await interaction.followup.send(embed=embed)

# ══════════════════════════════════════════════════════════════
#  LÓGICA: BUSCAR RESERVA
# ══════════════════════════════════════════════════════════════

async def procesar_reserva(interaction: discord.Interaction, codigo: str):
    await interaction.response.defer(ephemeral=True)
    db = cargar_db()

    reserva = db["reservas"].get(codigo)
    if not reserva:
        await interaction.followup.send(
            embed=embed_error(
                f"Código de reserva '{codigo}' no encontrado.\n"
                f"Verifique el código e intente nuevamente.\n"
                f"Ejemplo: ABC123, DEF456"
            ),
            ephemeral=True
        )
        return

    vuelo = db["vuelos"].get(reserva["vuelo"], {})
    checkin_status = "✅ Completado" if reserva.get("checkin_done") else "⏳ Pendiente"
    tipo_ruta = "🌍 Internacional" if vuelo.get("tipo") == "internacional" else "🇨🇱 Nacional"

    embed = discord.Embed(
        title=f"🎫 RESERVA {codigo}",
        description=f"Información de la reserva para **{reserva['pasajero']}**",
        color=COLOR_LATAM_BLUE
    )

    embed.add_field(name="👤 Pasajero", value=reserva["pasajero"], inline=True)
    embed.add_field(name="🎫 Código", value=f"`{codigo}`", inline=True)
    embed.add_field(name="✅ Check-in", value=checkin_status, inline=True)

    embed.add_field(name="✈️ Vuelo", value=reserva["vuelo"], inline=True)
    embed.add_field(name="📅 Fecha", value=reserva["fecha"], inline=True)
    embed.add_field(name="🗺️ Tipo de Ruta", value=tipo_ruta, inline=True)

    embed.add_field(
        name="🛫 Ruta",
        value=f"**{reserva['origen']}** ─── ✈️ ─── **{reserva['destino']}**",
        inline=False
    )

    embed.add_field(name="💺 Asiento", value=reserva["asiento"], inline=True)
    embed.add_field(name="🪑 Clase", value=reserva["clase"], inline=True)
    embed.add_field(name="🧳 Equipaje", value=reserva["equipaje"], inline=True)

    if reserva.get("checkin_done"):
        embed.add_field(
            name="🚪 Información de Embarque",
            value=(
                f"Puerta: **{reserva.get('gate', 'Ver pantallas')}** | "
                f"Grupo: **{reserva.get('boarding_group', 'Ver tarjeta')}**"
            ),
            inline=False
        )

    if vuelo:
        embed.add_field(
            name="⏰ Horarios del Vuelo",
            value=f"Salida: **{vuelo.get('salida', '—')}** | Llegada: **{vuelo.get('llegada', '—')}**",
            inline=False
        )

    embed.set_author(name="LATAM Airlines — Sistema de Reservas")
    embed.set_footer(text=timestamp_footer())

    await interaction.followup.send(embed=embed, ephemeral=True)

# ══════════════════════════════════════════════════════════════
#  LÓGICA: CHECK-IN
# ══════════════════════════════════════════════════════════════

async def procesar_checkin(interaction: discord.Interaction, codigo: str):
    await interaction.response.defer(ephemeral=True)
    db = cargar_db()

    reserva = db["reservas"].get(codigo)
    if not reserva:
        await interaction.followup.send(
            embed=embed_error(f"Código '{codigo}' no encontrado. Verifique e intente de nuevo."),
            ephemeral=True
        )
        return

    if reserva.get("checkin_done"):
        embed = discord.Embed(
            title="ℹ️ Check-in Ya Realizado",
            description=(
                f"El pasajero **{reserva['pasajero']}** ya realizó check-in para el vuelo **{reserva['vuelo']}**.\n\n"
                f"**Asiento:** {reserva.get('asiento', '—')}\n"
                f"**Puerta:** {reserva.get('gate', 'Ver pantallas')}\n"
                f"**Grupo de embarque:** {reserva.get('boarding_group', '—')}"
            ),
            color=COLOR_INFO
        )
        embed.set_footer(text=timestamp_footer())
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    vuelo = db["vuelos"].get(reserva["vuelo"])
    if not vuelo:
        await interaction.followup.send(
            embed=embed_error("No se encontró información del vuelo asociado a esta reserva."),
            ephemeral=True
        )
        return

    # Verificar si el vuelo está cancelado
    if vuelo.get("estado") == "Cancelado":
        embed = discord.Embed(
            title="🔴 Check-in No Disponible",
            description=(
                f"El vuelo **{reserva['vuelo']}** fue **cancelado**.\n"
                f"Contáctese con LATAM para reprogramar su vuelo o solicitar reembolso."
            ),
            color=COLOR_DANGER
        )
        embed.set_footer(text=timestamp_footer())
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    # Confirmación previa
    embed = discord.Embed(
        title="✅ Confirmar Check-in Online",
        description=(
            f"Está a punto de realizar el check-in para:\n\n"
            f"**Pasajero:** {reserva['pasajero']}\n"
            f"**Vuelo:** {reserva['vuelo']}  |  {reserva['origen']} → {reserva['destino']}\n"
            f"**Fecha:** {reserva['fecha']}\n"
            f"**Clase:** {reserva['clase']}\n"
            f"**Equipaje:** {reserva['equipaje']}\n\n"
            f"El check-in online está disponible desde **48 horas antes** de la salida."
        ),
        color=COLOR_LATAM_BLUE
    )
    embed.set_footer(text=timestamp_footer())

    view = ConfirmarCheckinView(codigo, vuelo, reserva)
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

# ══════════════════════════════════════════════════════════════
#  LÓGICA: SERVICIOS A BORDO
# ══════════════════════════════════════════════════════════════

SERVICIOS_NACIONAL = {
    "🍪 Alimentación": [
        "Snack dulce o salado (según disponibilidad)",
        "Bebidas frías: agua, jugos, refrescos",
        "Bebidas calientes: café, té",
        "Servicio de bebidas a demanda"
    ],
    "🎭 Entretenimiento": [
        "Revista digital LATAM Magazine",
        "Entretenimiento móvil vía app (según aeronave)",
        "Conexión Wi-Fi disponible en algunos vuelos",
        "Música seleccionada"
    ],
    "💼 Comodidades": [
        "Almohada de cuello (tarifa Premium Economy)",
        "Manta ligera (tarifa Premium Economy)",
        "Espacio para equipaje de mano",
        "Reclinación de asiento estándar"
    ],
    "🧳 Equipaje": [
        "Equipaje de mano: 1 artículo + 1 accesorio personal",
        "Bodega: según tarifa contratada (consultar reserva)"
    ]
}

SERVICIOS_INTERNACIONAL = {
    "🍽️ Alimentación": [
        "Comida caliente completa (entrada, plato principal, postre)",
        "Selección de menú especial bajo solicitud anticipada",
        "Menú vegetariano, vegano, sin gluten disponibles",
        "Bebidas alcohólicas gratuitas (vino, cerveza, licores)",
        "Bebidas calientes y frías ilimitadas",
        "Servicio de snacks entre comidas (vuelos +5h)",
        "Segunda comida en vuelos de larga distancia (+8h)"
    ],
    "🎬 Entretenimiento": [
        "Sistema AVOD personal en cada asiento",
        "Más de 1,000 horas de contenido: películas, series, música",
        "Canales de música y podcasts",
        "Juegos interactivos",
        "Wi-Fi disponible (cargo adicional en algunos vuelos)",
        "Mapa de vuelo en tiempo real"
    ],
    "🛏️ Comodidades (Economy)": [
        "Almohada de viaje",
        "Manta suave",
        "Kit de higiene (vuelos +8h)",
        "Puerto USB en asiento",
        "Pantalla táctil personal"
    ],
    "👑 Comodidades (Premium Business)": [
        "Asiento cama completamente plano (180°)",
        "Amenity kit premium (crema, antifaz, calcetines)",
        "Menú exclusivo Business con vinos seleccionados",
        "Acceso a sala VIP (LATAM Pass Gold/Platinum)",
        "Embarque y desembarque prioritario",
        "Almohada y manta de alta densidad",
        "Conexión Wi-Fi incluida"
    ],
    "🛍️ Servicios Adicionales": [
        "Duty Free disponible en vuelos internacionales seleccionados",
        "Artículos de farmacia y primeros auxilios a bordo",
        "Asistencia para pasajeros con necesidades especiales",
        "Asistencia para menores no acompañados (UMNR)"
    ],
    "🧳 Equipaje": [
        "Equipaje de mano: 1 artículo (hasta 10kg)",
        "Bodega: incluida en la mayoría de tarifas internacionales",
        "Equipaje adicional disponible con cargo"
    ]
}

async def procesar_servicios(interaction: discord.Interaction, identificador: str):
    await interaction.response.defer(ephemeral=False)
    db = cargar_db()

    # Buscar por número de vuelo o código de reserva
    vuelo_data = db["vuelos"].get(identificador)
    if not vuelo_data:
        reserva = db["reservas"].get(identificador)
        if reserva:
            vuelo_data = db["vuelos"].get(reserva["vuelo"])

    if not vuelo_data:
        await interaction.followup.send(
            embed=embed_error(
                f"'{identificador}' no encontrado.\n"
                f"Ingrese un número de vuelo (Ej: LA457) o un código de reserva (Ej: ABC123)."
            )
        )
        return

    nacional = es_vuelo_nacional(vuelo_data)
    tipo_label = "🇨🇱 RUTA NACIONAL" if nacional else "🌍 RUTA INTERNACIONAL"
    servicios = SERVICIOS_NACIONAL if nacional else SERVICIOS_INTERNACIONAL
    color = COLOR_LATAM_BLUE if not nacional else COLOR_INFO

    embed = discord.Embed(
        title=f"🍽️ SERVICIOS A BORDO — {vuelo_data['numero']}",
        description=(
            f"**{tipo_label}**  |  {vuelo_data['origen']} ✈️ {vuelo_data['destino']}\n"
            f"*Aeronave: {vuelo_data.get('aeronave', 'Por confirmar')}*"
        ),
        color=color
    )

    for categoria, items in servicios.items():
        valor = "\n".join(f"• {item}" for item in items)
        embed.add_field(name=categoria, value=valor, inline=False)

    if nacional:
        embed.add_field(
            name="ℹ️ Nota Importante",
            value=(
                "Los servicios en rutas nacionales pueden variar según la duración del vuelo y "
                "la aeronave asignada. Para vuelos inferiores a 1 hora, el servicio puede ser reducido."
            ),
            inline=False
        )
    else:
        embed.add_field(
            name="ℹ️ Nota Importante",
            value=(
                "Los servicios varían según la clase contratada y la aeronave. "
                "Para consultas específicas, contáctese con LATAM al 600 526 2000."
            ),
            inline=False
        )

    embed.set_author(name="LATAM Airlines — Servicios a Bordo")
    embed.set_footer(text=timestamp_footer())

    await interaction.followup.send(embed=embed)

# ══════════════════════════════════════════════════════════════
#  LÓGICA: MIS VUELOS
# ══════════════════════════════════════════════════════════════

async def procesar_mis_vuelos(interaction: discord.Interaction, codigo: str):
    await interaction.response.defer(ephemeral=True)
    db = cargar_db()

    # Buscar todas las reservas asociadas al código (exacto o prefijo)
    reservas_encontradas = {}
    for key, val in db["reservas"].items():
        if key == codigo or val.get("pasajero", "").upper() == codigo:
            reservas_encontradas[key] = val

    if not reservas_encontradas:
        await interaction.followup.send(
            embed=embed_error(f"No se encontraron reservas para '{codigo}'."),
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"🛫 MIS VUELOS — Reserva {codigo}",
        description=f"Se encontraron **{len(reservas_encontradas)}** vuelo(s) asociado(s).",
        color=COLOR_LATAM_BLUE
    )

    for cod, reserva in reservas_encontradas.items():
        vuelo = db["vuelos"].get(reserva["vuelo"], {})
        estado = vuelo.get("estado", "—")
        emoji = estado_emoji(estado)
        checkin = "✅" if reserva.get("checkin_done") else "⏳"

        embed.add_field(
            name=f"✈️ {reserva['vuelo']} — Código: `{cod}`",
            value=(
                f"**Pasajero:** {reserva['pasajero']}\n"
                f"**Ruta:** {reserva['origen']} → {reserva['destino']}\n"
                f"**Fecha:** {reserva['fecha']}  |  **Asiento:** {reserva['asiento']}\n"
                f"**Clase:** {reserva['clase']}  |  **Check-in:** {checkin}\n"
                f"**Estado vuelo:** {emoji} {estado}"
            ),
            inline=False
        )

    embed.set_footer(text=timestamp_footer())
    await interaction.followup.send(embed=embed, ephemeral=True)

# ══════════════════════════════════════════════════════════════
#  LÓGICA: AEROPUERTO
# ══════════════════════════════════════════════════════════════

async def procesar_aeropuerto(interaction: discord.Interaction, iata: str):
    await interaction.response.defer(ephemeral=False)
    db = cargar_db()

    ap = db["aeropuertos"].get(iata)
    if not ap:
        await interaction.followup.send(
            embed=embed_error(
                f"Aeropuerto con código IATA '{iata}' no encontrado.\n"
                f"Ejemplos: SCL, LIM, GRU, MIA, JFK, BOG, EZE"
            )
        )
        return

    hub_text = "✅ Hub LATAM Principal" if ap.get("hub") else "📍 Aeropuerto de Servicio"
    terminales = "\n".join(f"• {t}" for t in ap.get("terminales", []))

    embed = discord.Embed(
        title=f"🏢 {ap['nombre']}",
        description=f"**{ap['ciudad']}**, {ap['pais']}  |  {hub_text}",
        color=COLOR_LATAM_BLUE
    )

    embed.add_field(name="🛫 Código IATA", value=f"`{ap['iata']}`", inline=True)
    embed.add_field(name="📡 Código ICAO", value=f"`{ap['icao']}`", inline=True)
    embed.add_field(name="🌐 Web", value=ap.get("web", "—") or "—", inline=True)

    embed.add_field(
        name="📍 Coordenadas",
        value=f"Lat: {ap['lat']}  |  Lon: {ap['lon']}",
        inline=False
    )

    embed.add_field(name="🏛️ Terminales", value=terminales or "—", inline=False)

    # Listar vuelos activos en ese aeropuerto
    vuelos_desde = [
        f"✈️ {v['numero']} → {v['destino']} | {v['salida']} | {estado_emoji(v['estado'])} {v['estado']}"
        for v in db["vuelos"].values()
        if v["origen"] == iata
    ]
    vuelos_hacia = [
        f"✈️ {v['numero']} ← {v['origen']} | {v['llegada']} | {estado_emoji(v['estado'])} {v['estado']}"
        for v in db["vuelos"].values()
        if v["destino"] == iata
    ]

    if vuelos_desde:
        embed.add_field(
            name=f"🛫 Salidas LATAM desde {iata}",
            value="\n".join(vuelos_desde[:5]),
            inline=False
        )
    if vuelos_hacia:
        embed.add_field(
            name=f"🛬 Llegadas LATAM a {iata}",
            value="\n".join(vuelos_hacia[:5]),
            inline=False
        )

    embed.set_author(name="LATAM Airlines — Información de Aeropuerto")
    embed.set_footer(text=timestamp_footer())

    await interaction.followup.send(embed=embed)

# ══════════════════════════════════════════════════════════════
#  LÓGICA: OPERACIONES
# ══════════════════════════════════════════════════════════════

async def mostrar_operaciones(interaction: discord.Interaction):
    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=False)

    db = cargar_db()
    ops = db.get("operaciones", DEFAULT_DB["operaciones"])

    embed = discord.Embed(
        title="📢 ESTADO OPERACIONAL LATAM",
        description=f"Resumen de operaciones al {fecha_actual()} {hora_actual()}",
        color=COLOR_LATAM_BLUE
    )

    for filial, datos in ops.items():
        color_ops = datos.get("color", "verde")
        emoji_op = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴"}.get(color_ops, "⚪")
        embed.add_field(
            name=f"{emoji_op} {filial}",
            value=datos["estado"],
            inline=True
        )

    embed.add_field(
        name="\u200b",
        value="*La información operacional puede cambiar sin previo aviso.*",
        inline=False
    )

    embed.set_author(name="LATAM Airlines — Centro de Operaciones")
    embed.set_footer(text=timestamp_footer())

    if interaction.response.is_done():
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send(embed=embed)

# ══════════════════════════════════════════════════════════════
#  LÓGICA: AYUDA
# ══════════════════════════════════════════════════════════════

async def mostrar_ayuda(interaction: discord.Interaction):
    embed = discord.Embed(
        title="❓ GUÍA DE COMANDOS — LATAM ASSISTANT",
        description="Todos los comandos disponibles para el bot oficial de LATAM Airlines.",
        color=COLOR_LATAM_BLUE
    )

    embed.add_field(
        name="📋 Comandos Slash",
        value=(
            "`/menu` — Abre el menú interactivo principal\n"
            "`/vuelo [número]` — Estado de un vuelo (Ej: `/vuelo LA457`)\n"
            "`/reserva [código]` — Consultar reserva (Ej: `/reserva ABC123`)\n"
            "`/checkin [código]` — Realizar check-in online\n"
            "`/servicios [vuelo/código]` — Servicios a bordo\n"
            "`/misvuelos [código]` — Listar vuelos de una reserva\n"
            "`/aeropuerto [IATA]` — Info de aeropuerto (Ej: `/aeropuerto SCL`)\n"
            "`/operaciones` — Estado operacional de LATAM\n"
            "`/roles` — Asignar rol de tripulación\n"
            "`/ayuda` — Mostrar esta guía"
        ),
        inline=False
    )

    embed.add_field(
        name="🎭 Roles Disponibles",
        value=(
            "👨‍✈️ Capitán  |  🧑‍✈️ Primer Oficial  |  🎧 Tripulante de Cabina\n"
            "🛠️ Mantenimiento  |  🎫 Agente de Check-in  |  🛄 Agente de Embarque\n"
            "🚚 Rampa  |  📡 Centro de Operaciones"
        ),
        inline=False
    )

    embed.add_field(
        name="💡 Tips",
        value=(
            "• El check-in está disponible 48h antes del vuelo\n"
            "• Los servicios varían según ruta (nacional/internacional)\n"
            "• Para soporte real: 600 526 2000 o latam.com"
        ),
        inline=False
    )

    embed.set_author(name="LATAM Airlines — Sistema de Asistencia")
    embed.set_footer(text=timestamp_footer())

    if not interaction.response.is_done():
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.followup.send(embed=embed, ephemeral=True)

# ══════════════════════════════════════════════════════════════
#  VISTA: ROLES DE TRIPULACIÓN
# ══════════════════════════════════════════════════════════════

ROLES_TRIPULACION = {
    "👨‍✈️ Capitán": "Capitán",
    "🧑‍✈️ Primer Oficial": "Primer Oficial",
    "🎧 Tripulante de Cabina": "Tripulante de Cabina",
    "🛠️ Mantenimiento": "Mantenimiento",
    "🎫 Agente de Check-in": "Agente de Check-in",
    "🛄 Agente de Embarque": "Agente de Embarque",
    "🚚 Rampa": "Rampa",
    "📡 Centro de Operaciones": "Centro de Operaciones",
}

class RolesSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=nombre, value=nombre, emoji=nombre.split()[0])
            for nombre in ROLES_TRIPULACION.values()
        ]
        super().__init__(
            placeholder="Selecciona tu rol en LATAM...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        rol_nombre = self.values[0]
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Este comando solo funciona en servidores.", ephemeral=True)
            return

        # Buscar o crear el rol
        rol = discord.utils.get(guild.roles, name=rol_nombre)
        if not rol:
            try:
                rol = await guild.create_role(
                    name=rol_nombre,
                    color=discord.Color.from_rgb(27, 20, 100),  # Azul LATAM
                    reason="Rol LATAM Assistant"
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ No tengo permisos para crear roles. Pide al admin que los cree manualmente.",
                    ephemeral=True
                )
                return

        try:
            await interaction.user.add_roles(rol)
            embed = discord.Embed(
                title="✅ Rol Asignado",
                description=f"Bienvenido/a a la tripulación, **{interaction.user.display_name}**.\nRol asignado: **{rol_nombre}**",
                color=COLOR_SUCCESS
            )
            embed.set_footer(text=timestamp_footer())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para asignar roles. Contacta al administrador.",
                ephemeral=True
            )


class RolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(RolesSelect())

# ══════════════════════════════════════════════════════════════
#  COMANDOS SLASH
# ══════════════════════════════════════════════════════════════

@tree.command(name="menu", description="✈️ Abre el menú principal de LATAM Assistant")
async def cmd_menu(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✈️ LATAM ASSISTANT",
        description=(
            "**Sistema Oficial de Gestión de Vuelos**\n\n"
            "Selecciona una opción del menú para continuar:\n\n"
            "🛫 **Estado de Vuelo** — Consulta horarios y estado en tiempo real\n"
            "🎫 **Buscar Reserva** — Accede a tu reserva con el código\n"
            "✅ **Check-in** — Realiza tu check-in online\n"
            "🍽️ **Servicios a Bordo** — Conoce los servicios de tu vuelo\n"
            "🛫 **Mis Vuelos** — Lista todos tus vuelos\n"
            "📍 **Aeropuertos** — Información de aeropuertos IATA\n"
            "📢 **Operaciones** — Estado general de la red LATAM\n"
            "❓ **Ayuda** — Guía de uso del bot"
        ),
        color=COLOR_LATAM_BLUE
    )
    embed.set_thumbnail(url="https://i.imgur.com/7kqQnV2.png")
    embed.set_author(name="LATAM Airlines — Sistema de Asistencia al Pasajero")
    embed.set_footer(text=f"LATAM Airlines • {fecha_actual()} {hora_actual()} • Bienvenido a bordo")
    await interaction.response.send_message(embed=embed, view=MenuPrincipalView())


@tree.command(name="vuelo", description="✈️ Consulta el estado de un vuelo LATAM")
@app_commands.describe(numero="Número de vuelo (Ej: LA457, LA800)")
async def cmd_vuelo(interaction: discord.Interaction, numero: str):
    await procesar_estado_vuelo(interaction, numero.upper().strip())


@tree.command(name="reserva", description="🎫 Busca tu reserva por código")
@app_commands.describe(codigo="Código de reserva de 6 caracteres (Ej: ABC123)")
async def cmd_reserva(interaction: discord.Interaction, codigo: str):
    await procesar_reserva(interaction, codigo.upper().strip())


@tree.command(name="checkin", description="✅ Realiza el check-in online para tu vuelo")
@app_commands.describe(codigo="Código de reserva (Ej: ABC123)")
async def cmd_checkin(interaction: discord.Interaction, codigo: str):
    await procesar_checkin(interaction, codigo.upper().strip())


@tree.command(name="servicios", description="🍽️ Conoce los servicios a bordo de tu vuelo")
@app_commands.describe(identificador="Número de vuelo o código de reserva (Ej: LA457 o ABC123)")
async def cmd_servicios(interaction: discord.Interaction, identificador: str):
    await procesar_servicios(interaction, identificador.upper().strip())


@tree.command(name="misvuelos", description="🛫 Lista todos los vuelos asociados a tu reserva")
@app_commands.describe(codigo="Código de reserva (Ej: ABC123)")
async def cmd_misvuelos(interaction: discord.Interaction, codigo: str):
    await procesar_mis_vuelos(interaction, codigo.upper().strip())


@tree.command(name="aeropuerto", description="📍 Información de un aeropuerto por código IATA")
@app_commands.describe(iata="Código IATA del aeropuerto (Ej: SCL, LIM, GRU)")
async def cmd_aeropuerto(interaction: discord.Interaction, iata: str):
    await procesar_aeropuerto(interaction, iata.upper().strip())


@tree.command(name="operaciones", description="📢 Estado operacional de la red LATAM Airlines")
async def cmd_operaciones(interaction: discord.Interaction):
    await interaction.response.defer()
    await mostrar_operaciones(interaction)


@tree.command(name="ayuda", description="❓ Guía de todos los comandos disponibles")
async def cmd_ayuda(interaction: discord.Interaction):
    await mostrar_ayuda(interaction)


@tree.command(name="roles", description="🎭 Selecciona tu rol en la tripulación LATAM")
async def cmd_roles(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎭 ROLES DE TRIPULACIÓN",
        description=(
            "Selecciona tu posición dentro de LATAM Airlines.\n"
            "El rol será asignado automáticamente a tu perfil en el servidor."
        ),
        color=COLOR_LATAM_BLUE
    )
    embed.add_field(
        name="Roles Disponibles",
        value=(
            "👨‍✈️ Capitán\n"
            "🧑‍✈️ Primer Oficial\n"
            "🎧 Tripulante de Cabina\n"
            "🛠️ Mantenimiento\n"
            "🎫 Agente de Check-in\n"
            "🛄 Agente de Embarque\n"
            "🚚 Rampa\n"
            "📡 Centro de Operaciones"
        ),
        inline=False
    )
    embed.set_footer(text=timestamp_footer())
    await interaction.response.send_message(embed=embed, view=RolesView(), ephemeral=True)


# ══════════════════════════════════════════════════════════════
#  COMANDOS DE ADMINISTRACIÓN
# ══════════════════════════════════════════════════════════════

@tree.command(name="agregarreserva", description="[ADMIN] Agrega una nueva reserva al sistema")
@app_commands.describe(
    codigo="Código de reserva único",
    pasajero="Nombre completo del pasajero",
    vuelo="Número de vuelo",
    asiento="Número de asiento",
    clase="Clase (Economy/Business)",
    origen="Código IATA origen",
    destino="Código IATA destino",
    fecha="Fecha del vuelo (dd/mm/yyyy)"
)
@app_commands.checks.has_permissions(administrator=True)
async def cmd_agregar_reserva(
    interaction: discord.Interaction,
    codigo: str,
    pasajero: str,
    vuelo: str,
    asiento: str,
    clase: str,
    origen: str,
    destino: str,
    fecha: str
):
    db = cargar_db()

    if codigo.upper() in db["reservas"]:
        await interaction.response.send_message(
            embed=embed_error(f"El código `{codigo.upper()}` ya existe en el sistema."),
            ephemeral=True
        )
        return

    db["reservas"][codigo.upper()] = {
        "pasajero": pasajero,
        "vuelo": vuelo.upper(),
        "asiento": asiento,
        "clase": clase,
        "equipaje": "Según tarifa",
        "fecha": fecha,
        "origen": origen.upper(),
        "destino": destino.upper(),
        "checkin_done": False,
        "boarding_group": None,
        "gate": None
    }
    guardar_db(db)

    embed = discord.Embed(
        title="✅ Reserva Creada",
        description=f"Reserva **{codigo.upper()}** agregada correctamente.",
        color=COLOR_SUCCESS
    )
    embed.add_field(name="Pasajero", value=pasajero, inline=True)
    embed.add_field(name="Vuelo", value=vuelo.upper(), inline=True)
    embed.add_field(name="Ruta", value=f"{origen.upper()} → {destino.upper()}", inline=True)
    embed.set_footer(text=timestamp_footer())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="agregarvuelo", description="[ADMIN] Agrega un vuelo al sistema")
@app_commands.describe(
    numero="Número de vuelo (Ej: LA999)",
    origen="Código IATA origen",
    destino="Código IATA destino",
    salida="Hora de salida (HH:MM)",
    llegada="Hora de llegada (HH:MM)",
    tipo="Tipo de vuelo: nacional o internacional",
    aeronave="Tipo de aeronave",
    puerta="Puerta de embarque"
)
@app_commands.checks.has_permissions(administrator=True)
async def cmd_agregar_vuelo(
    interaction: discord.Interaction,
    numero: str,
    origen: str,
    destino: str,
    salida: str,
    llegada: str,
    tipo: str,
    aeronave: str,
    puerta: str
):
    db = cargar_db()
    clave = numero.upper()

    db["vuelos"][clave] = {
        "numero": clave,
        "origen": origen.upper(),
        "destino": destino.upper(),
        "salida": salida,
        "llegada": llegada,
        "estado": "En horario",
        "puerta": puerta,
        "terminal": "1",
        "aeronave": aeronave,
        "tipo": tipo.lower(),
        "fecha": fecha_actual(),
        "embarque": salida[:2] + ":" + str(max(0, int(salida[3:]) - 30)).zfill(2),
        "fin_embarque": salida[:2] + ":" + str(max(0, int(salida[3:]) - 10)).zfill(2)
    }
    guardar_db(db)

    embed = discord.Embed(
        title="✅ Vuelo Creado",
        description=f"Vuelo **{clave}** ({origen.upper()} → {destino.upper()}) agregado correctamente.",
        color=COLOR_SUCCESS
    )
    embed.set_footer(text=timestamp_footer())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="actualizarvuelo", description="[ADMIN] Actualiza el estado de un vuelo")
@app_commands.describe(
    numero="Número de vuelo",
    estado="Nuevo estado del vuelo",
    puerta="Nueva puerta (opcional)"
)
@app_commands.checks.has_permissions(administrator=True)
async def cmd_actualizar_vuelo(
    interaction: discord.Interaction,
    numero: str,
    estado: str,
    puerta: Optional[str] = None
):
    db = cargar_db()
    clave = numero.upper()

    if clave not in db["vuelos"]:
        await interaction.response.send_message(
            embed=embed_error(f"Vuelo '{clave}' no encontrado."),
            ephemeral=True
        )
        return

    db["vuelos"][clave]["estado"] = estado
    if puerta:
        db["vuelos"][clave]["puerta"] = puerta
    guardar_db(db)

    emoji = estado_emoji(estado)
    embed = discord.Embed(
        title="✅ Vuelo Actualizado",
        description=f"Vuelo **{clave}** actualizado a: {emoji} **{estado}**",
        color=color_estado(estado)
    )
    embed.set_footer(text=timestamp_footer())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="resetecheckin", description="[ADMIN] Resetea el check-in de una reserva")
@app_commands.describe(codigo="Código de reserva")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_reset_checkin(interaction: discord.Interaction, codigo: str):
    db = cargar_db()
    clave = codigo.upper()

    if clave not in db["reservas"]:
        await interaction.response.send_message(
            embed=embed_error(f"Reserva '{clave}' no encontrada."),
            ephemeral=True
        )
        return

    db["reservas"][clave]["checkin_done"] = False
    db["reservas"][clave]["boarding_group"] = None
    db["reservas"][clave]["gate"] = None
    guardar_db(db)

    embed = discord.Embed(
        title="✅ Check-in Reseteado",
        description=f"El check-in de la reserva **{clave}** fue reseteado correctamente.",
        color=COLOR_SUCCESS
    )
    embed.set_footer(text=timestamp_footer())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="listvuelos", description="[ADMIN] Lista todos los vuelos del sistema")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_list_vuelos(interaction: discord.Interaction):
    db = cargar_db()
    embed = discord.Embed(
        title="📋 VUELOS EN EL SISTEMA",
        color=COLOR_LATAM_BLUE
    )

    for num, v in db["vuelos"].items():
        emoji = estado_emoji(v["estado"])
        embed.add_field(
            name=f"✈️ {num}",
            value=f"{v['origen']} → {v['destino']} | {v['salida']} | {emoji} {v['estado']}",
            inline=True
        )

    embed.set_footer(text=timestamp_footer())
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ══════════════════════════════════════════════════════════════
#  MANEJADORES DE ERRORES
# ══════════════════════════════════════════════════════════════

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            embed=embed_error("No tienes permisos para usar este comando."),
            ephemeral=True
        )
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            embed=embed_error(f"Comando en espera. Intenta en {error.retry_after:.1f} segundos."),
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            embed=embed_error(f"Error interno: {str(error)[:200]}"),
            ephemeral=True
        )

# ══════════════════════════════════════════════════════════════
#  EVENTOS DEL BOT
# ══════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    print("╔══════════════════════════════════════════════════════╗")
    print("║          LATAM ASSISTANT - BOT INICIADO             ║")
    print(f"║  Conectado como: {bot.user.name:<36}║")
    print(f"║  ID: {bot.user.id:<48}║")
    print(f"║  Servidores: {len(bot.guilds):<41}║")
    print("╚══════════════════════════════════════════════════════╝")

    # Sincronizar comandos
    if GUILD_ID:
        guild = discord.Object(id=GUILD_ID)
        tree.copy_global_to(guild=guild)
        synced = await tree.sync(guild=guild)
        print(f"✅ {len(synced)} comandos sincronizados en servidor {GUILD_ID}")
    else:
        synced = await tree.sync()
        print(f"✅ {len(synced)} comandos sincronizados globalmente")

    # Inicializar DB
    cargar_db()
    print("✅ Base de datos inicializada")

    # Status del bot
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="✈️ Vuelos LATAM | /menu"
        ),
        status=discord.Status.online
    )
    print("✅ Estado del bot configurado")
    print("═" * 54)


@bot.event
async def on_member_join(member: discord.Member):
    """Mensaje de bienvenida al unirse al servidor"""
    canal = discord.utils.get(member.guild.text_channels, name="general")
    if not canal:
        canal = member.guild.system_channel
    if not canal:
        return

    embed = discord.Embed(
        title="✈️ ¡Bienvenido a LATAM Airlines!",
        description=(
            f"**{member.mention}**, nos complace tenerte a bordo.\n\n"
            "Usa `/menu` para acceder a todos los servicios disponibles,\n"
            "o `/roles` para seleccionar tu posición en la tripulación.\n\n"
            "*Que tengas un excelente vuelo.*"
        ),
        color=COLOR_LATAM_BLUE
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"LATAM Airlines • {fecha_actual()}")
    await canal.send(embed=embed)

# ══════════════════════════════════════════════════════════════
#  INICIO DEL BOT
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    bot.run(TOKEN)
