"""
URLs لخدمة المحتوى - منصة نائبك.كوم
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# إنشاء router للـ ViewSets (إذا احتجناها لاحقاً)
router = DefaultRouter()

urlpatterns = [
    # فحص صحة الخدمة
    path('health/', views.health_check, name='health_check'),
    
    # APIs الأساسية
    path('api/governorates/', views.GovernorateListView.as_view(), name='governorate-list'),
    path('api/districts/', views.DistrictListView.as_view(), name='district-list'),
    path('api/parties/', views.PoliticalPartyListView.as_view(), name='party-list'),
    
    # APIs النواب والمرشحين
    path('api/representatives/', views.RepresentativeListView.as_view(), name='representative-list'),
    path('api/representatives/create/', views.RepresentativeCreateView.as_view(), name='representative-create'),
    path('api/representatives/stats/', views.RepresentativeStatsView.as_view(), name='representative-stats'),
    path('api/representatives/<slug:slug>/', views.RepresentativeDetailView.as_view(), name='representative-detail'),
    path('api/representatives/<slug:slug>/update/', views.RepresentativeUpdateView.as_view(), name='representative-update'),
    
    # البحث والفلاتر
    path('api/search/', views.SearchView.as_view(), name='search'),
    path('api/filter-options/', views.get_filter_options, name='filter-options'),
    
    # الروابط العربية للصفحات الشخصية
    path('api/by-slug/<slug:slug>/', views.representative_by_slug, name='representative-by-slug'),
    
    # Router URLs
    path('api/', include(router.urls)),
]
