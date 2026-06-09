from flask import Blueprint, render_template

bp = Blueprint('web', __name__)


@bp.route('/')
def index():
    """首页"""
    return render_template('index.html')


@bp.route('/login')
def login_page():
    """登录页"""
    return render_template('auth/login.html')


@bp.route('/activities')
def activities_page():
    """活动列表页"""
    return render_template('activity/list.html')


@bp.route('/activities/<int:activity_id>')
def activity_detail_page(activity_id):
    """活动详情页"""
    return render_template('activity/detail.html', activity_id=activity_id)


@bp.route('/orgs')
def orgs_page():
    """组织列表页"""
    return render_template('org/list.html')


@bp.route('/admin')
def admin_page():
    """运营后台页"""
    return render_template('admin/dashboard.html')


@bp.route('/my/registrations')
def my_registrations_page():
    """我的报名页"""
    return render_template('registration/my.html')
