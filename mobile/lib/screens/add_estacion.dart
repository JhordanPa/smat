import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AddEstacionScreen extends StatefulWidget {
  const AddEstacionScreen({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _AddEstacionScreenState createState() => _AddEstacionScreenState();
}

class _AddEstacionScreenState extends State<AddEstacionScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nombreController = TextEditingController();
  final _ubicacionController = TextEditingController();
  void _guardar() async {
    if (_formKey.currentState!.validate()) {
      bool success = await ApiService().crearEstacion(
        _nombreController.text,
        _ubicacionController.text
      );
      
      // La pantalla de creación se cierra y regresa al Dashboard, que se refresca para mostrar la nueva estación.
      if (!mounted) return;

      if (success) {
        Navigator.pop(context, true); // Regresa al Dashboard
      } else {
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: No autorizado o Servidor caído')),
        );
      }
    }
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Nueva Estación')),
      body: Form(
        key: _formKey,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            children: [
              TextFormField(
                controller: _nombreController,
                decoration: InputDecoration(labelText: 'Nombre'),
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              TextFormField(
                controller: _ubicacionController,
                decoration: InputDecoration(labelText: 'Ubicación'),
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              SizedBox(height: 20),
              ElevatedButton(onPressed: _guardar, child: Text('Guardar Estación'))
            ],
          ),
        ),
      ),
    );
  }
}
