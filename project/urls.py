from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin
from filebrowser.sites import site

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if 'tinymce' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^tinymce/', include('tinymce.urls')),
        url(r'^admin/filebrowser/', include(site.urls)),
    )
