from machine import Pin, I2C
import ssd1306
import gfx
from time import sleep
import framebuf

from v2.helpers import load_buffer_from_pbm

pin_blue = Pin(4, Pin.IN)
pin_red = Pin(5, Pin.IN)

i2c = I2C(scl=Pin(2), sda=Pin(0), freq=100000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# oled = ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x27)
graphics = gfx.GFX(128, 64, oled.pixel)
oled.poweron()
oled.init_display()
oled.fill(0)

oled.show()


def blue_click():
    if status["is_jumpfinish"]:
        status["is_jump"] = True
        status["is_jumpfinish"] = False


def red_click():
    if status["game"] == "ready":
        status["game"] = "playing"
    elif status["game"] == "playing":
        status["game"] = "pause"
    elif status["game"] == "pause":
        status["game"] = "playing"
    elif (status["game"] == "gameover"):
        init_game_status()
        status["game"] = "playing"


def fire():
    pass


def status_constructor():
    s = dict()
    s["game"] = "loading"
    s["gametime"] = 0
    s["km"] = 0
    s["is_jump"] = False
    s["is_fire"] = False
    s["is_jumpfinish"] = True
    return s


status = status_constructor()


def player_constructor():
    p = dict()
    p["x"] = 10
    p["y"] = 44
    p["leg_status"] = "1"
    p['buffer_normal'] = load_buffer_from_pbm('player.pbm')
    p['buffer_foreleg_up'] = load_buffer_from_pbm('player1.pbm')
    p['buffer_aftleg_up'] = load_buffer_from_pbm('player2.pbm')
    p["buf"] = p['buffer_normal']
    return p


player = player_constructor()


def obstacle_constructor():
    obst = dict()
    obst["x"] = 130
    obst["y"] = 44
    obst["buf"] = load_buffer_from_pbm('cacti.pbm')
    return obst


obstacle = obstacle_constructor()


def background_constructor():
    b = dict()
    b["x"] = 0
    b["y"] = 53
    load_buffer_from_pbm('bg.pbm')
    return b


bg = background_constructor()
gameover_buf = load_buffer_from_pbm('gameover.pbm', wid=128, hgt=64)


def init_game_status():
    status["game"] = "loading"
    status["gametime"] = 0
    status["km"] = 0
    status["is_jump"] = False
    status["is_fire"] = False
    status["is_jumpfinish"] = True

    obstacle["x"] = 130
    obstacle["y"] = 44
    player["y"] = 44


def draw_player():
    # FIXME: jumping mechanism and player rendering are mixed together, do one and only one thing in a function.
    if status["is_jump"]:
        player["y"] -= 3
        oled.blit(player['buffer_normal'], player["x"], player["y"])
        if player["y"] < 15:
            status["is_jump"] = False
    else:
        player["buf"] = player['buffer_foreleg_up']
        player["y"] += 3

        if player["y"] >= 43:
            player["y"] = 43
            status["is_jumpfinish"] = True
        if player["leg_status"] == "1":
            oled.blit(player['buffer_foreleg_up'], player["x"], player["y"])
            player["leg_status"] = "2"
        elif player["leg_status"] == "2":
            oled.blit(player['buffer_aftleg_up'], player["x"], player["y"])
            player["leg_status"] = "1"


def draw_obstacle():
    # FIXME: obstacle scrolling mechanism and rendering are mixed together, do one and only one thing in a function.
    obstacle["x"] -= 4

    oled.blit(obstacle["buf"], obstacle["x"], obstacle["y"])

    if obstacle["x"] <= -10:
        obstacle["x"] = 130


def draw_bg():
    # FIXME: background scrolling mechanism and rendering are mixed together, do one and only one thing in a function.
    bg["x"] -= 4

    oled.blit(bg["buf"], bg["x"], bg["y"])
    oled.text("{0} km".format(status["km"]), 2, 0)
    if bg["x"] <= -10:
        bg["x"] = 0


def update_gameover_status():
    if obstacle["x"] - player["x"] < 15 and obstacle["y"] - player["y"] < 15:
        status["game"] = "gameover"


while True:
    oled.fill(0)
    oled.contrast(1)

    blue = pin_blue.value()
    red = pin_red.value()

    # FIXME: need a key binding mechanism even a input adapter.
    # FIXME: use separated functions for game life span control.
    if pin_red.value() == 1:
        red_click()
    if status["game"] == "loading":
        oled.text("loading.".format(status["km"]), 10, 30)
        oled.show()
        sleep(1)
        oled.text("loading..".format(status["km"]), 10, 30)
        oled.show()
        sleep(1)
        oled.text("loading...".format(status["km"]), 10, 30)
        oled.show()
        status["game"] = "ready"
    elif status["game"] == "ready":
        oled.text("> play".format(status["km"]), 10, 20)
        oled.text("code by".format(status["km"]), 10, 30)
        oled.text("cr4fun".format(status["km"]), 10, 40)
    elif status["game"] == "pause":
        oled.text("pause", 25, 30)
    elif status["game"] == "playing":
        if pin_blue.value() == 1:
            blue_click()
        status["km"] += 1
        status["gametime"] += 1
        # graphics.line(0, 63, 127, 63, 1)
        draw_bg()
        draw_player()
        draw_obstacle()
        update_gameover_status()
    elif status["game"] == "gameover":
        oled.text("{0} km".format(status["km"]), 2, 0)
        # oled.text("game over",25,30)
        oled.blit(gameover_buf, 0, 25)
    oled.show()
