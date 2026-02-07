"""
Database Manager - SQLite3 para Factory Management App
Compatible con Android (persistente en carpeta de la app)
"""

import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

# Detectar plataforma
IS_ANDROID = hasattr(sys, 'getandroidapilevel')

if IS_ANDROID:
    from android.storage import app_storage_path


class DatabaseManager:
    """
    Gestor de base de datos SQLite3 para la aplicación de gestión de fábrica.
    Mantiene persistencia en Android guardando la BD en el almacenamiento de la app.
    """
    
    DB_NAME = "factory_manager.db"
    DB_VERSION = 1
    
    def __init__(self):
        self.db_path = self._get_database_path()
        self.connection = None
        self.cursor = None
        self._init_connection()
    
    def _get_database_path(self) -> str:
        """
        Obtiene la ruta correcta para la base de datos según la plataforma.
        En Android usa el almacenamiento persistente de la app.
        """
        if IS_ANDROID:
            # Usar el directorio de almacenamiento de la app en Android
            storage_path = app_storage_path()
            db_dir = os.path.join(storage_path, 'databases')
        else:
            # En desktop, usar el directorio del script
            db_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Crear directorio si no existe
        os.makedirs(db_dir, exist_ok=True)
        
        return os.path.join(db_dir, self.DB_NAME)
    
    def _init_connection(self):
        """Inicializa la conexión a la base de datos"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            print(f"[DB] Conectado a: {self.db_path}")
        except sqlite3.Error as e:
            print(f"[DB ERROR] Error al conectar: {e}")
            raise
    
    def init_database(self):
        """Inicializa todas las tablas de la base de datos"""
        self._create_tables()
        self._insert_sample_data()
        print("[DB] Base de datos inicializada correctamente")
    
    def _create_tables(self):
        """Crea las tablas necesarias si no existen"""
        
        # Tabla de usuarios
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'operator',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Tabla de líneas de producción
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                capacity_per_hour INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de productos
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                unit TEXT DEFAULT 'units',
                target_production_time INTEGER,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de registros de producción
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                operator_id INTEGER,
                quantity INTEGER NOT NULL,
                defect_count INTEGER DEFAULT 0,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT DEFAULT 'completed',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (line_id) REFERENCES production_lines (id),
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (operator_id) REFERENCES users (id)
            )
        """)
        
        # Tabla de inventario
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                location TEXT,
                quantity INTEGER DEFAULT 0,
                min_stock INTEGER DEFAULT 0,
                max_stock INTEGER DEFAULT 1000,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        # Tabla de movimientos de inventario
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                movement_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                reference_type TEXT,
                reference_id INTEGER,
                notes TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        """)
        
        # Tabla de órdenes de trabajo
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                line_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity_requested INTEGER NOT NULL,
                quantity_produced INTEGER DEFAULT 0,
                priority TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'pending',
                scheduled_start TIMESTAMP,
                scheduled_end TIMESTAMP,
                actual_start TIMESTAMP,
                actual_end TIMESTAMP,
                notes TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (line_id) REFERENCES production_lines (id),
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        """)
        
        # Tabla de mantenimiento
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line_id INTEGER NOT NULL,
                maintenance_type TEXT NOT NULL,
                description TEXT NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                technician TEXT,
                cost REAL,
                status TEXT DEFAULT 'scheduled',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (line_id) REFERENCES production_lines (id)
            )
        """)
        
        # Tabla de configuración
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Índices para mejorar rendimiento
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_production_date 
            ON production_records (created_at)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_production_line 
            ON production_records (line_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_work_orders_status 
            ON work_orders (status)
        """)
        
        self.connection.commit()
    
    def _insert_sample_data(self):
        """Inserta datos de ejemplo si las tablas están vacías"""
        
        # Verificar si ya hay usuarios
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] > 0:
            return
        
        # Usuario admin por defecto (en producción usar hash seguro)
        self.cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
        """, ('admin', 'admin', 'Administrador', 'admin'))
        
        # Líneas de producción
        lines = [
            ('Línea A', 'Línea principal de ensamblaje', 'active', 100),
            ('Línea B', 'Línea secundaria de ensamblaje', 'active', 80),
            ('Línea C', 'Línea de empaque', 'active', 150),
            ('Línea D', 'Línea de calidad', 'maintenance', 50),
        ]
        self.cursor.executemany("""
            INSERT INTO production_lines (name, description, status, capacity_per_hour)
            VALUES (?, ?, ?, ?)
        """, lines)
        
        # Productos
        products = [
            ('PROD-001', 'Producto X Estándar', 'Producto base', 'units', 30),
            ('PROD-002', 'Producto Y Premium', 'Producto alta gama', 'units', 45),
            ('PROD-003', 'Producto Z Compacto', 'Producto compacto', 'units', 25),
            ('PROD-004', 'Producto W Industrial', 'Producto industrial', 'units', 60),
        ]
        self.cursor.executemany("""
            INSERT INTO products (code, name, description, unit, target_production_time)
            VALUES (?, ?, ?, ?, ?)
        """, products)
        
        # Inventario inicial
        self.cursor.execute("SELECT id FROM products")
        product_ids = [row[0] for row in self.cursor.fetchall()]
        
        for prod_id in product_ids:
            self.cursor.execute("""
                INSERT INTO inventory (product_id, location, quantity, min_stock, max_stock)
                VALUES (?, ?, ?, ?, ?)
            """, (prod_id, f'Almacén {prod_id}', 500, 100, 1000))
        
        # Registros de producción de ejemplo
        production_data = [
            (1, 1, 1, 150, 2, '2024-01-15 08:00:00', '2024-01-15 10:30:00', 'completed'),
            (2, 2, 1, 230, 5, '2024-01-15 09:30:00', '2024-01-15 12:00:00', 'completed'),
            (3, 3, 1, 89, 0, '2024-01-15 10:15:00', None, 'in_progress'),
            (1, 1, 1, 175, 3, '2024-01-15 11:00:00', '2024-01-15 13:30:00', 'completed'),
            (2, 4, 1, 300, 8, '2024-01-15 12:30:00', None, 'in_progress'),
        ]
        self.cursor.executemany("""
            INSERT INTO production_records 
            (line_id, product_id, operator_id, quantity, defect_count, start_time, end_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, production_data)
        
        # Órdenes de trabajo
        work_orders = [
            ('WO-2024-001', 1, 1, 500, 150, 'high', 'in_progress', '2024-01-15 08:00:00', '2024-01-15 16:00:00'),
            ('WO-2024-002', 2, 2, 400, 230, 'normal', 'in_progress', '2024-01-15 09:00:00', '2024-01-15 17:00:00'),
            ('WO-2024-003', 3, 3, 600, 89, 'low', 'pending', '2024-01-16 08:00:00', '2024-01-16 16:00:00'),
        ]
        self.cursor.executemany("""
            INSERT INTO work_orders 
            (order_number, line_id, product_id, quantity_requested, quantity_produced, priority, status, scheduled_start, scheduled_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, work_orders)
        
        self.connection.commit()
        print("[DB] Datos de ejemplo insertados")
    
    # ==================== MÉTODOS CRUD ====================
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Ejecuta una consulta SELECT y retorna los resultados"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Query error: {e}")
            return []
    
    def execute_command(self, query: str, params: tuple = ()) -> int:
        """Ejecuta un comando INSERT, UPDATE o DELETE"""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"[DB ERROR] Command error: {e}")
            self.connection.rollback()
            return -1
    
    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """Ejecuta un comando con múltiples parámetros"""
        try:
            self.cursor.executemany(query, params_list)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"[DB ERROR] Batch error: {e}")
            self.connection.rollback()
            return False
    
    # ==================== PRODUCCIÓN ====================
    
    def get_recent_production(self, limit: int = 10) -> List[Tuple]:
        """Obtiene los registros de producción más recientes"""
        query = """
            SELECT 
                pr.id,
                pl.name || ' - ' || p.name as production_line,
                pr.quantity,
                TIME(pr.start_time) as start_time,
                pr.status
            FROM production_records pr
            JOIN production_lines pl ON pr.line_id = pl.id
            JOIN products p ON pr.product_id = p.id
            ORDER BY pr.created_at DESC
            LIMIT ?
        """
        return self.execute_query(query, (limit,))
    
    def get_production_by_date_range(self, start_date: str, end_date: str) -> List[sqlite3.Row]:
        """Obtiene producción por rango de fechas"""
        query = """
            SELECT 
                pr.*,
                pl.name as line_name,
                p.name as product_name,
                p.code as product_code
            FROM production_records pr
            JOIN production_lines pl ON pr.line_id = pl.id
            JOIN products p ON pr.product_id = p.id
            WHERE DATE(pr.created_at) BETWEEN ? AND ?
            ORDER BY pr.created_at DESC
        """
        return self.execute_query(query, (start_date, end_date))
    
    def add_production_record(self, data: Dict[str, Any]) -> int:
        """Agrega un nuevo registro de producción"""
        query = """
            INSERT INTO production_records 
            (line_id, product_id, operator_id, quantity, defect_count, start_time, end_time, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get('line_id'),
            data.get('product_id'),
            data.get('operator_id'),
            data.get('quantity', 0),
            data.get('defect_count', 0),
            data.get('start_time'),
            data.get('end_time'),
            data.get('status', 'completed'),
            data.get('notes', '')
        )
        return self.execute_command(query, params)
    
    def get_production_stats(self, date: str = None) -> Dict[str, Any]:
        """Obtiene estadísticas de producción"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Total producido hoy
        query_total = """
            SELECT COALESCE(SUM(quantity), 0) as total
            FROM production_records
            WHERE DATE(created_at) = ?
        """
        total = self.execute_query(query_total, (date,))[0][0]
        
        # Eficiencia (producción vs defectos)
        query_efficiency = """
            SELECT 
                COALESCE(SUM(quantity), 0) as total,
                COALESCE(SUM(defect_count), 0) as defects
            FROM production_records
            WHERE DATE(created_at) = ?
        """
        result = self.execute_query(query_efficiency, (date,))[0]
        total_prod = result[0]
        defects = result[1]
        efficiency = ((total_prod - defects) / total_prod * 100) if total_prod > 0 else 0
        
        # Órdenes activas
        query_orders = """
            SELECT COUNT(*) as count
            FROM work_orders
            WHERE status IN ('pending', 'in_progress')
        """
        orders = self.execute_query(query_orders)[0][0]
        
        # Tasa de defectos
        defect_rate = (defects / total_prod * 100) if total_prod > 0 else 0
        
        return {
            'total': total,
            'efficiency': round(efficiency, 1),
            'orders': orders,
            'defect_rate': round(defect_rate, 1)
        }
    
    # ==================== INVENTARIO ====================
    
    def get_inventory(self) -> List[sqlite3.Row]:
        """Obtiene todo el inventario"""
        query = """
            SELECT 
                i.*,
                p.name as product_name,
                p.code as product_code
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            ORDER BY p.name
        """
        return self.execute_query(query)
    
    def get_low_stock_items(self) -> List[sqlite3.Row]:
        """Obtiene items con stock bajo"""
        query = """
            SELECT 
                i.*,
                p.name as product_name,
                p.code as product_code
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.quantity <= i.min_stock
            ORDER BY i.quantity ASC
        """
        return self.execute_query(query)
    
    def update_inventory(self, product_id: int, quantity: int, movement_type: str = 'adjustment') -> bool:
        """Actualiza el inventario y registra el movimiento"""
        try:
            # Obtener inventory_id
            self.cursor.execute(
                "SELECT id, quantity FROM inventory WHERE product_id = ?",
                (product_id,)
            )
            result = self.cursor.fetchone()
            
            if not result:
                return False
            
            inventory_id = result[0]
            old_quantity = result[1]
            new_quantity = old_quantity + quantity
            
            # Actualizar inventario
            self.cursor.execute("""
                UPDATE inventory 
                SET quantity = ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_quantity, inventory_id))
            
            # Registrar movimiento
            self.cursor.execute("""
                INSERT INTO inventory_movements 
                (inventory_id, movement_type, quantity, reference_type, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (inventory_id, movement_type, quantity, 'manual', f'Cantidad anterior: {old_quantity}'))
            
            self.connection.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"[DB ERROR] Update inventory error: {e}")
            self.connection.rollback()
            return False
    
    # ==================== ÓRDENES DE TRABAJO ====================
    
    def get_work_orders(self, status: str = None) -> List[sqlite3.Row]:
        """Obtiene órdenes de trabajo"""
        if status:
            query = """
                SELECT 
                    wo.*,
                    pl.name as line_name,
                    p.name as product_name,
                    p.code as product_code
                FROM work_orders wo
                JOIN production_lines pl ON wo.line_id = pl.id
                JOIN products p ON wo.product_id = p.id
                WHERE wo.status = ?
                ORDER BY wo.created_at DESC
            """
            return self.execute_query(query, (status,))
        else:
            query = """
                SELECT 
                    wo.*,
                    pl.name as line_name,
                    p.name as product_name,
                    p.code as product_code
                FROM work_orders wo
                JOIN production_lines pl ON wo.line_id = pl.id
                JOIN products p ON wo.product_id = p.id
                ORDER BY wo.created_at DESC
            """
            return self.execute_query(query)
    
    def create_work_order(self, data: Dict[str, Any]) -> int:
        """Crea una nueva orden de trabajo"""
        query = """
            INSERT INTO work_orders 
            (order_number, line_id, product_id, quantity_requested, priority, 
             scheduled_start, scheduled_end, notes, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get('order_number'),
            data.get('line_id'),
            data.get('product_id'),
            data.get('quantity_requested'),
            data.get('priority', 'normal'),
            data.get('scheduled_start'),
            data.get('scheduled_end'),
            data.get('notes', ''),
            data.get('created_by')
        )
        return self.execute_command(query, params)
    
    def update_work_order_status(self, order_id: int, status: str, quantity_produced: int = None) -> bool:
        """Actualiza el estado de una orden de trabajo"""
        try:
            if quantity_produced is not None:
                self.cursor.execute("""
                    UPDATE work_orders 
                    SET status = ?, quantity_produced = ?,
                        actual_end = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE actual_end END
                    WHERE id = ?
                """, (status, quantity_produced, status, order_id))
            else:
                self.cursor.execute("""
                    UPDATE work_orders 
                    SET status = ?,
                        actual_end = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE actual_end END
                    WHERE id = ?
                """, (status, status, order_id))
            
            self.connection.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"[DB ERROR] Update work order error: {e}")
            self.connection.rollback()
            return False
    
    # ==================== USUARIOS ====================
    
    def validate_user(self, username: str, password: str) -> Optional[sqlite3.Row]:
        """Valida credenciales de usuario"""
        query = """
            SELECT * FROM users 
            WHERE username = ? AND password_hash = ? AND is_active = 1
        """
        result = self.execute_query(query, (username, password))
        
        if result:
            # Actualizar último login
            self.cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?
            """, (username,))
            self.connection.commit()
            return result[0]
        
        return None
    
    def get_users(self) -> List[sqlite3.Row]:
        """Obtiene todos los usuarios"""
        query = "SELECT id, username, full_name, role, is_active, created_at FROM users"
        return self.execute_query(query)
    
    # ==================== UTILIDADES ====================
    
    def get_database_info(self) -> Dict[str, Any]:
        """Obtiene información sobre la base de datos"""
        info = {
            'path': self.db_path,
            'size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0,
            'tables': []
        }
        
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = self.cursor.fetchone()[0]
                info['tables'].append({'name': table_name, 'rows': count})
                
        except sqlite3.Error as e:
            print(f"[DB ERROR] Info error: {e}")
        
        return info
    
    def backup_database(self, backup_path: str = None) -> str:
        """Crea un backup de la base de datos"""
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.dirname(self.db_path)
            backup_path = os.path.join(backup_dir, f'backup_{timestamp}.db')
        
        try:
            backup_conn = sqlite3.connect(backup_path)
            self.connection.backup(backup_conn)
            backup_conn.close()
            print(f"[DB] Backup creado: {backup_path}")
            return backup_path
        except sqlite3.Error as e:
            print(f"[DB ERROR] Backup error: {e}")
            return None
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.connection:
            self.connection.close()
            print("[DB] Conexión cerrada")
    
    def __del__(self):
        """Destructor - cierra la conexión"""
        self.close()
