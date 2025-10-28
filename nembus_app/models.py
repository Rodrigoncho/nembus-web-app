from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal # Importar Decimal
from django.db.models import Sum # Importar Sum

# --- MODELOS DE ENTIDADES PRINCIPALES ---

class Cliente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    precio_litro_clp = models.DecimalField(max_digits=10, decimal_places=2)
    costo_flete_clp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def __str__(self): return self.nombre

class Camion(models.Model):
    patente = models.CharField(max_length=10, unique=True)
    capacidad_total = models.PositiveIntegerField()
    litros_actuales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Camión"          
        verbose_name_plural = "Camiones"
    
    def __str__(self): return f"Camión {self.patente}"

class PuntoDeVenta(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=255)
    def __str__(self): return self.nombre

class Bomba(models.Model):
    punto_de_venta = models.ForeignKey(PuntoDeVenta, on_delete=models.CASCADE, related_name='bombas')
    nombre = models.CharField(max_length=100)
    precio_litro_clp = models.DecimalField(max_digits=10, decimal_places=2)
    litros_actuales = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    def __str__(self): return f"{self.punto_de_venta.nombre} - {self.nombre}"

class Turno(models.Model):
    punto_de_venta = models.ForeignKey(PuntoDeVenta, on_delete=models.CASCADE, related_name='turnos')
    nombre = models.CharField(max_length=50) # Ej: "Turno A", "Turno B"
    def __str__(self): return f"{self.punto_de_venta.nombre} - {self.nombre}"

class PerfilTrabajador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    punto_de_venta_asignado = models.ForeignKey(PuntoDeVenta, on_delete=models.SET_NULL, null=True, blank=True)
    puede_recargar_combustible = models.BooleanField(default=False)
    puede_hacer_traspasos = models.BooleanField(default=False)
    clientes_asignados = models.ManyToManyField(Cliente, blank=True)
    camiones_asignados = models.ManyToManyField(Camion, blank=True, related_name='operadores_generales')
    camiones_traspaso = models.ManyToManyField(Camion, blank=True, related_name='operadores_traspaso')
    def __str__(self): return f"Perfil de {self.usuario.username}"

# --- MODELOS DE REGISTRO DE OPERACIONES ---

# Modelo para ventas realizadas por CHOFERES desde CAMIONES
class ReporteVenta(models.Model):
    trabajador = models.ForeignKey(User, on_delete=models.PROTECT)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    camion = models.ForeignKey(Camion, on_delete=models.PROTECT)
    litros_vendidos = models.DecimalField(max_digits=12, decimal_places=4)
    monto_combustible_clp = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    costo_flete_clp = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    monto_total_clp = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    foto_evidencia = models.ImageField(upload_to='evidencias/', blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Venta Camión: {self.litros_vendidos}L a {self.cliente.nombre}"

# Modelo para TRASPASOS entre CAMIONES (realizados por choferes)
class Traspaso(models.Model):
    trabajador = models.ForeignKey(User, on_delete=models.PROTECT)
    camion_origen = models.ForeignKey(Camion, on_delete=models.PROTECT, related_name='traspasos_salientes')
    camion_destino = models.ForeignKey(Camion, on_delete=models.PROTECT, related_name='traspasos_entrantes')
    litros = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Traspaso: {self.litros}L desde {self.camion_origen.patente} a {self.camion_destino.patente}"

# --- MODELOS MODIFICADOS/NUEVOS PARA EL FLUJO DE BOMBEROS ---

# Representa un turno activo de un bombero
class ReporteTurno(models.Model):
    trabajador = models.ForeignKey(User, on_delete=models.PROTECT)
    turno = models.ForeignKey(Turno, on_delete=models.PROTECT)
    fecha_inicio = models.DateTimeField(default=timezone.now) # Fecha/Hora de inicio del turno
    fecha_fin = models.DateTimeField(null=True, blank=True) # Se establece al finalizar
    esta_abierto = models.BooleanField(default=True) # Indica si el turno está activo

    def __str__(self):
        estado = "Abierto" if self.esta_abierto else "Cerrado"
        fecha_str = self.fecha_inicio.strftime('%d/%m/%Y') if self.fecha_inicio else 'N/A'
        return f"Reporte de {self.trabajador.username} - {self.turno.nombre} ({fecha_str}) - {estado}"

# Guarda la lectura inicial y final de UNA bomba específica DENTRO de un ReporteTurno
class LecturaBomba(models.Model):
    reporte_turno = models.ForeignKey(ReporteTurno, on_delete=models.CASCADE, related_name='lecturas')
    bomba = models.ForeignKey(Bomba, on_delete=models.PROTECT)
    contador_inicial = models.DecimalField(max_digits=12, decimal_places=4) # Se ingresa al iniciar turno
    contador_final = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True) # Se calcula/ingresa al finalizar
    litros_vendidos_turno = models.DecimalField(max_digits=12, decimal_places=4, default=0, editable=False) # Total calculado

    # Calcula el contador final y litros totales basado en ventas individuales
    def calcular_y_guardar_final(self):
        # Asegurarse que related_name='ventas_individuales' existe en RegistroVentaIndividualBomba.lectura_bomba
        total_litros_ventas = self.ventas_individuales.aggregate(Sum('litros_vendidos'))['litros_vendidos__sum'] or Decimal('0.00')
        self.contador_final = self.contador_inicial + total_litros_ventas
        self.litros_vendidos_turno = total_litros_ventas
        self.save(update_fields=['contador_final', 'litros_vendidos_turno'])

        # Actualizar inventario de la bomba al finalizar el turno
        try:
            bomba_obj = self.bomba
            # Usar Decimal para la resta
            bomba_obj.litros_actuales -= Decimal(self.litros_vendidos_turno)
            # Podrías añadir validación aquí si prefieres (ej. no permitir negativos)
            bomba_obj.save(update_fields=['litros_actuales'])
        except Exception as e:
            # Manejar error si no se pudo actualizar el inventario (loggear, etc.)
            print(f"Error actualizando inventario bomba {self.bomba.id}: {e}")
            # Considera si deberías detener el proceso o solo advertir

    def __str__(self):
        return f"Lectura {self.bomba.nombre} (Turno ID: {self.reporte_turno_id})"

# NUEVO MODELO: Guarda cada venta individual hecha desde una bomba durante un turno
class RegistroVentaIndividualBomba(models.Model):
    # Vinculado a la lectura específica de la bomba en un turno
    lectura_bomba = models.ForeignKey(LecturaBomba, on_delete=models.CASCADE, related_name='ventas_individuales')
    # Datos ingresados por el bombero para esta venta
    numero_maquina = models.CharField(max_length=50)
    socio_propietario = models.CharField(max_length=100)
    litros_vendidos = models.DecimalField(max_digits=10, decimal_places=2)
    # Datos calculados/guardados automáticamente
    precio_litro_venta = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True) # Precio al momento de la venta
    ingreso_registro = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0) # Ingreso de esta venta
    fecha_registro = models.DateTimeField(default=timezone.now) # Momento exacto del registro

    def save(self, *args, **kwargs):
        # Tomar precio de la bomba si no se ha asignado antes
        if self.precio_litro_venta is None and self.lectura_bomba and self.lectura_bomba.bomba:
            self.precio_litro_venta = self.lectura_bomba.bomba.precio_litro_clp

        # Calcular ingreso
        if self.litros_vendidos and self.precio_litro_venta:
            # Asegurar que son Decimal
            litros = Decimal(self.litros_vendidos) if self.litros_vendidos else Decimal('0.00')
            precio = Decimal(self.precio_litro_venta) if self.precio_litro_venta else Decimal('0.00')
            self.ingreso_registro = litros * precio
        else:
            self.ingreso_registro = Decimal('0.00')

        super().save(*args, **kwargs) # Guardar el registro

    def __str__(self):
        fecha_str = self.fecha_registro.strftime('%d/%m %H:%M') if self.fecha_registro else 'N/A'
        return f"{self.litros_vendidos}L a Máq:{self.numero_maquina} ({fecha_str})"