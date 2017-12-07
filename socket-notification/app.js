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
const oplog = MongoOplog('mongodb://127.0.0.1:27017/local', { ns: 'test.posts' })

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
  io.emit('transaction', { for: 'everyone' })
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
