# Guía Premium PySide6: Neutral-Dark & Native Shadows (Windows)

Esta guía documenta la configuración técnica definitiva para lograr una interfaz de alta calidad, minimalista y con integración nativa perfecta en Windows.

## 1. Sombra Nativa de Alta Calidad (WM_NCCALCSIZE)

Este método es superior a los efectos de Qt porque utiliza el motor de Windows (DWM), logrando una sombra suave y profesional sin esfuerzo de CPU.

```python
import ctypes
from ctypes import wintypes
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 1. Quitar barra nativa pero mantener Shadow/Resize nativo
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        if os.name == 'nt':
            hWnd = int(self.winId())
            GWL_STYLE = -16
            # Bits necesarios para que Windows considere la ventana "normal" y dibuje sombra
            WS_CAPTION = 0x00C00000
            WS_THICKFRAME = 0x00040000
            WS_SYSMENU = 0x00080000
            WS_MAXIMIZEBOX = 0x00010000
            WS_MINIMIZEBOX = 0x00020000
            
            style = ctypes.windll.user32.GetWindowLongW(hWnd, GWL_STYLE)
            ctypes.windll.user32.SetWindowLongW(hWnd, GWL_STYLE, style | WS_CAPTION | WS_THICKFRAME | WS_MAXIMIZEBOX | WS_MINIMIZEBOX | WS_SYSMENU)
            
            # Forzar la sombra DWM
            class MARGINS(ctypes.Structure):
                _fields_ = [("cxLeftWidth", ctypes.c_int), ("cxRightWidth", ctypes.c_int),
                            ("cyTopHeight", ctypes.c_int), ("cyBottomHeight", ctypes.c_int)]
            margins = MARGINS(1, 1, 1, 1)
            ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hWnd, ctypes.byref(margins))

    def nativeEvent(self, eventType, message):
        """EL TRUCO: Intercepta WM_NCCALCSIZE para ocultar la barra blanca nativa."""
        if eventType == "windows_generic_MSG":
            msg = wintypes.MSG.from_address(int(message))
            if msg.message == 0x0083: # WM_NCCALCSIZE
                return True, 0 # Windows no reserva espacio para la barra de título
        return super().nativeEvent(eventType, message)
```

---

## 2. Renderizado de Fuente "Estilo Editor" (Smooth & Body)

Para evitar letras delgadas o pixeladas sobre grises oscuros profundos, ajustamos el *Hinting* y la familia de fuentes.

```python
from PySide6.QtGui import QFont, QFontDatabase

def get_smooth_font(size=10, weight=QFont.Medium):
    # 'Segoe UI Variable' es la fuente nativa de Win11 que renderiza mejor
    f = QFont("Segoe UI Variable Display", size)
    if f.family() != "Segoe UI Variable Display":
        f = QFont("Inter", size)
    
    f.setWeight(weight)
    
    # ESTRATEGIA CLAVE: PreferNoHinting evita que Windows fuerce las letras a píxeles
    # individuales, permitiendo curvas suaves y redondas como en los editores de código.
    f.setStyleStrategy(QFont.PreferAntialias | QFont.PreferQuality)
    f.setHintingPreference(QFont.PreferNoHinting)
    return f

# Aplicación global en main():
# app.setFont(get_smooth_font(10, QFont.Medium))
```

---

## 3. Paleta "Neutral-Dark" (Tokens)

Colores neutros que eliminan el tinte azulado para un look más serio y profesional.

| Token | Color (HEX/RGB) | Uso |
|---|---|---|
| **Fondo** | `#252525` | Fondo principal del área de contenido |
| **Sidebar** | `#1A1A1A` | Barra lateral (máximo contraste) |
| **Borde / Línea** | `#383838` | Divisores sutiles y bordes de cards |
| **Superficie** | `#2D2D2D` | Fondo de tarjetas (ligeramente más claro) |
| **Texto Principal** | `#E1E1E1` | Blanco neutro, no puro para evitar fatiga |
| **Acento 🟠** | `#FF6428` | Naranja para números y botones principales |
| **Acento 🔵** | `#5A94FF` | Azul para métricas secundarias |

---

## 4. UI Patterns

- **Stats Row**: Uso de divisores verticales (`VLine`) entre métricas para un diseño limpio.
- **Uppercased Headers**: `letter-spacing: 1px` y `size: 10px` para títulos de sección profesionales.
- **Scrollbars Inset**: Anchura de `5px` o `6px` con color de acento semitransparente.

---

> [!IMPORTANT]
> **High-DPI**: Siempre llamar a `QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)` antes de crear la `QApplication` para evitar renderizados borrosos en monitores 4K o portátiles con escala (125%, 150%).
