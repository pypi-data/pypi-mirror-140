from django.urls import path
from django.urls.conf import include
from . import views

app_name = 'report'


urlpatterns = [
    path('', views.report_dashboard, name='report-dashboard'),
    path('get-administrativepost', views.load_posts, name='get-administrativepost'),

    # path('get-administrativepost', views.report_dashboard, name='get-administrativepost'),
]
