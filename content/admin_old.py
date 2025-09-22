"""
إعدادات لوحة الإدارة لخدمة المحتوى - منصة نائبك.كوم
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Governorate, District, PoliticalParty, Representative,
    RepresentativeImage, Achievement, News
)


@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'code', 'population', 'area', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'name_en', 'code']
    ordering = ['name']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'governorate', 'number', 'is_active']
    list_filter = ['governorate', 'is_active']
    search_fields = ['name', 'governorate__name']
    ordering = ['governorate', 'number']


@admin.register(PoliticalParty)
class PoliticalPartyAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'color_display', 'founded_date', 'is_active']
    list_filter = ['is_active', 'founded_date']
    search_fields = ['name', 'name_en', 'abbreviation']
    ordering = ['name']

    def color_display(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; padding: 2px 8px; color: white; border-radius: 3px;">{}</span>',
                obj.color,
                obj.color
            )
        return '-'
    color_display.short_description = 'اللون'


class RepresentativeImageInline(admin.TabularInline):
    model = RepresentativeImage
    extra = 1
    fields = ['image', 'caption', 'order']


class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 1
    fields = ['title', 'date', 'order']


class NewsInline(admin.TabularInline):
    model = News
    extra = 1
    fields = ['title', 'is_featured']


@admin.register(Representative)
class RepresentativeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'party', 'governorate_display', 'gender', 'status',
        'rating', 'is_distinguished', 'is_active'
    ]
    list_filter = [
        'gender', 'status', 'is_distinguished', 'is_active',
        'district__governorate', 'party', 'election_year'
    ]
    search_fields = ['name', 'name_en', 'profession', 'bio']
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
            'fields': ('bio', 'achievements', 'electoral_program'),
            'classes': ('collapse',)
        }),
        ('معلومات الاتصال', {
            'fields': ('phone', 'email', 'facebook', 'twitter', 'website'),
            'classes': ('collapse',)
        }),
        ('إعدادات', {
            'fields': ('is_active',)
        })
    )
    
    inlines = [RepresentativeImageInline, AchievementInline, NewsInline]
    
    def governorate_display(self, obj):
        return obj.district.governorate.name if obj.district else '-'
    governorate_display.short_description = 'المحافظة'
    
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from django.utils.text import slugify
            obj.slug = slugify(obj.name, allow_unicode=True)
        super().save_model(request, obj, form, change)


@admin.register(RepresentativeImage)
class RepresentativeImageAdmin(admin.ModelAdmin):
    list_display = ['representative', 'caption', 'order', 'created_at']
    list_filter = ['representative']
    ordering = ['representative', 'order']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['title', 'representative', 'date', 'order']
    list_filter = ['representative', 'date']
    search_fields = ['title', 'description', 'representative__name']
    ordering = ['-date', 'order']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'representative', 'published_date', 'is_featured']
    list_filter = ['representative', 'is_featured', 'published_date']
    search_fields = ['title', 'content', 'representative__name']
    ordering = ['-published_date']


# تخصيص عنوان لوحة الإدارة
admin.site.site_header = 'إدارة خدمة المحتوى - منصة نائبك'
admin.site.site_title = 'نائبك - إدارة المحتوى'
admin.site.index_title = 'مرحباً بك في لوحة إدارة المحتوى'
