from django.contrib import admin

# Register your models here.
from .models import User, Assignment, Fastrecord ,Signin_Assignment , QRCode ,Record ,Broadcast 
@admin.register( User, Fastrecord ,Signin_Assignment , QRCode ,Record ,Broadcast )
class PersonAdmin(admin.ModelAdmin):
    pass

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('User', 'seatname',  'Reservation_Day', 'begintimestr','endtimestr',)


admin.site.register(Assignment,AssignmentAdmin)