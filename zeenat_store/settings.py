import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


TEMPLATES = [
    {
        'BACKEND': "django.template.backends.django.DjangoTemplates",  
        'DIRS': [],
        'DEBUG': True,
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]





INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "inventory",
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "zeenat_store_db",
        "USER": "root",              # your MySQL username
        "PASSWORD": "yourpassword",  # your MySQL password
        "HOST": "127.0.0.1, localhost",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

import os
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "core", "static"),
]

TEMPLATE_DIR = os.path.join(BASE_DIR, "core", "templates")
TEMPLATES[0]["DIRS"] = [TEMPLATE_DIR]

