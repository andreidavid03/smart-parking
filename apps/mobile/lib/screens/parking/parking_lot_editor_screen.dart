import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class ParkingLotEditorScreen extends StatefulWidget {
  const ParkingLotEditorScreen({super.key});

  @override
  State<ParkingLotEditorScreen> createState() => _ParkingLotEditorScreenState();
}

class _ParkingLotEditorScreenState extends State<ParkingLotEditorScreen> {
  List<Map<String, dynamic>> _spots = [];
  bool _isLoading = true;
  bool _isSaving = false;
  
  // Pentru a adăuga spots noi
  final TextEditingController _newSpotController = TextEditingController();

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

  Future<void> _addSpot() async {
    final name = _newSpotController.text.trim().toUpperCase();
    
    if (name.isEmpty) {
      _showError('Te rog introdu un nume pentru spot (ex: A1, B5, C12)');
      return;
    }

    // Check if spot already exists
    if (_spots.any((spot) => spot['name'] == name)) {
      _showError('Spotul $name există deja!');
      return;
    }

    setState(() => _isSaving = true);

    final result = await ApiService.createSpot(name);
    
    if (result != null && result['success'] == true) {
      _newSpotController.clear();
      await _loadSpots();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ Spot $name adăugat!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } else {
      _showError(result?['message'] ?? 'Eroare la adăugarea spotului');
    }

    setState(() => _isSaving = false);
  }

  Future<void> _deleteSpot(String spotId, String spotName) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Șterge Spot'),
        content: Text('Ești sigur că vrei să ștergi spotul $spotName?'),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Anulează'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Șterge'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    setState(() => _isSaving = true);

    final result = await ApiService.deleteSpot(spotId);
    
    if (result == null) {
      await _loadSpots();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('🗑️ Spot $spotName șters!'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } else {
      _showError(result);
    }

    setState(() => _isSaving = false);
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  Color _getSpotColor(String status) {
    switch (status.toLowerCase()) {
      case 'occupied':
        return Colors.red.shade400;
      case 'available':
        return Colors.green.shade400;
      default:
        return Colors.grey.shade400;
    }
  }

  IconData _getSpotIcon(String status) {
    switch (status.toLowerCase()) {
      case 'occupied':
        return Icons.local_parking;
      case 'available':
        return Icons.check_circle;
      default:
        return Icons.block;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      appBar: AppBar(
        title: const Text(
          'Editor Parcare',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.orange.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadSpots,
            tooltip: 'Reîncarcă',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Header cu statistici
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Colors.orange.shade700, Colors.orange.shade500],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildStatCard(
                            'Total Spoturi',
                            _spots.length.toString(),
                            Icons.grid_on,
                          ),
                          _buildStatCard(
                            'Disponibile',
                            _spots.where((s) => s['status'] == 'available').length.toString(),
                            Icons.check_circle,
                          ),
                          _buildStatCard(
                            'Ocupate',
                            _spots.where((s) => s['status'] == 'occupied').length.toString(),
                            Icons.local_parking,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                // Add new spot section
                Container(
                  margin: const EdgeInsets.all(16),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
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
                      Expanded(
                        child: TextField(
                          controller: _newSpotController,
                          decoration: InputDecoration(
                            hintText: 'Nume spot (ex: A1, B5, C12)',
                            prefixIcon: const Icon(Icons.add_location_alt),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            filled: true,
                            fillColor: Colors.grey.shade50,
                          ),
                          textCapitalization: TextCapitalization.characters,
                          onSubmitted: (_) => _addSpot(),
                        ),
                      ),
                      const SizedBox(width: 12),
                      ElevatedButton.icon(
                        onPressed: _isSaving ? null : _addSpot,
                        icon: _isSaving
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Icon(Icons.add),
                        label: const Text('Adaugă'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange.shade700,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 24,
                            vertical: 16,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // Spots grid
                Expanded(
                  child: _spots.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.local_parking_outlined,
                                size: 80,
                                color: Colors.grey.shade400,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                'Nu există spoturi',
                                style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Adaugă primul spot folosind formularul de mai sus',
                                style: TextStyle(
                                  color: Colors.grey.shade500,
                                ),
                              ),
                            ],
                          ),
                        )
                      : GridView.builder(
                          padding: const EdgeInsets.all(16),
                          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 3,
                            childAspectRatio: 1.2,
                            crossAxisSpacing: 12,
                            mainAxisSpacing: 12,
                          ),
                          itemCount: _spots.length,
                          itemBuilder: (context, index) {
                            final spot = _spots[index];
                            final spotName = spot['name'] ?? 'N/A';
                            final spotStatus = spot['status'] ?? 'available';
                            final spotId = spot['id'];

                            return Card(
                              elevation: 4,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(16),
                              ),
                              child: InkWell(
                                onLongPress: () => _deleteSpot(spotId, spotName),
                                borderRadius: BorderRadius.circular(16),
                                child: Container(
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      colors: [
                                        _getSpotColor(spotStatus),
                                        _getSpotColor(spotStatus).withValues(alpha: 0.7),
                                      ],
                                      begin: Alignment.topLeft,
                                      end: Alignment.bottomRight,
                                    ),
                                    borderRadius: BorderRadius.circular(16),
                                  ),
                                  child: Column(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Icon(
                                        _getSpotIcon(spotStatus),
                                        color: Colors.white,
                                        size: 32,
                                      ),
                                      const SizedBox(height: 8),
                                      Text(
                                        spotName,
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 18,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        spotStatus == 'occupied' ? 'Ocupat' : 'Liber',
                                        style: TextStyle(
                                          color: Colors.white.withValues(alpha: 0.9),
                                          fontSize: 12,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                ),

                // Help text
                Container(
                  padding: const EdgeInsets.all(16),
                  color: Colors.orange.shade50,
                  child: Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.orange.shade700, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Ține apăsat pe un spot pentru a-l șterge',
                          style: TextStyle(
                            color: Colors.orange.shade700,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: Colors.white, size: 28),
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
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.9),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _newSpotController.dispose();
    super.dispose();
  }
}
