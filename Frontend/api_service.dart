import 'package:http/http.dart' as http;
import 'dart:convert';
import 'models/ride.dart';

class ApiService {
  final String baseUrl = 'http://127.0.0.1:8000';

  Future<List<Ride>> fetchRides() async {
    final response = await http.get(Uri.parse('$baseUrl/rides'));
    if (response.statusCode == 200) {
      List data = json.decode(response.body);
      return data.map((ride) => Ride.fromJson(ride)).toList();
    } else {
      throw Exception('Failed to load rides');
    }
  }
}