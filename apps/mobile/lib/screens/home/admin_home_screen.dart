import 'dart:async';
import 'package:flutter/material.dart';
import 'admin_overview_screen.dart';
import 'admin_scanner_screen.dart';
import 'admin_info_screen.dart';
import 'admin_alerts_screen.dart';
import 'camera_screen.dart';
import '../parking/parking_editor_combined_screen.dart';
import '../../services/api_service.dart';

class AdminHomeScreen extends StatefulWidget {
  const AdminHomeScreen({super.key});

  @override
  State<AdminHomeScreen> createState() => _AdminHomeScreenState();
}

class _AdminHomeScreenState extends State<AdminHomeScreen> {
  int _selectedIndex = 0;
  int _unreadAlerts = 0;
  Timer? _alertTimer;

  @override
  void initState() {
    super.initState();
    _pollUnreadAlerts();
    _alertTimer = Timer.periodic(const Duration(seconds: 8), (_) => _pollUnreadAlerts());
  }

  @override
  void dispose() {
    _alertTimer?.cancel();
    super.dispose();
  }

  Future<void> _pollUnreadAlerts() async {
    final data = await ApiService.getAlerts();
    if (data != null && mounted) {
      final count = (data['unread'] as num?)?.toInt() ?? 0;
      if (count != _unreadAlerts) setState(() => _unreadAlerts = count);
    }
  }

  void _onItemTapped(int index) {
    if (index == 5) setState(() => _unreadAlerts = 0); // clear badge when opening alerts
    setState(() => _selectedIndex = index);
  }

  List<Widget> get _screens => [
    const AdminOverviewScreen(),
    const ParkingEditorCombinedScreen(),
    AdminScannerScreen(onScanSuccess: () => _onItemTapped(0)),
    const CameraScreen(),
    AdminInfoScreen(onTabChange: _onItemTapped),
    const AdminAlertsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        selectedItemColor: Colors.orange.shade700,
        unselectedItemColor: Colors.grey.shade600,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
        items: [
          const BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_outlined),
            activeIcon: Icon(Icons.dashboard),
            label: 'Overview',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.edit_location_outlined),
            activeIcon: Icon(Icons.edit_location),
            label: 'Editor',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.qr_code_scanner_outlined),
            activeIcon: Icon(Icons.qr_code_scanner),
            label: 'Scanner',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.videocam_outlined),
            activeIcon: Icon(Icons.videocam),
            label: 'Camera',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.settings_outlined),
            activeIcon: Icon(Icons.settings),
            label: 'Config',
          ),
          BottomNavigationBarItem(
            icon: Badge(
              isLabelVisible: _unreadAlerts > 0,
              label: Text('$_unreadAlerts'),
              child: const Icon(Icons.notifications_outlined),
            ),
            activeIcon: Badge(
              isLabelVisible: _unreadAlerts > 0,
              label: Text('$_unreadAlerts'),
              child: const Icon(Icons.notifications),
            ),
            label: 'Alerte',
          ),
        ],
      ),
    );
  }
}
