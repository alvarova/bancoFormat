import sqlite3
import os

class GestorUsuarios:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'bancoSantafe.db')
        self.conexion = sqlite3.connect(self.db_path)
        self.cursor = self.conexion.cursor()
        self.crear_tabla()

    def crear_tabla(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        self.conexion.commit()

    def agregar_usuario(self, nombre, apellido, email):
        try:
            self.cursor.execute('''
                INSERT INTO usuarios (nombre, apellido, email)
                VALUES (?, ?, ?)
            ''', (nombre, apellido, email))
            self.conexion.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def obtener_usuarios(self):
        self.cursor.execute('SELECT * FROM usuarios')
        return self.cursor.fetchall()

    def actualizar_usuario(self, id, nombre, apellido, email):
        self.cursor.execute('''
            UPDATE usuarios
            SET nombre = ?, apellido = ?, email = ?
            WHERE id = ?
        ''', (nombre, apellido, email, id))
        self.conexion.commit()
        return self.cursor.rowcount > 0

    def eliminar_usuario(self, id):
        self.cursor.execute('DELETE FROM usuarios WHERE id = ?', (id,))
        self.conexion.commit()
        return self.cursor.rowcount > 0

    def cerrar_conexion(self):
        self.conexion.close()
