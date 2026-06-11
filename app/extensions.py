from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_mail import Mail
from flask_caching import Cache
from flask_limiter import Limiter
import redis as redis_lib

# 初始化扩展（不绑定 app）
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
mail = Mail()
cache = Cache()
limiter = Limiter(key_func=lambda: "global")

# Redis 客户端（延迟初始化）
_redis_client = None


def init_redis(app):
    global _redis_client
    _redis_client = redis_lib.from_url(app.config['REDIS_URL'])


def get_redis_client():
    return _redis_client


# 保持向后兼容的模块级引用
redis_client = _redis_client
