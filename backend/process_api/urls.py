from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'hosts', views.HostViewSet)
router.register(r'snapshots', views.ProcessSnapshotViewSet)
router.register(r'processes', views.ProcessViewSet)
router.register(r'system-metrics', views.SystemMetricsViewSet)
router.register(r'submit', views.ProcessDataSubmissionViewSet, basename='process-submission')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]

# Add custom endpoints
urlpatterns += [
    # Process tree endpoint
    path('snapshots/<uuid:pk>/tree/', views.ProcessSnapshotViewSet.as_view({'get': 'tree'}), name='snapshot-tree'),
    
    # Latest snapshots
    path('snapshots/latest/', views.ProcessSnapshotViewSet.as_view({'get': 'latest'}), name='latest-snapshots'),
    
    # Host summary
    path('hosts/summary/', views.HostViewSet.as_view({'get': 'summary'}), name='host-summary'),
    
    # Process search
    path('processes/search/', views.ProcessViewSet.as_view({'get': 'search'}), name='process-search'),
    
    # Top processes
    path('processes/top-cpu/', views.ProcessViewSet.as_view({'get': 'top_cpu'}), name='top-cpu'),
    path('processes/top-memory/', views.ProcessViewSet.as_view({'get': 'top_memory'}), name='top-memory'),
    
    # System metrics latest
    path('system-metrics/latest/', views.SystemMetricsViewSet.as_view({'get': 'latest'}), name='latest-metrics'),
]
