DATE=`date +%Y_%m_%d_%H_%M_%S` 
mongodump --host 127.0.0.1 --port 27017 -u otcgo -p u3fhhrPr --out /data/backup/$DATE   --authenticationDatabase admin --db neo-otcgo 
# https://brickyang.github.io/2017/03/02/Linux-%E8%87%AA%E5%8A%A8%E5%A4%87%E4%BB%BD-MongoDB/