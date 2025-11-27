import 'package:flutter/material.dart';
import 'dart:math' as math;
import 'package:geolocator/geolocator.dart';
import 'dart:async';

class DirectionalNavigationScreen extends StatefulWidget {
  final String spotName;
  final double? spotLat;
  final double? spotLng;

  const DirectionalNavigationScreen({
    super.key,
    required this.spotName,
    this.spotLat,
    this.spotLng,
  });

  @override
  State<DirectionalNavigationScreen> createState() =>
      _DirectionalNavigationScreenState();
}

class _DirectionalNavigationScreenState
    extends State<DirectionalNavigationScreen> {
  double _distance = 0.0;
  double _bearing = 0.0;
  String _direction = 'N';
  Position? _currentPosition;
  StreamSubscription<Position>? _positionStream;
  bool _permissionGranted = false;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _initializeLocation();
  }

  @override
  void dispose() {
    _positionStream?.cancel();
    super.dispose();
  }

  Future<void> _initializeLocation() async {
    // Check and request location permission
    LocationPermission permission = await Geolocator.checkPermission();
    
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }

    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      setState(() {
        _permissionGranted = false;
        _loading = false;
      });
      return;
    }

    setState(() {
      _permissionGranted = true;
    });

    // Get initial position
    try {
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      
      setState(() {
        _currentPosition = position;
        _loading = false;
      });
      
      _calculateNavigation();

      // Start listening to position updates
      _positionStream = Geolocator.getPositionStream(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          distanceFilter: 5, // Update every 5 meters
        ),
      ).listen((Position position) {
        setState(() {
          _currentPosition = position;
        });
        _calculateNavigation();
      });
    } catch (e) {
      setState(() {
        _loading = false;
        _permissionGranted = false;
      });
    }
  }

  void _calculateNavigation() {
    if (widget.spotLat != null &&
        widget.spotLng != null &&
        _currentPosition != null) {
      _distance = _calculateDistance(
        _currentPosition!.latitude,
        _currentPosition!.longitude,
        widget.spotLat!,
        widget.spotLng!,
      );

      _bearing = _calculateBearing(
        _currentPosition!.latitude,
        _currentPosition!.longitude,
        widget.spotLat!,
        widget.spotLng!,
      );

      _direction = _getDirectionFromBearing(_bearing);
    }
  }

  double _calculateDistance(
      double lat1, double lng1, double lat2, double lng2) {
    const R = 6371e3; // Earth radius in meters
    final phi1 = lat1 * math.pi / 180;
    final phi2 = lat2 * math.pi / 180;
    final deltaPhi = (lat2 - lat1) * math.pi / 180;
    final deltaLambda = (lng2 - lng1) * math.pi / 180;

    final a = math.sin(deltaPhi / 2) * math.sin(deltaPhi / 2) +
        math.cos(phi1) *
            math.cos(phi2) *
            math.sin(deltaLambda / 2) *
            math.sin(deltaLambda / 2);
    final c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));

    return R * c; // Distance in meters
  }

  double _calculateBearing(
      double lat1, double lng1, double lat2, double lng2) {
    final phi1 = lat1 * math.pi / 180;
    final phi2 = lat2 * math.pi / 180;
    final deltaLambda = (lng2 - lng1) * math.pi / 180;

    final y = math.sin(deltaLambda) * math.cos(phi2);
    final x = math.cos(phi1) * math.sin(phi2) -
        math.sin(phi1) * math.cos(phi2) * math.cos(deltaLambda);

    final theta = math.atan2(y, x);
    final bearing = (theta * 180 / math.pi + 360) % 360;

    return bearing;
  }

  String _getDirectionFromBearing(double bearing) {
    if (bearing >= 337.5 || bearing < 22.5) return 'Nord';
    if (bearing >= 22.5 && bearing < 67.5) return 'Nord-Est';
    if (bearing >= 67.5 && bearing < 112.5) return 'Est';
    if (bearing >= 112.5 && bearing < 157.5) return 'Sud-Est';
    if (bearing >= 157.5 && bearing < 202.5) return 'Sud';
    if (bearing >= 202.5 && bearing < 247.5) return 'Sud-Vest';
    if (bearing >= 247.5 && bearing < 292.5) return 'Vest';
    if (bearing >= 292.5 && bearing < 337.5) return 'Nord-Vest';
    return 'Nord';
  }

  IconData _getArrowIcon() {
    if (_bearing >= 337.5 || _bearing < 22.5) return Icons.arrow_upward;
    if (_bearing >= 22.5 && _bearing < 67.5) return Icons.north_east;
    if (_bearing >= 67.5 && _bearing < 112.5) return Icons.arrow_forward;
    if (_bearing >= 112.5 && _bearing < 157.5) return Icons.south_east;
    if (_bearing >= 157.5 && _bearing < 202.5) return Icons.arrow_downward;
    if (_bearing >= 202.5 && _bearing < 247.5) return Icons.south_west;
    if (_bearing >= 247.5 && _bearing < 292.5) return Icons.arrow_back;
    if (_bearing >= 292.5 && _bearing < 337.5) return Icons.north_west;
    return Icons.arrow_upward;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade900,
      appBar: AppBar(
        title: const Text(
          'Navigare către Spot',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: _loading
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: Colors.white),
                  SizedBox(height: 20),
                  Text(
                    'Obținere locație GPS...',
                    style: TextStyle(color: Colors.white70, fontSize: 16),
                  ),
                ],
              ),
            )
          : !_permissionGranted
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(32.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.location_off,
                          size: 80,
                          color: Colors.red.shade400,
                        ),
                        const SizedBox(height: 20),
                        const Text(
                          'Permisiune Locație Refuzată',
                          style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Pentru navigare, aplicația necesită acces la locația ta. Te rog activează permisiunea în Settings.',
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.grey.shade400,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 32),
                        ElevatedButton.icon(
                          onPressed: () {
                            Geolocator.openLocationSettings();
                          },
                          icon: const Icon(Icons.settings),
                          label: const Text('Deschide Settings'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.blue.shade700,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(
                                horizontal: 32, vertical: 16),
                          ),
                        ),
                      ],
                    ),
                  ),
                )
              : Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Spot name
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 24, vertical: 12),
                        decoration: BoxDecoration(
                          color: Colors.blue.shade700,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                'Spotul ${widget.spotName}',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ),

            const SizedBox(height: 60),

            // Large direction arrow
            Container(
              width: 200,
              height: 200,
              decoration: BoxDecoration(
                color: Colors.blue.shade700,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.blue.withValues(alpha: 0.5),
                    blurRadius: 30,
                    spreadRadius: 10,
                  ),
                ],
              ),
              child: Icon(
                _getArrowIcon(),
                size: 120,
                color: Colors.white,
              ),
            ),

            const SizedBox(height: 40),

            // Distance
            Text(
              _distance > 0
                  ? '${_distance.toStringAsFixed(0)}m'
                  : 'Calculare...',
              style: TextStyle(
                fontSize: 64,
                fontWeight: FontWeight.bold,
                color: Colors.blue.shade400,
              ),
            ),

            const SizedBox(height: 10),

            // Direction text
            Text(
              _direction,
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.w500,
                color: Colors.grey.shade400,
              ),
            ),

            const SizedBox(height: 60),

            // Instructions
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 32),
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.grey.shade800,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.blue.shade700, width: 2),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    color: Colors.blue.shade400,
                    size: 28,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Text(
                      'Urmează săgeata pentru a ajunge la spotul tău',
                      style: TextStyle(
                        color: Colors.grey.shade300,
                        fontSize: 16,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 40),

            // Simulate arrival button (for demo)
            ElevatedButton.icon(
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: const Text('✅ Ai ajuns!'),
                    content: Text(
                        'Bine ai venit la spotul ${widget.spotName}!\nPoți parca acum.'),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    actions: [
                      TextButton(
                        onPressed: () {
                          Navigator.pop(context);
                          Navigator.pop(context);
                        },
                        child: const Text('OK'),
                      ),
                    ],
                  ),
                );
              },
              icon: const Icon(Icons.check_circle),
              label: const Text('Am ajuns la spot'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green.shade600,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
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
    );
  }
}
