import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class SpotsScreen extends StatefulWidget {
  const SpotsScreen({super.key});

  @override
  State<SpotsScreen> createState() => _SpotsScreenState();
}

class _SpotsScreenState extends State<SpotsScreen> {
  bool _loading = true;
  List<Map<String, dynamic>> _spots = [];

  @override
  void initState() {
    super.initState();
    _loadSpots();
  }

  Future<void> _loadSpots() async {
    setState(() {
      _loading = true;
    });

    final spots = await ApiService.getSpots();

    if (mounted) {
      setState(() {
        _spots = spots;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Parking Spots'),
        backgroundColor: Colors.green.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadSpots,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _spots.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.local_parking, size: 64, color: Colors.grey[400]),
                      const SizedBox(height: 16),
                      Text(
                        'No parking spots available',
                        style: TextStyle(fontSize: 18, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                )
              : Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Stats
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [Colors.green.shade700, Colors.green.shade500],
                          ),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceAround,
                          children: [
                            _buildStatCard(
                              'Total',
                              _spots.length.toString(),
                              Icons.local_parking,
                              Colors.white,
                            ),
                            _buildStatCard(
                              'Available',
                              _spots.where((s) => s['status'] == 'available').length.toString(),
                              Icons.check_circle,
                              Colors.lightGreenAccent,
                            ),
                            _buildStatCard(
                              'Occupied',
                              _spots.where((s) => s['status'] == 'occupied').length.toString(),
                              Icons.cancel,
                              Colors.redAccent,
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Zones
                      Expanded(
                        child: ListView(
                          children: [
                            _buildZoneSection('Zone A', _spots.where((s) => (s['name'] as String).startsWith('A')).toList()),
                            const SizedBox(height: 24),
                            _buildZoneSection('Zone B', _spots.where((s) => (s['name'] as String).startsWith('B')).toList()),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color iconColor) {
    return Column(
      children: [
        Icon(icon, color: iconColor, size: 32),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildZoneSection(String zoneName, List<Map<String, dynamic>> zoneSpots) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          zoneName,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 5,
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 1,
          ),
          itemCount: zoneSpots.length,
          itemBuilder: (context, index) {
            final spot = zoneSpots[index];
            final isAvailable = spot['status'] == 'available';

            return Container(
              decoration: BoxDecoration(
                color: isAvailable ? Colors.green.shade100 : Colors.red.shade100,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isAvailable ? Colors.green.shade700 : Colors.red.shade700,
                  width: 2,
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.05),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    isAvailable ? Icons.check_circle : Icons.directions_car,
                    color: isAvailable ? Colors.green.shade700 : Colors.red.shade700,
                    size: 24,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    spot['name'] as String,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: isAvailable ? Colors.green.shade900 : Colors.red.shade900,
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }
}
