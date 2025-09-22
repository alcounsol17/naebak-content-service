"""
نماذج قاعدة البيانات لخدمة المحتوى - منصة نائبك.كوم
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import uuid


class BaseModel(models.Model):
    """نموذج أساسي يحتوي على الحقول المشتركة"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    class Meta:
        abstract = True


class Governorate(BaseModel):
    """نموذج المحافظات"""
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم المحافظة")
    name_en = models.CharField(max_length=100, blank=True, verbose_name="الاسم بالإنجليزية")
    code = models.CharField(max_length=10, unique=True, verbose_name="كود المحافظة")
    population = models.PositiveIntegerField(null=True, blank=True, verbose_name="عدد السكان")
    area = models.FloatField(null=True, blank=True, verbose_name="المساحة (كم²)")

    class Meta:
        verbose_name = "محافظة"
        verbose_name_plural = "المحافظات"
        ordering = ['name']

    def __str__(self):
        return self.name


class District(BaseModel):
    """نموذج الدوائر الانتخابية"""
    name = models.CharField(max_length=200, verbose_name="اسم الدائرة")
    governorate = models.ForeignKey(
        Governorate, 
        on_delete=models.CASCADE, 
        related_name='districts',
        verbose_name="المحافظة"
    )
    number = models.PositiveIntegerField(verbose_name="رقم الدائرة")
    description = models.TextField(blank=True, verbose_name="وصف الدائرة")

    class Meta:
        verbose_name = "دائرة انتخابية"
        verbose_name_plural = "الدوائر الانتخابية"
        unique_together = ['governorate', 'number']
        ordering = ['governorate', 'number']

    def __str__(self):
        return f"{self.name} - {self.governorate.name}"


class PoliticalParty(BaseModel):
    """نموذج الأحزاب السياسية"""
    name = models.CharField(max_length=200, unique=True, verbose_name="اسم الحزب")
    name_en = models.CharField(max_length=200, blank=True, verbose_name="الاسم بالإنجليزية")
    abbreviation = models.CharField(max_length=20, blank=True, verbose_name="الاختصار")
    logo = models.ImageField(upload_to='parties/logos/', blank=True, verbose_name="شعار الحزب")
    color = models.CharField(max_length=7, default='#000000', verbose_name="لون الحزب")
    founded_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التأسيس")
    description = models.TextField(blank=True, verbose_name="وصف الحزب")
    website = models.URLField(blank=True, verbose_name="الموقع الإلكتروني")

    class Meta:
        verbose_name = "حزب سياسي"
        verbose_name_plural = "الأحزاب السياسية"
        ordering = ['name']

    def __str__(self):
        return self.name


class Representative(BaseModel):
    """نموذج النواب والمرشحين"""
    
    GENDER_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ]
    
    STATUS_CHOICES = [
        ('candidate', 'مرشح'),
        ('elected', 'منتخب'),
        ('former', 'سابق'),
    ]

    # البيانات الأساسية
    name = models.CharField(max_length=255, verbose_name="الاسم الكامل")
    name_en = models.CharField(max_length=255, blank=True, verbose_name="الاسم بالإنجليزية")
    slug = models.SlugField(max_length=300, unique=True, blank=True, verbose_name="الرابط")
    
    # البيانات الشخصية
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="النوع")
    birth_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الميلاد")
    profession = models.CharField(max_length=200, blank=True, verbose_name="المهنة")
    education = models.TextField(blank=True, verbose_name="المؤهلات العلمية")
    
    # البيانات السياسية
    party = models.ForeignKey(
        PoliticalParty, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='representatives',
        verbose_name="الحزب"
    )
    district = models.ForeignKey(
        District, 
        on_delete=models.CASCADE, 
        related_name='representatives',
        verbose_name="الدائرة الانتخابية"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='candidate', verbose_name="الحالة")
    
    # البيانات الانتخابية
    electoral_number = models.CharField(max_length=50, blank=True, verbose_name="الرقم الانتخابي")
    electoral_symbol = models.CharField(max_length=255, blank=True, verbose_name="الرمز الانتخابي")
    election_year = models.PositiveIntegerField(default=2024, verbose_name="سنة الانتخاب")
    
    # الصور
    profile_image = models.ImageField(upload_to='representatives/profiles/', blank=True, verbose_name="الصورة الشخصية")
    banner_image = models.ImageField(upload_to='representatives/banners/', blank=True, verbose_name="صورة البانر")
    
    # التقييم والإحصائيات
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name="التقييم"
    )
    rating_count = models.PositiveIntegerField(default=0, verbose_name="عدد المقيمين")
    solved_complaints = models.PositiveIntegerField(default=0, verbose_name="الشكاوى المحلولة")
    received_complaints = models.PositiveIntegerField(default=0, verbose_name="الشكاوى المستلمة")
    
    # الحالة المميزة
    is_distinguished = models.BooleanField(default=False, verbose_name="مرشح مميز")
    
    # موافقة الإدارة
    admin_approved = models.BooleanField(default=False, verbose_name="موافقة الإدارة")
    
    # البيانات الإضافية
    bio = models.TextField(blank=True, verbose_name="السيرة الذاتية")
    achievements = models.TextField(blank=True, verbose_name="الإنجازات")
    electoral_program = models.TextField(blank=True, verbose_name="البرنامج الانتخابي")
    
    # معلومات الاتصال
    phone = models.CharField(max_length=20, blank=True, verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")
    facebook = models.URLField(blank=True, verbose_name="فيسبوك")
    twitter = models.URLField(blank=True, verbose_name="تويتر")
    website = models.URLField(blank=True, verbose_name="الموقع الشخصي")

    class Meta:
        verbose_name = "نائب/مرشح"
        verbose_name_plural = "النواب والمرشحين"
        ordering = ['-is_distinguished', '-rating', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['district', 'party']),
            models.Index(fields=['status', 'is_distinguished']),
            models.Index(fields=['rating']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            # استخدام الاسم الإنجليزي إذا كان متوفراً، وإلا استخدام transliteration
            if self.name_en:
                self.slug = slugify(self.name_en)
            else:
                # تحويل النص العربي إلى نص إنجليزي مبسط
                import re
                # إزالة التشكيل والرموز الخاصة
                clean_name = re.sub(r'[^\w\s-]', '', self.name)
                # استخدام unicode slugify
                self.slug = slugify(clean_name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.district}"

    @property
    def governorate(self):
        """إرجاع المحافظة من خلال الدائرة"""
        return self.district.governorate

    @property
    def age(self):
        """حساب العمر"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    @property
    def success_rate(self):
        """حساب معدل نجاح حل الشكاوى"""
        if self.received_complaints > 0:
            return round((self.solved_complaints / self.received_complaints) * 100, 1)
        return 0.0

    def get_absolute_url(self):
        """إرجاع الرابط المطلق للصفحة الشخصية"""
        return f"/{self.slug}/"


class RepresentativeImage(BaseModel):
    """نموذج صور إضافية للنواب"""
    representative = models.ForeignKey(
        Representative, 
        on_delete=models.CASCADE, 
        related_name='additional_images',
        verbose_name="النائب/المرشح"
    )
    image = models.ImageField(upload_to='representatives/gallery/', verbose_name="الصورة")
    caption = models.CharField(max_length=255, blank=True, verbose_name="وصف الصورة")
    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")

    class Meta:
        verbose_name = "صورة إضافية"
        verbose_name_plural = "الصور الإضافية"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"صورة {self.representative.name}"


class Achievement(BaseModel):
    """نموذج إنجازات النواب"""
    representative = models.ForeignKey(
        Representative, 
        on_delete=models.CASCADE, 
        related_name='achievement_list',
        verbose_name="النائب/المرشح"
    )
    title = models.CharField(max_length=255, verbose_name="عنوان الإنجاز")
    description = models.TextField(verbose_name="وصف الإنجاز")
    date = models.DateField(verbose_name="تاريخ الإنجاز")
    image = models.ImageField(upload_to='achievements/', blank=True, verbose_name="صورة الإنجاز")
    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")

    class Meta:
        verbose_name = "إنجاز"
        verbose_name_plural = "الإنجازات"
        ordering = ['-date', 'order']

    def __str__(self):
        return f"{self.title} - {self.representative.name}"


class News(BaseModel):
    """نموذج أخبار النواب"""
    representative = models.ForeignKey(
        Representative, 
        on_delete=models.CASCADE, 
        related_name='news',
        verbose_name="النائب/المرشح"
    )
    title = models.CharField(max_length=255, verbose_name="عنوان الخبر")
    content = models.TextField(verbose_name="محتوى الخبر")
    image = models.ImageField(upload_to='news/', blank=True, verbose_name="صورة الخبر")
    published_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ النشر")
    is_featured = models.BooleanField(default=False, verbose_name="خبر مميز")

    class Meta:
        verbose_name = "خبر"
        verbose_name_plural = "الأخبار"
        ordering = ['-published_date']

    def __str__(self):
        return f"{self.title} - {self.representative.name}"



# ========== الصفحات الثابتة ==========

class StaticPage(BaseModel):
    """الصفحات الثابتة (اتصل بنا، من نحن، إلخ)"""
    PAGE_TYPES = [
        ('contact', 'اتصل بنا'),
        ('about', 'من نحن'),
        ('privacy', 'سياسات الخصوصية'),
        ('terms', 'اشتراطات واتفاقيات'),
        ('faq', 'أسئلة وأجوبة'),
    ]
    
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, unique=True, verbose_name="نوع الصفحة")
    title = models.CharField(max_length=200, verbose_name="عنوان الصفحة")
    content = models.TextField(verbose_name="محتوى الصفحة")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="وصف SEO")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتيب العرض")

    class Meta:
        verbose_name = "صفحة ثابتة"
        verbose_name_plural = "الصفحات الثابتة"
        ordering = ['order', 'page_type']

    def __str__(self):
        return self.get_page_type_display()


# ========== إدارة البنرات ==========

class Banner(BaseModel):
    """إدارة البنرات"""
    BANNER_TYPES = [
        ('main', 'البنر الرئيسي'),
        ('representative', 'بنر النائب'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="اسم البنر")
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, verbose_name="نوع البنر")
    image = models.ImageField(upload_to='banners/', verbose_name="صورة البنر")
    representative = models.ForeignKey(
        Representative, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='banners',
        verbose_name="النائب"
    )
    is_default = models.BooleanField(default=False, verbose_name="البنر الافتراضي")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="النص البديل")

    class Meta:
        verbose_name = "بنر"
        verbose_name_plural = "البنرات"
        ordering = ['-is_default', 'name']

    def __str__(self):
        if self.representative:
            return f"بنر {self.representative.name}"
        return f"{self.name} ({self.get_banner_type_display()})"

    def save(self, *args, **kwargs):
        # التأكد من وجود بنر افتراضي واحد فقط للنوع الرئيسي
        if self.is_default and self.banner_type == 'main':
            Banner.objects.filter(banner_type='main', is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


# ========== إدارة الألوان ==========

class ColorSettings(BaseModel):
    """إعدادات الألوان"""
    COLOR_TYPES = [
        ('primary_green', 'الأخضر الأساسي'),
        ('primary_orange', 'البرتقالي الأساسي'),
        ('secondary_green', 'الأخضر الثانوي'),
        ('secondary_orange', 'البرتقالي الثانوي'),
        ('header_green', 'أخضر الهيدر'),
        ('footer_green', 'أخضر الفوتر'),
        ('news_ticker_orange', 'برتقالي الشريط الإخباري'),
    ]
    
    color_type = models.CharField(max_length=30, choices=COLOR_TYPES, unique=True, verbose_name="نوع اللون")
    color_value = models.CharField(max_length=7, verbose_name="قيمة اللون (HEX)")
    description = models.CharField(max_length=100, blank=True, verbose_name="وصف الاستخدام")

    class Meta:
        verbose_name = "إعداد لون"
        verbose_name_plural = "إعدادات الألوان"
        ordering = ['color_type']

    def __str__(self):
        return f"{self.get_color_type_display()} - {self.color_value}"


# ========== إعدادات الموقع العامة ==========

class SiteSettings(BaseModel):
    """إعدادات الموقع العامة"""
    site_name = models.CharField(max_length=100, default="نائبك.كوم", verbose_name="اسم الموقع")
    site_description = models.TextField(blank=True, verbose_name="وصف الموقع")
    contact_email = models.EmailField(blank=True, verbose_name="بريد التواصل")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="هاتف التواصل")
    contact_address = models.TextField(blank=True, verbose_name="عنوان التواصل")
    
    # روابط السوشيال ميديا
    facebook_url = models.URLField(blank=True, verbose_name="رابط فيسبوك")
    twitter_url = models.URLField(blank=True, verbose_name="رابط تويتر")
    instagram_url = models.URLField(blank=True, verbose_name="رابط إنستجرام")
    youtube_url = models.URLField(blank=True, verbose_name="رابط يوتيوب")
    linkedin_url = models.URLField(blank=True, verbose_name="رابط لينكد إن")
    
    # إعدادات عداد الزوار
    visitor_counter_min = models.PositiveIntegerField(default=1000, verbose_name="الحد الأدنى لعداد الزوار")
    visitor_counter_max = models.PositiveIntegerField(default=1500, verbose_name="الحد الأقصى لعداد الزوار")
    
    # اللوجو والأيقونات
    logo_green = models.ImageField(upload_to='logos/', blank=True, verbose_name="اللوجو الأخضر")
    logo_white = models.ImageField(upload_to='logos/', blank=True, verbose_name="اللوجو الأبيض")
    favicon = models.ImageField(upload_to='logos/', blank=True, verbose_name="الفيف أيكون")

    class Meta:
        verbose_name = "إعدادات الموقع"
        verbose_name_plural = "إعدادات الموقع"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # التأكد من وجود إعداد واحد فقط
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError("يمكن وجود إعداد واحد فقط للموقع")
        super().save(*args, **kwargs)


# ========== الأسئلة الشائعة ==========

class FAQ(BaseModel):
    """الأسئلة الشائعة"""
    question = models.CharField(max_length=300, verbose_name="السؤال")
    answer = models.TextField(verbose_name="الإجابة")
    category = models.CharField(max_length=100, blank=True, verbose_name="التصنيف")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتيب العرض")

    class Meta:
        verbose_name = "سؤال شائع"
        verbose_name_plural = "الأسئلة الشائعة"
        ordering = ['order', 'question']

    def __str__(self):
        return self.question[:100]


# ========== المناسبات والمؤتمرات ==========

class Event(BaseModel):
    """المناسبات والمؤتمرات"""
    EVENT_TYPES = [
        ('conference', 'مؤتمر'),
        ('meeting', 'اجتماع'),
        ('ceremony', 'حفل'),
        ('workshop', 'ورشة عمل'),
        ('other', 'أخرى'),
    ]
    
    representative = models.ForeignKey(
        Representative, 
        on_delete=models.CASCADE, 
        related_name='events', 
        verbose_name="النائب"
    )
    title = models.CharField(max_length=200, verbose_name="عنوان المناسبة")
    description = models.TextField(verbose_name="وصف المناسبة")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other', verbose_name="نوع المناسبة")
    event_date = models.DateTimeField(verbose_name="تاريخ المناسبة")
    location = models.CharField(max_length=200, blank=True, verbose_name="المكان")
    image = models.ImageField(upload_to='events/', blank=True, verbose_name="صورة المناسبة")
    admin_approved = models.BooleanField(default=False, verbose_name="موافقة الإدارة")

    class Meta:
        verbose_name = "مناسبة"
        verbose_name_plural = "المناسبات والمؤتمرات"
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.title} - {self.representative.name}"
