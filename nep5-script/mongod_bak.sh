#!/bin/sh
DUMP=mongodump
OUT_DIR=/data/backup/mongod/tmp   // 备份文件临时目录
TAR_DIR=/data/backup/mongod       // 备份文件正式目录
DATE=`date +%Y_%m_%d_%H_%M_%S`    // 备份文件将以备份时间保存
DB=neo-otcgo 
DB_USER=otcgo                    // 数据库操作员
DB_PASS=u3fhhrPr                // 数据库操作员密码
AUTH_DATABASE=admin
DAYS=14                           // 保留最新14天的备份
TAR_BAK="mongod_bak_$DATE.tar.gz" // 备份文件命名格式
cd $OUT_DIR                       // 创建文件夹
rm -rf $OUT_DIR/*                 // 清空临时目录
mkdir -p $OUT_DIR/$DATE           // 创建本次备份文件夹
$DUMP -u $DB_USER -p $DB_PASS --authenticationDatabase $AUTH_DATABASE -o $OUT_DIR/$DATE --db $DB  // 执行备份命令
tar -zcvf $TAR_DIR/$TAR_BAK $OUT_DIR/$DATE       // 将备份文件打包放入正式目录
find $TAR_DIR/ -mtime +$DAYS -delete             // 删除14天前的旧备份



# mongodump --host 127.0.0.1 --port 27017 -u otcgo -p u3fhhrPr --out /data/backup/  --authenticationDatabase admin --db neo-otcgo 
