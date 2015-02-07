from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mediaupload.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'ajaxupload.views.index', name='index'),
    url(r'^upload/new', 'ajaxupload.views.get_upload_id', name='get_upload_id'),
    url(r'^upload/', 'ajaxupload.views.upload', name='upload'),
    url(r'^pdfviewerjs', 'ajaxupload.views.pdfviewer', name='pdfviewer')
)
