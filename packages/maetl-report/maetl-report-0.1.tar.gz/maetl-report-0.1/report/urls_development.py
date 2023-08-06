from django.urls import path
from . import views

app_name = 'report_development'


urlpatterns = [
    path('', views.report_development_dashboard, name='report-development-dashboard'),
    path('project-charts-all/', views.project_charts_all, name="project-charts-all"),
    path('project-charts/<str:year>/', views.project_charts, name="project-charts"),
    path('project-charts-municpality/<str:mun>', views.project_charts_municipality, name="project-charts-municpality"),
    path('project-charts-municpality-year/<str:mun>/<str:year>/', views.project_charts_municipality_year, name="project-charts-municpality-year"),
    path('project-charts-municpality-adminpost/<str:mun>/<str:ap>/', views.project_charts_municipality_adminpost, name="project-charts-municpality-adminpost"),
    path('project-charts-municpality-adminpost-year/<str:mun>/<str:ap>/<str:year>/', views.project_charts_municipality_adminpost_year, name="project-charts-municpality-adminpost-year"),
    path('activity-charts/<str:year>/', views.activity_charts, name="activity-charts"),
    path('activity-charts-all/', views.activity_charts_all, name="activity-charts-all"),
    path('activity-charts-municpality/<str:mun>', views.activity_charts_municipality, name="activity-charts-municpality"),
    path('activity-charts-municpality-year/<str:mun>/<str:year>/', views.activity_charts_municipality_year, name="activity-charts-municpality-year"),
    path('activity-charts-municpality-adminpost/<str:mun>/<str:ap>', views.activity_charts_municipality_adminpost, name="activity-charts-municpality-adminpost"),
    path('activity-charts-municpality-adminpost-year/<str:mun>/<str:ap>/<str:year>', views.activity_charts_municipality_adminpost_year, name="activity-charts-municpality-adminpost-year"),

    # Projects
    path('projectlist-all/', views.ProjectListAll, name='project-list-all'),
    path('projectlist1/<str:mun>/', views.ProjectListmun, name='project-list-mun'),
    path('projectlist2/<str:mun>/<str:year>/', views.ProjectListmunyear, name='project-list-mun-year'),
    path('projectlist3/<str:mun>/<str:post>/', views.ProjectListmunpost, name='project-list-mun-post'),
    path('projectlist4/<str:mun>/<str:post>/<str:year>/', views.ProjectListmunpostyear, name='project-list-mun-post-year'),
    path('projectlist5/<str:mun>/<str:post>/<str:village>/', views.ProjectListmunpostvill, name='project-list-mun-post-village'),
    path('projectlist6/<str:mun>/<str:post>/<str:village>/<str:year>/', views.ProjectListmunpostvillyear, name='project-list-mun-post-village-year'),
    path('projectlist7/<str:year>/', views.ProjectListyear, name='project-list-year'),

     # Excel Projects
    path('excelproject6/<str:mun>/<str:post>/<str:village>/<str:year>/', views.ReportProject6, name='excel6'),
    path('excelproject5/<str:mun>/<str:post>/<str:village>/', views.ReportProject5, name='excel5'),
    path('excelproject4/<str:mun>/<str:post>/<str:year>/', views.ReportProject4, name='excel4'),
    path('excelproject3/<str:mun>/<str:post>/', views.ReportProject3, name='excel3'),
    path('excelproject2/<str:mun>/<str:year>/', views.ReportProject2, name='excel2'),
    path('excelproject1/<str:mun>/', views.ReportProject1, name='excel1'),
    path('excelproject7/<str:year>/', views.ReportProject7, name='excel7'),
    path('excelprojectall/', views.ReportProjectAll, name='excel-all'),

    # Print Projects
    path('printproject6/<str:mun>/<str:post>/<str:village>/<str:year>/', views.PrintProject6, name='print6'),
    path('printproject5/<str:mun>/<str:post>/<str:village>/', views.PrintProject5, name='print5'),
    path('printproject4/<str:mun>/<str:post>/<str:year>/', views.PrintProject4, name='print4'),
    path('printproject3/<str:mun>/<str:post>/', views.PrintProject3, name='print3'),
    path('printproject2/<str:mun>/<str:year>/', views.PrintProject2, name='print2'),
    path('printproject1/<str:mun>/', views.PrintProject1, name='print1'),    
    path('printproject7/<str:year>/', views.PrintProject7, name='print7'),
    path('printprojectall/', views.PrintProjectAll, name='print-all'),

    # Activities
    path('activitylist1/<str:mun>/', views.ActivityListmun, name='activity-list-mun'),
    path('activitylist-all/', views.ActivityListAll, name='activity-list-all'),
    path('activitylist2/<str:mun>/<str:year>/', views.ActivityListmunyear, name='activity-list-mun-year'),
    path('activitylist3/<str:mun>/<str:post>/', views.ActivityListmunpost, name='activity-list-mun-post'),
    path('activitylist4/<str:mun>/<str:post>/<str:year>/', views.ActivityListmunpostyear, name='activity-list-mun-post-year'),
    path('activitylist5/<str:mun>/<str:post>/<str:village>/', views.ActivityListmunpostvillage, name='activity-list-mun-post-village'),
    path('activitylist6/<str:mun>/<str:post>/<str:village>/<str:year>/', views.ActivityListmunpostvillageyear, name='activity-list-mun-post-village-year'),
    path('activitylist7/<str:year>/', views.ActivityListyear, name='activity-list-year'),

    # Print Activies
    path('printactivity1/<str:mun>/', views.PrintActivity1, name='printactivity1'),
    path('printactivity2/<str:mun>/<str:year>/', views.PrintActivity2, name='printactivity2'),
    path('printactivity3/<str:mun>/<str:post>/', views.PrintActivity3, name='printactivity3'),
    path('printactivity4/<str:mun>/<str:post>/<str:year>/', views.PrintActivity4, name='printactivity4'),
    path('printactivity5/<str:mun>/<str:post>/<str:village>/', views.PrintActivity5, name='printactivity5'),
    path('printactivity6/<str:mun>/<str:post>/<str:village>/<str:year>/', views.PrintActivity6, name='printactivity6'),
    path('printactivity7/<str:year>/', views.PrintActivity7, name='printactivity7'),
    path('printactivityall/', views.PrintActivityAll, name='printactivity-all'),

    # Excel Activities
    path('excelactivity1/<str:mun>/', views.ReportActivity1, name='excelactivity1'),
    path('excelactivity2/<str:mun>/<str:year>/', views.ReportActivity2, name='excelactivity2'),
    path('excelactivity3/<str:mun>/<str:post>/', views.ReportActivity3, name='excelactivity3'),
    path('excelactivity4/<str:mun>/<str:post>/<str:year>/', views.ReportActivity4, name='excelactivity4'),
    path('excelactivity5/<str:mun>/<str:post>/<str:village>/', views.ReportActivity5, name='excelactivity5'),
    path('excelactivity6/<str:mun>/<str:post>/<str:village>/<str:year>/', views.ReportActivity6, name='excelactivity6'),
    path('excelactivity7/<str:year>/', views.ReportActivity7, name='excelactivity7'),
    path('excelactivityall/', views.ReportActivityAll, name='excelactivity-all'),

]
