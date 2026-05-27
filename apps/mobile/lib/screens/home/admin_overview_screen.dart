import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import '../parking/parking_config_screen.dart';

class AdminOverviewScreen extends StatefulWidget {
  const AdminOverviewScreen({super.key});

  @override
  State<AdminOverviewScreen> createState() => _AdminOverviewScreenState();
}

class _AdminOverviewScreenState extends State<AdminOverviewScreen> {
  bool _loading = true;
  bool _saving = false;
  List<Map<String, dynamic>> _spots = [];
  Map<String, dynamic>? _environment;
  Map<String, dynamic>? _adminStatus;
  bool _flameInvert = false; // inversează logica senzori flacără (fix pin flotant)

  // Config state – stored so lat/lng are preserved when saving cost/speed only
  double _entranceLat = 0;
  double _entranceLng = 0;
  double _exitLat = 0;
  double _exitLng = 0;
  double _shopLat = 0;
  double _shopLng = 0;

  final _costController = TextEditingController();
  final _speedController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _costController.dispose();
    _speedController.dispose();
    super.dispose();
  }Swx

  Future<void> _loadData() async {
    setState(() => _loading = true);

    final results = await Future.wait([
      ApiService.getSpots(),
      ApiService.getParkingConfig(),
      ApiService.getAdminStatus(),
    ]);

    if (!mounted) return;

    final spots = results[0] as List<Map<String, dynamic>>;
    final config = results[1] as Map<String, dynamic>?;
    final adminStatus = results[2] as Map<String, dynamic>?;

    setState(() {
      _spots = spots;
      _adminStatus = adminStatus;
      _environment = adminStatus?['environment'] as Map<String, dynamic>?;
      if (config != null) {
        _entranceLat = (config['entranceLat'] as num?)?.toDouble() ?? 0;
        _entranceLng = (config['entranceLng'] as num?)?.toDouble() ?? 0;
        _exitLat = (config['exitLat'] as num?)?.toDouble() ?? 0;
        _exitLng = (config['exitLng'] as num?)?.toDouble() ?? 0;
        _shopLat = (config['shopLat'] as num?)?.toDouble() ?? 0;
        _shopLng = (config['shopLng'] as num?)?.toDouble() ?? 0;
        _costController.text =
            (config['parkingCostPerHour'] as num?)?.toString() ?? '';
        _speedController.text =
            (config['speedLimit'] as num?)?.toString() ?? '';
      }
      _loading = false;
    });
  }

  Future<void> _saveSettings() async {
    final cost = double.tryParse(_costController.text.trim());
    final speed = int.tryParse(_speedController.text.trim());

    if (cost == null || speed == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter valid cost and speed values')),
      );
      return;
    }

    setState(() => _saving = true);

    final error = await ApiService.updateParkingConfig(
      entranceLat: _entranceLat,
      entranceLng: _entranceLng,
      exitLat: _exitLat,
      exitLng: _exitLng,
      shopLat: _shopLat,
      shopLng: _shopLng,
      parkingCostPerHour: cost,
      speedLimit: speed,
    );

    if (!mounted) return;
    setState(() => _saving = false);

    if (error == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Settings saved'),
          backgroundColor: Colors.green,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $error'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Parking Overview'),
        backgroundColor: Colors.orange.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.map_outlined),
            tooltip: 'Map Layout',
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                  builder: (_) => const ParkingConfigScreen()),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
            onPressed: _loadData,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadData,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  _buildStatsBar(),
                  const SizedBox(height: 24),
                  if (_spots.isEmpty)
                    Center(
                      child: Text(
                        'No parking spots configured',
                        style: TextStyle(color: Colors.grey[600], fontSize: 16),
                      ),
                    )
                  else ...[
                    _buildZoneSection(
                      'Zone A',
                      _spots
                          .where((s) =>
                              (s['name'] as String).startsWith('A'))
                          .toList(),
                    ),
                    const SizedBox(height: 20),
                    _buildZoneSection(
                      'Zone B',
                      _spots
                          .where((s) =>
                              (s['name'] as String).startsWith('B'))
                          .toList(),
                    ),
                  ],
                  const SizedBox(height: 24),
                  _buildSpotSensorsCard(),
                  const SizedBox(height: 24),
                  _buildSensorsCard(),
                  const SizedBox(height: 24),
                  _buildSettingsCard(),
                ],
              ),
            ),
    );
  }

  Widget _buildStatsBar() {
    final total = _spots.length;
    final free = _spots.where((s) => s['status'] == 'available').length;
    final occupied = total - free;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.orange.shade700, Colors.orange.shade500],
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatItem('Total', total.toString(), Icons.local_parking,
              Colors.white),
          _buildStatItem('Free', free.toString(), Icons.check_circle,
              Colors.lightGreenAccent),
          _buildStatItem('Occupied', occupied.toString(), Icons.directions_car,
              Colors.redAccent),
        ],
      ),
    );
  }

  Widget _buildStatItem(
      String label, String value, IconData icon, Color iconColor) {
    return Column(
      children: [
        Icon(icon, color: iconColor, size: 30),
        const SizedBox(height: 6),
        Text(value,
            style: const TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontWeight: FontWeight.bold)),
        Text(label,
            style:
                const TextStyle(color: Colors.white70, fontSize: 12)),
      ],
    );
  }

  Widget _buildZoneSection(
      String zoneName, List<Map<String, dynamic>> zoneSpots) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          zoneName,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 10),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 5,
            mainAxisSpacing: 10,
            crossAxisSpacing: 10,
            childAspectRatio: 1,
          ),
          itemCount: zoneSpots.length,
          itemBuilder: (context, index) {
            final spot = zoneSpots[index];
            final isAvailable = spot['status'] == 'available';
            return Container(
              decoration: BoxDecoration(
                color: isAvailable
                    ? Colors.green.shade100
                    : Colors.red.shade100,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: isAvailable
                      ? Colors.green.shade700
                      : Colors.red.shade700,
                  width: 2,
                ),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    isAvailable
                        ? Icons.check_circle
                        : Icons.directions_car,
                    color: isAvailable
                        ? Colors.green.shade700
                        : Colors.red.shade700,
                    size: 22,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    spot['name'] as String,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: isAvailable
                          ? Colors.green.shade900
                          : Colors.red.shade900,
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

  Widget _buildSettingsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Parking Settings',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              'Tap the map icon above to edit entrance/exit markers',
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _costController,
              keyboardType:
                  const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: 'Cost per hour (RON)',
                prefixIcon: const Icon(Icons.attach_money),
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _speedController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: 'Speed limit (km/h)',
                prefixIcon: const Icon(Icons.speed),
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _saving ? null : _saveSettings,
                icon: _saving
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.save),
                label: Text(_saving ? 'Saving…' : 'Save Settings'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange.shade700,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSpotSensorsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.sensors, color: Colors.deepOrange),
                const SizedBox(width: 8),
                const Text(
                  'Senzori Spot',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.refresh, size: 20),
                  tooltip: 'Reîncarcă',
                  onPressed: _loadData,
                ),
              ],
            ),
            Text(
              'Simulează un eveniment de la senzorul fizic al unui spot',
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
            const SizedBox(height: 16),
            if (_spots.isEmpty)
              Center(
                child: Text(
                  'Niciun spot configurat',
                  style: TextStyle(color: Colors.grey[600], fontSize: 13),
                ),
              )
            else
              Wrap(
                spacing: 10,
                runSpacing: 10,
                children: _spots.map((spot) {
                  final name = spot['name'] as String;
                  final isOccupied = spot['status'] == 'occupied';
                  return Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 8),
                    decoration: BoxDecoration(
                      color: isOccupied
                          ? Colors.red.shade50
                          : Colors.green.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: isOccupied
                            ? Colors.red.shade200
                            : Colors.green.shade200,
                      ),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          name,
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                            color: isOccupied
                                ? Colors.red.shade800
                                : Colors.green.shade800,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            _sensorBtn(name, 'occupied', isOccupied),
                            const SizedBox(width: 6),
                            _sensorBtn(name, 'available', !isOccupied),
                          ],
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  Widget _sensorBtn(String spotName, String status, bool isActive) {
    final isOccupied = status == 'occupied';
    return GestureDetector(
      onTap: isActive
          ? null
          : () async {
              final ok = await ApiService.mockSensor(spotName, status);
              if (!mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(ok
                      ? '$spotName → ${isOccupied ? 'Ocupat' : 'Liber'}'
                      : 'Eroare la trimiterea evenimentului'),
                  backgroundColor: ok
                      ? (isOccupied ? Colors.red.shade600 : Colors.green.shade600)
                      : Colors.grey,
                  duration: const Duration(seconds: 2),
                ),
              );
              if (ok) _loadData();
            },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: isActive
              ? (isOccupied ? Colors.red.shade600 : Colors.green.shade600)
              : Colors.grey.shade200,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          isOccupied ? 'Ocupat' : 'Liber',
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: isActive ? Colors.white : Colors.grey.shade600,
          ),
        ),
      ),
    );
  }

  Widget _buildSensorsCard() {
    final env   = _environment ?? {};
    final diags = (_adminStatus?['diagnostics'] as Map<String, dynamic>?) ?? {};
    final spd   = (_adminStatus?['speed']) as Map<String, dynamic>?;

    // Rezolvă valori cu fallback pe diagnostics
    final temp    = env['temp']     ?? diags['dht_temp']    ?? diags['bmp_temp'];
    final hum     = env['humidity'] ?? diags['dht_humidity'];
    // Filtrează -999 (BMP offline) și valori <= 0
    final pressRaw = (env['pressure'] ?? diags['bmp_pressure']) as num?;
    final pressure = (pressRaw != null && pressRaw > 0) ? pressRaw : null;
    final gas1    = env['gas1']  ?? diags['gas1_raw'];
    final gas2    = env['gas2']  ?? diags['gas2_raw'];
    // Flame cu inversare
    final rawF1   = env['flame1'] ?? diags['flame1_detect'];
    final rawF2   = env['flame2'] ?? diags['flame2_detect'];
    final flame1  = rawF1 == null ? null : (_flameInvert ? !(rawF1 as bool) : rawF1 as bool);
    final flame2  = rawF2 == null ? null : (_flameInvert ? !(rawF2 as bool) : rawF2 as bool);
    final speedKmh = spd?['speed_kmh'] as num?;

    final hasData = temp != null || hum != null || gas1 != null;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.thermostat, color: Colors.blueGrey),
                const SizedBox(width: 8),
                const Expanded(child: Text('Environment & Safety',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold))),
                // Buton invert flacără
                TextButton.icon(
                  onPressed: () => setState(() => _flameInvert = !_flameInvert),
                  icon: Icon(Icons.swap_vert, size: 14,
                      color: _flameInvert ? Colors.orange : Colors.grey),
                  label: Text('Inv.flacără',
                      style: TextStyle(fontSize: 11,
                          color: _flameInvert ? Colors.orange : Colors.grey)),
                  style: TextButton.styleFrom(padding: EdgeInsets.zero,
                      minimumSize: const Size(60, 24)),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (!hasData && spd == null)
              Center(
                child: Text(
                  'No sensor data — ESP32 must be running',
                  style: TextStyle(color: Colors.grey[600], fontSize: 13),
                ),
              )
            else
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  if (temp != null)
                    _buildEnvTile('Temperature', '$temp°C',
                        Icons.device_thermostat, Colors.orange),
                  if (hum != null)
                    _buildEnvTile('Humidity', '$hum%',
                        Icons.water_drop, Colors.blue),
                  if (pressure != null)
                    _buildEnvTile('Pressure', '${pressure.round()} hPa',
                        Icons.compress, Colors.purple),
                  if (gas1 != null)
                    _buildEnvTile(
                      'Gas Left', '$gas1',
                      Icons.air,
                      (gas1 as num) > 700 ? Colors.red : Colors.green,
                      alert: gas1 > 700,
                    ),
                  if (gas2 != null)
                    _buildEnvTile(
                      'Gas Right', '$gas2',
                      Icons.air,
                      (gas2 as num) > 700 ? Colors.red : Colors.green,
                      alert: gas2 > 700,
                    ),
                  if (flame1 != null)
                    _buildEnvTile(
                      'Flame Left',
                      flame1 ? '🔥 DETECTED' : '✔ Clear',
                      Icons.local_fire_department,
                      flame1 ? Colors.red : Colors.green,
                      alert: flame1,
                    ),
                  if (flame2 != null)
                    _buildEnvTile(
                      'Flame Right',
                      flame2 ? '🔥 DETECTED' : '✔ Clear',
                      Icons.local_fire_department,
                      flame2 ? Colors.red : Colors.green,
                      alert: flame2,
                    ),
                  // Viteza — întotdeauna vizibilă
                  _buildEnvTile(
                    'Entry Speed',
                    speedKmh != null ? '$speedKmh km/h' : '—',
                    Icons.speed,
                    speedKmh != null && speedKmh > 10 ? Colors.red : Colors.green,
                    alert: speedKmh != null && speedKmh > 10,
                  ),
                ],
              ),
            if (env['updatedAt'] != null)
              Padding(
                padding: const EdgeInsets.only(top: 10),
                child: Text(
                  'Last update: ${env['updatedAt']}',
                  style: TextStyle(fontSize: 10, color: Colors.grey[500]),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildEnvTile(String label, String value, IconData icon, Color color,
      {bool alert = false}) {
    return Container(
      width: 130,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: alert ? Colors.red.shade50 : Colors.grey.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: alert ? Colors.red.shade300 : Colors.grey.shade200,
          width: alert ? 2 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(height: 6),
          Text(value,
              style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.bold,
                  color: alert ? Colors.red.shade700 : Colors.black87)),
          Text(label,
              style: TextStyle(fontSize: 11, color: Colors.grey[600])),
        ],
      ),
    );
  }
}
