from django.urls import path
from . import views

app_name = 'report_population'


urlpatterns = [
   #relatorio Jeral grafiku 
   path('reportb1jeralMunicipality',views.reportb1jeralMunicipality, name='reportb1jeralMunicipality'),  
   path('reportb1jeralPostadministrative/<id>',views.reportb1jeralPostadministrative, name='reportb1jeralPostadministrative'),
   path('reportb1jeralVillage/<id>',views.reportb1jeralVillage, name='reportb1jeralVillage'),
   path('reportb1jeralAldeia/<id>',views.reportb1jeralAldeia, name='reportb1jeralAldeia'),
 

#relatorio jeral ba print
   path('reportb1_printjeral',views.reportb1_printjeral, name='reportb1_printjeral'),
   path('reportb1_printPostadministrative/<id>',views.reportb1_printPostadministrative, name='reportb1_printPostadministrative'),
   path('reportb1_printVillage/<id>',views.reportb1_printVillage, name='reportb1_printVillage'),
   path('reportb1_printAldeia/<id>',views.reportb1_printAldeia, name='reportb1_printAldeia'),
   
   path('popchar_munisipality',views.popchar_munisipality, name='popchar_munisipality'),
   path('popchar_postadministrative/<id>',views.popchar_postadministrative, name='popchar_postadministrative'),
   path('popchar_village/<id>',views.popchar_village, name='popchar_village'),
   path('popchar_aldeia/<id>',views.popchar_aldeia, name='popchar_aldeia'),
   path('popchar_familymunisipality',views.popchar_familymunisipality, name='popchar_familymunisipality'),
   path('popchar_familypostadministrative/<id>',views.popchar_familypostadministrative, name='popchar_familypostadministrative'),
   path('popchar_familyvillage/<id>',views.popchar_familyvillage, name='popchar_familyvillage'),
   path('popchar_familyaldeia/<id>',views.popchar_familyaldeia, name='popchar_familyaldeia'),
   
   
   path('reportb4jeral',views.reportb4jeral, name='reportb4jeral'),
   path('reportb4jeral_print',views.reportb4jeral_print, name='reportb4jeral_print'),
   path('reportb4jeralmunisipiu_print',views.reportb4jeralmunisipiu_print, name='reportb4jeralmunisipiu_print'),  
   path('reportb4jeralpostu_print',views.reportb4jeralpostu_print, name='reportb4jeralpostu_print'),      
   path('reportb4jeralsuku_print',views.reportb4jeralsuku_print, name='reportb4jeralsuku_print'),      
    
    



]
