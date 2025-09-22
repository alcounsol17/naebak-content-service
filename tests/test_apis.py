"""
اختبارات APIs لخدمة المحتوى - منصة نائبك.كوم
"""

import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from model_bakery import baker
from content.models import (
    Governorate, District, PoliticalParty, Representative
)


@pytest.mark.django_db
class TestHealthCheckAPI:
    """اختبارات API فحص الصحة"""

    def test_health_check(self):
        """اختبار فحص صحة الخدمة"""
        client = APIClient()
        url = reverse('health_check')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'
        assert response.data['service'] == 'naebak-content-service'


@pytest.mark.django_db
class TestGovernorateAPI:
    """اختبارات API المحافظات"""

    def test_list_governorates(self):
        """اختبار قائمة المحافظات"""
        # إنشاء محافظات تجريبية
        baker.make(Governorate, name="القاهرة", is_active=True)
        baker.make(Governorate, name="الجيزة", is_active=True)
        baker.make(Governorate, name="الإسكندرية", is_active=False)  # غير نشطة
        
        client = APIClient()
        url = reverse('governorate-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # المحافظات النشطة فقط

    def test_search_governorates(self):
        """اختبار البحث في المحافظات"""
        baker.make(Governorate, name="القاهرة", is_active=True)
        baker.make(Governorate, name="الجيزة", is_active=True)
        
        client = APIClient()
        url = reverse('governorate-list')
        response = client.get(url, {'search': 'القاهرة'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == "القاهرة"


@pytest.mark.django_db
class TestDistrictAPI:
    """اختبارات API الدوائر الانتخابية"""

    def test_list_districts(self):
        """اختبار قائمة الدوائر الانتخابية"""
        governorate = baker.make(Governorate, name="القاهرة")
        baker.make(District, name="مصر الجديدة", governorate=governorate, is_active=True)
        baker.make(District, name="المعادي", governorate=governorate, is_active=True)
        
        client = APIClient()
        url = reverse('district-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_filter_districts_by_governorate(self):
        """اختبار فلترة الدوائر حسب المحافظة"""
        cairo = baker.make(Governorate, name="القاهرة")
        giza = baker.make(Governorate, name="الجيزة")
        
        baker.make(District, name="مصر الجديدة", governorate=cairo)
        baker.make(District, name="الدقي", governorate=giza)
        
        client = APIClient()
        url = reverse('district-list')
        response = client.get(url, {'governorate': 'القاهرة'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == "مصر الجديدة"


@pytest.mark.django_db
class TestPoliticalPartyAPI:
    """اختبارات API الأحزاب السياسية"""

    def test_list_parties(self):
        """اختبار قائمة الأحزاب السياسية"""
        baker.make(PoliticalParty, name="الحزب الوطني", is_active=True)
        baker.make(PoliticalParty, name="حزب الوفد", is_active=True)
        
        client = APIClient()
        url = reverse('party-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2


@pytest.mark.django_db
class TestRepresentativeAPI:
    """اختبارات API النواب والمرشحين"""

    def setup_method(self):
        """إعداد البيانات للاختبارات"""
        self.governorate = baker.make(Governorate, name="القاهرة")
        self.district = baker.make(District, governorate=self.governorate, number=1)
        self.party = baker.make(PoliticalParty, name="الحزب الوطني")

    def test_list_representatives(self):
        """اختبار قائمة النواب والمرشحين"""
        baker.make(
            Representative,
            name="أحمد محمد",
            district=self.district,
            party=self.party,
            is_active=True
        )
        baker.make(
            Representative,
            name="فاطمة علي",
            district=self.district,
            is_active=True
        )
        
        client = APIClient()
        url = reverse('representative-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        assert 'stats' in response.data

    def test_filter_representatives_by_gender(self):
        """اختبار فلترة النواب حسب النوع"""
        baker.make(
            Representative,
            name="أحمد محمد",
            gender="male",
            district=self.district,
            is_active=True
        )
        baker.make(
            Representative,
            name="فاطمة علي",
            gender="female",
            district=self.district,
            is_active=True
        )
        
        client = APIClient()
        url = reverse('representative-list')
        response = client.get(url, {'gender': 'male'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == "أحمد محمد"

    def test_filter_representatives_by_governorate(self):
        """اختبار فلترة النواب حسب المحافظة"""
        giza_gov = baker.make(Governorate, name="الجيزة")
        giza_district = baker.make(District, governorate=giza_gov)
        
        baker.make(
            Representative,
            name="أحمد محمد",
            district=self.district,  # القاهرة
            is_active=True
        )
        baker.make(
            Representative,
            name="محمد أحمد",
            district=giza_district,  # الجيزة
            is_active=True
        )
        
        client = APIClient()
        url = reverse('representative-list')
        response = client.get(url, {'governorate': 'القاهرة'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == "أحمد محمد"

    def test_filter_representatives_distinguished(self):
        """اختبار فلترة المرشحين المميزين"""
        baker.make(
            Representative,
            name="أحمد محمد",
            district=self.district,
            is_distinguished=True,
            is_active=True
        )
        baker.make(
            Representative,
            name="محمد أحمد",
            district=self.district,
            is_distinguished=False,
            is_active=True
        )
        
        client = APIClient()
        url = reverse('representative-list')
        response = client.get(url, {'is_distinguished': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == "أحمد محمد"

    def test_representative_detail(self):
        """اختبار تفاصيل نائب/مرشح"""
        representative = baker.make(
            Representative,
            name="أحمد محمد",
            slug="ahmed-mohamed",
            district=self.district,
            party=self.party,
            is_active=True
        )
        
        client = APIClient()
        url = reverse('representative-detail', kwargs={'slug': 'ahmed-mohamed'})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "أحمد محمد"
        assert response.data['slug'] == "ahmed-mohamed"

    def test_representative_detail_not_found(self):
        """اختبار عدم وجود نائب/مرشح"""
        client = APIClient()
        url = reverse('representative-detail', kwargs={'slug': 'non-existent'})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_representative(self):
        """اختبار إنشاء نائب/مرشح جديد"""
        client = APIClient()
        url = reverse('representative-create')
        data = {
            'name': 'نائب جديد',
            'gender': 'male',
            'district': self.district.id,
            'party': self.party.id,
            'status': 'candidate'
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Representative.objects.filter(name='نائب جديد').exists()


@pytest.mark.django_db
class TestSearchAPI:
    """اختبارات API البحث"""

    def setup_method(self):
        """إعداد البيانات للاختبارات"""
        self.governorate = baker.make(Governorate, name="القاهرة")
        self.district = baker.make(District, governorate=self.governorate)

    def test_search_representatives(self):
        """اختبار البحث في النواب"""
        baker.make(
            Representative,
            name="أحمد محمد علي",
            profession="مهندس",
            district=self.district,
            is_active=True
        )
        baker.make(
            Representative,
            name="فاطمة أحمد",
            profession="طبيبة",
            district=self.district,
            is_active=True
        )
        
        client = APIClient()
        url = reverse('search')
        response = client.get(url, {'q': 'أحمد'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # كلاهما يحتوي على "أحمد"

    def test_search_with_filters(self):
        """اختبار البحث مع الفلاتر"""
        baker.make(
            Representative,
            name="أحمد محمد",
            gender="male",
            district=self.district,
            is_active=True
        )
        baker.make(
            Representative,
            name="أحمد علي",
            gender="female",
            district=self.district,
            is_active=True
        )
        
        client = APIClient()
        url = reverse('search')
        response = client.get(url, {'q': 'أحمد', 'gender': 'male'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == "أحمد محمد"


@pytest.mark.django_db
class TestStatsAPI:
    """اختبارات API الإحصائيات"""

    def test_representatives_stats(self):
        """اختبار إحصائيات النواب"""
        governorate = baker.make(Governorate)
        district = baker.make(District, governorate=governorate)
        
        # إنشاء نواب ومرشحين متنوعين
        baker.make(
            Representative,
            district=district,
            gender="male",
            status="candidate",
            is_distinguished=True,
            is_active=True
        )
        baker.make(
            Representative,
            district=district,
            gender="female",
            status="elected",
            is_distinguished=False,
            is_active=True
        )
        
        client = APIClient()
        url = reverse('representative-stats')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_representatives'] == 2
        assert response.data['total_candidates'] == 1
        assert response.data['total_elected'] == 1
        assert response.data['distinguished_count'] == 1
        assert response.data['male_count'] == 1
        assert response.data['female_count'] == 1


@pytest.mark.django_db
class TestFilterOptionsAPI:
    """اختبارات API خيارات الفلاتر"""

    def test_get_filter_options(self):
        """اختبار الحصول على خيارات الفلاتر"""
        baker.make(Governorate, name="القاهرة", is_active=True)
        baker.make(Governorate, name="الجيزة", is_active=True)
        baker.make(PoliticalParty, name="الحزب الوطني", is_active=True)
        baker.make(PoliticalParty, name="حزب الوفد", is_active=True)
        
        client = APIClient()
        url = reverse('filter-options')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['governorates']) == 2
        assert len(response.data['parties']) == 2
        assert len(response.data['genders']) == 2
        assert len(response.data['statuses']) == 3
        assert "القاهرة" in response.data['governorates']
        assert "الحزب الوطني" in response.data['parties']


@pytest.mark.django_db
class TestRepresentativeBySlugAPI:
    """اختبارات API الحصول على نائب بالـ slug"""

    def test_get_representative_by_slug(self):
        """اختبار الحصول على نائب بالـ slug"""
        governorate = baker.make(Governorate)
        district = baker.make(District, governorate=governorate)
        representative = baker.make(
            Representative,
            name="أحمد محمد",
            slug="ahmed-mohamed",
            district=district,
            is_active=True
        )
        
        client = APIClient()
        url = reverse('representative-by-slug', kwargs={'slug': 'ahmed-mohamed'})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "أحمد محمد"
        assert response.data['slug'] == "ahmed-mohamed"

    def test_get_representative_by_slug_not_found(self):
        """اختبار عدم وجود نائب بالـ slug"""
        client = APIClient()
        url = reverse('representative-by-slug', kwargs={'slug': 'non-existent'})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # يمكن أن يكون 'error' أو 'detail' حسب إعدادات DRF
        assert 'error' in response.data or 'detail' in response.data
