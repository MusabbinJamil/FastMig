import 'package:flutter/material.dart';

class SideMenu extends StatelessWidget {
  final int selectedIndex;
  final Function(int) onItemSelected;

  const SideMenu({
    Key? key,
    required this.selectedIndex,
    required this.onItemSelected,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 250,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Colors.blue.shade800,
            Colors.blue.shade900,
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(2, 0),
          ),
        ],
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.symmetric(vertical: 30, horizontal: 20),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.2),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(
                    Icons.flash_on,
                    color: Colors.white,
                    size: 30,
                  ),
                ),
                const SizedBox(width: 12),
                const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'FastMig',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'Data Migration',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          // Menu Items
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 10),
              children: [
                _buildMenuItem(
                  icon: Icons.folder_open,
                  title: 'Load Data',
                  index: 0,
                  isSelected: selectedIndex == 0,
                ),
                _buildMenuItem(
                  icon: Icons.transform,
                  title: 'Convert Fields',
                  index: 1,
                  isSelected: selectedIndex == 1,
                ),
                _buildMenuItem(
                  icon: Icons.video_camera_back,
                  title: 'Record Steps',
                  index: 2,
                  isSelected: selectedIndex == 2,
                ),
                _buildMenuItem(
                  icon: Icons.table_chart,
                  title: 'View Data',
                  index: 3,
                  isSelected: selectedIndex == 3,
                ),
                _buildMenuItem(
                  icon: Icons.download,
                  title: 'Export Data',
                  index: 4,
                  isSelected: selectedIndex == 4,
                ),
                const Divider(color: Colors.white24, height: 30),
                _buildSectionHeader('ETL Operations'),
                _buildMenuItem(
                  icon: Icons.build,
                  title: 'ETL Transform',
                  index: 9,
                  isSelected: selectedIndex == 9,
                ),
                _buildMenuItem(
                  icon: Icons.code,
                  title: 'Encoding',
                  index: 10,
                  isSelected: selectedIndex == 10,
                ),
                const Divider(color: Colors.white24, height: 30),
                _buildSectionHeader('AI Features'),
                _buildMenuItem(
                  icon: Icons.health_and_safety,
                  title: 'Data Fitness',
                  index: 5,
                  isSelected: selectedIndex == 5,
                ),
                _buildMenuItem(
                  icon: Icons.auto_fix_high,
                  title: 'AI Cleaning',
                  index: 6,
                  isSelected: selectedIndex == 6,
                ),
                const Divider(color: Colors.white24, height: 30),
                _buildMenuItem(
                  icon: Icons.settings,
                  title: 'Settings',
                  index: 7,
                  isSelected: selectedIndex == 7,
                ),
                _buildMenuItem(
                  icon: Icons.help_outline,
                  title: 'Help',
                  index: 8,
                  isSelected: selectedIndex == 8,
                ),
              ],
            ),
          ),
          // Footer
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.2),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.check_circle,
                  color: Colors.green.shade300,
                  size: 16,
                ),
                const SizedBox(width: 8),
                const Text(
                  'Backend Connected',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem({
    required IconData icon,
    required String title,
    required int index,
    required bool isSelected,
  }) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      margin: const EdgeInsets.only(bottom: 5),
      decoration: BoxDecoration(
        color: isSelected ? Colors.white.withOpacity(0.2) : Colors.transparent,
        borderRadius: BorderRadius.circular(10),
        border: isSelected
            ? Border.all(color: Colors.white.withOpacity(0.3), width: 1)
            : null,
      ),
      child: ListTile(
        leading: Icon(
          icon,
          color: isSelected ? Colors.white : Colors.white70,
          size: 24,
        ),
        title: Text(
          title,
          style: TextStyle(
            color: isSelected ? Colors.white : Colors.white70,
            fontSize: 15,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
        onTap: () => onItemSelected(index),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Text(
        title,
        style: const TextStyle(
          color: Colors.white54,
          fontSize: 12,
          fontWeight: FontWeight.w600,
          letterSpacing: 1.2,
        ),
      ),
    );
  }
}
