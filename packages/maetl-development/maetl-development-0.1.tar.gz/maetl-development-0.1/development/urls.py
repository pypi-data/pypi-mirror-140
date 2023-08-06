from django.urls import path
from . import views
app_name = 'development'

urlpatterns =[
	path('', views.DevelopmentDashboard, name='dashboard-development'),
	path('load-postu/', views.load_postu, name='ajax_load_postu'),
    path('load-suku/', views.load_suku, name='ajax_load_suku'),

    # Projects
	path('project/list/', views.ProjectList, name='project-list'),
	path('project/add/', views.ProjectAdd, name='project-add'),
	path('project/edit/<str:hashed>/', views.ProjectEdit, name='project-edit'),
	path('project/viewdetail/<str:hashed>/', views.ProjectDetail, name='project-viewdetail'),
	path('project/add/image/<str:hashed>/', views.ImageProjectAdd, name='project-add-image'),
	path('project/delete/<str:hashed>/', views.DeleteProject, name='project-delete'),

	
	# Fundus Project
	path('project/add/fund/<str:hashed>/', views.FundProjectAdd, name='project-add-fund'),
	path('project/add1/fund1/<str:hashed>/', views.FundProjectAdd1, name='project-add1-fund1'),
	path('project/fundnational/list/', views.FundNationalList, name='fundnational-project-list'),
	path('project/fundnational/edit/<str:hashed>/', views.FundNationalEdit, name='fundnational-project-edit'),
	path('project/fundmunicipality/list/', views.FundMunicipalityList, name='fundmunicipality-project-list'),
	path('project/fundmunicipality/edit/<str:hashed>/', views.FundMunicipalityEdit, name='fundmunicipality-project-edit'),
	path('project/fundong/list/', views.FundONGList, name='fundong-project-list'),
	path('project/fundong/edit/<str:hashed>/', views.FundONGEdit, name='fundong-project-edit'),
	path('project/fundavolunteer/edit/<str:hashed>/', views.FundVolunteerEdit, name='fundvolunteer-project-edit'),

	# REPORTS
	path('report/list/', views.ReportList, name='report-list'),


	#Chart
	path('project-charts/', views.project_charts, name="project-charts"),
	path('activity-charts/', views.activity_charts, name="activity-charts"),

	# Activities
	path('activity/list/', views.ActivityList, name='activity-list'),
	path('activity/add/', views.ActivityAdd, name='activity-add'),
	path('activity/edit/<str:hashed>/', views.ActivityEdit, name='activity-edit'),
	path('activity/viewdetail/<str:hashed>/', views.ActivityDetail, name='activity-detail'),
	path('activity/add/image/<str:hashed>/', views.ImageActivityAdd, name='activity-add-image'),
	path('activity/delete/<str:hashed>/', views.DeleteActivity, name='activity-delete'),

	# Fundus Activities
	path('activity/add/fund/<str:hashed>/', views.FundActivityAdd, name='activity-add-fund'),
	path('activity/add1/fund1/<str:hashed>/', views.FundActivityAdd1, name='activity-add1-fund1'),
	path('activity/fundagency/list/', views.FundAgencyList, name='fundagency-activity-list'),
	path('activity/fundagency/edit/<str:hashed>/', views.FundAgencyEdit, name='fundagency-activity-edit'),
	path('activity/fundcommunity/edit/<str:hashed>/', views.FundCommunityContributeEdit, name='fundcommunity-activity-edit'),


	# CUSTOM NASIONAL
	path('custom/national/list/', views.CustomNationalList, name='custom-national-lists'),
	path('custom/national/add/', views.CustomNationalAdd, name='custom-national-add'),
	path('custom/national/update/<str:pk>', views.CustomNationalUpdate, name='custom-national-update'),

	# CUSTOM ONG
	path('custom/ong/list/', views.CustomONGList, name='custom-ong-lists'),
	path('custom/ong/add/', views.CustomONGAdd, name='custom-ong-add'),
	path('custom/ong/update/<str:pk>', views.CustomONGUpdate, name='custom-ong-update'),

	# CUSTOM AJENSIA
	path('custom/agency/list/', views.CustomAgencyList, name='custom-agency-lists'),
	path('custom/agency/add/', views.CustomAgencyAdd, name='custom-agency-add'),
	path('custom/agency/update/<str:pk>', views.CustomAgencypdate, name='custom-agency-update'),

	# CUSTOM KOMPANIA
	path('custom/company/list/', views.CustomCompanyList, name='custom-company-lists'),
	path('custom/company/add/', views.CustomCompanyAdd, name='custom-company-add'),
	path('custom/company/update/<str:pk>/', views.CustomCompanyUpdate, name='custom-company-update'),

]