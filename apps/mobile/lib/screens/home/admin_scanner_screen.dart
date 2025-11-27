import 'package:flutter/material.dart';
import 'package:qr_code_scanner/qr_code_scanner.dart';
import '../../services/api_service.dart';

class AdminScannerScreen extends StatefulWidget {
  const AdminScannerScreen({super.key});

  @override
  State<AdminScannerScreen> createState() => _AdminScannerScreenState();
}

class _AdminScannerScreenState extends State<AdminScannerScreen> {
  final GlobalKey qrKey = GlobalKey(debugLabel: 'QR');
  QRViewController? controller;
  String? _lastScannedCode;
  bool _processing = false;
  List<Map<String, dynamic>> _availableSpots = [];

  @override
  void initState() {
    super.initState();
    _loadAvailableSpots();
  }

  Future<void> _loadAvailableSpots() async {
    final spots = await ApiService.getSpots();
    setState(() {
      _availableSpots = spots.where((s) => s['status'] == 'available').toList();
    });
  }

  void _onQRViewCreated(QRViewController controller) {
    this.controller = controller;
    controller.scannedDataStream.listen((scanData) {
      if (_processing || scanData.code == null) return;
      if (_lastScannedCode == scanData.code) return; // Prevent duplicates
      
      _lastScannedCode = scanData.code;
      _handleScan(scanData.code!);
    });
  }

  Future<void> _handleScan(String qrCode) async {
    setState(() {
      _processing = true;
    });

    controller?.pauseCamera();

    // Show spot selection dialog first
    final spotId = await _showSpotSelectionDialog();
    
    if (spotId == null) {
      // User cancelled - resume scanning
      setState(() {
        _processing = false;
        _lastScannedCode = null;
      });
      controller?.resumeCamera();
      return;
    }

    final result = await ApiService.scanQRCode(qrCode, spotId: spotId);

    if (!mounted) return;

    if (result['success']) {
      final data = result['data'];
      final action = data['action'] ?? 'unknown';
      final spot = data['spot']?['name'] ?? 'N/A';
      
      _showResultDialog(
        success: true,
        title: action == 'entry' ? '✅ Entry Successful' : '✅ Exit Successful',
        message: action == 'entry' 
          ? 'Parked at spot $spot'
          : 'Session ended for spot $spot',
      );
    } else {
      _showResultDialog(
        success: false,
        title: '❌ Scan Failed',
        message: result['message'] ?? 'Unknown error',
      );
    }

    await _loadAvailableSpots(); // Refresh spots
  }

  Future<String?> _showSpotSelectionDialog() async {
    return showDialog<String>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Select Parking Spot'),
          content: SizedBox(
            width: double.maxFinite,
            child: _availableSpots.isEmpty
              ? const Padding(
                  padding: EdgeInsets.all(16),
                  child: Text('No available spots'),
                )
              : GridView.builder(
                  shrinkWrap: true,
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 4,
                    mainAxisSpacing: 8,
                    crossAxisSpacing: 8,
                  ),
                  itemCount: _availableSpots.length,
                  itemBuilder: (context, index) {
                    final spot = _availableSpots[index];
                    return ElevatedButton(
                      onPressed: () {
                        Navigator.pop(context, spot['id']);
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green.shade100,
                        foregroundColor: Colors.green.shade900,
                        padding: const EdgeInsets.all(8),
                      ),
                      child: Text(
                        spot['name'] as String,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    );
                  },
                ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
          ],
        );
      },
    );
  }

  void _showResultDialog({
    required bool success,
    required String title,
    required String message,
  }) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                _processing = false;
                _lastScannedCode = null;
              });
              controller?.resumeCamera();
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Admin Scanner'),
        backgroundColor: Colors.orange.shade700,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAvailableSpots,
            tooltip: 'Refresh Spots',
          ),
        ],
      ),
      body: Column(
        children: [
          // Available spots counter
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.orange.shade50,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.local_parking, color: Colors.orange.shade700),
                const SizedBox(width: 8),
                Text(
                  '${_availableSpots.length} spots available',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange.shade900,
                  ),
                ),
              ],
            ),
          ),

          // QR Scanner
          Expanded(
            child: QRView(
              key: qrKey,
              onQRViewCreated: _onQRViewCreated,
              overlay: QrScannerOverlayShape(
                borderColor: Colors.orange,
                borderRadius: 10,
                borderLength: 30,
                borderWidth: 10,
                cutOutSize: 300,
              ),
            ),
          ),

          // Instructions
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.white,
            child: Column(
              children: [
                Icon(Icons.qr_code_scanner, size: 48, color: Colors.orange.shade700),
                const SizedBox(height: 8),
                const Text(
                  'Scan User QR Code',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Text(
                  'Point camera at QR code to record entry/exit',
                  style: TextStyle(color: Colors.grey[600]),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
