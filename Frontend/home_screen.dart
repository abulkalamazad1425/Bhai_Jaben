import 'package:flutter/material.dart';
import '../api_service.dart';
import '../models/ride.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late Future<List<Ride>> rides;

  @override
  void initState() {
    super.initState();
    rides = ApiService().fetchRides();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ride Sharing'),
        centerTitle: true,
        backgroundColor: Colors.blueAccent,
      ),
      body: FutureBuilder<List<Ride>>(
        future: rides,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(
              child: Text(
                'Error: ${snapshot.error}',
                style: const TextStyle(color: Colors.red, fontSize: 18),
              ),
            );
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.directions_car, size: 80, color: Colors.grey[400]),
                  const SizedBox(height: 20),
                  const Text(
                    'No rides found.',
                    style: TextStyle(fontSize: 22, color: Colors.grey),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Try requesting a ride!',
                    style: TextStyle(fontSize: 16, color: Colors.grey[600]),
                  ),
                ],
              ),
            );
          }
          return ListView.builder(
            itemCount: snapshot.data!.length,
            itemBuilder: (context, index) {
              final ride = snapshot.data![index];
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                elevation: 3,
                child: ListTile(
                  leading: const Icon(Icons.local_taxi, color: Colors.blueAccent),
                  title: Text('${ride.origin} → ${ride.destination}'),
                  subtitle: Text('Status: ${ride.status}'),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () {
                    // Navigate to details screen if needed
                  },
                ),
              );
            },
          );
        },
      ),
      backgroundColor: const Color(0xFFF7F2F7),
    );
  }
}