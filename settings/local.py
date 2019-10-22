from .base import *

DATABASES['default'] = {
    **DATABASES['default'],
    **{
        'NAME': 'socialnetworkdb',
        'USER': 'legimonas',
        'PASSWORD': '12Ad23Sf34Dg',
        'HOST': 'localhost',
        'PORT': '3307',
    }
}
# Port for sending e-mail.
EMAIL_PORT = 587

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = 'progr.0820@gmail.com'
EMAIL_HOST_PASSWORD = '12Ad23Sf34Dg'
EMAIL_USE_TLS = True
# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'