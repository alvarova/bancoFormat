import sqlite3
import tkinter as tk
from tkinter import messagebox
import csv

# Conectar a la base de datos SQLite
def connect_db():
    return sqlite3.connect('sql/bancoSantafe.db')

# Función para cargar los empleados desde la base de datos
def load_employees():
    with connect_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, Apellido,Nombre, NroDoc, Cuit, Sucur FROM empleados")
        return cursor.fetchall()
    


# Función para actualizar un empleado
def update_employee(emp_id, nombre, dni, tipo_cuenta, numero_cuenta):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE empleados
            SET nombre = ?, dni = ?, tipoCuenta = ?, numeroCuenta = ?
            WHERE id = ?
        """, (nombre, dni, tipo_cuenta, numero_cuenta, emp_id))
        conn.commit()

# Función para exportar empleados seleccionados a CSV
def export_to_csv(selected_employees):
    with open('empleados_exportados.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Nombre', 'DNI', 'Tipo Cuenta', 'Número Cuenta'])
        for emp in selected_employees:
            writer.writerow(emp)
    messagebox.showinfo("Exportar", "Empleados exportados a empleados_exportados.csv")

# Función para mostrar los empleados en la interfaz
def display_employees():
    for widget in frame.winfo_children():
        widget.destroy()

    employees = load_employees()
    for emp in employees:
        emp_id, nombre, dni, tipo_cuenta, numero_cuenta = emp
        var = tk.BooleanVar()
        chk = tk.Checkbutton(frame, variable=var)
        chk.grid(row=emp_id, column=0)

        nombre_entry = tk.Entry(frame)
        nombre_entry.insert(0, nombre)
        nombre_entry.grid(row=emp_id, column=1)

        dni_entry = tk.Entry(frame)
        dni_entry.insert(0, dni)
        dni_entry.grid(row=emp_id, column=2)

        tipo_cuenta_entry = tk.Entry(frame)
        tipo_cuenta_entry.insert(0, tipo_cuenta)
        tipo_cuenta_entry.grid(row=emp_id, column=3)

        numero_cuenta_entry = tk.Entry(frame)
        numero_cuenta_entry.insert(0, numero_cuenta)
        numero_cuenta_entry.grid(row=emp_id, column=4)

        update_button = tk.Button(frame, text="Update", command=lambda id=emp_id: update_employee(id, nombre_entry.get(), dni_entry.get(), tipo_cuenta_entry.get(), numero_cuenta_entry.get()))
        update_button.grid(row=emp_id, column=5)

        # Guardar el estado del checkbox
        chk.config(command=lambda id=emp_id, var=var: selected_employees.append((id, nombre_entry.get(), dni_entry.get(), tipo_cuenta_entry.get(), numero_cuenta_entry.get())) if var.get() else None)

# Función para manejar la exportación
def handle_export():
    selected_employees = [emp for emp in load_employees() if emp[0] in selected_ids]
    export_to_csv(selected_employees)

# Crear la ventana principal
root = tk.Tk()
root.title("Gestión de Empleados")

frame = tk.Frame(root)
frame.pack()

# Botón para cargar y mostrar empleados
load_button = tk.Button(root, text="Cargar Empleados", command=display_employees)
load_button.pack()

# Botón para exportar a CSV
export_button = tk.Button(root, text="Exportar Seleccionados", command=handle_export)
export_button.pack()

# Lista para almacenar los ids seleccionados
selected_ids = []

root.mainloop()