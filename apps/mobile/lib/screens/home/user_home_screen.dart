import 'dart:async';
import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import 'qr_scan_screen.dart';
import 'history_screen.dart';
import 'profile_screen.dart';
import '../maps/parking_map_screen.dart';

class UserHomeScreen extends StatefulWidget {
  const UserHomeScreen({super.key});

  @override
  State<UserHomeScreen> createState() => _UserHomeScreenState();
}

class _UserHomeScreenState extends State<UserHomeScreen> {
  int _selectedIndex = 0;
  Timer? _alertTimer;
  final Set<String> _shownAlertIds = {};

  late final List<Widget> _screens;

  @override
  void initState() {
    super.initState();
    _screens = [
      const QRScanScreen(),
      const ParkingMapScreen(),
      const HistoryScreen(),
      const ProfileScreen(),
    ];
    _pollCriticalAlerts();
    _alertTimer = Timer.periodic(const Duration(seconds: 15), (_) => _pollCriticalAlerts());
  }

  @override
  void dispose() {
    _alertTimer?.cancel();
    super.dispose();
  }

  Future<void> _pollCriticalAlerts() async {
    final data = await ApiService.getAlerts();
    if (data == null || !mounted) return;
    final alerts = List<Map<String, dynamic>>.from(data['alerts'] ?? []);
    final now = DateTime.now();
    for (final alert in alerts) {
      final id = alert['id']?.toString() ?? '';
      final severity = alert['severity']?.toString() ?? '';
      // Only show alerts from the last 5 minutes to avoid old/demo alerts
      final tsStr = alert['timestamp']?.toString() ?? '';
      final ts = tsStr.isNotEmpty ? DateTime.tryParse(tsStr) : null;
      final isRecent = ts != null && now.difference(ts).inMinutes < 5;
      if (severity == 'critical' && id.isNotEmpty && isRecent && !_shownAlertIds.contains(id)) {
        _shownAlertIds.add(id);
        _showCriticalAlert(alert);
        break; // show one at a time; next poll will catch remaining ones
      }
    }
  }

  void _showCriticalAlert(Map<String, dynamic> alert) {
    final type    = alert['type']?.toString() ?? '';
    final title   = alert['title']?.toString() ?? 'Alertă Critică';
    final detail  = alert['detail']?.toString() ?? '';

    Color color;
    IconData icon;
    switch (type) {
      case 'flame':
        color = Colors.deepOrange; icon = Icons.local_fire_department; break;
      case 'gas':
        color = Colors.purple.shade300; icon = Icons.air; break;
      case 'speed':
        color = Colors.orange; icon = Icons.speed; break;
      case 'temperature':
        color = Colors.red.shade400; icon = Icons.thermostat; break;
      default:
        color = Colors.red; icon = Icons.warning_amber_rounded;
    }

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        backgroundColor: const Color(0xFF1E1E2E),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: color.withOpacity(0.6), width: 1.5),
        ),
        title: Row(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                title,
                style: TextStyle(color: color, fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(detail, style: const TextStyle(color: Color(0xFFCDD6F4), fontSize: 14)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                'ALERTĂ CRITICĂ — Parcarea Smart',
                style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('Am înțeles', style: TextStyle(color: color, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        selectedItemColor: Colors.blue.shade700,
        unselectedItemColor: Colors.grey.shade600,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.qr_code_scanner_outlined),
            activeIcon: Icon(Icons.qr_code_scanner),
            label: 'My QR',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.map_outlined),
            activeIcon: Icon(Icons.map),
            label: 'Map',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history_outlined),
            activeIcon: Icon(Icons.history),
            label: 'History',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}
