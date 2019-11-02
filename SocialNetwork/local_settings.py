# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'socialnetworkdb',
        'USER': 'legimonas',
        'PASSWORD': '12Ad23Sf34Dg',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3307',
    }
}
# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = 'progr.0820@gmail.com'
EMAIL_HOST_PASSWORD = '12Ad23Sf34Dg'
EMAIL_USE_TLS = True