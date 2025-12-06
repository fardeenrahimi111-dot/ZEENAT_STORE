INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "zeenat_store_db",
        "USER": "root",
        "PASSWORD": "yourpassword",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": { "init_command": "SET sql_mode='STRICT_TRANS_TABLES'" },
    }
}