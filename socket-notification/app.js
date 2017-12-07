/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/socket-notification/app.js
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/socket-notification
 * Created Date: Wednesday, December 6th 2017, 12:12:21 am
 * Author: qknow
 *
 * Copyright (c) 2017 Your Company
 */

const app = require('http').createServer()
const io = require('socket.io').listen(app)
const MongoOplog = require('mongo-oplog')
const config = require('config')
const oplog = MongoOplog(config.get('db.url'))

console.log('config', config)
app.listen(4002)

io.sockets.on('connection', (socket) => {
  console.log('socket:connection', socket.id)
 // io.sockets.emit('hello,all')
})

oplog.tail()

oplog.on('op', data => {
  console.log(data)
})

oplog.on('insert', doc => {
  switch (doc.ns) {
    case 'neo-otcgo.nep5_m_transactions':
      io.emit('transaction', 'new')
      break
    case 'neo-otcgo.nep5_m_addresses':
      io.emit('address', 'new')
      break
    case 'neo-otcgo.test':
      io.emit('transaction', 'new')
      io.emit('address', 'new')
      console.log('test')
      break
    default : break
  }
  console.log(doc)
})

oplog.on('update', doc => {
  console.log(doc)
})

oplog.on('delete', doc => {
  console.log(doc.o._id)
})

oplog.on('error', error => {
  console.log(error)
})

oplog.on('end', () => {
  console.log('Stream ended')
})
