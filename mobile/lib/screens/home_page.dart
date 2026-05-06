import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../models/estacion.dart';
import 'login_screen.dart';
import 'add_estacion.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  // Variable para guardar la lista de estaciones
  late Future<List<Estacion>> _futureEstaciones;

  @override
  void initState() {
    super.initState();
    _cargarEstaciones();
  }

  // Función que llama al ApiService para descargar los datos
  void _cargarEstaciones() {
    setState(() {
      _futureEstaciones = ApiService().fetchEstaciones();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Estaciones SMAT'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              // 1. Borramos el token de la memoria
              await AuthService().logout();
              
              if (!context.mounted) return;

              // 2. Reinicia la navegación al Login y borra el historial
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (context) => const LoginScreen()),
                (route) => false,
              );
            },
          ),
        ],
      ),
      // FutureBuilder para mostrar una bolita de carga mientras llegan los datos
      body: FutureBuilder<List<Estacion>>(
        future: _futureEstaciones,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error al cargar datos: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No hay estaciones registradas aún.'));
          }

          final estaciones = snapshot.data!;
          return ListView.builder(
            itemCount: estaciones.length,
            itemBuilder: (context, index) {
              final estacion = estaciones[index];
              return ListTile(
                leading: const Icon(Icons.sensors, color: Colors.blue),
                title: Text(estacion.nombre),
                subtitle: Text(estacion.ubicacion),
              );
            },
          );
        },
      ),
      // Botón flotante para ir a la pantalla de crear una nueva estación
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const AddEstacionScreen()),
          );
          
          // Si el usuario guardó con éxito (result == true), recargamos la lista
          if (result == true) {
            _cargarEstaciones();
          }
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}