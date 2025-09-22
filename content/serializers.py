"""
Serializers لخدمة المحتوى - منصة نائبك.كوم
"""

from rest_framework import serializers
from .models import (
    Governorate, District, PoliticalParty, Representative, 
    RepresentativeImage, Achievement, News
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
            'id', 'name', 'name_en', 'abbreviation', 'logo', 'color',
            'founded_date', 'description', 'website'
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


class RepresentativeListSerializer(serializers.ModelSerializer):
    """Serializer مبسط لقائمة النواب والمرشحين"""
    governorate = serializers.CharField(source='district.governorate.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    party_name = serializers.CharField(source='party.name', read_only=True)
    party_color = serializers.CharField(source='party.color', read_only=True)
    success_rate = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Representative
        fields = [
            'id', 'name', 'slug', 'gender', 'age', 'profession',
            'party_name', 'party_color', 'district_name', 'governorate',
            'status', 'electoral_number', 'electoral_symbol', 'election_year',
            'profile_image', 'rating', 'rating_count', 'solved_complaints',
            'received_complaints', 'success_rate', 'is_distinguished',
            'phone', 'email', 'created_at'
        ]


class RepresentativeDetailSerializer(serializers.ModelSerializer):
    """Serializer مفصل للنواب والمرشحين"""
    governorate = GovernorateSerializer(source='district.governorate', read_only=True)
    district = DistrictSerializer(read_only=True)
    party = PoliticalPartySerializer(read_only=True)
    additional_images = RepresentativeImageSerializer(many=True, read_only=True)
    achievement_list = AchievementSerializer(many=True, read_only=True)
    news = NewsSerializer(many=True, read_only=True)
    success_rate = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Representative
        fields = [
            'id', 'name', 'name_en', 'slug', 'gender', 'birth_date', 'age',
            'profession', 'education', 'party', 'district', 'governorate',
            'status', 'electoral_number', 'electoral_symbol', 'election_year',
            'profile_image', 'banner_image', 'rating', 'rating_count',
            'solved_complaints', 'received_complaints', 'success_rate',
            'is_distinguished', 'bio', 'achievements', 'electoral_program',
            'phone', 'email', 'facebook', 'twitter', 'website',
            'additional_images', 'achievement_list', 'news',
            'created_at', 'updated_at'
        ]


class RepresentativeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer لإنشاء وتحديث النواب والمرشحين"""
    
    class Meta:
        model = Representative
        fields = [
            'name', 'name_en', 'gender', 'birth_date', 'profession', 'education',
            'party', 'district', 'status', 'electoral_number', 'electoral_symbol',
            'election_year', 'profile_image', 'banner_image', 'is_distinguished',
            'bio', 'achievements', 'electoral_program', 'phone', 'email',
            'facebook', 'twitter', 'website'
        ]
    
    def validate_electoral_number(self, value):
        """التحقق من صحة الرقم الانتخابي"""
        if value and not value.isdigit():
            raise serializers.ValidationError("الرقم الانتخابي يجب أن يحتوي على أرقام فقط")
        return value
    
    def validate_phone(self, value):
        """التحقق من صحة رقم الهاتف"""
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("رقم الهاتف غير صحيح")
        return value


class RepresentativeStatsSerializer(serializers.Serializer):
    """Serializer لإحصائيات النواب"""
    total_representatives = serializers.IntegerField()
    total_candidates = serializers.IntegerField()
    total_elected = serializers.IntegerField()
    distinguished_count = serializers.IntegerField()
    male_count = serializers.IntegerField()
    female_count = serializers.IntegerField()
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=1)
    total_complaints_solved = serializers.IntegerField()
    total_complaints_received = serializers.IntegerField()
    governorates_count = serializers.IntegerField()
    parties_count = serializers.IntegerField()


class SearchSerializer(serializers.Serializer):
    """Serializer لمعاملات البحث"""
    q = serializers.CharField(required=False, help_text="البحث في الاسم")
    governorate = serializers.CharField(required=False, help_text="فلتر المحافظة")
    gender = serializers.ChoiceField(
        choices=['male', 'female'], 
        required=False, 
        help_text="فلتر النوع"
    )
    party = serializers.CharField(required=False, help_text="فلتر الحزب")
    status = serializers.ChoiceField(
        choices=['candidate', 'elected', 'former'], 
        required=False, 
        help_text="فلتر الحالة"
    )
    is_distinguished = serializers.BooleanField(required=False, help_text="المرشحين المميزين فقط")
    min_rating = serializers.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        required=False, 
        help_text="الحد الأدنى للتقييم"
    )
    max_rating = serializers.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        required=False, 
        help_text="الحد الأعلى للتقييم"
    )
    ordering = serializers.ChoiceField(
        choices=[
            'name', '-name', 'rating', '-rating', 'created_at', '-created_at',
            'solved_complaints', '-solved_complaints', 'is_distinguished'
        ],
        required=False,
        default='-is_distinguished',
        help_text="ترتيب النتائج"
    )
