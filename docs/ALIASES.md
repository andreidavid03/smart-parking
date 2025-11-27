# 🚀 Alias Setup (Optional - For Even Faster Access)

## Adaugă alias-uri în shell-ul tău pentru comenzi și mai rapide!

### Pentru Zsh (macOS default):

Adaugă în `~/.zshrc`:

```bash
# Smart Parking Aliases
alias parking-start="python3 ~/Projects/smart-parking/start.py"
alias parking-stop="python3 ~/Projects/smart-parking/stop.py"
alias parking-logs="cd ~/Projects/smart-parking && docker-compose -f infra/docker-compose.yml logs -f"
alias parking-db="docker exec -it infra-postgres-1 psql -U postgres -d smartparking"
```

### Apoi reload shell:
```bash
source ~/.zshrc
```

### Acum poți folosi:
```bash
# Pornește totul
parking-start

# Oprește totul
parking-stop

# Vezi logs Docker
parking-logs

# Conectează-te la DB
parking-db
```

---

## 🎯 Sau creează funcții zsh mai avansate:

Adaugă în `~/.zshrc`:

```bash
# Smart Parking Advanced Functions
parking() {
    case "$1" in
        start)
            echo "🚀 Pornesc Smart Parking..."
            python3 ~/Projects/smart-parking/start.py
            ;;
        stop)
            echo "🛑 Opresc Smart Parking..."
            python3 ~/Projects/smart-parking/stop.py
            ;;
        restart)
            echo "🔄 Restart Smart Parking..."
            python3 ~/Projects/smart-parking/stop.py
            sleep 2
            python3 ~/Projects/smart-parking/start.py
            ;;
        logs)
            cd ~/Projects/smart-parking
            docker-compose -f infra/docker-compose.yml logs -f
            ;;
        db)
            docker exec -it infra-postgres-1 psql -U postgres -d smartparking
            ;;
        health)
            echo "🏥 Verificare Health..."
            curl http://localhost:3000/health
            echo ""
            ;;
        *)
            echo "Usage: parking {start|stop|restart|logs|db|health}"
            ;;
    esac
}
```

### Apoi reload și folosește:
```bash
source ~/.zshrc

parking start      # Pornește
parking stop       # Oprește
parking restart    # Restart complet
parking logs       # Vezi logs
parking db         # PostgreSQL CLI
parking health     # Verifică backend
```

---

## 📱 Bonus: Desktop Shortcut (macOS)

### Creează app cu Automator:

1. Deschide **Automator**
2. Selectează **Application**
3. Adaugă action: **Run Shell Script**
4. Introdu:
   ```bash
   cd /Users/davidandrei/Projects/smart-parking
   /usr/bin/python3 start.py
   ```
5. Salvează ca: `Smart Parking Start.app`
6. Pune pe Desktop sau în Dock

Acum poți da dublu-click pe icon pentru a porni totul! 🎉

---

## 🔧 Pentru Windows (dacă migrezi):

Adaugă în PowerShell Profile (`$PROFILE`):

```powershell
function parking-start {
    python C:\Projects\smart-parking\start.py
}

function parking-stop {
    python C:\Projects\smart-parking\stop.py
}
```

---

**Now you're a true CLI ninja! 🥷**
