"""
اختبارات النماذج لخدمة المحتوى - منصة نائبك.كوم
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from model_bakery import baker
from content.models import (
    Governorate, District, PoliticalParty, Representative,
    RepresentativeImage, Achievement, News
)


@pytest.mark.django_db
class TestGovernorateModel:
    """اختبارات نموذج المحافظات"""

    def test_create_governorate(self):
        """اختبار إنشاء محافظة"""
        governorate = baker.make(
            Governorate,
            name="القاهرة",
            name_en="Cairo",
            code="CAI",
            population=10000000
        )
        assert governorate.name == "القاهرة"
        assert governorate.code == "CAI"
        assert str(governorate) == "القاهرة"

    def test_governorate_unique_name(self):
        """اختبار تفرد اسم المحافظة"""
        baker.make(Governorate, name="القاهرة", code="CAI")
        
        with pytest.raises(IntegrityError):
            baker.make(Governorate, name="القاهرة", code="CAI2")

    def test_governorate_unique_code(self):
        """اختبار تفرد كود المحافظة"""
        baker.make(Governorate, name="القاهرة", code="CAI")
        
        with pytest.raises(IntegrityError):
            baker.make(Governorate, name="الجيزة", code="CAI")


@pytest.mark.django_db
class TestDistrictModel:
    """اختبارات نموذج الدوائر الانتخابية"""

    def test_create_district(self):
        """اختبار إنشاء دائرة انتخابية"""
        governorate = baker.make(Governorate, name="القاهرة")
        district = baker.make(
            District,
            name="مصر الجديدة",
            governorate=governorate,
            number=1
        )
        assert district.name == "مصر الجديدة"
        assert district.governorate == governorate
        assert str(district) == "مصر الجديدة - القاهرة"

    def test_district_unique_together(self):
        """اختبار تفرد الدائرة في المحافظة"""
        governorate = baker.make(Governorate, name="القاهرة")
        baker.make(District, governorate=governorate, number=1)
        
        with pytest.raises(IntegrityError):
            baker.make(District, governorate=governorate, number=1)


@pytest.mark.django_db
class TestPoliticalPartyModel:
    """اختبارات نموذج الأحزاب السياسية"""

    def test_create_party(self):
        """اختبار إنشاء حزب سياسي"""
        party = baker.make(
            PoliticalParty,
            name="الحزب الوطني الديمقراطي",
            abbreviation="الوطني",
            color="#FF0000"
        )
        assert party.name == "الحزب الوطني الديمقراطي"
        assert party.color == "#FF0000"
        assert str(party) == "الحزب الوطني الديمقراطي"

    def test_party_unique_name(self):
        """اختبار تفرد اسم الحزب"""
        baker.make(PoliticalParty, name="الحزب الوطني")
        
        with pytest.raises(IntegrityError):
            baker.make(PoliticalParty, name="الحزب الوطني")


@pytest.mark.django_db
class TestRepresentativeModel:
    """اختبارات نموذج النواب والمرشحين"""

    def test_create_representative(self):
        """اختبار إنشاء نائب/مرشح"""
        governorate = baker.make(Governorate, name="القاهرة")
        district = baker.make(District, governorate=governorate, number=1)
        party = baker.make(PoliticalParty, name="الحزب الوطني")
        
        representative = baker.make(
            Representative,
            name="أحمد محمد علي",
            gender="male",
            district=district,
            party=party,
            status="candidate"
        )
        
        assert representative.name == "أحمد محمد علي"
        assert representative.gender == "male"
        assert representative.governorate == governorate
        assert str(representative) == f"أحمد محمد علي - {district}"

    def test_representative_slug_generation(self):
        """اختبار توليد slug تلقائياً"""
        governorate = baker.make(Governorate)
        district = baker.make(District, governorate=governorate)
        
        representative = Representative.objects.create(
            name="أحمد محمد علي",
            gender="male",
            district=district
        )
        
        assert representative.slug is not None
        assert len(representative.slug) > 0

    def test_representative_age_calculation(self):
        """اختبار حساب العمر"""
        from datetime import date
        governorate = baker.make(Governorate)
        district = baker.make(District, governorate=governorate)
        
        representative = baker.make(
            Representative,
            district=district,
            birth_date=date(1980, 1, 1)
        )
        
        assert representative.age is not None
        assert representative.age > 40

    def test_representative_success_rate(self):
        """اختبار حساب معدل النجاح"""
        governorate = baker.make(Governorate)
        district = baker.make(District, governorate=governorate)
        
        representative = baker.make(
            Representative,
            district=district,
            solved_complaints=80,
            received_complaints=100
        )
        
        assert representative.success_rate == 80.0

    def test_representative_success_rate_zero_complaints(self):
        """اختبار معدل النجاح عند عدم وجود شكاوى"""
        governorate = baker.make(Governorate)
        district = baker.make(District, governorate=governorate)
        
        representative = baker.make(
            Representative,
            district=district,
            solved_complaints=0,
            received_complaints=0
        )
        
        assert representative.success_rate == 0.0

    def test_representative_absolute_url(self):
        """اختبار الرابط المطلق"""
        governorate = baker.make(Governorate)
        district = baker.make(District, governorate=governorate)
        
        representative = baker.make(
            Representative,
            district=district,
            slug="ahmed-mohamed-ali"
        )
        
        assert representative.get_absolute_url() == "/ahmed-mohamed-ali/"


@pytest.mark.django_db
class TestRepresentativeImageModel:
    """اختبارات نموذج صور النواب"""

    def test_create_representative_image(self):
        """اختبار إنشاء صورة نائب"""
        governorate = baker.make(Governorate)
        district = baker.make(District, governorate=governorate)
        representative = baker.make(Representative, district=district)
        
        image = baker.make(
            RepresentativeImage,
            representative=representative,
            caption="صورة رسمية"
        )
        
        assert image.representative == representative
        assert image.caption == "صورة رسمية"
        assert str(image) == f"صورة {representative.name}"


@pytest.mark.django_db
class TestAchievementModel:
    """اختبارات نموذج الإنجازات"""

    def test_create_achievement(self):
        """اختبار إنشاء إنجاز"""
        from datetime import date
        governorate = baker.make(Governorate)
        district = baker.make(District, governorate=governorate)
        representative = baker.make(Representative, district=district)
        
        achievement = baker.make(
            Achievement,
            representative=representative,
            title="افتتاح مستشفى جديد",
            date=date.today()
        )
        
        assert achievement.representative == representative
        assert achievement.title == "افتتاح مستشفى جديد"
        assert str(achievement) == f"افتتاح مستشفى جديد - {representative.name}"


@pytest.mark.django_db
class TestNewsModel:
    """اختبارات نموذج الأخبار"""

    def test_create_news(self):
        """اختبار إنشاء خبر"""
        governorate = baker.make(Governorate)
        district = baker.make(District, governorate=governorate)
        representative = baker.make(Representative, district=district)
        
        news = baker.make(
            News,
            representative=representative,
            title="اجتماع مع المواطنين",
            content="تم عقد اجتماع مع المواطنين لمناقشة احتياجاتهم"
        )
        
        assert news.representative == representative
        assert news.title == "اجتماع مع المواطنين"
        assert str(news) == f"اجتماع مع المواطنين - {representative.name}"

    def test_news_published_date_auto(self):
        """اختبار تاريخ النشر التلقائي"""
        governorate = baker.make(Governorate)
        district = baker.make(District, governorate=governorate)
        representative = baker.make(Representative, district=district)
        
        news = baker.make(News, representative=representative)
        
        assert news.published_date is not None
