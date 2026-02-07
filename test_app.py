#!/usr/bin/env python3
"""
Test Script - Factory Manager Pro
Verifica que todos los módulos funcionen correctamente
"""

import os
import sys

# Configurar entorno
os.environ['KIVY_ORIENTATION'] = 'landscape'
os.environ['KIVY_GL_BACKEND'] = 'sdl2'

# Evitar que Kivy abra ventana en tests
os.environ['KIVY_WINDOW'] = 'null'
os.environ['KIVY_TEXT'] = 'pil'

def test_imports():
    """Test 1: Verificar importaciones"""
    print("=" * 60)
    print("TEST 1: Verificando importaciones...")
    print("=" * 60)
    
    try:
        print("✓ Importando Kivy...")
        from kivy.app import App
        from kivy.uix.boxlayout import BoxLayout
        print("✓ Kivy importado correctamente")
        
        print("✓ Importando KivyMD...")
        from kivymd.app import MDApp
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
        from kivymd.uix.list import MDListItem, MDListItemHeadlineText
        print("✓ KivyMD importado correctamente")
        
        print("✓ Importando módulos locales...")
        from modules.database import DatabaseManager
        from modules.pdf_generator import PDFGenerator
        from modules.utils import AppConstants, logger, format_number
        print("✓ Módulos locales importados correctamente")
        
        print("✓ Importando dependencias...")
        from fpdf import FPDF
        from PIL import Image
        print("✓ Dependencias importadas correctamente")
        
        print("\n✅ TEST 1 PASADO: Todas las importaciones funcionan\n")
        return True
        
    except ImportError as e:
        print(f"\n❌ TEST 1 FALLADO: {e}\n")
        return False


def test_database():
    """Test 2: Verificar base de datos"""
    print("=" * 60)
    print("TEST 2: Verificando base de datos...")
    print("=" * 60)
    
    try:
        from modules.database import DatabaseManager
        
        print("✓ Creando instancia de DatabaseManager...")
        db = DatabaseManager()
        
        print("✓ Inicializando base de datos...")
        db.init_database()
        
        print(f"✓ Ruta de BD: {db.db_path}")
        
        print("✓ Obteniendo información de la BD...")
        info = db.get_database_info()
        print(f"  - Tamaño: {info['size']} bytes")
        print(f"  - Tablas: {len(info['tables'])}")
        for table in info['tables']:
            print(f"    - {table['name']}: {table['rows']} filas")
        
        print("✓ Obteniendo estadísticas de producción...")
        stats = db.get_production_stats()
        print(f"  - Total: {stats['total']}")
        print(f"  - Eficiencia: {stats['efficiency']}%")
        print(f"  - Órdenes: {stats['orders']}")
        print(f"  - Defectos: {stats['defect_rate']}%")
        
        print("✓ Obteniendo producción reciente...")
        production = db.get_recent_production(5)
        print(f"  - {len(production)} registros encontrados")
        
        print("✓ Cerrando conexión...")
        db.close()
        
        print("\n✅ TEST 2 PASADO: Base de datos funciona correctamente\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 2 FALLADO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_generation():
    """Test 3: Verificar generación de PDFs"""
    print("=" * 60)
    print("TEST 3: Verificando generación de PDFs...")
    print("=" * 60)
    
    try:
        from modules.pdf_generator import PDFGenerator
        
        print("✓ Creando instancia de PDFGenerator...")
        pdf = PDFGenerator()
        print(f"✓ Directorio de reportes: {pdf.reports_dir}")
        
        print("✓ Generando reporte de producción...")
        data = {
            'title': 'Reporte de Prueba',
            'date': '2024-01-15',
            'productions': [
                (1, 'Línea A - Producto X', 150, '08:00', 'Completado'),
                (2, 'Línea B - Producto Y', 230, '09:30', 'En Proceso'),
                (3, 'Línea C - Producto Z', 89, '10:15', 'Pendiente'),
            ],
            'stats': {
                'total': 469,
                'efficiency': '87%',
                'orders': 42,
                'defects': '1.2%'
            }
        }
        
        filepath = pdf.generate_production_report(data, "test_produccion.pdf")
        print(f"✓ PDF generado: {filepath}")
        
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ Tamaño del PDF: {size} bytes")
            
            # Limpiar archivo de prueba
            os.remove(filepath)
            print("✓ Archivo de prueba eliminado")
        
        print("\n✅ TEST 3 PASADO: Generación de PDFs funciona correctamente\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 3 FALLADO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_utils():
    """Test 4: Verificar utilidades"""
    print("=" * 60)
    print("TEST 4: Verificando utilidades...")
    print("=" * 60)
    
    try:
        from modules.utils import (
            format_number, format_currency, format_datetime,
            get_relative_time, generate_order_number, calculate_efficiency,
            get_status_color, AppConstants, logger
        )
        
        print("✓ Probando format_number...")
        assert format_number(1000) == "1,000"
        assert format_number(1234567.89, 2) == "1,234,567.89"
        print("  - format_number: OK")
        
        print("✓ Probando format_currency...")
        assert format_currency(1234.56) == "$1,234.56"
        print("  - format_currency: OK")
        
        print("✓ Probando format_datetime...")
        from datetime import datetime
        dt = datetime(2024, 1, 15, 10, 30, 0)
        assert format_datetime(dt) == "15/01/2024 10:30"
        print("  - format_datetime: OK")
        
        print("✓ Probando generate_order_number...")
        order_num = generate_order_number()
        assert order_num.startswith("WO-")
        print(f"  - generate_order_number: {order_num}")
        
        print("✓ Probando calculate_efficiency...")
        eff = calculate_efficiency(85, 100)
        assert eff == 85.0
        print(f"  - calculate_efficiency: {eff}%")
        
        print("✓ Probando get_status_color...")
        assert get_status_color('completed') == '#4CAF50'
        assert get_status_color('pending') == '#FF9800'
        print("  - get_status_color: OK")
        
        print("✓ Probando AppConstants...")
        assert AppConstants.APP_NAME == "Factory Manager Pro"
        assert AppConstants.STATUS_COMPLETED == "completed"
        print("  - AppConstants: OK")
        
        print("✓ Probando logger...")
        logger.info("Mensaje de prueba")
        print("  - logger: OK")
        
        print("\n✅ TEST 4 PASADO: Utilidades funcionan correctamente\n")
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST 4 FALLADO: Assertion error: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ TEST 4 FALLADO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_kivy_ui():
    """Test 5: Verificar componentes de UI de KivyMD"""
    print("=" * 60)
    print("TEST 5: Verificando componentes de UI...")
    print("=" * 60)
    
    try:
        from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
        from kivymd.uix.list import (
            MDListItem, MDListItemHeadlineText, 
            MDListItemSupportingText, MDListItemLeadingIcon
        )
        from kivymd.uix.card import MDCard
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
        
        print("✓ Creando MDButton...")
        btn = MDButton(MDButtonText(text="Test"))
        print("  - MDButton: OK")
        
        print("✓ Creando MDTextField...")
        field = MDTextField(MDTextFieldHintText(text="Test"))
        print("  - MDTextField: OK")
        
        print("✓ Creando MDListItem...")
        item = MDListItem(
            MDListItemLeadingIcon(icon="test"),
            MDListItemHeadlineText(text="Test")
        )
        print("  - MDListItem: OK")
        
        print("✓ Creando MDCard...")
        card = MDCard()
        print("  - MDCard: OK")
        
        print("\n✅ TEST 5 PASADO: Componentes de UI funcionan correctamente\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 5 FALLADO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 60)
    print("FACTORY MANAGER PRO - TEST SUITE")
    print("=" * 60 + "\n")
    
    results = []
    
    # Ejecutar tests
    results.append(("Importaciones", test_imports()))
    results.append(("Base de Datos", test_database()))
    results.append(("Generación de PDFs", test_pdf_generation()))
    results.append(("Utilidades", test_utils()))
    results.append(("Componentes de UI", test_kivy_ui()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASADO" if result else "❌ FALLADO"
        print(f"{status}: {name}")
    
    print("-" * 60)
    print(f"Resultado: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON! La aplicación está lista.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron. Revise los errores arriba.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
