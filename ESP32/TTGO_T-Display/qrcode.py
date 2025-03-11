from uQR import QRCode
import time
import utime
from machine import Pin, SoftSPI, PWM
import st7789py as st7789
import framebuf
import gc

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

# QRCode 객체를 전역 변수로 생성하여 재사용
qr = QRCode()

def main():
    tft.fill(st7789.BLACK)  # 화면 초기화
    
    # PWM을 사용하여 백라이트 밝기 조절
    pwm_backlight = PWM(tft.backlight)  # 백라이트 핀을 PWM으로 설정
    pwm_backlight.freq(1000)  # PWM 주파수 설정 (1 kHz)
    pwm_backlight.duty(512)  # 밝기 값 조정 (0-1023, 512은 절반 밝기)
    
    tft.text(
            font,
            "Micro",
            20, 10,
            st7789.WHITE,
            st7789.BLACK)
    tft.text(
            font,
            "ESP32",
            36, 40,
            st7789.WHITE,
            st7789.BLACK)
    
    while True:
        try:
            drawQRCode()
        except MemoryError:
            print("메모리 부족으로 QR 코드 그리기 실패, 스킵합니다.")
        time.sleep(5)

def drawQRCode():
    timestamp = utime.time()
    timestamp_str = str(timestamp)
    timestamp_padded = '0' * (30 - len(timestamp_str)) + timestamp_str

    # QR 코드 데이터 설정
    qr.clear()  # 기존 데이터 지우기
    qr.add_data(timestamp_padded)
    qr.make()

    qr_image = qr.get_matrix()  # QR 코드 데이터 얻기
    qr_size = len(qr_image)  # QR 코드 크기

    # 배율 설정
    scale = 4  # 확대 배율
    img_size = qr_size * scale

    # 여백 설정
    x_offset = (135 - img_size) // 2  # 중앙 정렬
    y_offset = 80  # 상단 여백

    # 컬러 QR 코드를 위한 프레임버퍼 설정
    buffer_size = img_size * img_size * 2  # RGB565는 16비트(2바이트) 색상을 사용
    buffer = bytearray(buffer_size)
    fbuf = framebuf.FrameBuffer(buffer, img_size, img_size, framebuf.RGB565)

    # QR 코드 화면에 출력 (색상 적용)
    for y in range(qr_size):
        for x in range(qr_size):
            color = 0x0000 if qr_image[y][x] else 0xFFFF  # 검은색(0x0000) 또는 흰색(0xFFFF)
            fbuf.fill_rect(x * scale, y * scale, scale, scale, color)

    # fbuf에 그려진 이미지를 화면에 블릿
    tft.blit_buffer(fbuf, x_offset, y_offset, img_size, img_size)

    # 가비지 컬렉션 호출하여 메모리 회수
    gc.collect()

# 메인 함수 실행
main()

