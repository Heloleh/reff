from django.urls import reverse, resolve
from education_platform import urls as project_urls

def test_root_urls_imported():
    assert hasattr(project_urls, 'urlpatterns')
