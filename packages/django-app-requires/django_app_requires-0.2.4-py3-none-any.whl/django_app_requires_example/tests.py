from django.test import TestCase
from django.conf import settings

class TestDjangoAppRequiresExample(TestCase):
    def test01(self):
        assert "django_fastadmin" in settings.INSTALLED_APPS

    def test02(self):
        assert settings.INSTALLED_APPS.count("django_fastadmin") == 1
