import 'dart:async';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  static const _storage = FlutterSecureStorage();
  static const _ipKey = 'esp_cam_ip';

  final _ipController = TextEditingController();
  String? _connectedIp;
  Uint8List? _frameBytes;
  bool _connecting = false;
  String? _errorMsg;
  Timer? _pollTimer;
  int _fps = 0;
  int _frameCount = 0;
  DateTime _fpsTs = DateTime.now();

  @override
  void initState() {
    super.initState();
    _loadSavedIp();
  }

  Future<void> _loadSavedIp() async {
    final saved = await _storage.read(key: _ipKey);
    if (saved != null) {
      _ipController.text = saved;
    }
  }

  void _connect(String ip) {
    final trimmed = ip.trim();
    if (trimmed.isEmpty) return;
    _disconnect();
    setState(() {
      _connectedIp = trimmed;
      _connecting = true;
      _errorMsg = null;
      _frameBytes = null;
    });
    _storage.write(key: _ipKey, value: trimmed);
    // Primul frame imediat, apoi polling la 400ms
    _fetchFrame(trimmed);
    _pollTimer = Timer.periodic(const Duration(milliseconds: 400), (_) {
      _fetchFrame(trimmed);
    });
  }

  Future<void> _fetchFrame(String ip) async {
    try {
      final url = Uri.parse('http://$ip/capture');
      final response = await http.get(url).timeout(const Duration(seconds: 3));
      if (!mounted) return;
      if (response.statusCode == 200) {
        final now = DateTime.now();
        _frameCount++;
        if (now.difference(_fpsTs).inSeconds >= 1) {
          _fps = _frameCount;
          _frameCount = 0;
          _fpsTs = now;
        }
        setState(() {
          _frameBytes = response.bodyBytes;
          _connecting = false;
          _errorMsg = null;
        });
      } else {
        setState(() => _errorMsg = 'HTTP ${response.statusCode}');
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMsg = 'Eroare conexiune';
        _connecting = false;
      });
    }
  }

  void _disconnect() {
    _pollTimer?.cancel();
    _pollTimer = null;
    setState(() {
      _connectedIp = null;
      _frameBytes = null;
      _errorMsg = null;
      _connecting = false;
      _fps = 0;
    });
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _ipController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Camera parcare'),
        backgroundColor: Colors.orange.shade700,
        foregroundColor: Colors.white,
        actions: [
          if (_connectedIp != null)
            IconButton(
              icon: const Icon(Icons.link_off),
              tooltip: 'Deconectare',
              onPressed: _disconnect,
            ),
          if (_connectedIp != null)
            IconButton(
              icon: const Icon(Icons.refresh),
              tooltip: 'Reconectare',
              onPressed: () => _connect(_ipController.text),
            ),
        ],
      ),
      body: Column(
        children: [
          Container(
            color: Colors.grey.shade100,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _ipController,
                    keyboardType: TextInputType.url,
                    decoration: InputDecoration(
                      hintText: 'IP ESP-CAM  (ex: 192.168.1.189)',
                      prefixText: 'http://',
                      prefixStyle: TextStyle(color: Colors.grey.shade500),
                      suffixText: '/capture',
                      suffixStyle: TextStyle(color: Colors.grey.shade500),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      isDense: true,
                      contentPadding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 10),
                    ),
                    onSubmitted: _connect,
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: () => _connect(_ipController.text),
                  icon: const Icon(Icons.videocam, size: 18),
                  label: const Text('Connect'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange.shade700,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8)),
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: _connectedIp == null
                ? _buildPlaceholder()
                : Stack(
                    fit: StackFit.expand,
                    children: [
                      Container(color: Colors.black),
                      if (_frameBytes != null)
                        Image.memory(
                          _frameBytes!,
                          fit: BoxFit.contain,
                          gaplessPlayback: true,
                        ),
                      if (_connecting)
                        const Center(
                          child: CircularProgressIndicator(color: Colors.white),
                        ),
                      if (_errorMsg != null)
                        Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.error_outline,
                                  color: Colors.red, size: 48),
                              const SizedBox(height: 8),
                              Text(_errorMsg!,
                                  style: const TextStyle(
                                      color: Colors.white, fontSize: 14)),
                              const SizedBox(height: 8),
                              TextButton(
                                onPressed: () => _connect(_connectedIp!),
                                child: const Text('Retry',
                                    style: TextStyle(color: Colors.orange)),
                              ),
                            ],
                          ),
                        ),
                      // LIVE badge + FPS
                      Positioned(
                        top: 12,
                        left: 12,
                        child: Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: _errorMsg != null
                                    ? Colors.grey
                                    : Colors.red,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.circle,
                                      color: Colors.white, size: 8),
                                  const SizedBox(width: 4),
                                  Text(
                                      _errorMsg != null ? 'OFFLINE' : 'LIVE',
                                      style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 11,
                                          fontWeight: FontWeight.bold)),
                                ],
                              ),
                            ),
                            if (_fps > 0) ...[
                              const SizedBox(width: 6),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 6, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.black54,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text('$_fps fps',
                                    style: const TextStyle(
                                        color: Colors.white, fontSize: 11)),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlaceholder() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.videocam_off_outlined,
              size: 72, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text('Nicio camera conectata',
              style: TextStyle(fontSize: 18, color: Colors.grey.shade600)),
          const SizedBox(height: 8),
          Text('Introdu IP-ul ESP-CAM si apasa Connect',
              style: TextStyle(fontSize: 13, color: Colors.grey.shade400)),
        ],
      ),
    );
  }
}
