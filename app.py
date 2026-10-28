from flask import Flask

from app.database import init_db
from app.routes import bp

app = Flask(__name__)
app.secret_key = "troque-esta-chave-em-producao"
app.register_blueprint(bp)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    init_db()
    app.run(debug=True)