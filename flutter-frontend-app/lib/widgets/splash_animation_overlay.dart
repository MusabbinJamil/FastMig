import 'package:flutter/material.dart';
import 'dart:async';

/// Splash animation overlay - shows the app intro animation
class SplashAnimationOverlay extends StatefulWidget {
  final VoidCallback onClose;

  const SplashAnimationOverlay({Key? key, required this.onClose}) : super(key: key);

  @override
  State<SplashAnimationOverlay> createState() => _SplashAnimationOverlayState();
}

class _SplashAnimationOverlayState extends State<SplashAnimationOverlay>
    with TickerProviderStateMixin {
  late AnimationController _controller;
  late AnimationController _pulseController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _pulseAnimation;
  late Animation<double> _rotateAnimation;

  bool _showParticles = false;
  final List<_Particle> _particles = [];

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      duration: const Duration(milliseconds: 2500),
      vsync: this,
    );

    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.4, curve: Curves.easeIn),
      ),
    );

    _scaleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.5, curve: Curves.elasticOut),
      ),
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.5),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.3, 0.7, curve: Curves.easeOutCubic),
      ),
    );

    _rotateAnimation = Tween<double>(begin: -0.1, end: 0.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.5, curve: Curves.easeOut),
      ),
    );

    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.1).animate(
      CurvedAnimation(
        parent: _pulseController,
        curve: Curves.easeInOut,
      ),
    );

    _controller.forward();
    _pulseController.repeat(reverse: true);

    // Show particles after a delay
    Timer(const Duration(milliseconds: 800), () {
      if (mounted) {
        setState(() => _showParticles = true);
        _generateParticles();
      }
    });

    // Auto-close after animation
    Timer(const Duration(milliseconds: 4000), () {
      if (mounted) {
        _closeWithAnimation();
      }
    });
  }

  void _generateParticles() {
    final size = MediaQuery.of(context).size;
    for (int i = 0; i < 30; i++) {
      _particles.add(_Particle(
        x: size.width / 2,
        y: size.height / 2 - 50,
        targetX: (i % 2 == 0 ? 1 : -1) * (50 + (i * 15.0)),
        targetY: -100 - (i * 10.0),
        delay: i * 50,
        color: _particleColors[i % _particleColors.length],
      ));
    }
  }

  final List<Color> _particleColors = [
    Colors.blue.shade300,
    Colors.purple.shade300,
    Colors.cyan.shade300,
    Colors.white,
    Colors.amber.shade300,
  ];

  void _closeWithAnimation() async {
    await _controller.reverse();
    widget.onClose();
  }

  @override
  void dispose() {
    _controller.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: GestureDetector(
        onTap: _closeWithAnimation,
        child: AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            return Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Colors.blue.shade700.withOpacity(_fadeAnimation.value),
                    Colors.blue.shade900.withOpacity(_fadeAnimation.value),
                    Colors.purple.shade900.withOpacity(_fadeAnimation.value),
                  ],
                ),
              ),
              child: Stack(
                children: [
                  // Animated background circles
                  ..._buildBackgroundCircles(),

                  // Particles
                  if (_showParticles) ..._buildParticles(),

                  // Main content
                  Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // Logo Animation
                        FadeTransition(
                          opacity: _fadeAnimation,
                          child: ScaleTransition(
                            scale: _scaleAnimation,
                            child: AnimatedBuilder(
                              animation: _pulseController,
                              builder: (context, child) {
                                return Transform.scale(
                                  scale: _pulseAnimation.value,
                                  child: Transform.rotate(
                                    angle: _rotateAnimation.value,
                                    child: Container(
                                      padding: const EdgeInsets.all(35),
                                      decoration: BoxDecoration(
                                        color: Colors.white.withOpacity(0.15),
                                        shape: BoxShape.circle,
                                        boxShadow: [
                                          BoxShadow(
                                            color: Colors.white.withOpacity(0.3),
                                            blurRadius: 40,
                                            spreadRadius: 10,
                                          ),
                                          BoxShadow(
                                            color: Colors.blue.withOpacity(0.5),
                                            blurRadius: 60,
                                            spreadRadius: 20,
                                          ),
                                        ],
                                      ),
                                      child: const Icon(
                                        Icons.flash_on,
                                        size: 100,
                                        color: Colors.white,
                                      ),
                                    ),
                                  ),
                                );
                              },
                            ),
                          ),
                        ),
                        const SizedBox(height: 40),
                        // Title Animation
                        SlideTransition(
                          position: _slideAnimation,
                          child: FadeTransition(
                            opacity: _fadeAnimation,
                            child: Column(
                              children: [
                                ShaderMask(
                                  shaderCallback: (bounds) => LinearGradient(
                                    colors: [
                                      Colors.white,
                                      Colors.blue.shade200,
                                      Colors.white,
                                    ],
                                  ).createShader(bounds),
                                  child: const Text(
                                    'FastMig',
                                    style: TextStyle(
                                      fontSize: 56,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                      letterSpacing: 4,
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  'Lightning Fast Data Migration',
                                  style: TextStyle(
                                    fontSize: 18,
                                    color: Colors.white.withOpacity(0.9),
                                    letterSpacing: 2,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  'GA  |  PSO  |  DE  |  ES',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.white.withOpacity(0.7),
                                    letterSpacing: 3,
                                    fontWeight: FontWeight.w300,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                        const SizedBox(height: 60),
                        // Loading bar
                        FadeTransition(
                          opacity: _fadeAnimation,
                          child: SizedBox(
                            width: 250,
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(10),
                              child: LinearProgressIndicator(
                                backgroundColor: Colors.white.withOpacity(0.2),
                                valueColor: const AlwaysStoppedAnimation<Color>(
                                    Colors.white),
                                minHeight: 6,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Tap to close hint
                  Positioned(
                    bottom: 40,
                    left: 0,
                    right: 0,
                    child: FadeTransition(
                      opacity: _fadeAnimation,
                      child: const Center(
                        child: Text(
                          'Tap anywhere to close',
                          style: TextStyle(
                            color: Colors.white54,
                            fontSize: 14,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  List<Widget> _buildBackgroundCircles() {
    return [
      Positioned(
        top: -100,
        left: -100,
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: Container(
            width: 300,
            height: 300,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  Colors.blue.withOpacity(0.3),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),
      ),
      Positioned(
        bottom: -150,
        right: -150,
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: Container(
            width: 400,
            height: 400,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  Colors.purple.withOpacity(0.3),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),
      ),
    ];
  }

  List<Widget> _buildParticles() {
    return _particles.map((p) {
      return TweenAnimationBuilder<double>(
        tween: Tween(begin: 0.0, end: 1.0),
        duration: Duration(milliseconds: 1500 + p.delay),
        curve: Curves.easeOutCubic,
        builder: (context, value, child) {
          return Positioned(
            left: p.x + (p.targetX * value) - 4,
            top: p.y + (p.targetY * value) - 4,
            child: Opacity(
              opacity: (1 - value * 0.7).clamp(0.0, 1.0),
              child: Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: p.color,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: p.color.withOpacity(0.5),
                      blurRadius: 10,
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      );
    }).toList();
  }
}

class _Particle {
  final double x;
  final double y;
  final double targetX;
  final double targetY;
  final int delay;
  final Color color;

  _Particle({
    required this.x,
    required this.y,
    required this.targetX,
    required this.targetY,
    required this.delay,
    required this.color,
  });
}
