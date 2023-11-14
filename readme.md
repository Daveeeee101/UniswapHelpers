# Ethereum + Uniswap Code Snippets

This repo contains code created to easily interface with the ethereum ecosystem, with a specific emphasis on Uniswap liquidity pools.
I hope it is useful!

---

## Examples

A number of examples for using this code are given in examples.py. 
They cover the most important parts of the code base, but it is far from exhaustive.

---

## Overview

The code is broken into four main parts, each in their own directory. 

Web3Types provides the most basic of types any web3 application will use. 
I decided I wanted as little dependency on the current python web3 library so basic things like a HexBytes and Address type are given.
Be careful with these types throughout some of the programs you write on top of this - a lot of methods and functions may take an Address
object as opposed to a str - you will have to wrap the string as an address. 
Fortunately almost all methods and functions are type hinted, so it should be pretty easy to check what types the method expects if unsure.

UniswapTypes provides classes that represent Uniswap liquidity pools. 
Quite a few methods on these pools are implemented, but I've only written what I have needed myself, so you might find some useful parts missing.
If this is the case you can always try to add to the class yourself :). It also contains a simple class called RToken that represents
a token. It is very rudimentary - you may want to subclass and add a ticker symbol to the definition (for my use case tickers weren't really needed and pissed me off).
As with Web3Types, you may have to wrap a str token contract address as an RToken in various methods.
Also note that I make no attempt to do anything with the decimals for each token. Once again wasn't really important for my use case, but
it might be something you will want to add.

NetworkConnection provides utility for actually connecting to an Ethereum node (either other https or websockets). 
Note that the code is written to work with Infura and Alchemy. Use with other providers at your own risk! (It would probably work but
you would have to check the  RPC method responses). Put the provider URL's in config.json to connect to your specific instance.

The HTTPRPCConnection is designed in a very OOP'y way.
You create request objects (that are written in BaseRPCRequests and AlchemyRPCRequests), and then use the send_request method to send
these requests. This allows to create lots of requests and then send a batch request using send_batch_request.
Hopefully however, you shouldn't need to interact directly with this class too much. 

The most abstracted class is BlockchainConnectionManager.
This class provides methods to get Uniswap pools, get logs, load liquidity pools from factory contracts, update liquidity pools
and other useful functions. Be very aware of the descriptions given below the method signatures - they almost always contain
important pieces of information to keep in mind!

Finally, there is a Utilities directory. You will mainly use this to get abi function methods for smart contract requests. Just
copy what's in the example!

---