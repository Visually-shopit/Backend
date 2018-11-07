from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'shopitbackend.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^handleUpload/','main.views.handleUpload',name='handleUpload'),
    url(r'^test','main.views.test',name='test'),

]
