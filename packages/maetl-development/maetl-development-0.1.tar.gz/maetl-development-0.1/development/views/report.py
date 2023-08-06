from django.shortcuts import render, redirect, resolve_url, HttpResponse, get_object_or_404
from development.forms import ProjectForm
from development.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from custom.models import *
import numpy as np
import pandas as pd
from django.db.models import Q
from custom.utils import getnewid, getjustnewid, hash_md5, getlastid
from django.db.models import Avg, Count, Min, Sum
# report
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

from employee.models import *


@login_required
def ReportList(request):
    year = Year.objects.all()
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    if request.method == 'POST':
        developmentReport = request.POST.get('developmentReport')
        year = request.POST.get('year')
        if developmentReport == "C1":
            # print(year)
            project = Project.objects.filter(year__year=year,municipality=employee.municipality, administrativepost=employee.administrativepost, village=employee.village)
            fNational = FundNational.objects.all()
            fMunicipality = FundMunicipality.objects.all()
            fOng = FundONG.objects.all()
            fVolunteer = FundVolunteer.objects.all()
            total = []
            for pro in project:
                fn,fm,fo,fv,total_fund =   [],[],[],[], []
                fn = FundNational.objects.filter(project=pro.id).aggregate(Sum('national_amount'))
                fm = FundMunicipality.objects.filter(project=pro.id).aggregate(Sum('municipality_amount'))
                fo = FundONG.objects.filter(project=pro.id).aggregate(Sum('ong_amount'))
                fv = FundVolunteer.objects.filter(project=pro.id).aggregate(Sum('volunteer_amount'))
                if fn['national_amount__sum']:
                    total_fund.append(fn['national_amount__sum'])
                if fm['municipality_amount__sum']:
                    total_fund.append(fm['municipality_amount__sum'])
                if fo['ong_amount__sum']:
                    total_fund.append(fo['ong_amount__sum'])
                if fv['volunteer_amount__sum']:
                    total_fund.append(fv['volunteer_amount__sum'])
                total.append(np.sum(total_fund))
            df1 = pd.DataFrame(project)
            df1['total_amount'] = total
    
            data = {
                'title': 'Relatóriu Projetu', 
                'objects': df1, 'employee': employee,
                'fNational': fNational, 'fMunicipality': fMunicipality, 'fOng':fOng, 'fVolunteer':fVolunteer,
                'total_amount_national':total,'year':year
            }
            if 'print' in request.POST:
                data["page"] = "print"
                return render(request, 'reports/print/project.html', data)
            elif 'excel' in request.POST:
                data["page"] = "excel"
                return render(request, 'reports/print/project.html', data)

        if developmentReport == "C2":
            activity = Activity.objects.filter(year__year=year,municipality=employee.municipality, administrativepost=employee.administrativepost, village=employee.village)
            fNational = FundNational.objects.all()
            fMunicipality = FundMunicipality.objects.all()
            fCommunity = FundCommunityContribute.objects.all()
            fAgency = FundAgency.objects.all()
            total = []
            for ac in activity:
                fn,fm,fc,fa,total_fund =   [],[],[],[], []
                fn = FundNational.objects.filter(activity=ac.id).aggregate(Sum('national_amount'))
                fm = FundMunicipality.objects.filter(activity=ac.id).aggregate(Sum('municipality_amount'))
                fc = FundCommunityContribute.objects.filter(activity=ac.id).aggregate(Sum('communitycontribute_amount'))
                fa = FundAgency.objects.filter(activity=ac.id).aggregate(Sum('agency_amount'))
                if fn['national_amount__sum']:
                    total_fund.append(fn['national_amount__sum'])
                if fm['municipality_amount__sum']:
                    total_fund.append(fm['municipality_amount__sum'])
                if fc['communitycontribute_amount__sum']:
                    total_fund.append(fc['communitycontribute_amount__sum'])
                if fa['agency_amount__sum']:
                    total_fund.append(fa['agency_amount__sum'])
                total.append(np.sum(total_fund))
            df1 = pd.DataFrame(activity)
            df1['total_amount'] = total
    
            data = {
                'title': 'Relatóriu Atividade', 
                'objects': df1, 'employee': employee,
                'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
                'total_amount_national':total,'year':year
            }
            if 'print' in request.POST:
                data["page"] = "print"
                return render(request, 'reports/print/activity.html', data)
            elif 'excel' in request.POST:
                data["page"] = "excel"
                return render(request, 'reports/print/activity.html', data)

    context = {'year':year,'title':"Livru Relatóriu Sira", 'report':"active"}
    return render(request, 'reports/report_dashboard.html', context)




