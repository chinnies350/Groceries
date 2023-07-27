from app import create_app

app = create_app()

@app.route('/')
def hello_world():
    return 'Hello World!'

# flask run --host=192.168.1.23 --port=5009


if __name__ == '__main__':
    app.run(host="192.168.1.15",port=6000, debug=True)
    # app.run(host="192.168.1.17",port=6000)

