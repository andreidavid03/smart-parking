import 'package:flutter/material.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Profile & Preferences')),
      body: const Center(
        child: Text('Set your spot preferences here'),
      ),
    );
  }
}