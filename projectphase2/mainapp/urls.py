from django.urls import path
from . import views
urlpatterns = [
    path('', views.home,name='home'),
    path('data',views.data,name='data'),
    path('spatial/',views.spatial, name='spatial'),
    path('temporal/', views.temporal, name='temporal'),
    path('knn/', views.knn, name='knn'),
    path('trips/', views.trips, name='trips'),
    path('spatial/spatial_',views.spatial_, name='spatial_'),
    path('temporal/temporal_', views.temporal_, name='temporal_'),
    path('knn/knn_', views.knn_, name='knn_')
]