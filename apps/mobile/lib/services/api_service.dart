import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  static const String baseUrl = 'http://172.20.8.71:3000';
  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  static Future<String?> login(String email, String password) async {
    try {
      print('🚀 Authenticating with API at: $baseUrl/auth/login');
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );
      print('Response status: ${response.statusCode}');
      print('Response body: ${response.body}');
      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);
        // Save email and role to secure storage
        await _storage.write(key: 'user_email', value: email);
        await _storage.write(key: 'user_role', value: data['role'] ?? 'user');
        return null;
      } else {
        final data = jsonDecode(response.body);
        return data['message'] ?? 'Login failed';
      }
    } catch (e) {
      print('API Error: $e');
      return 'Connection error';
    }
  }

  static Future<String?> signup(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/signup'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return null;
      } else {
        final data = jsonDecode(response.body);
        return data['message'] ?? 'Signup failed';
      }
    } catch (e) {
      return 'Connection error';
    }
  }

  static Future<String?> logout() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/logout'),
        headers: {'Content-Type': 'application/json'},
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return null;
      } else {
        final data = jsonDecode(response.body);
        return data['message'] ?? 'Logout failed';
      }
    } catch (e) {
      return 'Connection error';
    }
  }

  static Future<String?> forgotPassword(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/forgot-password'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return null;
      } else {
        final data = jsonDecode(response.body);
        return data['message'] ?? 'Failed to send reset email';
      }
    } catch (e) {
      return 'Connection error';
    }
  }

  static Future<String?> resetPassword(String token, String newPassword) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/reset-password'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'token': token, 'newPassword': newPassword}),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return null;
      } else {
        final data = jsonDecode(response.body);
        return data['message'] ?? 'Failed to reset password';
      }
    } catch (e) {
      return 'Connection error';
    }
  }

  static Future<String?> updateCarColor(String email, String carColor) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/update-car-color'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'carColor': carColor}),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return null;
      } else {
        final data = jsonDecode(response.body);
        return data['message'] ?? 'Failed to update car color';
      }
    } catch (e) {
      return 'Connection error';
    }
  }

  static Future<String?> setPreferredSpot(String email, String? preferredSpot) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/set-preferred-spot'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'preferredSpot': preferredSpot}),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return null;
      } else {
        final data = jsonDecode(response.body);
        return data['message'] ?? 'Failed to set preferred spot';
      }
    } catch (e) {
      return 'Connection error';
    }
  }

  static Future<Map<String, dynamic>?> getUserProfile(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/profile'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  static Future<Map<String, dynamic>?> generateQRCode(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/parking/generate-qr'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  static Future<Map<String, dynamic>?> getLastSession(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/parking/last-session'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  static Future<Map<String, dynamic>?> getCurrentSession(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/parking/current-session'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  /// Ends the active session and opens the exit barrier via MQTT.
  /// Returns { spotName, sessionId, durationMinutes, costPerHour, totalCost }.
  static Future<Map<String, dynamic>?> exitSession(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/parking/exit'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  static Future<List<Map<String, dynamic>>> getSpots() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/spots'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.cast<Map<String, dynamic>>();
      }
      
      return [];
    } catch (e) {
      print('Error getting spots: $e');
      return [];
    }
  }

  static Future<Map<String, dynamic>?> createSpot(String name) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/spots'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'name': name}),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return {'success': true};
      } else {
        final data = jsonDecode(response.body);
        return {'success': false, 'message': data['message'] ?? 'Failed to create spot'};
      }
    } catch (e) {
      print('Error creating spot: $e');
      return {'success': false, 'message': 'Connection error'};
    }
  }

  static Future<String?> deleteSpot(String spotId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/spots/$spotId'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200 || response.statusCode == 204) {
        return null;
      } else {
        final data = jsonDecode(response.body);
        return data['message'] ?? 'Failed to delete spot';
      }
    } catch (e) {
      print('Error deleting spot: $e');
      return 'Connection error';
    }
  }

  static Future<Map<String, dynamic>> scanQRCode(String qrCode, {String? spotId}) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/parking/scan-qr'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'qrCode': qrCode,
          if (spotId != null) 'spotId': spotId,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 || response.statusCode == 201) {
        return {'success': true, 'data': data};
      }
      
      return {'success': false, 'message': data['message'] ?? 'Scan failed'};
    } catch (e) {
      print('Error scanning QR: $e');
      return {'success': false, 'message': 'Connection error'};
    }
  }

  static Future<Map<String, dynamic>?> getParkingConfig() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/parking/config'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
      
      return null;
    } catch (e) {
      print('Error getting parking config: $e');
      return null;
    }
  }

  static Future<String?> updateParkingConfig({
    required double entranceLat,
    required double entranceLng,
    required double exitLat,
    required double exitLng,
    required double shopLat,
    required double shopLng,
    double? parkingCostPerHour,
    int? speedLimit,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/parking/config'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'entranceLat': entranceLat,
          'entranceLng': entranceLng,
          'exitLat': exitLat,
          'exitLng': exitLng,
          'shopLat': shopLat,
          'shopLng': shopLng,
          if (parkingCostPerHour != null) 'parkingCostPerHour': parkingCostPerHour,
          if (speedLimit != null) 'speedLimit': speedLimit,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return null;
      } else {
        final data = jsonDecode(response.body);
        return data['message'] ?? 'Failed to update config';
      }
    } catch (e) {
      print('Error updating parking config: $e');
      return 'Connection error';
    }
  }

  static Future<Map<String, dynamic>?> getAdminStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/parking/admin-status'),
        headers: {'Content-Type': 'application/json'},
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
      return null;
    } catch (e) {
      print('Error getting admin status: $e');
      return null;
    }
  }

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

  static Future<List<Map<String, dynamic>>?> getSessionHistory(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/parking/history'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.cast<Map<String, dynamic>>();
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  /// Simulate a hardware sensor event for a parking spot.
  /// [status] must be "occupied" or "available".
  static Future<bool> mockSensor(String spotName, String status) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/parking/mock-sensor'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'spotName': spotName, 'status': status}),
      );
      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      return false;
    }
  }

  /// Reserve a parking spot → LED turns BLUE on the physical model.
  static Future<Map<String, dynamic>> reserveSpot(String spotName) async {
    try {
      final email = await _storage.read(key: 'user_email');
      if (email == null) return {'ok': false, 'message': 'Not logged in'};
      final response = await http.post(
        Uri.parse('$baseUrl/parking/reserve-spot'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'spotName': spotName}),
      );
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200 || response.statusCode == 201) {
        return {'ok': true, ...data};
      }
      return {'ok': false, 'message': data['message'] ?? 'Failed to reserve'};
    } catch (e) {
      return {'ok': false, 'message': 'Connection error'};
    }
  }

  /// Cancel a spot reservation → LED turns back GREEN.
  static Future<Map<String, dynamic>> cancelReservation(String spotName) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/parking/cancel-reservation'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'spotName': spotName}),
      );
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode == 200 || response.statusCode == 201) {
        return {'ok': true, ...data};
      }
      return {'ok': false, 'message': data['message'] ?? 'Failed to cancel'};
    } catch (e) {
      return {'ok': false, 'message': 'Connection error'};
    }
  }

  static Future<Map<String, dynamic>?> getAlerts() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/parking/alerts'));
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  static Future<void> markAlertsRead() async {
    try {
      await http.post(Uri.parse('$baseUrl/parking/alerts/read'));
    } catch (_) {}
  }

  static Future<bool> addMockAlerts() async {
    try {
      final response = await http.post(Uri.parse('$baseUrl/parking/alerts/mock'));
      return response.statusCode == 200 || response.statusCode == 201;
    } catch (_) {
      return false;
    }
  }

  static Future<Map<String, dynamic>?> getLatestSpeed() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/parking/admin-status'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return data['speed'] as Map<String, dynamic>?;
      }
      return null;
    } catch (_) {
      return null;
    }
  }
}
