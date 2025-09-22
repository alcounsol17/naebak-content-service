"""
Filters لخدمة المحتوى - منصة نائبك.كوم
"""

import django_filters
from django.db.models import Q
from .models import Representative, Governorate, PoliticalParty


class RepresentativeFilter(django_filters.FilterSet):
    """فلتر للنواب والمرشحين"""
    
    # البحث في الاسم
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='البحث في الاسم'
    )
    
    # فلتر المحافظة
    governorate = django_filters.CharFilter(
        field_name='district__governorate__name',
        lookup_expr='iexact',
        label='المحافظة'
    )
    
    # فلتر النوع
    gender = django_filters.ChoiceFilter(
        choices=Representative.GENDER_CHOICES,
        label='النوع'
    )
    
    # فلتر الحزب
    party = django_filters.CharFilter(
        field_name='party__name',
        lookup_expr='iexact',
        label='الحزب'
    )
    
    # فلتر الحالة
    status = django_filters.ChoiceFilter(
        choices=Representative.STATUS_CHOICES,
        label='الحالة'
    )
    
    # فلتر المرشحين المميزين
    is_distinguished = django_filters.BooleanFilter(
        label='مرشح مميز'
    )
    
    # فلتر التقييم
    min_rating = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='gte',
        label='الحد الأدنى للتقييم'
    )
    
    max_rating = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='lte',
        label='الحد الأعلى للتقييم'
    )
    
    # فلتر سنة الانتخاب
    election_year = django_filters.NumberFilter(
        label='سنة الانتخاب'
    )
    
    # فلتر الدائرة الانتخابية
    district = django_filters.CharFilter(
        field_name='district__name',
        lookup_expr='icontains',
        label='الدائرة الانتخابية'
    )
    
    # فلتر المهنة
    profession = django_filters.CharFilter(
        field_name='profession',
        lookup_expr='icontains',
        label='المهنة'
    )
    
    # البحث العام (في الاسم والمهنة والسيرة الذاتية)
    search = django_filters.CharFilter(
        method='filter_search',
        label='البحث العام'
    )
    
    def filter_search(self, queryset, name, value):
        """البحث في عدة حقول"""
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(profession__icontains=value) |
                Q(bio__icontains=value) |
                Q(electoral_program__icontains=value)
            )
        return queryset
    
    class Meta:
        model = Representative
        fields = [
            'name', 'governorate', 'gender', 'party', 'status',
            'is_distinguished', 'min_rating', 'max_rating',
            'election_year', 'district', 'profession', 'search'
        ]


class GovernorateFilter(django_filters.FilterSet):
    """فلتر للمحافظات"""
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='اسم المحافظة'
    )
    
    code = django_filters.CharFilter(
        field_name='code',
        lookup_expr='iexact',
        label='كود المحافظة'
    )
    
    class Meta:
        model = Governorate
        fields = ['name', 'code']


class PoliticalPartyFilter(django_filters.FilterSet):
    """فلتر للأحزاب السياسية"""
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='اسم الحزب'
    )
    
    class Meta:
        model = PoliticalParty
        fields = ['name']
