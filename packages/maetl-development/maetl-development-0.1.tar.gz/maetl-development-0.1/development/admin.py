from django.contrib import admin
from development.models import *

# Register your models here.
admin.site.register(ImageProject)
admin.site.register(ImageActivity)

from import_export import resources

from import_export.admin import ImportExportModelAdmin



class ProjectResource(resources.ModelResource):
    class Meta:
        model = Project
class ProjectAdmin(ImportExportModelAdmin):
    resource_class = ProjectResource
admin.site.register(Project, ProjectAdmin)


class ActivityResource(resources.ModelResource):
    class Meta:
        model = Activity
class ActivityAdmin(ImportExportModelAdmin):
    resource_class = ActivityResource
admin.site.register(Activity, ActivityAdmin)


class FundAgencyResource(resources.ModelResource):
    class Meta:
        model = FundAgency
class FundAgencyAdmin(ImportExportModelAdmin):
    resource_class = FundAgencyResource
admin.site.register(FundAgency, FundAgencyAdmin)



class FundCommunityContributeResource(resources.ModelResource):
    class Meta:
        model = FundCommunityContribute
class FundCommunityContributeAdmin(ImportExportModelAdmin):
    resource_class = FundCommunityContributeResource
admin.site.register(FundCommunityContribute, FundCommunityContributeAdmin)


class FundNationalResource(resources.ModelResource):
    class Meta:
        model = FundNational
class FundNationalAdmin(ImportExportModelAdmin):
    resource_class = FundNationalResource
admin.site.register(FundNational, FundNationalAdmin)



class FundMunicipalityResource(resources.ModelResource):
    class Meta:
        model = FundMunicipality
class FundMunicipalityAdmin(ImportExportModelAdmin):
    resource_class = FundMunicipalityResource
admin.site.register(FundMunicipality, FundMunicipalityAdmin)



class FundONGResource(resources.ModelResource):
    class Meta:
        model = FundONG
class FundONGAdmin(ImportExportModelAdmin):
    resource_class = FundONGResource
admin.site.register(FundONG, FundONGAdmin)



class FundVolunteerResource(resources.ModelResource):
    class Meta:
        model = FundVolunteer
class FundVolunteerAdmin(ImportExportModelAdmin):
    resource_class = FundVolunteerResource
admin.site.register(FundVolunteer, FundVolunteerAdmin)






