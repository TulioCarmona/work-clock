# Work Clock — PyQt6
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QProgressBar,
    QPushButton, QDialog, QLineEdit, QCheckBox,
    QSlider, QGridLayout, QHBoxLayout, QVBoxLayout,
    QComboBox, QMenu, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QFont, QFontDatabase,
    QIcon, QPixmap, QAction,
)

BASE_DIR    = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"
FONTS_DIR   = BASE_DIR / "fonts"

DAYS_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]  # index+1 = ISO weekday

# ── Font registry ─────────────────────────────────────────────────────────────
FONT_FAMILIES: dict[str, str] = {}

def load_fonts() -> None:
    for path in sorted(FONTS_DIR.glob("*.ttf")) + sorted(FONTS_DIR.glob("*.otf")):
        fid  = QFontDatabase.addApplicationFont(str(path))
        fams = QFontDatabase.applicationFontFamilies(fid)
        for fam in fams:
            FONT_FAMILIES[fam] = str(path)

# ── Greeting ──────────────────────────────────────────────────────────────────
def greeting() -> str:
    h = datetime.now().hour
    if   5  <= h < 12: return "Good Morning"
    elif 12 <= h < 14: return "Hello"
    elif 14 <= h < 19: return "Good Afternoon"
    elif 19 <= h < 22: return "Good Evening"
    else:              return "Good Night"

# ── Themes ────────────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "bg_color":     QColor(30, 30, 30),
        "text":         "#FFFFFF",
        "subtext":      "#CCCCCC",
        "shadow":       QColor(0, 0, 0),
        "progress_bg":  "#3a3a3a",
        "progress_fg":  "#680000",
        "btn_bg":       "#680000",
        "btn_text":     "#FFFFFF",
        "entry_bg":     "#2a2a2a",
        "entry_text":   "#FFFFFF",
        "entry_border": "#555555",
        "dialog_bg":    "#1e1e1e",
        "label_text":   "#FFFFFF",
        "combo_bg":     "#2a2a2a",
        "combo_text":   "#FFFFFF",
        "drop_icon":    "light-drop.png",
    },
    "light": {
        "bg_color":     QColor(240, 240, 240),
        "text":         "#000000",
        "subtext":      "#333333",
        "shadow":       QColor(180, 180, 180),
        "progress_bg":  "#cccccc",
        "progress_fg":  "#680000",
        "btn_bg":       "#680000",
        "btn_text":     "#FFFFFF",
        "entry_bg":     "#ffffff",
        "entry_text":   "#000000",
        "entry_border": "#aaaaaa",
        "dialog_bg":    "#f0f0f0",
        "label_text":   "#000000",
        "combo_bg":     "#ffffff",
        "combo_text":   "#000000",
        "drop_icon":    "dark-drop.png",
    },
}

# ── Config ────────────────────────────────────────────────────────────────────
def load_config() -> dict:
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ── Style helpers ─────────────────────────────────────────────────────────────
def _icon(filename: str, size: int = 18) -> QIcon:
    pix = QPixmap(str(BASE_DIR / "icons" / filename))
    return QIcon(pix.scaled(size, size,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation))

def _btn_style(t: dict) -> str:
    return f"""
        QPushButton {{
            background-color: {t['btn_bg']}; color: {t['btn_text']};
            border-radius: 10px; padding: 4px 10px; font-size: 12px;
        }}
        QPushButton:hover   {{ background-color: #8a0000; }}
        QPushButton:pressed {{ background-color: #4a0000; }}
    """

def _entry_style(t: dict) -> str:
    return f"""
        QLineEdit {{
            background-color: {t['entry_bg']}; color: {t['entry_text']};
            border: 1px solid {t['entry_border']};
            border-radius: 6px; padding: 3px 6px; font-size: 12px;
        }}
    """

def _label_style(t: dict, size: int = 12, bold: bool = False) -> str:
    w = "bold" if bold else "normal"
    return (f"color: {t['label_text']}; font-size: {size}px; "
            f"font-weight: {w}; background: transparent;")

def _combo_style(t: dict) -> str:
    return f"""
        QComboBox {{
            background-color: {t['combo_bg']}; color: {t['combo_text']};
            border: 1px solid {t['entry_border']};
            border-radius: 6px; padding: 3px 6px; font-size: 12px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {t['combo_bg']}; color: {t['combo_text']};
            selection-background-color: #680000; selection-color: #ffffff;
        }}
        QComboBox::drop-down {{ border: none; }}
    """

def _dialog_style(t: dict) -> str:
    return f"""
        QDialog {{ background-color: {t['dialog_bg']}; }}
        QCheckBox {{
            color: {t['label_text']}; font-size: 12px; background: transparent;
        }}
        QCheckBox::indicator {{
            width: 16px; height: 16px;
            border: 2px solid #680000; border-radius: 3px;
            background: {t['entry_bg']};
        }}
        QCheckBox::indicator:checked {{ background-color: #680000; }}
        QSlider::groove:horizontal {{
            height: 6px; background: {t['progress_bg']}; border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            width: 16px; height: 16px; margin: -5px 0;
            background: #680000; border-radius: 8px;
        }}
        QSlider::sub-page:horizontal {{
            background: #680000; border-radius: 3px;
        }}
    """

# ── Settings dialog ───────────────────────────────────────────────────────────
class SettingsDialog(QDialog):
    theme_changed   = pyqtSignal(str)
    opacity_preview = pyqtSignal(float)
    font_preview    = pyqtSignal(str)

    def __init__(self, parent: "WorkClockWidget"):
        super().__init__(parent, Qt.WindowType.Dialog)
        self.main_widget    = parent
        self.data           = load_config()
        self._theme         = self.data.get("theme", "dark")
        self._saved_opacity = float(self.data.get("opacity", 0.85))
        self._saved_font    = self.data.get("font", "UnifrakturCook")

        self.setWindowTitle("Settings")
        self.setFixedWidth(310)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self._build_ui()
        self._apply_theme()

    def _build_ui(self):
        g = QGridLayout(self)
        g.setSpacing(6)
        g.setContentsMargins(12, 12, 12, 12)
        g.setColumnStretch(0, 3)
        g.setColumnStretch(1, 1)
        g.setColumnStretch(2, 1)
        g.setColumnStretch(3, 1)
        row = 0

        # Name
        self.name_lbl   = QLabel("Name:")
        self.name_entry = QLineEdit()
        self.name_entry.setPlaceholderText(self.data["user_name"])
        self.name_entry.setFixedHeight(30)
        g.addWidget(self.name_lbl,   row, 0, 1, 4); row += 1
        g.addWidget(self.name_entry, row, 0, 1, 4); row += 1

        # Work hours
        self.hours_lbl   = QLabel("Daily work hours:")
        self.hours_entry = QLineEdit()
        self.hours_entry.setPlaceholderText(str(self.data["work_hours"]))
        self.hours_entry.setFixedHeight(30)
        self.hours_entry.setFixedWidth(60)
        self.fix_cbx = QCheckBox("Use fixed number of hours")
        self.fix_cbx.setChecked(self.data.get("time_mode", 0) == 1)
        self.fix_cbx.stateChanged.connect(self._cbx_callback)
        g.addWidget(self.hours_lbl,   row, 0, 1, 4); row += 1
        g.addWidget(self.hours_entry, row, 0)
        g.addWidget(self.fix_cbx,     row, 1, 1, 3); row += 1

        # Start time
        sh, sm = self.data["start_time"].split(":")
        self.start_lbl = QLabel("Start time:")
        self.start_h   = QLineEdit(); self.start_h.setPlaceholderText(sh); self.start_h.setFixedWidth(50); self.start_h.setFixedHeight(30)
        self.colon1    = QLabel(":"); self.colon1.setAlignment(Qt.AlignmentFlag.AlignCenter); self.colon1.setFixedWidth(12)
        self.start_m   = QLineEdit(); self.start_m.setPlaceholderText(sm); self.start_m.setFixedWidth(50); self.start_m.setFixedHeight(30)
        g.addWidget(self.start_lbl, row, 0, 1, 4); row += 1
        g.addWidget(self.start_h,   row, 0)
        g.addWidget(self.colon1,    row, 1)
        g.addWidget(self.start_m,   row, 2); row += 1

        # End time
        eh, em = self.data["end_time"].split(":")
        self.end_lbl = QLabel("End time:")
        self.end_h   = QLineEdit(); self.end_h.setPlaceholderText(eh); self.end_h.setFixedWidth(50); self.end_h.setFixedHeight(30)
        self.colon2  = QLabel(":"); self.colon2.setAlignment(Qt.AlignmentFlag.AlignCenter); self.colon2.setFixedWidth(12)
        self.end_m   = QLineEdit(); self.end_m.setPlaceholderText(em); self.end_m.setFixedWidth(50); self.end_m.setFixedHeight(30)
        g.addWidget(self.end_lbl, row, 0, 1, 4); row += 1
        g.addWidget(self.end_h,   row, 0)
        g.addWidget(self.colon2,  row, 1)
        g.addWidget(self.end_m,   row, 2); row += 1
        self._set_end_time_enabled(not self.fix_cbx.isChecked())

        # Work days
        self.days_lbl = QLabel("Show progress on:")
        g.addWidget(self.days_lbl, row, 0, 1, 4); row += 1

        work_days = self.data.get("work_days", [1, 2, 3, 4, 5])
        self.day_checks: list[QCheckBox] = []
        days_row = QHBoxLayout()
        days_row.setSpacing(4)
        for i, label in enumerate(DAYS_LABELS):
            cb = QCheckBox(label)
            cb.setChecked((i + 1) in work_days)
            self.day_checks.append(cb)
            days_row.addWidget(cb)
        days_row.addStretch()
        g.addLayout(days_row, row, 0, 1, 4); row += 1

        # Theme toggle
        self.theme_lbl = QLabel("Theme:")
        self.drop_btn  = QPushButton()
        self.drop_btn.setFixedSize(36, 28)
        self.drop_btn.setToolTip("Toggle dark / light theme")
        self.drop_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
        self.drop_btn.clicked.connect(self._toggle_theme)
        g.addWidget(self.theme_lbl, row, 0, 1, 2)
        g.addWidget(self.drop_btn,  row, 3, Qt.AlignmentFlag.AlignRight); row += 1

        # Font selector
        self.font_lbl   = QLabel("Font:")
        self.font_combo = QComboBox()
        self.font_combo.setFixedHeight(30)
        for family in sorted(FONT_FAMILIES.keys()):
            self.font_combo.addItem(family)
        idx = self.font_combo.findText(self.data.get("font", "UnifrakturCook"))
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        self.font_combo.currentTextChanged.connect(self._on_font_change)
        g.addWidget(self.font_lbl,   row, 0, 1, 4); row += 1
        g.addWidget(self.font_combo, row, 0, 1, 4); row += 1

        # Transparency
        self.transp_lbl     = QLabel("Transparency:")
        self.transp_val_lbl = QLabel(f"{int(self._saved_opacity * 100)}%")
        self.transp_val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.transp_slider  = QSlider(Qt.Orientation.Horizontal)
        self.transp_slider.setRange(0, 100)   # 0 = fully transparent
        self.transp_slider.setValue(int(self._saved_opacity * 100))
        self.transp_slider.valueChanged.connect(self._on_transp_change)
        g.addWidget(self.transp_lbl,     row, 0, 1, 2)
        g.addWidget(self.transp_val_lbl, row, 2, 1, 2); row += 1
        g.addWidget(self.transp_slider,  row, 0, 1, 4); row += 1

        # Ok / Cancel
        self.ok_btn     = QPushButton("Ok")
        self.cancel_btn = QPushButton("Cancel")
        self.ok_btn.setFixedHeight(30)
        self.cancel_btn.setFixedHeight(30)
        self.ok_btn.clicked.connect(self._ok_callback)
        self.cancel_btn.clicked.connect(self._cancel_callback)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.ok_btn,     stretch=1)
        btn_row.addWidget(self.cancel_btn, stretch=1)
        g.addLayout(btn_row, row, 0, 1, 4)

    # ── Theme ─────────────────────────────────────────────────────────────────
    def _apply_theme(self):
        t = THEMES[self._theme]
        self.setStyleSheet(_dialog_style(t))
        for lbl in (self.name_lbl, self.hours_lbl, self.start_lbl, self.end_lbl,
                    self.days_lbl, self.theme_lbl, self.font_lbl,
                    self.transp_lbl, self.transp_val_lbl, self.colon1, self.colon2):
            lbl.setStyleSheet(_label_style(t))
        for cb in self.day_checks:
            cb.setStyleSheet(f"color: {t['label_text']}; font-size: 12px; background: transparent;")
        for entry in (self.name_entry, self.hours_entry,
                      self.start_h, self.start_m, self.end_h, self.end_m):
            entry.setStyleSheet(_entry_style(t))
        self.font_combo.setStyleSheet(_combo_style(t))
        self.ok_btn.setStyleSheet(_btn_style(t))
        self.cancel_btn.setStyleSheet(_btn_style(t))
        self.drop_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
        self.drop_btn.setIcon(_icon(t["drop_icon"], 20))

    def _toggle_theme(self):
        self._theme = "light" if self._theme == "dark" else "dark"
        self._apply_theme()
        self.theme_changed.emit(self._theme)

    def _on_font_change(self, family: str):
        self.font_preview.emit(family)

    def _on_transp_change(self, value: int):
        self.transp_val_lbl.setText(f"{value}%")
        self.opacity_preview.emit(value / 100)

    def _set_end_time_enabled(self, enabled: bool):
        self.end_h.setEnabled(enabled)
        self.end_m.setEnabled(enabled)
        self.end_lbl.setEnabled(enabled)

    def _cbx_callback(self, state: int):
        self._set_end_time_enabled(state == 0)

    def _ok_callback(self):
        name      = self.name_entry.text().strip()
        hours_txt = self.hours_entry.text().strip()
        start_h   = self.start_h.text().strip() or self.data["start_time"].split(":")[0]
        start_m   = self.start_m.text().strip() or self.data["start_time"].split(":")[1]
        end_h_v   = self.end_h.text().strip()   or self.data["end_time"].split(":")[0]
        end_m_v   = self.end_m.text().strip()   or self.data["end_time"].split(":")[1]
        use_fixed = self.fix_cbx.isChecked()

        if name:
            self.data["user_name"] = name

        new_hours = int(hours_txt) if (hours_txt and hours_txt.isdigit()) else int(self.data["work_hours"])
        self.data["work_hours"] = new_hours

        try:
            start_dt = datetime.strptime(f"{start_h}:{start_m}", "%H:%M")
            self.data["start_time"] = start_dt.strftime("%H:%M")
        except ValueError:
            start_dt = datetime.strptime(self.data["start_time"], "%H:%M")

        if use_fixed:
            self.data["end_time"] = (start_dt + timedelta(hours=new_hours)).strftime("%H:%M")
        else:
            try:
                end_dt = datetime.strptime(f"{end_h_v}:{end_m_v}", "%H:%M")
                self.data["end_time"] = end_dt.strftime("%H:%M")
            except ValueError:
                pass

        self.data["time_mode"]  = 1 if use_fixed else 0
        self.data["opacity"]    = self.transp_slider.value() / 100
        self.data["theme"]      = self._theme
        self.data["font"]       = self.font_combo.currentText()
        self.data["work_days"]  = [i + 1 for i, cb in enumerate(self.day_checks) if cb.isChecked()]
        save_config(self.data)
        self.accept()

    def _cancel_callback(self):
        self.opacity_preview.emit(self._saved_opacity)
        self.theme_changed.emit(self.data.get("theme", "dark"))
        self.font_preview.emit(self._saved_font)
        self.reject()


# ── Main widget ───────────────────────────────────────────────────────────────
# Heights for the two display modes
HEIGHT_FULL    = 185   # clock + greeting + progress label + bar
HEIGHT_COMPACT = 145   # clock + greeting only

class WorkClockWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(300, HEIGHT_FULL)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self.data        = load_config()
        self._theme_name = self.data.get("theme", "dark")
        self._opacity    = float(self.data.get("opacity", 0.85))
        self._font_name  = self.data.get("font", "UnifrakturCook")
        self._drag_pos   = QPoint()

        self.start_time = datetime.strptime(self.data["start_time"], "%H:%M")
        self.end_time   = datetime.strptime(self.data["end_time"],   "%H:%M")

        self._build_ui()
        self._apply_theme(self._theme_name)
        self._update_shadow()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._last_greeting_hour = -1
        self._tick()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 8, 12, 12)
        outer.setSpacing(2)

        self.clock_lbl = QLabel("00:00")
        self.clock_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self.clock_lbl)

        self.greet_lbl = QLabel("")
        self.greet_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self.greet_lbl)

        self.progress_lbl = QLabel("0%")
        self.progress_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self.progress_lbl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(14)
        outer.addWidget(self.progress_bar)

        self._refresh_fonts()

    def _refresh_fonts(self):
        self.clock_lbl.setFont(QFont(self._font_name, 58))
        self.greet_lbl.setFont(QFont(self._font_name, 20))
        self.progress_lbl.setFont(QFont(self._font_name, 20))

    # ── Show/hide progress based on work day ──────────────────────────────────
    def _update_progress_visibility(self):
        work_days   = self.data.get("work_days", [1, 2, 3, 4, 5])
        today_iso   = datetime.now().isoweekday()   # 1=Mon … 7=Sun
        show        = today_iso in work_days
        self.progress_lbl.setVisible(show)
        self.progress_bar.setVisible(show)
        target_h = HEIGHT_FULL if show else HEIGHT_COMPACT
        if self.height() != target_h:
            self.setFixedSize(300, target_h)

    # ── Text shadow ───────────────────────────────────────────────────────────
    def _update_shadow(self):
        """
        Shadow strength scales with transparency:
        fully opaque (1.0) → subtle shadow (radius 3, alpha 60)
        fully transparent (0.0) → strong shadow (radius 8, alpha 200)
        """
        t          = THEMES[self._theme_name]
        inv        = 1.0 - self._opacity          # 0 opaque → 1 transparent
        radius     = 3 + inv * 5                  # 3 … 8
        alpha      = int(60 + inv * 140)          # 60 … 200
        shadow_col = QColor(t["shadow"])
        shadow_col.setAlpha(alpha)

        for lbl in (self.clock_lbl, self.greet_lbl, self.progress_lbl):
            fx = QGraphicsDropShadowEffect(lbl)
            fx.setBlurRadius(radius)
            fx.setOffset(1, 1)
            fx.setColor(shadow_col)
            lbl.setGraphicsEffect(fx)

    # ── Theme ─────────────────────────────────────────────────────────────────
    def _apply_theme(self, theme_name: str):
        self._theme_name = theme_name
        t = THEMES[theme_name]
        self.clock_lbl.setStyleSheet(   f"color: {t['text']};    background: transparent;")
        self.greet_lbl.setStyleSheet(   f"color: {t['text']};    background: transparent;")
        self.progress_lbl.setStyleSheet(f"color: {t['subtext']}; background: transparent;")
        self.progress_bar.setStyleSheet(f"""
            QProgressBar        {{ background-color: {t['progress_bg']}; border-radius: 7px; }}
            QProgressBar::chunk {{ background-color: {t['progress_fg']}; border-radius: 7px; }}
        """)
        self._update_shadow()
        self.update()

    def set_opacity(self, value: float):
        self._opacity = value
        self._update_shadow()
        self.update()

    def set_font(self, family: str):
        self._font_name = family
        self._refresh_fonts()

    # ── Context menu ──────────────────────────────────────────────────────────
    def _show_context_menu(self, pos: QPoint):
        t = THEMES[self._theme_name]
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {t['dialog_bg']};
                color: {t['label_text']};
                border: 1px solid {t['entry_border']};
                border-radius: 6px; padding: 4px; font-size: 12px;
            }}
            QMenu::item {{ padding: 6px 20px; border-radius: 4px; }}
            QMenu::item:selected {{ background-color: #680000; color: #ffffff; }}
        """)
        settings_action = QAction("⚙  Settings", self)
        close_action    = QAction("✕  Close",    self)
        settings_action.triggered.connect(self._open_settings)
        close_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(close_action)
        menu.exec(self.mapToGlobal(pos))

    # ── Paint ─────────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        if self._opacity <= 0:
            return                              # nothing to draw; fully transparent
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QColor(THEMES[self._theme_name]["bg_color"])
        bg.setAlphaF(self._opacity)
        painter.setBrush(QBrush(bg))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 14, 14)

    # ── Drag ─────────────────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    # ── Tick ─────────────────────────────────────────────────────────────────
    def _tick(self):
        now = datetime.now()
        self.clock_lbl.setText(now.strftime("%H:%M"))

        if now.hour != self._last_greeting_hour:
            self._last_greeting_hour = now.hour
            self.greet_lbl.setText(f"{greeting()}, {self.data['user_name']}")

        self._update_progress_visibility()

        start_min = self.start_time.hour * 60 + self.start_time.minute
        end_min   = self.end_time.hour   * 60 + self.end_time.minute
        now_min   = now.hour * 60 + now.minute
        total     = max(end_min - start_min, 1)
        progress  = max(0, min(100, int((now_min - start_min) * 100 / total)))
        self.progress_lbl.setText(f"{progress}%")
        self.progress_bar.setValue(progress)

    # ── Settings ─────────────────────────────────────────────────────────────
    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.theme_changed.connect(self._apply_theme)
        dlg.opacity_preview.connect(self.set_opacity)
        dlg.font_preview.connect(self.set_font)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.data        = load_config()
            self._theme_name = self.data.get("theme", "dark")
            self._opacity    = float(self.data.get("opacity", 0.85))
            self._font_name  = self.data.get("font", "UnifrakturCook")
            self.start_time  = datetime.strptime(self.data["start_time"], "%H:%M")
            self.end_time    = datetime.strptime(self.data["end_time"],   "%H:%M")
            self._last_greeting_hour = -1
            self._apply_theme(self._theme_name)
            self.set_opacity(self._opacity)
            self.set_font(self._font_name)
            self._tick()


# ── Entry point ───────────────────────────────────────────────────────────────
qapp = QApplication(sys.argv)
load_fonts()
widget = WorkClockWidget()
widget.show()
sys.exit(qapp.exec())
