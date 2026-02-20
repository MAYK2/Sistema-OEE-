from app import create_app, db

app = create_app()

if __name__ == '__main__':
    # host='0.0.0.0' abre la conexión a toda la red
    # port=5052 es el puerto para este sistema manual
    app.run(host='0.0.0.0', port=5052, debug=False)