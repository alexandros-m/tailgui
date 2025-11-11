import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, 
    QSystemTrayIcon, QMenu, QTextEdit, QLabel, QFrame, QGroupBox
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QTimer

# Import from manager
from manager import TailscaleManager

class TailGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TailGUI - Tailscale Manager")
        self.setMinimumSize(700, 550)
        
        self.manager = TailscaleManager(self.log)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("TailGUI")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Tailscale Network Manager")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; font-size: 12px;")
        main_layout.addWidget(subtitle_label)
        
        # Status indicators
        status_group = QGroupBox("Status")
        status_layout = QHBoxLayout()
        
        # Server status
        server_status_layout = QVBoxLayout()
        server_label = QLabel("Tailscale Daemon:")
        server_label.setStyleSheet("font-weight: bold;")
        self.server_indicator = QLabel("● Stopped")
        self.server_indicator.setStyleSheet("color: #e74c3c; font-size: 14px;")
        server_status_layout.addWidget(server_label)
        server_status_layout.addWidget(self.server_indicator)
        status_layout.addLayout(server_status_layout)
        
        status_layout.addSpacing(40)
        
        # Connection status
        connection_status_layout = QVBoxLayout()
        connection_label = QLabel("Connection:")
        connection_label.setStyleSheet("font-weight: bold;")
        self.connection_indicator = QLabel("● Disconnected")
        self.connection_indicator.setStyleSheet("color: #e74c3c; font-size: 14px;")
        connection_status_layout.addWidget(connection_label)
        connection_status_layout.addWidget(self.connection_indicator)
        status_layout.addLayout(connection_status_layout)
        
        status_layout.addStretch()
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Control buttons
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        
        # Server control button
        self.server_btn = QPushButton("Start Server")
        self.server_btn.setMinimumHeight(40)
        self.server_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.server_btn.clicked.connect(self.toggle_server)
        controls_layout.addWidget(self.server_btn)
        
        # Connection buttons
        button_layout = QHBoxLayout()
        
        connect_btn = QPushButton("Connect")
        connect_btn.setMinimumHeight(40)
        connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        connect_btn.clicked.connect(self.connect_tailscale)
        
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.setMinimumHeight(40)
        disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
        """)
        disconnect_btn.clicked.connect(self.disconnect_tailscale)
        
        button_layout.addWidget(connect_btn)
        button_layout.addWidget(disconnect_btn)
        controls_layout.addLayout(button_layout)
        
        # Status button
        status_btn = QPushButton("View Network Status")
        status_btn.setMinimumHeight(40)
        status_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        status_btn.clicked.connect(self.show_status)
        controls_layout.addWidget(status_btn)
        
        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)
        
        # Log area
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 5px;
                font-family: monospace;
                font-size: 11px;
                padding: 5px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Tray icon setup
        self.setup_tray_icon()
        
        # Start server by default
        self.log("TailGUI started")
        self.manager.startServer()
        self.update_status()
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(3000)  # Update every 3 seconds

    def setup_tray_icon(self):
        """Setup tray icon with single icon"""
        # Use the same icon everywhere
        app_icon = QIcon.fromTheme("network-vpn")
        
        # Set window icon
        self.setWindowIcon(app_icon)
        
        # Set tray icon (same as window icon)
        self.tray_icon = QSystemTrayIcon(app_icon, self)
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show", self.show_window)
        hide_action = tray_menu.addAction("Hide", self.hide_window)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("Quit", self.exit_app)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def tray_icon_activated(self, reason):
        """Handle tray icon clicks"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide_window()
            else:
                self.show_window()

    def show_window(self):
        """Show the main window and update tray icon"""
        self.show()
        self.raise_()
        self.activateWindow()

    def hide_window(self):
        """Hide the main window and update tray icon"""
        self.hide()
        # Update tray icon to "show" when window is closed

    def log(self, message):
        """Add a log message with timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def update_status(self):
        """Update status indicators"""
        # Check server status
        server_running = self.manager.is_server_running()
        if server_running:
            self.server_indicator.setText("● Running")
            self.server_indicator.setStyleSheet("color: #27ae60; font-size: 14px;")
            self.server_btn.setText("Stop Server")
            self.server_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
        else:
            self.server_indicator.setText("● Stopped")
            self.server_indicator.setStyleSheet("color: #e74c3c; font-size: 14px;")
            self.server_btn.setText("Start Server")
            self.server_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
            """)
        
        # Check connection status
        if server_running:
            connection_active = self.manager.is_connected()
            if connection_active:
                self.connection_indicator.setText("● Connected")
                self.connection_indicator.setStyleSheet("color: #27ae60; font-size: 14px;")
            else:
                self.connection_indicator.setText("● Disconnected")
                self.connection_indicator.setStyleSheet("color: #e74c3c; font-size: 14px;")
        else:
            self.connection_indicator.setText("● Server Offline")
            self.connection_indicator.setStyleSheet("color: #95a5a6; font-size: 14px;")

    def toggle_server(self):
        """Toggle server on/off"""
        if self.manager.is_server_running():
            self.manager.killServer()
        else:
            self.manager.startServer()
        self.update_status()

    def connect_tailscale(self):
        """Connect to Tailscale"""
        self.manager.connect()
        QTimer.singleShot(1000, self.update_status)

    def disconnect_tailscale(self):
        """Disconnect from Tailscale"""
        self.manager.disconnect()
        QTimer.singleShot(1000, self.update_status)

    def closeEvent(self, event):
        """Override close event to hide to tray instead of closing"""
        event.ignore()
        self.hide_window()

    def exit_app(self):
        """Properly exit the application"""
        self.log("Shutting down TailGUI...")
        self.status_timer.stop()
        self.manager.killServer()
        QApplication.instance().quit()

    def show_status(self):
        status = self.manager.status()
        
        # Create a dialog with formatted status
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Tailscale Network Status")
        
        # Parse and format the status
        formatted_status = self.format_status(status)
        
        # Use a QTextEdit for better display
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(formatted_status)
        text_edit.setMinimumWidth(700)
        text_edit.setMinimumHeight(300)
        text_edit.setStyleSheet("""
            QTextEdit {
                font-family: monospace;
                font-size: 11px;
            }
        """)
        
        dialog.layout().addWidget(text_edit, 0, 0, 1, dialog.layout().columnCount())
        dialog.exec()

    def format_status(self, status_output):
        """Parse and format tailscale status into a nice table"""
        lines = status_output.strip().split('\n')
        
        if not lines or not lines[0]:
            return "No devices found or Tailscale is not running."
        
        # Parse each line
        devices = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 4:
                ip = parts[0]
                hostname = parts[1]
                user = parts[2]
                os = parts[3]
                status = ' '.join(parts[4:]) if len(parts) > 4 else 'online'
                
                devices.append({
                    'ip': ip,
                    'hostname': hostname,
                    'user': user,
                    'os': os,
                    'status': status if status != '-' else 'online'
                })
        
        # Create formatted table
        header = f"{'IP Address':<17} {'Hostname':<25} {'User':<15} {'OS':<10} {'Status':<30}"
        separator = "=" * 110
        
        formatted = [separator, header, separator]
        
        for device in devices:
            row = f"{device['ip']:<17} {device['hostname']:<25} {device['user']:<15} {device['os']:<10} {device['status']:<30}"
            formatted.append(row)
        
        formatted.append(separator)
        
        return '\n'.join(formatted)