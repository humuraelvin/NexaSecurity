import sys
import json
import subprocess
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import QTimer
from pymongo import MongoClient

class NetworkScannerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Network Scanner")
        self.setGeometry(100, 100, 400, 200)

        self.status_label = QLabel("Click 'Start' to begin scanning the network.", self)

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_scan)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                width: 10px;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.start_button)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.scan_network)

        # MongoDB Atlas connection string
        self.client = MongoClient("mongodb+srv://elvinhumura:123@cluster0.huok3f1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.db = self.client["nexasec"]
        self.collection = self.db["network_results"]

    def start_scan(self):
        self.status_label.setText("Scanning network...")
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.timer.start(5000)

    def scan_network(self):
        try:
            my_ip, network_prefix = self.get_network_info()
            scan_data = self.perform_scan(network_prefix)

            with open("output.json", "w") as f:
                json.dump(scan_data, f, indent=2)

            self.collection.insert_one(scan_data)

            self.status_label.setText(f"Scan completed. Results saved to output.json and MongoDB.\nDevices found: {len(scan_data['devices'])}")
            self.progress_bar.setValue(100)
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.progress_bar.setValue(0)

    def get_network_info(self):
        result = subprocess.run(["ipconfig"], capture_output=True, text=True)
        output = result.stdout

        ip_info = [line for line in output.splitlines() if "IPv4 Address" in line]
        if not ip_info:
            raise Exception("Could not determine IP address. Make sure you're connected to a network.")

        my_ip = ip_info[0].split(":")[1].strip()
        network_prefix = ".".join(my_ip.split(".")[:3])
        return my_ip, network_prefix

    def perform_scan(self, network_prefix):
        devices = []
        online_devices = 0
        vulnerable_devices = 0

        for i in range(1, 255):
            ip = f"{network_prefix}.{i}"

            ping_result = subprocess.run(["ping", "-n", "1", "-w", "100", ip], capture_output=True, text=True)
            if "Reply from" in ping_result.stdout:
                online_devices += 1

                arp_result = subprocess.run(["arp", "-a", ip], capture_output=True, text=True)
                mac_address = "Unknown"
                for line in arp_result.stdout.splitlines():
                    if ip in line:
                        mac_address = line.split()[1]
                        break

                nslookup_result = subprocess.run(["nslookup", ip], capture_output=True, text=True)
                hostname = "Unknown"
                for line in nslookup_result.stdout.splitlines():
                    if "Name:" in line:
                        hostname = line.split(":")[1].strip()
                        break

                vulnerabilities = 0

                devices.append({
                    "id": f"dev-{i:03}",
                    "name": hostname if hostname != "Unknown" else f"Unknown Device-{i}",
                    "ip": ip,
                    "type": "unknown",
                    "status": "online",
                    "lastSeen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "vulnerabilities": vulnerabilities
                })

                if vulnerabilities > 0:
                    vulnerable_devices += 1

            progress = int((i / 254) * 100)
            self.progress_bar.setValue(progress)

        scan_history = [{
            "id": f"scan-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration": "2 minutes",
            "devicesScanned": len(devices),
            "vulnerabilitiesFound": vulnerable_devices,
            "status": "completed"
        }]

        return {
            "devices": devices,
            "scanHistory": scan_history,
            "Api_Key": "MTIzNDU6MjAyNS0wMy0yMVQxMjowMjoxNS4yMzMyODA6NDM5ZTlkZTAxMDJiNTg2ZmI5YjIyM2IyMjJiZjRkYWE0Y2MzMjM3YTY4MjRmNTVlNTNkMTIxYjEyMWYxODMwZg=="
        }

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NetworkScannerApp()
    window.show()
    sys.exit(app.exec())