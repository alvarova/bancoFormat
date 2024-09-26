import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import csv

# Conexión a la base de datos
conn = sqlite3.connect('sql/bancoSantafe.db')
cursor = conn.cursor()

# Crear la ventana principal
root = tk.Tk()
root.title("Browser de Datos")
root.geometry("640x480")

# Variables globales
current_page = 0
items_per_page = 50
selected_ids = set()  # Cambiado a set para una búsqueda más eficiente

# Función para cargar datos
def load_data(page):
    global current_page
    current_page = page
    offset = page * items_per_page
    cursor.execute("SELECT id, Apellido, Nombre, NroDoc, Cuit, Sucur FROM Empleados LIMIT ? OFFSET ?", (items_per_page, offset))
    rows = cursor.fetchall()
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", "end", values=row)

# Función para actualizar datos
def update_data():
    for item in tree.get_children():
        values = tree.item(item, 'values')
        cursor.execute("UPDATE Empleados SET Apellido=?, Nombre=?, NroDoc=?, Cuit=?, Sucur=? WHERE id=?", (values[1], values[2], values[3], values[4], values[5], values[0]))
    conn.commit()
    messagebox.showinfo("Actualización", "Datos actualizados correctamente")

# Función para exportar datos seleccionados a CSV
def export_to_csv():
    with open('selected_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'Apellido', 'Nombre', 'NroDoc', 'Cuit', 'Sucur'])
        for item_id in selected_ids:
            cursor.execute("SELECT id, Apellido, Nombre, NroDoc, Cuit, Sucur FROM Empleados WHERE id=?", (item_id,))
            row = cursor.fetchone()
            if row:
                writer.writerow(row)
    messagebox.showinfo("Exportación", "Datos exportados correctamente")

# Función para manejar la selección de checkboxes
def on_select(event):
    selected_item = tree.focus()
    item_id = tree.item(selected_item, 'values')[0]
    if item_id in selected_ids:
        selected_ids.remove(item_id)
        tree.item(selected_item, tags=())
    else:
        selected_ids.add(item_id)
        tree.item(selected_item, tags=('selected',))

def on_space(event):
    selected_item = tree.focus()
    if selected_item:
        on_select(None)

def clear_selections():
    global selected_ids
    selected_ids.clear()
    for item in tree.get_children():
        tree.item(item, tags=())
    messagebox.showinfo("Limpiar", "Todas las selecciones han sido eliminadas")

# Crear el Treeview
columns = ("id", "Apellido", "Nombre", "NroDoc", "Cuit", "Sucur")
tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
tree.pack(expand=True, fill='both')

# Configurar el estilo para los items seleccionados
style = ttk.Style()
style.configure("Treeview", rowheight=25)
style.map("Treeview", background=[('selected', 'gray')])

# Vincular eventos
tree.bind('<ButtonRelease-1>', on_select)
tree.bind('<space>', on_space)

# Añadir checkboxes
tree.bind('<ButtonRelease-1>', on_select)

# Botones de navegación y acciones
frame = tk.Frame(root)
frame.pack()

prev_button = tk.Button(frame, text="Anterior", command=lambda: load_data(current_page - 1 if current_page > 0 else 0))
prev_button.pack(side='left')

next_button = tk.Button(frame, text="Siguiente", command=lambda: load_data(current_page + 1))
next_button.pack(side='left')

update_button = tk.Button(frame, text="Actualizar", command=update_data)
update_button.pack(side='left')

export_button = tk.Button(frame, text="Descargar", command=export_to_csv)
export_button.pack(side='left')

clear_button = tk.Button(frame, text="Limpiar", command=clear_selections)
clear_button.pack(side=tk.LEFT, padx=5)
# Cargar la primera página de datos


load_data(0)
# Ejecutar la aplicación
root.mainloop()

# Cerrar la conexión a la base de datos
conn.close()