"""
Serializers لخدمة المحتوى - منصة نائبك.كوم
"""

from rest_framework import serializers
from .models import (
    Governorate, District, PoliticalParty, Representative, 
    RepresentativeImage, Achievement, News, StaticPage,
    Banner, ColorSettings, SiteSettings, FAQ, Event
)


class GovernorateSerializer(serializers.ModelSerializer):
    """Serializer للمحافظات"""
    
    class Meta:
        model = Governorate
        fields = ['id', 'name', 'name_en', 'code', 'population', 'area']


class DistrictSerializer(serializers.ModelSerializer):
    """Serializer للدوائر الانتخابية"""
    governorate_name = serializers.CharField(source='governorate.name', read_only=True)
    
    class Meta:
        model = District
        fields = ['id', 'name', 'governorate', 'governorate_name', 'number', 'description']


class PoliticalPartySerializer(serializers.ModelSerializer):
    """Serializer للأحزاب السياسية"""
    
    class Meta:
        model = PoliticalParty
        fields = [
            'id', 'name', 'name_en', 'abbreviation', 'logo', 
            'color', 'founded_date', 'description', 'website'
        ]


class RepresentativeImageSerializer(serializers.ModelSerializer):
    """Serializer لصور النواب الإضافية"""
    
    class Meta:
        model = RepresentativeImage
        fields = ['id', 'image', 'caption', 'order']


class AchievementSerializer(serializers.ModelSerializer):
    """Serializer لإنجازات النواب"""
    
    class Meta:
        model = Achievement
        fields = ['id', 'title', 'description', 'date', 'image', 'order']


class NewsSerializer(serializers.ModelSerializer):
    """Serializer لأخبار النواب"""
    
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'image', 'published_date', 'is_featured']


class EventSerializer(serializers.ModelSerializer):
    """Serializer للمناسبات والمؤتمرات"""
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'event_date', 
            'location', 'image', 'admin_approved'
        ]


class RepresentativeListSerializer(serializers.ModelSerializer):
    """Serializer مبسط لقائمة النواب"""
    governorate_name = serializers.CharField(source='governorate.name', read_only=True)
    party_name = serializers.CharField(source='party.name', read_only=True)
    party_color = serializers.CharField(source='party.color', read_only=True)
    
    class Meta:
        model = Representative
        fields = [
            'id', 'name', 'slug', 'gender', 'profession', 'profile_image',
            'district', 'governorate_name', 'party', 'party_name', 'party_color',
            'status', 'electoral_number', 'electoral_symbol',
            'rating', 'rating_count', 'solved_complaints', 'received_complaints',
            'is_distinguished', 'success_rate'
        ]


class RepresentativeDetailSerializer(serializers.ModelSerializer):
    """Serializer تفصيلي للنواب"""
    governorate_name = serializers.CharField(source='governorate.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    party_name = serializers.CharField(source='party.name', read_only=True)
    party_color = serializers.CharField(source='party.color', read_only=True)
    age = serializers.ReadOnlyField()
    success_rate = serializers.ReadOnlyField()
    
    # العلاقات
    additional_images = RepresentativeImageSerializer(many=True, read_only=True)
    achievement_list = AchievementSerializer(many=True, read_only=True)
    news = NewsSerializer(many=True, read_only=True)
    events = EventSerializer(many=True, read_only=True)
    
    class Meta:
        model = Representative
        fields = [
            'id', 'name', 'name_en', 'slug', 'gender', 'birth_date', 'age',
            'profession', 'education', 'party', 'party_name', 'party_color',
            'district', 'district_name', 'governorate_name', 'status',
            'electoral_number', 'electoral_symbol', 'election_year',
            'profile_image', 'banner_image', 'rating', 'rating_count',
            'solved_complaints', 'received_complaints', 'success_rate',
            'is_distinguished', 'bio', 'achievements', 'electoral_program',
            'phone', 'email', 'facebook', 'twitter', 'website',
            'additional_images', 'achievement_list', 'news', 'events',
            'created_at', 'updated_at'
        ]


class RepresentativeCreateSerializer(serializers.ModelSerializer):
    """Serializer لإنشاء نائب جديد"""
    
    class Meta:
        model = Representative
        fields = [
            'name', 'name_en', 'gender', 'birth_date', 'profession', 'education',
            'party', 'district', 'status', 'electoral_number', 'electoral_symbol',
            'profile_image', 'bio', 'electoral_program', 'phone', 'email',
            'facebook', 'twitter', 'website'
        ]

    def validate_name(self, value):
        """التحقق من عدم تكرار الاسم"""
        if Representative.objects.filter(name=value).exists():
            raise serializers.ValidationError("يوجد نائب بهذا الاسم بالفعل")
        return value


# ========== Serializers للصفحات الثابتة ==========

class StaticPageSerializer(serializers.ModelSerializer):
    """Serializer للصفحات الثابتة"""
    
    class Meta:
        model = StaticPage
        fields = ['id', 'page_type', 'title', 'content', 'meta_description', 'order']


# ========== Serializers لإدارة البنرات ==========

class BannerSerializer(serializers.ModelSerializer):
    """Serializer للبنرات"""
    representative_name = serializers.CharField(source='representative.name', read_only=True)
    
    class Meta:
        model = Banner
        fields = [
            'id', 'name', 'banner_type', 'image', 'representative', 
            'representative_name', 'is_default', 'alt_text'
        ]


# ========== Serializers لإدارة الألوان ==========

class ColorSettingsSerializer(serializers.ModelSerializer):
    """Serializer لإعدادات الألوان"""
    
    class Meta:
        model = ColorSettings
        fields = ['id', 'color_type', 'color_value', 'description']


# ========== Serializers لإعدادات الموقع ==========

class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer لإعدادات الموقع"""
    
    class Meta:
        model = SiteSettings
        fields = [
            'id', 'site_name', 'site_description', 'contact_email', 
            'contact_phone', 'contact_address', 'facebook_url', 'twitter_url',
            'instagram_url', 'youtube_url', 'linkedin_url', 'visitor_counter_min',
            'visitor_counter_max', 'logo_green', 'logo_white', 'favicon'
        ]


# ========== Serializers للأسئلة الشائعة ==========

class FAQSerializer(serializers.ModelSerializer):
    """Serializer للأسئلة الشائعة"""
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'order']


# ========== Serializers للإحصائيات ==========

class StatisticsSerializer(serializers.Serializer):
    """Serializer للإحصائيات العامة"""
    total_representatives = serializers.IntegerField()
    total_candidates = serializers.IntegerField()
    total_elected = serializers.IntegerField()
    total_former = serializers.IntegerField()
    total_distinguished = serializers.IntegerField()
    total_governorates = serializers.IntegerField()
    total_districts = serializers.IntegerField()
    total_parties = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    total_solved_complaints = serializers.IntegerField()
    total_received_complaints = serializers.IntegerField()
    
    # إحصائيات حسب المحافظة
    governorate_stats = serializers.ListField(child=serializers.DictField())
    
    # إحصائيات حسب النوع
    gender_stats = serializers.DictField()
    
    # إحصائيات حسب الحالة
    status_stats = serializers.DictField()


# ========== Serializers لخيارات الفلاتر ==========

class FilterOptionsSerializer(serializers.Serializer):
    """Serializer لخيارات الفلاتر"""
    governorates = GovernorateSerializer(many=True)
    parties = PoliticalPartySerializer(many=True)
    districts = DistrictSerializer(many=True)
    genders = serializers.ListField(child=serializers.DictField())
    statuses = serializers.ListField(child=serializers.DictField())


# ========== Serializers للبحث ==========

class SearchResultSerializer(serializers.Serializer):
    """Serializer لنتائج البحث"""
    representatives = RepresentativeListSerializer(many=True)
    total_count = serializers.IntegerField()
    page_count = serializers.IntegerField()
    current_page = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()
