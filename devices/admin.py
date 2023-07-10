from django.contrib import admin

# Register your models here.


from .models import Device, DeviceData, DeviceGroup



class DeviceGroupModelAdmin(admin.ModelAdmin):
    pass 


class DeviceDataModelAdmin(admin.ModelAdmin):
    model = DeviceData


class DeviceModelAdmin(admin.ModelAdmin):
    model = Device
    fields = [
        "name",
        "group",
    ]


admin.site.register(DeviceGroup, DeviceGroupModelAdmin)
admin.site.register(Device, DeviceModelAdmin)
admin.site.register(DeviceData, DeviceDataModelAdmin)

# admin.site.site_header = "SIA Admin"
# admin.site.site_title = "SIA Admin Portal"
# admin.site.index_title = "Welcome to SIA Admin Portal"
# admin.site.site_url = "/"
# admin.site.enable_nav_sidebar = True
