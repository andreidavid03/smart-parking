import 'package:flutter/material.dart';
import 'screens/auth/login_screen.dart';
import 'screens/home/user_home_screen.dart';
import 'screens/home/admin_home_screen.dart';
import 'screens/theme/app_theme.dart';

class SmartParkingApp extends StatelessWidget {
  const SmartParkingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Parking',
      theme: AppTheme.light,
      initialRoute: '/login',
      routes: {
        '/login': (_) => const LoginScreen(),
        '/home/user': (_) => const UserHomeScreen(),
        '/home/admin': (_) => const AdminHomeScreen(),
      },
    );
  }
}