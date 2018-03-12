# Web Server Quickstart

pass

## WebSockets

`aiohttp.web`支持开箱即用型websocket.

想要建立一个`Websocket`，需要在一个`request handler`中创建一个`WebSocketResponse`，
然后使用它来和另一个端点进行通讯:

```python
async def websocket_handler(request):
    
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data = 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % 
                  ws.exception())
    
    print('websocket connection closed')

    return ws
```
