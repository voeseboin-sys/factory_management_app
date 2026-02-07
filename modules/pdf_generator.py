"""
PDF Generator Module - Factory Management App
Generación de reportes PDF con fpdf2 y compartir con plyer
Compatible con Android 13+ (API 33)
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# fpdf2 para generación de PDF
from fpdf import FPDF

# Detectar plataforma
IS_ANDROID = hasattr(sys, 'getandroidapilevel')

if IS_ANDROID:
    from android.storage import app_storage_path
    from jnius import autoclass
    
    # Clases Android para compartir
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    FileProvider = autoclass('androidx.core.content.FileProvider')
    Uri = autoclass('android.net.Uri')
    Context = autoclass('android.content.Context')
    Build = autoclass('android.os.Build')


class PDFGenerator:
    """
    Generador de reportes PDF para la aplicación de gestión de fábrica.
    Soporta generación de múltiples tipos de reportes y compartir en Android.
    """
    
    def __init__(self):
        self.reports_dir = self._get_reports_directory()
        self._ensure_directory_exists()
        
        # Configuración de fuentes
        self.font_family = 'Arial'
        self.font_size_normal = 11
        self.font_size_title = 16
        self.font_size_header = 12
    
    def _get_reports_directory(self) -> str:
        """
        Obtiene el directorio para guardar reportes según la plataforma.
        En Android usa el almacenamiento de la app.
        """
        if IS_ANDROID:
            # Usar el directorio de documentos de la app en Android
            storage_path = app_storage_path()
            reports_dir = os.path.join(storage_path, 'reports')
        else:
            # En desktop, usar directorio del proyecto
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            reports_dir = os.path.join(base_dir, 'reports')
        
        return reports_dir
    
    def _ensure_directory_exists(self):
        """Asegura que el directorio de reportes exista"""
        os.makedirs(self.reports_dir, exist_ok=True)
        print(f"[PDF] Directorio de reportes: {self.reports_dir}")
    
    def _generate_filename(self, prefix: str = "report") -> str:
        """Genera un nombre de archivo único para el reporte"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{prefix}_{timestamp}.pdf"
    
    def _get_full_path(self, filename: str) -> str:
        """Obtiene la ruta completa del archivo"""
        return os.path.join(self.reports_dir, filename)
    
    class FactoryPDF(FPDF):
        """Clase personalizada de FPDF para reportes de fábrica"""
        
        def __init__(self, title: str = "Reporte"):
            super().__init__()
            self.report_title = title
            self.set_auto_page_break(auto=True, margin=20)
        
        def header(self):
            """Encabezado del PDF"""
            # Logo o título de la empresa
            self.set_font('Arial', 'B', 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, 'FACTORY MANAGER PRO', 0, 0, 'L')
            
            # Fecha
            self.cell(0, 10, datetime.now().strftime('%d/%m/%Y %H:%M'), 0, 0, 'R')
            self.ln(10)
            
            # Línea separadora
            self.set_draw_color(200, 200, 200)
            self.line(10, 25, 200, 25)
            self.ln(10)
            
            # Título del reporte
            self.set_font('Arial', 'B', 16)
            self.set_text_color(33, 37, 41)
            self.cell(0, 10, self.report_title, 0, 1, 'C')
            self.ln(5)
        
        def footer(self):
            """Pie de página del PDF"""
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
    
    def generate_production_report(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Genera un reporte de producción en PDF.
        
        Args:
            data: Diccionario con datos de producción
            filename: Nombre opcional del archivo
            
        Returns:
            Ruta completa del archivo PDF generado
        """
        if filename is None:
            filename = self._generate_filename("produccion")
        
        filepath = self._get_full_path(filename)
        
        # Crear PDF
        pdf = self.FactoryPDF(title=data.get('title', 'Reporte de Producción'))
        pdf.add_page()
        pdf.set_font(self.font_family, '', self.font_size_normal)
        
        # Información general
        pdf.set_font(self.font_family, 'B', self.font_size_header)
        pdf.cell(0, 10, 'Resumen General', 0, 1)
        pdf.set_font(self.font_family, '', self.font_size_normal)
        
        stats = data.get('stats', {})
        pdf.cell(60, 8, f"Producción Total: {stats.get('total', 0)} unidades", 0, 1)
        pdf.cell(60, 8, f"Eficiencia: {stats.get('efficiency', '0%')}", 0, 1)
        pdf.cell(60, 8, f"Órdenes Activas: {stats.get('orders', 0)}", 0, 1)
        pdf.cell(60, 8, f"Tasa de Defectos: {stats.get('defects', '0%')}", 0, 1)
        pdf.ln(10)
        
        # Tabla de producción
        pdf.set_font(self.font_family, 'B', self.font_size_header)
        pdf.cell(0, 10, 'Detalle de Producción', 0, 1)
        
        # Encabezados de tabla
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font(self.font_family, 'B', 10)
        pdf.cell(80, 8, 'Línea/Producto', 1, 0, 'C', True)
        pdf.cell(30, 8, 'Cantidad', 1, 0, 'C', True)
        pdf.cell(30, 8, 'Hora', 1, 0, 'C', True)
        pdf.cell(50, 8, 'Estado', 1, 1, 'C', True)
        
        # Datos
        pdf.set_font(self.font_family, '', 10)
        productions = data.get('productions', [])
        
        for prod in productions:
            # Manejar tanto diccionarios como tuplas
            if isinstance(prod, dict):
                line = prod.get('line', '')
                quantity = str(prod.get('quantity', 0))
                time = prod.get('time', '')
                status = prod.get('status', '')
            else:
                # Asumir que es una tupla (id, line, quantity, time, status)
                line = prod[1] if len(prod) > 1 else ''
                quantity = str(prod[2]) if len(prod) > 2 else '0'
                time = prod[3] if len(prod) > 3 else ''
                status = prod[4] if len(prod) > 4 else ''
            
            pdf.cell(80, 8, str(line), 1, 0, 'L')
            pdf.cell(30, 8, quantity, 1, 0, 'C')
            pdf.cell(30, 8, str(time), 1, 0, 'C')
            pdf.cell(50, 8, str(status), 1, 1, 'C')
        
        # Guardar PDF
        pdf.output(filepath)
        print(f"[PDF] Reporte generado: {filepath}")
        
        return filepath
    
    def generate_inventory_report(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Genera un reporte de inventario en PDF.
        
        Args:
            data: Diccionario con datos de inventario
            filename: Nombre opcional del archivo
            
        Returns:
            Ruta completa del archivo PDF generado
        """
        if filename is None:
            filename = self._generate_filename("inventario")
        
        filepath = self._get_full_path(filename)
        
        pdf = self.FactoryPDF(title=data.get('title', 'Reporte de Inventario'))
        pdf.add_page()
        pdf.set_font(self.font_family, '', self.font_size_normal)
        
        # Resumen
        pdf.set_font(self.font_family, 'B', self.font_size_header)
        pdf.cell(0, 10, 'Resumen de Inventario', 0, 1)
        pdf.set_font(self.font_family, '', self.font_size_normal)
        
        stats = data.get('stats', {})
        pdf.cell(60, 8, f"Total de Productos: {stats.get('total_products', 0)}", 0, 1)
        pdf.cell(60, 8, f"Valor Total: ${stats.get('total_value', 0):,.2f}", 0, 1)
        pdf.cell(60, 8, f"Stock Bajo: {stats.get('low_stock_count', 0)} items", 0, 1)
        pdf.ln(10)
        
        # Tabla de inventario
        pdf.set_font(self.font_family, 'B', self.font_size_header)
        pdf.cell(0, 10, 'Detalle de Inventario', 0, 1)
        
        # Encabezados
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font(self.font_family, 'B', 9)
        pdf.cell(60, 8, 'Producto', 1, 0, 'C', True)
        pdf.cell(40, 8, 'Código', 1, 0, 'C', True)
        pdf.cell(30, 8, 'Cantidad', 1, 0, 'C', True)
        pdf.cell(30, 8, 'Mínimo', 1, 0, 'C', True)
        pdf.cell(30, 8, 'Ubicación', 1, 1, 'C', True)
        
        # Datos
        pdf.set_font(self.font_family, '', 9)
        items = data.get('items', [])
        
        for item in items:
            if isinstance(item, dict):
                name = item.get('product_name', '')
                code = item.get('product_code', '')
                qty = str(item.get('quantity', 0))
                min_stock = str(item.get('min_stock', 0))
                location = item.get('location', '')
            else:
                name = item[1] if len(item) > 1 else ''
                code = item[2] if len(item) > 2 else ''
                qty = str(item[3]) if len(item) > 3 else '0'
                min_stock = str(item[4]) if len(item) > 4 else '0'
                location = item[5] if len(item) > 5 else ''
            
            # Color de alerta para stock bajo
            if int(qty) <= int(min_stock):
                pdf.set_text_color(220, 53, 69)  # Rojo
            else:
                pdf.set_text_color(0, 0, 0)  # Negro
            
            pdf.cell(60, 8, str(name), 1, 0, 'L')
            pdf.cell(40, 8, str(code), 1, 0, 'C')
            pdf.cell(30, 8, qty, 1, 0, 'C')
            pdf.cell(30, 8, min_stock, 1, 0, 'C')
            pdf.cell(30, 8, str(location), 1, 1, 'C')
        
        pdf.set_text_color(0, 0, 0)  # Reset color
        
        pdf.output(filepath)
        print(f"[PDF] Reporte de inventario generado: {filepath}")
        
        return filepath
    
    def generate_work_order_report(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Genera un reporte de órdenes de trabajo en PDF.
        
        Args:
            data: Diccionario con datos de órdenes
            filename: Nombre opcional del archivo
            
        Returns:
            Ruta completa del archivo PDF generado
        """
        if filename is None:
            filename = self._generate_filename("ordenes_trabajo")
        
        filepath = self._get_full_path(filename)
        
        pdf = self.FactoryPDF(title=data.get('title', 'Reporte de Órdenes de Trabajo'))
        pdf.add_page()
        pdf.set_font(self.font_family, '', self.font_size_normal)
        
        # Resumen
        pdf.set_font(self.font_family, 'B', self.font_size_header)
        pdf.cell(0, 10, 'Resumen de Órdenes', 0, 1)
        pdf.set_font(self.font_family, '', self.font_size_normal)
        
        stats = data.get('stats', {})
        pdf.cell(60, 8, f"Total de Órdenes: {stats.get('total', 0)}", 0, 1)
        pdf.cell(60, 8, f"Pendientes: {stats.get('pending', 0)}", 0, 1)
        pdf.cell(60, 8, f"En Proceso: {stats.get('in_progress', 0)}", 0, 1)
        pdf.cell(60, 8, f"Completadas: {stats.get('completed', 0)}", 0, 1)
        pdf.ln(10)
        
        # Tabla de órdenes
        pdf.set_font(self.font_family, 'B', self.font_size_header)
        pdf.cell(0, 10, 'Detalle de Órdenes', 0, 1)
        
        # Encabezados
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font(self.font_family, 'B', 8)
        pdf.cell(35, 8, 'Orden #', 1, 0, 'C', True)
        pdf.cell(40, 8, 'Producto', 1, 0, 'C', True)
        pdf.cell(25, 8, 'Cantidad', 1, 0, 'C', True)
        pdf.cell(25, 8, 'Producido', 1, 0, 'C', True)
        pdf.cell(25, 8, 'Estado', 1, 0, 'C', True)
        pdf.cell(40, 8, 'Prioridad', 1, 1, 'C', True)
        
        # Datos
        pdf.set_font(self.font_family, '', 8)
        orders = data.get('orders', [])
        
        for order in orders:
            if isinstance(order, dict):
                order_num = order.get('order_number', '')
                product = order.get('product_name', '')
                qty = str(order.get('quantity_requested', 0))
                produced = str(order.get('quantity_produced', 0))
                status = order.get('status', '')
                priority = order.get('priority', '')
            else:
                order_num = order[1] if len(order) > 1 else ''
                product = order[2] if len(order) > 2 else ''
                qty = str(order[3]) if len(order) > 3 else '0'
                produced = str(order[4]) if len(order) > 4 else '0'
                status = order[5] if len(order) > 5 else ''
                priority = order[6] if len(order) > 6 else ''
            
            pdf.cell(35, 8, str(order_num), 1, 0, 'L')
            pdf.cell(40, 8, str(product), 1, 0, 'L')
            pdf.cell(25, 8, qty, 1, 0, 'C')
            pdf.cell(25, 8, produced, 1, 0, 'C')
            pdf.cell(25, 8, str(status), 1, 0, 'C')
            pdf.cell(40, 8, str(priority), 1, 1, 'C')
        
        pdf.output(filepath)
        print(f"[PDF] Reporte de órdenes generado: {filepath}")
        
        return filepath
    
    def generate_custom_report(self, title: str, headers: List[str], 
                               rows: List[List], filename: str = None,
                               column_widths: List[int] = None) -> str:
        """
        Genera un reporte personalizado en PDF.
        
        Args:
            title: Título del reporte
            headers: Lista de encabezados de columnas
            rows: Lista de filas de datos
            filename: Nombre opcional del archivo
            column_widths: Anchos opcionales de columnas
            
        Returns:
            Ruta completa del archivo PDF generado
        """
        if filename is None:
            filename = self._generate_filename("custom")
        
        filepath = self._get_full_path(filename)
        
        pdf = self.FactoryPDF(title=title)
        pdf.add_page(orientation='L' if len(headers) > 5 else 'P')
        pdf.set_font(self.font_family, '', self.font_size_normal)
        
        # Calcular anchos si no se proporcionan
        if column_widths is None:
            page_width = 270 if len(headers) > 5 else 190
            col_width = page_width / len(headers)
            column_widths = [col_width] * len(headers)
        
        # Encabezados
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font(self.font_family, 'B', 9)
        
        for i, header in enumerate(headers):
            pdf.cell(column_widths[i], 8, str(header), 1, 0, 'C', True)
        pdf.ln()
        
        # Datos
        pdf.set_font(self.font_family, '', 9)
        
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(column_widths):
                    align = 'C' if isinstance(cell, (int, float)) else 'L'
                    pdf.cell(column_widths[i], 8, str(cell), 1, 0, align)
            pdf.ln()
        
        pdf.output(filepath)
        print(f"[PDF] Reporte personalizado generado: {filepath}")
        
        return filepath
    
    def share_pdf(self, filepath: str, title: str = "Compartir Reporte") -> bool:
        """
        Comparte el PDF usando las capacidades nativas del sistema.
        En Android usa Intent con FileProvider.
        
        Args:
            filepath: Ruta completa del archivo PDF
            title: Título para el diálogo de compartir
            
        Returns:
            True si se pudo iniciar el compartir, False en caso contrario
        """
        if not os.path.exists(filepath):
            print(f"[PDF ERROR] Archivo no encontrado: {filepath}")
            return False
        
        if IS_ANDROID:
            return self._share_android(filepath, title)
        else:
            return self._share_desktop(filepath)
    
    def _share_android(self, filepath: str, title: str) -> bool:
        """Comparte el PDF en Android usando Intent"""
        try:
            activity = PythonActivity.mActivity
            context = activity.getApplicationContext()
            
            # Obtener el archivo
            file = autoclass('java.io.File')(filepath)
            
            # Obtener URI usando FileProvider
            package_name = context.getPackageName()
            authority = f"{package_name}.fileprovider"
            
            uri = FileProvider.getUriForFile(context, authority, file)
            
            # Crear Intent de compartir
            intent = Intent(Intent.ACTION_SEND)
            intent.setType("application/pdf")
            intent.putExtra(Intent.EXTRA_STREAM, uri)
            intent.putExtra(Intent.EXTRA_SUBJECT, title)
            intent.putExtra(Intent.EXTRA_TEXT, f"Reporte generado el {datetime.now().strftime('%d/%m/%Y')}")
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            
            # Crear chooser
            chooser = Intent.createChooser(intent, title)
            chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            
            # Iniciar actividad
            context.startActivity(chooser)
            
            print(f"[PDF] Compartiendo archivo: {filepath}")
            return True
            
        except Exception as e:
            print(f"[PDF ERROR] Error al compartir en Android: {e}")
            return False
    
    def _share_desktop(self, filepath: str) -> bool:
        """Abre el PDF en el visor predeterminado del sistema (desktop)"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            
            if system == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            elif system == 'Windows':
                os.startfile(filepath)
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
            
            print(f"[PDF] Abriendo archivo: {filepath}")
            return True
            
        except Exception as e:
            print(f"[PDF ERROR] Error al abrir PDF: {e}")
            return False
    
    def get_reports_list(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de reportes generados.
        
        Returns:
            Lista de diccionarios con información de cada reporte
        """
        reports = []
        
        try:
            for filename in os.listdir(self.reports_dir):
                if filename.endswith('.pdf'):
                    filepath = os.path.join(self.reports_dir, filename)
                    stat = os.stat(filepath)
                    
                    reports.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).strftime('%d/%m/%Y %H:%M'),
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M')
                    })
            
            # Ordenar por fecha de creación (más reciente primero)
            reports.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            print(f"[PDF ERROR] Error al listar reportes: {e}")
        
        return reports
    
    def delete_report(self, filename: str) -> bool:
        """
        Elimina un reporte.
        
        Args:
            filename: Nombre del archivo a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        filepath = self._get_full_path(filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"[PDF] Reporte eliminado: {filepath}")
                return True
            else:
                print(f"[PDF ERROR] Archivo no encontrado: {filepath}")
                return False
                
        except Exception as e:
            print(f"[PDF ERROR] Error al eliminar reporte: {e}")
            return False
    
    def clear_old_reports(self, days: int = 30) -> int:
        """
        Elimina reportes antiguos.
        
        Args:
            days: Número de días para considerar un reporte como antiguo
            
        Returns:
            Número de reportes eliminados
        """
        from datetime import timedelta
        
        deleted_count = 0
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            for filename in os.listdir(self.reports_dir):
                if filename.endswith('.pdf'):
                    filepath = os.path.join(self.reports_dir, filename)
                    modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if modified_time < cutoff_date:
                        os.remove(filepath)
                        deleted_count += 1
                        print(f"[PDF] Reporte antiguo eliminado: {filename}")
            
            print(f"[PDF] Total de reportes eliminados: {deleted_count}")
            
        except Exception as e:
            print(f"[PDF ERROR] Error al limpiar reportes: {e}")
        
        return deleted_count
