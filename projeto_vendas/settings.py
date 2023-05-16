"""
Django settings for projeto_vendas project.

Generated by 'django-admin startproject' using Django 4.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-v)$l+-o!0ddq@df24j*8(bm0=9%m)tv#6s2oyriotn39&18__0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

#ALLOWED_HOSTS = ['54.207.82.154']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'usuarios',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',



]

ROOT_URLCONF = 'projeto_vendas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'projeto_vendas.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sistema_de_vendas',
        'USER': 'sa',
        'PASSWORD': '2241',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/mysite/assets/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'usuarios.CustomUsuario'


LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'
SESSION_COOKIE_AGE = 604800  # 1 semana



SESSION_COOKIE_HTTPONLY = True #  Isso significa que o cookie da sessão só pode ser acessado por meio do protocolo HTTP(S) e não por meio de JavaScript. Isso é uma medida de segurança que ajuda a prevenir ataques de roubo de sessão através de scripts maliciosos (ataques XSS, ou cross-site scripting).
SESSION_COOKIE_SECURE = True # Isso significa que o cookie da sessão só será enviado por uma conexão segura (HTTPS). Isso ajuda a prevenir o roubo de sessão por meio de sniffing de rede ou ataques man-in-the-middle.


SECURE_HSTS_SECONDS = True # HSTS significa HTTP Strict Transport Security. É um mecanismo de segurança que força o navegador a apenas se comunicar com o servidor via HTTPS, mesmo que o usuário tente acessar a página via HTTP. O valor é o número de segundos que essa regra deve ser mantida pelo navegador.
SECURE_HSTS_INCLUDE_SUBDOMAINS = True #  Se verdadeiro, a regra HSTS também se aplica a todos os subdomínios.
SECURE_CONTENT_TYPE_NOSNIFF = True #  Isso adiciona o cabeçalho X-Content-Type-Options: nosniff às respostas HTTP, o que pode ajudar a prevenir ataques onde scripts maliciosos são injetados em arquivos de mídia.
SUCURE_BROWSER_XSS_FILTER = True # Isso adiciona o cabeçalho X-XSS-Protection: 1; mode=block às respostas HTTP, o que pode ajudar a prevenir ataques XSS.
CSRF_COOKIE_SECURE = True # Isso significa que o cookie CSRF só será enviado por uma conexão segura (HTTPS). Isso ajuda a prevenir ataques de falsificação de solicitação em sites cruzados (CSRF).
CSRF_COOKIE_HTTPNLY = True # Isso significa que o cookie CSRF só pode ser acessado por meio do protocolo HTTP(S) e não por meio de JavaScript.
X_FRAME_OPTIONS = 'DENY' # Isso adiciona o cabeçalho X-Frame-Options: DENY às respostas HTTP, o que impede que o site seja exibido dentro de um <iframe> em outro site. Isso pode ajudar a prevenir ataques de clickjacking.


# LEMBRE-SE DE TROCAR A ROTA DO ADMIN PARA FICAR MAIS SEGURO
SECURE_SSL_REDIRECT = True




