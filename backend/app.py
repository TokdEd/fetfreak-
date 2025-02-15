from flask import Flask
from auth import auth_blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允許 React 請求 API
app.config['SECRET_KEY'] = 'your_secret_key'

# 註冊 blueprint (登入 API)
app.register_blueprint(auth_blueprint, url_prefix='/api/auth')

if __name__ == '__main__':
    app.run(debug=True)