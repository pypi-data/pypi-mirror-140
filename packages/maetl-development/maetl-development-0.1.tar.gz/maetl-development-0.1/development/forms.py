from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Button, HTML
from django.db.models import Q
from .models import *
from custom.models import *

class DateInput(forms.DateInput):
	input_type = 'date'

class DateDateField(forms.DateField):
	input_type = 'date'

class ProjectForm(forms.ModelForm):
	obs = forms.CharField(label="Observasaun", widget=forms.Textarea(attrs={"rows":2}), required=False)
	class Meta:
		model = Project
		fields = ['name','company','start_period','end_period','benefit','year','obs']

		widgets = {
		'start_period': DateInput(attrs={'type': 'date'}),
		'end_period': DateInput(attrs={'type': 'date'}),
		}
	def __init__(self, *args, **kwargs):
		super(ProjectForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('name', css_class='form-group col-md-6 mb-0'),			
				Column('company', css_class='form-group col-md-6 mb-0'),
			),
			Row(
				Column('start_period', css_class='form-group col-md-6 mb-0'),
				Column('end_period', css_class='form-group col-md-6 mb-0'),
			),
			Row(
				Column('year', css_class='form-group col-md-6 mb-0'),
				Column('benefit', css_class='form-group col-md-6 mb-0'),				
			),
			Row(
				Column('obs', css_class='form-group col-md-12 mb-1'),				
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="rai"><span class="btn-label"><i class='fa fa-save'></i></span>Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class ImageProjectForm(forms.ModelForm):
	class Meta:
		model = ImageProject
		fields = ['image']
		widgets = {
		'image':forms.FileInput(attrs={'class':'form-control-file','multiple':True}),
		}

	def __init__(self, *args, **kwargs):
		super(ImageProjectForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(			
			Row(
				Column('image', css_class='form-group col-md-12 mb-1'),				
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="rai"><span class="btn-label"><i class='fa fa-save'></i></span>Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class ActivityForm(forms.ModelForm):
	obs = forms.CharField(label="Observasaun", widget=forms.Textarea(attrs={"rows":2}), required=False)

	class Meta:
		model = Activity
		fields = ['name','date','place','participation','year',
		'benefit','obs']

		widgets = {
		'date': DateInput(attrs={'type': 'date'}),
		# 'image':forms.FileInput(attrs={'class':'form-control-file','multiple':True})
		}
	def __init__(self, *args, **kwargs):
		super(ActivityForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('name', css_class='form-group col-md-6 mb-0'),			
				Column('date', css_class='form-group col-md-6 mb-0'),
			),
			Row(
				Column('place', css_class='form-group col-md-6 mb-0'),
				Column('participation', css_class='form-group col-md-6 mb-0'),
			),
			Row(
				Column('year', css_class='form-group col-md-6 mb-0'),
				Column('benefit', css_class='form-group col-md-6 mb-0'),
			),
			Row(
				Column('obs', css_class='form-group col-md-12 mb-0'),
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="rai"><span class="btn-label"><i class='fa fa-save'></i></span>Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class ImageActivityForm(forms.ModelForm):
	class Meta:
		model = ImageActivity
		fields = ['image']
		widgets = {
		'image':forms.FileInput(attrs={'class':'form-control-file','multiple':True}),
		}

	def __init__(self, *args, **kwargs):
		super(ImageActivityForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(			
			Row(
				Column('image', css_class='form-group col-md-12 mb-1'),				
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="rai"><span class="btn-label"><i class='fa fa-save'></i></span>Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class OngForm(forms.ModelForm):
	class Meta:
		model = ONG
		fields = ['name']
class AgencyForm(forms.ModelForm):
	class Meta:
		model = Agency
		fields = ['name']

class NationalForm(forms.ModelForm):
	class Meta:
		model = National
		fields = ['name', 'code']

class FundMunicipalityForm(forms.ModelForm):
	class Meta:
		model = FundMunicipality
		fields = ['municipality', 'municipality_material', 'municipality_amount']

class FundNationalForm(forms.ModelForm):
	class Meta:
		model = FundNational
		fields = ['national', 'national_material', 'national_amount']

class FundONGForm(forms.ModelForm):
	class Meta:
		model = FundONG
		fields = ['ong', 'ong_material', 'ong_amount']

class FundVolunteerForm(forms.ModelForm):
	class Meta:
		model = FundVolunteer
		fields = ['volunteer', 'volunteer_material', 'volunteer_amount']

class FundCommunityContributeForm(forms.ModelForm):
	class Meta:
		model = FundCommunityContribute
		fields = ['community_contribute', 'communitycontribute_material', 'communitycontribute_amount']

class FundAgencyForm(forms.ModelForm):
	class Meta:
		model = FundAgency
		fields = ['agency', 'agency_material', 'agency_amount']

class CompanyForm(forms.ModelForm):
	class Meta:
		model = Company
		fields = ['name']
