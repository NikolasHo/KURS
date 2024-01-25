#!/bin/bash
    
    # Ermittle die eigene IP-Adresse
    my_ip=$(hostname -I | awk '{print $1}')

    # aktiviere virt. Umgebung
    source /home/hoppe/kurs/venv/bin/activate

    /home/hoppe/kurs/venv/bin/python /home/hoppe/kurs/web/manage.py runserver $my_ip:8523