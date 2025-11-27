import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../services/api_service.dart';
import '../../services/biometric_auth_service.dart';
import 'signup_screen.dart';
import 'forgot_password_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final BiometricAuthService _biometricService = BiometricAuthService();
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  
  String _email = '';
  String _password = '';
  bool _loading = false;
  String? _error;
  bool _biometricAvailable = false;
  bool _biometricEnabled = false;
  String _biometricType = 'Biometric';

  @override
  void initState() {
    super.initState();
    _checkBiometricAvailability();
  }

  Future<void> _checkBiometricAvailability() async {
    final available = await _biometricService.isBiometricAvailable();
    final enabled = await _biometricService.isBiometricEnabled();
    
    if (available) {
      final biometrics = await _biometricService.getAvailableBiometrics();
      final typeName = _biometricService.getBiometricTypeName(biometrics);
      
      setState(() {
        _biometricAvailable = available;
        _biometricEnabled = enabled;
        _biometricType = typeName;
      });
    }
  }

  Future<void> _loginWithBiometrics() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    final authenticated = await _biometricService.authenticateWithBiometrics();
    
    if (!authenticated) {
      setState(() {
        _loading = false;
        _error = 'Biometric authentication failed';
      });
      return;
    }

    // Get saved credentials
    final credentials = await _biometricService.getSavedCredentials();
    
    if (credentials == null) {
      setState(() {
        _loading = false;
        _error = 'No saved credentials found';
      });
      return;
    }

    // Login with saved credentials
    final error = await ApiService.login(credentials['email']!, credentials['password']!);
    
    if (!mounted) return;
    
    setState(() {
      _loading = false;
      _error = error;
    });
    
    if (error == null) {
      print('Biometric login successful');
      // Navigate based on role
      final role = await _storage.read(key: 'user_role') ?? 'user';
      if (mounted) {
        Navigator.pushReplacementNamed(
          context,
          role == 'admin' ? '/home/admin' : '/home/user',
        );
      }
    }
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();

    setState(() {
      _loading = true;
      _error = null;
    });

    final error = await ApiService.login(_email, _password);
    
    if (!mounted) return;
    
    setState(() {
      _loading = false;
      _error = error;
    });
    
    if (error == null) {
      print('Login successful');
      
      // Get user role from storage
      final role = await _storage.read(key: 'user_role') ?? 'user';
      
      // Offer to enable biometric login if available and not already enabled
      if (_biometricAvailable && !_biometricEnabled) {
        _showEnableBiometricDialog(role);
      } else {
        if (mounted) {
          Navigator.pushReplacementNamed(
            context,
            role == 'admin' ? '/home/admin' : '/home/user',
          );
        }
      }
    }
  }

  void _showEnableBiometricDialog(String role) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Enable $_biometricType'),
          content: Text('Would you like to enable $_biometricType for faster login?'),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.pushReplacementNamed(
                  context,
                  role == 'admin' ? '/home/admin' : '/home/user',
                );
              },
              child: const Text('Not Now'),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(context);
                await _biometricService.enableBiometricLogin(_email, _password);
                setState(() {
                  _biometricEnabled = true;
                });
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('$_biometricType enabled successfully')),
                  );
                  Navigator.pushReplacementNamed(
                    context,
                    role == 'admin' ? '/home/admin' : '/home/user',
                  );
                }
              },
              child: const Text('Enable'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(32),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Logo/Icon
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    Icons.local_parking,
                    size: 80,
                    color: Colors.blue.shade700,
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'Smart Parking',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade900,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  'Welcome back!',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: Colors.grey[600],
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 40),
                
                // Biometric login button (if available and enabled)
                if (_biometricAvailable && _biometricEnabled) ...[
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _loading ? null : _loginWithBiometrics,
                      icon: Icon(
                        _biometricType == 'Face ID' 
                          ? Icons.face 
                          : Icons.fingerprint,
                        size: 24,
                      ),
                      label: Text('Login with $_biometricType'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: Colors.blue.shade700,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  const Row(
                    children: [
                      Expanded(child: Divider()),
                      Padding(
                        padding: EdgeInsets.symmetric(horizontal: 16),
                        child: Text('OR', style: TextStyle(color: Colors.grey)),
                      ),
                      Expanded(child: Divider()),
                    ],
                  ),
                  const SizedBox(height: 24),
                ],
                
                // Email field
                TextFormField(
                  decoration: InputDecoration(
                    labelText: 'Email',
                    hintText: 'your.email@example.com',
                    prefixIcon: const Icon(Icons.email_outlined),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    filled: true,
                    fillColor: Colors.white,
                  ),
                  keyboardType: TextInputType.emailAddress,
                  validator: (v) => v != null && RegExp(r'^[^@]+@[^@]+\.[^@]+').hasMatch(v)
                      ? null
                      : 'Enter a valid email',
                  onSaved: (v) => _email = v!.trim(),
                ),
                const SizedBox(height: 16),
                
                // Password field
                TextFormField(
                  decoration: InputDecoration(
                    labelText: 'Password',
                    hintText: 'Enter your password',
                    prefixIcon: const Icon(Icons.lock_outline),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    filled: true,
                    fillColor: Colors.white,
                  ),
                  obscureText: true,
                  validator: (v) => v != null && v.length >= 8
                      ? null
                      : 'Min 8 characters',
                  onSaved: (v) => _password = v!,
                ),
                const SizedBox(height: 24),
                
                // Error message
                if (_error != null)
                  Container(
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.red.shade200),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.error_outline, color: Colors.red.shade700),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _error!,
                            style: TextStyle(color: Colors.red.shade700),
                          ),
                        ),
                      ],
                    ),
                  ),
                
                // Login button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _login,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: Colors.blue.shade600,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 2,
                    ),
                    child: _loading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : const Text(
                            'Login',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                  ),
                ),
                const SizedBox(height: 16),
                
                // Forgot password link
                TextButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const ForgotPasswordScreen()),
                    );
                  },
                  child: Text(
                    'Forgot Password?',
                    style: TextStyle(
                      color: Colors.blue.shade700,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                
                // Signup link
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      "Don't have an account? ",
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                    TextButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => const SignupScreen()),
                        );
                      },
                      style: TextButton.styleFrom(
                        padding: EdgeInsets.zero,
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      child: Text(
                        'Sign up',
                        style: TextStyle(
                          color: Colors.blue.shade700,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}