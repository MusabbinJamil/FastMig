import 'package:flutter/material.dart';
import 'dart:math';

/// DVD-style bouncing logo animation with fireworks on corner hits
class DvdLogoAnimation extends StatefulWidget {
  final VoidCallback onClose;

  const DvdLogoAnimation({Key? key, required this.onClose}) : super(key: key);

  @override
  State<DvdLogoAnimation> createState() => _DvdLogoAnimationState();
}

class _DvdLogoAnimationState extends State<DvdLogoAnimation>
    with TickerProviderStateMixin {
  late AnimationController _moveController;

  // Logo position and velocity
  double _x = 100;
  double _y = 100;
  double _vx = 3.0;
  double _vy = 2.5;

  // Logo size
  final double _logoWidth = 120;
  final double _logoHeight = 60;

  // Color cycling for DVD effect
  final List<Color> _colors = [
    Colors.blue,
    Colors.purple,
    Colors.pink,
    Colors.red,
    Colors.orange,
    Colors.yellow,
    Colors.green,
    Colors.teal,
    Colors.cyan,
  ];
  int _colorIndex = 0;

  // Fireworks
  final List<Firework> _fireworks = [];
  final Random _random = Random();

  // Corner hit tracking
  int _cornerHits = 0;

  @override
  void initState() {
    super.initState();

    // Initialize position randomly
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final size = MediaQuery.of(context).size;
      setState(() {
        _x = _random.nextDouble() * (size.width - _logoWidth - 100) + 50;
        _y = _random.nextDouble() * (size.height - _logoHeight - 100) + 50;
      });
    });

    _moveController = AnimationController(
      duration: const Duration(milliseconds: 16), // ~60fps
      vsync: this,
    )..addListener(_updatePosition);

    _moveController.repeat();
  }

  void _updatePosition() {
    if (!mounted) return;

    final size = MediaQuery.of(context).size;
    final maxX = size.width - _logoWidth - 20;
    final maxY = size.height - _logoHeight - 20;

    setState(() {
      // Update position
      _x += _vx;
      _y += _vy;

      bool hitLeft = false;
      bool hitRight = false;
      bool hitTop = false;
      bool hitBottom = false;

      // Bounce off walls
      if (_x <= 20) {
        _x = 20;
        _vx = _vx.abs();
        _changeColor();
        hitLeft = true;
      } else if (_x >= maxX) {
        _x = maxX;
        _vx = -_vx.abs();
        _changeColor();
        hitRight = true;
      }

      if (_y <= 20) {
        _y = 20;
        _vy = _vy.abs();
        _changeColor();
        hitTop = true;
      } else if (_y >= maxY) {
        _y = maxY;
        _vy = -_vy.abs();
        _changeColor();
        hitBottom = true;
      }

      // Check for corner hit
      if ((hitLeft || hitRight) && (hitTop || hitBottom)) {
        _cornerHits++;
        _triggerFireworks(_x + _logoWidth / 2, _y + _logoHeight / 2);
      }

      // Update fireworks
      _updateFireworks();
    });
  }

  void _changeColor() {
    _colorIndex = (_colorIndex + 1) % _colors.length;
  }

  void _triggerFireworks(double x, double y) {
    // Create multiple firework bursts
    for (int burst = 0; burst < 3; burst++) {
      Future.delayed(Duration(milliseconds: burst * 150), () {
        if (!mounted) return;
        setState(() {
          // Add particles for this burst
          for (int i = 0; i < 50; i++) {
            final angle = (i / 50) * 2 * pi + _random.nextDouble() * 0.5;
            final speed = 3.0 + _random.nextDouble() * 5.0;
            final color = _fireworkColors[_random.nextInt(_fireworkColors.length)];

            _fireworks.add(Firework(
              x: x + (_random.nextDouble() - 0.5) * 20,
              y: y + (_random.nextDouble() - 0.5) * 20,
              vx: cos(angle) * speed,
              vy: sin(angle) * speed,
              color: color,
              life: 1.0,
              size: 2.0 + _random.nextDouble() * 4.0,
            ));
          }
        });
      });
    }
  }

  final List<Color> _fireworkColors = [
    Colors.red,
    Colors.orange,
    Colors.yellow,
    Colors.green,
    Colors.blue,
    Colors.purple,
    Colors.pink,
    Colors.white,
    Colors.cyan,
    Colors.amber,
  ];

  void _updateFireworks() {
    for (int i = _fireworks.length - 1; i >= 0; i--) {
      final f = _fireworks[i];
      f.x += f.vx;
      f.y += f.vy;
      f.vy += 0.1; // gravity
      f.life -= 0.02;
      f.vx *= 0.98; // drag
      f.vy *= 0.98;

      if (f.life <= 0) {
        _fireworks.removeAt(i);
      }
    }
  }

  @override
  void dispose() {
    _moveController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.black.withOpacity(0.9),
      child: GestureDetector(
        onTap: widget.onClose,
        child: Stack(
          children: [
            // Instructions
            Positioned(
              top: 20,
              left: 0,
              right: 0,
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.black54,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    'Tap anywhere to close  |  Corner Hits: $_cornerHits',
                    style: const TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                ),
              ),
            ),

            // Fireworks
            ..._fireworks.map((f) => Positioned(
              left: f.x,
              top: f.y,
              child: Opacity(
                opacity: f.life.clamp(0.0, 1.0),
                child: Container(
                  width: f.size,
                  height: f.size,
                  decoration: BoxDecoration(
                    color: f.color,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: f.color.withOpacity(0.8),
                        blurRadius: f.size * 2,
                        spreadRadius: f.size / 2,
                      ),
                    ],
                  ),
                ),
              ),
            )),

            // DVD Logo
            Positioned(
              left: _x,
              top: _y,
              child: Container(
                width: _logoWidth,
                height: _logoHeight,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      _colors[_colorIndex],
                      _colors[(_colorIndex + 1) % _colors.length],
                    ],
                  ),
                  borderRadius: BorderRadius.circular(8),
                  boxShadow: [
                    BoxShadow(
                      color: _colors[_colorIndex].withOpacity(0.6),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.flash_on, color: Colors.white, size: 28),
                    SizedBox(width: 4),
                    Text(
                      'FastMig',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Corner hit celebration text
            if (_cornerHits > 0)
              Positioned(
                bottom: 40,
                left: 0,
                right: 0,
                child: Center(
                  child: AnimatedOpacity(
                    opacity: _fireworks.isNotEmpty ? 1.0 : 0.0,
                    duration: const Duration(milliseconds: 300),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [Colors.purple, Colors.pink],
                        ),
                        borderRadius: BorderRadius.circular(30),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.purple.withOpacity(0.5),
                            blurRadius: 20,
                          ),
                        ],
                      ),
                      child: Text(
                        _getCornerMessage(),
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  String _getCornerMessage() {
    if (_cornerHits == 1) return 'CORNER HIT!';
    if (_cornerHits < 5) return 'CORNER HIT x$_cornerHits!';
    if (_cornerHits < 10) return 'AMAZING x$_cornerHits!';
    if (_cornerHits < 20) return 'LEGENDARY x$_cornerHits!';
    return 'GODLIKE x$_cornerHits!';
  }
}

class Firework {
  double x;
  double y;
  double vx;
  double vy;
  Color color;
  double life;
  double size;

  Firework({
    required this.x,
    required this.y,
    required this.vx,
    required this.vy,
    required this.color,
    required this.life,
    required this.size,
  });
}
