cd /home/vmadm/proj/NBA
rm -rf authvpc/migrations
rm -rf config/migrations
cd ..
lnvenv/bin/python3 NBA/manage.py makemigrations authvpc
lnvenv/bin/python3 NBA/manage.py makemigrations config
lnvenv/bin/python3 NBA/manage.py migrate