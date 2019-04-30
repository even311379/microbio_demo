from django.db import models

# Create your models here.

class patient_data(models.Model):
    class Meta:
        verbose_name = '病人資料'
        verbose_name_plural = '病人資料'

    gender_choice = (
        ('男', '男'),
        ('女', '女'),)

    year_choice = [(i,i) for i in range(1930,2011)]
    month_choice = [(i,i) for i in range(1,13)]
    date_choice = [(i,i) for i in range(1,32)]

    PatientID = models.CharField(max_length = 15, verbose_name = '病人編號', unique=True, )
    Gender = models.CharField(max_length = 1, choices = gender_choice, verbose_name= '性別')
    birth_year = models.IntegerField(choices = year_choice,verbose_name = '出生年份')
    birth_month = models.IntegerField(choices = month_choice,verbose_name = '出生月份')
    birth_date = models.IntegerField(choices = date_choice,verbose_name = '出生日期')

    def __str__(self):
        return self.PatientID

class blood_test_data(models.Model):
    class Meta:
        verbose_name = '血液檢測資料'
        verbose_name_plural = '血液檢測資料'
    
    PatientID = models.OneToOneField(patient_data, on_delete=models.CASCADE, primary_key=True,)
    Treg1 = models.IntegerField(null=True, blank=True)
    Treg2 = models.IntegerField(null=True, blank=True)
    Treg3 = models.IntegerField(null=True, blank=True)
    Treg4 = models.IntegerField(null=True, blank=True)
    CTC1 = models.IntegerField(null=True, blank=True)
    CTC2 = models.IntegerField(null=True, blank=True)
    CTC3 = models.IntegerField(null=True, blank=True)
    CTC4 = models.IntegerField(null=True, blank=True)
    CEA1 = models.FloatField(null=True, blank=True)
    CEA2 = models.FloatField(null=True, blank=True)
    CEA3 = models.FloatField(null=True, blank=True)
    CEA4 = models.FloatField(null=True, blank=True)

    # def __str__(self):
    #     return self.PatientID