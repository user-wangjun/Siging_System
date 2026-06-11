from flask import Flask
from app.config import config_map
from app.extensions import db, migrate, jwt, ma, mail, cache, limiter, init_redis
from app.utils.exceptions import register_error_handlers


def create_app(config_name='default'):
    app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
    app.config.from_object(config_map[config_name])

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    init_redis(app)

    # 注册 JWT 回调
    register_jwt_callbacks(jwt)

    # 注册错误处理器
    register_error_handlers(app)

    # 注册 Blueprints
    register_blueprints(app)

    return app


def register_jwt_callbacks(jwt_manager):
    """注册 JWT 回调函数"""
    from app.extensions import get_redis_client

    @jwt_manager.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token_key = f"jwt:blacklist:{jti}"
        return get_redis_client().exists(token_key) > 0


def register_blueprints(app):
    from app.api.v1 import auth, user, organization, activity, registration, checkin, notification, admin, template
    from app.web import routes as web_routes

    # API v1
    app.register_blueprint(auth.bp, url_prefix='/api/v1/auth')
    app.register_blueprint(user.bp, url_prefix='/api/v1/users')
    app.register_blueprint(organization.bp, url_prefix='/api/v1/orgs')
    app.register_blueprint(activity.bp, url_prefix='/api/v1/activities')
    app.register_blueprint(registration.bp, url_prefix='/api/v1')
    app.register_blueprint(checkin.bp, url_prefix='/api/v1/checkin')
    app.register_blueprint(notification.bp, url_prefix='/api/v1/notifications')
    app.register_blueprint(admin.bp, url_prefix='/api/v1/admin')
    app.register_blueprint(template.bp, url_prefix='/api/v1/templates')

    # Web 页面
    app.register_blueprint(web_routes.bp)
