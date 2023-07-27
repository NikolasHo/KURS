#!/bin/bash

# Funktion zum Installieren von Django
install_virtual_env() {
    echo "Installiere virt..."
    python3 -m venv 
    echo "Virtual wurde erfolgreich installiert."
}

# Funktion zum Installieren von Django
install_packages() {
    echo "Installiere virt..."
    source bin/activate
    pip install -r requirements.txt
    echo "Virtual wurde erfolgreich installiert."
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
User=$USER
WorkingDirectory=$(pwd)/web
ExecStart=$(pwd)/python manage.py runserver_plus --cert-file cert.pem --key-file key.pem $my_ip

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

    sudo systemctl daemon-reload
    sudo systemctl enable kurs_server
}

# Aufruf der Hauptfunktion
main
