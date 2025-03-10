from uQR import QRCode
import random
import math
import time
import utime
from machine import Pin, SoftSPI, PWM
import st7789py as st7789

import vga1_16x32 as font


spi = SoftSPI(
    baudrate=20000000,
    polarity=1,
    phase=0,
    sck=Pin(18),
    mosi=Pin(19),
    miso=Pin(13))

tft = st7789.ST7789(
    spi,
    135,
    240,
    reset=Pin(23, Pin.OUT),
    cs=Pin(5, Pin.OUT),
    dc=Pin(16, Pin.OUT),
    backlight=Pin(4, Pin.OUT),
    rotation=4)


def main():
    

    tft.fill(st7789.BLACK)      # clear screen
    
    # PWM을 사용하여 백라이트 밝기 조절
    pwm_backlight = PWM(tft.backlight)  # 백라이트 핀을 PWM으로 설정
    pwm_backlight.freq(1000)  # PWM 주파수 설정 (1 kHz)
    pwm_backlight.duty(512)  # 밝기 값 조정 (0-1023, 512은 절반 밝기)
    

    tft.text(
            font,
            "Micro",
            20,10,
            st7789.WHITE,
            st7789.BLACK)
    tft.text(
            font,
            "ESP32",
            36,40,
            st7789.WHITE,
            st7789.BLACK)
    
    while True:
        drawQRCode()
        time.sleep(5)



def drawQRCode():

    # (0, 30)부터 시작하여 블랙으로 채우기
    tft.fill_rect(0, 80, 135, 210-70, st7789.BLACK)  
    
    # 현재 Unix 타임스탬프 얻기
    timestamp = utime.time()

    print("Timestamp:", timestamp)

    # 숫자형 timestamp를 문자열로 변환
    timestamp_str = str(timestamp)

    # 30자 길이로 0을 왼쪽에 채우기 (필요한 만큼 0을 추가)
    timestamp_padded = '0' * (30 - len(timestamp_str)) + timestamp_str
    
    # 결과 출력
    print("Padded Timestamp:", timestamp_padded)


    qr = QRCode()
    qr.add_data(timestamp_padded)
    qr_image  = qr.get_matrix()
          
      # 배율 설정
    scale = 4  # QR 코드 확대 배율 (2, 3, 4 등으로 설정 가능)

 
    # 여백 조정 (상단과 좌측 여백을 10 픽셀로 설정)
    x_offset = -4  # 좌측 여백
    y_offset = 80  # 상단 여백

    # QR 코드 화면에 출력 (세로 모드로 출력, 배율 적용)
    for y in range(len(qr_image)):
        for x in range(len(qr_image[y])):
            if qr_image[y][x]:
                # 배율 적용하여 각 픽셀 크기 확대
                for dy in range(scale):
                    for dx in range(scale):
                        if (y * scale + dy + y_offset) < 240 and (x * scale + dx + x_offset) < 135:
                            tft.pixel(x * scale + dx + x_offset, y * scale + dy + y_offset, st7789.BLACK)  # 검정색 픽셀 출력
            else:
                # 배율 적용하여 각 픽셀 크기 확대
                for dy in range(scale):
                    for dx in range(scale):
                        if (y * scale + dy + y_offset) < 240 and (x * scale + dx + x_offset) < 135:
                            tft.pixel(x * scale + dx + x_offset, y * scale + dy + y_offset, st7789.WHITE)  # 흰색 배경 출력

        
main()
