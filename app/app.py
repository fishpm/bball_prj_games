from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "This is where Fisher's baseball app will be!"

if __name__ == "__main__":
    app.run()
