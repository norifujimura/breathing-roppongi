# https://zenn.dev/knowhere_imai/articles/ba850780152b01
#import p5
import pygame
from pygame.locals import *
import sys

import asyncio
import time

import json
from ctypes import *
from bleak import BleakClient

import colorsys

#address = "19C40D9B-F748-1109-CF66-67D6BB739283" # 通信先のMacアドレス
address = "24:58:7C:5C:83:DD"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8" # CHARACTERISTIC_UUID


x = 0
y = 0
hue = 0
lightness = 0
saturation = 0
r = 0
g = 0
b = 0


async def say_after(delay, what):
    print(f"prepare {what} at {time.strftime('%X')}")
    await asyncio.sleep(delay)
    print(f"{what} at {time.strftime('%X')}")

async def my_loop(delay, what):
    global x,y
    while True:
        # return rateを1 Hzに設定
        print(f"{what} x: {x}  y: {y} at {time.strftime('%X')}")
        await asyncio.sleep(delay)

async def ble_byte_reconnect(address,delay):
    global x,y

    while True:
        async with BleakClient(
            address
        ) as client:
            message_received = await client.read_gatt_char(CHARACTERISTIC_UUID)
            print("message_received : {0}".format("".join(map(chr, message_received ))))
            
            while True:

                #message = bytearray( b'\x30\x30')
                message = bytearray(2)
                message[0] = x
                message[1] = y
                # return rateを1 Hzに設定
                try:
                    await client.write_gatt_char(CHARACTERISTIC_UUID,message,response=True)
                    await asyncio.sleep(delay)
                    #print("connected")
                except Exception:
                    print("DISConnected now reconnect")
                    break

async def ble_bytes_reconnect(address,delay):
    global x,y,r,g,b

    while True:
        async with BleakClient(
            address
        ) as client:
            message_received = await client.read_gatt_char(CHARACTERISTIC_UUID)
            print("message_received : {0}".format("".join(map(chr, message_received ))))
            
            while True:

                #message = bytearray( b'\x30\x30')
                message = bytearray(120 * 3)
                for i in range(120):
                    message[i*3] = r
                    message[i*3+1] = g
                    message[i*3+2] = b

                    '''
                    distance = abs( x - i)
                    if distance<30:
                        message[i] = 120- distance
                    else:
                        message[i] = 0
                    '''
                
                # return rateを1 Hzに設定
                try:
                    await client.write_gatt_char(CHARACTERISTIC_UUID,message,response=True)
                    await asyncio.sleep(delay)
                    #print("connected")
                except Exception:
                    print("DISConnected now reconnect")
                    break

async def ble_json_reconnect(address,delay):
    global x,y

    while True:
        async with BleakClient(
            address
        ) as client:
            message_received = await client.read_gatt_char(CHARACTERISTIC_UUID)
            print("message_received : {0}".format("".join(map(chr, message_received ))))
            
            while True:
                message = {
                    "x":x,
                    "y":y
                }
                
                message_b = json.dumps(message).encode('utf-8')
                # return rateを1 Hzに設定
                try:
                    await client.write_gatt_char(CHARACTERISTIC_UUID,message_b,response=True)
                    #await client.write_gatt_char(CHARACTERISTIC_UUID,message_b)
                    await asyncio.sleep(delay)
                    #print("connected")
                except Exception:
                    print("DISConnected now reconnect")
                    break
            
async def ble_json(address,delay):
    global x,y

    async with BleakClient(address) as client:
        message_received = await client.read_gatt_char(CHARACTERISTIC_UUID)
        print("message_received : {0}".format("".join(map(chr, message_received ))))
        
        #info = "{\"x\": \"100\",\"y\":\"100\"}" # put your large data here
        #length = len(info)
        #factory_info_bytes = create_string_buffer(info.encode('utf-8'), length)
        while True:

            message = {
                "x":x,
                "y":y
            }
            
            #masseage_b = json.dumps(message).encode('utf-8')
            message_b = json.dumps(message).encode('utf-8')
            # return rateを1 Hzに設定
            await client.write_gatt_char(CHARACTERISTIC_UUID,message_b,response=True)
            await asyncio.sleep(delay)

async def pygame_loop(delay):
    global x,y,r,g,b
    pygame.init() # 初期化
    screen = pygame.display.set_mode((120,120)) # ウィンドウサイズの指定
    pygame.display.set_caption("Pygame Test") # ウィンドウの上の方に出てくるアレの指定
    font = pygame.font.Font(None, 30)
    
    while(True):
        pygame.display.update()
        mouseX, mouseY = pygame.mouse.get_pos()
        text = font.render(f'{mouseX}, {mouseY}', True, (127,127,127))
        screen.fill((255, 255, 255))
        screen.blit(text, [0, 0])

        #pygame.display.update() # 画面更新
        x = mouseX
        y = mouseY

        hue = mouseX / 120
        lightness = mouseY / 120
        saturation = 1.0

        rTemp,gTemp,bTemp = colorsys.hls_to_rgb(hue,lightness,saturation)
        r = round(255*rTemp)
        g = round(255*gTemp)
        b = round(255*bTemp)

        pygame.draw.line(screen, (r,g,b), (mouseX,0), (mouseX,120), 1)
        pygame.draw.line(screen, (r,g,b), (0,mouseY), (120,mouseY), 1)
        pygame.display.flip()

        for event in pygame.event.get(): # 終了処理
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        await asyncio.sleep(delay)

async def main():


    task1 = asyncio.create_task(my_loop(1, 'hello'))
    task2 = asyncio.create_task(my_loop(2, 'world'))
    task2 = asyncio.create_task(my_loop(2, 'world'))
    task3 = asyncio.create_task(pygame_loop(0.02))
    task4 = asyncio.create_task(ble_bytes_reconnect(address,0.02))


    print(f"started at {time.strftime('%X')}")

    await task1

    print(f"returned from await task1 at {time.strftime('%X')}")

    await task2
    await task3

    print(f"finished at {time.strftime('%X')}")
    #asyncio.run(run(renderer="vispy",frame_rate=20))

asyncio.run(main())
