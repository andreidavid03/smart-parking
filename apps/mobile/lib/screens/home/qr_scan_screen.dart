import 'package:flutter/material.dart';

class QRScanScreen extends StatelessWidget {
  const QRScanScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan QR Code')),
      body: const Center(
        child: Text('QR Scanner will be here'),
      ),
    );
  }
}