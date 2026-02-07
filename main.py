"""
Factory Management App - KivyMD 2.0.1 (Material Design 3)
Compatible con Android 13+ (API 33)
Autor: Senior Kivy/KivyMD Developer
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Configuración de Kivy antes de importar cualquier otra cosa
os.environ['KIVY_ORIENTATION'] = 'landscape'
os.environ['KIVY_GL_BACKEND'] = 'sdl2'

from kivy.config import Config
Config.set('graphics', 'orientation', 'landscape')
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'resizable', '0')

from kivy.core.window import Window
Window.orientation = 'landscape'

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.list import (
    MDList, MDListItem, MDListItemHeadlineText, 
    MDListItemSupportingText, MDListItemLeadingIcon, MDListItemTrailingIcon
)
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.divider import MDDivider
from kivymd.uix.badge import MDBadge
from kivymd.uix.segmentedbutton import (
    MDSegmentedButton, MDSegmentedButtonItem, MDSegmentButtonIcon, MDSegmentButtonLabel
)
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.relativelayout import MDRelativeLayout

# Importar módulos locales
from modules.database import DatabaseManager
from modules.pdf_generator import PDFGenerator

# Detectar plataforma
IS_ANDROID = hasattr(sys, 'getandroidapilevel')

# Manejo de permisos para Android
if IS_ANDROID:
    from android.permissions import (
        request_permissions, check_permission, 
        Permission, request_storage_permission
    )
    from android.storage import app_storage_path
    from android.runnable import run_on_ui_thread
    from jnius import autoclass
    
    # Clases Android necesarias
    Environment = autoclass('android.os.Environment')
    Build = autoclass('android.os.Build')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')


class PermissionManager:
    """Gestor de permisos para Android 13+ (API 33+)"""
    
    def __init__(self, app):
        self.app = app
        self.permissions_granted = False
        
    def check_and_request_permissions(self, callback=None):
        """Verifica y solicita permisos necesarios para Android 13+"""
        if not IS_ANDROID:
            if callback:
                callback(True)
            return
            
        # Permisos necesarios para Android 13+
        permissions_needed = [
            Permission.INTERNET,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE,
        ]
        
        # Para Android 11+ (API 30+) necesitamos MANAGE_EXTERNAL_STORAGE
        if Build.VERSION.SDK_INT >= 30:
            permissions_needed.append(Permission.MANAGE_EXTERNAL_STORAGE)
        
        def on_permissions_result(permissions, results):
            all_granted = all(results)
            self.permissions_granted = all_granted
            
            if not all_granted:
                # Algunos permisos fueron denegados
                denied = [p for p, r in zip(permissions, results) if not r]
                self.show_permission_dialog(denied)
            else:
                self.show_snackbar("Permisos concedidos correctamente", "success")
            
            if callback:
                callback(all_granted)
        
        request_permissions(permissions_needed, on_permissions_result)
    
    def show_permission_dialog(self, denied_permissions):
        """Muestra diálogo explicando por qué se necesitan los permisos"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(20),
            size_hint_y=None,
            height=dp(150)
        )
        
        content.add_widget(
            MDLabel(
                text="La aplicación necesita acceso al almacenamiento para:\n"
                     "• Guardar reportes PDF\n"
                     "• Exportar datos de producción\n"
                     "• Compartir documentos",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(100)
            )
        )
        
        dialog = MDDialog(
            MDDialog.HeadlineText(text="Permisos Requeridos"),
            MDDialog.Content(content),
            MDDialog.ButtonContainer(
                MDButton(
                    MDButtonText(text="CANCELAR"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="CONFIGURACIÓN"),
                    style="text",
                    on_release=lambda x: self.open_app_settings(dialog)
                ),
                spacing=dp(10)
            )
        )
        dialog.open()
    
    def open_app_settings(self, dialog=None):
        """Abre la configuración de la aplicación"""
        if dialog:
            dialog.dismiss()
        
        if IS_ANDROID:
            intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
            uri = Uri.fromParts("package", Context.getPackageName(), None)
            intent.setData(uri)
            Context.startActivity(intent)
    
    def show_snackbar(self, text, style="info"):
        """Muestra un snackbar con el mensaje"""
        colors = {
            "success": "#4CAF50",
            "error": "#F44336",
            "warning": "#FF9800",
            "info": "#2196F3"
        }
        
        MDSnackbar(
            MDSnackbarText(text=text),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
            md_bg_color=colors.get(style, colors["info"])
        ).open()


class LoginScreen(MDScreen):
    """Pantalla de inicio de sesión"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(40),
            md_bg_color=self.theme_cls.surfaceColor
        )
        
        # Logo y título
        header = MDBoxLayout(
            orientation='vertical',
            size_hint_y=0.4,
            spacing=dp(10)
        )
        
        header.add_widget(
            MDLabel(
                text="🏭",
                font_style="Display",
                size_hint_y=None,
                height=dp(80),
                halign="center"
            )
        )
        
        header.add_widget(
            MDLabel(
                text="Factory Manager",
                font_style="Headline",
                size_hint_y=None,
                height=dp(40),
                halign="center",
                theme_text_color="Primary"
            )
        )
        
        header.add_widget(
            MDLabel(
                text="Sistema de Gestión de Producción",
                font_style="Body",
                size_hint_y=None,
                height=dp(24),
                halign="center",
                theme_text_color="Secondary"
            )
        )
        
        layout.add_widget(header)
        
        # Formulario
        form = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            size_hint_y=0.5,
            padding=[dp(100), dp(20), dp(100), dp(20)]
        )
        
        # Campo usuario
        self.username_field = MDTextField(
            MDTextFieldHintText(text="Usuario"),
            mode="outlined",
            icon_left="account",
            size_hint_x=1
        )
        form.add_widget(self.username_field)
        
        # Campo contraseña
        self.password_field = MDTextField(
            MDTextFieldHintText(text="Contraseña"),
            mode="outlined",
            icon_left="lock",
            password=True,
            size_hint_x=1
        )
        form.add_widget(self.password_field)
        
        # Botón login
        login_btn = MDButton(
            MDButtonText(text="INICIAR SESIÓN"),
            style="filled",
            size_hint_x=1,
            height=dp(50),
            on_release=self.do_login
        )
        form.add_widget(login_btn)
        
        layout.add_widget(form)
        
        # Footer
        footer = MDBoxLayout(
            size_hint_y=0.1,
            padding=dp(10)
        )
        footer.add_widget(
            MDLabel(
                text="© 2024 Factory Manager Pro v2.0",
                font_style="Caption",
                halign="center",
                theme_text_color="Tertiary"
            )
        )
        layout.add_widget(footer)
        
        self.add_widget(layout)
    
    def do_login(self, instance):
        """Procesa el login"""
        username = self.username_field.text.strip()
        password = self.password_field.text.strip()
        
        if not username or not password:
            self.show_error("Por favor complete todos los campos")
            return
        
        # Validación simple (en producción usar hash)
        if username == "admin" and password == "admin":
            self.manager.current = "dashboard"
            self.manager.get_screen("dashboard").load_data()
        else:
            self.show_error("Usuario o contraseña incorrectos")
    
    def show_error(self, message):
        """Muestra error en snackbar"""
        MDSnackbar(
            MDSnackbarText(text=message),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
            md_bg_color="#F44336"
        ).open()


class DashboardScreen(MDScreen):
    """Pantalla principal del dashboard"""
    
    production_data = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.pdf_gen = PDFGenerator()
        self.build_ui()
    
    def build_ui(self):
        main_layout = MDBoxLayout(orientation='horizontal')
        
        # Sidebar de navegación
        sidebar = self.create_sidebar()
        main_layout.add_widget(sidebar)
        
        # Contenido principal
        self.content_area = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(16)
        )
        
        # Header
        header = self.create_header()
        self.content_area.add_widget(header)
        
        # Área de contenido dinámico
        self.dynamic_content = MDBoxLayout(orientation='vertical')
        self.content_area.add_widget(self.dynamic_content)
        
        main_layout.add_widget(self.content_area)
        self.add_widget(main_layout)
        
        # Mostrar vista por defecto
        self.show_production_view()
    
    def create_sidebar(self):
        """Crea la barra lateral de navegación"""
        sidebar = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.2,
            md_bg_color=self.theme_cls.surfaceColor,
            padding=dp(8),
            spacing=dp(8)
        )
        
        # Logo
        sidebar.add_widget(
            MDLabel(
                text="🏭 Factory",
                font_style="Title",
                size_hint_y=None,
                height=dp(60),
                halign="center",
                padding=dp(10)
            )
        )
        
        sidebar.add_widget(MDDivider())
        
        # Menú de navegación
        menu_items = [
            ("Producción", "factory", self.show_production_view),
            ("Inventario", "package-variant", self.show_inventory_view),
            ("Reportes", "file-chart", self.show_reports_view),
            ("Configuración", "cog", self.show_settings_view),
        ]
        
        for text, icon, callback in menu_items:
            btn = MDListItem(
                MDListItemLeadingIcon(icon=icon),
                MDListItemHeadlineText(text=text),
                on_release=callback,
                radius=[dp(8),]
            )
            sidebar.add_widget(btn)
        
        # Espaciador
        sidebar.add_widget(MDBoxLayout())
        
        # Botón salir
        logout_btn = MDListItem(
            MDListItemLeadingIcon(icon="logout", theme_icon_color="Error"),
            MDListItemHeadlineText(text="Cerrar Sesión", theme_text_color="Error"),
            on_release=self.logout,
            radius=[dp(8),]
        )
        sidebar.add_widget(logout_btn)
        
        return sidebar
    
    def create_header(self):
        """Crea el header con información y acciones"""
        header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(70),
            spacing=dp(16),
            padding=[dp(16), dp(8)]
        )
        
        # Título y fecha
        title_box = MDBoxLayout(orientation='vertical', size_hint_x=0.6)
        title_box.add_widget(
            MDLabel(
                text="Panel de Control",
                font_style="Headline",
                theme_text_color="Primary"
            )
        )
        title_box.add_widget(
            MDLabel(
                text=datetime.now().strftime("%d/%m/%Y %H:%M"),
                font_style="Body",
                theme_text_color="Secondary"
            )
        )
        header.add_widget(title_box)
        
        # Acciones rápidas
        actions = MDBoxLayout(
            orientation='horizontal',
            size_hint_x=0.4,
            spacing=dp(8),
            halign="right"
        )
        
        # Botón exportar PDF
        export_btn = MDButton(
            MDButtonText(text="EXPORTAR PDF"),
            style="outlined",
            on_release=self.export_to_pdf
        )
        actions.add_widget(export_btn)
        
        # Botón compartir
        share_btn = MDButton(
            MDButtonText(text="COMPARTIR"),
            style="filled",
            on_release=self.share_report
        )
        actions.add_widget(share_btn)
        
        header.add_widget(actions)
        
        return header
    
    def show_production_view(self, *args):
        """Muestra la vista de producción"""
        self.dynamic_content.clear_widgets()
        
        # Grid de estadísticas
        stats_grid = MDGridLayout(
            cols=4,
            spacing=dp(16),
            size_hint_y=None,
            height=dp(120),
            padding=[0, dp(8)]
        )
        
        stats = [
            ("Producción Hoy", "1,250", "units", "#4CAF50"),
            ("Eficiencia", "87%", "+5%", "#2196F3"),
            ("Órdenes", "42", "activas", "#FF9800"),
            ("Defectos", "1.2%", "-0.3%", "#F44336"),
        ]
        
        for title, value, subtitle, color in stats:
            card = MDCard(
                MDBoxLayout(
                    MDLabel(text=title, font_style="Label", theme_text_color="Secondary"),
                    MDLabel(text=value, font_style="Headline", theme_text_color="Primary"),
                    MDLabel(text=subtitle, font_style="Caption", theme_text_color="Tertiary"),
                    orientation='vertical',
                    spacing=dp(4),
                    padding=dp(16)
                ),
                style="filled",
                md_bg_color=color + "15",  # 15 = 10% opacity en hex
                size_hint_y=1,
                radius=[dp(12),]
            )
            stats_grid.add_widget(card)
        
        self.dynamic_content.add_widget(stats_grid)
        
        # Lista de producción reciente
        list_container = MDBoxLayout(orientation='vertical', spacing=dp(8))
        list_container.add_widget(
            MDLabel(
                text="Producción Reciente",
                font_style="Title",
                size_hint_y=None,
                height=dp(40)
            )
        )
        
        scroll = MDScrollView()
        production_list = MDList(spacing=dp(4))
        
        # Datos de ejemplo (en producción vienen de la BD)
        productions = self.db.get_recent_production(10)
        if not productions:
            productions = [
                (1, "Línea A - Producto X", 150, "08:00", "Completado"),
                (2, "Línea B - Producto Y", 230, "09:30", "En Proceso"),
                (3, "Línea C - Producto Z", 89, "10:15", "Pendiente"),
                (4, "Línea A - Producto X", 175, "11:00", "Completado"),
                (5, "Línea D - Producto W", 300, "12:30", "En Proceso"),
            ]
        
        for prod in productions:
            status_colors = {
                "Completado": "green",
                "En Proceso": "blue",
                "Pendiente": "orange"
            }
            
            item = MDListItem(
                MDListItemLeadingIcon(
                    icon="factory",
                    theme_icon_color="Custom",
                    icon_color=self.theme_cls.primaryColor
                ),
                MDListItemHeadlineText(text=prod[1]),
                MDListItemSupportingText(text=f"Cantidad: {prod[2]} | Hora: {prod[3]}"),
                MDListItemTrailingIcon(
                    icon="circle-small",
                    theme_icon_color="Custom",
                    icon_color=status_colors.get(prod[4], "gray")
                ),
                radius=[dp(8),]
            )
            production_list.add_widget(item)
        
        scroll.add_widget(production_list)
        list_container.add_widget(scroll)
        self.dynamic_content.add_widget(list_container)
    
    def show_inventory_view(self, *args):
        """Muestra la vista de inventario"""
        self.dynamic_content.clear_widgets()
        
        self.dynamic_content.add_widget(
            MDLabel(
                text="Gestión de Inventario",
                font_style="Headline",
                size_hint_y=None,
                height=dp(50)
            )
        )
        
        # Formulario de nuevo item
        form_card = MDCard(
            MDBoxLayout(
                MDLabel(text="Nuevo Item", font_style="Title"),
                MDTextField(
                    MDTextFieldHintText(text="Nombre del producto"),
                    mode="outlined"
                ),
                MDTextField(
                    MDTextFieldHintText(text="Cantidad"),
                    mode="outlined",
                    input_filter="int"
                ),
                MDTextField(
                    MDTextFieldHintText(text="Ubicación"),
                    mode="outlined"
                ),
                MDButton(
                    MDButtonText(text="AGREGAR"),
                    style="filled",
                    pos_hint={"right": 1}
                ),
                orientation='vertical',
                spacing=dp(12),
                padding=dp(16)
            ),
            style="elevated",
            size_hint_y=None,
            height=dp(300),
            radius=[dp(12),]
        )
        self.dynamic_content.add_widget(form_card)
    
    def show_reports_view(self, *args):
        """Muestra la vista de reportes"""
        self.dynamic_content.clear_widgets()
        
        self.dynamic_content.add_widget(
            MDLabel(
                text="Reportes y Análisis",
                font_style="Headline",
                size_hint_y=None,
                height=dp(50)
            )
        )
        
        # Opciones de reportes
        reports_grid = MDGridLayout(cols=3, spacing=dp(16))
        
        reports = [
            ("Producción Diaria", "chart-bar", self.generate_daily_report),
            ("Eficiencia", "chart-line", self.generate_efficiency_report),
            ("Defectos", "chart-pie", self.generate_defects_report),
            ("Inventario", "package-variant", self.generate_inventory_report),
            ("Mantenimiento", "wrench", self.generate_maintenance_report),
            ("Personal", "account-group", self.generate_staff_report),
        ]
        
        for title, icon, callback in reports:
            btn = MDButton(
                MDBoxLayout(
                    MDLabel(text=icon, font_style="Display", halign="center"),
                    MDLabel(text=title, font_style="Label", halign="center"),
                    orientation='vertical',
                    spacing=dp(8)
                ),
                style="elevated",
                size_hint_y=None,
                height=dp(120),
                on_release=callback
            )
            reports_grid.add_widget(btn)
        
        self.dynamic_content.add_widget(reports_grid)
    
    def show_settings_view(self, *args):
        """Muestra la vista de configuración"""
        self.dynamic_content.clear_widgets()
        
        self.dynamic_content.add_widget(
            MDLabel(
                text="Configuración",
                font_style="Headline",
                size_hint_y=None,
                height=dp(50)
            )
        )
        
        settings_list = MDList()
        
        settings = [
            ("Notificaciones", "bell", True),
            ("Sincronización automática", "sync", True),
            ("Modo oscuro", "theme-light-dark", False),
            ("Sonidos", "volume-high", True),
        ]
        
        for title, icon, default in settings:
            item = MDListItem(
                MDListItemLeadingIcon(icon=icon),
                MDListItemHeadlineText(text=title),
                MDListItemTrailingIcon(icon="chevron-right"),
                radius=[dp(8),]
            )
            settings_list.add_widget(item)
        
        self.dynamic_content.add_widget(settings_list)
    
    def generate_daily_report(self, *args):
        """Genera reporte diario"""
        self.show_snackbar("Generando reporte diario...")
        # Implementar generación de reporte
    
    def generate_efficiency_report(self, *args):
        """Genera reporte de eficiencia"""
        self.show_snackbar("Generando reporte de eficiencia...")
    
    def generate_defects_report(self, *args):
        """Genera reporte de defectos"""
        self.show_snackbar("Generando reporte de defectos...")
    
    def generate_inventory_report(self, *args):
        """Genera reporte de inventario"""
        self.show_snackbar("Generando reporte de inventario...")
    
    def generate_maintenance_report(self, *args):
        """Genera reporte de mantenimiento"""
        self.show_snackbar("Generando reporte de mantenimiento...")
    
    def generate_staff_report(self, *args):
        """Genera reporte de personal"""
        self.show_snackbar("Generando reporte de personal...")
    
    def export_to_pdf(self, *args):
        """Exporta datos a PDF"""
        try:
            data = {
                'title': 'Reporte de Producción',
                'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'productions': self.db.get_recent_production(50),
                'stats': {
                    'total': 1250,
                    'efficiency': '87%',
                    'orders': 42,
                    'defects': '1.2%'
                }
            }
            
            filepath = self.pdf_gen.generate_production_report(data)
            self.show_snackbar(f"PDF guardado: {filepath}", "success")
            
        except Exception as e:
            self.show_snackbar(f"Error al generar PDF: {str(e)}", "error")
    
    def share_report(self, *args):
        """Comparte el reporte"""
        try:
            data = {
                'title': 'Reporte de Producción',
                'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'productions': self.db.get_recent_production(50),
                'stats': {
                    'total': 1250,
                    'efficiency': '87%',
                    'orders': 42,
                    'defects': '1.2%'
                }
            }
            
            filepath = self.pdf_gen.generate_production_report(data)
            self.pdf_gen.share_pdf(filepath)
            
        except Exception as e:
            self.show_snackbar(f"Error al compartir: {str(e)}", "error")
    
    def load_data(self):
        """Carga los datos iniciales"""
        self.db.init_database()
        self.show_production_view()
    
    def logout(self, *args):
        """Cierra la sesión"""
        self.manager.current = "login"
    
    def show_snackbar(self, text, style="info"):
        """Muestra un snackbar"""
        colors = {
            "success": "#4CAF50",
            "error": "#F44336",
            "info": "#2196F3"
        }
        
        MDSnackbar(
            MDSnackbarText(text=text),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
            md_bg_color=colors.get(style, colors["info"])
        ).open()


class FactoryApp(MDApp):
    """Aplicación principal de Factory Manager"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Amber"
        self.permission_manager = None
    
    def build(self):
        # Forzar orientación landscape
        Window.orientation = 'landscape'
        
        # Crear el gestor de pantallas
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        
        # Inicializar gestor de permisos
        self.permission_manager = PermissionManager(self)
        
        # Solicitar permisos en Android
        if IS_ANDROID:
            Clock.schedule_once(self.request_permissions, 1)
        
        return sm
    
    def request_permissions(self, dt):
        """Solicita permisos al iniciar"""
        self.permission_manager.check_and_request_permissions()
    
    def on_start(self):
        """Se ejecuta al iniciar la app"""
        pass
    
    def on_pause(self):
        """Se ejecuta al pausar la app (Android)"""
        return True
    
    def on_resume(self):
        """Se ejecuta al reanudar la app (Android)"""
        pass


if __name__ == "__main__":
    FactoryApp().run()
