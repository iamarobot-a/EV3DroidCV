set SVR=192.168.45.132
set USR=robot
SET PWD=*****
set DIR1=/mnt/c/Users/farago/PycharmProjects/p31/
set DIR2=/mnt/d/farago/projects/EV3DroidCV/EV3DroidCV/ev3pydrive/
set DIR1=%DIR2%
bash -c "sshpass -p %PWD% scp %DIR2%autonom.py %DIR2%tcpclient.py %USR%@%SVR%:/home/robot"
REM bash -c "sshpass -p %PWD% scp /mnt/c/Users/farago/PycharmProjects/p31/tcpclient.py %USR%@%SVR%:/home/robot"
REM bash -c "sshpass -p %PWD% scp /mnt/c/Users/farago/PycharmProjects/p31/ir.py %USR%@%SVR%:/home/robot"