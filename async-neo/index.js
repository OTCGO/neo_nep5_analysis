// -- Bootstrap

const Node = require('./src/node')
const config = require('config')
// -- Chain of command

async function main () {
  try {
    console.log('== Test Syncing Example ==')

  // Instantiate a mainnet node with specified local storage (and to a separate database as default of mongodb.js)
    const options = config.get('config')
    const node = new Node(options)

  // Allow it to sync for 30 seconds
    console.log('Start syncing for 30 seconds...')
    await sleep(30000)

  // Report document counts per collection type
    console.log('block count:', await node.storage.getBlockCount())

    const hash = await node.storage.getBestBlockHash()
    console.log('best block hash:', hash)

    const block = await node.storage.getBlockByHash(hash)
    console.log('best block:', block)

    const txid = block.tx[0].txid
    console.log('a TX ID of the best block:', txid)

    const transaction = await node.storage.getTX(txid)
    console.log('transaction:', transaction)

    console.log('== END ==')
  // process.exit() // neoBlockchain process in the background. Explicit exit call is needed.
  } catch (error) {
    await sleep(30000)
    main()
  }
}

// -- Helper methods

function sleep (ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// -- Execute

process.on('unhandledRejection', (reason, p) => {
  console.log('Unhandled Rejection at: Promise', p, 'reason:', reason)
})

main()
