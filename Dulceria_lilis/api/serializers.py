from rest_framework import serializers
from productos.models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'
<<<<<<< HEAD

    def validador_completo(self, data):
        if not data['producto']:
            raise serializers.ValidationError('El producto es obligatorio')
        if not data['proveedor']:
            raise serializers.ValidationError('El proveedor es obligatorio')
        if not data['costo']:
            raise serializers.ValidationError('El costo es obligatorio')
        if not data['lead_time_dias']:
            raise serializers.ValidationError('El lead time es obligatorio')
        if not data['min_lote']:
            raise serializers.ValidationError('El mínimo de lote es obligatorio')
        if len(data['lead_time_dias']) < 1:
            raise serializers.ValidationError('El lead time debe ser mayor a 0')
        return data
=======
>>>>>>> c9bd708 (cloude)
