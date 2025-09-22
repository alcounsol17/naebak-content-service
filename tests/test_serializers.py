"""
اختبارات Serializers لخدمة المحتوى - منصة نائبك.كوم (محدثة)
"""

import pytest
from django.test import TestCase
from model_bakery import baker
from content.models import (
    Governorate, District, PoliticalParty, Representative,
    StaticPage, Banner, ColorSettings, FAQ
)
from content.serializers import (
    GovernorateSerializer, DistrictSerializer, PoliticalPartySerializer,
    RepresentativeListSerializer, RepresentativeDetailSerializer,
    RepresentativeCreateSerializer, StaticPageSerializer,
    BannerSerializer, ColorSettingsSerializer, FAQSerializer
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


@pytest.mark.django_db
class TestDistrictSerializer:
    """اختبارات Serializer الدوائر الانتخابية"""
    
    def test_district_serialization(self):
        """اختبار تسلسل بيانات الدائرة"""
        governorate = baker.make(Governorate, name="الجيزة")
        district = baker.make(
            District,
            name="دائرة الهرم",
            governorate=governorate,
            number=1
        )
        
        serializer = DistrictSerializer(district)
        data = serializer.data
        
        assert data['name'] == "دائرة الهرم"
        assert data['governorate_name'] == "الجيزة"
        assert data['number'] == 1


@pytest.mark.django_db
class TestPoliticalPartySerializer:
    """اختبارات Serializer الأحزاب السياسية"""
    
    def test_party_serialization(self):
        """اختبار تسلسل بيانات الحزب"""
        party = baker.make(
            PoliticalParty,
            name="حزب الحرية والعدالة",
            abbreviation="حع",
            color="#FF5722"
        )
        
        serializer = PoliticalPartySerializer(party)
        data = serializer.data
        
        assert data['name'] == "حزب الحرية والعدالة"
        assert data['abbreviation'] == "حع"
        assert data['color'] == "#FF5722"


@pytest.mark.django_db
class TestRepresentativeListSerializer:
    """اختبارات Serializer قائمة النواب"""
    
    def test_representative_list_serialization(self):
        """اختبار تسلسل بيانات قائمة النواب"""
        governorate = baker.make(Governorate, name="الإسكندرية")
        district = baker.make(District, name="دائرة المنتزه", governorate=governorate)
        party = baker.make(PoliticalParty, name="الحزب الوطني", color="#4CAF50")
        
        representative = baker.make(
            Representative,
            name="أحمد محمد علي",
            gender="male",
            profession="مهندس",
            district=district,
            party=party,
            rating=4.5,
            is_distinguished=True
        )
        
        serializer = RepresentativeListSerializer(representative)
        data = serializer.data
        
        assert data['name'] == "أحمد محمد علي"
        assert data['gender'] == "male"
        assert data['profession'] == "مهندس"
        assert data['governorate_name'] == "الإسكندرية"
        assert data['party_name'] == "الحزب الوطني"
        assert data['party_color'] == "#4CAF50"
        assert data['rating'] == "4.5"
        assert data['is_distinguished'] is True


@pytest.mark.django_db
class TestRepresentativeDetailSerializer:
    """اختبارات Serializer تفاصيل النواب"""
    
    def test_representative_detail_serialization(self):
        """اختبار تسلسل تفاصيل النائب"""
        governorate = baker.make(Governorate, name="أسوان")
        district = baker.make(District, name="دائرة أسوان", governorate=governorate)
        party = baker.make(PoliticalParty, name="حزب المستقبل")
        
        representative = baker.make(
            Representative,
            name="فاطمة أحمد",
            gender="female",
            district=district,
            party=party,
            bio="سيرة ذاتية مفصلة",
            electoral_program="برنامج انتخابي شامل"
        )
        
        serializer = RepresentativeDetailSerializer(representative)
        data = serializer.data
        
        assert data['name'] == "فاطمة أحمد"
        assert data['gender'] == "female"
        assert data['district_name'] == "دائرة أسوان"
        assert data['governorate_name'] == "أسوان"
        assert data['party_name'] == "حزب المستقبل"
        assert data['bio'] == "سيرة ذاتية مفصلة"
        assert data['electoral_program'] == "برنامج انتخابي شامل"


@pytest.mark.django_db
class TestRepresentativeCreateSerializer:
    """اختبارات Serializer إنشاء النواب"""
    
    def test_representative_creation(self):
        """اختبار إنشاء نائب جديد"""
        governorate = baker.make(Governorate, name="المنيا")
        district = baker.make(District, governorate=governorate)
        party = baker.make(PoliticalParty)
        
        data = {
            'name': 'محمد سعد',
            'gender': 'male',
            'profession': 'طبيب',
            'district': district.id,
            'party': party.id,
            'status': 'candidate',
            'bio': 'سيرة ذاتية'
        }
        
        serializer = RepresentativeCreateSerializer(data=data)
        assert serializer.is_valid()
        
        representative = serializer.save()
        assert representative.name == 'محمد سعد'
        assert representative.gender == 'male'
        assert representative.profession == 'طبيب'


@pytest.mark.django_db
class TestStaticPageSerializer:
    """اختبارات Serializer الصفحات الثابتة"""
    
    def test_static_page_serialization(self):
        """اختبار تسلسل الصفحة الثابتة"""
        page = baker.make(
            StaticPage,
            page_type='contact',
            title='اتصل بنا',
            content='محتوى صفحة اتصل بنا',
            order=1
        )
        
        serializer = StaticPageSerializer(page)
        data = serializer.data
        
        assert data['page_type'] == 'contact'
        assert data['title'] == 'اتصل بنا'
        assert data['content'] == 'محتوى صفحة اتصل بنا'
        assert data['order'] == 1


@pytest.mark.django_db
class TestBannerSerializer:
    """اختبارات Serializer البنرات"""
    
    def test_banner_serialization(self):
        """اختبار تسلسل البنر"""
        representative = baker.make(Representative, name="علي حسن")
        banner = baker.make(
            Banner,
            name="بنر الصفحة الرئيسية",
            banner_type='main',
            representative=representative,
            is_default=True
        )
        
        serializer = BannerSerializer(banner)
        data = serializer.data
        
        assert data['name'] == "بنر الصفحة الرئيسية"
        assert data['banner_type'] == 'main'
        assert data['representative_name'] == "علي حسن"
        assert data['is_default'] is True


@pytest.mark.django_db
class TestColorSettingsSerializer:
    """اختبارات Serializer إعدادات الألوان"""
    
    def test_color_settings_serialization(self):
        """اختبار تسلسل إعدادات الألوان"""
        color_setting = baker.make(
            ColorSettings,
            color_type='primary_green',
            color_value='#4CAF50',
            description='اللون الأخضر الأساسي'
        )
        
        serializer = ColorSettingsSerializer(color_setting)
        data = serializer.data
        
        assert data['color_type'] == 'primary_green'
        assert data['color_value'] == '#4CAF50'
        assert data['description'] == 'اللون الأخضر الأساسي'


@pytest.mark.django_db
class TestFAQSerializer:
    """اختبارات Serializer الأسئلة الشائعة"""
    
    def test_faq_serialization(self):
        """اختبار تسلسل السؤال الشائع"""
        faq = baker.make(
            FAQ,
            question="كيف يمكنني التواصل مع النائب؟",
            answer="يمكنك التواصل عبر الصفحة الشخصية",
            category="التواصل",
            order=1
        )
        
        serializer = FAQSerializer(faq)
        data = serializer.data
        
        assert data['question'] == "كيف يمكنني التواصل مع النائب؟"
        assert data['answer'] == "يمكنك التواصل عبر الصفحة الشخصية"
        assert data['category'] == "التواصل"
        assert data['order'] == 1
