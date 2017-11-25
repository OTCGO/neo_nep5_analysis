from django.conf.urls import url,include
from views import index

urlpatterns = [
    url(r'^wallet/', include('wallet.urls')),
    url(r'^api/', include('core.urls')),
    url(r'^$', index),
]
