from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
import os

from database import db

jwt = JWTManager()
# 指定 async_mode（可选），并允许跨域
socketio = SocketIO(cors_allowed_origins="*")
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)  # 让 socketio 绑定到 app
    migrate.init_app(app, db)
    CORS(app)

    # 注册蓝图
    from routes.auth import auth_bp
    from routes.events import events_bp
    from routes.chat import chat_bp
    from routes.ai import ai_bp
    from routes.upload import upload_bp
    from routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    # 上传目录
    upload_dir = os.path.join(app.instance_path, app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_dir, exist_ok=True)

    # ⚠️ 生产环境最好用迁移，不建议 create_all()；本地可留
    with app.app_context():
        if os.getenv("ENABLE_CREATE_ALL", "false").lower() == "true":
            db.create_all()

    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'MealBuddy Flask API is running'}

    return app

# 关键：模块级创建 app，给 gunicorn 的 "app:app" 用
app = create_app()

# 仅本地开发直接运行（端口 3001）
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=3001)
