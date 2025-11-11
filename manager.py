import subprocess
import time
from datetime import datetime

def systemd_running():
    try:
        with open("/proc/1/comm") as f:
            return f.read().strip() == "systemd"
    except Exception:
        return False

class TailscaleManager:
    def __init__(self, log_callback):
        self.systemd = systemd_running()
        self.log = log_callback

    def _run(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return result.stderr
            return result.stdout
        except Exception as e:
            return str(e)
    
    def is_server_running(self):
        """Check if tailscaled is running"""
        check = subprocess.run(["pgrep", "-x", "tailscaled"], 
                              capture_output=True)
        return check.returncode == 0
    
    def is_connected(self):
        """Check if Tailscale is connected"""
        result = self._run("sudo tailscale status")
        # If status returns content and no error, we're connected
        return result and "100." in result and "Logged out" not in result
    
    def startServer(self):
        if self.systemd:
            self.log("Starting tailscaled via systemd...")
            output = self._run("sudo systemctl start tailscaled")
            if output:
                self.log(f"Server output: {output.strip()}")
            else:
                self.log("Tailscaled started successfully")
        else:
            self.log("Starting tailscaled daemon...")
            # Check if already running
            if not self.is_server_running():
                subprocess.Popen(["sudo", "tailscaled"], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                time.sleep(1)
                if self.is_server_running():
                    self.log("Tailscaled started successfully")
                else:
                    self.log("Failed to start tailscaled")
            else:
                self.log("Tailscaled is already running")
    
    def killServer(self):
        if not self.is_server_running():
            self.log("Server is not running")
            return
            
        if self.systemd:
            self.log("Stopping tailscaled via systemd...")
            output = self._run("sudo systemctl stop tailscaled")
            if output:
                self.log(f"Server output: {output.strip()}")
            else:
                self.log("Tailscaled stopped successfully")
        else:
            self.log("Stopping tailscaled daemon...")
            # Send SIGTERM first (graceful)
            subprocess.run(["sudo", "pkill", "-TERM", "tailscaled"])
            
            # Wait briefly and check if still running
            time.sleep(1)
            
            if self.is_server_running():
                # Force kill if still running
                self.log("Force stopping tailscaled...")
                subprocess.run(["sudo", "pkill", "-KILL", "tailscaled"])
                time.sleep(0.5)
            
            if not self.is_server_running():
                self.log("Tailscaled stopped successfully")
            else:
                self.log("Failed to stop tailscaled")

    def connect(self):
        self.log("Connecting to Tailscale network...")
        output = self._run("sudo tailscale up")
        if output:
            self.log(f"Connect output: {output.strip()}")
        else:
            self.log("Connected to Tailscale")

    def disconnect(self):
        self.log("Disconnecting from Tailscale network...")
        output = self._run("sudo tailscale down")
        if output:
            self.log(f"Disconnect output: {output.strip()}")
        else:
            self.log("Disconnected from Tailscale")

    def status(self):
        return self._run("sudo tailscale status")