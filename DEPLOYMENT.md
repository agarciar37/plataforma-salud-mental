# Plataforma de Salud Mental

## Estructura del proyecto

```text
plataforma-salud-mental/
├── backend/      # API FastAPI, MongoDB, autenticación y servicios de IA
├── frontend/     # Interfaz web Next.js
└── vercel.json   # Configuración de despliegue
```

## Requisitos previos

Antes de ejecutar el proyecto, instala en el ordenador:

- [Git](https://git-scm.com/)
- [Python](https://www.python.org/) 3.11 o superior
- [Node.js](https://nodejs.org/) con npm
- MongoDB local o una base de datos en MongoDB Atlas
- Una API key de OpenAI para probar respuestas reales de IA

## 1. Descargar el proyecto

Clona el repositorio:

```bash
git clone <[URL_DEL_REPOSITORIO](https://github.com/agarciar37/plataforma-salud-mental)>
cd plataforma-salud-mental
```

Si se entrega como archivo ZIP, descomprímelo y abre una terminal dentro de la carpeta `plataforma-salud-mental`.

## 2. Configurar el backend

Entra en la carpeta del backend:

```bash
cd backend
```

Crea un entorno virtual:

```bash
python -m venv .venv
```

Activa el entorno virtual.

En macOS/Linux:

```bash
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

Crea un archivo llamado `.env` dentro de la carpeta `backend/` con este contenido:

```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=plataforma_salud_mental
JWT_SECRET=una_clave_secreta_larga_para_pruebas
OPENAI_API_KEY=sk-tu_clave_de_openai
```

### Configuración de MongoDB

Si usas MongoDB local, asegúrate de que el servicio está iniciado y deja:

```env
MONGO_URI=mongodb://localhost:27017
```

Si usas MongoDB Atlas, sustituye `MONGO_URI` por la cadena de conexión de Atlas, por ejemplo:

```env
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
```

### Configuración de OpenAI

Para probar respuestas reales de IA, configura una API key válida:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

Si no quieres usar crédito de OpenAI durante una prueba rápida, puedes poner un valor de prueba. La aplicación arrancará, aunque las respuestas generadas por IA no funcionarán correctamente.

## 3. Arrancar el backend

Desde la carpeta `backend/`, ejecuta:

```bash
uvicorn app.main:app --reload --port 8000
```

Comprueba que la API funciona abriendo en el navegador:

```text
http://localhost:8000/
```

Deberías ver una respuesta parecida a:

```json
{
  "message": "API del TFG funcionando correctamente"
}
```

También puedes comprobar la conexión con MongoDB en:

```text
http://localhost:8000/auth/db-test
```

Si MongoDB está bien configurado, devolverá un mensaje de conexión correcta y la lista de colecciones.

## 4. Configurar el frontend

Abre una segunda terminal desde la raíz del proyecto y entra en la carpeta del frontend:

```bash
cd frontend
```

Instala las dependencias:

```bash
npm install
```

Crea un archivo llamado `.env.local` dentro de `frontend/` con este contenido:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Esta variable indica al frontend dónde está ejecutándose la API del backend.

## 5. Arrancar el frontend

Desde la carpeta `frontend/`, ejecuta:

```bash
npm run dev
```

Abre la aplicación en el navegador:

```text
http://localhost:3000
```

## 6. Flujo de prueba recomendado

Para comprobar el proyecto completo, sigue estos pasos:

1. Arranca MongoDB.
2. Arranca el backend en `http://localhost:8000`.
3. Arranca el frontend en `http://localhost:3000`.
4. Abre `http://localhost:3000` en el navegador.
5. Registra un usuario nuevo.
6. Inicia sesión con ese usuario.
7. Entra en el chat y envía varios mensajes, por ejemplo:
   - `Hoy me siento bastante estresado por los estudios.`
   - `Me siento algo triste y necesito organizar mis ideas.`
   - `Hoy he tenido un buen día y me siento contento.`
8. Comprueba que el sistema responde, detecta emociones y muestra recomendaciones.
9. Accede al perfil/resumen si está disponible en la interfaz para revisar estadísticas del historial emocional.

## 7. Probar la API manualmente

FastAPI genera documentación automática. Con el backend arrancado, abre:

```text
http://localhost:8000/docs
```

Desde ahí se pueden probar rutas como:

- `GET /`
- `GET /auth/ping`
- `GET /auth/db-test`
- `POST /auth/register`
- `POST /auth/login`
- `POST /chat/message`
- `GET /chat/history`
- `GET /chat/summary`

Para las rutas de chat hace falta autenticarse primero y enviar el token como Bearer token.

## 8. Ejecutar pruebas automáticas

Desde la raíz del proyecto, ejecuta las pruebas del backend:

```bash
python -m pytest backend/tests -q
```

Para comprobar el frontend:

```bash
cd frontend
npm run lint
npm run build
```

## 9. Comandos resumidos

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

En Windows, sustituye la activación del entorno virtual por:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 10. Solución de problemas frecuentes

### El frontend no conecta con el backend

Comprueba que existe `frontend/.env.local` y contiene:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Después reinicia el servidor del frontend.

### Error de CORS

Asegúrate de abrir el frontend en:

```text
http://localhost:3000
```

El backend está preparado para aceptar peticiones desde ese origen durante el desarrollo local.

### Error conectando con MongoDB

Comprueba que:

- MongoDB está arrancado.
- `MONGO_URI` es correcto.
- El archivo `backend/.env` existe.
- La ruta `http://localhost:8000/auth/db-test` responde correctamente.

### Error con OpenAI

Comprueba que `OPENAI_API_KEY` existe en `backend/.env` y que la clave es válida.

### El puerto ya está ocupado

Si `8000` o `3000` están ocupados, cierra el proceso que los usa o cambia el puerto. Si cambias el puerto del backend, actualiza también `NEXT_PUBLIC_API_URL` en `frontend/.env.local`.
