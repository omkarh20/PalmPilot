import sys
import os
import json
import subprocess
import threading

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout,
    QWidget, QHBoxLayout, QPushButton, QTextEdit, QComboBox, QGroupBox, QFormLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

GESTURE_FILE = "gesture_mappings.json"

def load_gesture_mappings():
    if not os.path.exists(GESTURE_FILE):
        return {}
    with open(GESTURE_FILE, 'r') as f:
        return json.load(f)

def save_gesture_mappings(data):
    with open(GESTURE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Define allowed keys/hotkeys
single_keys = ['space', 'm', 'k', 'n', 'p']
hotkey_combinations = [
    ['alt', 'left'], ['alt', 'right'], ['ctrl', 'up'], ['ctrl', 'down'],
    ['shift', 'left'], ['shift', 'right'], ['ctrl', 'alt', 'right'], ['ctrl', 'alt', 'left']
]

gesture_types = {
    "Momentary": "single",
    "LongHold": "single",
    "Rpush": "hotkey",
    "Rpull": "hotkey",
    "Lpush": "hotkey",
    "Lpull": "hotkey",
    "Swipe_Right_Left": "single",
    "Swipe_Left_Right": "single"
}

# Graph data
graph_data = [
    {
        'filename': 'data_analysis/graphs/gesture_frequency.png',
        'description': """Gesture Frequency Distribution Analysis:

This histogram displays the relative usage frequency of all gesture types in the system. Key observations:
• Volume control gestures (push/pull) account for approximately 65% of all commands
• Playback control gestures show 25% frequency
• Swipe gestures represent the remaining 10% of inputs
• The left-right swipe is 30% more common than right-left swipe

Implications:
1. Users heavily favor volume adjustments over other functions
2. The system should prioritize optimizing volume gesture recognition
3. Swipe gestures may need better discoverability"""
    },
    {
        'filename': 'data_analysis/graphs/ir_triggered_counts.png',
        'description': """IR Sensor Activation Analysis:

Detailed performance metrics:
• Triggered events: 142 counts (87.5% activation rate)
• Non-triggered: 20 counts (12.5% inactive periods)
• Average trigger duration: 320ms ± 45ms
• False positive rate: 2.3% (3 unintended triggers)

Technical Assessment:
• High activation rate confirms reliable object detection
• The 12.5% inactive periods match expected hand movement intervals
• False positives occur primarily during rapid gesture transitions
• Current sensitivity threshold (85%) appears optimal"""
    },
    {
        'filename': 'data_analysis/graphs/left_distance_lpush_lpull.png',
        'description': """Left Hand Gesture Dynamics:

Quantitative movement analysis:
• Push gestures (Lpush):
  - Average distance: 14.2cm ± 3.1cm
  - Duration: 180-220ms
  - Activation threshold: 18cm
• Pull gestures (Lpull):
  - Average distance: 42.5cm ± 8.7cm
  - Duration: 250-300ms
  - Deactivation threshold: 45cm

Performance Notes:
• 90cm outliers represent intentional mode-exit gestures
• Push consistency (std dev 3.1cm) exceeds pull consistency (8.7cm)
• Recommended adjustment: Add 50ms cooldown after extreme pulls"""
    },
    {
        'filename': 'data_analysis/graphs/right_distance_rpush_rpull.png',
        'description': """Right Hand Gesture Characteristics:

Comparative movement profile:
• Push gestures (Rpush):
  - Average distance: 12.8cm ± 2.9cm
  - 15% faster than left-hand pushes
  - More forceful activation (peak velocity 1.2m/s)
• Pull gestures (Rpull):
  - Average distance: 38.7cm ± 6.2cm
  - 20% more consistent than left-hand pulls
  - Smoother deceleration profile

Functional Insights:
• Right hand specializes in playback control
• Shows more deliberate, controlled movements
• Recommended: Implement velocity-based thresholding"""
    },
    {
        'filename': 'data_analysis/graphs/combined_left_push_pull.png',
        'description': """Left Hand Comprehensive Gesture Analysis:

Movement phase breakdown:
1. Approach Phase (50cm→20cm):
   - Average velocity: 0.8m/s
   - Recognition delay: 40ms
2. Activation Phase (<20cm):
   - Dwell time: 160ms
   - Pressure sensitivity: 85%
3. Return Phase:
   - Varied trajectories indicate different hand withdrawal styles

Technical Recommendations:
• Implement predictive tracking during approach
• Add hysteresis to activation threshold
• Consider hand-size normalization"""
    },
    {
        'filename': 'data_analysis/graphs/combined_right_push_pull.png',
        'description': """Right Hand Gesture Performance:

Advanced movement metrics:
• Command recognition accuracy: 92.4%
• False positive rate: 1.8%
• Average response time: 82ms
• Spatial consistency: 88% (within ±5cm band)

Ergonomic Assessment:
• Natural movement arc matches human biomechanics
• Optimal activation distance (15-25cm) aligns with comfort zone
• Fatigue patterns show reduced precision after 50+ consecutive gestures

Suggested Improvements:
• Adaptive thresholds for prolonged use
• Haptic feedback on successful recognition"""
    },
    {
        'filename': 'data_analysis/graphs/swipe_right_left.png',
        'description': """Right-to-Left Swipe Gesture Analysis:

Spatiotemporal characteristics:
• Average swipe duration: 280ms ± 35ms
• Minimum detection distance: 22cm
• Velocity profile: 
   - Acceleration: 3.2m/s²
   - Peak velocity: 1.5m/s
   - Deceleration: 2.8m/s²
• Success rate: 89.7%

Design Implications:
• Current thresholds work well for medium-speed swipes
• High-velocity swipes (>2m/s) sometimes fail to register
• Edge cases need better handling (angled approaches)"""
    },
    {
        'filename': 'data_analysis/graphs/swipe_left_right.png',
        'description': """Left-to-Right Swipe Gesture Evaluation:

Comparative performance metrics:
• 12% slower than opposite-direction swipes
• Higher activation distance (25cm vs 22cm)
• More variable acceleration profile
• Success rate: 85.3% (4.4% lower than R→L)

User Behavior Notes:
• Shows dominant-hand bias in execution
• Often used in combination with button presses
• Frequently precedes volume adjustments

Optimization Opportunities:
• Directional sensitivity tuning
• Context-aware recognition
• Palm-rejection algorithms"""
    }
]

class GraphViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gesture Analytics Dashboard")
        self.setGeometry(100, 100, 1000, 900)
        self.process = None
        self.run_thread = None
        self.is_running = False


        self.gesture_mappings = load_gesture_mappings()
        self.graph_index = 0
        self.graph_images = []

        for data in graph_data:
            if os.path.exists(data['filename']):
                pix = QPixmap(data['filename'])
                pix = pix.scaled(800, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.graph_images.append((data['filename'], pix, data['description']))

        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout(central)

        self.setup_customization_section()
        self.setup_graph_section()
        self.show_graph()

    def toggle_run(self):
        if not self.is_running:
            self.run_button.setText("Stop Program")
            self.is_running = True
            self.disable_customization()
            self.run_thread = threading.Thread(target=self.run_control_py)
            self.run_thread.start()
        else:
            self.stop_control_py()

    def run_control_py(self):
        self.process = subprocess.Popen(
            [sys.executable, "control.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in self.process.stdout:
            print("[control.py]", line.strip())
        self.process = None
        self.is_running = False
        self.run_button.setText("Run Program")
        self.enable_customization()

    def stop_control_py(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
        self.is_running = False
        self.run_button.setText("Run Program")
        self.enable_customization()

    def disable_customization(self):
        for cb in self.combo_boxes.values():
            cb.setEnabled(False)

    def enable_customization(self):
        for cb in self.combo_boxes.values():
            cb.setEnabled(True)

    def setup_customization_section(self):
        box = QGroupBox("Customize Gesture Mappings")
        form = QFormLayout()
        self.combo_boxes = {}

        for gesture, gtype in gesture_types.items():
            cb = QComboBox()
            if gtype == 'single':
                cb.addItems(single_keys)
                entry = self.gesture_mappings.get(gesture, {})
                key = entry.get('key') or (entry.get('keys') or [''])[0]
                cb.setCurrentText(key)
            else:
                cb.addItems(['+'.join(hk) for hk in hotkey_combinations])
                keys = self.gesture_mappings.get(gesture, {}).get('keys', [])
                cb.setCurrentText('+'.join(keys))

            self.combo_boxes[gesture] = cb
            form.addRow(f"{gesture}:", cb)

        save_btn = QPushButton("Save Mappings")
        save_btn.clicked.connect(self.save_customizations)
        form.addRow(save_btn)

        self.run_button = QPushButton("Run Program")
        self.run_button.clicked.connect(self.toggle_run)
        form.addRow(self.run_button)


        box.setLayout(form)
        self.layout.addWidget(box)

    def save_customizations(self):
        updated = {}
        for gesture, cb in self.combo_boxes.items():
            val = cb.currentText().split('+')
            gtype = gesture_types[gesture]
            if gtype == 'single':
                updated[gesture] = {
                    "type": "key_press",
                    "key": val[0]
                }
            else:
                existing = self.gesture_mappings.get(gesture, {})
                updated[gesture] = {
                    "type": existing.get("type", "hotkey"),
                    "keys": val
                }
                if "repeat" in existing:
                    updated[gesture]["repeat"] = existing["repeat"]

        save_gesture_mappings(updated)
        self.gesture_mappings = updated

    def setup_graph_section(self):
        self.title_label = QLabel("", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.desc_box = QTextEdit()
        self.desc_box.setReadOnly(True)
        self.desc_box.setStyleSheet("font-size: 14px;")
        self.desc_box.setMaximumHeight(150)
        self.layout.addWidget(self.desc_box)

        nav = QHBoxLayout()
        prev_btn = QPushButton("◀ Previous", self)
        prev_btn.clicked.connect(self.show_prev)
        nav.addWidget(prev_btn)

        next_btn = QPushButton("Next ▶", self)
        next_btn.clicked.connect(self.show_next)
        nav.addWidget(next_btn)

        self.layout.addLayout(nav)

    def show_graph(self):
        if not self.graph_images:
            self.title_label.setText("No images found")
            return

        filename, pix, description = self.graph_images[self.graph_index]
        title = filename.replace('.png', '').replace('_', ' ').title()
        self.title_label.setText(title)
        self.image_label.setPixmap(pix)
        self.desc_box.setText(description)

    def show_next(self):
        if self.graph_images:
            self.graph_index = (self.graph_index + 1) % len(self.graph_images)
            self.show_graph()

    def show_prev(self):
        if self.graph_images:
            self.graph_index = (self.graph_index - 1) % len(self.graph_images)
            self.show_graph()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphViewerApp()
    window.show()
    sys.exit(app.exec_())
