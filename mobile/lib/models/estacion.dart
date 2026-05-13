class Estacion {
  final int id;
  final String nombre;
  final String ubicacion;
  final double? ultimoValor;

  Estacion({required this.id, required this.nombre, required this.ubicacion, this.ultimoValor});
  factory Estacion.fromJson(Map<String, dynamic> json) {
    return Estacion(
      id: json['id'],
      nombre: json['nombre'],
      ubicacion: json['ubicacion'],
      ultimoValor: json['ultimo_valor'] != null
        ? (json['ultimo_valor'] as num).toDouble()
        : null,
    );
  }
}
