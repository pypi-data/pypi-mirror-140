from django.urls import path
from .views import *

app_name = 'report_administration'


urlpatterns = [
    path('', nationalReportDashboard, name='administrationReportDashboard'),
    path('report-livru-administrasaun/', nationalReportFilter, name='nationalReportFilter'),
    path('report-livru-administrasaun/KonselluSuku/<str:Munid>', A1Munisipiu, name='A1Munisipiu'),
    path('report-livru-administrasaun/KonselluSuku/Print/<str:Munid>', PrintA1Munisipiu, name='PrintA1Munisipiu'),
    path('report-livru-administrasaun/XefeSuku/<str:Munid>', A2Munisipiu, name='A2Munisipiu'),
    path('report-livru-administrasaun/XefeSuku/Print/<str:Munid>', PrintA2Munisipiu, name='PrintA2Munisipiu'),
    path('report-livru-administrasaun/Inventaria/<str:Munid>', A3Munisipiu, name='A3Munisipiu'),
    path('report-livru-administrasaun/Inventaria/Print/<str:Munid>', PrintA3Munisipiu, name='PrintA3Munisipiu'),
    path('report-livru-administrasaun/KartaSai/<str:Munid>', A4Munisipiu, name='A4Munisipiu'),
    path('report-livru-administrasaun/KartaSai/Print/<str:Munid>', PrintA4Munisipiu, name='PrintA4Munisipiu'),
	path('report-livru-administrasaun/KartaTama/<str:Munid>', A5Munisipiu, name='A5Munisipiu'),
	path('report-livru-administrasaun/KartaTama/Print/<str:Munid>', PrintA5Munisipiu, name='PrintA5Munisipiu'),
	path('report-livru-administrasaun/Espedisaun/<str:Munid>', A6Munisipiu, name='A6Munisipiu'),
	path('report-livru-administrasaun/Espedisaun/Print/<str:Munid>', PrintA6Munisipiu, name='PrintA6Munisipiu'),
	path('report-livru-administrasaun/LideransaKomunitaria/<str:Munid>', A7Munisipiu, name='A7Munisipiu'),
	path('report-livru-administrasaun/LideransaKomunitaria/Print/<str:Munid>', PrintA7Munisipiu, name='PrintA7Munisipiu'),
	path('report-livru-administrasaun/KeixaSuku/<str:Munid>', A10Munisipiu, name='A10Munisipiu'),
	path('report-livru-administrasaun/KeixaSuku/Print/<str:Munid>', PrintA10Munisipiu, name='PrintA10Munisipiu'),
	path('report-livru-administrasaun/BainakaSuku/<str:Munid>', A11Munisipiu, name='A11Munisipiu'),
	path('report-livru-administrasaun/BainakaSuku/Print/<str:Munid>', PrintA11Munisipiu, name='PrintA11Munisipiu'),

]
