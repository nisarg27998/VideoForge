"""
Styling and Theming for VideoForge
"""

class DarkTheme:
    """Dark theme stylesheet provider"""
    
    def __init__(self):
        self.colors = {
            'background': '#2b2b2b',
            'surface': '#404040',
            'surface_variant': '#1e1e1e',
            'primary': '#00A8E8',
            'primary_dark': '#007BB8',
            'secondary': '#4CAF50',
            'accent': '#FFA500',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'text_disabled': '#888888',
            'border': '#555555',
            'error': '#f44336',
            'warning': '#FF9800',
            'success': '#4CAF50'
        }
    
    def get_stylesheet(self) -> str:
        """Get the complete stylesheet"""
        return f"""
        /* Main Window Styling */
        QMainWindow {{
            background-color: {self.colors['background']};
            color: {self.colors['text_primary']};
        }}
        
        QWidget {{
            background-color: {self.colors['background']};
            color: {self.colors['text_primary']};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
        }}
        
        /* Menu Bar */
        QMenuBar {{
            background-color: {self.colors['surface']};
            border-bottom: 1px solid {self.colors['border']};
            padding: 2px;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 12px;
            border-radius: 4px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {self.colors['primary']};
        }}
        
        QMenu {{
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 25px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {self.colors['primary']};
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {self.colors['surface_variant']};
            border-top: 1px solid {self.colors['border']};
            padding: 4px;
        }}
        
        /* Group Boxes */
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {self.colors['border']};
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 15px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px;
            color: {self.colors['primary']};
            font-size: 13px;
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background-color: {self.colors['primary_dark']};
            border-color: {self.colors['primary']};
        }}
        
        QPushButton:pressed {{
            background-color: {self.colors['primary']};
        }}
        
        QPushButton:disabled {{
            background-color: #2a2a2a;
            color: {self.colors['text_disabled']};
            border-color: #333;
        }}
        
        QPushButton:checked {{
            background-color: {self.colors['primary']};
            border-color: {self.colors['primary']};
        }}
        
        /* Input Fields */
        QLineEdit, QSpinBox, QDoubleSpinBox, QTimeEdit {{
            background-color: {self.colors['surface']};
            border: 2px solid {self.colors['border']};
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
        }}
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTimeEdit:focus {{
            border-color: {self.colors['primary']};
        }}
        
        /* Combo Boxes */
        QComboBox {{
            background-color: {self.colors['surface']};
            border: 2px solid {self.colors['border']};
            padding: 8px 12px;
            border-radius: 6px;
            min-width: 120px;
        }}
        
        QComboBox:focus {{
            border-color: {self.colors['primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border: 5px solid transparent;
            border-top: 6px solid {self.colors['text_secondary']};
            margin-right: 5px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            outline: none;
        }}
        
        /* Text Areas */
        QTextEdit, QPlainTextEdit {{
            background-color: {self.colors['surface_variant']};
            border: 2px solid {self.colors['border']};
            border-radius: 6px;
            padding: 8px;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        
        QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {self.colors['primary']};
        }}
        
        /* List Widgets */
        QListWidget {{
            background-color: {self.colors['surface_variant']};
            border: 2px solid {self.colors['border']};
            border-radius: 6px;
            outline: none;
        }}
        
        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {self.colors['border']};
        }}
        
        QListWidget::item:selected {{
            background-color: {self.colors['primary']};
            color: white;
        }}
        
        QListWidget::item:hover {{
            background-color: {self.colors['surface']};
        }}
        
        /* Progress Bars */
        QProgressBar {{
            border: 2px solid {self.colors['border']};
            border-radius: 6px;
            text-align: center;
            background-color: {self.colors['surface']};
            height: 25px;
            font-weight: bold;
        }}
        
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                      stop:0 {self.colors['primary']}, 
                                      stop:1 {self.colors['primary_dark']});
            border-radius: 4px;
            margin: 2px;
        }}
        
        /* Tab Widget */
        QTabWidget::pane {{
            border: 2px solid {self.colors['border']};
            border-radius: 8px;
            background-color: {self.colors['background']};
            margin-top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {self.colors['surface']};
            border: 2px solid {self.colors['border']};
            padding: 12px 24px;
            margin-right: 2px;
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 500;
        }}
        
        QTabBar::tab:selected {{
            background-color: {self.colors['primary']};
            color: white;
            border-color: {self.colors['primary']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {self.colors['primary_dark']};
        }}
        
        /* Checkboxes */
        QCheckBox {{
            spacing: 8px;
            font-size: 12px;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {self.colors['primary']};
            border-color: {self.colors['primary']};
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {self.colors['primary']};
        }}
        
        /* Scroll Bars */
        QScrollBar:vertical {{
            background-color: {self.colors['surface']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {self.colors['border']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {self.colors['primary']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        
        /* Frames */
        QFrame {{
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
            background-color: {self.colors['background']};
        }}
        
        /* Tooltips */
        QToolTip {{
            background-color: {self.colors['surface_variant']};
            color: {self.colors['text_primary']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            padding: 6px;
            font-size: 11px;
        }}
        
        /* Special button styles */
        .start-button {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 {self.colors['primary']}, 
                                      stop:1 {self.colors['primary_dark']});
            border: 2px solid {self.colors['primary']};
            color: white;
            font-weight: bold;
            font-size: 14px;
        }}
        
        .stop-button {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 {self.colors['error']}, 
                                      stop:1 #d32f2f);
            border: 2px solid {self.colors['error']};
            color: white;
        }}
        
        .format-button {{
            font-weight: bold;
            min-height: 35px;
            border-width: 2px;
        }}
        """


class LightTheme(DarkTheme):
    """Light theme variant"""
    
    def __init__(self):
        super().__init__()
        self.colors.update({
            'background': '#f5f5f5',
            'surface': '#ffffff',
            'surface_variant': '#f0f0f0',
            'text_primary': '#212121',
            'text_secondary': '#666666',
            'text_disabled': '#999999',
            'border': '#dddddd'
        })


# Additional utility functions
def get_app_theme() -> DarkTheme:
    """Get the application theme"""
    return DarkTheme()


def apply_button_style(button, style_type: str = "default"):
    """Apply specific button styles"""
    if style_type == "start":
        button.setProperty("class", "start-button")
    elif style_type == "stop":
        button.setProperty("class", "stop-button")
    elif style_type == "format":
        button.setProperty("class", "format-button")