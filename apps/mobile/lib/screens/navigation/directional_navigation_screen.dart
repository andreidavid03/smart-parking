import 'package:flutter/material.dart';
import 'dart:math' as math;
import 'package:geolocator/geolocator.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:async';
import '../../services/api_service.dart';
import '../payment/payment_screen.dart';

class DirectionalNavigationScreen extends StatefulWidget {
  final String spotName;
  final double? spotLat;
  final double? spotLng;
  final String sessionId;
  final String sessionStartTime;

  const DirectionalNavigationScreen({
    super.key,
    required this.spotName,
    this.spotLat,
    this.spotLng,
    required this.sessionId,
    required this.sessionStartTime,
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
  bool _arrived = false;
  bool _navigatedToPayment = false;
  Timer? _sessionPollTimer;
  Timer? _uiRefreshTimer;
  bool _exitLoading = false;
  String? _userEmail;

  // ── Speed alert ─────────────────────────────────────────────────────────────
  static const double _speedLimitKmh = 10.0;
  Timer? _speedPollTimer;
  bool _speedAlertVisible = false;
  double _speedAlertValue = 0.0;
  Timer? _speedAlertDismissTimer;

  @override
  void initState() {
    super.initState();
    _initializeLocation();
    _loadEmailAndStartPolling();
    _startSpeedPolling();
  }

  @override
  void dispose() {
    _positionStream?.cancel();
    _sessionPollTimer?.cancel();
    _uiRefreshTimer?.cancel();
    _speedPollTimer?.cancel();
    _speedAlertDismissTimer?.cancel();
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

  Future<void> _loadEmailAndStartPolling() async {
    const storage = FlutterSecureStorage();
    _userEmail = await storage.read(key: 'user_email');
    _sessionPollTimer = Timer.periodic(
      const Duration(seconds: 3),
      (_) => _checkSessionStatus(),
    );
  }

  void _startSpeedPolling() {
    _speedPollTimer = Timer.periodic(const Duration(seconds: 3), (_) async {
      final speed = await ApiService.getLatestSpeed();
      if (!mounted) return;
      final kmh = (speed?['speed_kmh'] as num?)?.toDouble() ?? 0;
      if (kmh > _speedLimitKmh) {
        _showSpeedAlert(kmh);
      }
    });
  }

  void _showSpeedAlert(double kmh) {
    if (_speedAlertVisible) return; // already showing
    setState(() {
      _speedAlertVisible = true;
      _speedAlertValue = kmh;
    });
    _speedAlertDismissTimer?.cancel();
    _speedAlertDismissTimer = Timer(const Duration(seconds: 12), _dismissSpeedAlert);
  }

  void _dismissSpeedAlert() {
    if (mounted) setState(() => _speedAlertVisible = false);
    _speedAlertDismissTimer?.cancel();
  }

  Future<void> _checkSessionStatus() async {
    if (_navigatedToPayment || _userEmail == null || !mounted) return;
    final result = await ApiService.getCurrentSession(_userEmail!);
    if (result == null || !mounted) return;
    if (result['hasActiveSession'] != true) {
      _navigatedToPayment = true;
      _sessionPollTimer?.cancel();
      _uiRefreshTimer?.cancel();
      final lastSession = await ApiService.getLastSession(_userEmail!);
      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => PaymentScreen(
            spotName: widget.spotName,
            sessionId: widget.sessionId,
            durationMinutes:
                (lastSession?['durationMinutes'] as num?)?.toInt() ?? 0,
            costPerHour:
                (lastSession?['costPerHour'] as num?)?.toDouble() ?? 5.0,
            totalCost:
                (lastSession?['totalCost'] as num?)?.toDouble() ?? 0.0,
          ),
        ),
      );
    }
  }

  void _arriveAtSpot() {
    if (_arrived) return;
    setState(() => _arrived = true);
    _uiRefreshTimer = Timer.periodic(
      const Duration(seconds: 1),
      (_) { if (mounted) setState(() {}); },
    );
  }

  /// Actual elapsed time since the session started on the server.
  Duration get _elapsed {
    final start = DateTime.tryParse(widget.sessionStartTime);
    if (start == null) return Duration.zero;
    return DateTime.now().difference(start.toLocal());
  }

  String get _parkingDurationString {
    final d = _elapsed;
    final h = d.inHours;
    final m = d.inMinutes % 60;
    final s = d.inSeconds % 60;
    if (h > 0) return '${h}h ${m}m ${s}s';
    if (m > 0) return '${m}m ${s}s';
    return '${s}s';
  }

  /// Called when user presses "Exit parcare". Ends session → barrier opens → PaymentScreen.
  Future<void> _exitParking() async {
    if (_navigatedToPayment || _userEmail == null) return;
    setState(() => _exitLoading = true);
    final result = await ApiService.exitSession(_userEmail!);
    if (!mounted) return;
    _navigatedToPayment = true;
    _sessionPollTimer?.cancel();
    _uiRefreshTimer?.cancel();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => PaymentScreen(
          spotName: widget.spotName,
          sessionId: widget.sessionId,
          durationMinutes: (result?['durationMinutes'] as num?)?.toInt() ?? 0,
          costPerHour: (result?['costPerHour'] as num?)?.toDouble() ?? 5.0,
          totalCost: (result?['totalCost'] as num?)?.toDouble() ?? 0.0,
        ),
      ),
    );
  }

  Widget _buildArrivedWidget() {
    final startLocal = DateTime.tryParse(widget.sessionStartTime)?.toLocal();
    final startLabel = startLocal != null
        ? '${startLocal.hour.toString().padLeft(2, '0')}:${startLocal.minute.toString().padLeft(2, '0')}'
        : '?';

    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
        child: Column(
          children: [
            Container(
              width: 140,
              height: 140,
              decoration: BoxDecoration(
                color: Colors.green.shade700,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.green.withValues(alpha: 0.45),
                    blurRadius: 30,
                    spreadRadius: 8,
                  ),
                ],
              ),
              child: const Icon(Icons.local_parking, size: 80, color: Colors.white),
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
              decoration: BoxDecoration(
                color: Colors.green.shade700,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                'Parcat — Locul ${widget.spotName}',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ),
            const SizedBox(height: 28),
            // Live timer — always computed from actual session start
            Text(
              _parkingDurationString,
              style: TextStyle(
                fontSize: 52,
                fontWeight: FontWeight.bold,
                color: Colors.green.shade400,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'de la $startLabel',
              style: TextStyle(fontSize: 13, color: Colors.grey.shade500),
            ),
            const SizedBox(height: 40),
            // Exit button — camera sees car → press this → barrier opens + payment
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _exitLoading ? null : _exitParking,
                icon: _exitLoading
                    ? const SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2.5,
                        ),
                      )
                    : const Icon(Icons.exit_to_app, size: 26),
                label: Text(
                  _exitLoading ? 'Se procesează...' : 'Exit parcare',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red.shade600,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 18),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Camera va detecta mașina la barieră.\nApasă Exit → plată automată → bariera se deschide.',
              style: TextStyle(
                color: Colors.grey.shade500,
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: Colors.grey.shade900,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.grey.shade700),
              ),
              child: Row(
                children: [
                  Icon(Icons.sensors, color: Colors.grey.shade600, size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Cameră monitorizare spot — prezența mașinii confirmată vizual',
                      style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
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

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Scaffold(
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
          body: _arrived
              ? _buildArrivedWidget()
              : _loading
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

            // Mark arrival at spot → switches to parked state
            ElevatedButton.icon(
              onPressed: _arriveAtSpot,
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
    ),
    _buildSpeedAlertOverlay(),
  ],
);
  }

  Widget _buildSpeedAlertOverlay() {
    return AnimatedOpacity(
      opacity: _speedAlertVisible ? 1.0 : 0.0,
      duration: const Duration(milliseconds: 250),
      child: IgnorePointer(
        ignoring: !_speedAlertVisible,
        child: Container(
          color: Colors.black.withValues(alpha: 0.75),
          child: Center(
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 32),
              padding: const EdgeInsets.all(28),
              decoration: BoxDecoration(
                color: const Color(0xFF1e1e2e),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.red.shade400, width: 2),
                boxShadow: [BoxShadow(color: Colors.red.withValues(alpha: 0.3), blurRadius: 30, spreadRadius: 4)],
              ),
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                const Text('🚨', style: TextStyle(fontSize: 52)),
                const SizedBox(height: 8),
                const Text('VITEZĂ DEPĂȘITĂ!',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Colors.redAccent, letterSpacing: 1.5)),
                const SizedBox(height: 12),
                Text('${_speedAlertValue.toStringAsFixed(1)} km/h',
                  style: const TextStyle(fontSize: 52, fontWeight: FontWeight.w900, color: Colors.orange, fontFeatures: [])),
                const SizedBox(height: 4),
                Text('Limita: ${_speedLimitKmh.toInt()} km/h',
                  style: const TextStyle(fontSize: 14, color: Colors.white60)),
                const SizedBox(height: 8),
                const Text('Reduceți viteza în parcare!',
                  style: TextStyle(fontSize: 13, color: Colors.white54)),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _dismissSpeedAlert,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red.shade600,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: const Text('Am înțeles', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  ),
                ),
              ]),
            ),
          ),
        ),
      ),
    );
  }
}
