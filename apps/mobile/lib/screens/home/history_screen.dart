import 'package:flutter/material.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Parking History')),
      body: const Center(
        child: Text('Your parking sessions will be listed here'),
      ),
    );
  }
}