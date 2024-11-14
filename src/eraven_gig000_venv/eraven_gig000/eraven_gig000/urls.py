from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500, handler403
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/pages/', include(('pages.urls'))),  # Unique namespace 'pages'
    path('api/v1/ums/', include(('ums.urls'))),          # Unique namespace 'ums'
    path('api/v1/cms/', include(('cms.urls'))),          # Unique namespace 'cms'
    path('api/v1/products/', include(('products.urls'))),  
    path('api/v1/orders/', include(('orders.urls'))),  
    path('api/v1/payments/', include(('payments.urls'))),  
]

# Define custom error handlers
def custom_404_view(request, exception):
    return render(request, 'exceptions/404.html', status=404)

def custom_500_view(request):
    return render(request, 'exceptions/500.html', status=500)

def custom_403_view(request, exception):
    return render(request, 'exceptions/403.html', status=403)

# Link the custom error handlers
handler404 = custom_404_view
handler500 = custom_500_view
handler403 = custom_403_view

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
