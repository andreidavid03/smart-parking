import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'user_profile_screen.dart';
import 'admin_info_screen.dart';

class ProfileScreen extends StatefulWidget {
  final Function(int)? onTabChange;
  
  const ProfileScreen({super.key, this.onTabChange});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  bool _isLoading = true;
  bool _isAdmin = false;

  @override
  void initState() {
    super.initState();
    _checkRole();
  }

  Future<void> _checkRole() async {
    final role = await _storage.read(key: 'user_role');
    setState(() {
      _isAdmin = role == 'admin';
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return _isAdmin 
        ? AdminInfoScreen(onTabChange: widget.onTabChange) 
        : const UserProfileScreen();
  }
}
