import math
import os
import random
import struct
import sys
import pygame

# -----------------------------------------------------------------------------
# ИНИЦИАЛИЗАЦИЯ И НАСТРОЙКИ
# -----------------------------------------------------------------------------
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)

WIDTH, HEIGHT = 980, 690
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PIZZA RUSH - F1 Master Edition")
CLOCK = pygame.time.Clock()

# Дизайнерская Цветовая Палитра
COLOR_BG = (22, 19, 23)
COLOR_COUNTER = (55, 38, 30)
COLOR_COUNTER_TOP = (78, 54, 42)
COLOR_PANEL = (34, 29, 36)
COLOR_PANEL_LIGHT = (48, 42, 52)
COLOR_CARD = (42, 36, 45)

COLOR_TEXT = (245, 240, 235)
COLOR_TEXT_DIM = (170, 160, 175)
COLOR_GOLD = (255, 200, 55)
COLOR_GREEN = (46, 204, 113)
COLOR_GREEN_DARK = (30, 130, 72)
COLOR_RED = (231, 76, 60)
COLOR_BLUE = (52, 152, 219)
COLOR_PURPLE = (155, 89, 182)

TOPPING_DATA = {
    "pepperoni": {"name": "Пепперони", "color": (210, 50, 40)},
    "mushrooms": {"name": "Грибы", "color": (195, 175, 155)},
    "olives": {"name": "Оливки", "color": (40, 40, 40)},
    "basil": {"name": "Базилик", "color": (46, 170, 60)},
    "tomatoes": {"name": "Томаты", "color": (235, 75, 45)},
}

MYSTERY_RIDDLES = [
    {"text": "«Только красное и зелёное!»", "sauce": "red", "toppings": ["pepperoni", "basil"]},
    {"text": "«Белая классика с оливками!»", "sauce": "white", "toppings": ["olives"]},
    {"text": "«Огородная с грибами и томатами»", "sauce": "red", "toppings": ["mushrooms", "tomatoes"]},
]

# -----------------------------------------------------------------------------
# ЗВУКИ И F1 THEME
# -----------------------------------------------------------------------------
def create_sound(sound_type):
    sample_rate = 22050
    duration = 0.18
    n_samples = int(sample_rate * duration)
    samples = bytearray()

    for i in range(n_samples):
        t = i / sample_rate
        env = 1.0 - (i / n_samples)

        if sound_type == "click":
            freq = 480 + 300 * t
            val = math.sin(2 * math.pi * freq * t)
        elif sound_type == "cash":
            freq = 880 if i % 1800 < 900 else 1320
            val = math.sin(2 * math.pi * freq * t)
        elif sound_type == "bake":
            freq = 220 + math.sin(i * 0.05) * 40
            val = math.sin(2 * math.pi * freq * t)
        elif sound_type == "fail":
            freq = 170 - 70 * t
            val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
        elif sound_type == "buy":
            freq = 523 + (t * 800)
            val = math.sin(2 * math.pi * freq * t)
        elif sound_type == "slice":
            freq = 1100 - 700 * t
            val = (1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0)
        elif sound_type == "drink":
            freq = 320 + math.sin(i * 0.1) * 60
            val = math.sin(2 * math.pi * freq * t)
        else:
            val = 0.0

        int_val = max(-32768, min(32767, int(val * env * 10000)))
        packed = struct.pack("<h", int_val)
        samples.extend(packed)
        samples.extend(packed)

    try:
        return pygame.mixer.Sound(buffer=bytes(samples))
    except Exception:
        return None


def generate_f1_theme_procedural():
    sample_rate = 22050
    bpm = 138
    beat_dur = 60.0 / bpm

    melody = [
        (293.66, 0.5), (293.66, 0.5), (293.66, 0.5), (349.23, 0.5),
        (392.00, 0.5), (440.00, 0.5), (523.25, 0.75), (587.33, 1.25),
        (698.46, 0.5), (587.33, 0.5), (523.25, 0.5), (440.00, 0.5),
        (392.00, 0.5), (349.23, 0.5), (293.66, 1.0), (293.66, 1.0)
    ]

    total_time = sum(dur * beat_dur for _, dur in melody)
    n_samples = int(sample_rate * total_time)
    samples = bytearray()

    current_sample = 0
    for freq, dur in melody:
        note_samples = int(sample_rate * (dur * beat_dur))
        for i in range(note_samples):
            t = current_sample / sample_rate
            note_t = i / sample_rate
            env = max(0.0, 1.0 - (note_t / (dur * beat_dur)))
            
            synth_wave = (2.0 * ((freq * t) % 1.0) - 1.0) * 0.25
            sq_wave = (1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0) * 0.15
            lead_val = (synth_wave + sq_wave) * env * 0.12

            bass_freq = 146.83 if (int(t * 4) % 2 == 0) else 110.00
            bass_val = (1.0 if math.sin(2 * math.pi * bass_freq * t) > 0 else -1.0) * 0.05

            total = lead_val + bass_val
            int_val = max(-32768, min(32767, int(total * 2000)))  # Комфортная тихая громкость
            packed = struct.pack("<h", int_val)
            samples.extend(packed)
            samples.extend(packed)
            current_sample += 1

    try:
        return pygame.mixer.Sound(buffer=bytes(samples))
    except Exception:
        return None


def setup_background_music():
    for ext in ["mp3", "wav", "ogg"]:
        filename = f"f1_theme.{ext}"
        if os.path.exists(filename):
            try:
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.18)
                return
            except Exception:
                pass

    f1_synth = generate_f1_theme_procedural()
    if f1_synth:
        f1_synth.play(loops=-1)


SOUNDS = {
    "click": create_sound("click"),
    "cash": create_sound("cash"),
    "bake": create_sound("bake"),
    "fail": create_sound("fail"),
    "buy": create_sound("buy"),
    "slice": create_sound("slice"),
    "drink": create_sound("drink"),
}

setup_background_music()


def play_sound(name):
    if SOUNDS.get(name):
        SOUNDS[name].play()


# -----------------------------------------------------------------------------
# ЧАСТИЦЫ И ЭФФЕКТЫ
# -----------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.2, 1.2)
        self.vy = random.uniform(-2.0, -0.5)
        self.color = color
        self.alpha = 255
        self.radius = random.randint(3, 7)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 5
        self.radius = max(1, self.radius - 0.06)

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, max(0, int(self.alpha)))
            pygame.draw.circle(s, color_with_alpha, (self.radius, self.radius), self.radius)
            surface.blit(s, (self.x - self.radius, self.y - self.radius))


class FloatingText:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 255
        self.font = pygame.font.SysFont("Arial", 22, bold=True)

    def update(self):
        self.y -= 1.3
        self.alpha -= 4.5

    def draw(self, surface):
        if self.alpha > 0:
            txt_surface = self.font.render(self.text, True, self.color)
            txt_surface.set_alpha(max(0, self.alpha))
            surface.blit(txt_surface, (self.x, self.y))


# -----------------------------------------------------------------------------
# КЛИЕНТ
# -----------------------------------------------------------------------------
class Customer:
    def __init__(self, x, y, max_patience_bonus=0):
        self.x = x
        self.y = y
        self.ctype = random.choice(["normal", "normal", "vip", "mystery"])
        self.skin_color = random.choice([(255, 219, 172), (240, 184, 135), (224, 172, 105), (141, 85, 36)])
        self.hair_color = random.choice([(30, 20, 15), (180, 90, 30), (220, 180, 50), (100, 50, 20)])
        self.hair_style = random.choice(["short", "curly", "long"])
        self.shirt_color = (255, 200, 50) if self.ctype == "vip" else random.choice([(210, 60, 60), (50, 130, 210), (50, 180, 90)])
        
        self.max_patience = (80.0 if self.ctype == "vip" else 100.0) + max_patience_bonus
        self.patience = self.max_patience

        self.dough = random.choice(["thin", "fluffy"])
        self.sauce = random.choice(["red", "white"])
        self.toppings = random.sample(list(TOPPING_DATA.keys()), random.randint(1, 3))
        self.slices = random.choice([4, 6])
        self.wants_drink = random.choice([True, False])

        self.riddle_text = ""
        if self.ctype == "mystery":
            riddle = random.choice(MYSTERY_RIDDLES)
            self.riddle_text = riddle["text"]
            self.sauce = riddle["sauce"]
            self.toppings = riddle["toppings"]

    def update(self, dt):
        decay = 4.8 if self.ctype == "vip" else 3.2
        self.patience -= dt * decay

    def draw(self, surface):
        cx, cy = self.x, self.y

        # Облако заказа
        bubble_w, bubble_h = 270, 100
        bx, by = cx + 50, cy - 105
        
        # Тень и корпус карточки
        pygame.draw.rect(surface, (15, 12, 18), (bx + 4, by + 4, bubble_w, bubble_h), border_radius=14)
        pygame.draw.rect(surface, COLOR_CARD, (bx, by, bubble_w, bubble_h), border_radius=14)
        pygame.draw.rect(surface, COLOR_PANEL_LIGHT, (bx, by, bubble_w, bubble_h), 2, border_radius=14)
        pygame.draw.polygon(surface, COLOR_CARD, [(cx + 25, cy - 25), (bx + 10, cy - 18), (bx + 25, cy - 8)])

        font_sm = pygame.font.SysFont("Arial", 13, bold=True)

        if self.ctype == "vip":
            txt_title = font_sm.render("★ VIP КЛИЕНТ (2x Чаевые) ★", True, COLOR_GOLD)
            surface.blit(txt_title, (bx + 12, by + 8))
        elif self.ctype == "mystery":
            txt_title = font_sm.render("❓ ЗАГАДОЧНЫЙ ЗАКАЗ", True, COLOR_PURPLE)
            surface.blit(txt_title, (bx + 12, by + 8))
        else:
            txt_title = font_sm.render("Заказ клиента:", True, COLOR_TEXT_DIM)
            surface.blit(txt_title, (bx + 12, by + 8))

        if self.ctype == "mystery":
            txt_r = font_sm.render(self.riddle_text, True, COLOR_TEXT)
            surface.blit(txt_r, (bx + 12, by + 32))
            txt_sl = font_sm.render(f"Нарезать на: {self.slices} кусков!", True, COLOR_RED)
            surface.blit(txt_sl, (bx + 12, by + 56))
        else:
            d_str = "Тонкое" if self.dough == "thin" else "Пышное"
            s_str = "Красный" if self.sauce == "red" else "Белый"
            top_str = ", ".join([TOPPING_DATA[t]["name"] for t in self.toppings])
            txt_spec = font_sm.render(f"{d_str} тесто, {s_str} соус", True, COLOR_TEXT)
            surface.blit(txt_spec, (bx + 12, by + 28))
            txt_top = font_sm.render(f"Начинка: {top_str}", True, COLOR_GOLD)
            surface.blit(txt_top, (bx + 12, by + 48))

            dr_str = "+ Кола" if self.wants_drink else ""
            txt_extra = font_sm.render(f"Нарезать: {self.slices} кусков {dr_str}", True, COLOR_BLUE)
            surface.blit(txt_extra, (bx + 12, by + 68))

        # Персонаж
        pygame.draw.ellipse(surface, self.shirt_color, (cx - 50, cy + 30, 100, 70))
        pygame.draw.rect(surface, self.skin_color, (cx - 12, cy + 15, 24, 22))
        pygame.draw.circle(surface, self.skin_color, (cx, cy), 35)

        if self.ctype == "vip":
            pygame.draw.polygon(surface, COLOR_GOLD, [(cx - 20, cy - 35), (cx - 10, cy - 52), (cx, cy - 38), (cx + 10, cy - 52), (cx + 20, cy - 35)])

        if self.hair_style == "short":
            pygame.draw.ellipse(surface, self.hair_color, (cx - 36, cy - 42, 72, 32))
        elif self.hair_style == "curly":
            for ox in [-25, -12, 0, 12, 25]:
                pygame.draw.circle(surface, self.hair_color, (cx + ox, cy - 28), 14)
        elif self.hair_style == "long":
            pygame.draw.ellipse(surface, self.hair_color, (cx - 38, cy - 42, 76, 36))
            pygame.draw.rect(surface, self.hair_color, (cx - 38, cy - 20, 14, 50))
            pygame.draw.rect(surface, self.hair_color, (cx + 24, cy - 20, 14, 50))

        # Глаза
        pygame.draw.circle(surface, (255, 255, 255), (cx - 12, cy - 4), 7)
        pygame.draw.circle(surface, (255, 255, 255), (cx + 12, cy - 4), 7)
        pygame.draw.circle(surface, (20, 20, 20), (cx - 12, cy - 4), 3)
        pygame.draw.circle(surface, (20, 20, 20), (cx + 12, cy - 4), 3)

        # Рот
        ratio = self.patience / self.max_patience
        if ratio > 0.6:
            pygame.draw.arc(surface, (180, 40, 40), (cx - 12, cy + 2, 24, 18), math.pi, 2 * math.pi, 3)
        elif ratio > 0.3:
            pygame.draw.line(surface, (180, 40, 40), (cx - 10, cy + 14), (cx + 10, cy + 14), 3)
        else:
            pygame.draw.arc(surface, (180, 40, 40), (cx - 12, cy + 10, 24, 14), 0, math.pi, 3)

        # Полоса терпения
        bar_w, bar_h = 96, 9
        bar_x, bar_y = cx - bar_w // 2, cy - 58
        pygame.draw.rect(surface, (30, 25, 35), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
        fill_w = int(bar_w * (max(0, self.patience) / self.max_patience))
        bar_color = COLOR_GREEN if ratio > 0.5 else (COLOR_GOLD if ratio > 0.25 else COLOR_RED)
        if fill_w > 0:
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_w, bar_h), border_radius=5)


# -----------------------------------------------------------------------------
# ИГРОВАЯ ПИЦЦА
# -----------------------------------------------------------------------------
class Pizza:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 85
        self.dough = "thin"
        self.sauce = None
        self.toppings = []
        self.bake_level = 0.0
        self.baked = False
        self.cuts = 0

    def add_topping(self, topping_type):
        if len(self.toppings) < 8 and not self.baked and self.sauce:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(10, self.radius - 25)
            ox = math.cos(angle) * dist
            oy = math.sin(angle) * dist
            self.toppings.append({"type": topping_type, "ox": ox, "oy": oy})
            play_sound("click")

    def slice_pizza(self):
        """Переключает количество разрезов пиццы: 0 -> 4 -> 6 -> 0"""
        if self.cuts == 0:
            self.cuts = 4
        elif self.cuts == 4:
            self.cuts = 6
        else:
            self.cuts = 0
        play_sound("slice")

    def draw(self, surface):
        rad = self.radius + 8 if self.dough == "fluffy" else self.radius

        if self.bake_level < 0.2:
            crust_color, cheese_color = (225, 190, 140), (245, 220, 150)
        elif self.bake_level <= 1.2:
            crust_color, cheese_color = (195, 130, 60), (255, 200, 70)
        else:
            crust_color, cheese_color = (60, 40, 35), (100, 80, 50)

        pygame.draw.circle(surface, crust_color, (self.x, self.y), rad)

        if self.sauce == "red":
            pygame.draw.circle(surface, (185, 45, 35), (self.x, self.y), rad - 8)
            pygame.draw.circle(surface, cheese_color, (self.x, self.y), rad - 14)
        elif self.sauce == "white":
            pygame.draw.circle(surface, (240, 235, 215), (self.x, self.y), rad - 8)
            pygame.draw.circle(surface, cheese_color, (self.x, self.y), rad - 14)

        for item in self.toppings:
            tx, ty = self.x + item["ox"], self.y + item["oy"]
            color = TOPPING_DATA[item["type"]]["color"]

            if item["type"] == "pepperoni":
                pygame.draw.circle(surface, color, (tx, ty), 12)
            elif item["type"] == "mushrooms":
                pygame.draw.ellipse(surface, color, (tx - 8, ty - 6, 16, 12))
            elif item["type"] == "olives":
                pygame.draw.circle(surface, color, (tx, ty), 7)
                pygame.draw.circle(surface, cheese_color, (tx, ty), 3)
            elif item["type"] == "basil":
                pygame.draw.ellipse(surface, color, (tx - 8, ty - 4, 16, 8))
            elif item["type"] == "tomatoes":
                pygame.draw.circle(surface, color, (tx, ty), 10)

        # Линии разреза
        if self.cuts >= 4:
            pygame.draw.line(surface, (30, 20, 15), (self.x - rad, self.y), (self.x + rad, self.y), 3)
            pygame.draw.line(surface, (30, 20, 15), (self.x, self.y - rad), (self.x, self.y + rad), 3)
        if self.cuts == 6:
            pygame.draw.line(surface, (30, 20, 15), (self.x - rad * 0.7, self.y - rad * 0.7), (self.x + rad * 0.7, self.y + rad * 0.7), 3)
            pygame.draw.line(surface, (30, 20, 15), (self.x - rad * 0.7, self.y + rad * 0.7), (self.x + rad * 0.7, self.y - rad * 0.7), 3)


# -----------------------------------------------------------------------------
# ИГРОВОЙ МЕНЕДЖЕР
# -----------------------------------------------------------------------------
class PizzaRushGame:
    def __init__(self):
        self.state = "MENU"
        self.init_game_data()

        # Элементы интерфейса
        self.dough_btn = pygame.Rect(440, 320, 145, 42)
        self.sauce_red_btn = pygame.Rect(440, 372, 145, 42)
        self.sauce_white_btn = pygame.Rect(440, 424, 145, 42)
        self.drink_btn = pygame.Rect(440, 476, 145, 42)
        self.slice_btn = pygame.Rect(440, 528, 145, 42)

        self.topping_buttons = []
        for i, (key, data) in enumerate(TOPPING_DATA.items()):
            btn_rect = pygame.Rect(730, 310 + i * 52, 220, 44)
            self.topping_buttons.append({"key": key, "rect": btn_rect, "data": data})

        self.bake_btn = pygame.Rect(600, 600, 160, 52)
        self.serve_btn = pygame.Rect(780, 600, 160, 52)
        self.shop_in_game_btn = pygame.Rect(840, 12, 120, 40)

        # Главное меню / Кнопки
        self.btn_start = pygame.Rect(360, 260, 260, 58)
        self.btn_shop = pygame.Rect(360, 335, 260, 58)
        self.btn_exit = pygame.Rect(360, 410, 260, 58)
        self.btn_back_menu = pygame.Rect(50, 600, 200, 50)
        self.btn_next_day = pygame.Rect(390, 520, 200, 52)
        self.btn_restart = pygame.Rect(370, 440, 240, 58)

        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)

    def init_game_data(self):
        self.score = 200
        self.day = 1
        self.time_of_day = 9.0
        self.rent = 180

        self.daily_served = 0
        self.daily_revenue = 0
        self.combo = 0

        self.shake_timer = 0.0
        self.oven_broken = False
        self.oven_fix_clicks = 0

        self.has_drink = False

        self.upgrades = {
            "patience": {"name": "Терпение клиентов", "level": 0, "max": 5, "cost": 150},
            "oven_speed": {"name": "Скорость печи", "level": 0, "max": 5, "cost": 200},
            "tips": {"name": "Щедрые чаевые", "level": 0, "max": 5, "cost": 250},
        }

        self.pizza = Pizza(280, 460)
        self.customer = Customer(480, 160)
        self.particles = []
        self.floaters = []
        self.in_oven = False

    def trigger_shake(self):
        self.shake_timer = 0.35

    def run(self):
        running = True
        while running:
            dt = CLOCK.tick(60) / 1000.0

            if self.shake_timer > 0:
                self.shake_timer -= dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mpos = event.pos
                    if self.state == "MENU":
                        self.handle_menu_click(mpos)
                    elif self.state == "GAME":
                        self.handle_game_click(mpos)
                    elif self.state == "SHOP":
                        self.handle_shop_click(mpos)
                    elif self.state == "DAY_SUMMARY":
                        if self.btn_next_day.collidepoint(mpos):
                            self.start_next_day()
                    elif self.state == "GAME_OVER":
                        if self.btn_restart.collidepoint(mpos):
                            play_sound("click")
                            self.init_game_data()
                            self.state = "GAME"

            if self.state == "GAME":
                self.update_game(dt)

            self.draw()

        pygame.quit()
        sys.exit()

    def handle_menu_click(self, pos):
        if self.btn_start.collidepoint(pos):
            play_sound("click")
            self.state = "GAME"
        elif self.btn_shop.collidepoint(pos):
            play_sound("click")
            self.state = "SHOP"
        elif self.btn_exit.collidepoint(pos):
            pygame.quit()
            sys.exit()

    def handle_game_click(self, pos):
        if self.oven_broken:
            oven_rect = pygame.Rect(50, 310, 130, 130)
            if oven_rect.collidepoint(pos):
                self.oven_fix_clicks += 1
                play_sound("click")
                if self.oven_fix_clicks >= 4:
                    self.oven_broken = False
                    self.floaters.append(FloatingText("Печь починена!", 110, 300, COLOR_GREEN))
            return

        for btn in self.topping_buttons:
            if btn["rect"].collidepoint(pos):
                self.pizza.add_topping(btn["key"])

        if self.dough_btn.collidepoint(pos) and not self.pizza.baked:
            self.pizza.dough = "fluffy" if self.pizza.dough == "thin" else "thin"
            play_sound("click")

        if self.sauce_red_btn.collidepoint(pos) and not self.pizza.baked:
            self.pizza.sauce = "red"
            play_sound("click")
        elif self.sauce_white_btn.collidepoint(pos) and not self.pizza.baked:
            self.pizza.sauce = "white"
            play_sound("click")

        if self.drink_btn.collidepoint(pos):
            self.has_drink = not self.has_drink
            play_sound("drink")

        # КНОПКА НАРЕЗКИ ПИЦЦЫ
        if self.slice_btn.collidepoint(pos):
            self.pizza.slice_pizza()

        if self.bake_btn.collidepoint(pos) and not self.in_oven:
            if self.pizza.sauce:
                self.in_oven = True
                play_sound("bake")

        if self.serve_btn.collidepoint(pos):
            self.serve_pizza()

        if self.shop_in_game_btn.collidepoint(pos):
            play_sound("click")
            self.state = "SHOP"

    def handle_shop_click(self, pos):
        if self.btn_back_menu.collidepoint(pos):
            play_sound("click")
            self.state = "GAME"

        for i, (key, item) in enumerate(self.upgrades.items()):
            btn_rect = pygame.Rect(670, 180 + i * 90, 160, 45)
            if btn_rect.collidepoint(pos):
                if item["level"] < item["max"] and self.score >= item["cost"]:
                    self.score -= item["cost"]
                    item["level"] += 1
                    item["cost"] = int(item["cost"] * 1.6)
                    play_sound("buy")

    def update_game(self, dt):
        self.time_of_day += dt * 0.15
        if self.time_of_day >= 21.0:
            self.end_day()
            return

        if self.in_oven and not self.oven_broken and random.random() < 0.002:
            self.oven_broken = True
            self.oven_fix_clicks = 0
            self.trigger_shake()
            play_sound("fail")

        self.customer.update(dt)

        if self.in_oven and not self.oven_broken:
            speed_mult = 1.0 + (self.upgrades["oven_speed"]["level"] * 0.35)
            self.pizza.bake_level += dt * 0.45 * speed_mult
            self.pizza.baked = True
            if random.random() < 0.4:
                self.particles.append(Particle(self.pizza.x + random.randint(-40, 40), self.pizza.y, (220, 220, 220)))

        for p in self.particles[:]:
            p.update()
            if p.alpha <= 0:
                self.particles.remove(p)

        for f in self.floaters[:]:
            f.update()
            if f.alpha <= 0:
                self.floaters.remove(f)

        if self.customer.patience <= 0:
            play_sound("fail")
            self.combo = 0
            self.trigger_shake()
            self.floaters.append(FloatingText("Клиент ушел!", 430, 160, COLOR_RED))
            self.reset_customer()

    def serve_pizza(self):
        c = self.customer
        p = self.pizza

        pizza_toppings = [t["type"] for t in p.toppings]
        correct_toppings = set(pizza_toppings) == set(c.toppings)
        correct_dough = p.dough == c.dough
        correct_sauce = p.sauce == c.sauce
        correct_slices = p.cuts == c.slices
        correct_drink = self.has_drink == c.wants_drink
        correct_bake = 0.8 <= p.bake_level <= 1.35

        is_perfect = correct_toppings and correct_dough and correct_sauce and correct_slices and correct_drink and correct_bake

        if is_perfect:
            self.combo += 1
            combo_mult = 2.0 if self.combo >= 3 else 1.0
            vip_mult = 2.0 if c.ctype == "vip" else 1.0
            tip_mult = 1.0 + (self.upgrades["tips"]["level"] * 0.3)

            base_reward = 180 + int(c.patience)
            reward = int(base_reward * combo_mult * vip_mult * tip_mult)

            self.score += reward
            self.daily_revenue += reward
            self.daily_served += 1
            play_sound("cash")

            msg = "ИДЕАЛЬНО! (F1 RUSH!)" if self.combo >= 3 else "ОТЛИЧНО!"
            self.floaters.append(FloatingText(f"+${reward} {msg}", 400, 140, COLOR_GOLD))
            for _ in range(20):
                self.particles.append(Particle(480, 160, COLOR_GOLD))
        else:
            play_sound("fail")
            self.combo = 0
            self.trigger_shake()
            penalty = 60
            self.score = max(0, self.score - penalty)
            self.floaters.append(FloatingText(f"-${penalty} Ошибка в заказе!", 380, 140, COLOR_RED))

        self.reset_customer()

    def reset_customer(self):
        patience_bonus = self.upgrades["patience"]["level"] * 25
        self.customer = Customer(480, 160, max_patience_bonus=patience_bonus)
        self.pizza = Pizza(280, 460)
        self.in_oven = False
        self.has_drink = False

    def end_day(self):
        self.state = "DAY_SUMMARY"

    def start_next_day(self):
        self.score -= self.rent
        if self.score < 0:
            self.state = "GAME_OVER"
            return

        self.day += 1
        self.time_of_day = 9.0
        self.rent += 50
        self.daily_served = 0
        self.daily_revenue = 0
        self.reset_customer()
        self.state = "GAME"

    # --- ОТРИСОВКА И ДИЗАЙН ---
    def draw(self):
        ox = random.randint(-4, 4) if self.shake_timer > 0 else 0
        oy = random.randint(-4, 4) if self.shake_timer > 0 else 0

        temp_surface = pygame.Surface((WIDTH, HEIGHT))

        if self.state == "MENU":
            self.draw_menu(temp_surface)
        elif self.state == "GAME":
            self.draw_game(temp_surface)
        elif self.state == "SHOP":
            self.draw_shop(temp_surface)
        elif self.state == "DAY_SUMMARY":
            self.draw_day_summary(temp_surface)
        elif self.state == "GAME_OVER":
            self.draw_game_over(temp_surface)

        SCREEN.blit(temp_surface, (ox, oy))
        pygame.display.flip()

    def draw_menu(self, surface):
        surface.fill(COLOR_BG)
        title = self.title_font.render("PIZZA RUSH - F1 SPEED", True, COLOR_GOLD)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 140))

        for btn, text, col in [
            (self.btn_start, "ИГРАТЬ", COLOR_GREEN_DARK),
            (self.btn_shop, "МАГАЗИН", COLOR_BLUE),
            (self.btn_exit, "ВЫХОД", COLOR_RED),
        ]:
            pygame.draw.rect(surface, col, btn, border_radius=12)
            pygame.draw.rect(surface, COLOR_TEXT, btn, 2, border_radius=12)
            txt_surf = self.font.render(text, True, COLOR_TEXT)
            surface.blit(txt_surf, (btn.x + (btn.width - txt_surf.get_width()) // 2, btn.y + 18))

    def draw_day_summary(self, surface):
        surface.fill(COLOR_BG)
        title = self.title_font.render(f"ИТОГИ ДНЯ {self.day}", True, COLOR_GOLD)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 70))

        card = pygame.Rect(210, 140, 560, 340)
        pygame.draw.rect(surface, COLOR_CARD, card, border_radius=16)
        pygame.draw.rect(surface, COLOR_PANEL_LIGHT, card, 2, border_radius=16)

        t1 = self.font.render(f"Выполнено заказов: {self.daily_served}", True, COLOR_TEXT)
        t2 = self.font.render(f"Выручка за день: +${self.daily_revenue}", True, COLOR_GREEN)
        t3 = self.font.render(f"Аренда помещения: -${self.rent}", True, COLOR_RED)
        net = self.daily_revenue - self.rent
        t4 = self.font.render(f"Чистая прибыль: ${net}", True, COLOR_GOLD if net >= 0 else COLOR_RED)
        t5 = self.font.render(f"Баланс после оплаты: ${self.score - self.rent}", True, COLOR_TEXT)

        surface.blit(t1, (250, 180))
        surface.blit(t2, (250, 230))
        surface.blit(t3, (250, 280))
        surface.blit(t4, (250, 330))
        surface.blit(t5, (250, 380))

        pygame.draw.rect(surface, COLOR_GREEN_DARK, self.btn_next_day, border_radius=12)
        pygame.draw.rect(surface, COLOR_GREEN, self.btn_next_day, 2, border_radius=12)
        btn_txt = self.font.render("СЛЕДУЮЩИЙ ДЕНЬ", True, COLOR_TEXT)
        surface.blit(btn_txt, (self.btn_next_day.x + 15, self.btn_next_day.y + 15))

    def draw_game_over(self, surface):
        surface.fill((18, 12, 14))
        
        # Заголовок
        t = self.title_font.render("GAME OVER - БАНКРОТ!", True, COLOR_RED)
        sub = self.font.render("Вы не смогли оплатить аренду заведения.", True, COLOR_TEXT_DIM)
        surface.blit(t, (WIDTH // 2 - t.get_width() // 2, 230))
        surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 300))

        # КНОПКА ПЕРЕЗАПУСКА
        pygame.draw.rect(surface, COLOR_GREEN_DARK, self.btn_restart, border_radius=14)
        pygame.draw.rect(surface, COLOR_GREEN, self.btn_restart, 2, border_radius=14)
        btn_txt = self.font.render("НАЧАТЬ ЗАНОВО", True, COLOR_TEXT)
        surface.blit(btn_txt, (self.btn_restart.x + (self.btn_restart.width - btn_txt.get_width()) // 2, self.btn_restart.y + 18))

    def draw_shop(self, surface):
        surface.fill(COLOR_BG)
        title = self.title_font.render("МАГАЗИН УЛУЧШЕНИЙ", True, COLOR_GOLD)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        money_txt = self.font.render(f"Ваш Баланс: ${self.score}", True, COLOR_GOLD)
        surface.blit(money_txt, (WIDTH // 2 - money_txt.get_width() // 2, 100))

        for i, (key, item) in enumerate(self.upgrades.items()):
            card_rect = pygame.Rect(120, 160 + i * 95, 740, 78)
            pygame.draw.rect(surface, COLOR_CARD, card_rect, border_radius=12)
            pygame.draw.rect(surface, COLOR_PANEL_LIGHT, card_rect, 2, border_radius=12)

            name_txt = self.font.render(f"{item['name']} (Уровень {item['level']}/{item['max']})", True, COLOR_TEXT)
            surface.blit(name_txt, (card_rect.x + 24, card_rect.y + 26))

            buy_btn = pygame.Rect(670, card_rect.y + 16, 160, 46)
            if item["level"] < item["max"]:
                btn_col = COLOR_GREEN_DARK if self.score >= item["cost"] else (60, 60, 60)
                pygame.draw.rect(surface, btn_col, buy_btn, border_radius=10)
                btn_txt = self.font.render(f"${item['cost']}", True, COLOR_TEXT)
            else:
                pygame.draw.rect(surface, (70, 70, 70), buy_btn, border_radius=10)
                btn_txt = self.font.render("МАКС", True, COLOR_TEXT)

            surface.blit(btn_txt, (buy_btn.x + (buy_btn.width - btn_txt.get_width()) // 2, buy_btn.y + 13))

        pygame.draw.rect(surface, COLOR_PANEL_LIGHT, self.btn_back_menu, border_radius=12)
        back_txt = self.font.render("В ИГРУ", True, COLOR_TEXT)
        surface.blit(back_txt, (self.btn_back_menu.x + 65, self.btn_back_menu.y + 14))

    def draw_game(self, surface):
        surface.fill(COLOR_BG)

        # Деревянный Прилавок
        pygame.draw.rect(surface, COLOR_COUNTER, (0, 250, WIDTH, HEIGHT - 250))
        pygame.draw.rect(surface, COLOR_COUNTER_TOP, (0, 250, WIDTH, 12))

        # Верхний стильный HUD
        pygame.draw.rect(surface, COLOR_PANEL, (0, 0, WIDTH, 65))
        pygame.draw.line(surface, COLOR_PANEL_LIGHT, (0, 65), (WIDTH, 65), 2)

        score_txt = self.title_font.render(f"${self.score}", True, COLOR_GOLD)
        surface.blit(score_txt, (24, 12))

        hours = int(self.time_of_day)
        mins = int((self.time_of_day - hours) * 60)
        time_str = f"День {self.day}   |   Время: {hours:02d}:{mins:02d}"
        time_txt = self.font.render(time_str, True, COLOR_TEXT)
        surface.blit(time_txt, (200, 22))

        if self.combo >= 3:
            combo_txt = self.font.render("🔥 F1 RUSH HOUR (x2) 🔥", True, COLOR_GOLD)
            surface.blit(combo_txt, (530, 22))

        pygame.draw.rect(surface, COLOR_BLUE, self.shop_in_game_btn, border_radius=8)
        sh_txt = self.font.render("Магазин", True, COLOR_TEXT)
        surface.blit(sh_txt, (self.shop_in_game_btn.x + 20, self.shop_in_game_btn.y + 9))

        # Клиент
        self.customer.draw(surface)

        # Пицца
        pygame.draw.circle(surface, (35, 30, 32), (self.pizza.x, self.pizza.y), 100)
        self.pizza.draw(surface)

        # Печь со свечением
        oven_rect = pygame.Rect(50, 310, 130, 130)
        pygame.draw.rect(surface, (30, 30, 30), oven_rect, border_radius=14)

        if self.in_oven and not self.oven_broken:
            pygame.draw.rect(surface, (255, 120, 30), oven_rect, border_radius=14)
            pygame.draw.rect(surface, COLOR_GOLD, oven_rect, 4, border_radius=14)
        else:
            pygame.draw.rect(surface, COLOR_RED if self.oven_broken else COLOR_PANEL_LIGHT, oven_rect, 4, border_radius=14)

        if self.oven_broken:
            ov_txt = self.font.render("ПОЛОМКА!", True, COLOR_RED)
            fix_txt = self.font.render("КЛИКАЙ!", True, COLOR_GOLD)
            surface.blit(ov_txt, (65, 340))
            surface.blit(fix_txt, (75, 370))
        else:
            ov_txt = self.font.render("ПЕЧЬ", True, COLOR_TEXT)
            surface.blit(ov_txt, (90, 320))
            bake_bar_rect = pygame.Rect(65, 395, 100, 12)
            pygame.draw.rect(surface, (20, 20, 20), bake_bar_rect, border_radius=4)
            bake_fill = min(100, int(100 * (self.pizza.bake_level / 1.5)))
            pygame.draw.rect(surface, COLOR_GOLD if self.pizza.bake_level <= 1.2 else COLOR_RED, (65, 395, bake_fill, 12), border_radius=4)

        # ПАНЕЛЬ ОПЦИЙ ПИЦЦЫ
        # Тесто
        pygame.draw.rect(surface, COLOR_PANEL_LIGHT if self.pizza.dough == 'fluffy' else COLOR_PANEL, self.dough_btn, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD if self.pizza.dough == 'fluffy' else COLOR_PANEL_LIGHT, self.dough_btn, 2, border_radius=8)
        d_lbl = self.font.render(f"Тесто: {'Пышное' if self.pizza.dough == 'fluffy' else 'Тонкое'}", True, COLOR_TEXT)
        surface.blit(d_lbl, (self.dough_btn.x + 10, self.dough_btn.y + 9))

        # Красный соус
        pygame.draw.rect(surface, COLOR_RED if self.pizza.sauce == 'red' else COLOR_PANEL, self.sauce_red_btn, border_radius=8)
        pygame.draw.rect(surface, COLOR_TEXT if self.pizza.sauce == 'red' else COLOR_PANEL_LIGHT, self.sauce_red_btn, 2, border_radius=8)
        sr_lbl = self.font.render("Красн. соус", True, COLOR_TEXT)
        surface.blit(sr_lbl, (self.sauce_red_btn.x + 10, self.sauce_red_btn.y + 9))

        # Белый соус
        pygame.draw.rect(surface, (230, 220, 200) if self.pizza.sauce == 'white' else COLOR_PANEL, self.sauce_white_btn, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD if self.pizza.sauce == 'white' else COLOR_PANEL_LIGHT, self.sauce_white_btn, 2, border_radius=8)
        sw_lbl = self.font.render("Белый соус", True, (20, 20, 20) if self.pizza.sauce == 'white' else COLOR_TEXT)
        surface.blit(sw_lbl, (self.sauce_white_btn.x + 10, self.sauce_white_btn.y + 9))

        # Кола
        pygame.draw.rect(surface, COLOR_BLUE if self.has_drink else COLOR_PANEL, self.drink_btn, border_radius=8)
        pygame.draw.rect(surface, COLOR_TEXT if self.has_drink else COLOR_PANEL_LIGHT, self.drink_btn, 2, border_radius=8)
        dr_lbl = self.font.render("Кола: Налита" if self.has_drink else "+ Налить Колу", True, COLOR_TEXT)
        surface.blit(dr_lbl, (self.drink_btn.x + 10, self.drink_btn.y + 9))

        # КНОПКА НАРЕЗКИ
        pygame.draw.rect(surface, COLOR_PURPLE if self.pizza.cuts > 0 else COLOR_PANEL, self.slice_btn, border_radius=8)
        pygame.draw.rect(surface, COLOR_TEXT if self.pizza.cuts > 0 else COLOR_PANEL_LIGHT, self.slice_btn, 2, border_radius=8)
        sl_lbl = self.font.render(f"Резать: {self.pizza.cuts}/6", True, COLOR_TEXT)
        surface.blit(sl_lbl, (self.slice_btn.x + 10, self.slice_btn.y + 9))

        # Кнопки Начинок
        for btn in self.topping_buttons:
            r = btn["rect"]
            pygame.draw.rect(surface, COLOR_PANEL, r, border_radius=8)
            pygame.draw.rect(surface, COLOR_PANEL_LIGHT, r, 2, border_radius=8)
            pygame.draw.rect(surface, btn["data"]["color"], (r.x + 12, r.y + 10, 24, 24), border_radius=6)
            t_txt = self.font.render(btn["data"]["name"], True, COLOR_TEXT)
            surface.blit(t_txt, (r.x + 48, r.y + 10))

        # Эффекты и тексты
        for p in self.particles:
            p.draw(surface)
        for f in self.floaters:
            f.draw(surface)

        # Главные Кнопки Действий
        pygame.draw.rect(surface, (210, 105, 30), self.bake_btn, border_radius=12)
        pygame.draw.rect(surface, COLOR_TEXT, self.bake_btn, 2, border_radius=12)
        bake_lbl = self.font.render("В ПЕЧЬ", True, COLOR_TEXT)
        surface.blit(bake_lbl, (self.bake_btn.x + 45, self.bake_btn.y + 14))

        pygame.draw.rect(surface, COLOR_GREEN_DARK, self.serve_btn, border_radius=12)
        pygame.draw.rect(surface, COLOR_GREEN, self.serve_btn, 2, border_radius=12)
        serve_lbl = self.font.render("ПОДАТЬ", True, COLOR_TEXT)
        surface.blit(serve_lbl, (self.serve_btn.x + 45, self.serve_btn.y + 14))


# -----------------------------------------------------------------------------
# ЗАПУСК
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    game = PizzaRushGame()
    game.run()