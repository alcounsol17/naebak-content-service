"""
إعدادات pytest لخدمة المحتوى - منصة نائبك.كوم
"""

import os
import django
from django.conf import settings
from django.test.utils import get_runner

def pytest_configure():
    """إعداد Django للاختبارات"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'content_service.settings')
    django.setup()
    
    # إعداد قاعدة بيانات الاختبار
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'rest_framework',
                'content',
            ],
            SECRET_KEY='test-secret-key',
            USE_TZ=True,
        )
