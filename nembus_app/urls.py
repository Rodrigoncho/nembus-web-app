# nembus_web/nembus_app/urls.py

from django.urls import path
from . import views
app_name = 'nembus_app' # Mantener el app_name es importante

urlpatterns = [
    # --- VISTA PARA LA RAÍZ (puedes elegir login o dashboard) ---
    path('', views.login_usuario, name='vista_raiz'), # O views.dashboard_trabajador

    # --- URLs de Autenticación ---
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    # --- Dashboards ---
    path('dashboard/', views.dashboard_trabajador, name='dashboard_trabajador'),
    path('gerente/dashboard/', views.dashboard_redirect, name='dashboard_gerente_redirect'),
    path('gerente/dashboard/<str:division>/<str:periodo>/', views.dashboard_gerente, name='dashboard_gerente'),

    # --- URLs para CHOFERES (Camiones) ---
    path('reporte/nuevo/', views.crear_reporte_venta, name='crear_reporte'), # Venta desde camión
    path('reporte/exito/', views.reporte_exito, name='reporte_exito'), # Página éxito genérica?
    path('recarga/nueva/', views.crear_recarga, name='crear_recarga'), # Recarga de camión
    path('traspaso/nuevo/', views.crear_traspaso, name='crear_traspaso'), # Traspaso entre camiones

    # --- URLs para BOMBEROS (Nuevo flujo de Turnos y Ventas) ---
    path('turno/iniciar/', views.iniciar_turno, name='iniciar_turno'), # <-- NUEVA RUTA para iniciar turno
    path('turno/gestionar/<int:reporte_id>/', views.gestionar_turno, name='gestionar_turno'), # <-- NUEVA RUTA para ver/añadir ventas/finalizar
    # path('reporte-bomba/nuevo/', views.crear_reporte_turno, name='crear_reporte_turno'), # <-- RUTA ANTIGUA COMENTADA O ELIMINADA

    # --- URLs de Exportación ---
    path('reportes/exportar/', views.exportar_reportes_csv, name='exportar_reportes'), # Exportación CSV (¿quizás solo camiones ahora?)
    path('reportes/ventas/bombas/exportar/', views.exportar_ventas_bomba_excel, name='exportar_ventas_bomba_excel'), # <-- NUEVA RUTA EXPORTACIÓN EXCEL BOMBAS

]