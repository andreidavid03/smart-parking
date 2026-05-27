#!/usr/bin/env python3
"""
Smart Parking - One-Click Startup Script
=========================================
Pornește automat toate serviciile necesare:
- Docker containers (PostgreSQL, MQTT, Adminer)
- Backend NestJS API
- Flutter mobile app

Usage: python3 start.py
"""

import subprocess
import sys
import time
import platform
import socket
import os
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def get_local_ip():
    """Detectează IP-ul local al Mac-ului"""
    try:
        # Try to get en0 interface IP (WiFi/Ethernet on Mac)
        result = subprocess.run(
            ['ipconfig', 'getifaddr', 'en0'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
        
        # Fallback: try socket method
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print_warning(f"Nu pot detecta IP automat: {e}")
        return "localhost"

def update_flutter_ip(ip_address):
    """Actualizează IP-ul în api_service.dart"""
    api_service_path = Path(__file__).parent / "apps/mobile/lib/services/api_service.dart"
    
    if not api_service_path.exists():
        print_error(f"Nu găsesc fișierul: {api_service_path}")
        return False
    
    try:
        content = api_service_path.read_text()
        
        # Replace the baseUrl IP
        import re
        new_content = re.sub(
            r"static const String baseUrl = 'http://[\d.]+:3000';",
            f"static const String baseUrl = 'http://{ip_address}:3000';",
            content
        )
        
        if new_content != content:
            api_service_path.write_text(new_content)
            print_success(f"IP actualizat în api_service.dart: {ip_address}")
            return True
        else:
            print_info("IP-ul este deja setat corect")
            return True
    except Exception as e:
        print_error(f"Eroare la actualizare IP: {e}")
        return False

def update_esp32_ip(ip_address):
    """Actualizează MQTT_BROKER în sketch-ul ESP32"""
    sketch_path = Path(__file__).parent / "apps/esp32/smart_parking_esp32/smart_parking_esp32.ino"

    if not sketch_path.exists():
        print_warning(f"Sketch ESP32 nu găsit: {sketch_path}")
        return False

    try:
        content = sketch_path.read_text()
        import re
        new_content = re.sub(
            r'(const char\* MQTT_BROKER\s*=\s*")[^"]+(")',
            rf'\g<1>{ip_address}\g<2>',
            content
        )
        if new_content != content:
            sketch_path.write_text(new_content)
            print_success(f"MQTT_BROKER actualizat în ESP32 sketch: {ip_address}")
        else:
            print_info("MQTT_BROKER este deja setat corect în sketch")
        return True
    except Exception as e:
        print_error(f"Eroare la actualizare sketch ESP32: {e}")
        return False

def check_docker():
    """Verifică dacă Docker este pornit"""
    try:
        result = subprocess.run(
            ['docker', 'ps'],
            capture_output=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def start_docker_containers():
    """Pornește Docker containers"""
    print_info("Pornesc Docker containers...")
    
    infra_path = Path(__file__).parent / "infra"
    
    try:
        subprocess.run(
            ['docker-compose', 'up', '-d'],
            cwd=infra_path,
            check=True
        )
        
        # Wait for containers to be ready
        print_info("Aștept ca containers să fie ready...")
        time.sleep(5)
        
        # Verify containers are running
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            check=True
        )
        
        running_containers = result.stdout.strip().split('\n')
        print_success(f"Docker containers pornite: {', '.join(running_containers)}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Eroare la pornirea Docker: {e}")
        return False

def free_port(port):
    """Kill any process holding the given port"""
    try:
        import os, signal
        result = subprocess.run(
            ['lsof', '-ti', f'tcp:{port}'],
            capture_output=True, text=True, check=False
        )
        pids = result.stdout.strip().split()
        for pid in pids:
            if pid:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except Exception:
                    pass
        if pids:
            time.sleep(1)
    except Exception:
        pass


def start_backend():
    """Pornește Backend NestJS în background"""
    print_info("Pornesc Backend NestJS...")

    # Free port 3000 first so no EADDRINUSE
    free_port(3000)

    backend_path = Path(__file__).parent / "apps/api"
    
    try:
        # Check if node_modules exists
        if not (backend_path / "node_modules").exists():
            print_warning("node_modules lipsesc. Rulez npm install...")
            subprocess.run(['npm', 'install'], cwd=backend_path, check=True)
        
        # Start backend in background
        if platform.system() == 'Windows':
            process = subprocess.Popen(
                ['cmd', '/c', 'start', 'npm', 'run', 'start:dev'],
                cwd=backend_path,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # macOS/Linux: use osascript to open new Terminal tab
            root_path = Path(__file__).parent
            script = f'''
tell application "Terminal"
    activate
    do script "cd {root_path} && zsh run_backend.sh"
end tell
'''
            subprocess.Popen(['osascript', '-e', script])
        
        # Wait for backend to start
        print_info("Aștept ca Backend să pornească (20 secunde)...")
        for i in range(20):
            time.sleep(1)
            # Try to check if backend is up
            try:
                result = subprocess.run(
                    ['curl', '-s', 'http://localhost:3000/health'],
                    capture_output=True,
                    timeout=2,
                    check=False
                )
                if result.returncode == 0:
                    print_success("Backend NestJS pornit pe http://localhost:3000")
                    return True
            except:
                pass
        
        print_warning("Backend pornit, dar verificarea health nu a confirmat încă (continuă în background)")
        return True
    except Exception as e:
        print_error(f"Eroare la pornirea Backend: {e}")
        return False

def start_flutter():
    """Pornește Flutter app"""
    print_info("Pornesc Flutter app...")
    
    mobile_path = Path(__file__).parent / "apps/mobile"
    
    try:
        # Find iOS 26.1 simulator
        result = subprocess.run(
            ['xcrun', 'simctl', 'list', 'devices', '--json'],
            capture_output=True,
            text=True,
            check=False
        )
        
        ios26_device_id = None
        if result.returncode == 0:
            import json
            devices = json.loads(result.stdout)
            # Look for iOS 26.1 devices
            for runtime, device_list in devices.get('devices', {}).items():
                if 'iOS-26-1' in runtime or 'iOS 26.1' in runtime:
                    for device in device_list:
                        if 'iPhone 16 Plus' in device.get('name', ''):
                            ios26_device_id = device.get('udid')
                            print_success(f"Găsit simulator iOS 26.1: {device.get('name')} ({ios26_device_id})")
                            break
                    if ios26_device_id:
                        break
        
        # Boot the iOS 26.1 simulator if found
        if ios26_device_id:
            # Check if already booted
            boot_result = subprocess.run(
                ['xcrun', 'simctl', 'list', 'devices'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if ios26_device_id not in boot_result.stdout or 'Booted' not in boot_result.stdout:
                print_info("Pornesc iOS 26.1 Simulator...")
                subprocess.run(['xcrun', 'simctl', 'boot', ios26_device_id], check=False)
                subprocess.run(['open', '-a', 'Simulator'], check=False)
                time.sleep(5)
        else:
            print_warning("Nu găsesc simulator iOS 26.1, folosesc simulatorul default...")
            if 'Booted' not in result.stdout:
                print_info("Pornesc iOS Simulator...")
                subprocess.run(['open', '-a', 'Simulator'], check=False)
                time.sleep(5)
        
        # Start Flutter in new Terminal tab with specific device
        if platform.system() == 'Windows':
            subprocess.Popen(
                ['cmd', '/c', 'start', 'flutter', 'run'],
                cwd=mobile_path,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            flutter_cmd = f"cd {mobile_path} && flutter run"
            if ios26_device_id:
                flutter_cmd = f"cd {mobile_path} && flutter run -d {ios26_device_id}"
            
            script = f'''
tell application "Terminal"
    activate
    do script "{flutter_cmd}"
end tell
'''
            subprocess.Popen(['osascript', '-e', script])
        
        print_success("Flutter app pornit în Terminal nou")
        return True
    except Exception as e:
        print_error(f"Eroare la pornirea Flutter: {e}")
        return False

def start_scanner_bridge():
    """Afișează instrucțiuni pentru Scanner Bridge"""
    print_success("QR Scanner Bridge: rulează din VS Code terminal (vezi nota de mai jos)")
    return True


def start_dashboard():
    """Pornește dashboard-ul web pe port 8090"""
    print_info("Pornesc Dashboard web pe http://localhost:8090/dashboard.html ...")

    project_path = str(Path(__file__).parent)

    try:
        free_port(8090)
        subprocess.Popen(
            [sys.executable, '-m', 'http.server', '8090', '--directory', project_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)
        subprocess.Popen(['open', 'http://localhost:8090/dashboard.html'])
        print_success("Dashboard pornit: http://localhost:8090/dashboard.html")
        return True
    except Exception as e:
        print_error(f"Eroare la pornirea Dashboard: {e}")
        return False


def start_homebrew_services():
    """Pornește Mosquitto + PostgreSQL via Homebrew (fallback când Docker nu e disponibil)"""
    print_info("Pornesc Mosquitto + PostgreSQL via Homebrew...")
    try:
        subprocess.run(['brew', 'services', 'start', 'mosquitto'], check=False, capture_output=True)
        subprocess.run(['brew', 'services', 'start', 'postgresql@16'], check=False, capture_output=True)
        time.sleep(2)
        # Verify mosquitto port
        import socket as _s
        try:
            c = _s.create_connection(('localhost', 1883), timeout=2)
            c.close()
            print_success("Mosquitto MQTT pornit pe localhost:1883")
        except Exception:
            print_warning("Mosquitto pare offline — verifică manual: brew services start mosquitto")
        print_success("PostgreSQL pornit pe localhost:5432")
        return True
    except Exception as e:
        print_error(f"Eroare Homebrew services: {e}")
        return False


def main():
    print_header("🚗 SMART PARKING - STARTUP SCRIPT 🚗")
    
    # Step 1: Detect and update IP
    print_info("Pas 1/5: Detectez IP-ul local...")
    ip_address = get_local_ip()
    print_success(f"IP detectat: {ip_address}")
    
    if not update_flutter_ip(ip_address):
        print_error("Nu pot actualiza IP-ul în Flutter")
        sys.exit(1)

    update_esp32_ip(ip_address)

    # Step 2: Check and start Docker (fallback to Homebrew)
    print_info("\nPas 2/5: Verific Docker...")
    if check_docker():
        print_success("Docker este disponibil")
        if not start_docker_containers():
            print_error("Nu pot porni Docker containers")
            sys.exit(1)
    else:
        print_warning("Docker offline — folosesc Homebrew (mosquitto + postgresql@16)")
        if not start_homebrew_services():
            print_error("Nu pot porni serviciile de infrastructură")
            sys.exit(1)
    
    # Step 3: Start Backend
    print_info("\nPas 3/5: Pornesc Backend...")
    if not start_backend():
        print_warning("Backend nu a pornit corect, dar continuăm...")
    
    # Step 4: Start Flutter
    print_info("\nPas 4/5: Pornesc Flutter...")
    if not start_flutter():
        print_error("Nu pot porni Flutter app")
        sys.exit(1)

    # Step 5: Start Scanner Bridge
    print_info("\nPas 5/6: Pornesc QR Scanner Bridge...")
    start_scanner_bridge()

    # Step 6: Start Dashboard
    print_info("\nPas 6/6: Pornesc Dashboard web...")
    start_dashboard()

    # Summary
    print_header("✅ TOATE SERVICIILE AU PORNIT! ✅")
    print(f"""
{Colors.OKGREEN}Servicii disponibile:{Colors.ENDC}
  • Backend API: http://localhost:3000
  • PostgreSQL: localhost:5432
  • Adminer: http://localhost:8080
  • MQTT: localhost:1883
  • Flutter App: iPhone Simulator
  • 🌐 Dashboard: http://localhost:8090/dashboard.html

{Colors.OKCYAN}IP detectat: {ip_address}{Colors.ENDC}

{Colors.WARNING}Note:{Colors.ENDC}
  - Backend și Flutter rulează în Terminal tabs separate
  - Apasă Ctrl+C în fiecare tab pentru a opri serviciile
  - Pentru hot reload Flutter: apasă 'r' în terminal
  - Pentru hot restart Flutter: apasă 'R' în terminal

{Colors.BOLD}▶  Dashboard QR Scanner — deschis automat în browser:{Colors.ENDC}
{Colors.OKGREEN}   http://localhost:8090/dashboard.html{Colors.ENDC}
  Click pe bara verde din dashboard, apoi scanează cu GM65

{Colors.BOLD}Happy coding! 🚀{Colors.ENDC}
""")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nScript întrerupt de utilizator")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n\nEroare neașteptată: {e}")
        sys.exit(1)
