# خدمة المحتوى - منصة نائبك.كوم
# Dockerfile للإنتاج

FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# إنشاء مستخدم غير جذر
RUN groupadd -r naebak && useradd -r -g naebak naebak

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملفات المتطلبات
COPY requirements.txt .

# تثبيت متطلبات Python
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كود المشروع
COPY . .

# تجميع الملفات الثابتة
RUN python manage.py collectstatic --noinput

# تغيير ملكية الملفات
RUN chown -R naebak:naebak /app

# التبديل للمستخدم غير الجذر
USER naebak

# فتح المنفذ
EXPOSE 8000

# فحص صحة الحاوية
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health/', timeout=10)"

# تشغيل الخادم
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "content_service.wsgi:application"]
