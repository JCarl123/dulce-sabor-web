import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc

# Inicializar la aplicación Flask
app = Flask(__name__)

def obtener_conexion():
    conexion = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'
        'DATABASE=DulceSaborDB;'  # Reemplaza con el nombre real de tu base de datos si es diferente
        'Trusted_connection=yes;'
    )
    return conexion

# Ruta principal (Controlador)
@app.route('/')
def home():
    # Puedes pasar datos dinámicos al front-end usando diccionarios
    titulo = "Proyecto Análisis y Diseño de Sistemas"
    return render_template('index.html', titulo=titulo)


@app.route('/menu.html')
def menu():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT p.id_producto, p.nombre, p.precio_venta, p.stock_actual, c.nombre AS categoria 
        FROM PRODUCTO p 
        INNER JOIN CATEGORIA c ON p.id_categoria = c.id_categoria 
        WHERE p.estado = 'A'
    """)
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    return render_template('menu.html', productos=productos)

# ─── NUEVA RUTA PARA MOSTRAR VENTAS Y SUS DETALLES ───
@app.route('/ventas.html')
def ventas():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # 1. Consultar las ventas realizadas con el cliente y el cajero
        cursor.execute("""
            SELECT v.id_venta, v.fecha, v.total, v.metodo_pago, c.nombre AS cliente, u.nombre AS cajero
            FROM VENTA v
            INNER JOIN CLIENTE c ON v.id_cliente = c.id_cliente
            INNER JOIN USUARIO u ON v.id_usuario = u.id_usuario
            ORDER BY v.id_venta DESC
        """)
        ventas_raw = cursor.fetchall()
        
        # 2. Consultar todos los detalles de venta con el nombre del producto
        cursor.execute("""
            SELECT dv.id_venta, p.nombre AS producto, dv.cantidad, dv.precio_unitario, dv.subtotal
            FROM DETALLE_VENTA dv
            INNER JOIN PRODUCTO p ON dv.id_producto = p.id_producto
        """)
        detalles_raw = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        # Agrupar los detalles según cada id_venta
        ventas_lista = []
        for v in ventas_raw:
            id_v = v[0]
            # Filtrar los detalles correspondientes a esta venta
            detalles_venta = [d for d in detalles_raw if d[0] == id_v]
            ventas_lista.append({
                'id_venta': v[0],
                'fecha': v[1],
                'total': v[2],
                'metodo_pago': v[3],
                'cliente': v[4],
                'cajero': v[5],
                'detalles': detalles_venta
            })
            
    except Exception as e:
        print(f"Error al obtener ventas: {e}")
        ventas_lista = []

    return render_template('ventas.html', ventas=ventas_lista)

# ─── NUEVA RUTA PARA MOSTRAR COMPRAS Y SUS DETALLES ───
@app.route('/compras.html')
def compras():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # 1. Consultar las compras realizadas con Proveedor y Usuario Encargado
        cursor.execute("""
            SELECT c.id_compra, c.fecha, c.total, pr.razon_social AS proveedor, u.nombre AS registrado_por
            FROM COMPRA c
            INNER JOIN PROVEEDOR pr ON c.id_proveedor = pr.id_proveedor
            INNER JOIN USUARIO u ON c.id_usuario = u.id_usuario
            ORDER BY c.id_compra DESC
        """)
        compras_raw = cursor.fetchall()
        
        # 2. Consultar los detalles de compra con el nombre del producto
        cursor.execute("""
            SELECT dc.id_compra, p.nombre AS producto, dc.cantidad, dc.precio_unitario, dc.subtotal
            FROM DETALLE_COMPRA dc
            INNER JOIN PRODUCTO p ON dc.id_producto = p.id_producto
        """)
        detalles_raw = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        # Agrupar detalles por cada id_compra
        compras_lista = []
        for c in compras_raw:
            id_c = c[0]
            detalles_compra = [d for d in detalles_raw if d[0] == id_c]
            compras_lista.append({
                'id_compra': c[0],
                'fecha': c[1],
                'total': c[2],
                'proveedor': c[3],
                'registrado_por': c[4],
                'detalles': detalles_compra
            })
            
    except Exception as e:
        print(f"Error al obtener compras: {e}")
        compras_lista = []

    return render_template('compras.html', compras=compras_lista)

from flask import Flask, render_template, request, redirect, url_for, flash

# ─── RUTA PARA MOVIMIENTOS Y REABASTECIMIENTO DE STOCK ───
@app.route('/movimientos.html', methods=['GET', 'POST'])
def movimientos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Si se envía el formulario para añadir stock
    if request.method == 'POST':
        try:
            id_producto = request.form['id_producto']
            cantidad_sumar = int(request.form['cantidad'])
            motivo = request.form.get('referencia', 'Reabastecimiento manual desde Web')
            id_usuario = 1  # ID del usuario administrador por defecto

            if cantidad_sumar > 0:
                # 1. Incrementar el stock actual en la tabla PRODUCTO
                cursor.execute("""
                    UPDATE PRODUCTO 
                    SET stock_actual = stock_actual + ? 
                    WHERE id_producto = ?
                """, (cantidad_sumar, id_producto))

                # 2. Registrar el movimiento de ENTRADA en la bitácora Kardex
                cursor.execute("""
                    INSERT INTO MOVIMIENTO_INVENTARIO (tipo, cantidad, fecha, referencia, id_producto, id_usuario)
                    VALUES ('ENTRADA', ?, GETDATE(), ?, ?, ?)
                """, (cantidad_sumar, motivo, id_producto, id_usuario))

                # Confirmar la transacción en SQL Server
                conexion.commit()

        except Exception as e:
            conexion.rollback()
            print(f"Error al reabastecer stock: {e}")
        finally:
            cursor.close()
            conexion.close()
        
        return redirect(url_for('movimientos'))

    # Si es una petición GET: Consultar productos para el <select> y los movimientos existentes
    try:
        # Lista de productos para llenar el desplegable del formulario
        cursor.execute("SELECT id_producto, nombre, stock_actual FROM PRODUCTO WHERE estado = 'A' ORDER BY nombre")
        productos_select = cursor.fetchall()

        # Historial de movimientos registrados
        cursor.execute("""
            SELECT m.id_movimiento, m.tipo, m.cantidad, m.fecha, m.referencia, 
                   p.nombre AS producto, u.nombre AS usuario
            FROM MOVIMIENTO_INVENTARIO m
            INNER JOIN PRODUCTO p ON m.id_producto = p.id_producto
            INNER JOIN USUARIO u ON m.id_usuario = u.id_usuario
            ORDER BY m.id_movimiento DESC
        """)
        movimientos_raw = cursor.fetchall()

        movimientos_lista = []
        for m in movimientos_raw:
            movimientos_lista.append({
                'id_movimiento': m[0],
                'tipo': m[1],
                'cantidad': m[2],
                'fecha': m[3],
                'referencia': m[4],
                'producto': m[5],
                'usuario': m[6]
            })

    except Exception as e:
        print(f"Error al obtener movimientos: {e}")
        productos_select = []
        movimientos_lista = []
    finally:
        cursor.close()
        conexion.close()

    return render_template('movimientos.html', movimientos=movimientos_lista, productos_select=productos_select)

# ─── NUEVA RUTA PARA CLIENTES ───
@app.route('/clientes.html')
def clientes():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_cliente, nombre, telefono, documento FROM CLIENTE ORDER BY id_cliente")
        clientes_raw = cursor.fetchall()
        cursor.close()
        conexion.close()
        
        clientes_lista = []
        for c in clientes_raw:
            clientes_lista.append({
                'id_cliente': c[0],
                'nombre': c[1],
                'telefono': c[2],
                'documento': c[3]
            })
    except Exception as e:
        print(f"Error al obtener clientes: {e}")
        clientes_lista = []

    return render_template('clientes.html', clientes=clientes_lista)


# ─── NUEVA RUTA PARA PROVEEDORES ───
@app.route('/proveedores.html')
def proveedores():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_proveedor, razon_social, telefono, direccion FROM PROVEEDOR ORDER BY id_proveedor")
        proveedores_raw = cursor.fetchall()
        cursor.close()
        conexion.close()
        
        proveedores_lista = []
        for p in proveedores_raw:
            proveedores_lista.append({
                'id_proveedor': p[0],
                'razon_social': p[1],
                'telefono': p[2],
                'direccion': p[3]
            })
    except Exception as e:
        print(f"Error al obtener proveedores: {e}")
        proveedores_lista = []

    return render_template('proveedores.html', proveedores=proveedores_lista)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)