import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import *
import csv
import math

# Conexión a la base de datos
conn = sqlite3.connect('db/banco.db')
cursor = conn.cursor()

# Crear la ventana principal
root = tk.Tk()
root.title("Browser de Datos")
root.geometry("940x580")





# Variables globales
current_page = 0
items_per_page = 50
selected_ids = set()  # Cambiado a set para una búsqueda más eficiente
export_button = None


# Función para obtener el número total de páginas
def get_total_pages():
    cursor.execute("SELECT COUNT(*) FROM Empleados")
    total_items = cursor.fetchone()[0]
    return math.ceil(total_items / items_per_page)

# Función para ir a la primera página
def go_to_first_page():
    load_data(0)

# Función para ir a la última página
def go_to_last_page():
    total_pages = get_total_pages()
    load_data(total_pages - 1)

def get_next_id():
    cursor.execute("SELECT MAX(id) FROM Empleados")
    max_id = cursor.fetchone()[0]
    return max_id + 1 if max_id else 1


def add_or_edit_item(item_id=None):
    # Crear una nueva ventana para el formulario
    form_window = tk.Toplevel(root)
    form_window.title("Agregar nuevo empleado" if item_id is None else "Editar empleado")
    form_window.geometry("300x250")

    # Obtener datos existentes si es una edición
    if item_id is not None:
        cursor.execute("SELECT Apellido, Nombre, NroDoc, Cuit, Sucur FROM Empleados WHERE id=?", (item_id,))
        existing_data = cursor.fetchone()
    else:
        existing_data = [""] * 5

    # Crear y colocar los campos del formulario
    fields = ["Apellido", "Nombre", "NroDoc", "Cuit", "Sucur"]
    entries = {}

    for i, field in enumerate(fields):
        tk.Label(form_window, text=f"{field}:").pack()
        entry = tk.Entry(form_window)
        entry.insert(0, existing_data[i])
        entry.pack()
        entries[field] = entry

    # Función para guardar el item
    def save_item():
        values = [entries[field].get().upper() for field in fields]
        
        if item_id is None:
            new_id = get_next_id()
            cursor.execute("INSERT INTO Empleados (id, Apellido, Nombre, NroDoc, Cuit, Sucur) VALUES (?, ?, ?, ?, ?, ?)",
                           (new_id, *values))
            message = "Nuevo empleado agregado correctamente"
        else:
            cursor.execute("UPDATE Empleados SET Apellido=?, Nombre=?, NroDoc=?, Cuit=?, Sucur=? WHERE id=?",
                           (*values, item_id))
            message = "Empleado actualizado correctamente"
        
        conn.commit()
        messagebox.showinfo("Éxito", message)
        form_window.destroy()
        load_data(current_page)  # Recargar los datos en el Treeview

    # Botón para guardar
    tk.Button(form_window, text="Guardar", command=save_item).pack(pady=10)




# Función para agregar un nuevo item
def add_new_item():
    add_or_edit_item()


def edit_item(event):
    item = tree.selection()[0]
    item_id = tree.item(item, "values")[0]
    add_or_edit_item(item_id)

def update_export_button():
    export_button.config(text=f"Descargar ({len(selected_ids)})")


# Función para cargar datos
def load_data(page):
    global current_page
    total_pages = get_total_pages()
    current_page = page
    offset = page * items_per_page
    cursor.execute("SELECT id, Apellido, Nombre, NroDoc, Cuit, Sucur FROM Empleados LIMIT ? OFFSET ?", (items_per_page, offset))
    rows = cursor.fetchall()
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", "end", values=row)
    page_label.config(text=f"{current_page + 1} / {total_pages}")

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
    update_export_button()

def on_space(event):
    selected_item = tree.focus()
    if selected_item:
        on_select(None)

def clear_selections():
    global selected_ids
    selected_ids.clear()
    for item in tree.get_children():
        tree.item(item, tags=())
    update_export_button() 
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
tree.bind('<Double-1>', edit_item)  # Doble clic para editar

# Añadir checkboxes
tree.bind('<ButtonRelease-1>', on_select)

# Botones de navegación y acciones
frame = tk.Frame(root)
frame.pack()

add_button = tk.Button(frame, text="Agregar+", command=add_new_item)
add_button.pack(side=tk.LEFT, padx=10)


first_button = tk.Button(frame, text="|<", command=go_to_first_page)
first_button.pack(side='left')

prev_button = tk.Button(frame, text="<", command=lambda: load_data(current_page - 1 if current_page > 0 else 0))
prev_button.pack(side='left')

page_label = tk.Label(frame, text="")
page_label.pack(side='left', padx=10)

next_button = tk.Button(frame, text=">", command=lambda: load_data(current_page + 1))
next_button.pack(side='left')
last_button = tk.Button(frame, text=">|", command=go_to_last_page)
last_button.pack(side='left')

update_button = tk.Button(frame, text="Actualizar", command=update_data)
update_button.pack(side='left')

export_button = tk.Button(frame, text="Descargar", command=export_to_csv)
export_button.pack(side='left')

clear_button = tk.Button(frame, text="Limpiar", command=clear_selections)
clear_button.pack(side=tk.LEFT, padx=5)
# Cargar la primera página de datos


# Menú superior
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Agregar Usuario", command=add_or_edit_item)
filemenu.add_command(label="Actualizar Lista", command=update_data)
filemenu.add_command(label="Descargar", command=export_to_csv)
filemenu.add_command(label="Limpiar", command=clear_selections)
filemenu.add_separator()
filemenu.add_command(label="Salir", command=root.quit)
menubar.add_cascade(label="Archivo", menu=filemenu)

load_data(0)
# Ejecutar la aplicación
root.config(menu=menubar)
root.mainloop()

# Cerrar la conexión a la base de datos
conn.close()