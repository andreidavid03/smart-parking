import 'dart:async';
import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class AdminAlertsScreen extends StatefulWidget {
  const AdminAlertsScreen({super.key});

  @override
  State<AdminAlertsScreen> createState() => _AdminAlertsScreenState();
}

class _AdminAlertsScreenState extends State<AdminAlertsScreen> {
  List<Map<String, dynamic>> _alerts = [];
  int _unread = 0;
  bool _loading = true;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _loadAndMarkRead();
    _timer = Timer.periodic(const Duration(seconds: 5), (_) => _load());
  }

  Future<void> _loadAndMarkRead() async {
    await _load();
    ApiService.markAlertsRead();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    final data = await ApiService.getAlerts();
    if (data != null && mounted) {
      setState(() {
        _alerts = List<Map<String, dynamic>>.from(data['alerts'] ?? []);
        _unread = (data['unread'] as num?)?.toInt() ?? 0;
        _loading = false;
      });
    } else if (mounted) {
      setState(() => _loading = false);
    }
  }

  Future<void> _addMockAlerts() async {
    setState(() => _loading = true);
    await ApiService.addMockAlerts();
    await _load();
  }

  Future<void> _markRead() async {
    await ApiService.markAlertsRead();
    setState(() => _unread = 0);
  }

  Color _typeColor(String type) {
    switch (type) {
      case 'speed':       return Colors.orange.shade600;
      case 'temperature': return Colors.red.shade400;
      case 'flame':       return Colors.deepOrange.shade600;
      case 'gas':         return Colors.purple.shade400;
      default:            return Colors.grey;
    }
  }

  IconData _typeIcon(String type) {
    switch (type) {
      case 'speed':       return Icons.speed;
      case 'temperature': return Icons.thermostat;
      case 'flame':       return Icons.local_fire_department;
      case 'gas':         return Icons.air;
      default:            return Icons.warning;
    }
  }

  Color _severityColor(String severity) =>
      severity == 'critical' ? Colors.red.shade600 : Colors.orange.shade500;

  String _formatTime(String iso) {
    try {
      final dt = DateTime.parse(iso).toLocal();
      final now = DateTime.now();
      final diff = now.difference(dt);
      if (diff.inSeconds < 60) return '${diff.inSeconds}s în urmă';
      if (diff.inMinutes < 60) return '${diff.inMinutes}m în urmă';
      if (diff.inHours < 24)   return '${diff.inHours}h în urmă';
      return '${dt.day.toString().padLeft(2,'0')}.${dt.month.toString().padLeft(2,'0')} ${dt.hour.toString().padLeft(2,'0')}:${dt.minute.toString().padLeft(2,'0')}';
    } catch (_) {
      return iso;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      appBar: AppBar(
        title: Row(children: [
          const Text('Alerte', style: TextStyle(fontWeight: FontWeight.bold)),
          if (_unread > 0) ...[
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(color: Colors.red, borderRadius: BorderRadius.circular(12)),
              child: Text('$_unread nou', style: const TextStyle(fontSize: 11, color: Colors.white, fontWeight: FontWeight.bold)),
            ),
          ],
        ]),
        backgroundColor: Colors.red.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (_unread > 0)
            IconButton(
              icon: const Icon(Icons.done_all),
              tooltip: 'Marchează toate ca citite',
              onPressed: _markRead,
            ),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _load),
        ],
      ),
      body: Column(
        children: [
          // Stats bar
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.red.shade700, Colors.red.shade500],
                begin: Alignment.topLeft, end: Alignment.bottomRight,
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _statItem(Icons.warning_amber, 'Total', _alerts.length.toString(), Colors.white),
                _statItem(Icons.fiber_new, 'Necitite', _unread.toString(), Colors.yellow.shade200),
                _statItem(Icons.dangerous, 'Critice',
                    _alerts.where((a) => a['severity'] == 'critical').length.toString(),
                    Colors.orange.shade200),
              ],
            ),
          ),

          // Mock button bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            color: Colors.grey.shade200,
            child: Row(children: [
              Icon(Icons.science_outlined, size: 16, color: Colors.grey.shade600),
              const SizedBox(width: 6),
              Text('Demo prezentare:', style: TextStyle(fontSize: 12, color: Colors.grey.shade700, fontWeight: FontWeight.w600)),
              const SizedBox(width: 8),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _loading ? null : _addMockAlerts,
                  icon: const Icon(Icons.add_alert, size: 16),
                  label: const Text('Adaugă alerte mock', style: TextStyle(fontSize: 12)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red.shade700,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    elevation: 1,
                  ),
                ),
              ),
            ]),
          ),

          // List
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _alerts.isEmpty
                    ? Center(
                        child: Column(mainAxisSize: MainAxisSize.min, children: [
                          Icon(Icons.check_circle_outline, size: 72, color: Colors.green.shade300),
                          const SizedBox(height: 16),
                          Text('Nicio alertă activă', style: TextStyle(fontSize: 18, color: Colors.grey.shade600, fontWeight: FontWeight.w500)),
                          const SizedBox(height: 8),
                          Text('Sistemul funcționează normal', style: TextStyle(fontSize: 13, color: Colors.grey.shade400)),
                        ]),
                      )
                    : RefreshIndicator(
                        onRefresh: _load,
                        child: ListView.builder(
                          padding: const EdgeInsets.all(12),
                          itemCount: _alerts.length,
                          itemBuilder: (ctx, i) => _buildAlertCard(_alerts[i]),
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertCard(Map<String, dynamic> alert) {
    final type     = alert['type']     as String? ?? 'speed';
    final severity = alert['severity'] as String? ?? 'warning';
    final title    = alert['title']    as String? ?? '';
    final detail   = alert['detail']   as String? ?? '';
    final ts       = alert['timestamp'] as String? ?? '';
    final read     = alert['read']     as bool?   ?? true;
    final color    = _typeColor(type);
    final sevColor = _severityColor(severity);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: read ? Colors.grey.shade200 : sevColor.withValues(alpha: 0.5),
          width: read ? 1 : 2,
        ),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 8, offset: const Offset(0, 2))],
      ),
      child: Row(
        children: [
          // Color bar left
          Container(
            width: 6,
            height: 80,
            decoration: BoxDecoration(
              color: color,
              borderRadius: const BorderRadius.only(topLeft: Radius.circular(14), bottomLeft: Radius.circular(14)),
            ),
          ),
          const SizedBox(width: 12),
          // Icon
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.12),
              shape: BoxShape.circle,
            ),
            child: Icon(_typeIcon(type), color: color, size: 22),
          ),
          const SizedBox(width: 12),
          // Text
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(children: [
                    Expanded(
                      child: Text(title,
                        style: TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 14,
                          color: read ? Colors.black87 : Colors.black,
                        ),
                        maxLines: 1, overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                      decoration: BoxDecoration(
                        color: sevColor.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: sevColor.withValues(alpha: 0.4)),
                      ),
                      child: Text(
                        severity == 'critical' ? 'CRITIC' : 'AVERTISMENT',
                        style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: sevColor),
                      ),
                    ),
                  ]),
                  const SizedBox(height: 4),
                  Text(detail, style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                  const SizedBox(height: 4),
                  Text(_formatTime(ts), style: TextStyle(fontSize: 11, color: Colors.grey.shade400)),
                ],
              ),
            ),
          ),
          // Unread dot
          if (!read)
            Padding(
              padding: const EdgeInsets.only(right: 14),
              child: Container(
                width: 10, height: 10,
                decoration: BoxDecoration(color: sevColor, shape: BoxShape.circle),
              ),
            )
          else
            const SizedBox(width: 14),
        ],
      ),
    );
  }

  Widget _statItem(IconData icon, String label, String value, Color color) {
    return Column(children: [
      Icon(icon, color: color, size: 20),
      const SizedBox(height: 3),
      Text(value, style: TextStyle(color: color, fontSize: 20, fontWeight: FontWeight.bold)),
      Text(label, style: TextStyle(color: color.withValues(alpha: 0.85), fontSize: 10)),
    ]);
  }
}
