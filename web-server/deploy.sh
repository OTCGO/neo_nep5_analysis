#!/bin/bash
export NVM_DIR="/home/qknow/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
cd /var/otcgo/neo_wallet_analysis/web-server
git reset --hard
git pull origin master:master
rm -rf dist/
npm install
npm run build
count=`pm2 list|grep neo-nep5 |grep -v grep |wc -l`
if [ $count -eq 0 ];then
pm2 pm2.prod.config.js 
else
pm2 restart pm2.prod.config.js 
fi