# flask_mail.py

from flask_mail import Mail, Message


# Configuración de Flask-Mail
def init_mail(app):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Usando Gmail como servidor SMTP
    app.config['MAIL_PORT'] = 587  # Puerto para TLS
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'jesonico258@gmail.com'  # Tu correo electrónico
    app.config['MAIL_PASSWORD'] = 'ghdj xwcs qewj lxea'  # Tu contraseña
    app.config['MAIL_DEFAULT_SENDER'] = 'jesonico258@gmail.com'  # Correo de envío por defecto
    return Mail(app)


# Función para enviar el correo de confirmación de compra
def enviar_correo_confirmacion(app, response, productos_comprados, correo_destino):
    """Envia un correo de confirmación con los detalles de la compra realizada"""

    # Crear el mensaje
    asunto = "Confirmación de Compra - Tu pedido ha sido recibido"
    cuerpo = f"¡Gracias por tu compra!\n\nDetalles de la compra:\n\n"

    # Agregar productos comprados
    for producto in productos_comprados:
        cuerpo += f"- {producto['nombre']} (x{producto['cantidad']}) - ${producto['precio']} c/u\n"

    # Calcular el total
    total = sum([producto['subtotal'] for producto in productos_comprados])
    cuerpo += f"\nTotal: ${total}\n\n"
    cuerpo += "Tu pedido será procesado pronto. ¡Gracias por confiar en nosotros!"

    # Crear el mensaje de correo
    msg = Message(asunto, recipients=[correo_destino])
    msg.body = cuerpo

    try:
        # Inicializar Flask-Mail
        mail = init_mail(app)

        # Enviar el correo
        mail.send(msg)
        print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")