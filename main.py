import sys
import os
import math
import random
import ctypes
from ctypes import wintypes

os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QScrollArea, QSizePolicy, QGridLayout, QProgressBar
)
from PySide6.QtCore import (
    Qt, QPoint, QPropertyAnimation, QEasingCurve,
    QTimer, QParallelAnimationGroup, QRectF
)
from PySide6.QtGui import (
    QPainter, QColor, QLinearGradient, QBrush, QPen, QFont,
    QPainterPath, QPalette
)

# ── Motor de Temas de Producción Élite (Nivel 10) ────────
import json
try:
    import resources_rc # Intentar cargar recursos compilados
except ImportError:
    pass
from PySide6.QtCore import QFileSystemWatcher, Signal, QObject

class ThemeManager(QObject):
    themeChanged = Signal() # Señal para el Hot-Reload
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ThemeManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        if not hasattr(self, "_initialized"):
            self._init_themes()
            self._initialized = True

    def _init_themes(self):
        # Prioridad 1: Recurso embebido (Producción)
        # Prioridad 2: Archivo físico (Desarrollo/Hot-Reload)
        self.theme_res = ":/theme.json"
        self.theme_file = os.path.join(os.getcwd(), "theme.json")
        self._load_from_disk()
        
        # Vigilar cambios en el archivo físico si existe (Hot-Reload)
        self.watcher = QFileSystemWatcher()
        if os.path.exists(self.theme_file):
            self.watcher.addPath(self.theme_file)
        self.watcher.fileChanged.connect(self._on_file_changed)

    def _load_from_disk(self):
        try:
            from PySide6.QtCore import QFile, QTextStream
            # Recordar qué tema teníamos antes de recargar del disco
            active_name = getattr(self, "current_name", "neutral_dark")
            
            if os.path.exists(self.theme_file):
                with open(self.theme_file, "r") as f:
                    self.themes = json.load(f)
            else:
                f_qt = QFile(self.theme_res)
                if f_qt.open(QFile.ReadOnly | QFile.Text):
                    stream = QTextStream(f_qt)
                    self.themes = json.loads(stream.readAll())
                    f_qt.close()
            
            self.current_name = active_name
            self.current = self.themes[self.current_name]
        except Exception as e:
            print(f"Error cargando tema: {e}")

    def set_theme(self, name):
        if name in self.themes:
            self.current_name = name
            self.current = self.themes[name]
            self.themeChanged.emit() # ¡BUM! Hot-Reload interno
            print(f"Cambiado a tema: {name} ✨")

    def _on_file_changed(self, path):
        # Pequeño delay porque algunos editores guardan en dos pasos
        QTimer.singleShot(100, self._reload)

    def _reload(self):
        self._load_from_disk()
        self.themeChanged.emit() # Notificar a todos
        print("Tema recargado en caliente (Hot-Reload Activo) 🔥")

    def get_color(self, key):
        if isinstance(key, QColor): return key
        return QColor(self.current.get(key, "#FF00FF"))

    def get_master_qss(self):
        c = self.current
        return f"""
            QWidget#root {{ background-color: {c['bg']}; color: {c['text']}; }}
            .Sidebar {{ background-color: {c['sidebar']}; border: none; }}
            .FlatCard {{ background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 10px; }}
            .FlatCard[state="active"] {{ border-color: {c['accent']}; }}
            .FlatCard:hover {{ border-color: {c['accent']}; }}
            QScrollBar:vertical {{ border: none; background: transparent; width: 6px; }}
            QScrollBar::handle:vertical {{ background: {c['accent']}; opacity: 0.5; border-radius: 3px; }}
        """

theme = ThemeManager()

def update_widget_style(w, state=None):
    """El truco industrial: fuerza a Qt a re-evaluar el QSS al cambiar propiedades."""
    if state: w.setProperty("state", state)
    w.style().unpolish(w)
    w.style().polish(w)
    w.update()

# Punteros de compatibilidad vivos (Nivel 10)
C_BG = theme.get_color("bg")
C_SIDEBAR = theme.get_color("sidebar")
C_SURFACE = theme.get_color("surface")
C_SURFACE2 = theme.get_color("surface2")
C_BORDER = theme.get_color("border")
C_BORDER_H = theme.get_color("border_h")
C_ORANGE = theme.get_color("accent")
C_BLUE = theme.get_color("secondary")
C_TEXT = theme.get_color("text")
C_DIM = theme.get_color("dim")
C_GREEN = theme.get_color("green")
C_RED = theme.get_color("red")
C_YELLOW = theme.get_color("accent")

def refresh_global_colors():
    global C_BG, C_SIDEBAR, C_SURFACE, C_SURFACE2, C_BORDER, C_BORDER_H, C_ORANGE, C_BLUE, C_TEXT, C_DIM, C_GREEN, C_RED, C_YELLOW
    C_BG = theme.get_color("bg")
    C_SIDEBAR = theme.get_color("sidebar")
    C_SURFACE = theme.get_color("surface")
    C_SURFACE2 = theme.get_color("surface2")
    C_BORDER = theme.get_color("border")
    C_BORDER_H = theme.get_color("border_h")
    C_ORANGE = theme.get_color("accent")
    C_BLUE = theme.get_color("secondary")
    C_TEXT = theme.get_color("text")
    C_DIM = theme.get_color("dim")
    C_GREEN = theme.get_color("green")
    C_RED = theme.get_color("red")
    C_YELLOW = theme.get_color("accent")

theme.themeChanged.connect(refresh_global_colors)

def aa_font(size=10, weight=QFont.Medium):
    f = QFont("Segoe UI Variable Display", size)
    if f.family() != "Segoe UI Variable Display": f = QFont("Inter", size)
    f.setWeight(weight)
    f.setStyleStrategy(QFont.PreferAntialias | QFont.PreferQuality)
    f.setHintingPreference(QFont.PreferNoHinting)
    return f

def label(text, size=11, color="text", bold=False, caps=False, letter_spacing=0):
    l = QLabel(text)
    c = theme.get_color(color)
    weight = "600" if bold else "500"
    ls = f"letter-spacing:{letter_spacing}px;" if letter_spacing else ""
    tc = f"text-transform:uppercase;" if caps else ""
    l.setStyleSheet(f"color:rgba({c.red()},{c.green()},{c.blue()},255); font-size:{size}px; font-weight:{weight}; background:transparent; {ls}{tc}")
    return l


# ── Fondo estático con gradiente sutil ────────
class FlatBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, _):
        p = QPainter(self)
        g = QLinearGradient(0, 0, self.width(), self.height())
        g.setColorAt(0, QColor(22, 18, 36))
        g.setColorAt(1, QColor(14, 12, 24))
        p.fillRect(self.rect(), QBrush(g))
        p.end()


# ── FlatCard ──────────────────────────────────
class FlatCard(QWidget):
    def __init__(self, parent=None, radius=12):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._hover = False
        self._radius = radius

    def enterEvent(self, e): self._hover = True;  self.update(); super().enterEvent(e)
    def leaveEvent(self, e): self._hover = False; self.update(); super().leaveEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        # Nivel 10 Rendering Strategy
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        r = self.rect()
        path = QPainterPath()
        path.addRoundedRect(r.x(), r.y(), r.width(), r.height(), self._radius, self._radius)
        p.setPen(Qt.NoPen)
        p.fillPath(path, QBrush(theme.get_color("surface2") if self._hover else theme.get_color("surface")))
        p.setPen(QPen(theme.get_color("border_h") if self._hover else theme.get_color("border"), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(r.adjusted(1,1,-1,-1), self._radius, self._radius)
        p.end()


# ── StatCard ─────────────────────────────────
class StatCard(FlatCard):
    def __init__(self, title, value, value_unit, subtitle, color, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(110)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18); lay.setSpacing(4)

        # Número grande
        num_row = QHBoxLayout(); num_row.setSpacing(4); num_row.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        num_lbl = QLabel(value)
        num_lbl.setStyleSheet(f"color:rgba({color.red()},{color.green()},{color.blue()},255);"
                              f"font-size:32px;font-weight:800;background:transparent;")
        num_row.addWidget(num_lbl)
        if value_unit:
            unit_lbl = QLabel(value_unit)
            unit_lbl.setStyleSheet(f"color:rgba({color.red()},{color.green()},{color.blue()},200);"
                                   f"font-size:14px;font-weight:600;background:transparent;")
            unit_lbl.setAlignment(Qt.AlignBottom)
            num_row.addWidget(unit_lbl)
        num_row.addStretch()

        sec_title = label(title.upper(), size=10, color=C_DIM, letter_spacing=1)
        desc_lbl  = label(subtitle, size=11, color=QColor(180, 175, 205))

        lay.addWidget(sec_title)
        lay.addLayout(num_row)
        lay.addWidget(desc_lbl)


# ── StatsPanel (replica del screenshot) ───────
class StatsPanel(FlatCard):
    """Panel con varias stats en una fila, como la imagen de referencia."""
    def __init__(self, section_title, stats, parent=None):
        super().__init__(parent, radius=10)
        lay = QVBoxLayout(self); lay.setContentsMargins(20,16,20,16); lay.setSpacing(12)

        sec = label(section_title.upper(), size=10, color=C_DIM, letter_spacing=2)
        lay.addWidget(sec)

        # Línea divisora
        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:rgba({C_BORDER.red()},{C_BORDER.green()},{C_BORDER.blue()},255);border:none;max-height:1px;")
        lay.addWidget(sep)

        row = QHBoxLayout(); row.setSpacing(0)
        for i, (val, unit, desc, color) in enumerate(stats):
            if i > 0:
                div = QFrame(); div.setFrameShape(QFrame.VLine)
                div.setStyleSheet(f"background:rgba({C_BORDER.red()},{C_BORDER.green()},{C_BORDER.blue()},255);border:none;max-width:1px;")
                row.addWidget(div)

            cell = QWidget(); cell.setAttribute(Qt.WA_TranslucentBackground)
            cl = QVBoxLayout(cell); cl.setContentsMargins(16 if i>0 else 0, 0, 16, 0); cl.setSpacing(2)

            num_row = QHBoxLayout(); num_row.setSpacing(4); num_row.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            nl = QLabel(val)
            nl.setStyleSheet(f"color:rgba({color.red()},{color.green()},{color.blue()},255);font-size:26px;font-weight:800;background:transparent;")
            num_row.addWidget(nl)
            if unit:
                ul = QLabel(unit)
                ul.setStyleSheet(f"color:rgba({color.red()},{color.green()},{color.blue()},200);font-size:12px;font-weight:600;background:transparent;")
                ul.setAlignment(Qt.AlignBottom); num_row.addWidget(ul)

            dl = label(desc, size=11, color=C_DIM)
            dl.setWordWrap(True)
            cl.addLayout(num_row); cl.addWidget(dl)
            row.addWidget(cell, 1)
        lay.addLayout(row)


class BarChart(QWidget):
    def __init__(self, color_key="accent", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._color_key = color_key
        # Caché Dinámica con Conexión al Motor (Nivel 10)
        self._refresh_cache()
        theme.themeChanged.connect(self._refresh_cache)
        
        self._labels = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
        self._values = [random.randint(20,95) for _ in range(7)]
        self._av = [0.0]*7
        t = QTimer(self); t.timeout.connect(self._anim); t.start(16)

    def _refresh_cache(self):
        self._cache_color = theme.get_color(self._color_key)
        self._cache_dim = QColor(int(self._cache_color.red()*0.45), 
                                 int(self._cache_color.green()*0.45), 
                                 int(self._cache_color.blue()*0.45))
        self.update()

    def _anim(self):
        done = True
        for i in range(7):
            tgt = self._values[i]/100
            if self._av[i] < tgt: self._av[i] = min(tgt, self._av[i]+0.025); done=False
        self.update()
        if done: self.sender().stop()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        w, h = self.width(), self.height()
        pl, pb = 8, 26; ch = h-pb-8; bw = (w-pl*2)/7; gap = bw*0.35
        mx = max(self._av) if max(self._av) > 0 else 1
        
        # Uso de color cacheado
        col_main = self._cache_color
        col_dim = QColor(int(col_main.red()*0.45), int(col_main.green()*0.45), int(col_main.blue()*0.45))
        
        for i, (lbl, val) in enumerate(zip(self._labels, self._av)):
            bx = pl + i*bw + gap/2; bww = bw-gap; bh = ch*(val/mx)*0.9; by = h-pb-bh
            col = col_main if i == self._av.index(max(self._av)) else col_dim
            path = QPainterPath(); r2 = min(4, bww/2)
            path.addRoundedRect(bx, by, bww, bh, r2, r2)
            p.setPen(Qt.NoPen); p.fillPath(path, QBrush(col))
            p.setPen(C_DIM); p.setFont(aa_font(9))
            p.drawText(int(bx), h-4, int(bww), 18, Qt.AlignCenter, lbl)
        p.end()


# ── LineChart ─────────────────────────────────
class LineChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._series = {
            "Visitants":   ([45,62,38,75,55,88,72,91,68,85,78,95], C_ORANGE),
            "Sessions":    ([32,48,28,58,44,71,60,78,55,70,65,82], C_BLUE),
            "Conversions": ([12,18, 9,22,16,28,21,31,19,25,23,34], C_GREEN),
        }
        self._months = ["Gen","Feb","Mar","Abr","Mai","Jun","Jul","Ago","Set","Oct","Nov","Des"]
        self._prog = 0.0
        t = QTimer(self); t.timeout.connect(self._tick); t.start(16)

    def _tick(self):
        if self._prog < 1.0: self._prog = min(1.0, self._prog+0.018); self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        w, h = self.width(), self.height()
        pl, pr, pt, pb = 40, 12, 8, 28
        cw, ch_h = w-pl-pr, h-pt-pb
        n = len(self._months)
        all_v = [v for s in self._series.values() for v in s[0]]
        mx = max(all_v)*1.12

        def tx(i): return pl + i*cw/(n-1)
        def ty(v): return pt + ch_h - v/mx*ch_h

        p.setPen(QPen(C_BORDER, 1))
        for i in range(5):
            y = pt + i*ch_h/4
            p.drawLine(int(pl), int(y), int(w-pr), int(y))
            p.setPen(C_DIM); p.setFont(aa_font(8))
            p.drawText(0, int(y)-8, int(pl)-4, 16, Qt.AlignRight|Qt.AlignVCenter, str(int(mx*(1-i/4))))
            p.setPen(QPen(C_BORDER, 1))

        p.setPen(C_DIM); p.setFont(aa_font(9))
        for i, m in enumerate(self._months):
            p.drawText(int(tx(i))-14, h-pb+4, 28, 20, Qt.AlignCenter, m)

        for _, (vals, color) in self._series.items():
            count = max(2, int(self._prog*(n-1))+1)
            pts = [(tx(i), ty(v)) for i, v in enumerate(vals)]
            vis = list(pts[:count])
            if count <= n-1:
                frac = self._prog*(n-1) - (count-2)
                x0,y0 = pts[count-2]; x1,y1 = pts[count-1]
                vis[-1] = (x0+(x1-x0)*frac, y0+(y1-y0)*frac)

            ap = QPainterPath(); ap.moveTo(vis[0][0], h-pb)
            for x,y in vis: ap.lineTo(x,y)
            ap.lineTo(vis[-1][0], h-pb); ap.closeSubpath()
            ag = QLinearGradient(0,pt,0,h-pb)
            ag.setColorAt(0, QColor(color.red(),color.green(),color.blue(),40))
            ag.setColorAt(1, QColor(color.red(),color.green(),color.blue(),0))
            p.fillPath(ap, QBrush(ag))

            lp = QPainterPath(); lp.moveTo(*vis[0])
            for x,y in vis[1:]: lp.lineTo(x,y)
            p.setPen(QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush); p.drawPath(lp)

            lx,ly = vis[-1]
            p.setBrush(color); p.setPen(QPen(C_SURFACE, 2))
            p.drawEllipse(QPoint(int(lx),int(ly)), 4, 4)
        p.end()


# ── DonutChart ────────────────────────────────
class DonutChart(QWidget):
    def __init__(self, segs, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._segs = segs; self._prog = 0.0
        t = QTimer(self); t.timeout.connect(self._tick); t.start(16)

    def _tick(self):
        if self._prog < 1.0: self._prog = min(1.0, self._prog+0.02); self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        w,h = self.width(),self.height()
        sz = min(w,h)-20; rect = QRectF((w-sz)/2,(h-sz)/2,sz,sz)
        total = sum(v for _,v,_ in self._segs); start = -90*16
        for _,val,color in self._segs:
            span = int(360*16*val/total*self._prog)
            p.setPen(Qt.NoPen); p.setBrush(color); p.drawPie(rect,start,span); start+=span
        inner = sz*0.6; ir = QRectF((w-inner)/2,(h-inner)/2,inner,inner)
        p.setBrush(C_SURFACE); p.setPen(Qt.NoPen); p.drawEllipse(ir)
        p.setPen(C_TEXT); p.setFont(aa_font(14, QFont.Bold))
        p.drawText(ir.toRect(), Qt.AlignCenter, f"{int(sum(v for _,v,_ in self._segs)*self._prog):,}")
        p.end()


# ── ActivityRow ───────────────────────────────
class ActivityRow(QWidget):
    def __init__(self, icon, text, time_str, color, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(48)
        lay = QHBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(12)

        dot = QLabel(icon); dot.setFixedSize(34,34); dot.setAlignment(Qt.AlignCenter)
        dot.setStyleSheet(f"font-size:15px;background:rgba({color.red()},{color.green()},{color.blue()},30);"
                          f"border-radius:17px;border:1px solid rgba({color.red()},{color.green()},{color.blue()},80);color:white;")
        tl = label(text, 12); tl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        ti = label(time_str, 11, C_DIM)
        lay.addWidget(dot); lay.addWidget(tl); lay.addWidget(ti)


# ── KanbanCard ────────────────────────────────
class KanbanCard(FlatCard):
    def __init__(self, title, user, tag, tag_color, prog, parent=None):
        super().__init__(parent, radius=8)
        lay = QVBoxLayout(self); lay.setContentsMargins(14,12,14,12); lay.setSpacing(8)

        tag_lbl = QLabel(tag.upper()); tag_lbl.setFixedHeight(20); tag_lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        tag_lbl.setStyleSheet(f"color:rgba({tag_color.red()},{tag_color.green()},{tag_color.blue()},255);"
                              f"font-size:9px;letter-spacing:1px;font-weight:700;"
                              f"background:rgba({tag_color.red()},{tag_color.green()},{tag_color.blue()},25);"
                              f"border:1px solid rgba({tag_color.red()},{tag_color.green()},{tag_color.blue()},80);"
                              f"border-radius:4px;padding:0 7px;")
        tag_lbl.setAlignment(Qt.AlignCenter)

        t = label(title, 12, bold=True); t.setWordWrap(True)

        bot = QHBoxLayout(); bot.setSpacing(8)
        av = QLabel(user); av.setFixedSize(24,24); av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"background:rgba({tag_color.red()},{tag_color.green()},{tag_color.blue()},60);"
                         f"color:rgba({tag_color.red()},{tag_color.green()},{tag_color.blue()},255);"
                         f"font-size:10px;font-weight:700;border-radius:12px;"
                         f"border:1px solid rgba({tag_color.red()},{tag_color.green()},{tag_color.blue()},120);")

        bw = QWidget(); bw.setAttribute(Qt.WA_TranslucentBackground)
        bl = QVBoxLayout(bw); bl.setContentsMargins(0,0,0,0); bl.setSpacing(2)
        bar = QProgressBar(); bar.setValue(prog); bar.setTextVisible(False); bar.setFixedHeight(3)
        bar.setStyleSheet(f"QProgressBar{{background:rgba({C_BORDER.red()},{C_BORDER.green()},{C_BORDER.blue()},255);border-radius:1px;border:none;}}"
                          f"QProgressBar::chunk{{background:rgba({tag_color.red()},{tag_color.green()},{tag_color.blue()},200);border-radius:1px;}}")
        pct = label(f"{prog}%", 10, C_DIM)
        bl.addWidget(bar); bl.addWidget(pct)

        bot.addWidget(av); bot.addWidget(bw, 1)
        lay.addWidget(tag_lbl); lay.addWidget(t); lay.addLayout(bot)


# ── SidebarButton ─────────────────────────────
class SidebarButton(QPushButton):
    def __init__(self, icon_char, lbl, active=False, parent=None):
        super().__init__(parent)
        self._active = active
        self.setFixedHeight(44); self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True); self.setChecked(active)
        self.setText(f"  {icon_char}  {lbl}")
        self._style(); self.toggled.connect(lambda c: (setattr(self,'_active',c), self._style()))

    def _style(self):
        if self._active:
            self.setStyleSheet(f"""QPushButton{{
                background:rgba({C_ORANGE.red()},{C_ORANGE.green()},{C_ORANGE.blue()},22);
                color:rgba({C_ORANGE.red()},{C_ORANGE.green()},{C_ORANGE.blue()},255);
                font-size:13px;font-weight:600;
                border-left:3px solid rgba({C_ORANGE.red()},{C_ORANGE.green()},{C_ORANGE.blue()},255);
                border-right:none;border-top:none;border-bottom:none;
                border-radius:0px;text-align:left;padding-left:13px;}}""")
        else:
            self.setStyleSheet(f"""QPushButton{{
                background:transparent;color:rgba({C_DIM.red()},{C_DIM.green()},{C_DIM.blue()},255);
                font-size:13px;border:none;border-radius:0;
                text-align:left;padding-left:16px;}}
                QPushButton:hover{{background:rgba(255,255,255,6);
                color:rgba({C_TEXT.red()},{C_TEXT.green()},{C_TEXT.blue()},255);}}""")


# ── TitleBar ──────────────────────────────────
class TitleBar(QWidget):
    def __init__(self, win, parent=None):
        super().__init__(parent)
        self._win = win; self._drag = None
        self.setFixedHeight(48)
        self.setStyleSheet(f"background:rgba({C_SIDEBAR.red()},{C_SIDEBAR.green()},{C_SIDEBAR.blue()},255);")
        lay = QHBoxLayout(self); lay.setContentsMargins(20,0,12,0); lay.setSpacing(10)

        logo = QLabel("◈"); logo.setStyleSheet(f"color:rgba({C_ORANGE.red()},{C_ORANGE.green()},{C_ORANGE.blue()},255);font-size:18px;background:transparent;")
        title = QLabel("Prototip"); title.setStyleSheet("color:white;font-size:14px;font-weight:700;background:transparent;")
        sub = QLabel("DASHBOARD"); sub.setStyleSheet(f"color:rgba({C_DIM.red()},{C_DIM.green()},{C_DIM.blue()},255);font-size:10px;letter-spacing:2px;background:transparent;")
        lay.addWidget(logo); lay.addWidget(title); lay.addWidget(sub); lay.addStretch()

        for ch, tip, col, fn in [("─","Minimizar",C_DIM,win.showMinimized),
                                   ("□","Maximizar",C_DIM,self._toggle_max),
                                   ("✕","Cerrar",C_RED,win.close)]:
            b = QPushButton(ch); b.setFixedSize(30,30); b.setToolTip(tip); b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(f"QPushButton{{background:transparent;color:rgba({col.red()},{col.green()},{col.blue()},200);border:none;font-size:13px;border-radius:6px;}}"
                            f"QPushButton:hover{{background:rgba(255,255,255,10);color:white;}}")
            b.clicked.connect(fn); lay.addWidget(b)

    def _toggle_max(self):
        self._win.showNormal() if self._win.isMaximized() else self._win.showMaximized()
    def mousePressEvent(self, e):
        if e.button()==Qt.LeftButton: self._drag = e.globalPosition().toPoint()-self._win.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if self._drag and e.buttons()&Qt.LeftButton: self._win.move(e.globalPosition().toPoint()-self._drag)
    def mouseReleaseEvent(self, _): self._drag = None


# Eliminado helper nativo inconsistente



# ── AnimatedStack ─────────────────────────────
class AnimatedStack(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pages = []; self._cur = 0; self._busy = False; self._grp = None

    def addPage(self, w):
        w.setParent(self); w.setGeometry(0,0,self.width(),self.height())
        w.setVisible(len(self._pages)==0); self._pages.append(w)

    def switchTo(self, idx):
        if idx==self._cur or self._busy or not self._pages: return
        direction = 1 if idx>self._cur else -1
        self._busy = True
        old=self._pages[self._cur]; new=self._pages[idx]; W=self.width()
        new.setGeometry(direction*W,0,W,self.height()); new.show(); new.raise_()
        oe=QGraphicsOpacityEffect(old); ne=QGraphicsOpacityEffect(new)
        old.setGraphicsEffect(oe); new.setGraphicsEffect(ne); ne.setOpacity(0.0)
        dur=360; ease=QEasingCurve.OutCubic

        def pa(w,s,e):
            a=QPropertyAnimation(w,b"pos"); a.setDuration(dur)
            a.setStartValue(QPoint(s,0)); a.setEndValue(QPoint(e,0)); a.setEasingCurve(ease); return a
        def fa(e,s,ev):
            a=QPropertyAnimation(e,b"opacity"); a.setDuration(dur)
            a.setStartValue(s); a.setEndValue(ev); a.setEasingCurve(ease); return a

        grp=QParallelAnimationGroup(self)
        grp.addAnimation(pa(old,0,-direction*W)); grp.addAnimation(pa(new,direction*W,0))
        grp.addAnimation(fa(oe,1.0,0.0)); grp.addAnimation(fa(ne,0.0,1.0))

        def done():
            old.hide(); old.move(0,0); old.setGraphicsEffect(None)
            new.setGraphicsEffect(None); self._cur=idx; self._busy=False

        grp.finished.connect(done); grp.start(); self._grp=grp

    def resizeEvent(self, e):
        super().resizeEvent(e)
        for i,pg in enumerate(self._pages):
            if i==self._cur: pg.setGeometry(0,0,self.width(),self.height())


# ══════════════════════════════════════════════
#  HELPERS UI
# ══════════════════════════════════════════════
def _sep():
    s=QFrame(); s.setFrameShape(QFrame.HLine)
    s.setStyleSheet(f"background:rgba({C_BORDER.red()},{C_BORDER.green()},{C_BORDER.blue()},255);border:none;max-height:1px;"); return s

def _scroll(inner):
    sc=QScrollArea(); sc.setWidgetResizable(True); sc.setFrameShape(QFrame.NoFrame)
    sc.setStyleSheet("QScrollArea{background:transparent;border:none;}")
    sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    sc.verticalScrollBar().setStyleSheet(
        f"QScrollBar:vertical{{background:rgba({C_SURFACE.red()},{C_SURFACE.green()},{C_SURFACE.blue()},255);width:5px;border-radius:2px;}}"
        f"QScrollBar::handle:vertical{{background:rgba({C_ORANGE.red()},{C_ORANGE.green()},{C_ORANGE.blue()},120);border-radius:2px;}}"
        "QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}")
    inner.setStyleSheet("background:transparent;"); sc.setWidget(inner); return sc

def _section(main_text, sub_text=None):
    w=QWidget(); w.setAttribute(Qt.WA_TranslucentBackground)
    l=QVBoxLayout(w); l.setContentsMargins(0,0,0,0); l.setSpacing(3)
    l.addWidget(label(main_text, 20, bold=True))
    if sub_text: l.addWidget(label(sub_text, 12, C_DIM))
    return w

def _card_title(text):
    l=label(text.upper(), 10, C_DIM, letter_spacing=1)
    l.setContentsMargins(0,0,0,6); return l


# ══════════════════════════════════════════════
#  PÁGINAS
# ══════════════════════════════════════════════
class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.setAttribute(Qt.WA_TranslucentBackground)
        inner=QWidget(); lay=QVBoxLayout(inner); lay.setContentsMargins(28,24,28,28); lay.setSpacing(20)

        lay.addWidget(_section("Resum general", "Avui, 6 de març de 2026"))

        # Panel estilo referencia (el screenshot del usuario)
        panel = StatsPanel("ESTADÍSTIQUES", [
            ("14.453", "", "Peticions processades avui", C_ORANGE),
            ("407,6", "MB", "Dades transferides", C_BLUE),
            ("13", "min", "Temps mitjà de resposta", C_TEXT),
        ])
        panel.setFixedHeight(130)
        lay.addWidget(panel)

        # Stat cards
        sg=QGridLayout(); sg.setSpacing(14)
        for i,(tit,val,unit,sub,col) in enumerate([
            ("USUARIS ACTIUS","1.284","","↑ 12% respecte ahir",C_ORANGE),
            ("INGRESSOS","€48.320","","↑ 8.4% aquest mes",C_BLUE),
            ("SOL·LICITUDS","3.921","","↓ 3% respecte ahir",C_DIM),
            ("TEMPS RESPOSTA","124","ms","✓ Rang òptim",C_GREEN),
        ]): sg.addWidget(StatCard(tit,val,unit,sub,col), 0, i)
        lay.addLayout(sg)

        bot=QHBoxLayout(); bot.setSpacing(14)

        cc=FlatCard(); cc.setMinimumHeight(260); cl=QVBoxLayout(cc); cl.setContentsMargins(18,16,18,16)
        cl.addWidget(_card_title("activitat setmanal"))
        bc=BarChart(C_ORANGE); bc.setMinimumHeight(180); cl.addWidget(bc,1)
        bot.addWidget(cc,3)

        ac=FlatCard(); al=QVBoxLayout(ac); al.setContentsMargins(18,16,18,10); al.setSpacing(0)
        al.addWidget(_card_title("activitat recent"))
        for ico,txt,t,col in [("🚀","Nou desplegament","fa 2 min",C_ORANGE),
                                ("👤","Marc s'ha connectat","fa 8 min",C_BLUE),
                                ("⚠️","Alerta rendiment","fa 15 min",C_YELLOW),
                                ("✅","Backup completat","fa 32 min",C_GREEN),
                                ("📦","Paquet instal·lat","fa 1 h",C_BLUE),
                                ("🔒","Accés denegat","fa 2 h",C_RED)]:
            al.addWidget(ActivityRow(ico,txt,t,col)); al.addWidget(_sep())
        al.addStretch()
        bot.addWidget(ac,2); lay.addLayout(bot); lay.addStretch()

        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.addWidget(_scroll(inner))


class AnalitiquesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.setAttribute(Qt.WA_TranslucentBackground)
        inner=QWidget(); lay=QVBoxLayout(inner); lay.setContentsMargins(28,24,28,28); lay.setSpacing(20)

        lay.addWidget(_section("Analítiques", "Rendiment del darrer any"))

        panel = StatsPanel("RESUM ANUAL", [
            ("124.830","","Visitants únics", C_ORANGE),
            ("3,42","%","Taxa de conversió", C_BLUE),
            ("4m 12s","","Temps mitjà de sessió", C_GREEN),
        ])
        panel.setFixedHeight(130); lay.addWidget(panel)

        lc_card=FlatCard(); lc_card.setMinimumHeight(300)
        ll=QVBoxLayout(lc_card); ll.setContentsMargins(18,16,18,16)
        hdr=QHBoxLayout(); hdr.addWidget(_card_title("evolució anual")); hdr.addStretch()
        for nm,col in [("Visitants",C_ORANGE),("Sessions",C_BLUE),("Conversions",C_GREEN)]:
            dl=QLabel("●"); dl.setStyleSheet(f"color:rgba({col.red()},{col.green()},{col.blue()},255);background:transparent;font-size:12px;")
            nl=label(nm, 11, C_DIM); nl.setContentsMargins(0,0,12,0)
            hdr.addWidget(dl); hdr.addWidget(nl)
        ll.addLayout(hdr)
        lc=LineChart(); lc.setMinimumHeight(220); ll.addWidget(lc,1)
        lay.addWidget(lc_card)

        bot=QHBoxLayout(); bot.setSpacing(14)
        dc=FlatCard(); dl2=QVBoxLayout(dc); dl2.setContentsMargins(18,16,18,16)
        dl2.addWidget(_card_title("font de trànsit"))
        segs=[("Orgànic",52,C_ORANGE),("Directe",24,C_BLUE),("Social",14,C_GREEN),("Email",10,C_YELLOW)]
        dn=DonutChart(segs); dn.setMinimumHeight(200); dl2.addWidget(dn,1)
        bot.addWidget(dc,2)

        tc=FlatCard(); tl2=QVBoxLayout(tc); tl2.setContentsMargins(18,16,18,16); tl2.setSpacing(10)
        tl2.addWidget(_card_title("desglossament"))
        for lbl2,pct,col in segs:
            rr=QHBoxLayout(); rr.setSpacing(8)
            d2=QLabel("●"); d2.setStyleSheet(f"color:rgba({col.red()},{col.green()},{col.blue()},255);background:transparent;")
            nl2=label(lbl2, 12); nl2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            pl2=label(f"{pct}%", 13, col, bold=True)
            pb=QProgressBar(); pb.setValue(pct); pb.setTextVisible(False); pb.setFixedHeight(3)
            pb.setStyleSheet(f"QProgressBar{{background:rgba({C_BORDER.red()},{C_BORDER.green()},{C_BORDER.blue()},255);border-radius:1px;border:none;}}"
                             f"QProgressBar::chunk{{background:rgba({col.red()},{col.green()},{col.blue()},200);border-radius:1px;}}")
            rr.addWidget(d2); rr.addWidget(nl2); rr.addWidget(pl2)
            tl2.addLayout(rr); tl2.addWidget(pb)
        tl2.addStretch(); bot.addWidget(tc,3)
        lay.addLayout(bot); lay.addStretch()

        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.addWidget(_scroll(inner))


class ProjectesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.setAttribute(Qt.WA_TranslucentBackground)
        inner=QWidget(); lay=QVBoxLayout(inner); lay.setContentsMargins(28,24,28,28); lay.setSpacing(20)

        hdr=QHBoxLayout()
        hdr.addWidget(_section("Projectes", "Gestió i seguiment de l'equip"))
        hdr.addStretch()
        nb=QPushButton("+ Nou projecte"); nb.setFixedHeight(36); nb.setCursor(Qt.PointingHandCursor)
        nb.setStyleSheet(f"QPushButton{{background:rgba({C_ORANGE.red()},{C_ORANGE.green()},{C_ORANGE.blue()},200);"
                         f"color:white;font-size:12px;font-weight:700;border:none;border-radius:6px;padding:0 18px;}}"
                         f"QPushButton:hover{{background:rgba({C_ORANGE.red()},{C_ORANGE.green()},{C_ORANGE.blue()},255);}}")
        hdr.addWidget(nb); lay.addLayout(hdr)

        projects={
            "EN CURS":[
                ("Redisseny web corporativa","A",C_ORANGE,72,"Disseny"),
                ("Integració API pagaments","M",C_BLUE,45,"Backend"),
                ("App mòbil v2.0","L",C_YELLOW,30,"Mòbil"),
            ],
            "REVISIÓ":[
                ("Migració base de dades","J",C_YELLOW,88,"DevOps"),
                ("Tests E2E frontend","S",C_GREEN,95,"QA"),
            ],
            "COMPLETAT":[
                ("Dashboard analítiques","G",C_GREEN,100,"Dades"),
                ("Sistema autenticació","P",C_BLUE,100,"Seguretat"),
                ("Refactor API REST","R",C_ORANGE,100,"Backend"),
            ],
        }
        cols=QHBoxLayout(); cols.setSpacing(14)
        for col_t,tasks in projects.items():
            cc2=FlatCard(radius=10); cl2=QVBoxLayout(cc2); cl2.setContentsMargins(14,14,14,14); cl2.setSpacing(10)
            row_h=QHBoxLayout()
            row_h.addWidget(_card_title(col_t))
            cnt=label(str(len(tasks)), 11, C_DIM); row_h.addStretch(); row_h.addWidget(cnt)
            cl2.addLayout(row_h); cl2.addWidget(_sep())
            for title,user,tag_col,prog,tag_lbl in tasks:
                cl2.addWidget(KanbanCard(title,user,tag_lbl,tag_col,prog))
            cl2.addStretch(); cols.addWidget(cc2,1)
        lay.addLayout(cols); lay.addStretch()

        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.addWidget(_scroll(inner))


# ══════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prototip")
        self.setMinimumSize(1100,700); self.resize(1280,780)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Aplicar estilos nativos para habilitar la sombra real de Windows
        if os.name == 'nt':
            hWnd = int(self.winId())
            GWL_STYLE = -16
            WS_CAPTION = 0x00C00000
            WS_THICKFRAME = 0x00040000
            WS_MINIMIZEBOX = 0x00020000
            WS_MAXIMIZEBOX = 0x00010000
            WS_SYSMENU = 0x00080000
            
            style = ctypes.windll.user32.GetWindowLongW(hWnd, GWL_STYLE)
            ctypes.windll.user32.SetWindowLongW(hWnd, GWL_STYLE, style | WS_CAPTION | WS_THICKFRAME | WS_MAXIMIZEBOX | WS_MINIMIZEBOX | WS_SYSMENU)
            
            # Forzar sombra DWM
            class MARGINS(ctypes.Structure):
                _fields_ = [("cxLeftWidth", ctypes.c_int), ("cxRightWidth", ctypes.c_int),
                            ("cyTopHeight", ctypes.c_int), ("cyBottomHeight", ctypes.c_int)]
            margins = MARGINS(1, 1, 1, 1)
            ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hWnd, ctypes.byref(margins))

        # Hot-Reload: Re-aplicar estilos cuando el JSON cambie
        theme.themeChanged.connect(self._refresh_styles)
        self._refresh_styles()

    def _refresh_styles(self):
        self.setStyleSheet(theme.get_master_qss())
        # Notificar a los hijos manuales (si los hay)
        self.update()

        root=QWidget(); root.setObjectName("root")
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        
        # Barra de título
        root_layout.addWidget(TitleBar(self, root))

        body=QHBoxLayout(); body.setContentsMargins(0,0,0,0); body.setSpacing(0)
        root_layout.addLayout(body,1)

        sidebar,self._btns=self._build_sidebar()
        body.addWidget(sidebar)

        # Divisor vertical
        vd=QFrame(); vd.setFrameShape(QFrame.VLine)
        vd.setStyleSheet(f"background:rgba({C_BORDER.red()},{C_BORDER.green()},{C_BORDER.blue()},255);border:none;max-width:1px;")
        body.addWidget(vd)

        self._stack=AnimatedStack()
        self._stack.addPage(DashboardPage())
        self._stack.addPage(AnalitiquesPage())
        self._stack.addPage(ProjectesPage())
        body.addWidget(self._stack,1)

        for bi,pi in {0:0,1:1,2:2}.items():
            self._btns[bi].clicked.connect(lambda _,i=pi: self._stack.switchTo(i))

    def _build_sidebar(self):
        sb=QWidget(); sb.setFixedWidth(210)
        sb.setStyleSheet(f"background:rgba({C_SIDEBAR.red()},{C_SIDEBAR.green()},{C_SIDEBAR.blue()},255);")
        lay=QVBoxLayout(sb); lay.setContentsMargins(0,16,0,20); lay.setSpacing(2)

        # Logo area
        logo_w=QWidget(); logo_w.setAttribute(Qt.WA_TranslucentBackground)
        logo_l=QHBoxLayout(logo_w); logo_l.setContentsMargins(16,0,16,12); logo_l.setSpacing(8)
        lgo=QLabel("◈"); lgo.setStyleSheet(f"color:rgba({C_ORANGE.red()},{C_ORANGE.green()},{C_ORANGE.blue()},255);font-size:22px;background:transparent;")
        lgo_t=QLabel("Prototip\nGlass"); lgo_t.setStyleSheet("color:white;font-size:13px;font-weight:700;background:transparent;line-height:1.3;")
        logo_l.addWidget(lgo); logo_l.addWidget(lgo_t); logo_l.addStretch()
        lay.addWidget(logo_w)

        sep=QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:rgba({C_BORDER.red()},{C_BORDER.green()},{C_BORDER.blue()},255);border:none;max-height:1px;margin:0 0 8px 0;")
        lay.addWidget(sep)

        items=[("◉","Dashboard",True),("◈","Analítiques",False),("◇","Projectes",False),
               ("△","Usuaris",False),("◎","Missatges",False),("☰","Configuració",False)]
        btns=[]
        for ico,lbl2,act in items:
            b=SidebarButton(ico,lbl2,act); btns.append(b); lay.addWidget(b)

        def exclusive(clicked):
            def h(checked):
                if checked:
                    for bb in btns:
                        if bb is not clicked: bb.setChecked(False)
            return h
        for b in btns: b.toggled.connect(exclusive(b))

        lay.addStretch()

        # Toggle de tema (Nivel 10 Elite Feature)
        self._btn_theme = SidebarButton("◑", "Tema Clar" if theme.current_name == "neutral_dark" else "Tema Fosc")
        self._btn_theme.clicked.connect(self._toggle_theme)
        lay.addWidget(self._btn_theme)

        sep2=QFrame(); sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet(f"background:rgba({C_BORDER.red()},{C_BORDER.green()},{C_BORDER.blue()},255);border:none;max-height:1px;margin:8px 0;")
        lay.addWidget(sep2)

        # User area
        uw=QWidget(); uw.setAttribute(Qt.WA_TranslucentBackground)
        ul=QHBoxLayout(uw); ul.setContentsMargins(16,12,16,0); ul.setSpacing(10)
        av=QLabel("G"); av.setFixedSize(36,36); av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"background:rgba({C_ORANGE.red()},{C_ORANGE.green()},{C_ORANGE.blue()},40);"
                         f"color:rgba({C_ORANGE.red()},{C_ORANGE.green()},{C_ORANGE.blue()},255);"
                         f"font-size:14px;font-weight:700;border-radius:18px;"
                         f"border:1px solid rgba({C_ORANGE.red()},{C_ORANGE.green()},{C_ORANGE.blue()},100);")
        vl=QVBoxLayout(); vl.setSpacing(1)
        vl.addWidget(label("Guillem P.", 12, bold=True))
        vl.addWidget(label("Administrador", 10, C_DIM))
        ul.addWidget(av); ul.addLayout(vl); lay.addWidget(uw)
        return sb, btns

    def _toggle_theme(self):
        # Efecto de fundido (Nivel 10 Polish)
        f = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(f)
        ani = QPropertyAnimation(f, b"opacity")
        ani.setDuration(300); ani.setStartValue(1.0); ani.setEndValue(0.0)
        
        def swap():
            new_name = "neutral_light" if theme.current_name == "neutral_dark" else "neutral_dark"
            theme.set_theme(new_name)
            self._btn_theme.setText(f"  ◑  {'Tema Fosc' if new_name == 'neutral_light' else 'Tema Clar'}")
            self._btn_theme.setChecked(False)
            # Volver a 1.0
            ani2 = QPropertyAnimation(f, b"opacity")
            ani2.setDuration(400); ani2.setStartValue(0.0); ani2.setEndValue(1.0)
            ani2.finished.connect(lambda: self.setGraphicsEffect(None))
            ani2.start()
            self._ani2 = ani2 # Keep ref
            
        ani.finished.connect(swap)
        ani.start()
        self._ani = ani # Keep ref

    def nativeEvent(self, eventType, message):
        """Intercepta mensajes de Windows para controlar el área no cliente (sombra y bordes)."""
        if eventType == "windows_generic_MSG":
            # Usamos ctypes para leer el mensaje de Windows
            msg = wintypes.MSG.from_address(int(message))
            if msg.message == 0x0083: # WM_NCCALCSIZE
                # Al devolver 1 (True), le decimos a Windows que no calcule área no cliente
                # Esto elimina la barra de título pero permite que DWM pinte la sombra nativa.
                return True, 0
        return super().nativeEvent(eventType, message)

    def resizeEvent(self, e):
        super().resizeEvent(e)


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app=QApplication(sys.argv); app.setStyle("Fusion")
    f=aa_font(10, QFont.Medium); app.setFont(f)

    pal=QPalette()
    pal.setColor(QPalette.Window, theme.get_color("bg"))
    pal.setColor(QPalette.WindowText, theme.get_color("text"))
    pal.setColor(QPalette.Base, theme.get_color("surface"))
    pal.setColor(QPalette.Text, theme.get_color("text"))
    pal.setColor(QPalette.Button, theme.get_color("surface"))
    pal.setColor(QPalette.ButtonText, theme.get_color("text"))
    pal.setColor(QPalette.Highlight, theme.get_color("accent"))
    pal.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(pal)

    win=MainWindow(); win.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main()
