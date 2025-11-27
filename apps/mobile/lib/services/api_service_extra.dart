import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiServiceExtra {
  static const String baseUrl = 'http://192.168.1.194:3000';
  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  static Future<Map<String, dynamic>?> getProfile() async {
    try {
      final email = await _storage.read(key: 'user_email');
      if (email == null) return null;

      final response = await http.get(
        Uri.parse('$baseUrl/auth/profile?email=$email'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
      
      return null;
    } catch (e) {
      print('Error getting profile: $e');
      return null;
    }
  }

  static Future<String?> updatePreference({
    required String preferenceType,
    String? specificSpot,
  }) async {
    try {
      final email = await _storage.read(key: 'user_email');
      if (email == null) return 'User not logged in';

      final response = await http.patch(
        Uri.parse('$baseUrl/auth/update-preference'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'spotPreferenceType': preferenceType,
          'preferredSpot': specificSpot,
        }),
      );

      if (response.statusCode == 200) {
        return null;
      } else {
        final data = jsonDecode(response.body);
        return data['message'] ?? 'Failed to update preference';
      }
    } catch (e) {
      print('Error updating preference: $e');
      return 'Connection error';
    }
  }

  static Future<String?> updateCarColorSimple(String color) async {
    try {
      final email = await _storage.read(key: 'user_email');
      if (email == null) return 'User not logged in';

      final response = await http.patch(
        Uri.parse('$baseUrl/auth/update-car-color'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'carColor': color,
        }),
      );

      if (response.statusCode == 200) {
        return null;
      } else {
        final data = jsonDecode(response.body);
        return data['message'] ?? 'Failed to update car color';
      }
    } catch (e) {
      print('Error updating car color: $e');
      return 'Connection error';
    }
  }
}
