#!/bin/bash
cd /home/usekevinshey/frappe-projects/Recovery-Master
echo "Testing recovery.local site..."
bench --site recovery.local mariadb -e "SELECT name, module, standard FROM tabPage WHERE name='interview_console';"
echo "Testing onefm.local site..."
bench --site onefm.local mariadb -e "SELECT name, module, standard FROM tabPage WHERE name='interview_console';"
