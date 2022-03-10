"""library URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Core import views as Core
from Web import views as Web
from django.urls import include
from .views import page_not_found
urlpatterns = [
    path('admin/' , admin.site.urls),
    path('Core/signin' , Core.StringAnalyse),

    path('',Web.User_Login),
    path('fast/',Web.Fast),
    path('clock/',Web.Clock),
    path('account/',Web.Account),
    path('about/',Web.About),
    path('logout/',Web.Logout),
    path('qrcode/',Web.QRCode_reserve),
    path('searchseat/',Web.Search_SeatAuto),
    path('seatprocess/',Web.Get_Process),
    path('contact/',Web.Contact),
    path('delete/',Web.delete),
    path('deleteassignment/',Web.delete_assignment),
    path('help/',Web.Help),
    path('declaration/',Web.Declaration),
    # path(r'silk/', include('silk.urls', namespace='silk')),
]
handler404 = page_not_found