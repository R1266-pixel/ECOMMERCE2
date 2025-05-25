from flask import Flask, render_template, request, session, redirect, url_for
import db
from blueprints.cliente.routes import cliente

app = Flask(__name__)
app.secret_key = "clave_secreta"
app.register_blueprint(cliente, url_prefix="/cliente")
@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip()
        numero_contacto = request.form.get("numero_contacto")
        usuario = db.Cliente.LOGIN(correo, numero_contacto)
        
        if usuario and usuario.get("CORREO") == correo and usuario.get("NUMERO_CONTACTO") == numero_contacto:
            session["cliente_id"] = usuario.get("ID")  # Guardar el ID del cliente en la sesión
            session["correo"] = usuario.get("CORREO", "Correo no encontrado")
            session["role"] = usuario.get("ROLE", "cliente").lower()
            
            # Redirigir según el rol del usuario
            if usuario.get("ROLE", "").lower() == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("cliente_dashboard"))
        else:
            return render_template("login.html", error="Credenciales incorrectas. Por favor, verifica tu correo y número de contacto.")
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        numero = request.form["numero"]
        direccion = {
            "cp": request.form["cp"],
            "cuidad": request.form["cuidad"],
            "calle": request.form["calle"],
            "numero": request.form["numero_depto"]
        }
        cliente = db.Cliente(nombre, numero, correo, direccion)
        cliente.CREATE()
        return redirect(url_for("index"))
    return render_template("registrar.html")

@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        correo = request.form["correo"]
        with db.Database() as cur:
            cur.execute("SELECT * FROM cliente WHERE correo = %s", (correo,))
            usuario = cur.fetchone()
        if usuario:
            return f"Tu contraseña es: {usuario.get('contraseña', 'No registrada')}"
        return "Correo no encontrado."
    return render_template("recuperar.html")
 
#BUSQUEDA DE PRODUCTOS
@app.route("/admin_dashboard", methods=["GET"])
def admin_dashboard():
    productos = db.Producto.READ_ALL()
    busqueda = request.args.get("buscar", "").lower()

    if busqueda:
        productos = [p for p in productos if busqueda in p["NOMBRE"].lower()]

    return render_template("admin_dashboard.html", productos=productos)


@app.route("/cliente_dashboard", methods=["GET"])
def cliente_dashboard():
    productos = db.Producto.READ_ALL()
    busqueda = request.args.get("buscar", "").lower()

    if busqueda:
        productos = [p for p in productos if busqueda in p["NOMBRE"].lower()]

    return render_template("cliente_dashboard.html", productos=productos)


@app.route('/producto', methods=['GET', 'POST'])
def producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        color = request.form['color']
        categoria = request.form['categoria']

        nuevo = db.Producto(precio, color, nombre, categoria)
        nuevo.CREATE()
        return redirect(url_for('producto'))  # Redirige después de insertar

    # GET: mostrar productos + búsqueda
    productos = db.Producto.READ_ALL()
    busqueda = request.args.get("busqueda", "").lower()
    if busqueda:
        productos = [p for p in productos if busqueda in p["NOMBRE"].lower()]

    return render_template("producto.html", productos=productos)
#BUSQUEDA DE PRODUCTOS



   
@app.route('/eliminar_producto/<id>', methods=['GET'])
def eliminar_producto(id):
    db.Producto.DELETE_VENTAS(id)
    db.Producto.DELETE(id)
    
    return redirect(url_for('producto'))

@app.route('/carrito', methods=['GET', 'POST'])
def carrito():
    cliente_id = session.get('cliente_id')  # Obtener el cliente_id de la sesión
    if not cliente_id:
        return redirect(url_for('login'))  # Redirigir al login si no está autenticado

    if request.method == 'POST':
        data = request.get_json()
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad', 1)

        # Insertar o actualizar el producto en la tabla carrito
        try:
            with db.Database() as cur:
                # Verificar si el producto ya está en el carrito
                cur.execute(
                    "SELECT * FROM carrito WHERE cliente_id = %s AND producto_id = %s",
                    (cliente_id, producto_id)
                )
                item = cur.fetchone()

                if item:
                    # Actualizar la cantidad si ya existe
                    cur.execute(
                        "UPDATE carrito SET cantidad = cantidad + %s WHERE cliente_id = %s AND producto_id = %s",
                        (cantidad, cliente_id, producto_id)
                    )
                else:
                    # Insertar un nuevo producto
                    cur.execute(
                        "INSERT INTO carrito (cliente_id, producto_id, cantidad) VALUES (%s, %s, %s)",
                        (cliente_id, producto_id, cantidad)
                    )
            return {'success': True}, 200
        except Exception as e:
            print(f"Error al agregar al carrito: {e}")
            return {'success': False, 'error': 'Error al agregar al carrito'}, 500

    # GET: Recuperar los productos del carrito
    try:
        with db.Database() as cur:
            cur.execute("""
                SELECT p.nombre, p.precio, c.cantidad
                FROM carrito c
                JOIN producto p ON c.producto_id = p.id
                WHERE c.cliente_id = %s
            """, (cliente_id,))
            carrito = cur.fetchall()
        return render_template('carrito.html', carrito=carrito)
    except Exception as e:
        print(f"Error al recuperar el carrito: {e}")
        return render_template('carrito.html', carrito=[])
    

@app.route('/eliminar_del_carrito/<producto_id>', methods=['POST'])
def eliminar_del_carrito(producto_id):
    if 'carrito' in session:
        session['carrito'] = [item for item in session['carrito'] if item['id'] != producto_id]
        session.modified = True

    return redirect(url_for('carrito'))


@app.route('/vaciar_carrito', methods=['POST'])
def vaciar_carrito():
    session.pop('carrito', None)
    return redirect(url_for('carrito'))

@app.route('/historial_ventas')
def ventas():
    return render_template("historial_ventas.html")


if __name__ == "__main__":
    app.run(debug=True)
