import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class BypassModeScreen extends StatefulWidget {
  const BypassModeScreen({super.key});

  @override
  State<BypassModeScreen> createState() => _BypassModeScreenState();
}

class _BypassModeScreenState extends State<BypassModeScreen> {
  bool _entranceBarrierOpen = false;
  bool _exitBarrierOpen = false;
  String? _detectedCarSpot;
  List<Map<String, dynamic>> _spots = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSpots();
  }

  Future<void> _loadSpots() async {
    setState(() => _isLoading = true);
    final spots = await ApiService.getSpots();
    if (mounted) {
      setState(() {
        _spots = List<Map<String, dynamic>>.from(spots);
        _isLoading = false;
      });
    }
  }

  void _toggleEntranceBarrier() {
    setState(() {
      _entranceBarrierOpen = !_entranceBarrierOpen;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          _entranceBarrierOpen
              ? '✅ Bariera INTRARE deschisă'
              : '⛔ Bariera INTRARE închisă',
        ),
        backgroundColor: _entranceBarrierOpen ? Colors.green : Colors.red,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _toggleExitBarrier() {
    setState(() {
      _exitBarrierOpen = !_exitBarrierOpen;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          _exitBarrierOpen
              ? '✅ Bariera IEȘIRE deschisă'
              : '⛔ Bariera IEȘIRE închisă',
        ),
        backgroundColor: _exitBarrierOpen ? Colors.green : Colors.red,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _simulateCarDetection(String spotName) {
    setState(() {
      _detectedCarSpot = spotName;
    });

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('🚗 Mașină Detectată'),
        content: Text(
          'Senzor simulat: Mașină detectată în spotul $spotName\n\nÎn producție, acest semnal ar veni de la senzori fizici (ultrasonici sau camera).',
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        actions: [
          TextButton(
            onPressed: () {
              setState(() {
                _detectedCarSpot = null;
              });
              Navigator.pop(context);
            },
            child: const Text('Șterge detectare'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      appBar: AppBar(
        title: const Text(
          '⚙️ BYPASS Mode',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.deepPurple.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Column(
                children: [
                  // Header
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Colors.deepPurple.shade700,
                          Colors.deepPurple.shade500
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                    ),
                    child: Column(
                      children: [
                        const Icon(
                          Icons.construction,
                          size: 50,
                          color: Colors.white,
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'Simulare Hardware',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Testează funcționalitățile fără hardware fizic',
                          style: TextStyle(
                            color: Colors.white.withValues(alpha: 0.9),
                            fontSize: 14,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Barrier Controls
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          '🚧 Control Bariere',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),

                        // Entrance Barrier
                        _buildBarrierCard(
                          'Barieră Intrare',
                          Icons.login,
                          Colors.green,
                          _entranceBarrierOpen,
                          _toggleEntranceBarrier,
                        ),

                        const SizedBox(height: 12),

                        // Exit Barrier
                        _buildBarrierCard(
                          'Barieră Ieșire',
                          Icons.logout,
                          Colors.orange,
                          _exitBarrierOpen,
                          _toggleExitBarrier,
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Car Detection Simulation
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          '🚗 Simulare Detectare Mașină',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Apasă pe un spot pentru a simula detectarea unei mașini',
                          style: TextStyle(
                            color: Colors.grey.shade600,
                            fontSize: 14,
                          ),
                        ),
                        const SizedBox(height: 16),

                        if (_detectedCarSpot != null)
                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(16),
                            margin: const EdgeInsets.only(bottom: 16),
                            decoration: BoxDecoration(
                              color: Colors.blue.shade50,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                  color: Colors.blue.shade700, width: 2),
                            ),
                            child: Row(
                              children: [
                                Icon(Icons.directions_car,
                                    color: Colors.blue.shade700, size: 32),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      const Text(
                                        'Mașină Detectată',
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 16,
                                        ),
                                      ),
                                      Text(
                                        'Spot: $_detectedCarSpot',
                                        style: TextStyle(
                                          color: Colors.grey.shade700,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                IconButton(
                                  icon: const Icon(Icons.close),
                                  onPressed: () {
                                    setState(() {
                                      _detectedCarSpot = null;
                                    });
                                  },
                                ),
                              ],
                            ),
                          ),

                        GridView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          gridDelegate:
                              const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 4,
                            childAspectRatio: 1.2,
                            crossAxisSpacing: 8,
                            mainAxisSpacing: 8,
                          ),
                          itemCount: _spots.length,
                          itemBuilder: (context, index) {
                            final spot = _spots[index];
                            final spotName = spot['name'] ?? 'N/A';
                            final isDetected = _detectedCarSpot == spotName;
                            final isOccupied = spot['status'] == 'occupied';

                            return GestureDetector(
                              onTap: () => _simulateCarDetection(spotName),
                              child: Container(
                                decoration: BoxDecoration(
                                  color: isDetected
                                      ? Colors.blue.shade700
                                      : (isOccupied
                                          ? Colors.red.shade100
                                          : Colors.green.shade50),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(
                                    color: isDetected
                                        ? Colors.blue.shade900
                                        : (isOccupied
                                            ? Colors.red.shade300
                                            : Colors.green.shade300),
                                    width: 2,
                                  ),
                                ),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(
                                      isDetected
                                          ? Icons.directions_car
                                          : Icons.local_parking,
                                      color: isDetected
                                          ? Colors.white
                                          : (isOccupied
                                              ? Colors.red.shade700
                                              : Colors.green.shade700),
                                      size: 24,
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      spotName,
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 12,
                                        color: isDetected
                                            ? Colors.white
                                            : Colors.black87,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Info footer
                  Container(
                    margin: const EdgeInsets.all(16),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.deepPurple.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border:
                          Border.all(color: Colors.deepPurple.shade200),
                    ),
                    child: Column(
                      children: [
                        Row(
                          children: [
                            Icon(Icons.info_outline,
                                color: Colors.deepPurple.shade700),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                'BYPASS Mode - Simulare Hardware',
                                style: TextStyle(
                                  color: Colors.deepPurple.shade700,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Aceste controale simulează hardware-ul fizic (bariere, senzori) care va fi integrat în 2 luni. Folosește acest mod pentru testare și development.',
                          style: TextStyle(
                            color: Colors.deepPurple.shade700,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildBarrierCard(
    String title,
    IconData icon,
    Color color,
    bool isOpen,
    VoidCallback onToggle,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isOpen ? color : Colors.grey.shade300,
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 32),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Text(
                  isOpen ? 'Deschisă ✅' : 'Închisă ⛔',
                  style: TextStyle(
                    color: isOpen ? Colors.green : Colors.red,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: isOpen,
            onChanged: (_) => onToggle(),
            activeThumbColor: color,
          ),
        ],
      ),
    );
  }
}
