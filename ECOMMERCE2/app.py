from flask import Flask, render_template, request
import db  # Si tienes una clase de base de datos o conexión
from blueprints.cliente.routes import cliente  # Importas el blueprint de cliente

# Crea la aplicación Flask
app = Flask(__name__)
app.secret_key = "clave_secreta"
# Registra el blueprint
app.register_blueprint(cliente, url_prefix="/cliente")

# Ruta principal
@app.route("/")
def index():
    return render_template("login.html")  # Asegúrate de tener un archivo login.html en tu carpeta templates

# Aquí es donde colocas el bloque para ejecutar la app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", use_reloader=True)
