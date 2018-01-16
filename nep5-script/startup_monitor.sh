#!/bin/bash

python sync_nep5_assets_monitor.py  -r /var/neo-cli/Notifications -d neo-otcgo -m mongodb://otcgo:u3fhhrPr@127.0.0.1:27017/?authSource=admin&replicaSet=rs1 



 db.nep5_m_assets.ensureIndex({"contract":1},{"unique":true})