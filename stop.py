#!/usr/bin/env python3
"""
Smart Parking - Stop Script
============================
Oprește toate serviciile:
- Docker containers
- Backend NestJS
- Flutter app

Usage: python3 stop.py
"""

import subprocess
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.WARNING}ℹ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def stop_docker():
    """Oprește Docker containers"""
    print_info("Opresc Docker containers...")
    infra_path = Path(__file__).parent / "infra"
    
    try:
        subprocess.run(
            ['docker-compose', 'down'],
            cwd=infra_path,
            check=True
        )
        print_success("Docker containers oprite")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Eroare la oprirea Docker: {e}")
        return False

def kill_node_processes():
    """Oprește procesele Node.js (Backend)"""
    print_info("Opresc Backend NestJS...")
    
    try:
        # Find and kill node processes related to smart-parking
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            check=True
        )
        
        killed_count = 0
        for line in result.stdout.split('\n'):
            if 'node' in line.lower() and 'smart-parking' in line:
                try:
                    # Extract PID (second column)
                    pid = line.split()[1]
                    subprocess.run(['kill', pid], check=False)
                    killed_count += 1
                except:
                    pass
        
        if killed_count > 0:
            print_success(f"Backend oprit ({killed_count} procese)")
        else:
            print_info("Nu am găsit procese Node.js active")
        return True
    except Exception as e:
        print_error(f"Eroare la oprirea Backend: {e}")
        return False

def kill_flutter_processes():
    """Oprește procesele Flutter"""
    print_info("Opresc Flutter app...")
    
    try:
        # Find and kill flutter processes
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            check=True
        )
        
        killed_count = 0
        for line in result.stdout.split('\n'):
            if 'flutter' in line.lower() and ('run' in line or 'dart' in line):
                try:
                    pid = line.split()[1]
                    subprocess.run(['kill', pid], check=False)
                    killed_count += 1
                except:
                    pass
        
        if killed_count > 0:
            print_success(f"Flutter oprit ({killed_count} procese)")
        else:
            print_info("Nu am găsit procese Flutter active")
        return True
    except Exception as e:
        print_error(f"Eroare la oprirea Flutter: {e}")
        return False

def main():
    print_header("🛑 SMART PARKING - STOP SCRIPT 🛑")
    
    # Stop all services
    stop_docker()
    kill_node_processes()
    kill_flutter_processes()
    
    print_header("✅ TOATE SERVICIILE AU FOST OPRITE ✅")
    print(f"""
{Colors.WARNING}Note:{Colors.ENDC}
  - Dacă mai sunt Terminal tabs deschise, le poți închide manual
  - Docker containers au fost oprite și șterse
  - Poți reporni totul cu: python3 start.py

{Colors.BOLD}Bye! 👋{Colors.ENDC}
""")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nScript întrerupt de utilizator")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n\nEroare neașteptată: {e}")
        sys.exit(1)
