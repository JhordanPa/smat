import 'package:flutter/material.dart';
import 'services/api_service.dart';
import 'models/estacion.dart';
import 'screens/login_screen.dart';
import 'screens/home_page.dart';
import 'services/auth_service.dart';
void main() => runApp(const SMATApp());

class SMATApp extends StatelessWidget {
  const SMATApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'SMAT Mobile',
      // El home ahora depende de la verificación del token
      home: FutureBuilder<String?>(
        future: AuthService().getToken(),
        builder: (context, snapshot) {
          // Mientras verifica, muestra un indicador de carga
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Scaffold(
              body: Center(child: CircularProgressIndicator()),
            );
          }
        
          // Si el token existe, va al Home, si no, al Login
          if (snapshot.hasData && snapshot.data != null) {
            return const HomePage();
          }
          return const LoginScreen();
        },
      ),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late Future<List<Estacion>> futureEstaciones;
  @override

  void initState() {
    super.initState();
    futureEstaciones = ApiService().fetchEstaciones();
  }

  void _refrescarDatos() {
    setState(() {
      futureEstaciones = ApiService().fetchEstaciones();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('SMAT - Monitoreo Móvil')),
      body: FutureBuilder<List<Estacion>>(
        future: futureEstaciones,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('❌ Error de conexión'));
          } else {
            return ListView.builder(
              itemCount: snapshot.data!.length,
              itemBuilder: (context, index) {
                final est = snapshot.data![index];
                return ListTile(
                  leading: const Icon(Icons.satellite_alt),
                  title: Text(est.nombre),
                  subtitle: Text(est.ubicacion),
                );
              },
            );
          }
        },
      ),

      floatingActionButton: FloatingActionButton(
        onPressed: _refrescarDatos,
        child: const Icon(Icons.refresh),
      ),
      
    );
  }
}
