from django.shortcuts import render, redirect
from django.contrib import messages
from development.forms import FundMunicipalityForm, FundNationalForm,FundONGForm,FundVolunteerForm, FundCommunityContributeForm,FundAgencyForm
from custom.utils import getnewid, getjustnewid, hash_md5, getlastid
from django.contrib.auth.decorators import login_required
from custom.models import *
from development.models import *
from employee.models import *
from django.contrib.auth.models import User

@login_required
def FundNationalList(request):
	national = FundNational.objects.filter(user_id=request.user.id)
	context ={'title':'Fundus Nasional', 'fundnational':"active", 'page':"National",'national':national}
	return render(request, 'fund/fundlist.html', context)

@login_required
def FundMunicipalityList(request):
	municipality = FundMunicipality.objects.filter(user_id=request.user.id)
	context ={'title':'Fundus Munisípiu',
	'fundmunicipality':"active", 'page':"Municipality",'municipality':municipality}
	return render(request, 'fund/fundlist.html', context)

@login_required
def FundONGList(request):
	ong = FundONG.objects.filter(user_id=request.user.id)
	context ={'title':'Fundus ONG', 'fundong':"active", 'page':"ONG",'ong':ong}
	return render(request, 'fund/fundlist.html', context)

@login_required
def FundAgencyList(request):
	agency = FundAgency.objects.filter(user_id=request.user.id)
	context ={'title':'Fundus ONG', 'fundagency':"active", 'page':"Agency",'agency':agency}
	return render(request, 'fund/fundlist.html', context)

@login_required
def FundProjectAdd(request, hashed):
	project = Project.objects.get(hashed=hashed)
	form = FundMunicipalityForm()
	form1 = FundNationalForm()
	form2 = FundONGForm()
	form3 = FundVolunteerForm()

	if request.method == 'POST':
		if request.POST['municipality_amount']:
			newid = getjustnewid(FundMunicipality)

			form = FundMunicipalityForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.id = newid
				instance.project_id = project.id
				instance.user = request.user
				instance.save()

		if request.POST['national_amount']:
			newid1 = getjustnewid(FundNational)

			form1 = FundNationalForm(request.POST)
			if form1.is_valid():
				instance = form1.save(commit=False)
				instance.id = newid1
				instance.project_id = project.id
				instance.user = request.user
				instance.save()

		if request.POST['ong_amount']:
			newid2 = getjustnewid(FundONG)

			form2 = FundONGForm(request.POST)
			if form2.is_valid():
				instance = form2.save(commit=False)
				instance.id = newid2
				instance.project_id = project.id
				instance.user = request.user
				instance.save()

		if request.POST['volunteer_amount']:
			newid3 = getjustnewid(Project)

			form3 = FundVolunteerForm(request.POST)
			if form3.is_valid():
				instance = form3.save(commit=False)
				instance.id = newid3
				instance.project_id = project.id
				instance.user = request.user
				instance.save()
		messages.success(request, f'Susesu Kria Fundus ba Projetu' )
		return redirect('development:project-add-image', project.hashed)

	context = {'title':'Adisiona Fundus Projetu', 'project1':"active", 'page':"addproject", 'project':project, 'form':form,'form1':form1,'form2':form2,'form3':form3}
	return render(request, 'fund/fundprojectadd.html', context)

@login_required
def FundProjectAdd1(request, hashed):
	project = Project.objects.get(hashed=hashed)
	form = FundMunicipalityForm()
	form1 = FundNationalForm()
	form2 = FundONGForm()
	form3 = FundVolunteerForm()

	if request.method == 'POST':
		if request.POST['municipality_amount']:
			newid = getjustnewid(FundMunicipality)

			form = FundMunicipalityForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.id = newid
				instance.project_id = project.id
				instance.user = request.user
				instance.save()

		if request.POST['national_amount']:
			newid1 = getjustnewid(FundNational)

			form1 = FundNationalForm(request.POST)
			if form1.is_valid():
				instance = form1.save(commit=False)
				instance.id = newid1
				instance.project_id = project.id
				instance.user = request.user
				instance.save()

		if request.POST['ong_amount']:
			newid2 = getjustnewid(FundONG)

			form2 = FundONGForm(request.POST)
			if form2.is_valid():
				instance = form2.save(commit=False)
				instance.id = newid2
				instance.project_id = project.id
				instance.user = request.user
				instance.save()

		if request.POST['volunteer_amount']:
			newid3 = getjustnewid(Project)

			form3 = FundVolunteerForm(request.POST)
			if form3.is_valid():
				instance = form3.save(commit=False)
				instance.id = newid3
				instance.project_id = project.id
				instance.user = request.user
				instance.save()
		messages.success(request, f'Susesu Kria Fundus ba Projetu' )
		return redirect('development:project-viewdetail', project.hashed)

	context = {'title':'Adisiona Fundus Projetu', 'project1':"active", 'page':"addproject", 'project':project, 'form':form,'form1':form1,'form2':form2,'form3':form3}
	return render(request, 'fund/fundprojectadd.html', context)

@login_required
def FundNationalEdit(request, hashed):
	fundnational = FundNational.objects.get(hashed=hashed)
	project = fundnational.project
	page = 'editprojectfundnational'
	if fundnational.activity:
		page ='editactivityfundnational'
		project = fundnational.activity
	# page = 'editprojectfundnational'
	form = FundNationalForm(instance=fundnational)
	if request.method == 'POST':
		form = FundNationalForm(request.POST, instance=fundnational)
		if form.is_valid():
			form.save()
			if fundnational.activity == None:
				messages.success(request, f'Susesu Altera Fundus Husi Nasional ba Projetu' )
				return redirect('development:project-viewdetail', fundnational.project.hashed)
			else:
				messages.success(request, f'Susesu Altera Fundus Husi Nasional ba Atividade' )
				return redirect('development:activity-detail', fundnational.activity.hashed)

	context = {'title':'Altera Fundus Husi Nasional', 'page':page, 'project':project, 'form':form}
	return render(request, 'fund/fundprojectadd.html', context)

@login_required
def FundMunicipalityEdit(request, hashed):
	fundmunicipality = FundMunicipality.objects.get(hashed=hashed)
	project = fundmunicipality.project
	page = 'editprojectfundmunicipality'
	if fundmunicipality.activity:
		page ='editactivityfundmunicipality'
		project = fundmunicipality.activity
	
	# print(fundmunicipality.activity)
	form = FundMunicipalityForm(instance=fundmunicipality)
	if request.method == 'POST':
		form = FundMunicipalityForm(request.POST, instance=fundmunicipality)
		if form.is_valid():
			form.save()
			if fundmunicipality.activity == None:
				messages.success(request, f'Susesu Altera Fundus Husi Munisípiu ba Projetu')
				return redirect('development:project-viewdetail', fundmunicipality.project.hashed)
			else:
				messages.success(request, f'Susesu Altera Fundus Husi Munisípiu ba Atividade')
				return redirect('development:activity-detail', fundmunicipality.activity.hashed)

	context = {'title':'Altera Fundus Husi Munisípiu', 'page':page, 'project':project, 'form':form}
	return render(request, 'fund/fundprojectadd.html', context)

def FundONGEdit(request, hashed):
	fundong = FundONG.objects.get(hashed=hashed)
	project = fundong.project
	page = 'editprojectong'
	form = FundONGForm(instance=fundong)
	if request.method == 'POST':
		form = FundONGForm(request.POST, instance=fundong)
		if form.is_valid():
			form.save()
			messages.success(request, f'Susesu Altera Fundus Husi ONG ba Projetu')
			return redirect('development:project-viewdetail', fundong.project.hashed)

	context = {'title':'Altera Fundus Husi ONG ba Projetu', 'page':page, 'project':project,'form':form}
	return render(request, 'fund/fundprojectadd.html', context)

@login_required
def FundVolunteerEdit(request, hashed):
	fundvolunteer = FundVolunteer.objects.get(hashed=hashed)
	project = fundvolunteer.project
	page = 'editprojecvolunteer'
	form = FundVolunteerForm(instance=fundvolunteer)
	if request.method == 'POST':
		form = FundVolunteerForm(request.POST, instance=fundvolunteer)
		if form.is_valid():
			form.save()
			messages.success(request, f'Susesu Altera Fundus Husi Volutariu ba Projetu')
			return redirect('development:project-viewdetail', fundvolunteer.project.hashed)

	context = {'title':'Altera Fundus Husi Voluntariu ba Projetu', 'project':project, 'page':page, 'form':form}
	return render(request, 'fund/fundprojectadd.html', context)

@login_required
def FundActivityAdd(request, hashed):
	activity = Activity.objects.get(hashed=hashed)
	form = FundCommunityContributeForm()
	form1 = FundMunicipalityForm()
	form2 = FundNationalForm()
	form3 = FundAgencyForm()

	if request.method == 'POST':
		if request.POST['communitycontribute_amount']:
			newid = getjustnewid(FundCommunityContribute)

			form = FundCommunityContributeForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.id = newid
				instance.activity_id = activity.id
				instance.user = request.user
				instance.save()

		if request.POST['municipality_amount']:
			newid1 = getjustnewid(FundMunicipality)

			form1 = FundMunicipalityForm(request.POST)
			if form1.is_valid():
				instance = form1.save(commit=False)
				instance.id = newid1
				instance.activity_id = activity.id
				instance.user = request.user
				instance.save()

		if request.POST['national_amount']:
			newid2 = getjustnewid(FundNational)

			form2 = FundNationalForm(request.POST)
			if form2.is_valid():
				instance = form2.save(commit=False)
				instance.id = newid2
				instance.activity_id = activity.id
				instance.user = request.user
				instance.save()

		if request.POST['agency_amount']:
			newid3 = getjustnewid(FundAgency)

			form3 = FundAgencyForm(request.POST)
			if form3.is_valid():
				instance = form3.save(commit=False)
				instance.id = newid3
				instance.activity_id = activity.id
				instance.user = request.user
				instance.save()
		messages.success(request, f'Susesu Kria Fundus ba Atividade' )
		return redirect('development:activity-add-image', activity.hashed)
	context = {'title':'Adisiona Fundus Atividade', 'activity1':"active", 'page':"addactivity", 'activity':activity, 'form':form,'form1':form1,'form2':form2,'form3':form3}
	return render(request, 'fund/fundactivityadd.html', context)

@login_required
def FundActivityAdd1(request, hashed):
	activity = Activity.objects.get(hashed=hashed)
	form = FundCommunityContributeForm()
	form1 = FundMunicipalityForm()
	form2 = FundNationalForm()
	form3 = FundAgencyForm()

	if request.method == 'POST':
		if request.POST['communitycontribute_amount']:
			newid = getjustnewid(FundCommunityContribute)

			form = FundCommunityContributeForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.id = newid
				instance.activity_id = activity.id
				instance.user = request.user
				instance.save()

		if request.POST['municipality_amount']:
			newid1 = getjustnewid(FundMunicipality)

			form1 = FundMunicipalityForm(request.POST)
			if form1.is_valid():
				instance = form1.save(commit=False)
				instance.id = newid1
				instance.activity_id = activity.id
				instance.user = request.user
				instance.save()

		if request.POST['national_amount']:
			newid2 = getjustnewid(FundNational)

			form2 = FundNationalForm(request.POST)
			if form2.is_valid():
				instance = form2.save(commit=False)
				instance.id = newid2
				instance.activity_id = activity.id
				instance.user = request.user
				instance.save()

		if request.POST['agency_amount']:
			newid3 = getjustnewid(FundAgency)

			form3 = FundAgencyForm(request.POST)
			if form3.is_valid():
				instance = form3.save(commit=False)
				instance.id = newid3
				instance.activity_id = activity.id
				instance.user = request.user
				instance.save()
		messages.success(request, f'Susesu Kria Fundus ba Atividade' )
		return redirect('development:activity-detail', activity.hashed)
	context = {'title':'Adisiona Fundus Atividade', 'activity1':"active", 'page':"addactivity", 'activity':activity, 'form':form,'form1':form1,'form2':form2,'form3':form3}
	return render(request, 'fund/fundactivityadd.html', context)

@login_required
def FundAgencyEdit(request, hashed):
	fundagency = FundAgency.objects.get(hashed=hashed)
	activity = fundagency.activity
	form = FundAgencyForm(instance=fundagency)
	if request.method == 'POST':
		form = FundAgencyForm(request.POST, instance=fundagency)
		if form.is_valid():
			form.save()
			messages.success(request, f'Susesu Altera Fundus Husi Ajensia ba Atividade')
			return redirect('development:activity-detail', fundagency.activity.hashed)

	context = {'title':'Altera fundus Atividade Husi Ajensia','activity': activity, 'page':"editactivityagency", 'form':form}
	return render(request, 'fund/fundactivityadd.html', context)

@login_required
def FundCommunityContributeEdit(request, hashed):
	fundcommunitycontribute = FundCommunityContribute.objects.get(hashed=hashed)
	activity = fundcommunitycontribute.activity
	form = FundCommunityContributeForm(instance=fundcommunitycontribute)
	if request.method == 'POST':
		form = FundCommunityContributeForm(request.POST, instance=fundcommunitycontribute)
		if form.is_valid():
			form.save()
			messages.success(request, f'Susesu Altera Fundus Husi Kontribuisaun Komunidade ba Projetu')
			return redirect('development:activity-detail', fundcommunitycontribute.activity.hashed)

	context = {'title':'Altera fundus Atividade Husi Komunidade', 'activity': activity, 'page':"editactivitycommunity", 'form':form}
	return render(request, 'fund/fundactivityadd.html', context)




