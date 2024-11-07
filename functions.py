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
        cabecera = generar_cabecera79('2894', '0004', today, str(importe_total))        
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

                empresa = str('2894').rjust(4, '0')[:4]
                convenio = str('0004').rjust(4, '0')[:4]
                sistema = str(sistema)[-2:].zfill(2)
                sucursal = str(sucur).rjust(4, '0')[:4]
                cuenta = str(nro_cta).rjust(12, '0')[:12]
                tipo_operacion = str('0002').rjust(4, '0')[:4]
                importe = int(monto * 100)
                importe_str = f"{importe:010d}"
                fecha = today
                comprobante = str(nro_doc).rjust(10, '0')[:10]
                afinidad = str('9999').ljust(4)[:4]
                extracto_limpio = limpiar_texto(f"{apellido}, {nombre}")
                extracto = extracto_limpio.ljust(30, ' ')[:30]

                registro = (f"{empresa}{convenio}{sistema}{sucursal}{cuenta}{tipo_operacion}{importe_str}"
                          f"{fecha}{comprobante}{afinidad}{extracto}")
                registros.append(registro+'0000000000000')
                salelinea = (f"Empresa:{empresa} Convenio:{convenio} Sistema:{sistema} Sucursal:{sucursal} Cuenta:{cuenta} TipoOpera:{tipo_operacion} Importe:{importe_str}"
                          f"Fecha:{fecha} Comprobante:{comprobante} Afinidad:{afinidad} Extracto:{extracto}")
                print(salelinea)                
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













def export_to_txt():
    if not selected_ids:
        messagebox.showwarning("Advertencia", "Necesita seleccionar elementos de la lista para exportar.")
        return
    #Definimos las constantes 
    today = datetime.now()
    año = today.strftime("%Y").rjust(4, '0')   # Año en 4 caracteres
    mes = today.strftime("%m").rjust(2, '0')    # Mes en 2 caracteres
    dia = today.strftime("%d").rjust(2, '0')    # Día en 2 caracteres
    nombre_archivo = f"{today.strftime('%d%m%Y')}_salida.txt"
    
    empresa = '2894'.rjust(4, '0')  # 4 caracteres, valor fijo
    codigo_control = '00'.rjust(2, '0')  # 2 caracteres, valor fijo
    tipo_registro = '02'.rjust(2, '0')  # 2 caracteres, valor fijo
    cierre = '9999'.rjust(4, '0')  # 4 caracteres, valor fijo
    control_adicional = '00000000'.rjust(8, '0')  # 8 caracteres, valor fijo
    id_adicional = '00000'.rjust(5, '0')  # 5 caracteres, valor fijo
    #montoTotal = getTotal()

    with open(nombre_archivo, 'w', newline='') as file:
        # Agregar cabecera al principio del archivo
        #file.seek(0)
        cabecera = generar_cabecera('2894', '0004', today.strftime('%d%m%Y'), 
                                    f"{sum(int(monto * 1000) for monto in selected_ids.values() if monto)}")
        file.write(cabecera)        
        for item_id, monto in selected_ids.items():
            if monto is None or monto == 0:
                continue
            print(monto)
            cursor.execute("SELECT NroCta, Sucur, NroDoc, Sistema, Apellido, Nombre FROM Usuarios WHERE id=?", (item_id,))
            row = cursor.fetchone()
            if row:
                nro_cta_raw, sucur, nro_doc_raw, sistema, apellido, nombre = row
                
                # Limpiar y formatear los datos
                sucursal = str(sucur).rjust(2, '0')  # Asegurar 2 caracteres
                nro_cta = str(sistema).rjust(4, '0')  # Asegurar 4 caracteres
                nro_cta_detallado = limpiar_numeros(nro_cta_raw).rjust(12, '0')  # Asegurar 12 caracteres
                importe = int(monto * 1000)  # Asumiendo que el monto está en milésimas
                importe_str = f"{importe:014d}"  # Asegurar 14 caracteres
                nro_doc = limpiar_numeros(nro_doc_raw).rjust(10, '0')  # Asegurar 10 caracteres
                extracto = limpiar_texto(f"{apellido}, {nombre}").ljust(30, ' ')[:30]  # Asegurar 30 caracteres

                # Combinar todos los campos en una línea respetando la estructura
                linea = (f"{empresa}{sucursal}{nro_cta}{nro_cta_detallado}{tipo_registro}"
                         f"{importe_str}{año}{mes}{dia}{codigo_control}{nro_doc}{sucursal}{cierre}"
                         f"{extracto}{control_adicional}{id_adicional}\r\n")
                file.write(linea)
                salelinea = (f"empresa:{sucursal} nro_cta:{nro_cta} nro_cta_detallado:{nro_cta_detallado} tipo_registro:{tipo_registro}"
                         f" importe_str:{importe_str} fecha:{año}{mes}{dia} codigoCtrl:{codigo_control} NroDoc:{nro_doc} Sucursal:{sucursal} Cierre:{cierre}"
                         f" extracto:{extracto} CtrlAdd:{control_adicional}{id_adicional}\r\n")
                print(salelinea)


    messagebox.showinfo("Exportación", f"Datos exportados correctamente a {nombre_archivo}.")

