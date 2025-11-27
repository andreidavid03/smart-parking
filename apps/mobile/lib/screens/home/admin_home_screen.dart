import 'package:flutter/material.dart';
import 'spots_screen.dart';
import 'admin_scanner_screen.dart';
import 'history_screen.dart';
import 'profile_screen.dart';
import '../parking/parking_lot_editor_screen.dart';
import '../parking/parking_config_screen.dart';
import '../bypass/bypass_mode_screen.dart';

class AdminHomeScreen extends StatefulWidget {
  const AdminHomeScreen({super.key});

  @override
  State<AdminHomeScreen> createState() => _AdminHomeScreenState();
}

class _AdminHomeScreenState extends State<AdminHomeScreen> {
  int _selectedIndex = 0;

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  List<Widget> get _screens => [
    const SpotsScreen(),
    const ParkingLotEditorScreen(),
    const ParkingConfigScreen(),
    const BypassModeScreen(),
    const AdminScannerScreen(),
    const HistoryScreen(),
    ProfileScreen(onTabChange: _onItemTapped),
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
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.local_parking_outlined),
            activeIcon: Icon(Icons.local_parking),
            label: 'Spots',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.edit_location_outlined),
            activeIcon: Icon(Icons.edit_location),
            label: 'Editor',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings_outlined),
            activeIcon: Icon(Icons.settings),
            label: 'Config',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.construction_outlined),
            activeIcon: Icon(Icons.construction),
            label: 'BYPASS',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.qr_code_scanner_outlined),
            activeIcon: Icon(Icons.qr_code_scanner),
            label: 'Scanner',
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
