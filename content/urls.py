"""
URLs لخدمة المحتوى - منصة نائبك.كوم
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# إنشاء router للـ ViewSets
router = DefaultRouter()

urlpatterns = [
    # ========== APIs الأساسية للنواب ==========
    path('api/representatives/', views.RepresentativeListView.as_view(), name='representative-list'),
    path('api/representatives/create/', views.RepresentativeCreateView.as_view(), name='representative-create'),
    path('api/representatives/<slug:slug>/', views.RepresentativeDetailView.as_view(), name='representative-detail'),
    
    # ========== APIs الصفحات الثابتة ==========
    path('api/pages/', views.StaticPageListView.as_view(), name='static-page-list'),
    path('api/pages/<str:page_type>/', views.StaticPageDetailView.as_view(), name='static-page-detail'),
    path('api/admin/pages/<str:page_type>/', views.StaticPageCreateUpdateView.as_view(), name='static-page-admin'),
    
    # ========== APIs إدارة البنرات ==========
    path('api/banners/', views.BannerListView.as_view(), name='banner-list'),
    path('api/banners/create/', views.BannerCreateView.as_view(), name='banner-create'),
    path('api/banners/<uuid:pk>/', views.BannerDetailView.as_view(), name='banner-detail'),
    path('api/banners/default/', views.get_default_banner, name='default-banner'),
    
    # ========== APIs إدارة الألوان ==========
    path('api/colors/', views.ColorSettingsListView.as_view(), name='color-list'),
    path('api/colors/<str:color_type>/', views.ColorSettingsDetailView.as_view(), name='color-detail'),
    path('api/colors/scheme/', views.get_color_scheme, name='color-scheme'),
    
    # ========== APIs إعدادات الموقع ==========
    path('api/settings/', views.SiteSettingsView.as_view(), name='site-settings'),
    
    # ========== APIs الأسئلة الشائعة ==========
    path('api/faq/', views.FAQListView.as_view(), name='faq-list'),
    path('api/faq/<uuid:pk>/', views.FAQDetailView.as_view(), name='faq-detail'),
    
    # ========== APIs المناسبات والمؤتمرات ==========
    path('api/events/', views.EventListView.as_view(), name='event-list'),
    path('api/events/<uuid:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    
    # ========== APIs الإحصائيات والبحث ==========
    path('api/statistics/', views.statistics_view, name='statistics'),
    path('api/filter-options/', views.filter_options_view, name='filter-options'),
    path('api/search/', views.search_view, name='search'),
    
    # ========== API فحص الصحة ==========
    path('health/', views.health_check, name='health-check'),
    
    # ========== Router URLs ==========
    path('api/', include(router.urls)),
]

# إضافة مسارات الصفحات الشخصية بالروابط العربية
urlpatterns += [
    # مسار الصفحة الشخصية بالرابط العربي
    path('<slug:slug>/', views.RepresentativeDetailView.as_view(), name='representative-page-arabic'),
]
