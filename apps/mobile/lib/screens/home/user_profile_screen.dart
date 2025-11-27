import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class UserProfileScreen extends StatefulWidget {
  const UserProfileScreen({super.key});

  @override
  State<UserProfileScreen> createState() => _UserProfileScreenState();
}

class _UserProfileScreenState extends State<UserProfileScreen> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  
  bool _isLoading = true;
  bool _isSaving = false;
  
  String? _email;
  String? _carColor;
  String? _preferredSpot;
  String? _spotPreferenceType; // 'specific', 'entrance', 'exit', 'shop', null
  
  List<Map<String, dynamic>> _spots = [];
  
  @override
  void initState() {
    super.initState();
    _loadProfile();
    _loadSpots();
  }

  Future<void> _loadProfile() async {
    setState(() => _isLoading = true);
    
    final email = await _storage.read(key: 'user_email');
    final profile = await ApiService.getProfile();
    
    if (profile != null && mounted) {
      setState(() {
        _email = email;
        _carColor = profile['carColor'];
        _preferredSpot = profile['preferredSpot'];
        _spotPreferenceType = profile['spotPreferenceType'];
        _isLoading = false;
      });
    } else {
      setState(() {
        _email = email;
        _isLoading = false;
      });
    }
  }

  Future<void> _loadSpots() async {
    final spots = await ApiService.getSpots();
    if (mounted) {
      setState(() {
        _spots = List<Map<String, dynamic>>.from(spots);
      });
    }
  }

  Future<void> _updatePreference(String type, {String? specificSpot}) async {
    setState(() => _isSaving = true);

    final result = await ApiService.updatePreference(
      preferenceType: type,
      specificSpot: specificSpot,
    );

    if (result == null) {
      setState(() {
        _spotPreferenceType = type;
        _preferredSpot = specificSpot;
        _isSaving = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Preferință salvată!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } else {
      setState(() => _isSaving = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _updateCarColor(String color) async {
    final result = await ApiService.updateCarColorSimple(color);
    
    if (result == null) {
      setState(() => _carColor = color);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Culoare mașină salvată!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    }
  }

  Future<void> _logout() async {
    await _storage.deleteAll();
    if (mounted) {
      Navigator.of(context).pushReplacementNamed('/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      appBar: AppBar(
        title: const Text(
          'Profil & Preferințe',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _logout,
            tooltip: 'Deconectare',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadProfile,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: Column(
                  children: [
                    // User info header
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [Colors.blue.shade700, Colors.blue.shade500],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                      ),
                      child: Column(
                        children: [
                          const CircleAvatar(
                            radius: 40,
                            backgroundColor: Colors.white,
                            child: Icon(Icons.person, size: 50, color: Colors.blue),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            _email ?? 'User',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          if (_carColor != null) ...[
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                                vertical: 6,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.white.withValues(alpha: 0.2),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.directions_car, color: Colors.white, size: 16),
                                  const SizedBox(width: 6),
                                  Text(
                                    _carColor!,
                                    style: const TextStyle(color: Colors.white),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),

                    const SizedBox(height: 20),

                    // Car Color Section
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            '🚗 Culoare Mașină',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 12),
                          _buildCarColorPicker(),
                        ],
                      ),
                    ),

                    const SizedBox(height: 24),

                    // Preference Type Selection
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            '📍 Preferință Parcare',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 12),
                          _buildPreferenceCards(),
                        ],
                      ),
                    ),

                    const SizedBox(height: 24),

                    // Specific Spot Selection (doar dacă e 'specific')
                    if (_spotPreferenceType == 'specific') ...[
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              '🅿️ Alege Spot Specific',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 12),
                            _buildSpecificSpotsGrid(),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],

                    // Info card
                    Container(
                      margin: const EdgeInsets.all(16),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade50,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.blue.shade200),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.info_outline, color: Colors.blue.shade700),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'Sistemul va încerca să îți aloce un spot bazat pe preferințele tale.',
                              style: TextStyle(
                                color: Colors.blue.shade700,
                                fontSize: 13,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildCarColorPicker() {
    final colors = [
      {'name': 'Negru', 'color': Colors.black},
      {'name': 'Alb', 'color': Colors.white},
      {'name': 'Gri', 'color': Colors.grey},
      {'name': 'Roșu', 'color': Colors.red},
      {'name': 'Albastru', 'color': Colors.blue},
      {'name': 'Verde', 'color': Colors.green},
    ];

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: colors.map((c) {
        final isSelected = _carColor == c['name'];
        return GestureDetector(
          onTap: () => _updateCarColor(c['name'] as String),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: isSelected ? Colors.blue.shade100 : Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: isSelected ? Colors.blue.shade700 : Colors.grey.shade300,
                width: 2,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    color: c['color'] as Color,
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.grey.shade400),
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  c['name'] as String,
                  style: TextStyle(
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    color: isSelected ? Colors.blue.shade700 : Colors.black87,
                  ),
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildPreferenceCards() {
    final preferences = [
      {
        'type': 'entrance',
        'icon': Icons.input,
        'label': 'Aproape de Intrare',
        'description': 'Spot cât mai aproape de intrarea în parcare',
        'color': Colors.green,
      },
      {
        'type': 'exit',
        'icon': Icons.output,
        'label': 'Aproape de Ieșire',
        'description': 'Spot cât mai aproape de ieșire',
        'color': Colors.orange,
      },
      {
        'type': 'shop',
        'icon': Icons.shopping_bag,
        'label': 'Aproape de Magazine',
        'description': 'Spot cât mai aproape de zona comercială',
        'color': Colors.purple,
      },
      {
        'type': 'specific',
        'icon': Icons.push_pin,
        'label': 'Spot Specific',
        'description': 'Alege întotdeauna același spot',
        'color': Colors.blue,
      },
    ];

    return Column(
      children: preferences.map((pref) {
        final isSelected = _spotPreferenceType == pref['type'];
        return GestureDetector(
          onTap: _isSaving
              ? null
              : () => _updatePreference(pref['type'] as String),
          child: Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isSelected
                  ? (pref['color'] as Color).withValues(alpha: 0.1)
                  : Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isSelected
                    ? (pref['color'] as Color)
                    : Colors.grey.shade300,
                width: isSelected ? 2 : 1,
              ),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: (pref['color'] as Color).withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    pref['icon'] as IconData,
                    color: pref['color'] as Color,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        pref['label'] as String,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                          color: isSelected
                              ? (pref['color'] as Color)
                              : Colors.black87,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        pref['description'] as String,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                ),
                if (isSelected)
                  Icon(
                    Icons.check_circle,
                    color: pref['color'] as Color,
                  ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildSpecificSpotsGrid() {
    if (_spots.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 5,
        childAspectRatio: 1,
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
      ),
      itemCount: _spots.length,
      itemBuilder: (context, index) {
        final spot = _spots[index];
        final spotName = spot['name'] ?? 'N/A';
        final isSelected = _preferredSpot == spotName;
        final isAvailable = spot['status'] == 'available';

        return GestureDetector(
          onTap: _isSaving
              ? null
              : () => _updatePreference('specific', specificSpot: spotName),
          child: Container(
            decoration: BoxDecoration(
              color: isSelected
                  ? Colors.blue.shade700
                  : (isAvailable ? Colors.green.shade50 : Colors.red.shade50),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: isSelected
                    ? Colors.blue.shade900
                    : (isAvailable ? Colors.green.shade300 : Colors.red.shade300),
                width: isSelected ? 2 : 1,
              ),
            ),
            child: Center(
              child: Text(
                spotName,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: isSelected
                      ? Colors.white
                      : (isAvailable ? Colors.green.shade900 : Colors.red.shade900),
                  fontSize: 12,
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
