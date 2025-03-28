from django.urls import path

from accounts.views import CustomLoginView

urlpatterns = [

    path('login/', CustomLoginView.as_view(), name='login'),

]
