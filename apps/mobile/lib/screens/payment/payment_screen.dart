import 'package:flutter/material.dart';
import 'dart:async';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../home/user_home_screen.dart';

class PaymentScreen extends StatefulWidget {
  final String spotName;
  final String sessionId;
  final int durationMinutes;
  final double costPerHour;
  final double totalCost;

  const PaymentScreen({
    super.key,
    required this.spotName,
    required this.sessionId,
    required this.durationMinutes,
    required this.costPerHour,
    required this.totalCost,
  });

  @override
  State<PaymentScreen> createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  String _selectedMethod = 'card';
  bool _paying = false;

  // Saved payment method (from profile)
  String? _savedMethodType;
  String? _savedMethodDisplay;
  int _autoPayCountdown = 3;
  Timer? _autoPayTimer;

  @override
  void initState() {
    super.initState();
    _loadSavedMethod();
  }

  @override
  void dispose() {
    _autoPayTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadSavedMethod() async {
    const storage = FlutterSecureStorage();
    final type    = await storage.read(key: 'payment_method_type');
    final display = await storage.read(key: 'payment_display');
    if (!mounted) return;
    if (type != null) {
      setState(() {
        _savedMethodType    = type;
        _savedMethodDisplay = display;
        _selectedMethod     = type;
        _autoPayCountdown   = 3;
      });
      _startAutoPayCountdown();
    }
  }

  void _startAutoPayCountdown() {
    _autoPayTimer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) { t.cancel(); return; }
      if (_autoPayCountdown <= 1) {
        t.cancel();
        _processPayment();
      } else {
        setState(() => _autoPayCountdown--);
      }
    });
  }

  void _cancelAutoPay() {
    _autoPayTimer?.cancel();
    setState(() {
      _savedMethodType = null;
      _savedMethodDisplay = null;
    });
  }

  String get _durationString {
    final h = widget.durationMinutes ~/ 60;
    final m = widget.durationMinutes % 60;
    if (h > 0) return '$h h $m min';
    return '$m min';
  }

  Future<void> _processPayment() async {
    setState(() => _paying = true);
    await Future.delayed(const Duration(seconds: 2));
    if (!mounted) return;
    setState(() => _paying = false);
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 16),
            Icon(Icons.check_circle, color: Colors.green.shade600, size: 80),
            const SizedBox(height: 16),
            const Text(
              'Plată efectuată!',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              '${widget.totalCost.toStringAsFixed(2)} RON',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Colors.green.shade700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Mulțumim! La revedere.',
              style: TextStyle(color: Colors.grey.shade600),
            ),
            const SizedBox(height: 24),
          ],
        ),
        actions: [
          Center(
            child: ElevatedButton.icon(
              onPressed: () {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const UserHomeScreen()),
                  (_) => false,
                );
              },
              icon: const Icon(Icons.home),
              label: const Text('Înapoi acasă'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green.shade700,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 14),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text('Finalizare parcare'),
        backgroundColor: Colors.green.shade700,
        foregroundColor: Colors.white,
        automaticallyImplyLeading: false,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 16),
              // Session summary card
              Card(
                elevation: 4,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(20)),
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.local_parking,
                              color: Colors.green.shade700, size: 32),
                          const SizedBox(width: 12),
                          Text(
                            'Locul ${widget.spotName}',
                            style: TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              color: Colors.green.shade700,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 24),
                      const Divider(),
                      const SizedBox(height: 16),
                      _infoRow(Icons.access_time, 'Durată', _durationString),
                      const SizedBox(height: 12),
                      _infoRow(Icons.attach_money, 'Tarif',
                          '${widget.costPerHour.toStringAsFixed(2)} RON/h'),
                      const SizedBox(height: 16),
                      const Divider(),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'TOTAL',
                            style: TextStyle(
                                fontSize: 20, fontWeight: FontWeight.bold),
                          ),
                          Text(
                            '${widget.totalCost.toStringAsFixed(2)} RON',
                            style: TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              color: Colors.green.shade700,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),
              // Auto-pay UI when saved method is present
              if (_savedMethodType != null) ...[
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.green.shade400, width: 2),
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Icon(Icons.check_circle,
                              color: Colors.green.shade700, size: 28),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Plată automată',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.green.shade800,
                                  ),
                                ),
                                Text(
                                  _savedMethodDisplay ?? _savedMethodType!,
                                  style: TextStyle(
                                    fontSize: 13,
                                    color: Colors.green.shade700,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            width: 52,
                            height: 52,
                            decoration: BoxDecoration(
                              color: Colors.green.shade700,
                              shape: BoxShape.circle,
                            ),
                            child: Center(
                              child: Text(
                                '$_autoPayCountdown',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 22,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Plata va fi procesată automat în $_autoPayCountdown secunde...',
                        style: TextStyle(
                            fontSize: 13, color: Colors.green.shade700),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 12),
                      TextButton(
                        onPressed: _cancelAutoPay,
                        child: Text(
                          'Anulează plata automată',
                          style: TextStyle(color: Colors.red.shade600),
                        ),
                      ),
                    ],
                  ),
                ),
              ] else ...[
                const Text(
                  'Metodă de plată',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 8),
                Text(
                  'Salvează o metodă în profil pentru plată automată la viitoarele ieșiri.',
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                ),
                const SizedBox(height: 12),
                _paymentMethodTile(
                    'card', Icons.credit_card, 'Card bancar', 'Visa / Mastercard'),
                const SizedBox(height: 8),
                _paymentMethodTile(
                    'cash', Icons.money, 'Numerar', 'Plată la casier'),
                const SizedBox(height: 8),
                _paymentMethodTile('phone', Icons.phone_android,
                    'Apple Pay / Google Pay', 'Plată mobilă'),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: _paying ? null : _processPayment,
                  icon: _paying
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2),
                        )
                      : const Icon(Icons.payment),
                  label: Text(
                    _paying
                        ? 'Se procesează...'
                        : 'Plătește ${widget.totalCost.toStringAsFixed(2)} RON',
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green.shade700,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 18),
                    textStyle: const TextStyle(
                        fontSize: 18, fontWeight: FontWeight.bold),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16)),
                  ),
                ),
              ],
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _infoRow(IconData icon, String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(children: [
          Icon(icon, color: Colors.grey.shade600, size: 20),
          const SizedBox(width: 8),
          Text(label,
              style: TextStyle(color: Colors.grey.shade600, fontSize: 16)),
        ]),
        Text(value,
            style:
                const TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
      ],
    );
  }

  Widget _paymentMethodTile(
      String value, IconData icon, String title, String subtitle) {
    final selected = _selectedMethod == value;
    return GestureDetector(
      onTap: () => setState(() => _selectedMethod = value),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: selected ? Colors.green.shade50 : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color:
                selected ? Colors.green.shade600 : Colors.grey.shade300,
            width: selected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Icon(icon,
                color: selected
                    ? Colors.green.shade700
                    : Colors.grey.shade600,
                size: 28),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        color: selected
                            ? Colors.green.shade900
                            : Colors.black87,
                      )),
                  Text(subtitle,
                      style: TextStyle(
                          color: Colors.grey.shade600, fontSize: 12)),
                ],
              ),
            ),
            if (selected)
              Icon(Icons.check_circle, color: Colors.green.shade600),
          ],
        ),
      ),
    );
  }
}
