# graphTest5.py
# Real-time drill string visualization with PyQtGraph and TCP sockets
import sys
import os
import math
import threading
import socket
import json
import time
import numpy as np
import pyqtgraph as pg
from scipy.interpolate import splprep, splev
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout,
    QGroupBox, QSizePolicy, QSpacerItem, QPushButton, QGraphicsEllipseItem, QComboBox,
    QScrollArea, QFrame
)
from PyQt5.QtGui import QBrush, QPen

# ==== SETTINGS & CONFIGURATION ==== #
HOST = '10.119.97.116'   # LabVIEW source
PORT = 8081
HOSTB = 'localhost'      # Blender listener
PORTB = 13000
LABVIEW_RECONNECT_DELAY = 2.0  # seconds

# Visualization settings
scale_factor = 1.5
zoom_window = 0.01
string_zoom_range = 0.009
wellbore_radius = 0.001

# ==== Persistent Blender Sender ==== #
class BlenderSender:
    def __init__(self, host, port, reconnect_interval=2.0, status_callback=None):
        self.host = host
        self.port = port
        self.sock = None
        self.lock = threading.Lock()
        self.last_attempt = 0.0
        self.reconnect_interval = reconnect_interval
        self.status_callback = status_callback  # callable(bool)
        self._connected_flag = False

    def _connect(self):
        if self.sock:
            return True
        now = time.time()
        if now - self.last_attempt < self.reconnect_interval:
            return False
        self.last_attempt = now
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect((self.host, self.port))
            self.sock = s
            print("[Blender] Connected ✅")
            if not self._connected_flag:
                self._connected_flag = True
                if self.status_callback:
                    self.status_callback(True)
            return True
        except Exception as e:
            print(f"[Blender] Connect failed: {e}")
            self.sock = None
            if self._connected_flag:
                self._connected_flag = False
                if self.status_callback:
                    self.status_callback(False)
            return False

    def close(self):
        with self.lock:
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
                self.sock = None
                print("[Blender] Connection closed")
                if self._connected_flag:
                    self._connected_flag = False
                    if self.status_callback:
                        self.status_callback(False)

    def send_last_two(self, frame_dict: dict):
        with self.lock:
            if not self._connect():
                return
            try:
                indices = sorted(int(k[1:]) for k in frame_dict if k.startswith('x'))
                if len(indices) < 2:
                    return
                payload = {}
                for idx in indices[-2:]:
                    for key in ('x', 'y', 'rot'):
                        payload[f"{key}{idx}"] = frame_dict[f"{key}{idx}"]
                msg = json.dumps(payload) + "\n"
                self.sock.sendall(msg.encode('utf-8'))
                print(f"[Blender] Sent: {payload}")
            except (BrokenPipeError, ConnectionResetError) as e:
                print(f"[Blender] Broken pipe/reset: {e}")
                self.close()
            except Exception as e:
                print(f"[Blender] Send error: {e}")

# ================== GUI CLASS (REAL-TIME) ================== #
class NodePlot(QWidget):
    new_frame = pyqtSignal(dict)   # thread-safe frame signal
    labview_status = pyqtSignal(bool)
    blender_status = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drill String Visualization – Live Streaming")
        self.resize(1800, 1100)

        # Global palette / stylesheet (dark theme)
        self.setStyleSheet(
            """
            QWidget { background-color: #101418; color: #E0E6ED; font-family: Segoe UI, Arial; }
            QGroupBox { border: 1px solid #2A323C; border-radius:6px; margin-top:14px; }
            QGroupBox::title { subcontrol-origin: margin; left:10px; padding:0 4px; color:#9CC9FF; }
            QLabel { font-size:14px; }
            QPushButton { background:#1F2630; border:1px solid #394554; border-radius:4px; padding:6px 10px; font-weight:600; }
            QPushButton:hover { background:#27313D; }
            QPushButton:pressed { background:#324050; }
            QComboBox { background:#1C222A; border:1px solid #394554; padding:4px 6px; }
            QScrollArea { border:none; }
            QToolTip { background:#1F2630; color:#E0E6ED; border:1px solid #394554; }
            """
        )

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # ===== Top Section: HUD + Meta + Controls =====
        self.top_layout = QHBoxLayout()
        self.hud_boxes = []

        # Node data container inside scroll area (adaptive to many nodes)
        self.hud_container = QWidget()
        self.hud_layout = QHBoxLayout(self.hud_container)
        self.hud_layout.setContentsMargins(4, 4, 4, 4)
        self.hud_layout.setSpacing(8)
        self.hud_scroll = QScrollArea()
        self.hud_scroll.setWidgetResizable(True)
        self.hud_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.hud_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.hud_scroll.setFrameShape(QFrame.NoFrame)
        self.hud_scroll.setWidget(self.hud_container)
        self.hud_group = QGroupBox("Node Data")
        hud_group_layout = QVBoxLayout()
        hud_group_layout.addWidget(self.hud_scroll)
        self.hud_group.setLayout(hud_group_layout)

        self.frame_group = QGroupBox("Simulation / Metrics")
        self.frame_group.setMinimumSize(180, 130)
        frame_layout = QVBoxLayout()
        self.frame_label = QLabel("Frame Index: 0")
        self.time_label = QLabel("Elapsed Time: 0.000 s")
        self.displacement_label = QLabel("Total Displacement: 0.0000 m")
        for lbl in (self.frame_label, self.time_label, self.displacement_label):
            lbl.setStyleSheet("font-size:16px; padding:2px;")
            frame_layout.addWidget(lbl)
        self.frame_group.setLayout(frame_layout)
        self.frame_group.setStyleSheet("QGroupBox { font-weight:bold; font-size:18px; padding-top:24px; }")

        # Controls group
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.pause_button = QPushButton("Pause Stream")
        self.pause_button.setToolTip("Pause / resume incoming live data updates (local only)")
        self.pause_button.setMaximumWidth(140)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.restart_button = QPushButton("Restart App")
        self.restart_button.setToolTip("Restart the entire visualization application")
        self.restart_button.setMaximumWidth(140)
        self.restart_button.clicked.connect(self.restart_program)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.restart_button)
        self.controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        controls_layout.addLayout(button_layout)
        self.controls_group.setLayout(controls_layout)

        self.top_layout.addWidget(self.hud_group, stretch=5)
        self.top_layout.addWidget(self.frame_group, stretch=1)
        self.top_layout.addWidget(self.controls_group, stretch=1)
        self.layout.addLayout(self.top_layout, 0, 0, 1, 6)

        # Center container for main plots (row 1)
        self.plot_row_container = QHBoxLayout()
        self.compare_plot = pg.PlotWidget(title="String Shape: Baseline vs Current (Top View)")
        vb = self.compare_plot.getViewBox()
        vb.setAspectLocked(True)
        vb.invertY(True)
        self.compare_plot.showGrid(x=True, y=True)
        self.compare_plot.setLabel('left', 'Y')
        self.compare_plot.setLabel('bottom', 'X')
        self.compare_plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_row_container.addWidget(self.compare_plot, stretch=1)
        self.torsion_plot = pg.PlotWidget(title="Torsional Rotation History (deg/s)")
        self.torsion_plot.showGrid(x=True, y=True)
        self.torsion_plot.setLabel('left', 'Torsion (deg/s)')
        self.torsion_plot.setLabel('bottom', 'Frame')
        self.torsion_plot.addLegend()
        self.torsion_plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_row_container.addWidget(self.torsion_plot, stretch=1)
        self.layout.addLayout(self.plot_row_container, 1, 0, 1, 6)
        self.layout.setRowStretch(1, 4)

        # Single node detail section (row 2)
        self.detail_container = QHBoxLayout()
        self.node_selector = QComboBox()
        self.node_selector.setToolTip("Choose a node to inspect its local displacement vs baseline")
        self.node_selector.currentIndexChanged.connect(self.update_node_detail_plot)
        self.node_selector.setEnabled(False)
        selector_label = QLabel("Focused Node:")
        selector_label.setStyleSheet("font-weight:600;")
        self.detail_container.addWidget(selector_label)
        self.detail_container.addWidget(self.node_selector)
        self.detail_plot = pg.PlotWidget(title="Focused Node – Local Motion")
        self.detail_plot.setAspectLocked(True)
        self.detail_plot.showGrid(x=True, y=True)
        self.detail_plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.detail_container.addWidget(self.detail_plot, stretch=1)
        self.layout.addLayout(self.detail_container, 2, 0, 1, 6)
        self.layout.setRowStretch(2, 2)

        # Status bar (bottom)
        self.status_bar = QHBoxLayout()
        self.lbl_status_labview = QLabel("LabVIEW: Disconnected")
        self.lbl_status_blender = QLabel("Blender: Disconnected")
        for lbl in (self.lbl_status_labview, self.lbl_status_blender):
            lbl.setStyleSheet("font-size:13px; color:#89A7C2; padding:2px 6px;")
        self.status_bar.addWidget(self.lbl_status_labview)
        self.status_bar.addWidget(self.lbl_status_blender)
        self.status_bar.addStretch(1)
        self.layout.addLayout(self.status_bar, 3, 0, 1, 6)

        # ---- State ----
        self.frame_index = 0
        self.first_frame = None
        self.prev_positions = None
        self.total_displacement = 0.0
        self.time_history = []
        self.torsion_history = []
        self.node_count = 0
        self.full_view_mode = False
        self.paused = False
        self.wellbore_path = {'x': [], 'y': []}

        # ---- Signal wiring ----
        self.new_frame.connect(self.add_frame)
        self.labview_status.connect(self.set_labview_status)
        self.blender_status.connect(self.set_blender_status)

    def build_node_ui(self, node_count):
        for i in range(node_count):
            group = QGroupBox(f"Node {i+1}")
            group.setMinimumSize(160, 120)
            gl = QVBoxLayout()
            gl.addItem(QSpacerItem(20, 10))
            lx = QLabel("X: --")
            ly = QLabel("Y: --")
            lt = QLabel("Torsion: --")
            for lbl in (lx, ly, lt):
                lbl.setStyleSheet("font-size:14px; padding:1px;")
                gl.addWidget(lbl)
            group.setLayout(gl)
            group.setStyleSheet("QGroupBox { font-weight:bold; font-size:16px; padding-top:18px; }")
            self.hud_layout.addWidget(group)
            self.hud_boxes.append((lx, ly, lt))

        # Populate selector
        self.node_selector.clear()
        for i in range(node_count):
            self.node_selector.addItem(f"Node {i+1}", i)
        self.node_selector.setEnabled(True)

        self.torsion_history = [[] for _ in range(node_count)]

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.setText("Play" if self.paused else "Pause")

    def restart_program(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F:
            self.full_view_mode = not self.full_view_mode

    def interpolate_nurbs(self, xs, ys, smooth=0):
        if len(xs) <= 3:
            return xs, ys
        pts = np.array([xs, ys])
        try:
            tck, u = splprep(pts, s=smooth)
            unew = np.linspace(0, 1.0, 100)
            out = splev(unew, tck)
            return out[0], out[1]
        except Exception:
            return xs, ys

    def add_frame(self, frame_dict):
        """Ingest a new frame dictionary from the listener thread (via signal)."""
        if self.paused:
            return

        # First frame -> initialize baseline & HUD
        if self.first_frame is None:
            self.first_frame = frame_dict.copy()
            self.node_count = len([k for k in frame_dict if k.startswith('x')])
            self.build_node_ui(self.node_count)

        # Accumulate total displacement (sum of Euclidean movements per node)
        if self.prev_positions is not None:
            for i in range(self.node_count):
                x_curr = frame_dict.get(f'x{i+1}', 0.0)
                y_curr = frame_dict.get(f'y{i+1}', 0.0)
                x_prev, y_prev = self.prev_positions[i]
                dx = x_curr - x_prev
                dy = y_curr - y_prev
                self.total_displacement += math.sqrt(dx * dx + dy * dy)

        # Cache current positions for next displacement calc
        self.prev_positions = [
            (frame_dict.get(f'x{i+1}', 0.0), frame_dict.get(f'y{i+1}', 0.0))
            for i in range(self.node_count)
        ]

        # Update summary labels
        self.frame_label.setText(f"Frame Index: {self.frame_index}")
        self.time_label.setText(f"Elapsed Time: {self.frame_index * 0.001:.3f} s")
        self.displacement_label.setText(f"Total Displacement: {self.total_displacement:.4f} m")
        self.time_history.append(self.frame_index)

        # HUD per node + torsion histories
        for i in range(self.node_count):
            x = frame_dict.get(f'x{i+1}', 0.0)
            y = frame_dict.get(f'y{i+1}', 0.0)
            rot = frame_dict.get(f'rot{i+1}', 0.0)
            self.hud_boxes[i][0].setText(f"X: {x:.5f}")
            self.hud_boxes[i][1].setText(f"Y: {y:.5f}")
            self.hud_boxes[i][2].setText(f"Torsion: {rot:.3f}")
            self.torsion_history[i].append(rot)

        # Plots
        self.update_node_detail_plot()
        self.update_comparison_plot(frame_dict)
        self.update_torsion_plot()

        # Advance frame counter
        self.frame_index += 1

    def update_comparison_plot(self, current):
        self.compare_plot.clear()
        xs0 = [self.first_frame[f'y{i+1}'] for i in range(self.node_count)]  # flipped
        ys0 = [self.first_frame[f'x{i+1}'] for i in range(self.node_count)]
        xsN = [current[f'y{i+1}'] for i in range(self.node_count)]
        ysN = [current[f'x{i+1}'] for i in range(self.node_count)]

        x0s, y0s = self.interpolate_nurbs(xs0, ys0)
        xNs, yNs = self.interpolate_nurbs(xsN, ysN)
        p0 = self.compare_plot.plot(x0s, y0s, pen=pg.mkPen('b', width=2))
        pN = self.compare_plot.plot(xNs, yNs, pen=pg.mkPen('g', width=2, style=pg.QtCore.Qt.DashLine))
        self.compare_plot.plot(xs0, ys0, pen=None, symbol='o', symbolBrush='b')
        self.compare_plot.plot(xsN, ysN, pen=None, symbol='x', symbolBrush='g')

        # Trail (limit length to avoid buildup)
        self.wellbore_path['x'].append(xsN[-1])
        self.wellbore_path['y'].append(ysN[-1])
        MAX_TRAIL = 400
        if len(self.wellbore_path['x']) > MAX_TRAIL:
            self.wellbore_path['x'] = self.wellbore_path['x'][-MAX_TRAIL:]
            self.wellbore_path['y'] = self.wellbore_path['y'][-MAX_TRAIL:]

        for x, y in zip(self.wellbore_path['x'], self.wellbore_path['y']):
            ellipse = QGraphicsEllipseItem(
                x - wellbore_radius, y - wellbore_radius,
                wellbore_radius * 2, wellbore_radius * 2
            )
            ellipse.setBrush(pg.mkBrush(150, 150, 150, 30))
            ellipse.setPen(pg.mkPen(None))
            self.compare_plot.addItem(ellipse)

        if self.full_view_mode:
            self.compare_plot.autoRange()
        else:
            cx = (xs0[-1] + xsN[-1]) / 2
            cy = (ys0[-1] + ysN[-1]) / 2
            self.compare_plot.setXRange(cx - string_zoom_range, cx + string_zoom_range)
            self.compare_plot.setYRange(cy - string_zoom_range, cy + string_zoom_range)

    def update_torsion_plot(self):
        self.torsion_plot.clear()
        for i, data in enumerate(self.torsion_history):
            pen = pg.mkPen(color=pg.intColor(i), width=2)
            # Ensure equal length (defensive in case of any race)
            n = min(len(self.time_history), len(data))
            if n == 0:
                continue
            self.torsion_plot.plot(self.time_history[:n], data[:n], pen=pen, name=f'Node {i+1}')

    def update_node_detail_plot(self):
        """Update the bottom close-up displacement view for the currently selected node."""
        if self.node_count == 0 or self.first_frame is None or not hasattr(self, 'node_selector'):
            return
        sel_index = self.node_selector.currentData() if self.node_selector.count() else 0
        if sel_index is None:
            sel_index = 0
        if sel_index >= self.node_count:
            sel_index = self.node_count - 1
        i = sel_index
        if self.prev_positions is None:
            return
        # Reference (baseline) and current positions
        x_ref = self.first_frame.get(f'x{i+1}', 0.0)
        y_ref = self.first_frame.get(f'y{i+1}', 0.0)
        x_curr, y_curr = self.prev_positions[i]
        self.detail_plot.clear()
        self.detail_plot.plot([x_ref], [y_ref], pen=None, symbol='o', symbolBrush='b')
        self.detail_plot.plot([x_curr], [y_curr], pen=None, symbol='o', symbolBrush='g')
        sx, sy = self.interpolate_nurbs([x_ref, x_curr], [y_ref, y_curr])
        self.detail_plot.addItem(pg.PlotDataItem(x=sx, y=sy, pen=pg.mkPen('r', width=2)))
        self.detail_plot.setXRange((x_curr + x_ref)/2 - zoom_window, (x_curr + x_ref)/2 + zoom_window)
        self.detail_plot.setYRange((y_curr + y_ref)/2 - zoom_window, (y_curr + y_ref)/2 + zoom_window)
        self.detail_plot.setTitle(f"Close-Up View of Node {i+1} Displacement - Frame {self.frame_index}")

    # ===== Status helpers =====
    def set_labview_status(self, ok: bool):
        if ok:
            self.lbl_status_labview.setText("LabVIEW: Connected")
            self.lbl_status_labview.setStyleSheet("color:#4CC990; font-weight:600;")
        else:
            self.lbl_status_labview.setText("LabVIEW: Disconnected")
            self.lbl_status_labview.setStyleSheet("color:#CC6666; font-weight:600;")

    def set_blender_status(self, ok: bool):
        if ok:
            self.lbl_status_blender.setText("Blender: Connected")
            self.lbl_status_blender.setStyleSheet("color:#4CC990; font-weight:600;")
        else:
            self.lbl_status_blender.setText("Blender: Disconnected")
            self.lbl_status_blender.setStyleSheet("color:#CC6666; font-weight:600;")

# ================== LISTENER ================== #
def listen_for_data(window, blender_sender: BlenderSender):
    """Persistent listener with auto-reconnect handling socket closure cleanly."""
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5.0)
                try:
                    s.connect((HOST, PORT))
                    print("[LabVIEW] Connected ✅")
                    window.labview_status.emit(True)
                except Exception as ce:
                    print(f"[LabVIEW] Connect failed: {ce}")
                    window.labview_status.emit(False)
                    time.sleep(LABVIEW_RECONNECT_DELAY)
                    continue

                # Once connected, make a file wrapper (no timeout)
                s.settimeout(None)
                f = s.makefile("r", encoding="utf-8", newline="\n")
                while True:
                    try:
                        line = f.readline()
                        if not line:  # remote closed
                            print("[LabVIEW] Remote closed connection.")
                            break
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            values = [float(x.replace('"', '')) for x in line.split(',')]
                            node_count = len(values) // 3
                            formatted = {}
                            for i in range(node_count):
                                base = i * 3
                                formatted[f"x{i+1}"] = values[base]
                                formatted[f"y{i+1}"] = values[base + 1]
                                formatted[f"rot{i+1}"] = values[base + 2]
                            # print("Received:", formatted)  # verbose; keep if needed
                            window.new_frame.emit(formatted)
                            blender_sender.send_last_two(formatted)
                        except ValueError as pe:
                            print(f"[LabVIEW] Parse error: {pe} (line='{line}')")
                        except Exception as pe:
                            print(f"[LabVIEW] Frame handling error: {pe}")
                    except (OSError, socket.error) as re:
                        print(f"[LabVIEW] Read error: {re}")
                        break
                    except Exception as ue:
                        print(f"[LabVIEW] Unexpected read loop error: {ue}")
                        break
        finally:
            window.labview_status.emit(False)
            # Delay before attempting reconnection (avoid tight loop)
            time.sleep(LABVIEW_RECONNECT_DELAY)

# ================== MAIN ================== #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NodePlot()
    window.show()

    # Provide callback to update blender status safely via signal
    def blender_status_cb(ok: bool):
        # invoked from sender thread context (listener), forward to GUI thread
        window.blender_status.emit(ok)

    blender_sender = BlenderSender(HOSTB, PORTB, status_callback=blender_status_cb)

    listener_thread = threading.Thread(
        target=listen_for_data,
        args=(window, blender_sender),
        daemon=True
    )
    listener_thread.start()

    exit_code = app.exec_()
    blender_sender.close()
    sys.exit(exit_code)