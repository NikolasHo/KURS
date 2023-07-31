#!/bin/bash

# Funktion zum Installieren von Django
install_virtual_env() {
    if [ -d "venv" ]; then
        echo "Eine virtuelle Umgebung existiert bereits im aktuellen Verzeichnis."
    else
        echo "Installiere virtuelle Umgebung..."
        sudo pip install virtualenv
        virtualenv venv
        echo "Virtuelle Umgebung wurde erfolgreich installiert."
    fi
}

# Funktion zum Installieren von Django
install_packages() {
    echo "Prüfe, ob Requirements installiert wurden..."
    source venv/bin/activate

    if [ -n "$VIRTUAL_ENV" ]; then
    echo "Die virtuelle Umgebung ist aktiv: $VIRTUAL_ENV"
    else
        echo "Die virtuelle Umgebung konnte nicht aktiviert werden."
        exit
    fi
    if pip freeze | grep -Fq -x -f requirements.txt; then
        echo "Requirements wurden bereits installiert."
    else
        echo "Installiere Requirements..."
        pip install django
        pip install tensorflow
        sudo apt-get install python3-tk
        pip install -r requirements.txt
        
        echo "Requirements wurden erfolgreich installiert."
    fi
}


# Funktion zum Einfügen der aktuellen IP-Adresse in die Django-Einstellungen
update_allowed_hosts() {
    echo "Ermittle die aktuelle IP-Adresse..."
    current_ip=$(hostname -I | awk '{print $1}')

    # Passe die ALLOWED_HOSTS-Einstellung in den Django-Einstellungen an
    sed -i "s/ALLOWED_HOSTS = \['.*'\]/ALLOWED_HOSTS = \['$current_ip', 'localhost', '127.0.0.1'\]/" web/web/settings.py

    echo "Aktuelle IP-Adresse wurde in die Django-Einstellungen eingefügt."
}



create_systemd_service() {
    echo "Erstelle den systemd-Service-File..."

    # Ermittle die eigene IP-Adresse
    my_ip=$(hostname -I | awk '{print $1}')

    cat <<EOF > /etc/systemd/system/kurs_server.service
[Unit]
Description=Kurs Server
After=network.target

[Service]
User=hoppe
WorkingDirectory=/home/hoppe/kurs
ExecStart=/home/hoppe/kurs/runserver.sh
Restart=always


[Install]
WantedBy=multi-user.target
EOF
    echo "Der systemd-Service-File wurde erfolgreich erstellt."
    echo "Starten Sie den Dienst mit 'sudo systemctl start kurs_server'."
    echo "Aktivieren Sie den Autostart des Dienstes mit 'sudo systemctl enable kurs_server'."
}


run_migrations() {
    echo "Führe Django-Datenbank-Migrationen aus..."
    cd web  # Gehe zum Django-Projektverzeichnis

    # Erstelle Datenbank-Migrationen basierend auf Django-Modellen
    python manage.py makemigrations

    # Wende die erstellten Migrationen an und aktualisiere die Datenbanktabellen
    python manage.py migrate

    cd -
    echo "Datenbank-Migrationen wurden erfolgreich durchgeführt."
}


# Hauptfunktion
main() {
    echo "Willkommen zur automatisierten Django-Installation und Webdienst-Einrichtung!"

    # Installation von Python3 und pip
    echo "Installiere Python3 und pip..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
    
    # Aufruf der Funktionen
    install_virtual_env

    install_packages

    update_allowed_hosts

    run_migrations

    create_systemd_service

    chmod 777 runserver.sh

    sudo systemctl daemon-reload
    sudo systemctl enable kurs_server
}

# Aufruf der Hauptfunktion
main
