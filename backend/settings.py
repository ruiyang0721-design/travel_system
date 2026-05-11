"""
Django 项目配置文件
==================
配置项目的全局设置，包括：
- 数据库连接（MySQL）
- 已安装的应用（SimpleUI、DRF、CORS 等）
- 中间件配置
- JWT 认证配置
- SimpleUI 管理后台美化主题
- CORS 跨域配置
- 国际化和时区设置
"""

from pathlib import Path

# 项目根目录路径
BASE_DIR = Path(__file__).resolve().parent.parent

# Django 安全密钥（生产环境应使用环境变量，不要硬编码）
SECRET_KEY = 'django-insecure-o5=#har^wbf3hbi#v&y0vsxd9@v(vsd&ncqvo609gukqi2bw4c'

# 调试模式开关（生产环境必须设为 False）
DEBUG = True

# 允许访问的主机列表（空表示只允许 localhost）
ALLOWED_HOSTS = []


# ==================== 已安装的应用 ====================
INSTALLED_APPS = [
    'simpleui',            # Django SimpleUI 管理后台主题（必须在 admin 之前注册）
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',      # Django REST Framework：构建 RESTful API 的核心框架
    'corsheaders',         # django-cors-headers：解决前后端分离的跨域问题
    'backend.api',         # 业务应用：包含模型、视图、算法引擎等
]


# ==================== 中间件配置 ====================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS 中间件：处理跨域请求头
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# ==================== 数据库配置 ====================
# 使用 MySQL 数据库，字符集 utf8mb4 支持中文和 Emoji
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'travel_system',      # 数据库名
        'USER': 'root',               # 用户名
        'PASSWORD': '123456',         # 密码
        'HOST': '127.0.0.1',          # 主机地址
        'PORT': '3306',               # 端口号
        'OPTIONS': {
            'charset': 'utf8mb4',     # 支持中文和特殊字符
        },
    }
}


# ==================== 密码验证规则 ====================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==================== 国际化和时区 ====================
LANGUAGE_CODE = 'zh-hans'        # 使用简体中文
TIME_ZONE = 'Asia/Shanghai'      # 时区设为上海
USE_I18N = True                  # 启用国际化
USE_TZ = True                    # 启用时区感知


# ==================== 静态文件 ====================
STATIC_URL = 'static/'

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== CORS 跨域配置 ====================
# 开发环境允许所有来源访问（生产环境应限制为前端域名）
CORS_ALLOW_ALL_ORIGINS = True


# ==================== SimpleUI 管理后台配置 ====================
# 隐藏右侧 SimpleUI 广告链接
SIMPLEUI_HOME_INFO = False
# 使用本地离线静态文件（不加载 CDN，避免网络问题）
SIMPLEUI_STATIC_OFFLINE = True
# 默认主题风格
SIMPLEUI_DEFAULT_THEME = 'simpleui.css'
# 首页链接（留空则使用 Django 默认管理首页）
SIMPLEUI_INDEX = ''
# 显示快捷操作和服务器信息
SIMPLEUI_HOME_QUICK = True
SIMPLEUI_HOME_ACTION = True

# 自定义管理后台左侧菜单
SIMPLEUI_CONFIG = {
    'system_keep': False,  # 不使用系统默认菜单，完全自定义
    'menus': [
        {
            'name': '数据看板',
            'url': '/admin/api/dashboardproxy/',
            'app': 'api',
            'model': 'dashboardproxy',
        },
        {
            'name': '景点列表',
            'url': '/admin/api/spot/',
        },
        {
            'name': '景点攻略',
            'url': '/admin/api/spottip/',
        },
        {
            'name': '行程管理',
            'url': '/admin/api/savedplan/',
        },
        {
            'name': '收藏',
            'url': '/admin/api/favorite/',
        },
        {
            'name': '旅行日记',
            'url': '/admin/api/traveldiary/',
        },
        {
            'name': '认证和授权',
            'models': [
                {
                    'name': '用户',
                    'url': '/admin/auth/user/',
                },
                {
                    'name': '组',
                    'url': '/admin/auth/group/',
                },
            ]
        },
    ]
}


# ==================== Django REST Framework 配置 ====================
# 默认使用 JWT Token 作为认证方式
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# ==================== JWT Token 有效期配置 ====================
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),      # Access Token 有效期 1 天
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # Refresh Token 有效期 7 天
}
