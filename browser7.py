import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from tkinter import StringVar
from tkinter import *
import csv
import math, re
from datetime import datetime


# Definicion de variables globales
# Conexión a la base de datos
conn = sqlite3.connect('db/banco.db')
cursor = conn.cursor()


def init_global_vars():
    global empresa_var, convenio_var
    empresa_var = StringVar(value="2894")
    convenio_var = StringVar(value="4")

# Crear la ventana principal
root = tk.Tk()
root.title("BancoFormat")
root.geometry("940x580")
init_global_vars()



# ******************************
# Variables globales
# *****************************
current_page = 0
items_per_page = 50
selected_ids = {}   # Cambiado a set para una búsqueda más eficiente
export_button = None
selected_items_window = None
empresa_var = None
convenio_var = None




# Actualiza los items en la ventana flotante
def update_selected_items_window():
    global selected_items_window
    
    if selected_items_window is None or not selected_items_window.winfo_exists():
        selected_items_window = tk.Toplevel(root)
        selected_items_window.title("Lista para exportar")
        selected_items_window.geometry("300x400")
        
        global selected_listbox
        selected_listbox = tk.Listbox(selected_items_window, width=40, height=20)
        selected_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        selected_listbox.bind('<Double-1>', remove_selected_item)
        selected_listbox.bind('<ButtonRelease-1>', ask_for_amount)  # Nuevo evento
    
    selected_listbox.delete(0, tk.END)
    for item_id, monto in selected_ids.items():
        cursor.execute("SELECT Apellido, Nombre FROM Usuarios WHERE id=?", (item_id,))
        apellido, nombre = cursor.fetchone()
        monto_str = f" - Monto: {monto}" if monto is not None else ""
        selected_listbox.insert(tk.END, f"{item_id}: {apellido}, {nombre}{monto_str}")

# Funcion para solicitar monto para cada ITEM seleccionado
def ask_for_amount(event):
    index = selected_listbox.nearest(event.y)
    item = selected_listbox.get(index)
    item_id = int(item.split(':')[0])
    
    current_amount = selected_ids.get(item_id, None)
    
    amount = simpledialog.askinteger("Ingresar Monto", 
                                     f"Ingrese el monto para el empleado {item_id}:",
                                     initialvalue=current_amount)
    
    if amount == 0:
            selected_ids.pop(item_id)
            update_selected_items_window()
    elif amount is not None:
        selected_ids[item_id] = amount
        update_selected_items_window()
    


# PAGINADO
# Función para obtener el número total de páginas
def get_total_pages():
    cursor.execute("SELECT COUNT(*) FROM Usuarios")
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
    cursor.execute("SELECT MAX(id) FROM Usuarios")
    max_id = cursor.fetchone()[0]
    return max_id + 1 if max_id else 1

# Funcion para agregar elementos vinculado al boton AGREGAR
def add_or_edit_item(item_id=None):
    # Crear una nueva ventana para el formulario
    form_window = tk.Toplevel(root)
    form_window.title("Agregar nuevo empleado" if item_id is None else "Editar empleado")
    form_window.geometry("300x250")

    # Obtener datos existentes si es una edición
    if item_id is not None:
        cursor.execute("SELECT Apellido, Nombre, NroDoc, Cuit, Sucur, NroCta FROM Usuarios WHERE id=?", (item_id,))
        existing_data = cursor.fetchone()
    else:
        existing_data = [""] * 5

    # Crear y colocar los campos del formulario
    fields = ["Apellido", "Nombre", "NroDoc", "Cuit", "Sucur", "NroCta"]
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
            cursor.execute("INSERT INTO Usuarios (id, Apellido, Nombre, NroDoc, Cuit, Sucur, NroCta) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (new_id, *values))
            message = "Nuevo empleado agregado correctamente"
        else:
            cursor.execute("UPDATE Usuarios SET Apellido=?, Nombre=?, NroDoc=?, Cuit=?, Sucur=?, NroCta=? WHERE id=?",
                           (*values, item_id))
            message = "Empleado actualizado correctamente"
        
        conn.commit()
        messagebox.showinfo("Éxito", message)
        form_window.destroy()
        load_data(current_page)  # Recargar los datos en el Treeview

    # Botón para guardar
    tk.Button(form_window, text="Guardar", command=save_item).pack(pady=10)



# exFunción para agregar un nuevo item, se reemplaza por la funcion AGREGA y Modifica
def add_new_item():
    add_or_edit_item()


def edit_item(event):
    item = tree.selection()[0]
    item_id = tree.item(item, "values")[0]
    add_or_edit_item(item_id)

def update_export_button():
    export_button.config(text=f"Descargar ({len(selected_ids)})")


# Funcion para la busqueda desde inputbox
def search_filter(*args):
    search_text = search_var.get().strip()
    if len(search_text) >= 3:
        if search_text.isdigit():
            query = "SELECT id, Apellido, Nombre, NroDoc, Cuit, Sucur, NroCta FROM Usuarios WHERE Cuit LIKE ? ORDER BY Apellido, Nombre"
            params = ('%' + search_text + '%',)
        else:
            query = "SELECT id, Apellido, Nombre, NroDoc, Cuit, Sucur, NroCta FROM Usuarios WHERE Apellido LIKE ? OR Nombre LIKE ? ORDER BY Apellido, Nombre"
            params = ('%' + search_text + '%', '%' + search_text + '%')
        
        cursor.execute(query, params)
    else:
        cursor.execute("SELECT id, Apellido, Nombre, NroDoc, Cuit, Sucur, NroCta FROM Usuarios ORDER BY Apellido, Nombre LIMIT ? OFFSET ?", (items_per_page, current_page * items_per_page))
    
    rows = cursor.fetchall()
    tree.delete(*tree.get_children())
    for row in rows:
        tree.insert("", "end", values=row, tags=('selected',) if row[0] in selected_ids else ())
    
    update_export_button()



# Función para recargar datos desde la db segun la painga
def load_data(page):
    global current_page
    total_pages = get_total_pages()
    current_page = page
    offset = page * items_per_page
    cursor.execute("SELECT id, Apellido, Nombre, NroDoc, Cuit, Sucur, NroCta FROM Usuarios LIMIT ? OFFSET ?", (items_per_page, offset))
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
        cursor.execute("UPDATE Usuarios SET Apellido=?, Nombre=?, NroDoc=?, Cuit=?, Sucur=?, NroCta=? WHERE id=?", (values[1], values[2], values[3], values[4], values[5], values[0], values[6]))
    conn.commit()
    messagebox.showinfo("Actualización", "Datos actualizados correctamente")




def on_select(event):
    selected_item = tree.focus()
    item_id = int(tree.item(selected_item, 'values')[0])
    if item_id in selected_ids:
        del selected_ids[item_id]
        tree.item(selected_item, tags=())
    else:
        selected_ids[item_id] = None
        tree.item(selected_item, tags=('selected',))
    update_export_button()
    update_selected_items_window()

# Modificar la función de exportación para incluir el monto
def export_to_csvbase():
    with open('selected_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'Apellido', 'Nombre', 'NroDoc', 'Cuit', 'Sucur', 'NroCta', 'Monto'])
        for item_id, monto in selected_ids.items():
            cursor.execute("SELECT id, Apellido, Nombre, NroDoc, Cuit, Sucur, NroCta FROM Usuarios WHERE id=?", (item_id,))
            row = cursor.fetchone()
            if row:
                writer.writerow(list(row) + [monto])
    messagebox.showinfo("Exportación", "Datos exportados correctamente")


def limpiar_numeros(texto):
    return re.sub(r'\D', '', str(texto))

def export_to_csv():
    if not selected_ids:
        messagebox.showwarning("Advertencia", "Necesita seleccionar elementos de la lista para exportar.")
        return

    today = datetime.now().strftime("%d/%m/%Y")
    hoy = datetime.now().strftime("%Y%m%d")
    elementos_exportados = 0
    elementos_no_exportados = 0
    montoTotal = 0
    nombre_archivo = hoy+'_salida_habilitaciones.txt'
    with open(nombre_archivo, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        #writer.writerow(['Empresa', 'Convenio', 'Sistema', 'Sucursal', 'Cuenta', 'TipoOperacion', 'Importe', 'Fecha', 'Comprobante', 'Afinidad', 'Extracto'])
        for item_id, monto in selected_ids.items():
            if monto is None or monto == 0:
                elementos_no_exportados += 1
                continue
            else:
                montoTotal+=monto
            cursor.execute("SELECT NroCta, Sucur, NroDoc, Sistema, Apellido, Nombre FROM Usuarios WHERE id=?", (item_id,))
            row = cursor.fetchone()
            if row:
                nro_ctaRaw, sucur, nro_docRaw, sistema, apellido, nombre = row
                nro_cta = limpiar_numeros(nro_ctaRaw)
                nro_doc = limpiar_numeros(nro_docRaw)
                writer.writerow([
                    '2894',  # Empresa (fijo)
                    '4',     # Convenio (fijo)
                    sistema, # Sistema (asumiendo que es el mismo que Convenio)
                    sucur,   # Sucursal
                    nro_cta, # Cuenta
                    '2',     # TipoOperacion (fijo)
                    monto,   # Importe
                    today,   # Fecha de hoy
                    nro_doc, # Comprobante (NroDoc)
                    '9999',  # Afinidad (fijo)
                    f"{apellido}, {nombre}"  # Extracto (Apellido, Nombre concatenados)
                ])
                elementos_exportados += 1
        cabecera = generar_cabecera('2894','4',today,montoTotal)
    if elementos_exportados > 0:
        with open(nombre_archivo, 'r') as archivo:
            contenido_actual = archivo.read()
        # Escribe la nueva cabecera seguida del contenido original
        with open(nombre_archivo, 'w') as archivo:
            archivo.write(cabecera + contenido_actual)
        mensaje = f"Se exportaron {elementos_exportados} elementos correctamente."
        if elementos_no_exportados > 0:
            mensaje += f"\nNo se exportaron {elementos_no_exportados} elementos por no tener monto definido."
        messagebox.showinfo("Exportación", mensaje)
    else:
        messagebox.showwarning("Advertencia", "No se exportó ningún elemento. Todos los elementos seleccionados tenían monto 0 o no definido.")




def getTotal():
    montoTotal = 0
    for monto in selected_ids.items():
        montoTotal+= monto
    return montoTotal


def limpiar_texto(texto):
    # Eliminar caracteres que no sean letras, espacios, comas o puntos
    texto_limpio = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ ,.]', '', texto)
    return texto_limpio


#Formateo de CABECERA con 119 bytes de salida. Normalizado y corregido. 
def generar_cabecera(empresa, convenio, fecha_envio, importe_total):
    """
    Genera una cabecera con el formato:
    9998|EEEE|CCCC|AAAA|MM|DD|000001|TTTTTTTTTTTTTT + 79 espacios
    Total: 119 caracteres (40 caracteres de datos + 79 espacios)
    """
    # Formatear cada campo con el ancho exacto
    header_id = "9998"                    # 4 caracteres
    empresa = empresa.rjust(4, '0')       # 4 caracteres
    convenio = convenio.rjust(4, '0')     # 4 caracteres
    año = fecha_envio[0:4]                # 4 caracteres
    mes = fecha_envio[4:6]                # 2 caracteres
    dia = fecha_envio[6:8]                # 2 caracteres
    secuencia = "000001"                  # 6 caracteres
    
    # Convertir el importe a entero y multiplicar por 1000
    importe = int(float(importe_total) * 1000)
    importe_str = str(importe).rjust(14, '0')  # 14 caracteres
    
    # Construir la cabecera (40 caracteres de datos)
    datos = f"{header_id}{empresa}{convenio}{año}{mes}{dia}{secuencia}{importe_str}"
    
    # Agregar exactamente 79 espacios en blanco para llegar a 119 caracteres
    cabecera = datos + " " * 79
    
    # Verificación de longitud
    if len(cabecera) != 119:
        print(f"¡Error! Longitud de cabecera: {len(cabecera)}")
        print(f"Datos: {len(datos)} caracteres")
        print(f"Cabecera completa: {cabecera}")
    else:
        print(f"Ok! Longitud de cabecera: {len(cabecera)}")
        
    return cabecera



# Funcion para activar la seleccion de item con la barraespaciadora
def on_space(event):
    selected_item = tree.focus()
    if selected_item:
        on_select(None)


def remove_selected_item(event):
    global selected_ids
    index = selected_listbox.curselection()[0]
    item = selected_listbox.get(index)
    item_id = int(item.split(':')[0])
    
    selected_ids.remove(item_id)
    update_selected_items_window()
    update_export_button()
    
    for tree_item in tree.get_children():
        if tree.item(tree_item, 'values')[0] == str(item_id):
            tree.item(tree_item, tags=())
            break




# Funcion para limpiar todos los elementos del listado
def clear_selections():
    global selected_ids
    selected_ids.clear()
    for item in tree.get_children():
        tree.item(item, tags=())
    update_export_button() 
    update_selected_items_window()
    messagebox.showinfo("Limpiar", "Todas las selecciones han sido eliminadas")




def generar_lotes(sheet, addColumna, empresa, convenio, fecha_envio, valida_digito):
        lotes = []
        lotesNo = []
        row = 7
        cuenta = 0

        while True:
            sistema = str(sheet.cell(row=row, column=1+addColumna).value).zfill(2)
            sucursal = str(sheet.cell(row=row, column=2+addColumna).value).zfill(4)
            nro_cuenta = str(sheet.cell(row=row, column=3+addColumna).value).zfill(12)
            validaCuenta = str(sheet.cell(row=row, column=3+addColumna).value).zfill(9)
            nro_comprobante = str(sheet.cell(row=row, column=4+addColumna).value).zfill(10)
            importe = str(sheet.cell(row=row, column=5+addColumna).value * 1000).zfill(14)
            cuenta += 1

            if valida_digito(sucursal, validaCuenta):
                lote = f"{empresa}{sistema}{sucursal}{nro_cuenta}02{importe}{fecha_envio[0:4]}{fecha_envio[4:6]}{fecha_envio[6:8]}00{nro_comprobante}{convenio}9999"
                lote += " " * 40 + "0000000000000" + "\r\n"
                lotes.append(lote)
            else:
                lotesNo.append(nro_cuenta + "\r\n")

            row += 1
            if sheet.cell(row=row, column=1).value is None:
                break

        return lotes, lotesNo, cuenta


def export_to_fixed_width():
    if not selected_ids:
        messagebox.showwarning("Advertencia", "Necesita seleccionar elementos de la lista para exportar.")
        return

    today = datetime.now().strftime("%d%m%Y")
    elementos_exportados = 0
    elementos_no_exportados = 0
    importe_total = 0
    nombre_archivo = f"{today}_salida.txt"
    
    # Abrimos el archivo en modo binario para control preciso de EOL
    with open(nombre_archivo, 'wb') as file:
        registros = []
        # Generar la cabecera
        importe_total = sum(monto for monto in selected_ids.values() if monto is not None)
        
            # Usar las variables globales
        empresa = empresa_var.get().strip() or "2894"
        convenio = convenio_var.get().strip() or "4"
        cabecera = generar_cabecera(empresa, convenio, today, str(importe_total))
        # Primero procesamos todos los registros
        for item_id, monto in selected_ids.items():
            if monto is None or monto == 0:
                elementos_no_exportados += 1
                continue

            cursor.execute("SELECT NroCta, Sucur, NroDoc, Sistema, Apellido, Nombre FROM Usuarios WHERE id=?", (item_id,))
            row = cursor.fetchone()
            if row:
                nro_ctaRaw, sucur, nro_docRaw, sistema, apellido, nombre = row
                nro_cta = limpiar_numeros(nro_ctaRaw)
                nro_doc = limpiar_numeros(nro_docRaw)



                empresa = empresa.rjust(4, '0')[:4]             # EMPRESA Constante
                sistema = str(sistema)[-2:].zfill(2)            # Sistema CAJA DE AHORRO O CTA CTE
                sucursal = str(sucur).rjust(4, '0')[:4]         # SUCURSAL
                cuenta = str(nro_cta).rjust(12, '0')[:12]
                tipo_operacion = str('02')

                importe = int(monto) * 1000
                importe_str = str(importe).rjust(14, '0')[:14]

                fecha = datetime.now().strftime("%Y%m%d")                           
                codigoControl='00'
                nroDocumento = str(nro_doc).rjust(10, '0')[:10]
                convenio = str('0004').rjust(4, '0')[:4]        # Convenio
                afinidad = str('9999').ljust(4)[:4]             # Codigo de CIERRE
                
                extracto_limpio = limpiar_texto(f"{apellido}, {nombre}")
                nombreApellido = extracto_limpio.ljust(40, ' ')[:40]
                ctrlAdicional = '00000000'
                idAdicional = '00000'


                registro = (f"{empresa}{sistema}{sucursal}{cuenta}{tipo_operacion}{importe_str}"
                          f"{fecha}{codigoControl}{nroDocumento}{convenio}{afinidad}{nombreApellido}{ctrlAdicional}{idAdicional}")

                registros.append(registro)

                print(registro)                
                elementos_exportados += 1
                importe_total += importe

        # Generamos la cabecera (exactamente 118 bytes)
        file.write(cabecera.encode('utf-8'))
        file.write(b'\r\n')
        #cabecera = cabecera.ljust(118)[:118]  # Aseguramos exactamente 118 bytes
        print("Total caracteres cabecera:", len(cabecera))
                
        # Escribimos cada registro + EOL
        for registro in registros:
            print("registro:", len(registro))
            file.write(registro.encode('utf-8'))
            file.write(b'\r\n')

    if elementos_exportados > 0:
        mensaje = f"Se exportaron {elementos_exportados} elementos correctamente."
        if elementos_no_exportados > 0:
            mensaje += f"\nNo se exportaron {elementos_no_exportados} elementos por no tener monto definido."
        messagebox.showinfo("Exportación", mensaje)
    else:
        messagebox.showwarning("Advertencia", "No se exportó ningún elemento. Todos los elementos seleccionados tenían monto 0 o no definido.")







def valida_digito(suc, cta):
        """Valida el dígito verificador de una cuenta bancaria.

        Args:
            suc: Número de sucursal (cadena de 3 dígitos).
            cta: Número de cuenta (cadena de 7 dígitos).

        Returns:
            True si el dígito verificador es correcto, False en caso contrario.
        """
        print("===> In Value Suc/Cta:"+str(suc)+"/"+str(cta))
        def nulo_cero(val):
            return val if val is not None else 0

        cdig = str(cta)[-2:]
        idig = int(cdig)
        print("===> In Value cDig:"+str(cdig))
        suc=suc.zfill(3)   # Formatea sucursal a 3 dígitos
        suc=suc[-3:]
        cta = str(cta).zfill(9)  # Rellenar con ceros a la izquierda hasta 9 dígitos
        cta = cta[:7]          # Tomar los primeros 7 caracteres


        v1 = int(suc[0]) * 9
        v2 = int(suc[1]) * 8
        v3 = int(suc[2]) * 7

        v4 = int(cta[0]) * 8
        v5 = int(cta[1]) * 9
        v6 = int(cta[2]) * 6
        v7 = int(cta[3]) * 5
        v8 = int(cta[4]) * 4
        v9 = int(cta[5]) * 3
        v10 = int(cta[6]) * 2
        print("+SUC:"+suc)
        print("+CTA:"+cta)
        
        vdigito = v1 + v2 + v3 + v4 + v5 + v6 + v7 + v8 + v9 + v10
        
        print("++++"+str(vdigito))
        
        vdigito = 11 - (vdigito % 11)
        
        if vdigito == 11:
            vdigito = 0
        vale = str(vdigito == idig)
        print ("Valida:"+vale)
        return vdigito == idig  



# *********************************
# Definicion de UI e interaccion 
# *********************************


# Crear el Treeview
columns = ("id", "Apellido", "Nombre", "NroDoc", "Cuit", "Sucur", "NroCta")
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



# Frame para Empresa y Convenio (agregar antes del frame de botones)
empresa_convenio_frame = tk.Frame(root)
empresa_convenio_frame.pack()

# Input para Empresa
tk.Label(empresa_convenio_frame, text="Empresa:").pack(side=tk.LEFT, padx=5)
empresa_var = StringVar(value="2894")
empresa_entry = ttk.Entry(empresa_convenio_frame, textvariable=empresa_var, width=10)
empresa_entry.pack(side=tk.LEFT, padx=5)

# Input para Convenio
tk.Label(empresa_convenio_frame, text="Convenio:").pack(side=tk.LEFT, padx=5)
convenio_var = StringVar(value="4")
convenio_entry = ttk.Entry(empresa_convenio_frame, textvariable=convenio_var, width=10)
convenio_entry.pack(side=tk.LEFT, padx=5)


# Botones de navegación y acciones
frame = tk.Frame(root)
frame.pack()

# Cuadro de búsqueda
search_var = StringVar()
search_var.trace_add("write", lambda *args: search_filter())
search_entry = ttk.Entry(frame, textvariable=search_var, width=30)
search_entry.pack(side=tk.LEFT, padx=(10, 5))

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

export_button = tk.Button(frame, text="Descargar", command=export_to_fixed_width)
export_button.pack(side='left')

clear_button = tk.Button(frame, text="Limpiar", command=clear_selections)
clear_button.pack(side=tk.LEFT, padx=5)
# Cargar la primera página de datos


# Menú superior
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Agregar Usuario", command=add_or_edit_item)
filemenu.add_command(label="Actualizar Lista", command=update_data)
filemenu.add_command(label="Descargar", command=export_to_fixed_width)
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