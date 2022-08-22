const TronWeb = require('tronweb')
const HttpProvider = "https://api.trongrid.io";

const dotenv  = require('dotenv')
dotenv.config()
// console.log(HttpProvider);
// let fullNode = 'https://api.trongrid.io';
// let solidityNode = 'https://api.trongrid.io';
// let eventServer = 'https://api.trongrid.io';
let fullNode = 'https://nile.trongrid.io';
let solidityNode = 'https://nile.trongrid.io';
let eventServer = 'https://nile.trongrid.io';
const privateKey = process.env.TRONPRIVATE;
const tronWeb = new TronWeb(fullNode, solidityNode, eventServer, privateKey);
const  redis = require('redis');

const redispwd = process.env.REDISPWD
const redishost = process.env.REDISHOST
// console.log(redispwd)
const client = redis.createClient({
    socket: {
        host: redishost,
    },
    password: redispwd,
    database:3

});
process.on('uncaughtException', function (err) {
    console.error(err.stack);
    console.log("Node NOT Exiting...");
   });
//contract.[eventname].watch(callback)  eventname是要监听此合约事件的名称

async function start_sync() {
    console.log("syncing tron usdt");
    await client.connect();
    // const trc20ContractAddress = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"; //mainnet USDT contract
    const trc20ContractAddress = "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"; //neil USDT contract
    let contract = await tronWeb.contract().at(trc20ContractAddress);
    await contract && contract.Transfer().watch((err, event) => {
        if (err)
            return console.error('Error with "Message" event:', err);

        console.group('New event received');
        console.log('- Contract Address:', event.contract);
        console.log('- Event Name:', event.name);
        console.log('- Transaction:', event.transaction);
        console.log('- Block number:', event.block);
        console.log('- Result:', event.result, '\n');
        console.groupEnd();

        const data = {
            "contractAddress":event.contract,
            "eventName":event.name,
            "transactionHash":event.transaction,
            "blockNumber":event.block,
            "result":event.result
        }
        // console.log(JSON.parse(data));
        client.set("last_block_TUSDT",event.block)
        client.rPush("TronTransfer",JSON.stringify(data))
        // client.disconnect();


    });

}


start_sync();