"""
إعدادات لوحة الإدارة لخدمة المحتوى - منصة نائبك.كوم
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Governorate, District, PoliticalParty, Representative,
    RepresentativeImage, Achievement, News, StaticPage,
    Banner, ColorSettings, SiteSettings, FAQ, Event
)


@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    """إدارة المحافظات"""
    list_display = ['name', 'name_en', 'code', 'population', 'area', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'name_en', 'code']
    ordering = ['name']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    """إدارة الدوائر الانتخابية"""
    list_display = ['name', 'governorate', 'number', 'is_active']
    list_filter = ['governorate', 'is_active']
    search_fields = ['name', 'governorate__name']
    ordering = ['governorate', 'number']


@admin.register(PoliticalParty)
class PoliticalPartyAdmin(admin.ModelAdmin):
    """إدارة الأحزاب السياسية"""
    list_display = ['name', 'abbreviation', 'color_preview', 'founded_date', 'is_active']
    list_filter = ['is_active', 'founded_date']
    search_fields = ['name', 'name_en', 'abbreviation']
    ordering = ['name']
    
    def color_preview(self, obj):
        if obj.color:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
                obj.color
            )
        return '-'
    color_preview.short_description = 'اللون'


class RepresentativeImageInline(admin.TabularInline):
    """صور إضافية للنواب"""
    model = RepresentativeImage
    extra = 1
    fields = ['image', 'caption', 'order']


class AchievementInline(admin.TabularInline):
    """إنجازات النواب"""
    model = Achievement
    extra = 1
    fields = ['title', 'date', 'order']


class NewsInline(admin.TabularInline):
    """أخبار النواب"""
    model = News
    extra = 1
    fields = ['title', 'is_featured']


class EventInline(admin.TabularInline):
    """مناسبات النواب"""
    model = Event
    extra = 1
    fields = ['title', 'event_date', 'admin_approved']


@admin.register(Representative)
class RepresentativeAdmin(admin.ModelAdmin):
    """إدارة النواب والمرشحين"""
    list_display = [
        'name', 'district', 'party', 'status', 'gender', 
        'rating', 'is_distinguished', 'is_active'
    ]
    list_filter = [
        'status', 'gender', 'is_distinguished', 
        'is_active', 'district__governorate', 'party'
    ]
    search_fields = ['name', 'name_en', 'profession', 'district__name']
    ordering = ['-is_distinguished', '-rating', 'name']
    
    fieldsets = (
        ('البيانات الأساسية', {
            'fields': ('name', 'name_en', 'slug', 'gender', 'birth_date', 'profession', 'education')
        }),
        ('البيانات السياسية', {
            'fields': ('party', 'district', 'status', 'electoral_number', 'electoral_symbol', 'election_year')
        }),
        ('الصور', {
            'fields': ('profile_image', 'banner_image')
        }),
        ('التقييم والإحصائيات', {
            'fields': ('rating', 'rating_count', 'solved_complaints', 'received_complaints', 'is_distinguished')
        }),
        ('المحتوى', {
            'fields': ('bio', 'achievements', 'electoral_program')
        }),
        ('معلومات الاتصال', {
            'fields': ('phone', 'email', 'facebook', 'twitter', 'website')
        }),
        ('الإعدادات', {
            'fields': ('is_active',)
        }),
    )
    
    inlines = [RepresentativeImageInline, AchievementInline, NewsInline, EventInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('district', 'party', 'district__governorate')


@admin.register(RepresentativeImage)
class RepresentativeImageAdmin(admin.ModelAdmin):
    """إدارة صور النواب"""
    list_display = ['representative', 'caption', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['representative__name', 'caption']
    ordering = ['representative', 'order']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """إدارة إنجازات النواب"""
    list_display = ['title', 'representative', 'date', 'order', 'is_active']
    list_filter = ['is_active', 'date']
    search_fields = ['title', 'representative__name']
    ordering = ['-date', 'order']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """إدارة أخبار النواب"""
    list_display = ['title', 'representative', 'published_date', 'is_featured', 'is_active']
    list_filter = ['is_featured', 'is_active', 'published_date']
    search_fields = ['title', 'representative__name']
    ordering = ['-published_date']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """إدارة المناسبات والمؤتمرات"""
    list_display = ['title', 'representative', 'event_type', 'event_date', 'admin_approved', 'is_active']
    list_filter = ['event_type', 'admin_approved', 'is_active', 'event_date']
    search_fields = ['title', 'representative__name', 'location']
    ordering = ['-event_date']


# ========== إدارة الصفحات الثابتة ==========

@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    """إدارة الصفحات الثابتة"""
    list_display = ['get_page_type_display', 'title', 'order', 'is_active']
    list_filter = ['page_type', 'is_active']
    search_fields = ['title', 'content']
    ordering = ['order', 'page_type']
    
    fieldsets = (
        ('معلومات الصفحة', {
            'fields': ('page_type', 'title', 'order')
        }),
        ('المحتوى', {
            'fields': ('content', 'meta_description')
        }),
        ('الإعدادات', {
            'fields': ('is_active',)
        }),
    )


# ========== إدارة البنرات ==========

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """إدارة البنرات"""
    list_display = ['name', 'banner_type', 'representative', 'is_default', 'is_active']
    list_filter = ['banner_type', 'is_default', 'is_active']
    search_fields = ['name', 'representative__name']
    ordering = ['-is_default', 'banner_type', 'name']
    
    fieldsets = (
        ('معلومات البنر', {
            'fields': ('name', 'banner_type', 'representative')
        }),
        ('الصورة', {
            'fields': ('image', 'alt_text')
        }),
        ('الإعدادات', {
            'fields': ('is_default', 'is_active')
        }),
    )


# ========== إدارة الألوان ==========

@admin.register(ColorSettings)
class ColorSettingsAdmin(admin.ModelAdmin):
    """إدارة إعدادات الألوان"""
    list_display = ['get_color_type_display', 'color_preview', 'color_value', 'description', 'is_active']
    list_filter = ['color_type', 'is_active']
    search_fields = ['color_value', 'description']
    ordering = ['color_type']
    
    def color_preview(self, obj):
        if obj.color_value:
            return format_html(
                '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block;"></div>',
                obj.color_value
            )
        return '-'
    color_preview.short_description = 'معاينة اللون'
    
    fieldsets = (
        ('إعدادات اللون', {
            'fields': ('color_type', 'color_value', 'description')
        }),
        ('الإعدادات', {
            'fields': ('is_active',)
        }),
    )


# ========== إعدادات الموقع ==========

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """إدارة إعدادات الموقع"""
    list_display = ['site_name', 'contact_email', 'contact_phone', 'is_active']
    
    fieldsets = (
        ('معلومات الموقع', {
            'fields': ('site_name', 'site_description')
        }),
        ('معلومات التواصل', {
            'fields': ('contact_email', 'contact_phone', 'contact_address')
        }),
        ('روابط السوشيال ميديا', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'youtube_url', 'linkedin_url')
        }),
        ('إعدادات عداد الزوار', {
            'fields': ('visitor_counter_min', 'visitor_counter_max')
        }),
        ('اللوجو والأيقونات', {
            'fields': ('logo_green', 'logo_white', 'favicon')
        }),
        ('الإعدادات', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        # السماح بإضافة إعداد واحد فقط
        return not SiteSettings.objects.exists()


# ========== الأسئلة الشائعة ==========

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """إدارة الأسئلة الشائعة"""
    list_display = ['question_preview', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer', 'category']
    ordering = ['order', 'question']
    
    def question_preview(self, obj):
        return obj.question[:100] + '...' if len(obj.question) > 100 else obj.question
    question_preview.short_description = 'السؤال'
    
    fieldsets = (
        ('السؤال والإجابة', {
            'fields': ('question', 'answer', 'category')
        }),
        ('الإعدادات', {
            'fields': ('order', 'is_active')
        }),
    )


# تخصيص عنوان لوحة الإدارة
admin.site.site_header = "إدارة منصة نائبك.كوم"
admin.site.site_title = "نائبك.كوم"
admin.site.index_title = "لوحة التحكم الرئيسية"
