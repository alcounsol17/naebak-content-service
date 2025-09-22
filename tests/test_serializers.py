"""
اختبارات Serializers لخدمة المحتوى - منصة نائبك.كوم
"""

import pytest
from django.test import TestCase
from model_bakery import baker
from content.models import (
    Governorate, District, PoliticalParty, Representative
)
from content.serializers import (
    GovernorateSerializer, DistrictSerializer, PoliticalPartySerializer,
    RepresentativeListSerializer, RepresentativeDetailSerializer,
    RepresentativeCreateUpdateSerializer, SearchSerializer
)


@pytest.mark.django_db
class TestGovernorateSerializer:
    """اختبارات Serializer المحافظات"""

    def test_governorate_serialization(self):
        """اختبار تسلسل بيانات المحافظة"""
        governorate = baker.make(
            Governorate,
            name="القاهرة",
            name_en="Cairo",
            code="CAI",
            population=10000000,
            area=606.0
        )
        
        serializer = GovernorateSerializer(governorate)
        data = serializer.data
        
        assert data['name'] == "القاهرة"
        assert data['name_en'] == "Cairo"
        assert data['code'] == "CAI"
        assert data['population'] == 10000000
        assert data['area'] == 606.0

    def test_governorate_deserialization(self):
        """اختبار إلغاء تسلسل بيانات المحافظة"""
        data = {
            'name': 'الجيزة',
            'name_en': 'Giza',
            'code': 'GIZ',
            'population': 8000000,
            'area': 85153.0
        }
        
        serializer = GovernorateSerializer(data=data)
        assert serializer.is_valid()
        
        governorate = serializer.save()
        assert governorate.name == 'الجيزة'
        assert governorate.code == 'GIZ'


@pytest.mark.django_db
class TestDistrictSerializer:
    """اختبارات Serializer الدوائر الانتخابية"""

    def test_district_serialization(self):
        """اختبار تسلسل بيانات الدائرة الانتخابية"""
        governorate = baker.make(Governorate, name="القاهرة")
        district = baker.make(
            District,
            name="مصر الجديدة",
            governorate=governorate,
            number=1,
            description="دائرة مصر الجديدة الانتخابية"
        )
        
        serializer = DistrictSerializer(district)
        data = serializer.data
        
        assert data['name'] == "مصر الجديدة"
        assert data['governorate_name'] == "القاهرة"
        assert data['number'] == 1
        assert data['description'] == "دائرة مصر الجديدة الانتخابية"


@pytest.mark.django_db
class TestPoliticalPartySerializer:
    """اختبارات Serializer الأحزاب السياسية"""

    def test_party_serialization(self):
        """اختبار تسلسل بيانات الحزب السياسي"""
        from datetime import date
        party = baker.make(
            PoliticalParty,
            name="الحزب الوطني الديمقراطي",
            name_en="National Democratic Party",
            abbreviation="الوطني",
            color="#FF0000",
            founded_date=date(1978, 7, 11),
            description="الحزب الوطني الديمقراطي المصري"
        )
        
        serializer = PoliticalPartySerializer(party)
        data = serializer.data
        
        assert data['name'] == "الحزب الوطني الديمقراطي"
        assert data['name_en'] == "National Democratic Party"
        assert data['abbreviation'] == "الوطني"
        assert data['color'] == "#FF0000"
        assert data['description'] == "الحزب الوطني الديمقراطي المصري"


@pytest.mark.django_db
class TestRepresentativeListSerializer:
    """اختبارات Serializer قائمة النواب"""

    def test_representative_list_serialization(self):
        """اختبار تسلسل قائمة النواب"""
        from datetime import date
        governorate = baker.make(Governorate, name="القاهرة")
        district = baker.make(District, name="مصر الجديدة", governorate=governorate)
        party = baker.make(PoliticalParty, name="الحزب الوطني", color="#FF0000")
        
        representative = baker.make(
            Representative,
            name="أحمد محمد علي",
            gender="male",
            birth_date=date(1980, 1, 1),
            profession="مهندس",
            district=district,
            party=party,
            status="candidate",
            rating=4.5,
            rating_count=100,
            solved_complaints=80,
            received_complaints=100,
            is_distinguished=True
        )
        
        serializer = RepresentativeListSerializer(representative)
        data = serializer.data
        
        assert data['name'] == "أحمد محمد علي"
        assert data['gender'] == "male"
        assert data['profession'] == "مهندس"
        assert data['party_name'] == "الحزب الوطني"
        assert data['party_color'] == "#FF0000"
        assert data['district_name'] == "مصر الجديدة"
        assert data['governorate'] == "القاهرة"
        assert data['status'] == "candidate"
        assert float(data['rating']) == 4.5
        assert data['success_rate'] == 80.0
        assert data['is_distinguished'] is True
        assert data['age'] is not None


@pytest.mark.django_db
class TestRepresentativeDetailSerializer:
    """اختبارات Serializer تفاصيل النواب"""

    def test_representative_detail_serialization(self):
        """اختبار تسلسل تفاصيل النائب"""
        governorate = baker.make(Governorate, name="القاهرة")
        district = baker.make(District, name="مصر الجديدة", governorate=governorate)
        party = baker.make(PoliticalParty, name="الحزب الوطني")
        
        representative = baker.make(
            Representative,
            name="أحمد محمد علي",
            slug="ahmed-mohamed-ali",
            district=district,
            party=party,
            bio="سيرة ذاتية مفصلة",
            electoral_program="برنامج انتخابي شامل"
        )
        
        # إضافة صور وإنجازات وأخبار
        baker.make('RepresentativeImage', representative=representative, _quantity=2)
        baker.make('Achievement', representative=representative, _quantity=3)
        baker.make('News', representative=representative, _quantity=2)
        
        serializer = RepresentativeDetailSerializer(representative)
        data = serializer.data
        
        assert data['name'] == "أحمد محمد علي"
        assert data['slug'] == "ahmed-mohamed-ali"
        assert data['bio'] == "سيرة ذاتية مفصلة"
        assert data['electoral_program'] == "برنامج انتخابي شامل"
        assert 'governorate' in data
        assert 'district' in data
        assert 'party' in data
        assert len(data['additional_images']) == 2
        assert len(data['achievement_list']) == 3
        assert len(data['news']) == 2


@pytest.mark.django_db
class TestRepresentativeCreateUpdateSerializer:
    """اختبارات Serializer إنشاء وتحديث النواب"""

    def test_representative_creation(self):
        """اختبار إنشاء نائب جديد"""
        governorate = baker.make(Governorate)
        district = baker.make(District, governorate=governorate)
        party = baker.make(PoliticalParty)
        
        data = {
            'name': 'نائب جديد',
            'gender': 'male',
            'profession': 'محامي',
            'district': district.id,
            'party': party.id,
            'status': 'candidate',
            'electoral_number': '12345',
            'phone': '+201234567890',
            'email': 'representative@example.com'
        }
        
        serializer = RepresentativeCreateUpdateSerializer(data=data)
        assert serializer.is_valid()
        
        representative = serializer.save()
        assert representative.name == 'نائب جديد'
        assert representative.gender == 'male'
        assert representative.district == district
        assert representative.party == party

    def test_electoral_number_validation(self):
        """اختبار التحقق من صحة الرقم الانتخابي"""
        data = {
            'name': 'نائب جديد',
            'gender': 'male',
            'electoral_number': 'abc123'  # رقم غير صحيح
        }
        
        serializer = RepresentativeCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'electoral_number' in serializer.errors

    def test_phone_validation(self):
        """اختبار التحقق من صحة رقم الهاتف"""
        data = {
            'name': 'نائب جديد',
            'gender': 'male',
            'phone': 'invalid-phone'  # رقم غير صحيح
        }
        
        serializer = RepresentativeCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'phone' in serializer.errors

    def test_valid_phone_formats(self):
        """اختبار أشكال صحيحة لأرقام الهاتف"""
        valid_phones = [
            '+201234567890',
            '01234567890',
            '012-345-67890',
            '012 345 67890'
        ]
        
        for phone in valid_phones:
            data = {
                'name': 'نائب جديد',
                'gender': 'male',
                'phone': phone
            }
            
            serializer = RepresentativeCreateUpdateSerializer(data=data)
            # يجب أن يكون الهاتف صحيحاً (لا توجد أخطاء في phone)
            if not serializer.is_valid():
                assert 'phone' not in serializer.errors


@pytest.mark.django_db
class TestSearchSerializer:
    """اختبارات Serializer البحث"""

    def test_search_serializer_validation(self):
        """اختبار التحقق من صحة بيانات البحث"""
        data = {
            'q': 'أحمد',
            'governorate': 'القاهرة',
            'gender': 'male',
            'status': 'candidate',
            'is_distinguished': True,
            'min_rating': 3.0,
            'max_rating': 5.0,
            'ordering': '-rating'
        }
        
        serializer = SearchSerializer(data=data)
        assert serializer.is_valid()
        
        validated_data = serializer.validated_data
        assert validated_data['q'] == 'أحمد'
        assert validated_data['governorate'] == 'القاهرة'
        assert validated_data['gender'] == 'male'
        assert validated_data['is_distinguished'] is True

    def test_search_serializer_invalid_gender(self):
        """اختبار نوع غير صحيح"""
        data = {
            'gender': 'invalid'
        }
        
        serializer = SearchSerializer(data=data)
        assert not serializer.is_valid()
        assert 'gender' in serializer.errors

    def test_search_serializer_invalid_status(self):
        """اختبار حالة غير صحيحة"""
        data = {
            'status': 'invalid'
        }
        
        serializer = SearchSerializer(data=data)
        assert not serializer.is_valid()
        assert 'status' in serializer.errors

    def test_search_serializer_invalid_ordering(self):
        """اختبار ترتيب غير صحيح"""
        data = {
            'ordering': 'invalid_field'
        }
        
        serializer = SearchSerializer(data=data)
        assert not serializer.is_valid()
        assert 'ordering' in serializer.errors

    def test_search_serializer_empty_data(self):
        """اختبار بيانات فارغة (يجب أن تكون صحيحة)"""
        data = {}
        
        serializer = SearchSerializer(data=data)
        assert serializer.is_valid()
        
        # يجب أن يكون الترتيب الافتراضي موجود
        validated_data = serializer.validated_data
        assert validated_data.get('ordering') == '-is_distinguished'
