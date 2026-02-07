# 🚀 Guía de Despliegue - Factory Manager Pro

Esta guía explica cómo compilar y desplegar la aplicación Factory Manager Pro para Android usando Buildozer y GitHub Actions.

## 📋 Tabla de Contenidos

1. [Despliegue con GitHub Actions (Recomendado)](#despliegue-con-github-actions)
2. [Compilación Local](#compilación-local)
3. [Solución de Problemas](#solución-de-problemas)
4. [Configuración Avanzada](#configuración-avanzada)

---

## Despliegue con GitHub Actions

Este es el método recomendado ya que automatiza todo el proceso de compilación.

### Configuración Inicial

1. **Sube el código a GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <tu-repo-github>
   git push -u origin main
   ```

2. **Verifica que el workflow esté activo**:
   - Ve a la pestaña **Actions** en tu repositorio de GitHub
   - El workflow "Build Android APK/AAB" debería aparecer

### Compilación Automática

#### Opción A: Compilar APK Debug (Desarrollo)

Cada vez que hagas push a `main` o `develop`, se compilará automáticamente un APK debug.

```bash
git add .
git commit -m "Nueva funcionalidad"
git push origin main
```

El APK estará disponible en:
- **Actions** → **Build Android APK/AAB** → **Artifacts** → `factory-manager-debug-apk`

#### Opción B: Compilar AAB Release (Producción)

Para crear un AAB para Google Play Store:

```bash
git tag -a v1.0.0 -m "Versión 1.0.0"
git push origin v1.0.0
```

El AAB se creará automáticamente y se publicará como **GitHub Release**.

#### Opción C: Compilación Manual

1. Ve a **Actions** → **Build Android APK/AAB**
2. Click en **Run workflow**
3. Selecciona el tipo de build: `debug` o `release`
4. Click en **Run workflow**

### Configurar Firma de Release (Opcional)

Para publicar en Google Play Store, necesitas firmar el AAB:

1. **Crear keystore** (una sola vez):
   ```bash
   keytool -genkey -v -keystore factory-manager.keystore -alias factorymanager -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Convertir a base64**:
   ```bash
   base64 factory-manager.keystore | pbcopy  # Mac
   # o
   base64 factory-manager.keystore -w 0  # Linux
   ```

3. **Añadir secrets a GitHub**:
   - Ve a **Settings** → **Secrets and variables** → **Actions**
   - Añade:
     - `KEYSTORE_BASE64`: Contenido del keystore en base64
     - `KEYSTORE_PASSWORD`: Contraseña del keystore
     - `KEY_ALIAS`: Alias de la clave
     - `KEY_PASSWORD`: Contraseña de la clave

4. **Actualizar el workflow** (`.github/workflows/build-android.yml`):
   Añade el paso de firma después de compilar:
   ```yaml
   - name: Sign AAB
     uses: r0adkll/sign-android-release@v1
     with:
       releaseDirectory: bin
       signingKeyBase64: ${{ secrets.KEYSTORE_BASE64 }}
       alias: ${{ secrets.KEY_ALIAS }}
       keyStorePassword: ${{ secrets.KEYSTORE_PASSWORD }}
       keyPassword: ${{ secrets.KEY_PASSWORD }}
   ```

---

## Compilación Local

### Requisitos

- Ubuntu 20.04+ (recomendado) o Docker
- Python 3.10+
- Java JDK 17
- 8GB+ RAM
- 20GB+ espacio libre

### Instalación de Dependencias

```bash
# Actualizar sistema
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libgstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    libsqlite3-dev \
    libffi-dev \
    libssl-dev \
    autoconf \
    automake \
    libtool \
    pkg-config \
    zip \
    unzip

# Instalar Java 17
sudo apt-get install -y openjdk-17-jdk

# Configurar Java
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$PATH:$JAVA_HOME/bin
```

### Instalar Buildozer

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip setuptools wheel
pip install buildozer cython==0.29.36
```

### Compilar APK Debug

```bash
# Primera compilación (descarga dependencias)
buildozer android debug

# Compilaciones posteriores (más rápido)
buildozer android debug deploy run
```

El APK se generará en: `bin/factorymanager-2.0.1-arm64-v8a_armeabi-v7a-debug.apk`

### Compilar AAB Release

```bash
# Compilar AAB
buildozer android release

# El AAB se generará en: bin/*.aab
```

### Instalar en Dispositivo

```bash
# Instalar y ejecutar
buildozer android debug deploy run

# Solo instalar
buildozer android deploy
```

---

## Solución de Problemas

### Error: `No module named 'kivymd'`

**Causa**: KivyMD 2.0 no está instalado correctamente.

**Solución**:
```bash
pip uninstall kivymd -y
pip install https://github.com/kivymd/KivyMD/archive/master.zip
```

### Error: `No module named 'materialyoucolor'`

**Causa**: Dependencia faltante de KivyMD 2.0.

**Solución**:
```bash
pip install materialyoucolor
```

### Error: `mutex lock failed`

**Causa**: Problema con multiprocesamiento en Android.

**Solución**: 
- No uses `multiprocessing` en Android
- Usa `Clock.schedule_once()` para operaciones asíncronas
- Asegúrate de usar `kivy==2.3.0`

### Error: `ModuleNotFoundError: android`

**Causa**: El módulo `android` solo está disponible en Android.

**Solución**: La aplicación detecta automáticamente la plataforma. No es un error en desktop.

### Error: `Permission denied` en Android 13+

**Causa**: Permisos de almacenamiento no concedidos.

**Solución**:
- La app solicita permisos automáticamente
- Si se rechazan, ve a Configuración → Apps → Factory Manager → Permisos
- Habilita "Acceso a todos los archivos"

### Error de compilación: `NDK not found`

**Solución**:
```bash
# Limpiar y recompilar
buildozer android clean
buildozer android debug
```

### Error: `Out of memory`

**Solución**:
```bash
# Aumentar memoria swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Configuración Avanzada

### Optimizar Tamaño del APK

Edita `buildozer.spec`:

```ini
# Excluir archivos innecesarios
source.exclude_exts = spec,txt,md,rst,json
source.exclude_dirs = tests, docs, .git

# Comprimir recursos
android.add_assets = assets/
```

### Configurar ProGuard (Ofuscación)

Añade a `buildozer.spec`:

```ini
android.gradle_dependencies = androidx.core:core:1.10.1
android.enable_androidx = True
```

### Soporte para Arquitecturas Específicas

```ini
# Solo ARM64 (más pequeño)
android.archs = arm64-v8a

# Todas las arquitecturas
android.archs = arm64-v8a, armeabi-v7a, x86, x86_64
```

### Configurar Versión de Python

```ini
requirements = python3==3.10.11, kivy==2.3.0, ...
```

---

## 📚 Recursos Adicionales

- [Documentación de Kivy](https://kivy.org/doc/stable/)
- [Documentación de KivyMD](https://kivymd.readthedocs.io/)
- [Documentación de Buildozer](https://buildozer.readthedocs.io/)
- [Python for Android](https://python-for-android.readthedocs.io/)

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs de GitHub Actions
2. Ejecuta `buildozer android debug` localmente para ver errores detallados
3. Consulta la sección de [Solución de Problemas](#solución-de-problemas)
4. Crea un issue en el repositorio

---

<p align="center">
  <b>🏭 Factory Manager Pro - Compilación Exitosa</b>
</p>
