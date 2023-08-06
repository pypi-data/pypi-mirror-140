from django.shortcuts import render, redirect, get_object_or_404
from development.forms import ProjectForm, ImageProjectForm
from django.http import JsonResponse
from django.contrib import messages
from development.models import *
from custom.utils import getnewid, getjustnewid, hash_md5, getlastid
from django.db.models import Count
from xhtml2pdf import pisa
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from datetime import date
import numpy as np
from administration.models import Year
from main.decorators import allowed_users
from employee.models import *
# ===================charts===================
def convertMonthNumberToText(number):
	if number == 1:
		return "Janeiru"
	elif number == 2:
		return "Fevreiru"
	elif number == 3:
		return "Marsu"
	elif number == 4:
		return "Abril"
	elif number == 5:
		return "Maiu"
	elif number == 6:
		return "Junhu"
	elif number == 7:
		return "Julhu"
	elif number == 8:
		return "Augustu"
	elif number == 9:
		return "Setembru"
	elif number == 10:
		return "Outubru"
	elif number == 11:
		return "Novembru"
	elif number == 12:
		return "Dezembru"
	
# Create your views here.


@login_required
def DevelopmentDashboard(request):
	try:
		empuser = EmployeeUser.objects.get(user = request.user)
		employee = Employee.objects.get(employeeuser=empuser)
	except:
		print('You are admin')
	countproject = Project.objects.filter(municipality=employee.municipality, administrativepost=employee.administrativepost, village=employee.village).count()
	countactivity = Activity.objects.filter(municipality=employee.municipality, administrativepost=employee.administrativepost, village=employee.village).count()

	context = {'title': 'Painel Dezenvolvimentu', 'employee':employee, 'development':"active",
	'countproject':countproject,'countactivity':countactivity}
	return render(request, 'development/dashboard_development.html', context)

@login_required
def project_charts(request):
	# currentYear = date.today().year
	try:
		empuser = EmployeeUser.objects.get(user = request.user)
		employee = Employee.objects.get(employeeuser=empuser)
	except:
		print('You are admin')
	labels = []
	data = []
	# currentYear2 = get_object_or_404(Year,year=currentYear)
	querysets = Project.objects.filter(municipality=employee.municipality, administrativepost=employee.administrativepost, village=employee.village)\
	.values('year__year').annotate(count=Count('id'))
	for entry in querysets:
		# month = convertMonthNumberToText(entry['datetime__year'])
		labels.append(entry['year__year'])
		data.append(entry['count'])
	# print(data)
	return JsonResponse(data={
		'labels':labels,
		'data':data,
		})

@login_required
def activity_charts(request):
	currentYear = date.today().year
	try:
		empuser = EmployeeUser.objects.get(user = request.user)
		employee = Employee.objects.get(employeeuser=empuser)
	except:
		print('You are admin')
	labels = []
	data = []
	# currentYear2 = get_object_or_404(Year,year=currentYear)
	querysets = Activity.objects.filter(municipality=employee.municipality, administrativepost=employee.administrativepost, village=employee.village)\
	.values('year__year').annotate(count=Count('id'))
	for entry in querysets:
		# month = convertMonthNumberToText(entry['date__month'])
		labels.append(entry['year__year'])
		data.append(entry['count'])
	# print(data)
	return JsonResponse(data={
		'labels':labels,
		'data':data,
		})

@login_required
def ProjectList(request):
	group = request.user.groups.all()[0].name
	try:
		empuser = EmployeeUser.objects.get(user = request.user)
		employee = Employee.objects.get(employeeuser=empuser)
	except:
		print('You are admin')
	objects = Project.objects.filter(municipality=employee.municipality, administrativepost=employee.administrativepost, village=employee.village)
	context = {
		'title': 'Lista Projetu','page':"view", 'group': group,
		'objects': objects,'project1':"active"
	}
	return render(request,'project/list.html', context)

@login_required
def ProjectDetail(request, hashed):
	group = request.user.groups.all()[0].name
	objects = Project.objects.get(hashed=hashed)
	imageproject = ImageProject.objects.filter(project=objects)
	fundNational = FundNational.objects.filter(project=objects)
	fundMunicipality = FundMunicipality.objects.filter(project=objects)
	fundOng = FundONG.objects.filter(project=objects)
	fundVolunteer = FundVolunteer.objects.filter(project=objects)
	data = []
	for i in fundNational:
		data.append({'fund': 'Nasional', 'name': i, 'hashed': i.hashed, 'amount': i.national_amount, 'material': i.national_material})
	for j in fundMunicipality:
		data.append({'fund': 'Munisípiu', 'name': j, 'hashed': j.hashed, 'amount': j.municipality_amount, 'material': j.municipality_material})
	for k in fundOng:
		data.append({'fund': 'ONG', 'name': k, 'hashed': k.hashed, 'amount': k.ong_amount, 'material': k.ong_material})
	for l in fundVolunteer:
		data.append({'fund': 'Voluntáriu', 'name': l, 'hashed': l.hashed, 'amount': l.volunteer_amount, 'material': l.volunteer_material})
	result = np.array(data)
	total = []
	for r  in result:
		total.append(r['amount'])
	total_amount = np.sum(total)
	context =  {
		'objects':objects,'title': 'Detalla Projetu', 'project1':"active",'group': group,
		'result': result, 'total': total_amount, 'fundNational':fundNational,
		'imageproject':imageproject
	}
	return render(request, 'project/detail.html', context)


@login_required
@allowed_users(['sec', 'admin', 'xefe'])
def ProjectAdd(request):
	municipality = Municipality.objects.all()
	if request.method == 'POST':
		newid = getjustnewid(Project)

		form = ProjectForm(request.POST, request.FILES)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.id = newid
			instance.user = request.user
			user = get_object_or_404(EmployeeUser,user__id=request.user.id)
			instance.municipality = user.employee.municipality
			instance.administrativepost = user.employee.administrativepost
			instance.village = user.employee.village
			instance.save()
			messages.success(request, f'Susesu Kria Projetu!' )
			return redirect('development:project-add-fund', instance.hashed)
	else:
		form = ProjectForm()	
	context = {'form':form, 'municipality':municipality, 'project1':"active",
	'title':'Adisiona Projetu'}
	return render(request, 'project/add.html', context)

@login_required
@allowed_users(['sec', 'admin', 'xefe'])
def ImageProjectAdd(request, hashed):
	project = get_object_or_404(Project, hashed=hashed)
	if request.method == 'POST':
		newid = getjustnewid(ImageProject)
		images = request.FILES.getlist('image')

		form = ImageProjectForm(request.POST, request.FILES)
		if form.is_valid():
			for f in images:
				files = ImageProject(project_id=project.id, image=f,user=request.user)
				files.save()
			messages.success(request, f'Susesu Kria Aneksu Imajen!' )
			return redirect('development:project-viewdetail', project.hashed)
	else:
		form = ImageProjectForm()	
	context = {'form':form, 'project1':"active",
	'title':'Aneksu Imajen ba Projetu %s' % (project.name)}
	return render(request, 'project/add1.html', context)

@login_required
@allowed_users(['sec'])
def ProjectEdit(request, hashed):
	project = Project.objects.get(hashed=hashed)

	form = ProjectForm(instance=project)
	if request.method == 'POST':
		form = ProjectForm(request.POST, instance=project)
		if form.is_valid():
			form.save()
			messages.success(request, f'Susesu Altera Projetu' )
			return redirect('development:project-list')

	context = {'title':'Altera Projetu','form':form, 'page': 'altera','project1':"active"}
	return render(request, 'project/add.html', context)

@login_required
@allowed_users(allowed_roles=['sec', 'xefe'])
def DeleteProject(request, hashed):
	project = get_object_or_404(Project,hashed=hashed)
	project.delete()
	messages.success(request, f'Dadus projetu {project.name} Hamoos ho Susesu.')
	return redirect('development:project-list')
