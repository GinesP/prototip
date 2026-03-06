# 🚀 Prototip - Elite PySide6 Application Framework

**Prototip** es un motor de aplicaciones de escritorio de alto rendimiento construido con **PySide6**. Este proyecto ha evolucionado de un prototipo funcional a una arquitectura industrial de **Nivel 10**, priorizando la fidelidad visual, la mantenibilidad y el rendimiento nativo.

---

## ✨ Características Destacadas (Nivel 10)

### 🎨 Arquitectura Reactiva "Data-Driven"
- **ThemeManager (Singleton)**: Toda la estética está desacoplada en un archivo `theme.json` externo.
- **Hot-Reload de Estilo**: Edita los colores en `theme.json` y observa cómo la aplicación se actualiza en tiempo real sin reiniciarse (vía `QFileSystemWatcher`).
- **Sistema de Pulido (Unpolish/Polish)**: Reactividad instantánea en cambios de estado de widgets mediante propiedades dinámicas.

### 🖥️ Experiencia Nativa de Alta Fidelidad
- **Sombras Reales (DWM)**: Integración con la API de Windows (`ctypes`) para obtener sombras nativas sin penalización de CPU por efectos de desenfoque por software.
- **Tipografía "Editor-Grade"**: Configuración de renderizado personalizada para fuentes suaves y legibles sobre fondos oscuros (Segoe UI Variable / Inter).
- **Anti-Aliasing Industrial**: Triple estrategia de suavizado (`Antialiasing`, `TextAntialiasing`, `SmoothPixmapTransform`).

### ⚡ Rendimiento y Distribución
- **Compilación en C++**: Preparado para ser compilado con **Nuitka**, lo que traduce el código Python a binario nativo, protegiendo la IP y mejorando el tiempo de arranque.
- **Sistema de Recursos (.qrc)**: Los activos críticos (temas, iconos) están embebidos en el binario final para una distribución sin dependencias externas.

---

## 🛠️ Requisitos e Instalación

1. **Clonar el repositorio** e instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. **Compilar recursos de Qt** (necesario antes de ejecutar o compilar):
   ```bash
   pyside6-rcc resources.qrc -o resources_rc.py
   ```

---

## 🚀 Ejecución y Desarrollo

- **Modo Normal**:
  ```bash
  python main.py
  ```
- **Hot-Reload**: Mientras la aplicación corre, abre `theme.json` en tu editor y cambia cualquier valor de color. La aplicación detectará el cambio y se redibujará automáticamente.

---

## 🏗️ Compilación Profesional (Nuitka)

Para generar un ejecutable único (`.exe`) de alto rendimiento sin consola y con icono personalizado:

```bash
python -m nuitka --standalone --onefile --plugin-enable=pyside6 \
--windows-disable-console --windows-icon-from-ico=assets/logo.ico \
--output-dir=dist main.py
```

*El binario final se generará en la carpeta `dist/`.*

---

## 📘 Guía de Diseño
Para más detalles sobre los principios técnicos detrás de esta aplicación, consulta la [Pyside6 Native Design Guide](./Pyside6_Native_Design_Guide.md).

---
> [!TIP]
> **Pro Tip**: Si necesitas desplegar en producción, asegúrate de haber ejecutado `pyside6-rcc` para que el binario tome la versión más reciente del tema.
