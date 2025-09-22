"""
Views لخدمة المحتوى - منصة نائبك.كوم
"""

from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Governorate, District, PoliticalParty, Representative,
    StaticPage, Banner, ColorSettings, SiteSettings, FAQ, Event
)
from .serializers import (
    GovernorateSerializer, DistrictSerializer, PoliticalPartySerializer,
    RepresentativeListSerializer, RepresentativeDetailSerializer,
    RepresentativeCreateSerializer, StatisticsSerializer,
    FilterOptionsSerializer, SearchResultSerializer,
    StaticPageSerializer, BannerSerializer, ColorSettingsSerializer,
    SiteSettingsSerializer, FAQSerializer, EventSerializer
)
from .filters import RepresentativeFilter


class StandardResultsSetPagination(PageNumberPagination):
    """إعدادات الترقيم القياسية"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ========== APIs الأساسية للنواب ==========

class RepresentativeListView(generics.ListAPIView):
    """قائمة النواب مع الفلاتر والبحث"""
    queryset = Representative.objects.filter(is_active=True, admin_approved=True)
    serializer_class = RepresentativeListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RepresentativeFilter
    search_fields = ['name', 'profession', 'bio', 'electoral_program']
    ordering_fields = ['name', 'rating', 'created_at', 'solved_complaints']
    ordering = ['-is_distinguished', '-rating', 'name']


class RepresentativeDetailView(generics.RetrieveAPIView):
    """تفاصيل النائب بالرابط العربي"""
    queryset = Representative.objects.filter(is_active=True, admin_approved=True)
    serializer_class = RepresentativeDetailSerializer
    lookup_field = 'slug'


class RepresentativeCreateView(generics.CreateAPIView):
    """إنشاء نائب جديد"""
    queryset = Representative.objects.all()
    serializer_class = RepresentativeCreateSerializer


# ========== APIs الصفحات الثابتة ==========

class StaticPageListView(generics.ListAPIView):
    """قائمة الصفحات الثابتة"""
    queryset = StaticPage.objects.filter(is_active=True)
    serializer_class = StaticPageSerializer


class StaticPageDetailView(generics.RetrieveAPIView):
    """تفاصيل صفحة ثابتة"""
    queryset = StaticPage.objects.filter(is_active=True)
    serializer_class = StaticPageSerializer
    lookup_field = 'page_type'


class StaticPageCreateUpdateView(generics.RetrieveUpdateAPIView):
    """إنشاء أو تحديث صفحة ثابتة"""
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    lookup_field = 'page_type'


# ========== APIs إدارة البنرات ==========

class BannerListView(generics.ListAPIView):
    """قائمة البنرات"""
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['banner_type', 'representative', 'is_default']


class BannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """تفاصيل وتحديث البنر"""
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer


class BannerCreateView(generics.CreateAPIView):
    """إنشاء بنر جديد"""
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer


@api_view(['GET'])
def get_default_banner(request):
    """الحصول على البنر الافتراضي"""
    try:
        banner = Banner.objects.filter(banner_type='main', is_default=True, is_active=True).first()
        if banner:
            serializer = BannerSerializer(banner)
            return Response(serializer.data)
        else:
            return Response({'message': 'لا يوجد بنر افتراضي'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== APIs إدارة الألوان ==========

class ColorSettingsListView(generics.ListAPIView):
    """قائمة إعدادات الألوان"""
    queryset = ColorSettings.objects.filter(is_active=True)
    serializer_class = ColorSettingsSerializer


class ColorSettingsDetailView(generics.RetrieveUpdateAPIView):
    """تفاصيل وتحديث إعدادات اللون"""
    queryset = ColorSettings.objects.all()
    serializer_class = ColorSettingsSerializer
    lookup_field = 'color_type'


@api_view(['GET'])
def get_color_scheme(request):
    """الحصول على نظام الألوان الكامل"""
    try:
        colors = ColorSettings.objects.filter(is_active=True)
        color_scheme = {}
        for color in colors:
            color_scheme[color.color_type] = color.color_value
        
        return Response({
            'colors': color_scheme,
            'css_variables': {
                f'--{color.color_type.replace("_", "-")}': color.color_value 
                for color in colors
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== APIs إعدادات الموقع ==========

class SiteSettingsView(generics.RetrieveUpdateAPIView):
    """إعدادات الموقع"""
    serializer_class = SiteSettingsSerializer
    
    def get_object(self):
        settings, created = SiteSettings.objects.get_or_create(
            defaults={
                'site_name': 'نائبك.كوم',
                'visitor_counter_min': 1000,
                'visitor_counter_max': 1500
            }
        )
        return settings


# ========== APIs الأسئلة الشائعة ==========

class FAQListView(generics.ListCreateAPIView):
    """قائمة الأسئلة الشائعة"""
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']


class FAQDetailView(generics.RetrieveUpdateDestroyAPIView):
    """تفاصيل السؤال الشائع"""
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


# ========== APIs المناسبات والمؤتمرات ==========

class EventListView(generics.ListCreateAPIView):
    """قائمة المناسبات"""
    queryset = Event.objects.filter(is_active=True, admin_approved=True)
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['representative', 'event_type']
    ordering = ['-event_date']


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """تفاصيل المناسبة"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer


# ========== APIs الإحصائيات ==========

@api_view(['GET'])
def statistics_view(request):
    """إحصائيات شاملة للمنصة"""
    try:
        # الإحصائيات الأساسية
        total_representatives = Representative.objects.filter(is_active=True).count()
        total_candidates = Representative.objects.filter(status='candidate', is_active=True).count()
        total_elected = Representative.objects.filter(status='elected', is_active=True).count()
        total_former = Representative.objects.filter(status='former', is_active=True).count()
        total_distinguished = Representative.objects.filter(is_distinguished=True, is_active=True).count()
        
        total_governorates = Governorate.objects.filter(is_active=True).count()
        total_districts = District.objects.filter(is_active=True).count()
        total_parties = PoliticalParty.objects.filter(is_active=True).count()
        
        # متوسط التقييم
        avg_rating = Representative.objects.filter(is_active=True).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0.0
        
        # إحصائيات الشكاوى
        total_solved = Representative.objects.filter(is_active=True).aggregate(
            total=Count('solved_complaints')
        )['total'] or 0
        
        total_received = Representative.objects.filter(is_active=True).aggregate(
            total=Count('received_complaints')
        )['total'] or 0
        
        # إحصائيات حسب المحافظة
        governorate_stats = []
        for gov in Governorate.objects.filter(is_active=True):
            count = Representative.objects.filter(
                district__governorate=gov, 
                is_active=True
            ).count()
            if count > 0:
                governorate_stats.append({
                    'name': gov.name,
                    'count': count
                })
        
        # إحصائيات حسب النوع
        gender_stats = {
            'male': Representative.objects.filter(gender='male', is_active=True).count(),
            'female': Representative.objects.filter(gender='female', is_active=True).count()
        }
        
        # إحصائيات حسب الحالة
        status_stats = {
            'candidate': total_candidates,
            'elected': total_elected,
            'former': total_former
        }
        
        data = {
            'total_representatives': total_representatives,
            'total_candidates': total_candidates,
            'total_elected': total_elected,
            'total_former': total_former,
            'total_distinguished': total_distinguished,
            'total_governorates': total_governorates,
            'total_districts': total_districts,
            'total_parties': total_parties,
            'average_rating': round(avg_rating, 2),
            'total_solved_complaints': total_solved,
            'total_received_complaints': total_received,
            'governorate_stats': governorate_stats,
            'gender_stats': gender_stats,
            'status_stats': status_stats
        }
        
        serializer = StatisticsSerializer(data)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== APIs خيارات الفلاتر ==========

@api_view(['GET'])
def filter_options_view(request):
    """خيارات الفلاتر المتاحة"""
    try:
        governorates = Governorate.objects.filter(is_active=True)
        parties = PoliticalParty.objects.filter(is_active=True)
        districts = District.objects.filter(is_active=True)
        
        genders = [
            {'value': 'male', 'label': 'ذكر'},
            {'value': 'female', 'label': 'أنثى'}
        ]
        
        statuses = [
            {'value': 'candidate', 'label': 'مرشح'},
            {'value': 'elected', 'label': 'منتخب'},
            {'value': 'former', 'label': 'سابق'}
        ]
        
        data = {
            'governorates': GovernorateSerializer(governorates, many=True).data,
            'parties': PoliticalPartySerializer(parties, many=True).data,
            'districts': DistrictSerializer(districts, many=True).data,
            'genders': genders,
            'statuses': statuses
        }
        
        serializer = FilterOptionsSerializer(data)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== API البحث المتقدم ==========

@api_view(['GET'])
def search_view(request):
    """البحث المتقدم في النواب"""
    try:
        query = request.GET.get('q', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        if not query:
            return Response({'error': 'يجب إدخال كلمة البحث'}, status=status.HTTP_400_BAD_REQUEST)
        
        # البحث في الحقول المختلفة
        representatives = Representative.objects.filter(
            Q(name__icontains=query) |
            Q(profession__icontains=query) |
            Q(bio__icontains=query) |
            Q(electoral_program__icontains=query) |
            Q(district__name__icontains=query) |
            Q(district__governorate__name__icontains=query) |
            Q(party__name__icontains=query),
            is_active=True,
            admin_approved=True
        ).distinct().order_by('-is_distinguished', '-rating', 'name')
        
        # الترقيم
        total_count = representatives.count()
        start = (page - 1) * page_size
        end = start + page_size
        page_representatives = representatives[start:end]
        
        page_count = (total_count + page_size - 1) // page_size
        has_next = page < page_count
        has_previous = page > 1
        
        data = {
            'representatives': RepresentativeListSerializer(page_representatives, many=True).data,
            'total_count': total_count,
            'page_count': page_count,
            'current_page': page,
            'has_next': has_next,
            'has_previous': has_previous
        }
        
        serializer = SearchResultSerializer(data)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== API فحص الصحة ==========

@api_view(['GET'])
def health_check(request):
    """فحص صحة الخدمة"""
    try:
        # فحص قاعدة البيانات
        Representative.objects.count()
        
        return Response({
            'status': 'healthy',
            'service': 'naebak-content-service',
            'version': '1.0.0',
            'timestamp': '2025-09-22T04:30:00Z'
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
