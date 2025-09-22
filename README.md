# خدمة المحتوى - منصة نائبك.كوم

خدمة مصغرة لإدارة محتوى النواب والمرشحين في منصة نائبك.كوم، مبنية باستخدام Django REST Framework.

## 🎯 الوظائف الرئيسية

- **إدارة النواب والمرشحين**: بيانات شاملة تشمل السيرة الذاتية والبرنامج الانتخابي
- **نظام التقييم**: تقييم النواب من قبل المواطنين
- **إحصائيات الشكاوى**: متابعة الشكاوى المحلولة والمستلمة
- **الفلاتر المتقدمة**: البحث والفلترة حسب المحافظة والحزب والنوع
- **الروابط العربية**: دعم الروابط باللغة العربية للصفحات الشخصية
- **APIs شاملة**: واجهات برمجية متكاملة مع التوثيق

## 🏗️ البنية التقنية

### التقنيات المستخدمة
- **Backend**: Django 4.2.7 + Django REST Framework 3.14.0
- **قاعدة البيانات**: PostgreSQL (SQLite للتطوير)
- **Cache**: Redis
- **المهام غير المتزامنة**: Celery
- **الاختبارات**: pytest + pytest-django
- **النشر**: GitHub Actions + Gunicorn

### النماذج الأساسية
- `Governorate`: المحافظات
- `District`: الدوائر الانتخابية  
- `PoliticalParty`: الأحزاب السياسية
- `Representative`: النواب والمرشحين
- `Achievement`: إنجازات النواب
- `News`: أخبار النواب

## 🚀 التثبيت والتشغيل

### المتطلبات
- Python 3.11+
- PostgreSQL (اختياري)
- Redis (اختياري)

### خطوات التثبيت

1. **استنساخ المشروع**
```bash
git clone https://github.com/alcounsol17/naebak-content-service.git
cd naebak-content-service
```

2. **إنشاء البيئة الافتراضية**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\\Scripts\\activate  # Windows
```

3. **تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

4. **إعداد متغيرات البيئة**
```bash
cp .env.example .env
# قم بتحرير ملف .env وإضافة القيم المطلوبة
```

5. **تطبيق migrations**
```bash
python manage.py migrate
```

6. **إنشاء مستخدم إداري**
```bash
python manage.py createsuperuser
```

7. **تشغيل الخادم**
```bash
python manage.py runserver
```

## 📊 APIs المتاحة

### النقاط الأساسية
- `GET /health/` - فحص صحة الخدمة
- `GET /api/representatives/` - قائمة النواب والمرشحين
- `GET /api/representatives/{slug}/` - تفاصيل نائب/مرشح
- `GET /api/representatives/stats/` - إحصائيات شاملة
- `GET /api/search/` - البحث المتقدم
- `GET /api/filter-options/` - خيارات الفلاتر

### الفلاتر المدعومة
- `governorate`: المحافظة
- `gender`: النوع (male/female)
- `party`: الحزب السياسي
- `status`: الحالة (candidate/elected/former)
- `is_distinguished`: المرشحين المميزين
- `min_rating` / `max_rating`: نطاق التقييم

### مثال على الاستخدام
```bash
# الحصول على جميع المرشحين المميزين في القاهرة
GET /api/representatives/?governorate=القاهرة&is_distinguished=true

# البحث عن مرشحين بالاسم
GET /api/search/?q=أحمد&gender=male

# الحصول على إحصائيات شاملة
GET /api/representatives/stats/
```

## 🧪 الاختبارات

### تشغيل جميع الاختبارات
```bash
python -m pytest
```

### تشغيل اختبارات محددة
```bash
python -m pytest tests/test_models.py -v
python -m pytest tests/test_apis.py -v
python -m pytest tests/test_serializers.py -v
```

### تقرير التغطية
```bash
python -m pytest --cov=content --cov-report=html
```

### إحصائيات الاختبارات
- **إجمالي الاختبارات**: 51 اختبار
- **معدل النجاح**: 100%
- **تغطية الكود**: 85%+
- **اختبارات النماذج**: 17 اختبار
- **اختبارات APIs**: 19 اختبار  
- **اختبارات Serializers**: 15 اختبار

## 🔧 الإعدادات

### متغيرات البيئة المطلوبة
```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### إعدادات الإنتاج
```env
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://redis-host:6379/0
ALLOWED_HOSTS=your-domain.com
```

## 📁 هيكل المشروع

```
naebak-content-service/
├── content/                 # التطبيق الرئيسي
│   ├── models.py           # نماذج قاعدة البيانات
│   ├── serializers.py      # مسلسلات البيانات
│   ├── views.py            # عروض APIs
│   ├── filters.py          # فلاتر البحث
│   ├── urls.py             # روابط APIs
│   └── admin.py            # لوحة الإدارة
├── tests/                   # الاختبارات
│   ├── test_models.py      # اختبارات النماذج
│   ├── test_apis.py        # اختبارات APIs
│   └── test_serializers.py # اختبارات Serializers
├── content_service/         # إعدادات المشروع
│   ├── settings.py         # الإعدادات الرئيسية
│   ├── test_settings.py    # إعدادات الاختبار
│   └── urls.py             # الروابط الرئيسية
├── requirements.txt         # المتطلبات الأساسية
├── requirements-test.txt    # متطلبات الاختبار
├── pytest.ini             # إعدادات pytest
├── .gitignore             # ملفات Git المتجاهلة
└── README.md              # هذا الملف
```

## 🚀 النشر

### GitHub Actions
يتم النشر تلقائياً عند push إلى branch main باستخدام GitHub Actions.

### النشر اليدوي
```bash
# تجميع الملفات الثابتة
python manage.py collectstatic --noinput

# تشغيل مع Gunicorn
gunicorn content_service.wsgi:application --bind 0.0.0.0:8000
```

## 🤝 المساهمة

1. Fork المشروع
2. إنشاء branch جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push إلى Branch (`git push origin feature/amazing-feature`)
5. فتح Pull Request

## 📝 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 📞 التواصل

- **المشروع**: [نائبك.كوم](https://naebak.com)
- **المطور**: alcounsol17
- **GitHub**: [https://github.com/alcounsol17](https://github.com/alcounsol17)

## 🔄 التحديثات الأخيرة

### الإصدار 1.0.0 (سبتمبر 2024)
- ✅ إطلاق النسخة الأولى
- ✅ APIs شاملة للنواب والمرشحين
- ✅ نظام الفلترة والبحث المتقدم
- ✅ اختبارات شاملة (51 اختبار)
- ✅ دعم الروابط العربية
- ✅ نظام التقييم والإحصائيات
- ✅ لوحة إدارة متكاملة
- ✅ GitHub Actions للنشر التلقائي

---

**ملاحظة**: هذه الخدمة جزء من منظومة نائبك.كوم المتكاملة لربط المواطنين بنوابهم في البرلمان.
