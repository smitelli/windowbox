from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/post/<int:post_id>')
def single_post(post_id):
    pass

if __name__ == "__main__":
    app.run()
