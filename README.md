# AdrianDevelopment Bot 🤖

Bot de Discord para gestionar contactos, pagos, entregas y soporte automatizado.  
Incluye paneles interactivos con botones y menús desplegables para que los usuarios puedan contactar fácilmente con el administrador.

---

## ✨ Características

- 📩 **Panel de contacto** con botón interactivo.
- 💳 **Soporte de pagos** vía **PayPal** y **Litecoin**.
- 📬 **Mensajes entre usuario y dueño** (tickets privados).
- 📦 **Sistema de entregas** con asignación de roles a clientes.
- 📊 **Estadísticas de usuarios** (compras y dinero gastado).
- 🔄 **Auto-refresh de paneles** cada 40 segundos (se borran y se regeneran).
- 🛠️ **Comandos Slash** con `/`.

---

## 📋 Requisitos

- Python **3.11+**
- Librerías:
  - `discord.py` (versión 2.3+ con soporte a `discord.ui`)
  - `PyYAML`
  - `asyncio`
  - Tu propia clase `database` (ya incluida en `core/database.py`)

---

## ⚙️ Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/adrianez28/AdrianDevelopment-Discord-Bot.git
   cd AdrianDevelopment-Discord-Bot
