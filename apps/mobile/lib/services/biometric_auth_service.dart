import 'package:local_auth/local_auth.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class BiometricAuthService {
  final LocalAuthentication _localAuth = LocalAuthentication();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  // Keys for secure storage
  static const String _biometricEnabledKey = 'biometric_enabled';
  static const String _savedEmailKey = 'saved_email';
  static const String _savedPasswordKey = 'saved_password';

  /// Check if device supports biometric authentication
  Future<bool> isBiometricAvailable() async {
    try {
      final bool canAuthenticateWithBiometrics = await _localAuth.canCheckBiometrics;
      final bool canAuthenticate = canAuthenticateWithBiometrics || await _localAuth.isDeviceSupported();
      return canAuthenticate;
    } catch (e) {
      print('Error checking biometric availability: $e');
      return false;
    }
  }

  /// Get available biometric types (Face ID, Touch ID, etc.)
  Future<List<BiometricType>> getAvailableBiometrics() async {
    try {
      return await _localAuth.getAvailableBiometrics();
    } catch (e) {
      print('Error getting available biometrics: $e');
      return [];
    }
  }

  /// Authenticate using biometrics
  Future<bool> authenticateWithBiometrics() async {
    try {
      final bool didAuthenticate = await _localAuth.authenticate(
        localizedReason: 'Please authenticate to login to Smart Parking',
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: true,
        ),
      );
      return didAuthenticate;
    } catch (e) {
      print('Error during biometric authentication: $e');
      return false;
    }
  }

  /// Check if biometric login is enabled
  Future<bool> isBiometricEnabled() async {
    final String? enabled = await _secureStorage.read(key: _biometricEnabledKey);
    return enabled == 'true';
  }

  /// Enable biometric login and save credentials
  Future<void> enableBiometricLogin(String email, String password) async {
    await _secureStorage.write(key: _biometricEnabledKey, value: 'true');
    await _secureStorage.write(key: _savedEmailKey, value: email);
    await _secureStorage.write(key: _savedPasswordKey, value: password);
  }

  /// Disable biometric login and clear saved credentials
  Future<void> disableBiometricLogin() async {
    await _secureStorage.delete(key: _biometricEnabledKey);
    await _secureStorage.delete(key: _savedEmailKey);
    await _secureStorage.delete(key: _savedPasswordKey);
  }

  /// Get saved credentials (only after successful biometric authentication)
  Future<Map<String, String>?> getSavedCredentials() async {
    final String? email = await _secureStorage.read(key: _savedEmailKey);
    final String? password = await _secureStorage.read(key: _savedPasswordKey);

    if (email != null && password != null) {
      return {
        'email': email,
        'password': password,
      };
    }
    return null;
  }

  /// Get biometric type name for display
  String getBiometricTypeName(List<BiometricType> biometrics) {
    if (biometrics.contains(BiometricType.face)) {
      return 'Face ID';
    } else if (biometrics.contains(BiometricType.fingerprint)) {
      return 'Touch ID';
    } else if (biometrics.contains(BiometricType.iris)) {
      return 'Iris';
    } else {
      return 'Biometric';
    }
  }
}
