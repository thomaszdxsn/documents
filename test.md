## MongoDB的集合结构

### 数据库: depthquant_data

- huobi_depth, okex_spot_depth, bitfinex_depth

    - _id: Date
    - pair: Array(交易所的depth长度并不一致)
    
        [{price:Double, amount:Double}, ...]

- binance_depth

    除了普通depth结构的数据以外，还多了一个字段:

    - timestamp: int64

- binance_xxx_yyy

    这些集合是应严总要求存入的binance-order数据，存放的方式并不科学:**pair作为集合名称的一部分而存在**

    document字段包括:

    - _id:Int32 代表交易的tid
    - price:String
    - qty:String
    - time:Int64
    - isBuyerMaker:Boolean
    - isBestMatch:Boolean
    - currency:String
    - exchange:String


### 数据库: shannan_hrt

future数据库的通病是: 没有symbol这个交易对字段，channel字段里面包含了交易对信息但是需要使用正则表达式才能进行查询

- okex_future_depth:
    - _id: Date
    - channel: String
    - timestamp: Int64
    - asks: Array
    - bids: Array

- okex_future_index_price:
    - _id: Date
    - binary: Int32
    - channel: String
    - timestamp: Int64
    - data: Object
        - usdCnyRate: String
        - futureIndex: String
        - timestamp: String

- okex_future_ticker
    - _id: Date
    - binary: Int32
    - channel: String
    - timestamp: String
    - data:Object
        - high: String
        - limitLow: String
        - vol: String
        - last: String
        - low: String
        - buy: String
        - hold_amount: String
        - sell: String
        - contractId: Int64
        - unitAmount: 10
        - limitHight: String
    
- okex_future_trade
    - _id: Date
    - tid: String
    - price: String
    - amount: String
    - time: String
    - type: String
    - channel: String
    - timestamp: Int64

### 数据库: shannan_xinpu

- binance_depth
    
    同depthquant_data的binance_depth集合一摸一样，多余？

- binance_trades

    重复数据，depthquant_data已经存在该数据

- ticker_bfx

    best_ask字段和其它同类型collection不一样，少了后缀`_price`

    - _id: Date
    - symbol: String
    - best_bid_price: Int32
    - best_bid_quantity: Double
    - best_ask: Int32               (? 没有price)
    - best_ask_quantity: Double
    - change: Int32
    - change_perc: Double
    - volume: Double
    - high: Int32
    - low: Int32
    - timestamp: Int64

- ticker_binance

    这个collection几乎所有字段都是String类型。

    - _id: Date
    - symbol: String
    - timestamp: Int64
    - change: String
    - change_perc: String
    - best_bid_price: String
    - best_bid_quantity: String
    - best_ask_price: String
    - best_ask_quantity: String
    - high: String
    - low: String
    - volume: String
    - open: String +
    - close: String +
    - close_quantity: String +

- ticker_huobi

    这个collection主要是字段少

    - _id: Date
    - symbol: String
    - timestamp: Int64
    - best_ask_price: Double
    - best_ask_quantity: Double
    - best_bid_price: Double
    - best_bid_quantity: Double
    
- ticker_okex

    这个collection大部分字段也没有定义类型，都是以String存储.以及没有best_xx_quantity字段

    - _id: Date
    - symbol: String
    - timestamp: Int64
    - high: String
    - low: String
    - volume: String
    - best_bid_price: String
    - best_ask_price: String
    - change: String
    - close: String
    - open: String

## 数据存放的位置

### 脚本

TickerPicker主要的入口在monitors目录下的三个脚本:

- shannan_picker.py
- ticker_picker.py
- xinpu_ticker_picker.py

### 数据库Client

使用的MongoDB数据库Client主要有:

代号 | ADDRESS | 数据库 | USER | AUTH_SOURCE(AUTH数据库)
-- | -- | -- | -- | --
001 | 52.199.28.152:27017 | depthquant_data | admin | admin
002 | 52.199.28.152:27017 | shannan_xinpu | shannan_xinpu | shannan_xinpu
003 | 52.199.28.152:27017 | shannan_hrt | shannan_hrt | shannan_hrt


### ticker_picker.py

交易所 | 数据类型 | 爬取方式| 数据库名称 | 数据库client | symbol
-- | -- | -- | -- | -- | --
Bitfinex | depth | Websocket | bitfinex_depth | 001 | ETHUSD, BTCUSD, ETHBTC, QTMUSD, BCHETH, BCHBTC, EOSETH, EOSBTC
OkexSpot | depth | Websocket | okex_spot_depth | 001 | btc_usdt, eth_usdt, eth_btc,qtum_btc, eos_btc, neo_btc,bch_eth, bch_btc, eos_eth
Huobi | depth | Websocket | huobi_depth | 001 | ethusdt, ethbtc, btcusdt,qtumbtc, eosbtc, neobtc, bcheth, bchbtc, eoseth
Binance | depth | REST | binance_depth | 001 | bnb_btc, btc_usdt, bnb_usdt, ltc_eth,ltc_bnb,bcc_usdt,eth_usdt, bcc_bnb,bcc_btc, ven_bnb, bnb_eth, ven_eth,eth_btc, bcc_eth, ltc_btc, ltc_usdt
Binance | trade | REST | binance_xxx_yyy | 001 | 同上
OkexFuture | depth | Websocket | okex_future_depth | 003 | symbol: eth_usd, btc_usd 合约类型: this_week, next_week, quarter
OkexFuture | ticker | Websocket | okex_future_ticker | 003 |  同上 
OkexFuture | trade | Websocket | okex_future_trade | 003 | 同上
OkexFuture | index_price | Websocket | okex_future_index_price | 003 | 同上

### shannan_picker.py

交易所 | 数据类型 | 爬取方式| 数据库名称 | 数据库client |  symbol
-- | -- | -- | -- | -- |  --
Binance | depth | REST | binance_depth | 001 |  BTCUSDT

### xinpu_ticker_picker.py

交易所 | 数据类型 | 爬取方式| 数据库名称 | 数据库client | symbol
-- | -- | -- | -- | -- | --
Bitfinex | ticker | Websocket | ticker_bfx | 002 | ETHUSD, BTCUSD, ETHBTC, EOSBTC, NEOBTC, QTMUSD
OkexSpot | ticker | Websocket | ticker_okex | 002 | btc_usdt, eth_usdt, eth_btc,qtum_btc, eos_btc, neo_btc, bch_eth, bch_btc, eos_eth
Huobi | ticker | Websocket | ticker_huobi | 002 | ethusdt, ethbtc, btcusdt,qtumbtc, eosbtc, neobtc, bcheth, bchbtc, eoseth
Binance | ticker | Websocket | ticker_binance | 002 | eth_usdt, eth_btc, btc_usdt, qtum_btc, eos_btc, neo_btc 