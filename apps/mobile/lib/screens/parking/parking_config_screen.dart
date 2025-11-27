import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import '../../services/api_service.dart';

class ParkingConfigScreen extends StatefulWidget {
  const ParkingConfigScreen({super.key});

  @override
  State<ParkingConfigScreen> createState() => _ParkingConfigScreenState();
}

class _ParkingConfigScreenState extends State<ParkingConfigScreen> {
  bool _isLoading = true;
  bool _isSaving = false;
  
  LatLng _entrancePos = const LatLng(37.7749, -122.4194);
  LatLng _exitPos = const LatLng(37.7750, -122.4195);
  LatLng _shopPos = const LatLng(37.7751, -122.4196);
  
  String _selectedMarker = 'entrance'; // 'entrance', 'exit', 'shop'
  
  final Set<Marker> _markers = {};

  @override
  void initState() {
    super.initState();
    _loadConfig();
  }

  Future<void> _loadConfig() async {
    setState(() {
      _isLoading = true;
    });

    final config = await ApiService.getParkingConfig();
    
    if (config != null && mounted) {
      setState(() {
        _entrancePos = LatLng(
          config['entranceLat'] as double,
          config['entranceLng'] as double,
        );
        _exitPos = LatLng(
          config['exitLat'] as double,
          config['exitLng'] as double,
        );
        _shopPos = LatLng(
          config['shopLat'] as double,
          config['shopLng'] as double,
        );
        _isLoading = false;
      });
      _updateMarkers();
    } else {
      setState(() {
        _isLoading = false;
      });
      _updateMarkers();
    }
  }

  void _updateMarkers() {
    setState(() {
      _markers.clear();
      
      _markers.add(
        Marker(
          markerId: const MarkerId('entrance'),
          position: _entrancePos,
          icon: BitmapDescriptor.defaultMarkerWithHue(
            _selectedMarker == 'entrance' 
                ? BitmapDescriptor.hueGreen 
                : BitmapDescriptor.hueBlue,
          ),
          infoWindow: const InfoWindow(title: '🚪 Entrance'),
          onTap: () => setState(() => _selectedMarker = 'entrance'),
        ),
      );
      
      _markers.add(
        Marker(
          markerId: const MarkerId('exit'),
          position: _exitPos,
          icon: BitmapDescriptor.defaultMarkerWithHue(
            _selectedMarker == 'exit' 
                ? BitmapDescriptor.hueGreen 
                : BitmapDescriptor.hueOrange,
          ),
          infoWindow: const InfoWindow(title: '🚗 Exit'),
          onTap: () => setState(() => _selectedMarker = 'exit'),
        ),
      );
      
      _markers.add(
        Marker(
          markerId: const MarkerId('shop'),
          position: _shopPos,
          icon: BitmapDescriptor.defaultMarkerWithHue(
            _selectedMarker == 'shop' 
                ? BitmapDescriptor.hueGreen 
                : BitmapDescriptor.hueMagenta,
          ),
          infoWindow: const InfoWindow(title: '🏪 Shop'),
          onTap: () => setState(() => _selectedMarker = 'shop'),
        ),
      );
    });
  }

  void _onMapTap(LatLng position) {
    setState(() {
      switch (_selectedMarker) {
        case 'entrance':
          _entrancePos = position;
          break;
        case 'exit':
          _exitPos = position;
          break;
        case 'shop':
          _shopPos = position;
          break;
      }
    });
    _updateMarkers();
  }

  Future<void> _saveConfig() async {
    setState(() {
      _isSaving = true;
    });

    final error = await ApiService.updateParkingConfig(
      entranceLat: _entrancePos.latitude,
      entranceLng: _entrancePos.longitude,
      exitLat: _exitPos.latitude,
      exitLng: _exitPos.longitude,
      shopLat: _shopPos.latitude,
      shopLng: _shopPos.longitude,
    );

    if (mounted) {
      setState(() {
        _isSaving = false;
      });

      if (error == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Parking configuration saved!'),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error: $error'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Configure Parking Layout'),
        backgroundColor: Colors.indigo.shade700,
        foregroundColor: Colors.white,
        actions: [
          if (!_isLoading)
            IconButton(
              onPressed: _isSaving ? null : _saveConfig,
              icon: _isSaving
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : const Icon(Icons.save),
              tooltip: 'Save Configuration',
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Instructions
                Container(
                  padding: const EdgeInsets.all(16),
                  color: Colors.indigo.shade50,
                  child: Column(
                    children: [
                      const Text(
                        'Tap on map to place markers',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          _buildMarkerButton(
                            '🚪 Entrance',
                            'entrance',
                            Colors.blue,
                          ),
                          _buildMarkerButton(
                            '🚗 Exit',
                            'exit',
                            Colors.orange,
                          ),
                          _buildMarkerButton(
                            '🏪 Shop',
                            'shop',
                            Colors.purple,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                
                // FUTURE: Custom Macheta Overlay
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  color: Colors.amber.shade50,
                  child: Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.amber.shade700, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          '💡 Viitor: Macheta Overlay + Google Maps API pentru navigație reală',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.amber.shade900,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Map
                Expanded(
                  child: GoogleMap(
                    initialCameraPosition: CameraPosition(
                      target: _entrancePos,
                      zoom: 17,
                    ),
                    markers: _markers,
                    onTap: _onMapTap,
                    myLocationButtonEnabled: true,
                    myLocationEnabled: true,
                    mapType: MapType.hybrid,
                  ),
                ),
                
                // Info panel
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.1),
                        blurRadius: 10,
                        offset: const Offset(0, -2),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      _buildInfoRow('🚪 Entrance', _entrancePos, Colors.blue),
                      const SizedBox(height: 8),
                      _buildInfoRow('🚗 Exit', _exitPos, Colors.orange),
                      const SizedBox(height: 8),
                      _buildInfoRow('🏪 Shop', _shopPos, Colors.purple),
                    ],
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildMarkerButton(String label, String value, Color color) {
    final isSelected = _selectedMarker == value;
    
    return ElevatedButton(
      onPressed: () {
        setState(() {
          _selectedMarker = value;
        });
        _updateMarkers();
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: isSelected ? color : Colors.grey.shade200,
        foregroundColor: isSelected ? Colors.white : Colors.black87,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(
            color: isSelected ? color : Colors.transparent,
            width: 2,
          ),
        ),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, LatLng position, Color color) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            label,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
        ),
        Text(
          '${position.latitude.toStringAsFixed(6)}, ${position.longitude.toStringAsFixed(6)}',
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
            fontFamily: 'monospace',
          ),
        ),
      ],
    );
  }
}
