from django.contrib import admin
from .models import *

# Register your models here.

from import_export import resources

from import_export.admin import ImportExportModelAdmin


class AgencyResource(resources.ModelResource):
    class Meta:
        model = Agency
class AgencyAdmin(ImportExportModelAdmin):
    resource_class = AgencyResource
admin.site.register(Agency, AgencyAdmin)


class NationalResource(resources.ModelResource):
    class Meta:
        model = National
class NationalAdmin(ImportExportModelAdmin):
    resource_class = NationalResource
admin.site.register(National, NationalAdmin)

class CompanyResource(resources.ModelResource):
    class Meta:
        model = Company
class CompanyAdmin(ImportExportModelAdmin):
    resource_class = CompanyResource
admin.site.register(Company, CompanyAdmin)



class ONGResource(resources.ModelResource):
    class Meta:
        model = ONG
class ONGAdmin(ImportExportModelAdmin):
    resource_class = ONGResource
admin.site.register(ONG, ONGAdmin)

