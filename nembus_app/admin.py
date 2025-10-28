from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Cliente, Camion, ReporteVenta, PerfilTrabajador, Traspaso,
    PuntoDeVenta, Bomba, Turno, ReporteTurno, LecturaBomba,
    RegistroVentaIndividualBomba # Importar el nuevo modelo
)
from django.utils.html import format_html
from django.db.models import Sum, F # Importar Sum y F
from decimal import Decimal

# --- Admin para Modelos Existentes (sin cambios o con ajustes menores) ---

class ReporteVentaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'trabajador', 'camion', 'cliente', 'litros_vendidos', 'monto_total_clp', 'fecha_hora')
    # Ajustar fields si es necesario, asegurarse que 'ver_foto_evidencia' sigue siendo válido
    fields = ('trabajador', 'cliente', 'camion', 'litros_vendidos', 'monto_combustible_clp', 'costo_flete_clp', 'monto_total_clp', 'ver_foto_evidencia', 'fecha_hora')
    readonly_fields = ('ver_foto_evidencia', 'fecha_hora') # Hacer fecha_hora readonly
    search_fields = ('cliente__nombre', 'camion__patente', 'trabajador__username')
    list_filter = ('fecha_hora', 'trabajador', 'camion', 'cliente')

    def ver_foto_evidencia(self, obj):
        if obj.foto_evidencia:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" width="150" /></a>', obj.foto_evidencia.url)
        return "No hay foto"
    ver_foto_evidencia.short_description = 'Foto Evidencia'

class PerfilTrabajadorInline(admin.StackedInline):
    model = PerfilTrabajador
    can_delete = False
    verbose_name_plural = 'Perfil de Trabajador'
    fields = ('punto_de_venta_asignado', 'puede_recargar_combustible', 'puede_hacer_traspasos', 'clientes_asignados', 'camiones_asignados', 'camiones_traspaso')
    filter_horizontal = ('clientes_asignados', 'camiones_asignados', 'camiones_traspaso')
    # Asegúrate que los 'related_name' en ManyToManyField coincidan si usas filter_horizontal

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilTrabajadorInline,)

    # --- AÑADE ESTA CLASE Media ---
    class Media:
        css = {
            # Carga tu archivo CSS personalizado en todas las páginas del admin de User
            'all': ('nembus_app/css/admin_custom.css',)
        }

# Inline para mostrar las ventas individuales DENTRO de la LecturaBomba
class RegistroVentaIndividualBombaInline(admin.TabularInline):
    model = RegistroVentaIndividualBomba
    fields = ('fecha_registro', 'numero_maquina', 'socio_propietario', 'litros_vendidos', 'precio_litro_venta', 'ingreso_registro')
    readonly_fields = ('fecha_registro', 'precio_litro_venta', 'ingreso_registro')
    extra = 0 # No mostrar formularios vacíos por defecto
    ordering = ('fecha_registro',)

# Modificado para reflejar la nueva estructura y añadir el inline de ventas
class LecturaBombaAdmin(admin.ModelAdmin): # Crear un admin explícito para LecturaBomba
    list_display = ('__str__', 'reporte_turno', 'bomba', 'contador_inicial', 'contador_final', 'litros_vendidos_turno')
    readonly_fields = ('litros_vendidos_turno',) # El total se calcula
    inlines = [RegistroVentaIndividualBombaInline] # Mostrar ventas aquí
    list_filter = ('reporte_turno__fecha_inicio', 'bomba') # Asume que ReporteTurno tiene fecha_inicio
    search_fields = ('bomba__nombre', 'reporte_turno__trabajador__username')

# Inline para mostrar las LecturasBomba dentro del ReporteTurno
class LecturaBombaInlineForTurno(admin.TabularInline):
    model = LecturaBomba
    # Usar los nuevos nombres de campo
    fields = ('bomba', 'contador_inicial', 'contador_final', 'litros_vendidos_turno')
    readonly_fields = ('bomba', 'contador_inicial', 'contador_final', 'litros_vendidos_turno')
    extra = 0
    can_delete = False
    # No permitir añadir lecturas desde aquí, se crean al iniciar turno
    def has_add_permission(self, request, obj=None): return False

# Modificado para reflejar la nueva estructura de ReporteTurno
class ReporteTurnoAdmin(admin.ModelAdmin):
    inlines = [LecturaBombaInlineForTurno]
    # Usar los nuevos nombres de campo y añadir estado
    list_display = ('__str__', 'trabajador', 'turno', 'fecha_inicio', 'fecha_fin', 'esta_abierto', 'total_litros_vendidos', 'total_ingresos_turno') # Asume que ReporteTurno tiene estos campos
    # Hacer campos readonly que se gestionan automáticamente
    readonly_fields = ('trabajador', 'turno', 'fecha_inicio', 'fecha_fin', 'esta_abierto') # Asume que ReporteTurno tiene estos campos
    list_filter = ('esta_abierto', 'fecha_inicio', 'turno', 'trabajador') # Asume que ReporteTurno tiene estos campos
    search_fields = ('trabajador__username', 'turno__nombre')
    ordering = ('-fecha_inicio',) # Asume que ReporteTurno tiene fecha_inicio

    # Métodos para calcular totales (ahora usan los nuevos campos/relaciones)
    def total_litros_vendidos(self, obj):
        # Sumar los totales de cada lectura de bomba asociada
        total = obj.lecturas.aggregate(total_l=Sum('litros_vendidos_turno'))['total_l'] # Asume related_name='lecturas' y campo='litros_vendidos_turno'
        return total or 0
    total_litros_vendidos.short_description = 'Total Litros (Turno)'

    def total_ingresos_turno(self, obj):
        # Sumar los ingresos de TODAS las ventas individuales asociadas a las lecturas de este turno
        total = RegistroVentaIndividualBomba.objects.filter(lectura_bomba__reporte_turno=obj).aggregate(total_i=Sum('ingreso_registro'))['total_i'] # Asume campo='ingreso_registro'
        # Formatear como moneda
        total_decimal = total or Decimal('0.00')
        return f"${int(total_decimal):,}".replace(",", ".") # Formato chileno
    total_ingresos_turno.short_description = 'Total Ingresos (CLP)'

# --- Registros en el Admin Site ---

admin.site.unregister(User) # Desregistrar el User admin por defecto
admin.site.register(User, UserAdmin) # Registrar User con nuestro inline

admin.site.register(Cliente)
admin.site.register(Camion)
admin.site.register(ReporteVenta, ReporteVentaAdmin)
admin.site.register(Traspaso)
admin.site.register(PuntoDeVenta)
admin.site.register(Bomba)
admin.site.register(Turno)
admin.site.register(ReporteTurno, ReporteTurnoAdmin)
admin.site.register(LecturaBomba, LecturaBombaAdmin)
# No registramos RegistroVentaIndividualBomba directamente, se ve a través de LecturaBombaAdmin