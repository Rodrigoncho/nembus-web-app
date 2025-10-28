# nembus_app/forms.py
from django import forms
from .models import Turno, Bomba, ReporteTurno, LecturaBomba, RegistroVentaIndividualBomba # Importa los modelos necesarios
from django.forms import inlineformset_factory # Para el formset de ventas

# Formulario para la pantalla "Iniciar Turno"
# nembus_app/forms.py
# ... (imports) ...

class IniciarTurnoForm(forms.Form):
    turno = forms.ModelChoiceField(queryset=Turno.objects.none(), label="Selecciona tu Turno", empty_label="-- Elige Turno --")

    def __init__(self, *args, **kwargs):
        punto_venta = kwargs.pop('punto_venta', None)
        super().__init__(*args, **kwargs)

        print(f"--- Depurando IniciarTurnoForm.__init__ ---") # <-- AÑADIR
        print(f"Punto de Venta recibido: {punto_venta}") # <-- AÑADIR

        if punto_venta:
            self.fields['turno'].queryset = Turno.objects.filter(punto_de_venta=punto_venta)
            bombas = Bomba.objects.filter(punto_de_venta=punto_venta)

            print(f"Bombas encontradas para {punto_venta}: {list(bombas)}") # <-- AÑADIR (Convertir a lista para ver)

            for bomba in bombas:
                field_name = f'contador_inicial_{bomba.id}' # <-- Nombre esperado
                print(f"  Añadiendo campo: {field_name}") # <-- AÑADIR
                self.fields[field_name] = forms.DecimalField(
                    label=f"Contador Inicial ({bomba.nombre})",
                    max_digits=12,
                    decimal_places=4,
                    required=True,
                    widget=forms.NumberInput(attrs={'step': '0.01'})
                )
        print(f"Campos finales en el form: {list(self.fields.keys())}") # <-- AÑADIR
        print(f"--- Fin Depuración Form ---") # <-- AÑADIR

# Formulario base para UNA venta individual
class VentaIndividualForm(forms.ModelForm):
    class Meta:
        model = RegistroVentaIndividualBomba
        # Campos que llenará el bombero al registrar la venta
        fields = ['numero_maquina', 'socio_propietario', 'litros_vendidos']
        widgets = {
             # Puedes añadir atributos HTML si quieres (ej. placeholders, clases CSS)
            'numero_maquina': forms.TextInput(attrs={'placeholder': 'N° Máquina'}),
            'socio_propietario': forms.TextInput(attrs={'placeholder': 'Socio/Dueño'}),
            'litros_vendidos': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

# FormSet: Permite manejar MÚLTIPLES formularios de VentaIndividualForm
# asociados a UNA LecturaBomba específica (es decir, todas las ventas de una bomba en un turno)
VentaIndividualFormSet = inlineformset_factory(
    LecturaBomba,                     # Modelo Padre (la lectura de la bomba en el turno)
    RegistroVentaIndividualBomba,    # Modelo Hijo (las ventas de esa bomba en ese turno)
    form=VentaIndividualForm,         # Formulario a usar para cada venta
    fields=['numero_maquina', 'socio_propietario', 'litros_vendidos'], # Campos a mostrar/editar
    extra=1,                          # Muestra 1 formulario vacío listo para añadir una nueva venta
    can_delete=True                   # Permite marcar ventas para borrarlas (útil si se comete un error)
)