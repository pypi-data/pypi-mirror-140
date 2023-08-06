from django.contrib import admin
from .models import *


from import_export import resources

from import_export.admin import ImportExportModelAdmin



class MunicipalityResource(resources.ModelResource):
    class Meta:
        model = Municipality
class MunicipalityAdmin(ImportExportModelAdmin):
    resource_class = MunicipalityResource
admin.site.register(Municipality, MunicipalityAdmin)



class AdministrativePostResource(resources.ModelResource):
    class Meta:
        model = AdministrativePost
class AdministrativePostAdmin(ImportExportModelAdmin):
    resource_class = AdministrativePostResource
admin.site.register(AdministrativePost, AdministrativePostAdmin)



class VillageResource(resources.ModelResource):
    class Meta:
        model = Village
class VillageAdmin(ImportExportModelAdmin):
    resource_class = VillageResource
admin.site.register(Village, VillageAdmin)

class AldeiaResource(resources.ModelResource):
    class Meta:
        model = Aldeia
class AldeiaAdmin(ImportExportModelAdmin):
    resource_class = AldeiaResource
admin.site.register(Aldeia, AldeiaAdmin)



class YearResource(resources.ModelResource):
    class Meta:
        model = Year
class YearAdmin(ImportExportModelAdmin):
    resource_class = YearResource
admin.site.register(Year, YearAdmin)