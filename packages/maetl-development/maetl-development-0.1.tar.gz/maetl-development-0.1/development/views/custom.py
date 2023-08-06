import datetime
from django.http import request
from django.shortcuts import get_object_or_404, redirect, render
from custom_development.models import *
from development.forms import AgencyForm, NationalForm, OngForm, CompanyForm
from django.contrib import messages
from custom.utils import getjustnewid
from django.contrib.auth.decorators import login_required
from custom.models import *
from development.models import *
from main.decorators import allowed_users


@login_required
def CustomNationalList(request):
    group = request.user.groups.all()[0].name
    fields = ['Nu.', 'Naran', 'Code', 'Asaun']
    objects = National.objects.all()
    context = {
        'title': 'Lista Dadus Custom Nasional',
        'objects': objects, 'group':group,
        'fields': fields, 'nationalactive':"active"
    }
    return render(request, 'custom/national_list.html', context)


@login_required
@allowed_users(['sec', 'admin', 'xefe'])
def CustomNationalAdd(request):
    if request.method == 'POST':
        newid = getjustnewid(National)
        form = NationalForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.id = newid
            instance.save()
            messages.success(request, f'Susesu Kria Nasional' )
            return redirect('development:custom-national-lists')
    else: 
        form = NationalForm()
    context = {
        'title': 'Aumenta Dadus Custom Nasional',
        'form': form, 'nationalactive':"active"
    }
    return render(request, 'custom/national_form.html', context)

@login_required
@allowed_users(['sec', 'admin'])
def CustomNationalUpdate(request, pk):
    objects = get_object_or_404(National, id=pk)
    if request.method == 'POST':
        form = NationalForm(request.POST, instance=objects)
        if form.is_valid():
            form.save()
            messages.success(request, f'Susesu Altera Nasional' )
            return redirect('development:custom-national-lists')
    else:
        form = NationalForm(instance=objects)
    context = {
        'title': 'Altera Dadus Custom Nasional',
        'form': form, 'nationalactive':"active"
    }
    return render(request, 'custom/national_form.html', context)


@login_required
def CustomONGList(request):
    group = request.user.groups.all()[0].name
    objects = ONG.objects.all()
    fields = ['Nu.', 'Naran', 'Asaun']
    
    # field_names = list(model._meta.get_fields())
    # titles = [f.verbose_name for f in field_names]
    context = {
        'title': 'Lista Dadus Custom ONG',
        'objects': objects, 'group': group,
        'fields': fields,'ongactive':"active"
    }
    return render(request, 'custom/ong_list.html', context)


@login_required
@allowed_users(['sec', 'admin', 'xefe'])
def CustomONGAdd(request):
    if request.method == 'POST':
        newid = getjustnewid(ONG)
        form = OngForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.id = newid
            instance.save()
            messages.success(request, f'Susesu Kria ONG' )
            return redirect('development:custom-ong-lists')
    else: 
        form = OngForm()
    context = {
        'title': 'Aumenta Dadus Custom ONG',
        'form': form, 'ongactive':"active"
    }
    return render(request, 'custom/ong_form.html', context)

@login_required
@allowed_users(['sec', 'admin'])
def CustomONGUpdate(request, pk):
    objects = get_object_or_404(ONG, id=pk)
    if request.method == 'POST':
        form = OngForm(request.POST, instance=objects)
        if form.is_valid():
            form.save()
            messages.success(request, f'Susesu Altera ONG' )
            return redirect('development:custom-ong-lists')
    else:
        form = OngForm(instance=objects)
    context = {
        'title': 'Altera Dadus Custom ONG',
        'form': form,'ongactive':"active"
    }
    return render(request, 'custom/ong_form.html', context)


@login_required
def CustomAgencyList(request):
    group = request.user.groups.all()[0].name
    objects = Agency.objects.all()
    fields = ['Nu.', 'Naran', 'Asaun']
    
    # field_names = list(model._meta.get_fields())
    # titles = [f.verbose_name for f in field_names]
    context = {
        'title': 'Lista Dadus Custom Ajénsia',
        'objects': objects, 'group': group,
        'fields': fields,'agencyactive':"active"
    }
    return render(request, 'custom/agency_list.html', context)


@login_required
@allowed_users(['sec', 'admin', 'xefe'])
def CustomAgencyAdd(request):
    if request.method == 'POST':
        newid = getjustnewid(Agency)
        form = AgencyForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.id = newid
            instance.save()
            messages.success(request, f'Susesu Kria Ajénsia' )
            return redirect('development:custom-agency-lists')
    else: 
        form = AgencyForm()
    context = {
        'title': 'Aumenta Dadus Custom Ajénsia',
        'form': form,'agencyactive':"active"
    }
    return render(request, 'custom/agency_form.html', context)

@login_required
@allowed_users(['sec', 'admin'])
def CustomAgencypdate(request, pk):
    objects = get_object_or_404(Agency, id=pk)
    if request.method == 'POST':
        form = AgencyForm(request.POST, instance=objects)
        if form.is_valid():
            form.save()
            messages.success(request, f'Susesu Altera Ajénsia' )
            return redirect('development:custom-agency-lists')
    else:
        form = AgencyForm(instance=objects)
    context = {
        'title': 'Altera Dadus Custom Ajénsia',
        'form': form, 'agencyactive':"active"
    }
    return render(request, 'custom/agency_form.html', context)


@login_required
def CustomCompanyList(request):
    group = request.user.groups.all()[0].name
    company = Company.objects.all()
    fields = ['Nu.', 'Naran', 'Asaun']
    context = {'title':'Lista Dadus Custom Kompañia','objects':company, 'group': group,
    'fields':fields,'companyactive':"active"}
    return render(request, 'custom/company_list.html', context)

@login_required
@allowed_users(['sec', 'admin', 'xefe'])
def CustomCompanyAdd(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(request, f'Susesu Kria Kompañia')
            return redirect('development:custom-company-lists')
    else: 
        form = CompanyForm()
    context = {
        'title': 'Aumenta Dadus Custom Kompañia',
        'form': form,'companyactive':"active"
    }
    return render(request, 'custom/company_form.html', context)

@login_required
@allowed_users(['sec', 'admin'])
def CustomCompanyUpdate(request, pk):
    objects = get_object_or_404(Company, id=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=objects)
        if form.is_valid():
            form.save()
            messages.success(request, f'Susesu Altera Kompañia' )
            return redirect('development:custom-company-lists')
    else:
        form = CompanyForm(instance=objects)
    context = {
        'title': 'Altera Dadus Custom Kompañia',
        'form': form,'companyactive':"active"
    }
    return render(request, 'custom/company_form.html', context)

@login_required
def load_postu(request):
    id_municipality = request.GET.get('municipality')
    post = AdministrativePost.objects.filter(municipality=id_municipality).order_by('id')
    context = {'post':post,'load_ajax':'post'}

    return render(request, 'custom/dependent_select.html',context)

@login_required
def load_suku(request):
    id_post = request.GET.get('post')
    village = Village.objects.filter(post=id_post).order_by('id')
    context = {'village':village,'load_ajax':'village'}

    return render(request, 'custom/dependent_select.html',context)



