import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class ParkingMapScreen extends StatefulWidget {
  const ParkingMapScreen({super.key});

  @override
  State<ParkingMapScreen> createState() => _ParkingMapScreenState();
}

class _ParkingMapScreenState extends State<ParkingMapScreen> {
  List<Map<String, dynamic>> _spots = [];
  Map<String, dynamic>? _parkingConfig;
  bool _loading = true;
  
  @override
  void initState() {
    super.initState();
    _loadData();
  }
  
  Future<void> _loadData() async {
    setState(() {
      _loading = true;
    });
    
    try {
      final spots = await ApiService.getSpots();
      final config = await ApiService.getParkingConfig();
      
      if (mounted) {
        setState(() {
          _spots = spots;
          _parkingConfig = config;
          _loading = false;
        });
      }
    } catch (e) {
      print('Error loading data: $e');
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  Color _getSpotColor(String status) {
    return status == 'available' ? Colors.green.shade600 : Colors.red.shade600;
  }

  IconData _getLocationIcon(String label) {
    switch (label.toLowerCase()) {
      case 'intrare':
        return Icons.login;
      case 'ieșire':
        return Icons.logout;
      case 'magazine':
        return Icons.shopping_bag;
      default:
        return Icons.place;
    }
  }

  @override
  Widget build(BuildContext context) {
    final availableCount = _spots.where((s) => s['status'] == 'available').length;
    final totalCount = _spots.length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Hartă Parcare'),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
            tooltip: 'Reîmprospătează',
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Header cu statistici
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Colors.blue.shade700, Colors.blue.shade500],
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildStatCard(
                        'Locuri Libere',
                        '$availableCount',
                        Icons.check_circle,
                        Colors.green.shade400,
                      ),
                      _buildStatCard(
                        'Locuri Ocupate',
                        '${totalCount - availableCount}',
                        Icons.cancel,
                        Colors.red.shade400,
                      ),
                      _buildStatCard(
                        'Total Locuri',
                        '$totalCount',
                        Icons.local_parking,
                        Colors.white,
                      ),
                    ],
                  ),
                ),

                // Mock parking lot map
                Expanded(
                  child: SingleChildScrollView(
                    child: Container(
                      color: Colors.grey.shade200,
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        children: [
                          // Locații importante (Intrare, Ieșire, Magazine)
                          if (_parkingConfig != null) ...[
                            _buildLocationMarker('INTRARE', Colors.green.shade700),
                            const SizedBox(height: 20),
                          ],

                          // Grid parking spots
                          _buildParkingGrid(),

                          const SizedBox(height: 20),

                          if (_parkingConfig != null) ...[
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                _buildLocationMarker('IEȘIRE', Colors.orange.shade700),
                                _buildLocationMarker('MAGAZINE', Colors.purple.shade700),
                              ],
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ),

                // Legendă
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.05),
                        blurRadius: 10,
                        offset: const Offset(0, -2),
                      ),
                    ],
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _buildLegendItem(Icons.check_circle, 'Disponibil', Colors.green.shade600),
                      _buildLegendItem(Icons.cancel, 'Ocupat', Colors.red.shade600),
                      _buildLegendItem(Icons.place, 'Locații', Colors.blue.shade700),
                    ],
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          Text(
            label,
            style: const TextStyle(
              fontSize: 11,
              color: Colors.white70,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildLocationMarker(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_getLocationIcon(label), color: Colors.white, size: 20),
          const SizedBox(width: 8),
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildParkingGrid() {
    // Grupăm spot-urile pe rânduri (A, B, C, etc.)
    Map<String, List<Map<String, dynamic>>> rows = {};
    
    for (var spot in _spots) {
      final String name = spot['name'];
      if (name.isNotEmpty) {
        final String row = name[0]; // Prima literă (A, B, C...)
        if (!rows.containsKey(row)) {
          rows[row] = [];
        }
        rows[row]!.add(spot);
      }
    }

    // Sortăm rândurile alfabetic
    final sortedRows = rows.keys.toList()..sort();

    return Column(
      children: sortedRows.map((rowKey) {
        final rowSpots = rows[rowKey]!;
        // Sortăm spot-urile din rând numeric
        rowSpots.sort((a, b) {
          final numA = int.tryParse(a['name'].substring(1)) ?? 0;
          final numB = int.tryParse(b['name'].substring(1)) ?? 0;
          return numA.compareTo(numB);
        });

        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Column(
            children: [
              // Label rând
              Text(
                'Rândul $rowKey',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey.shade700,
                ),
              ),
              const SizedBox(height: 8),
              // Spoturi în rând
              Wrap(
                spacing: 8,
                runSpacing: 8,
                alignment: WrapAlignment.center,
                children: rowSpots.map((spot) => _buildSpotCard(spot)).toList(),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildSpotCard(Map<String, dynamic> spot) {
    final String name = spot['name'];
    final String status = spot['status'];
    final Color color = _getSpotColor(status);

    return InkWell(
      onTap: () => _showSpotDialog(spot),
      child: Container(
        width: 70,
        height: 70,
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: color.withValues(alpha: 0.3),
              blurRadius: 6,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.local_parking,
              color: Colors.white,
              size: 28,
            ),
            const SizedBox(height: 4),
            Text(
              name,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showSpotDialog(Map<String, dynamic> spot) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              Icons.local_parking,
              color: _getSpotColor(spot['status']),
            ),
            const SizedBox(width: 8),
            Text('Loc ${spot['name']}'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  spot['status'] == 'available' ? Icons.check_circle : Icons.cancel,
                  color: _getSpotColor(spot['status']),
                  size: 32,
                ),
                const SizedBox(width: 12),
                Text(
                  spot['status'] == 'available' ? 'Disponibil' : 'Ocupat',
                  style: TextStyle(
                    fontSize: 20,
                    color: _getSpotColor(spot['status']),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ],
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Închide'),
          ),
        ],
      ),
    );
  }

  Widget _buildLegendItem(IconData icon, String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 6),
        Text(
          label,
          style: TextStyle(
            color: Colors.grey.shade700,
            fontSize: 13,
          ),
        ),
      ],
    );
  }
}
