from django.contrib import admin

from mysite import models

class PatientAdmin(admin.ModelAdmin):
    list_display = ('PatientID','Gender','birth_year')

class BloodTestAdmin(admin.ModelAdmin):
    list_display = ('PatientID','Treg1','Treg2','Treg3','Treg4','CTC1', 'CTC2', 'CTC3', 'CTC4', 'CEA1', 'CEA2','CEA3','CEA4',)

# Register your models here.
admin.site.register(models.patient_data, PatientAdmin)
admin.site.register(models.blood_test_data, BloodTestAdmin)