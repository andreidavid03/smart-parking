import 'package:flutter/material.dart';
import '../services/api_service.dart';

class CarColorSelectionScreen extends StatefulWidget {
  final String email;
  final String? currentColor;

  const CarColorSelectionScreen({
    super.key,
    required this.email,
    this.currentColor,
  });

  @override
  State<CarColorSelectionScreen> createState() => _CarColorSelectionScreenState();
}

class _CarColorSelectionScreenState extends State<CarColorSelectionScreen> {
  String? _selectedColor;
  bool _loading = false;

  final List<Map<String, dynamic>> _colors = [
    {'name': 'Red', 'value': 'red', 'color': Colors.red},
    {'name': 'Blue', 'value': 'blue', 'color': Colors.blue},
    {'name': 'Green', 'value': 'green', 'color': Colors.green},
    {'name': 'Black', 'value': 'black', 'color': Colors.black},
    {'name': 'White', 'value': 'white', 'color': Colors.white},
    {'name': 'Silver', 'value': 'silver', 'color': Colors.grey},
    {'name': 'Yellow', 'value': 'yellow', 'color': Colors.yellow},
    {'name': 'Orange', 'value': 'orange', 'color': Colors.orange},
    {'name': 'Purple', 'value': 'purple', 'color': Colors.purple},
    {'name': 'Brown', 'value': 'brown', 'color': Colors.brown},
  ];

  @override
  void initState() {
    super.initState();
    _selectedColor = widget.currentColor;
  }

  Future<void> _saveColor() async {
    if (_selectedColor == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a color')),
      );
      return;
    }

    setState(() {
      _loading = true;
    });

    final error = await ApiService.updateCarColor(widget.email, _selectedColor!);

    if (!mounted) return;

    setState(() {
      _loading = false;
    });

    if (error == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Car color saved successfully'),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.pop(context, _selectedColor);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(error),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Select Car Color'),
        backgroundColor: Colors.orange.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Column(
        children: [
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  mainAxisSpacing: 16,
                  crossAxisSpacing: 16,
                  childAspectRatio: 1.5,
                ),
                itemCount: _colors.length,
                itemBuilder: (context, index) {
                  final colorData = _colors[index];
                  final isSelected = _selectedColor == colorData['value'];

                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        _selectedColor = colorData['value'] as String;
                      });
                    },
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: isSelected
                              ? Colors.orange.shade700
                              : Colors.grey.shade300,
                          width: isSelected ? 3 : 1,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.05),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            width: 60,
                            height: 60,
                            decoration: BoxDecoration(
                              color: colorData['color'] as Color,
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: colorData['value'] == 'white'
                                    ? Colors.grey.shade300
                                    : Colors.transparent,
                                width: 2,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: (colorData['color'] as Color)
                                      .withValues(alpha: 0.3),
                                  blurRadius: 8,
                                  offset: const Offset(0, 2),
                                ),
                              ],
                            ),
                            child: isSelected
                                ? const Icon(
                                    Icons.check,
                                    color: Colors.white,
                                    size: 30,
                                  )
                                : null,
                          ),
                          const SizedBox(height: 12),
                          Text(
                            colorData['name'] as String,
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: isSelected
                                  ? FontWeight.bold
                                  : FontWeight.w500,
                              color: isSelected
                                  ? Colors.orange.shade700
                                  : Colors.grey.shade800,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -4),
                ),
              ],
            ),
            child: SafeArea(
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _loading ? null : _saveColor,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: Colors.orange.shade600,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 2,
                  ),
                  child: _loading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor:
                                AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Text(
                          'Save Color',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
