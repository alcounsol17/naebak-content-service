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
            self.slug = slugify(self.name, allow_unicode=True)
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
