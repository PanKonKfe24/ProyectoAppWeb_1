from flask import Flask,render_template,request,redirect,session
import mysql.connector

app = Flask(__name__)
app.secret_key='Clave_De_Seguridad'
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bodega"
    )

@app.route("/")
def Seleccion():
    return render_template("index.html")
 
@app.route("/Registro/Cliente")
def Registroc():
    return render_template("Registro_c.html")

@app.route("/Registro/Administrador")
def Registrod():
    return render_template("Registro_a.html")

@app.route("/Iniciar/Cliente")
def IniciarC():
    return render_template("Iniciar_c.html")

@app.route("/Iniciar/Administrador")
def IniciarA():
    return render_template("Iniciar_a.html")

@app.route("/Registrar_C", methods=["POST"])
def Añadir_C():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tbl_cliente (Numero,Usuario,Password) VALUES (%s,%s,%s)",(request.form["Numero"], request.form["Usuario"],request.form["RepetirContraseña"]))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/Registrar_A",methods=["POST"])
def Añadir_A():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tbl_administrador (Numero,Usuario,Correo,Password) VALUES (%s,%s,%s,%s)",(request.form["Numero"], request.form["Usuario"],request.form["Correo"],request.form["RepetirContraseña"]))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/SesionC",methods=["POST"])
def IniciarSesion_C():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tbl_cliente")
    Clientes = cursor.fetchall()
    conn.close()
    Usuario = request.form.get("Usuario")
    Password = request.form.get("Contraseña")
    for Cliente in Clientes:
        if Usuario==Cliente[1] and Password==Cliente[2]:
            return redirect("/Pagina_C")
    return redirect("/")

@app.route("/Pagina_C")
def Pagina_C():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tbl_inventario")
    datos = cursor.fetchall()
    conn.close()
    if "carrito" not in session:
        session["carrito"] = []
        
    return render_template("Mostrar_C.html", Productos = datos, Carrito=session["carrito"])

@app.route("/AgregarCarrito", methods=["POST"])
def AgregarCarrito():
    Id_producto = request.form["Id_producto"]
    Cantidad = int(request.form[f"Cantidad{Id_producto}"])
    
    producto_en_carrito = next((p for p in session["carrito"] if p["Id"] == Id_producto), None)

    if producto_en_carrito:
        producto_en_carrito["Cantidad"] += Cantidad
    else:
        session["carrito"].append({"Id": Id_producto,"Cantidad":Cantidad})

    session.modified = True
    return redirect("/Pagina_C")

@app.route("/SesionA",methods=["POST"])
def IniciarSesion_A():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tbl_administrador")
    Administradores = cursor.fetchall()
    conn.close()
    Usuario = request.form.get("Usuario")
    Password = request.form.get("Contraseña")
    for Admin in Administradores:
        if Usuario==Admin[1] and Password==Admin[3]:
            return redirect("/Pagina_A")
    return redirect("/")

@app.route("/Pagina_A")
def Pagina_A():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tbl_inventario")
    datos = cursor.fetchall()
    Productos =[
        {
            'Id' : dato[0],
            'Producto' : dato[1],
            'Existencias' : dato[2],
            'Precio' : dato[3],
            'Valor_Stock' : dato[4]
        }
        for dato in datos
    ]
    return render_template("Mostrar_A.html", productos = Productos)

@app.route("/AgregarProducto", methods=["POST"])
def agregar_producto():
    id = request.form["id"]
    producto = request.form["producto"]
    existencias = request.form["existencias"]
    precio = request.form["precio"]
    valorTotalStock = request.form["valorTotalStock"]
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tbl_inventario (ID, Producto, Existencias, Precio, Valor_Stock) VALUES (%s, %s, %s, %s, %s)", 
                   (id, producto, existencias, precio, valorTotalStock))
    conn.commit()
    conn.close()
    
    return redirect("/Pagina_A")

@app.route("/Editar", methods=["POST"])
def editar_producto():
    productoId = request.form["productoId"]
    existencias = request.form["existencias"]
    precio = request.form["precio"]
    valorTotalStock = request.form["valorTotalStock"]
    
    conn = get_db()
    cursor = conn.cursor()
    query = "UPDATE tbl_inventario SET"
    params = []

    if existencias:
        query += " Existencias = %s,"
        params.append(existencias)
    
    if precio:
        query += " Precio = %s,"
        params.append(precio)
    
    if valorTotalStock:
        query += " Valor_Stock = %s,"
        params.append(valorTotalStock)

    query = query.rstrip(',')

    query += " WHERE ID = %s"
    params.append(productoId)

    cursor.execute(query,params)
    conn.commit()
    conn.close()

    return redirect("/Pagina_A")

@app.route("/Eliminar/<ID>")
def Eliminar(ID):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tbl_inventario WHERE ID = %s", (ID,))
    conn.commit()
    conn.close()
    return redirect("/Pagina_A")