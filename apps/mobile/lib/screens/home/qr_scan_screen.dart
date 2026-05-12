import 'dart:async';
import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../services/api_service.dart';
import '../navigation/directional_navigation_screen.dart';

class QRScanScreen extends StatefulWidget {
  final VoidCallback? onSessionDetected;
  const QRScanScreen({super.key, this.onSessionDetected});

  @override
  State<QRScanScreen> createState() => _QRScanScreenState();
}

class _QRScanScreenState extends State<QRScanScreen> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  bool _loading = true;
  String? _qrCode;
  Map<String, dynamic>? _session;
  Timer? _pollTimer;

  // Spot statuses fetched from backend: spotName → 'available'|'occupied'
  Map<String, String> _spotStatuses = {};
  // The spot this user has reserved (from this session in the app)
  String? _reservedSpot;
  bool _spotsLoading = false;

  static const List<String> _rowA = ['A1', 'A2', 'A3', 'A4', 'A5'];
  static const List<String> _rowB = ['B1', 'B2', 'B3', 'B4', 'B5'];

  @override
  void initState() {
    super.initState();
    _loadAll();
    _pollTimer = Timer.periodic(const Duration(seconds: 4), (_) {
      if (_session == null && !_loading) {
        _pollSession();
        _loadSpots();
      }
    });
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadAll() async {
    await Future.wait([_loadQRCodeAndSession(), _loadSpots()]);
  }

  Future<void> _loadSpots() async {
    if (_spotsLoading) return;
    setState(() => _spotsLoading = true);
    final spots = await ApiService.getSpots();
    if (mounted) {
      final map = <String, String>{};
      for (final s in spots) {
        final name = s['name'] as String?;
        final status = s['status'] as String?;
        if (name != null && status != null) map[name] = status;
      }
      setState(() {
        _spotStatuses = map;
        _spotsLoading = false;
      });
    }
  }

  Future<void> _pollSession() async {
    final email = await _storage.read(key: 'user_email');
    if (email == null || !mounted) return;
    final sessionResult = await ApiService.getCurrentSession(email);
    final newSession = sessionResult?['session'];
    if (newSession != null && mounted) {
      setState(() => _session = newSession);
      _pollTimer?.cancel();
      final spotName = newSession['spot']?['name'] ?? '?';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.local_parking, color: Colors.white),
              const SizedBox(width: 8),
              Text('Parcat! Locul tău: $spotName'),
            ],
          ),
          backgroundColor: Colors.green.shade700,
          duration: const Duration(seconds: 5),
        ),
      );
      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => DirectionalNavigationScreen(
              spotName: newSession['spot']?['name'] as String? ?? '?',
              spotLat: (newSession['spot']?['spotLat'] as num?)?.toDouble(),
              spotLng: (newSession['spot']?['spotLng'] as num?)?.toDouble(),
              sessionId: newSession['id'] as String? ?? '',
              sessionStartTime: newSession['startTime'] as String? ?? '',
            ),
          ),
        );
      }
    }
  }

  Future<void> _loadQRCodeAndSession() async {
    setState(() => _loading = true);
    final email = await _storage.read(key: 'user_email');
    if (email != null) {
      final qrResult = await ApiService.generateQRCode(email);
      final sessionResult = await ApiService.getCurrentSession(email);
      if (mounted) {
        setState(() {
          _qrCode = qrResult?['qrCode'];
          _session = sessionResult?['session'];
          _loading = false;
        });
        if (_session == null) {
          _pollTimer?.cancel();
          _pollTimer = Timer.periodic(const Duration(seconds: 4), (_) {
            if (_session == null && !_loading) {
              _pollSession();
              _loadSpots();
            }
          });
        }
      }
    } else {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _onSpotTapped(String spotName) async {
    final status = _spotStatuses[spotName] ?? 'available';
    if (status == 'occupied') return; // can't reserve occupied

    if (_reservedSpot == spotName) {
      // Cancel reservation
      final result = await ApiService.cancelReservation(spotName);
      if (mounted) {
        setState(() => _reservedSpot = null);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(result['ok'] == true
              ? 'Rezervare anulată pentru $spotName'
              : result['message'] ?? 'Eroare'),
          backgroundColor:
              result['ok'] == true ? Colors.orange : Colors.red,
        ));
      }
      return;
    }

    // Cancel previous reservation if any
    if (_reservedSpot != null) {
      await ApiService.cancelReservation(_reservedSpot!);
    }

    // Reserve new spot
    final result = await ApiService.reserveSpot(spotName);
    if (mounted) {
      if (result['ok'] == true) {
        setState(() => _reservedSpot = spotName);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Loc $spotName rezervat! LED-ul devine albastru.'),
          backgroundColor: Colors.blue.shade700,
        ));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(result['message'] ?? 'Nu s-a putut rezerva'),
          backgroundColor: Colors.red,
        ));
        await _loadSpots(); // refresh — spot may have changed
      }
    }
  }

  Color _spotColor(String spotName) {
    if (_reservedSpot == spotName) return Colors.blue.shade600;
    final s = _spotStatuses[spotName] ?? 'available';
    if (s == 'occupied') return Colors.red.shade600;
    return Colors.green.shade600;
  }

  Widget _buildParkingMap() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Hartă parcare',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
              if (_spotsLoading)
                const SizedBox(
                    width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
              else
                GestureDetector(
                  onTap: _loadSpots,
                  child: Icon(Icons.refresh, size: 18, color: Colors.grey[600]),
                ),
            ],
          ),
          const SizedBox(height: 12),
          // Row labels + spots
          _buildRow('Rând A', _rowA),
          const SizedBox(height: 8),
          // Road divider
          Container(
            height: 24,
            decoration: BoxDecoration(
              color: Colors.grey.shade400,
              borderRadius: BorderRadius.circular(4),
            ),
            child: const Center(
              child: Text('DRUM', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(height: 8),
          _buildRow('Rând B', _rowB),
          const SizedBox(height: 12),
          // Legend
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _legendItem(Colors.green.shade600, 'Liber'),
              const SizedBox(width: 16),
              _legendItem(Colors.blue.shade600, 'Rezervat'),
              const SizedBox(width: 16),
              _legendItem(Colors.red.shade600, 'Ocupat'),
            ],
          ),
          if (_reservedSpot != null) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Loc rezervat: $_reservedSpot',
                      style: TextStyle(color: Colors.blue.shade800, fontWeight: FontWeight.bold)),
                  TextButton(
                    onPressed: () => _onSpotTapped(_reservedSpot!),
                    style: TextButton.styleFrom(
                        foregroundColor: Colors.red, padding: EdgeInsets.zero, minimumSize: const Size(60, 30)),
                    child: const Text('Anulează'),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildRow(String label, List<String> spots) {
    return Row(
      children: [
        SizedBox(
          width: 52,
          child: Text(label,
              style: TextStyle(fontSize: 11, color: Colors.grey[600], fontWeight: FontWeight.w500)),
        ),
        ...spots.map((name) {
          final color = _spotColor(name);
          final isOccupied = (_spotStatuses[name] ?? 'available') == 'occupied';
          return Expanded(
            child: GestureDetector(
              onTap: () => _onSpotTapped(name),
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 3),
                height: 44,
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(8),
                  border: _reservedSpot == name
                      ? Border.all(color: Colors.white, width: 2)
                      : null,
                  boxShadow: [BoxShadow(color: color.withValues(alpha: 0.4), blurRadius: 4, offset: const Offset(0, 2))],
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(name,
                        style: const TextStyle(
                            color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                    if (isOccupied)
                      const Icon(Icons.directions_car, color: Colors.white, size: 12)
                    else if (_reservedSpot == name)
                      const Icon(Icons.bookmark, color: Colors.white, size: 12)
                    else
                      const Icon(Icons.check, color: Colors.white, size: 12),
                  ],
                ),
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _legendItem(Color color, String label) {
    return Row(
      children: [
        Container(width: 12, height: 12, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(3))),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 11)),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final hasSession = _session != null;

    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('QR & Rezervare'),
        backgroundColor: hasSession ? Colors.green.shade700 : Colors.blue.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAll,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _qrCode == null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.qr_code, size: 64, color: Colors.grey[400]),
                      const SizedBox(height: 16),
                      Text('Nu s-a putut genera codul QR',
                          style: TextStyle(fontSize: 18, color: Colors.grey[600])),
                      const SizedBox(height: 24),
                      ElevatedButton.icon(
                        onPressed: _loadAll,
                        icon: const Icon(Icons.refresh),
                        label: const Text('Încearcă din nou'),
                      ),
                    ],
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      // Status badge
                      Container(
                        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 20),
                        decoration: BoxDecoration(
                          color: hasSession ? Colors.green.shade50 : Colors.blue.shade50,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: hasSession ? Colors.green.shade200 : Colors.blue.shade200,
                            width: 2,
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              hasSession ? Icons.local_parking : Icons.qr_code_2,
                              color: hasSession ? Colors.green.shade700 : Colors.blue.shade700,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              hasSession ? 'Parcat' : 'Gata de parcare',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: hasSession ? Colors.green.shade900 : Colors.blue.shade900,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                      // QR code
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(20),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.08),
                              blurRadius: 20,
                              offset: const Offset(0, 8),
                            ),
                          ],
                        ),
                        child: QrImageView(
                          data: _qrCode!,
                          version: QrVersions.auto,
                          size: 220,
                          backgroundColor: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Prezintă codul QR la barieră',
                        style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 28),
                      // Active session card
                      if (hasSession) ...[
                        Container(
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [Colors.green.shade700, Colors.green.shade500],
                            ),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Column(
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  const Icon(Icons.location_on, color: Colors.white, size: 28),
                                  const SizedBox(width: 8),
                                  Text(
                                    'Locul tău: ${_session!['spot']['name']}',
                                    style: const TextStyle(
                                        fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Parcat de la: ${_formatTime(_session!['startTime'])}',
                                style: const TextStyle(fontSize: 14, color: Colors.white70),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 12),
                        ElevatedButton.icon(
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => DirectionalNavigationScreen(
                                  spotName: _session!['spot']['name'] as String? ?? '?',
                                  spotLat: (_session!['spot']['spotLat'] as num?)?.toDouble(),
                                  spotLng: (_session!['spot']['spotLng'] as num?)?.toDouble(),
                                  sessionId: _session!['id'] as String? ?? '',
                                  sessionStartTime: _session!['startTime'] as String? ?? '',
                                ),
                              ),
                            );
                          },
                          icon: const Icon(Icons.navigation),
                          label: const Text('Navighează la loc'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.white,
                            foregroundColor: Colors.green.shade700,
                            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Scanează din nou la ieșire pentru a termina sesiunea',
                          style: TextStyle(fontSize: 13, color: Colors.grey[600], fontStyle: FontStyle.italic),
                          textAlign: TextAlign.center,
                        ),
                      ] else ...[
                        // Parking lot map — only shown when no active session
                        _buildParkingMap(),
                        const SizedBox(height: 12),
                        Text(
                          'Apasă pe un loc liber pentru a-l rezerva.\nLED-ul devine albastru pe machetă.',
                          style: TextStyle(fontSize: 13, color: Colors.grey[600]),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ],
                  ),
                ),
    );
  }

  String _formatTime(String timestamp) {
    try {
      final DateTime dt = DateTime.parse(timestamp);
      return '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return timestamp;
    }
  }
}
