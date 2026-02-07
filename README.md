# 🏭 Factory Manager Pro

Aplicación de Gestión de Fábrica desarrollada con **Kivy 2.3.0** y **KivyMD 2.0.1** (Material Design 3). Optimizada para Android 13+ (API 33) con soporte completo para generación de PDFs y compartir archivos.

## ✨ Características

- 📊 **Dashboard de Producción** en tiempo real
- 📦 **Gestión de Inventario** con alertas de stock bajo
- 📋 **Órdenes de Trabajo** con seguimiento de estado
- 📄 **Generación de Reportes PDF** con fpdf2
- 📤 **Compartir Reportes** nativo en Android
- 💾 **Base de Datos SQLite3** persistente
- 🎨 **Material Design 3** con temas dinámicos
- 📱 **Optimizado para Android 13+**

## 🛠️ Stack Tecnológico

| Componente | Versión |
|------------|---------|
| Python | 3.10+ |
| Kivy | 2.3.0 |
| KivyMD | 2.0.1 (master) |
| materialyoucolor | 0.1.5+ |
| fpdf2 | 2.7.0+ |
| plyer | 2.1.0+ |
| pillow | 10.0.0+ |

## 📁 Estructura del Proyecto

```
factory_management_app/
├── main.py                 # Punto de entrada principal
├── factory.kv             # Definiciones de UI (KV Language)
├── buildozer.spec         # Configuración de Buildozer
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
├── modules/              # Módulos de la aplicación
│   ├── __init__.py
│   ├── database.py       # Gestor de SQLite3
│   └── pdf_generator.py  # Generador de PDFs
├── assets/               # Imágenes y recursos
├── reports/              # Reportes PDF generados
└── .github/
    └── workflows/
        └── build-android.yml  # CI/CD GitHub Actions
```

## 🚀 Instalación Local

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd factory_management_app
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias

```bash
pip install --upgrade pip setuptools wheel
pip install kivy==2.3.0
pip install https://github.com/kivymd/KivyMD/archive/master.zip
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
python main.py
```

## 🤖 Compilación para Android

### Requisitos Previos

- Ubuntu 20.04+ (recomendado) o Docker
- Python 3.10+
- Java JDK 17
- Android SDK/NDK (se descarga automáticamente)

### Compilación Local

```bash
# Instalar buildozer
pip install buildozer cython==0.29.36

# Compilar APK debug
buildozer android debug

# Compilar AAB release
buildozer android release
```

### Compilación con GitHub Actions

El proyecto incluye un workflow de GitHub Actions que compila automáticamente:

1. **Push a main/develop**: Compila APK debug
2. **Tag v\***: Compila AAB release y crea GitHub Release
3. **Manual**: Puede ejecutarse manualmente desde Actions

#### Configurar GitHub Actions

1. Ve a **Settings > Secrets and variables > Actions**
2. Añade los siguientes secrets (opcional para firma):
   - `KEYSTORE_BASE64`: Keystore en base64
   - `KEYSTORE_PASSWORD`: Contraseña del keystore
   - `KEY_ALIAS`: Alias de la clave
   - `KEY_PASSWORD`: Contraseña de la clave

## 📋 Configuración de Buildozer

El archivo `buildozer.spec` está optimizado para:

- **Android API 33** (Android 13+)
- **Arquitecturas**: arm64-v8a, armeabi-v7a
- **Orientación**: Landscape forzado
- **Permisos**: Almacenamiento completo para Android 13+

### Permisos Configurados

```
INTERET
WRITE_EXTERNAL_STORAGE
READ_EXTERNAL_STORAGE
MANAGE_EXTERNAL_STORAGE (Android 11+)
ACCESS_NETWORK_STATE
WAKE_LOCK
VIBRATE
```

## 🎨 Componentes de UI (KivyMD 2.0.1)

La aplicación utiliza la sintaxis moderna de Material Design 3:

```python
# Botones
MDButton(
    MDButtonText(text="ACEPTAR"),
    style="filled"
)

# Campos de texto
MDTextField(
    MDTextFieldHintText(text="Usuario"),
    mode="outlined"
)

# Listas
MDListItem(
    MDListItemLeadingIcon(icon="factory"),
    MDListItemHeadlineText(text="Línea A"),
    MDListItemSupportingText(text="Producción: 150 unidades")
)

# Tarjetas
MDCard(
    style="elevated",
    radius=[dp(12),]
)
```

## 💾 Base de Datos

La aplicación usa SQLite3 con las siguientes tablas:

- **users**: Usuarios y autenticación
- **production_lines**: Líneas de producción
- **products**: Catálogo de productos
- **production_records**: Registros de producción
- **inventory**: Inventario actual
- **inventory_movements**: Movimientos de inventario
- **work_orders**: Órdenes de trabajo
- **maintenance_records**: Registros de mantenimiento

### Ubicación de la BD

- **Android**: `/data/data/com.factorymanager.app/files/databases/`
- **Desktop**: `./factory_manager.db`

## 📄 Generación de PDFs

### Tipos de Reportes

1. **Reporte de Producción**: Resumen diario con estadísticas
2. **Reporte de Inventario**: Stock actual con alertas
3. **Reporte de Órdenes**: Estado de órdenes de trabajo
4. **Reporte Personalizado**: Configurable

### Compartir en Android

```python
from modules.pdf_generator import PDFGenerator

pdf = PDFGenerator()
data = {...}
filepath = pdf.generate_production_report(data)
pdf.share_pdf(filepath)
```

## 🔐 Autenticación

Usuario por defecto:
- **Usuario**: `admin`
- **Contraseña**: `admin`

> ⚠️ En producción, implementar hash seguro para contraseñas.

## 🐛 Solución de Problemas

### Error: `ModuleNotFoundError: materialyoucolor`

```bash
pip install materialyoucolor
```

### Error: `No module named 'android'`

Este error solo ocurre en desktop. La aplicación detecta automáticamente la plataforma.

### Error de permisos en Android 13+

La aplicación solicita permisos en tiempo de ejecución:
- `MANAGE_EXTERNAL_STORAGE` para acceso completo
- `READ/WRITE_EXTERNAL_STORAGE` para compatibilidad

### Mutex Error en Android

Si ocurre error de mutex:
1. Asegúrate de usar `kivy==2.3.0`
2. No uses `multiprocessing` en Android
3. Usa `Clock.schedule_once()` para operaciones asíncronas

## 📊 GitHub Actions - Workflows

### Build Android

```yaml
Trigger:
  - Push a main/develop
  - Tag v*
  - Manual

Jobs:
  - build-android: Compila APK/AAB
  - code-quality: Linting con flake8/black
  - test: Pruebas básicas
  - notify: Notificación de resultado
```

### Artefactos

- **Debug APK**: `factory-manager-debug-apk`
- **Release AAB**: `factory-manager-release-aab`

## 📝 Changelog

### v2.0.1
- ✅ KivyMD 2.0.1 con Material Design 3
- ✅ Soporte Android 13+ (API 33)
- ✅ Permisos modernos de almacenamiento
- ✅ Generación de PDFs con fpdf2
- ✅ Compartir nativo en Android
- ✅ Base de datos SQLite3 persistente

## 📄 Licencia

MIT License - Ver LICENSE para detalles.

## 👨‍💻 Autor

Desarrollado por el equipo de Factory Manager Pro.

---

<p align="center">
  <b>🏭 Factory Manager Pro - Gestión Inteligente de Producción</b>
</p>
