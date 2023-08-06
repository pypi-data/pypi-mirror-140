from django.shortcuts import render, redirect,get_object_or_404
from development.forms import ActivityForm, ImageActivityForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from custom.utils import getnewid, getjustnewid, hash_md5, getlastid
from django.contrib.auth.decorators import login_required
from custom.models import *
from development.models import *
import numpy as np
from main.decorators import allowed_users
from employee.models import *

@login_required
def ActivityList(request):
    group = request.user.groups.all()[0].name
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    activity = Activity.objects.filter(municipality=employee.municipality, administrativepost=employee.administrativepost, village=employee.village)
    context = {
        'title': 'Lista Atividade', 'activity1':"active",'group':group,
         'page':"view", 'objects':activity
    }
    return render(request, 'activity/list.html', context)

@login_required
@allowed_users(['sec', 'admin', 'xefe'])
def ActivityAdd(request):
    if request.method == 'POST':
        newid = getjustnewid(Activity)
        form = ActivityForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.id = newid
            instance.user = request.user
            user = get_object_or_404(EmployeeUser,user__id=request.user.id)
            instance.municipality = user.employee.municipality
            instance.administrativepost = user.employee.administrativepost
            instance.village = user.employee.village
            instance.save()
            # print(instance.hashed)
            messages.success(request, f'Susesu Kria Atividade' )
            return redirect('development:activity-add-fund', instance.hashed)
    else:
        form = ActivityForm()
    context = {'title':'Adisiona Atividade', 'activity1':"active",
     'page':"addactivity", 'form':form}
    return render(request, 'activity/add.html', context)

@login_required
@allowed_users(['sec', 'admin', 'xefe'])
def ImageActivityAdd(request, hashed):
    activity = get_object_or_404(Activity, hashed=hashed)
    if request.method == 'POST':
        newid = getjustnewid(Activity)
        images = request.FILES.getlist('image')
        form = ImageActivityForm(request.POST, request.FILES)
        if form.is_valid():
            for image in images:
                files = ImageActivity(activity_id=activity.id, image=image, user=request.user)
                files.save()
            messages.success(request, f'Susesu Kria Aneksu Imajen!' )
            return redirect('development:activity-detail', activity.hashed)
    else:
        form = ImageActivityForm()
    context = {'title':'Aneksu Imajen ba Atividade %s' % (activity.name), 'activity1':"active",
     'page':"addactivity", 'form':form}
    return render(request, 'activity/add1.html', context)

@login_required
@allowed_users('sec')
def ActivityEdit(request, hashed):
    group = request.user.groups.all()[0].name
    activity = Activity.objects.get(hashed=hashed)

    form = ActivityForm(instance=activity)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, f'Susesu Altera Atividade' )
            return redirect('development:activity-list')

    context = {'title':'Altera Atividade', 'activity1':"active", 'group': group,
     'form':form}
    return render(request, 'activity/add.html', context)

@login_required
def ActivityDetail(request, hashed):
    group = request.user.groups.all()[0].name
    objects = Activity.objects.get(hashed=hashed)
    imageactivity = ImageActivity.objects.filter(activity=objects)
    fundNational = FundNational.objects.filter(activity=objects)
    fundMunicipality = FundMunicipality.objects.filter(activity=objects)
    fundContribute = FundCommunityContribute.objects.filter(activity=objects)
    fundAgency = FundAgency.objects.filter(activity=objects)
    data = []
    for i in fundNational:
        data.append({'fund': 'Nasional', 'name': i, 'hashed': i.hashed, 'amount': i.national_amount, 'material': i.national_material})
    for j in fundMunicipality:
        data.append({'fund': 'Municipio', 'name': j, 'hashed': j.hashed, 'amount': j.municipality_amount, 'material': j.municipality_material})
    for k in fundContribute:
        data.append({'fund': 'Kontribuisaun Komunidade', 'name': k, 'hashed': k.hashed, 'amount': k.communitycontribute_amount, 'material': k.communitycontribute_material})
    for l in fundAgency:
        data.append({'fund': 'Ajensia', 'name': l, 'hashed': l.hashed, 'amount': l.agency_amount, 'material': l.agency_material})
    result = np.array(data)
    total = []
    for r  in result:
        total.append(r['amount'])
    total_amount = np.sum(total)
    context =  {
		'objects':objects,'title': 'Detalla Atividade', 'group':group,
		'result': result, 'total': total_amount, 'activity1':"active",'imageactivity':imageactivity
	}
    return render(request, 'activity/detail.html', context)

@login_required
@allowed_users(allowed_roles=['sec', 'xefe'])
def DeleteActivity(request, hashed):
    activity = get_object_or_404(Activity,hashed=hashed)
    activity.delete()
    messages.success(request, f'Dadus Atividade {activity.name} Hamoos ho Susesu.')
    return redirect('development:activity-list')
