from django.db import models
import hashlib
from django.contrib.auth.models import User
from custom.models import *
from custom_development.models import * 
from django.core.validators import FileExtensionValidator


	
class Project(models.Model):
	name = models.CharField(max_length=300, verbose_name='Naran Projetu', null=True)
	company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Naran Kompañia", null=True)
	start_period = models.DateField(auto_now_add=False, verbose_name='Data Hahu', null=True)
	end_period = models.DateField(auto_now_add=False, verbose_name='Data Remata', null=True)
	benefit = models.CharField(max_length=200, verbose_name='Benefísiu', null=True)
	obs = models.TextField(verbose_name="OBS")
	year = models.ForeignKey(Year, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Tinan")
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, blank=True, null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE, blank=True, null=True)
	village = models.ForeignKey(Village, on_delete=models.CASCADE, blank=True, null=True)	
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Author")
	hashed = models.CharField(max_length=50, null=True, blank=True)
	datetime = models.DateTimeField(auto_now_add=True, null=True)
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

	def save(self, *args, **kwargs):
		self.hashed = hashlib.md5(str(self.id).encode()).hexdigest()
		return super(Project, self).save(*args, **kwargs)

	class Meta:
		verbose_name_plural='C.1. Livru Dadus Projetu Suku'

class ImageProject(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Naran Projetu', null=True)
	image = models.FileField(upload_to='development/project/', null=True, blank=True,
			validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png'])], verbose_name="Aneksu Imajen")
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	datetime = models.DateTimeField(null=True)

	def __str__(self):
		template = '{0.project}'
		return template.format(self)

	class Meta:
		verbose_name_plural='Aneksu Imajen Projetu'	

class FundONG(models.Model):
	ong = models.ForeignKey(ONG, on_delete=models.CASCADE, verbose_name="ONG", null=True, blank=True)
	ong_material = models.CharField(max_length=50, null=True, blank=True, verbose_name="Ajuda Material")
	ong_amount = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True, verbose_name='Total Osan')
	project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Naran Projetu", null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Author")
	hashed = models.CharField(max_length=50, null=True, blank=True)

	def __str__(self):
		template = '{0.ong}'
		return template.format(self)

	def save(self, *args, **kwargs):
		self.hashed = hashlib.md5(str(self.id).encode()).hexdigest()
		return super(FundONG, self).save(*args, **kwargs)

	class Meta:
		verbose_name_plural='Fundus Husi ONG'

class FundVolunteer(models.Model):
	volunteer = models.CharField(max_length=200, verbose_name='Voluntáriu', null=True, blank=True)
	volunteer_material = models.CharField(max_length=50, null=True, blank=True, verbose_name="Ajuda Material")
	volunteer_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name='Total Osan', null=True, blank=True)
	project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Naran Projetu', null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Author")
	hashed = models.CharField(max_length=50, null=True, blank=True)

	def __str__(self):
		template = '{0.volunteer}'
		return template.format(self)
	def save(self, *args, **kwargs):
		self.hashed = hashlib.md5(str(self.id).encode()).hexdigest()
		return super(FundVolunteer, self).save(*args, **kwargs)

	class Meta:
		verbose_name_plural='Fundus Husi Voluntáriu'

class Activity(models.Model):
	date = models.DateField(auto_now_add=False, verbose_name='Data Atividade', null=True)
	name = models.CharField(max_length=300, verbose_name="Naran Atividade", blank=True)
	place = models.CharField(max_length=250, verbose_name='Fatin', blank=True)	
	participation = models.CharField(max_length=255, verbose_name="Partisipasaun", null=True)
	benefit = models.CharField(max_length=250, verbose_name="Benefísiu", null=True)
	obs = models.TextField(verbose_name="OBS")
	year = models.ForeignKey(Year, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Tinan")
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, blank=True, null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE, blank=True, null=True)
	village = models.ForeignKey(Village, on_delete=models.CASCADE, blank=True, null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Author")
	hashed = models.CharField(max_length=50, null=True, blank=True)
	datetime = models.DateTimeField(auto_now_add=True, null=True)
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

	def save(self, *args, **kwargs):
		self.hashed = hashlib.md5(str(self.id).encode()).hexdigest()
		return super(Activity, self).save(*args, **kwargs)

	class Meta:
		verbose_name_plural='C.2. Livru Dadus Atividade Suku'

class ImageActivity(models.Model):
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, related_name="activityfiles", verbose_name="Naran Atividade")
	image = models.FileField(upload_to='development/activity/', null=True, blank=True,
			validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png'])], verbose_name="Aneksu Imajen")
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	datetime = models.DateTimeField(null=True)

	def __str__(self):
		template = '{0.activity}'
		return template.format(self)
	
	class Meta:
		verbose_name_plural='Aneksu Imajen Atividade'


class FundCommunityContribute(models.Model):
	community_contribute = models.CharField(max_length=200, verbose_name='Kontribuisaun Komunidade', null=True, blank=True)
	communitycontribute_material = models.CharField(max_length=50, null=True, blank=True, verbose_name="Ajuda Material")
	communitycontribute_amount = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True, verbose_name='Total Osan')
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name='Naran Atividade', null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Author")
	hashed = models.CharField(max_length=50, null=True, blank=True)

	def __str__(self):
		template = '{0.community_contribute}'
		return template.format(self)

	def save(self, *args, **kwargs):
		self.hashed = hashlib.md5(str(self.id).encode()).hexdigest()
		return super(FundCommunityContribute, self).save(*args, **kwargs)
	class Meta:
		verbose_name_plural='Fundus Husi Kontribuisaun Komunidade'

class FundAgency(models.Model):
	agency = models.ForeignKey(Agency, on_delete=models.CASCADE, verbose_name='Ajénsia', null=True, blank=True)
	agency_material = models.CharField(max_length=50, null=True, blank=True, verbose_name="Ajuda Material")
	agency_amount = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True, verbose_name='Total Osan')
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name='Naran Projetu', null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Author")
	hashed = models.CharField(max_length=32, null=True, blank=True)

	def __str__(self):
		template = '{0.agency}'
		return template.format(self)

	def save(self, *args, **kwargs):
		self.hashed = hashlib.md5(str(self.id).encode()).hexdigest()
		return super(FundAgency, self).save(*args, **kwargs)
	class Meta:
		verbose_name_plural='Fundus Husi Ajénsia'


class FundMunicipality(models.Model):
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, verbose_name="Munisípiu", null=True, blank=True)
	municipality_material = models.CharField(max_length=50, null=True, blank=True, verbose_name="Ajuda Material")
	municipality_amount = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True, verbose_name='Total Osan')
	project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Naran Projetu", null=True, blank=True)
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="Naran Atividade", null=True, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Author")
	hashed = models.CharField(max_length=50, null=True, blank=True)

	def __str__(self):
		template = '{0.municipality}'
		return template.format(self)

	def save(self, *args, **kwargs):
		self.hashed = hashlib.md5(str(self.id).encode()).hexdigest()
		return super(FundMunicipality, self).save(*args, **kwargs)
	class Meta:
		verbose_name_plural='Fundus Husi Munisípiu'

class FundNational(models.Model):
	national = models.ForeignKey(National, on_delete=models.CASCADE, verbose_name="Nasional", null=True, blank=True)
	national_material = models.CharField(max_length=50, null=True, blank=True, verbose_name="Ajuda Material")
	national_amount = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True, verbose_name='Total Osan')
	project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Naran Projetu", null=True, blank=True)
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="Naran Atividade", null=True, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Author")
	hashed = models.CharField(max_length=50, null=True, blank=True)


	def __str__(self):
		template = '{0.national}'
		return template.format(self)

	def save(self, *args, **kwargs):
		self.hashed = hashlib.md5(str(self.id).encode()).hexdigest()
		return super(FundNational, self).save(*args, **kwargs)

	class Meta:
		verbose_name_plural='Fundus Husi Nasional'