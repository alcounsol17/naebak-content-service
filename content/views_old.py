"""
Views لخدمة المحتوى - منصة نائبك.كوم
"""

from django.db.models import Count, Avg, Q
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Governorate, District, PoliticalParty, Representative,
    RepresentativeImage, Achievement, News
)
from .serializers import (
    GovernorateSerializer, DistrictSerializer, PoliticalPartySerializer,
    RepresentativeListSerializer, RepresentativeDetailSerializer,
    RepresentativeCreateUpdateSerializer, RepresentativeStatsSerializer,
    SearchSerializer
)
from .filters import RepresentativeFilter, GovernorateFilter, PoliticalPartyFilter

import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def health_check(request):
    """فحص صحة الخدمة"""
    return Response({
        'status': 'healthy',
        'service': 'naebak-content-service',
        'version': '1.0.0',
        'timestamp': '2024-09-22'
    })


class GovernorateListView(generics.ListAPIView):
    """قائمة المحافظات"""
    queryset = Governorate.objects.filter(is_active=True)
    serializer_class = GovernorateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GovernorateFilter
    search_fields = ['name', 'name_en']
    ordering_fields = ['name', 'population', 'area']
    ordering = ['name']

    def get_queryset(self):
        """إضافة cache للمحافظات"""
        cache_key = 'governorates_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            queryset = super().get_queryset()
            cache.set(cache_key, list(queryset), 3600)  # cache لمدة ساعة
            return queryset
        
        return Governorate.objects.filter(id__in=[g.id for g in cached_data])


class DistrictListView(generics.ListAPIView):
    """قائمة الدوائر الانتخابية"""
    queryset = District.objects.filter(is_active=True).select_related('governorate')
    serializer_class = DistrictSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'governorate__name']
    ordering_fields = ['name', 'number', 'governorate__name']
    ordering = ['governorate__name', 'number']

    def get_queryset(self):
        queryset = super().get_queryset()
        governorate = self.request.query_params.get('governorate')
        if governorate:
            queryset = queryset.filter(governorate__name__iexact=governorate)
        return queryset


class PoliticalPartyListView(generics.ListAPIView):
    """قائمة الأحزاب السياسية"""
    queryset = PoliticalParty.objects.filter(is_active=True)
    serializer_class = PoliticalPartySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PoliticalPartyFilter
    search_fields = ['name', 'name_en', 'abbreviation']
    ordering_fields = ['name', 'founded_date']
    ordering = ['name']


class RepresentativeListView(generics.ListAPIView):
    """قائمة النواب والمرشحين"""
    serializer_class = RepresentativeListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RepresentativeFilter
    search_fields = ['name', 'profession', 'bio']
    ordering_fields = [
        'name', 'rating', 'created_at', 'solved_complaints',
        'received_complaints', 'is_distinguished'
    ]
    ordering = ['-is_distinguished', '-rating', 'name']

    def get_queryset(self):
        """تحسين الاستعلام مع العلاقات"""
        return Representative.objects.filter(is_active=True).select_related(
            'district__governorate', 'party'
        ).prefetch_related('additional_images')

    def list(self, request, *args, **kwargs):
        """إضافة معلومات إضافية للاستجابة"""
        response = super().list(request, *args, **kwargs)
        
        # إضافة إحصائيات سريعة
        queryset = self.filter_queryset(self.get_queryset())
        stats = {
            'total_count': queryset.count(),
            'distinguished_count': queryset.filter(is_distinguished=True).count(),
            'male_count': queryset.filter(gender='male').count(),
            'female_count': queryset.filter(gender='female').count(),
        }
        
        response.data['stats'] = stats
        return response


class RepresentativeDetailView(generics.RetrieveAPIView):
    """تفاصيل نائب أو مرشح"""
    serializer_class = RepresentativeDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Representative.objects.filter(is_active=True).select_related(
            'district__governorate', 'party'
        ).prefetch_related(
            'additional_images', 'achievement_list', 'news'
        )

    def retrieve(self, request, *args, **kwargs):
        """إضافة cache للتفاصيل"""
        slug = kwargs.get('slug')
        cache_key = f'representative_detail_{slug}'
        
        # محاولة الحصول على البيانات من cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # إذا لم توجد في cache، جلب البيانات وحفظها
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, 1800)  # cache لمدة 30 دقيقة
        
        return response


class RepresentativeCreateView(generics.CreateAPIView):
    """إنشاء نائب أو مرشح جديد"""
    queryset = Representative.objects.all()
    serializer_class = RepresentativeCreateUpdateSerializer

    def perform_create(self, serializer):
        """إضافة logging عند الإنشاء"""
        representative = serializer.save()
        logger.info(f"تم إنشاء مرشح جديد: {representative.name}")


class RepresentativeUpdateView(generics.UpdateAPIView):
    """تحديث بيانات نائب أو مرشح"""
    queryset = Representative.objects.all()
    serializer_class = RepresentativeCreateUpdateSerializer
    lookup_field = 'slug'

    def perform_update(self, serializer):
        """مسح cache عند التحديث"""
        representative = serializer.save()
        cache_key = f'representative_detail_{representative.slug}'
        cache.delete(cache_key)
        logger.info(f"تم تحديث بيانات المرشح: {representative.name}")


class RepresentativeStatsView(APIView):
    """إحصائيات شاملة للنواب والمرشحين"""

    def get(self, request):
        cache_key = 'representatives_stats'
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)

        # حساب الإحصائيات
        representatives = Representative.objects.filter(is_active=True)
        
        stats = {
            'total_representatives': representatives.count(),
            'total_candidates': representatives.filter(status='candidate').count(),
            'total_elected': representatives.filter(status='elected').count(),
            'distinguished_count': representatives.filter(is_distinguished=True).count(),
            'male_count': representatives.filter(gender='male').count(),
            'female_count': representatives.filter(gender='female').count(),
            'avg_rating': representatives.aggregate(Avg('rating'))['rating__avg'] or 0,
            'total_complaints_solved': sum(rep.solved_complaints for rep in representatives),
            'total_complaints_received': sum(rep.received_complaints for rep in representatives),
            'governorates_count': Governorate.objects.filter(is_active=True).count(),
            'parties_count': PoliticalParty.objects.filter(is_active=True).count(),
        }

        serializer = RepresentativeStatsSerializer(stats)
        
        # حفظ في cache لمدة 15 دقيقة
        cache.set(cache_key, serializer.data, 900)
        
        return Response(serializer.data)


class SearchView(APIView):
    """البحث المتقدم في النواب والمرشحين"""

    def get(self, request):
        serializer = SearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        queryset = Representative.objects.filter(is_active=True).select_related(
            'district__governorate', 'party'
        )

        # تطبيق الفلاتر
        if data.get('q'):
            queryset = queryset.filter(
                Q(name__icontains=data['q']) |
                Q(profession__icontains=data['q']) |
                Q(bio__icontains=data['q'])
            )

        if data.get('governorate'):
            queryset = queryset.filter(district__governorate__name__iexact=data['governorate'])

        if data.get('gender'):
            queryset = queryset.filter(gender=data['gender'])

        if data.get('party'):
            queryset = queryset.filter(party__name__iexact=data['party'])

        if data.get('status'):
            queryset = queryset.filter(status=data['status'])

        if data.get('is_distinguished') is not None:
            queryset = queryset.filter(is_distinguished=data['is_distinguished'])

        if data.get('min_rating'):
            queryset = queryset.filter(rating__gte=data['min_rating'])

        if data.get('max_rating'):
            queryset = queryset.filter(rating__lte=data['max_rating'])

        # الترتيب
        ordering = data.get('ordering', '-is_distinguished')
        queryset = queryset.order_by(ordering, 'name')

        # Pagination
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = RepresentativeListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = RepresentativeListSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def get_filter_options(request):
    """الحصول على خيارات الفلاتر"""
    cache_key = 'filter_options'
    cached_options = cache.get(cache_key)
    
    if cached_options:
        return Response(cached_options)

    # جمع خيارات الفلاتر
    governorates = list(
        Governorate.objects.filter(is_active=True)
        .values_list('name', flat=True)
        .order_by('name')
    )
    
    parties = list(
        PoliticalParty.objects.filter(is_active=True)
        .values_list('name', flat=True)
        .order_by('name')
    )
    
    options = {
        'governorates': governorates,
        'parties': parties,
        'genders': [
            {'value': 'male', 'label': 'ذكر'},
            {'value': 'female', 'label': 'أنثى'}
        ],
        'statuses': [
            {'value': 'candidate', 'label': 'مرشح'},
            {'value': 'elected', 'label': 'منتخب'},
            {'value': 'former', 'label': 'سابق'}
        ]
    }
    
    # حفظ في cache لمدة ساعة
    cache.set(cache_key, options, 3600)
    
    return Response(options)


@api_view(['GET'])
def representative_by_slug(request, slug):
    """الحصول على نائب بالـ slug (للروابط العربية)"""
    try:
        representative = get_object_or_404(
            Representative.objects.select_related('district__governorate', 'party')
            .prefetch_related('additional_images', 'achievement_list', 'news'),
            slug=slug,
            is_active=True
        )
        
        serializer = RepresentativeDetailSerializer(representative)
        return Response(serializer.data)
        
    except Representative.DoesNotExist:
        return Response(
            {'error': 'المرشح غير موجود'},
            status=status.HTTP_404_NOT_FOUND
        )
