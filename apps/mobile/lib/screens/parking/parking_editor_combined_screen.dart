import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import '../../services/api_service.dart';

class ParkingEditorCombinedScreen extends StatefulWidget {
  const ParkingEditorCombinedScreen({super.key});

  @override
  State<ParkingEditorCombinedScreen> createState() =>
      _ParkingEditorCombinedScreenState();
}

class _ParkingEditorCombinedScreenState
    extends State<ParkingEditorCombinedScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // ─── Spots tab state ────────────────────────────────────────────────────────
  List<Map<String, dynamic>> _spots = [];
  bool _spotsLoading = true;
  bool _spotsSaving = false;
  final TextEditingController _newSpotController = TextEditingController();

  // ─── Config tab state ───────────────────────────────────────────────────────
  bool _configLoading = true;
  bool _configSaving = false;
  LatLng _entrancePos = const LatLng(44.4268, 26.1025);
  LatLng _exitPos     = const LatLng(44.4269, 26.1026);
  LatLng _shopPos     = const LatLng(44.4270, 26.1027);
  String _selectedMarker = 'entrance';
  final TextEditingController _costController       = TextEditingController();
  final TextEditingController _speedLimitController = TextEditingController();
  final Set<Marker> _markers = {};

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadSpots();
    _loadConfig();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _newSpotController.dispose();
    _costController.dispose();
    _speedLimitController.dispose();
    super.dispose();
  }

  // ─── Spots logic ────────────────────────────────────────────────────────────
  Future<void> _loadSpots() async {
    setState(() => _spotsLoading = true);
    final spots = await ApiService.getSpots();
    if (mounted) {
      setState(() {
        _spots = List<Map<String, dynamic>>.from(spots);
        _spotsLoading = false;
      });
    }
  }

  Future<void> _addSpot() async {
    final name = _newSpotController.text.trim().toUpperCase();
    if (name.isEmpty) { _showSnack('Introdu un nume (ex: A1, B5)', Colors.red); return; }
    if (_spots.any((s) => s['name'] == name)) { _showSnack('Spotul $name există deja!', Colors.red); return; }
    setState(() => _spotsSaving = true);
    final result = await ApiService.createSpot(name);
    if (result != null && result['success'] == true) {
      _newSpotController.clear();
      await _loadSpots();
      _showSnack('✅ Spot $name adăugat!', Colors.green);
    } else {
      _showSnack(result?['message'] ?? 'Eroare la adăugare', Colors.red);
    }
    setState(() => _spotsSaving = false);
  }

  Future<void> _deleteSpot(String spotId, String spotName) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Șterge Spot'),
        content: Text('Ștergi spotul $spotName?'),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Anulează')),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
            child: const Text('Șterge'),
          ),
        ],
      ),
    );
    if (confirm != true) return;
    setState(() => _spotsSaving = true);
    final err = await ApiService.deleteSpot(spotId);
    if (err == null) {
      await _loadSpots();
      _showSnack('🗑️ Spot $spotName șters!', Colors.orange);
    } else {
      _showSnack(err, Colors.red);
    }
    setState(() => _spotsSaving = false);
  }

  // ─── Config logic ───────────────────────────────────────────────────────────
  Future<void> _loadConfig() async {
    setState(() => _configLoading = true);
    final config = await ApiService.getParkingConfig();
    if (config != null && mounted) {
      setState(() {
        _entrancePos = LatLng(config['entranceLat'] as double, config['entranceLng'] as double);
        _exitPos     = LatLng(config['exitLat']     as double, config['exitLng']     as double);
        _shopPos     = LatLng(config['shopLat']     as double, config['shopLng']     as double);
        _costController.text       = (config['parkingCostPerHour'] ?? 5.0).toString();
        _speedLimitController.text = (config['speedLimit'] ?? 10).toString();
        _configLoading = false;
      });
    } else {
      setState(() => _configLoading = false);
    }
    _updateMarkers();
  }

  void _updateMarkers() {
    setState(() {
      _markers.clear();
      _markers.add(Marker(
        markerId: const MarkerId('entrance'),
        position: _entrancePos,
        icon: BitmapDescriptor.defaultMarkerWithHue(
          _selectedMarker == 'entrance' ? BitmapDescriptor.hueGreen : BitmapDescriptor.hueBlue),
        infoWindow: const InfoWindow(title: '🚪 Intrare'),
        onTap: () => setState(() => _selectedMarker = 'entrance'),
      ));
      _markers.add(Marker(
        markerId: const MarkerId('exit'),
        position: _exitPos,
        icon: BitmapDescriptor.defaultMarkerWithHue(
          _selectedMarker == 'exit' ? BitmapDescriptor.hueGreen : BitmapDescriptor.hueOrange),
        infoWindow: const InfoWindow(title: '🚗 Ieșire'),
        onTap: () => setState(() => _selectedMarker = 'exit'),
      ));
      _markers.add(Marker(
        markerId: const MarkerId('shop'),
        position: _shopPos,
        icon: BitmapDescriptor.defaultMarkerWithHue(
          _selectedMarker == 'shop' ? BitmapDescriptor.hueGreen : BitmapDescriptor.hueMagenta),
        infoWindow: const InfoWindow(title: '🏪 Magazin'),
        onTap: () => setState(() => _selectedMarker = 'shop'),
      ));
    });
  }

  void _onMapTap(LatLng pos) {
    setState(() {
      if (_selectedMarker == 'entrance') _entrancePos = pos;
      else if (_selectedMarker == 'exit') _exitPos = pos;
      else _shopPos = pos;
    });
    _updateMarkers();
  }

  Future<void> _saveConfig() async {
    setState(() => _configSaving = true);
    final err = await ApiService.updateParkingConfig(
      entranceLat: _entrancePos.latitude, entranceLng: _entrancePos.longitude,
      exitLat:     _exitPos.latitude,     exitLng:     _exitPos.longitude,
      shopLat:     _shopPos.latitude,     shopLng:     _shopPos.longitude,
      parkingCostPerHour: double.tryParse(_costController.text),
      speedLimit:         int.tryParse(_speedLimitController.text),
    );
    if (mounted) {
      setState(() => _configSaving = false);
      _showSnack(err == null ? '✅ Configurare salvată!' : '❌ $err',
          err == null ? Colors.green : Colors.red);
    }
  }

  // ─── Helpers ────────────────────────────────────────────────────────────────
  void _showSnack(String msg, Color color) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: color),
    );
  }

  Color _spotColor(String status) {
    if (status == 'occupied') return Colors.red.shade400;
    if (status == 'available') return Colors.green.shade400;
    return Colors.grey.shade400;
  }

  IconData _spotIcon(String status) {
    if (status == 'occupied') return Icons.local_parking;
    if (status == 'available') return Icons.check_circle;
    return Icons.block;
  }

  // ─── Build ──────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      appBar: AppBar(
        title: const Text('Editor Parcare', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.orange.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () { _loadSpots(); _loadConfig(); },
            tooltip: 'Reîncarcă',
          ),
          if (_tabController.index == 1)
            IconButton(
              icon: _configSaving
                  ? const SizedBox(width: 20, height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.save),
              onPressed: _configSaving ? null : _saveConfig,
              tooltip: 'Salvează configurarea',
            ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          onTap: (_) => setState(() {}),
          tabs: const [
            Tab(icon: Icon(Icons.grid_on), text: 'Locuri'),
            Tab(icon: Icon(Icons.map_outlined), text: 'Configurare'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildSpotsTab(),
          _buildConfigTab(),
        ],
      ),
    );
  }

  // ─── Spots tab ──────────────────────────────────────────────────────────────
  Widget _buildSpotsTab() {
    if (_spotsLoading) return const Center(child: CircularProgressIndicator());
    return Column(
      children: [
        // Stats header
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.orange.shade700, Colors.orange.shade500],
              begin: Alignment.topLeft, end: Alignment.bottomRight,
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _statCard('Total', _spots.length.toString(), Icons.grid_on),
              _statCard('Libere', _spots.where((s) => s['status'] == 'available').length.toString(), Icons.check_circle),
              _statCard('Ocupate', _spots.where((s) => s['status'] == 'occupied').length.toString(), Icons.local_parking),
            ],
          ),
        ),
        // Add spot
        Container(
          margin: const EdgeInsets.all(12),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 8)],
          ),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _newSpotController,
                  decoration: InputDecoration(
                    hintText: 'Nume spot (ex: A1, B5)',
                    prefixIcon: const Icon(Icons.add_location_alt),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    filled: true, fillColor: Colors.grey.shade50,
                    isDense: true,
                  ),
                  textCapitalization: TextCapitalization.characters,
                  onSubmitted: (_) => _addSpot(),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton.icon(
                onPressed: _spotsSaving ? null : _addSpot,
                icon: _spotsSaving
                    ? const SizedBox(width: 16, height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.add),
                label: const Text('Adaugă'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange.shade700,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ],
          ),
        ),
        // Grid
        Expanded(
          child: _spots.isEmpty
              ? Center(
                  child: Column(mainAxisSize: MainAxisSize.min, children: [
                    Icon(Icons.local_parking_outlined, size: 64, color: Colors.grey.shade400),
                    const SizedBox(height: 12),
                    Text('Nu există spoturi', style: TextStyle(fontSize: 18, color: Colors.grey.shade600)),
                  ]),
                )
              : GridView.builder(
                  padding: const EdgeInsets.all(12),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 3, childAspectRatio: 1.2,
                    crossAxisSpacing: 10, mainAxisSpacing: 10,
                  ),
                  itemCount: _spots.length,
                  itemBuilder: (ctx, i) {
                    final spot   = _spots[i];
                    final name   = spot['name']   ?? 'N/A';
                    final status = spot['status'] ?? 'available';
                    final id     = spot['id'];
                    return Card(
                      elevation: 3,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                      child: InkWell(
                        onLongPress: () => _deleteSpot(id, name),
                        borderRadius: BorderRadius.circular(14),
                        child: Container(
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [_spotColor(status), _spotColor(status).withValues(alpha: 0.7)],
                              begin: Alignment.topLeft, end: Alignment.bottomRight,
                            ),
                            borderRadius: BorderRadius.circular(14),
                          ),
                          child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                            Icon(_spotIcon(status), color: Colors.white, size: 28),
                            const SizedBox(height: 6),
                            Text(name, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                            Text(status == 'occupied' ? 'Ocupat' : 'Liber',
                                style: TextStyle(color: Colors.white.withValues(alpha: 0.9), fontSize: 11)),
                          ]),
                        ),
                      ),
                    );
                  },
                ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          color: Colors.orange.shade50,
          child: Row(children: [
            Icon(Icons.info_outline, color: Colors.orange.shade700, size: 18),
            const SizedBox(width: 8),
            Text('Ține apăsat pe un spot pentru a-l șterge',
                style: TextStyle(color: Colors.orange.shade700, fontSize: 12)),
          ]),
        ),
      ],
    );
  }

  // ─── Config tab ─────────────────────────────────────────────────────────────
  Widget _buildConfigTab() {
    if (_configLoading) return const Center(child: CircularProgressIndicator());
    return Column(
      children: [
        // Marker selector
        Container(
          padding: const EdgeInsets.all(12),
          color: Colors.orange.shade50,
          child: Column(children: [
            Text('Apasă pe hartă pentru a muta marker-ul selectat',
                style: TextStyle(fontSize: 13, color: Colors.orange.shade900)),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _markerBtn('🚪 Intrare', 'entrance', Colors.blue),
                _markerBtn('🚗 Ieșire',  'exit',     Colors.deepOrange),
                _markerBtn('🏪 Magazin', 'shop',     Colors.purple),
              ],
            ),
          ]),
        ),
        // Map
        Expanded(
          child: GoogleMap(
            initialCameraPosition: CameraPosition(target: _entrancePos, zoom: 17),
            markers: _markers,
            onTap: _onMapTap,
            myLocationButtonEnabled: true,
            myLocationEnabled: true,
            mapType: MapType.hybrid,
          ),
        ),
        // Settings panel
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.white,
            boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.1), blurRadius: 10, offset: const Offset(0, -2))],
          ),
          child: Column(children: [
            Row(children: [
              Expanded(
                child: TextField(
                  controller: _costController,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(
                    labelText: 'Cost/oră (RON)',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.attach_money),
                    isDense: true,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  controller: _speedLimitController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Limită viteză (km/h)',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.speed),
                    isDense: true,
                  ),
                ),
              ),
            ]),
            const SizedBox(height: 10),
            _infoRow('🚪 Intrare',  _entrancePos, Colors.blue),
            const SizedBox(height: 4),
            _infoRow('🚗 Ieșire',   _exitPos,     Colors.deepOrange),
            const SizedBox(height: 4),
            _infoRow('🏪 Magazin',  _shopPos,     Colors.purple),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _configSaving ? null : _saveConfig,
                icon: _configSaving
                    ? const SizedBox(width: 18, height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.save),
                label: const Text('Salvează configurarea'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange.shade700,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
          ]),
        ),
      ],
    );
  }

  Widget _statCard(String label, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(12)),
      child: Column(children: [
        Icon(icon, color: Colors.white, size: 24),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
        Text(label, style: TextStyle(color: Colors.white.withValues(alpha: 0.9), fontSize: 11)),
      ]),
    );
  }

  Widget _markerBtn(String label, String value, Color color) {
    final sel = _selectedMarker == value;
    return ElevatedButton(
      onPressed: () { setState(() => _selectedMarker = value); _updateMarkers(); },
      style: ElevatedButton.styleFrom(
        backgroundColor: sel ? color : Colors.grey.shade200,
        foregroundColor: sel ? Colors.white : Colors.black87,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      ),
      child: Text(label, style: TextStyle(fontWeight: sel ? FontWeight.bold : FontWeight.normal, fontSize: 12)),
    );
  }

  Widget _infoRow(String label, LatLng pos, Color color) {
    return Row(children: [
      Container(width: 10, height: 10, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
      const SizedBox(width: 8),
      Expanded(child: Text(label, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13))),
      Text('${pos.latitude.toStringAsFixed(5)}, ${pos.longitude.toStringAsFixed(5)}',
          style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
    ]);
  }
}
