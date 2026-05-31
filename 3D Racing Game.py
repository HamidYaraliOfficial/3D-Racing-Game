import sys
import math
import random
import time
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# ─── Translations ───────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "en": {
        "title": "3D Racing Game",
        "speed": "Speed",
        "score": "Score",
        "lap": "Lap",
        "best": "Best",
        "start": "START",
        "pause": "PAUSE",
        "resume": "RESUME",
        "restart": "RESTART",
        "settings": "SETTINGS",
        "language": "Language",
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
        "controls": "Controls: ← → Steer | ↑ Accelerate | ↓ Brake | SPACE Nitro",
        "game_over": "GAME OVER",
        "new_record": "NEW RECORD!",
        "km_h": "km/h",
        "nitro": "NITRO",
        "lives": "Lives",
        "level": "Level",
        "paused": "PAUSED",
        "press_start": "Press START to Play",
        "coins": "Coins",
    },
    "fa": {
        "title": "بازی ماشین سه‌بعدی",
        "speed": "سرعت",
        "score": "امتیاز",
        "lap": "دور",
        "best": "بهترین",
        "start": "شروع",
        "pause": "مکث",
        "resume": "ادامه",
        "restart": "شروع مجدد",
        "settings": "تنظیمات",
        "language": "زبان",
        "theme": "پوسته",
        "light": "روشن",
        "dark": "تاریک",
        "controls": "کنترل: ← → فرمان | ↑ گاز | ↓ ترمز | SPACE نیترو",
        "game_over": "بازی تمام شد",
        "new_record": "رکورد جدید!",
        "km_h": "کیلومتر/ساعت",
        "nitro": "نیترو",
        "lives": "جان",
        "level": "سطح",
        "paused": "مکث",
        "press_start": "برای شروع کلیک کنید",
        "coins": "سکه",
    },
    "zh": {
        "title": "3D赛车游戏",
        "speed": "速度",
        "score": "分数",
        "lap": "圈数",
        "best": "最佳",
        "start": "开始",
        "pause": "暂停",
        "resume": "继续",
        "restart": "重新开始",
        "settings": "设置",
        "language": "语言",
        "theme": "主题",
        "light": "浅色",
        "dark": "深色",
        "controls": "控制: ← → 转向 | ↑ 加速 | ↓ 刹车 | SPACE 氮气",
        "game_over": "游戏结束",
        "new_record": "新纪录！",
        "km_h": "公里/小时",
        "nitro": "氮气",
        "lives": "生命",
        "level": "等级",
        "paused": "已暂停",
        "press_start": "按开始键游玩",
        "coins": "金币",
    },
}

# ─── Theme Palettes ──────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "bg": "#0a0a0f",
        "panel": "#12121a",
        "panel2": "#1a1a28",
        "accent": "#00d4ff",
        "accent2": "#ff6b35",
        "accent3": "#7c3aed",
        "text": "#e8e8ff",
        "text2": "#8888aa",
        "road": "#1a1a2e",
        "road_line": "#f0c040",
        "sky_top": "#050510",
        "sky_bot": "#0d0d2b",
        "grass": "#0a1a0a",
        "grass2": "#0d220d",
        "border": "#2a2a45",
        "btn_bg": "#1e1e35",
        "btn_hover": "#2a2a50",
        "nitro_color": "#00ffff",
        "danger": "#ff3355",
        "success": "#00ff88",
        "warning": "#ffcc00",
        "hud_bg": "rgba(10,10,20,200)",
        "shadow": "#000000",
    },
    "light": {
        "bg": "#e8eaf6",
        "panel": "#ffffff",
        "panel2": "#f0f2ff",
        "accent": "#1565c0",
        "accent2": "#e64a19",
        "accent3": "#6a1b9a",
        "text": "#1a1a2e",
        "text2": "#555577",
        "road": "#607d8b",
        "road_line": "#ffeb3b",
        "sky_top": "#42a5f5",
        "sky_bot": "#90caf9",
        "grass": "#66bb6a",
        "grass2": "#81c784",
        "border": "#c5cae9",
        "btn_bg": "#e3e8ff",
        "btn_hover": "#c5cae9",
        "nitro_color": "#0288d1",
        "danger": "#d32f2f",
        "success": "#2e7d32",
        "warning": "#f57f17",
        "hud_bg": "rgba(255,255,255,200)",
        "shadow": "#9e9e9e",
    },
}


# ─── Game Canvas ─────────────────────────────────────────────────────────────────
class GameCanvas(QWidget):
    score_changed = pyqtSignal(int)
    speed_changed = pyqtSignal(float)
    lap_changed = pyqtSignal(int)
    lives_changed = pyqtSignal(int)
    nitro_changed = pyqtSignal(float)
    coins_changed = pyqtSignal(int)
    game_over_signal = pyqtSignal(bool)  # bool = is new record

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._theme = THEMES["dark"]
        self._init_game()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._animate)
        self._anim_timer.start(16)
        self._keys = set()
        self._running = False
        self._paused = False
        self._game_over = False
        self._best_score = 0
        self._particles = []
        self._stars = [(random.uniform(0, 1), random.uniform(0, 0.45), random.uniform(0.5, 2.5)) for _ in range(120)]
        self._flash = 0
        self._shake = 0
        self._nitro_flash = 0
        self._coin_anim = []
        self._road_offset = 0.0
        self._bg_offset = 0.0
        self._frame = 0

    def _init_game(self):
        self._car_x = 0.0          # -1 to 1
        self._car_y = 0.0
        self._speed = 0.0
        self._max_speed = 220.0
        self._accel = 0.0
        self._steer = 0.0
        self._score = 0
        self._lap = 1
        self._lives = 3
        self._nitro = 100.0
        self._nitro_active = False
        self._coins = 0
        self._obstacles = []
        self._coin_objects = []
        self._road_curve = 0.0
        self._target_curve = 0.0
        self._curve_timer = 0
        self._distance = 0.0
        self._lap_dist = 2000.0
        self._invincible = 0
        self._level = 1
        self._road_offset = 0.0
        self._bg_offset = 0.0
        self._spawn_timer = 0
        self._coin_spawn_timer = 0
        self._road_segments = []
        self._generate_road()

    def _generate_road(self):
        self._road_segments = []
        for i in range(300):
            self._road_segments.append({
                "curve": random.uniform(-0.6, 0.6) if i % 40 < 20 else 0.0,
                "hill": math.sin(i * 0.05) * 0.3,
            })

    def set_theme(self, theme_name):
        self._theme = THEMES.get(theme_name, THEMES["dark"])
        self.update()

    def start_game(self):
        self._init_game()
        self._running = True
        self._paused = False
        self._game_over = False
        self._timer.start(16)
        self.setFocus()
        self.score_changed.emit(0)
        self.speed_changed.emit(0)
        self.lap_changed.emit(1)
        self.lives_changed.emit(3)
        self.nitro_changed.emit(100.0)
        self.coins_changed.emit(0)

    def pause_game(self):
        if self._running and not self._game_over:
            self._paused = not self._paused
            if self._paused:
                self._timer.stop()
            else:
                self._timer.start(16)
                self.setFocus()

    def restart_game(self):
        self._timer.stop()
        self.start_game()

    def _update(self):
        if not self._running or self._paused or self._game_over:
            return
        self._frame += 1
        dt = 0.016
        keys = self._keys

        # Steering
        steer_input = 0.0
        if Qt.Key.Key_Left in keys:
            steer_input = -1.0
        if Qt.Key.Key_Right in keys:
            steer_input = 1.0
        self._steer += (steer_input - self._steer) * 0.18

        # Acceleration
        accel_input = 0.0
        if Qt.Key.Key_Up in keys:
            accel_input = 1.0
        if Qt.Key.Key_Down in keys:
            accel_input = -0.6

        # Nitro
        self._nitro_active = Qt.Key.Key_Space in keys and self._nitro > 0
        if self._nitro_active:
            self._nitro = max(0, self._nitro - 1.2)
            accel_input = min(accel_input + 0.5, 1.5)
            self._nitro_flash = 8
        else:
            self._nitro = min(100, self._nitro + 0.18)

        # Speed physics
        target_speed = self._max_speed * accel_input
        if accel_input > 0:
            self._speed += (target_speed - self._speed) * 0.04
        else:
            self._speed += (target_speed - self._speed) * 0.07
        self._speed = max(0, min(self._speed, self._max_speed * 1.4 if self._nitro_active else self._max_speed))

        # Car position
        curve_effect = self._road_curve * 0.012 * (self._speed / 100)
        self._car_x += self._steer * 0.025 * (self._speed / 80 + 0.3) - curve_effect
        self._car_x = max(-1.0, min(1.0, self._car_x))

        # Road offset
        self._road_offset += self._speed * dt * 0.8
        self._bg_offset += self._speed * dt * 0.15

        # Road curve
        self._curve_timer += 1
        if self._curve_timer > 80:
            self._target_curve = random.uniform(-0.7, 0.7)
            self._curve_timer = 0
        self._road_curve += (self._target_curve - self._road_curve) * 0.015

        # Distance & lap
        self._distance += self._speed * dt
        if self._distance >= self._lap_dist:
            self._distance -= self._lap_dist
            self._lap += 1
            self._level = min(10, 1 + self._lap // 2)
            self._max_speed = 220 + self._level * 15
            self.lap_changed.emit(self._lap)
            self._flash = 20
            self._spawn_particles(self.width() // 2, self.height() // 2, "#00ff88", 30)

        # Score
        self._score += int(self._speed * dt * 0.5) + (2 if self._nitro_active else 0)
        self.score_changed.emit(self._score)
        self.speed_changed.emit(self._speed)
        self.nitro_changed.emit(self._nitro)

        # Spawn obstacles
        self._spawn_timer += 1
        spawn_rate = max(30, 80 - self._level * 5)
        if self._spawn_timer >= spawn_rate:
            self._spawn_timer = 0
            lane = random.choice([-0.55, -0.2, 0.2, 0.55])
            self._obstacles.append({
                "x": lane + random.uniform(-0.08, 0.08),
                "z": 1.0,
                "type": random.choice(["car", "truck", "cone"]),
                "color": random.choice(["#ff4444", "#4444ff", "#ffaa00", "#44ff44", "#ff44ff"]),
                "speed": random.uniform(0.3, 0.7),
            })

        # Spawn coins
        self._coin_spawn_timer += 1
        if self._coin_spawn_timer >= 45:
            self._coin_spawn_timer = 0
            self._coin_objects.append({
                "x": random.uniform(-0.7, 0.7),
                "z": 1.0,
                "collected": False,
            })

        # Update obstacles
        new_obs = []
        for obs in self._obstacles:
            obs["z"] -= (self._speed / 200 + obs["speed"] * 0.01) * dt * 60
            if obs["z"] > 0.05:
                new_obs.append(obs)
            # Collision
            if 0.08 < obs["z"] < 0.22 and self._invincible == 0:
                car_screen_x = self._car_x
                if abs(obs["x"] - car_screen_x) < 0.18:
                    self._lives -= 1
                    self.lives_changed.emit(self._lives)
                    self._invincible = 120
                    self._shake = 18
                    self._flash = 15
                    self._speed *= 0.3
                    self._spawn_particles(self.width() // 2, int(self.height() * 0.65), "#ff3355", 25)
                    if self._lives <= 0:
                        self._end_game()
                        return
        self._obstacles = new_obs

        # Update coins
        new_coins = []
        for coin in self._coin_objects:
            coin["z"] -= (self._speed / 200) * dt * 60
            if coin["z"] > 0.05 and not coin["collected"]:
                new_coins.append(coin)
            if 0.08 < coin["z"] < 0.22 and not coin["collected"]:
                car_screen_x = self._car_x
                if abs(coin["x"] - car_screen_x) < 0.14:
                    coin["collected"] = True
                    self._coins += 1
                    self._score += 50
                    self.coins_changed.emit(self._coins)
                    self._coin_anim.append({"x": self.width() // 2, "y": int(self.height() * 0.6), "life": 40})
        self._coin_objects = new_coins

        # Invincibility
        if self._invincible > 0:
            self._invincible -= 1

        # Update particles
        new_p = []
        for p in self._particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.3
            p["life"] -= 1
            if p["life"] > 0:
                new_p.append(p)
        self._particles = new_p

        # Coin anim
        new_ca = []
        for ca in self._coin_anim:
            ca["y"] -= 2
            ca["life"] -= 1
            if ca["life"] > 0:
                new_ca.append(ca)
        self._coin_anim = new_ca

        if self._flash > 0:
            self._flash -= 1
        if self._shake > 0:
            self._shake -= 1
        if self._nitro_flash > 0:
            self._nitro_flash -= 1

        self.update()

    def _animate(self):
        if not self._running or self._paused:
            self.update()

    def _end_game(self):
        self._running = False
        self._game_over = True
        self._timer.stop()
        is_record = self._score > self._best_score
        if is_record:
            self._best_score = self._score
        self.game_over_signal.emit(is_record)
        self.update()

    def _spawn_particles(self, x, y, color, count=20):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 9)
            self._particles.append({
                "x": float(x), "y": float(y),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 3,
                "life": random.randint(20, 50),
                "max_life": 50,
                "color": color,
                "size": random.uniform(2, 6),
            })

    # ─── Drawing ─────────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w, h = self.width(), self.height()
        t = self._theme

        # Shake
        if self._shake > 0:
            dx = random.randint(-self._shake, self._shake)
            dy = random.randint(-self._shake // 2, self._shake // 2)
            painter.translate(dx, dy)

        self._draw_sky(painter, w, h, t)
        self._draw_road(painter, w, h, t)
        self._draw_scenery(painter, w, h, t)
        self._draw_obstacles(painter, w, h, t)
        self._draw_coins_3d(painter, w, h, t)
        self._draw_car(painter, w, h, t)
        self._draw_particles(painter)
        self._draw_coin_anim(painter, w, h, t)

        # Flash overlay
        if self._flash > 0:
            alpha = int(self._flash * 12)
            painter.fillRect(0, 0, w, h, QColor(255, 50, 50, alpha))

        # Nitro flash
        if self._nitro_flash > 0:
            alpha = int(self._nitro_flash * 8)
            painter.fillRect(0, 0, w, h, QColor(0, 200, 255, alpha))

        if not self._running and not self._game_over:
            self._draw_start_screen(painter, w, h, t)
        if self._paused:
            self._draw_pause_screen(painter, w, h, t)
        if self._game_over:
            self._draw_game_over(painter, w, h, t)

        painter.end()

    def _draw_sky(self, p, w, h, t):
        horizon = int(h * 0.42)
        grad = QLinearGradient(0, 0, 0, horizon)
        grad.setColorAt(0, QColor(t["sky_top"]))
        grad.setColorAt(1, QColor(t["sky_bot"]))
        p.fillRect(0, 0, w, horizon, grad)

        # Stars (dark theme only)
        if t == THEMES["dark"]:
            p.setPen(Qt.PenStyle.NoPen)
            for sx, sy, sr in self._stars:
                bx = int((sx + self._bg_offset * 0.001) % 1.0 * w)
                by = int(sy * horizon)
                alpha = int(150 + 100 * math.sin(self._frame * 0.05 + sx * 10))
                p.setBrush(QColor(255, 255, 255, alpha))
                p.drawEllipse(bx - int(sr), by - int(sr), int(sr * 2), int(sr * 2))

        # Sun / Moon
        sun_x = int(w * 0.75)
        sun_y = int(horizon * 0.35)
        if t == THEMES["dark"]:
            # Moon
            p.setBrush(QColor(220, 220, 255, 200))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(sun_x - 18, sun_y - 18, 36, 36)
            p.setBrush(QColor(t["sky_top"]))
            p.drawEllipse(sun_x - 10, sun_y - 22, 30, 30)
        else:
            # Sun glow
            for r in range(5, 0, -1):
                p.setBrush(QColor(255, 220, 50, 30 * r))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(sun_x - r * 8, sun_y - r * 8, r * 16, r * 16)
            p.setBrush(QColor(255, 240, 100))
            p.drawEllipse(sun_x - 20, sun_y - 20, 40, 40)

        # Mountains
        p.setPen(Qt.PenStyle.NoPen)
        mountain_color = QColor(t["sky_top"]).lighter(130) if t == THEMES["light"] else QColor(20, 20, 50)
        p.setBrush(mountain_color)
        pts = []
        for i in range(0, w + 60, 60):
            bx = (i + int(self._bg_offset * 0.3)) % (w + 120) - 60
            by = horizon - 30 - int(40 * math.sin(i * 0.04 + 1.2))
            pts.extend([bx, by])
        pts = [0, horizon] + pts + [w, horizon]
        poly = QPolygon([QPoint(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)])
        p.drawPolygon(poly)

    def _draw_road(self, p, w, h, t):
        horizon = int(h * 0.42)
        road_w_near = w * 0.72
        road_w_far = w * 0.08
        center_x = w / 2
        curve_offset = self._road_curve * w * 0.18

        # Grass
        grad_g = QLinearGradient(0, horizon, 0, h)
        grad_g.setColorAt(0, QColor(t["grass"]))
        grad_g.setColorAt(1, QColor(t["grass2"]))
        p.fillRect(0, horizon, w, h - horizon, grad_g)

        # Grass stripes
        stripe_count = 8
        for i in range(stripe_count):
            frac = i / stripe_count
            y_top = horizon + int((h - horizon) * frac)
            y_bot = horizon + int((h - horizon) * (frac + 1 / stripe_count))
            if i % 2 == 0:
                p.fillRect(0, y_top, w, y_bot - y_top, QColor(t["grass2"] + "44"))

        # Road surface
        road_pts = QPolygon([
            QPoint(int(center_x - road_w_near / 2), h),
            QPoint(int(center_x + road_w_near / 2), h),
            QPoint(int(center_x + road_w_far / 2 + curve_offset), horizon),
            QPoint(int(center_x - road_w_far / 2 + curve_offset), horizon),
        ])
        grad_r = QLinearGradient(0, horizon, 0, h)
        grad_r.setColorAt(0, QColor(t["road"]).darker(130))
        grad_r.setColorAt(1, QColor(t["road"]))
        p.setBrush(grad_r)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(road_pts)

        # Road edge lines
        p.setPen(QPen(QColor(255, 255, 255, 180), 3))
        p.drawLine(
            int(center_x - road_w_near / 2), h,
            int(center_x - road_w_far / 2 + curve_offset), horizon
        )
        p.drawLine(
            int(center_x + road_w_near / 2), h,
            int(center_x + road_w_far / 2 + curve_offset), horizon
        )

        # Dashed center lines
        num_dashes = 14
        for i in range(num_dashes):
            frac_top = i / num_dashes
            frac_bot = (i + 0.5) / num_dashes
            offset = (self._road_offset * 0.012) % (1 / num_dashes)
            ft = (frac_top + offset) % 1.0
            fb = (frac_bot + offset) % 1.0
            yt = horizon + int((h - horizon) * ft)
            yb = horizon + int((h - horizon) * fb)
            xt = center_x + curve_offset * ft
            xb = center_x + curve_offset * fb
            rw_t = road_w_far + (road_w_near - road_w_far) * ft
            rw_b = road_w_far + (road_w_near - road_w_far) * fb
            # Left lane
            p.setPen(QPen(QColor(t["road_line"]), max(1, int(2 * (ft + 0.3)))))
            p.drawLine(int(xt - rw_t * 0.28), yt, int(xb - rw_b * 0.28), yb)
            # Right lane
            p.drawLine(int(xt + rw_t * 0.28), yt, int(xb + rw_b * 0.28), yb)

        # Rumble strips
        strip_count = 10
        for i in range(strip_count):
            frac = i / strip_count
            offset = (self._road_offset * 0.015) % (1 / strip_count)
            ft = (frac + offset) % 1.0
            fb = ((frac + 0.5 / strip_count) + offset) % 1.0
            yt = horizon + int((h - horizon) * ft)
            yb = horizon + int((h - horizon) * fb)
            xt = center_x + curve_offset * ft
            xb = center_x + curve_offset * fb
            rw_t = road_w_far + (road_w_near - road_w_far) * ft
            rw_b = road_w_far + (road_w_near - road_w_far) * fb
            color = QColor("#ff2222") if i % 2 == 0 else QColor("#ffffff")
            p.setPen(QPen(color, max(1, int(3 * ft))))
            p.drawLine(int(xt - rw_t / 2), yt, int(xb - rw_b / 2), yb)
            p.drawLine(int(xt + rw_t / 2), yt, int(xb + rw_b / 2), yb)

    def _draw_scenery(self, p, w, h, t):
        horizon = int(h * 0.42)
        center_x = w / 2
        road_w_near = w * 0.72
        curve_offset = self._road_curve * w * 0.18

        # Trees / poles
        tree_positions = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
        tree_offset = (self._road_offset * 0.018) % 0.1
        for base_frac in tree_positions:
            frac = (base_frac + tree_offset) % 1.0
            y = horizon + int((h - horizon) * frac)
            scale = 0.3 + frac * 0.7
            cx_off = curve_offset * frac
            rw = road_w_near * frac * 0.5 + w * 0.04 * (1 - frac)

            for side in [-1, 1]:
                tx = int(center_x + cx_off + side * (road_w_near / 2 * frac + rw * 0.3 + 10))
                trunk_h = int(30 * scale)
                trunk_w = max(2, int(5 * scale))
                p.setBrush(QColor(80, 50, 20))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawRect(tx - trunk_w // 2, y - trunk_h, trunk_w, trunk_h)
                tree_color = QColor(t["grass"]).lighter(140) if t == THEMES["light"] else QColor(30, 80, 30)
                p.setBrush(tree_color)
                foliage_r = int(18 * scale)
                p.drawEllipse(tx - foliage_r, y - trunk_h - foliage_r, foliage_r * 2, foliage_r * 2)

    def _draw_obstacles(self, p, w, h, t):
        horizon = int(h * 0.42)
        center_x = w / 2
        road_w_near = w * 0.72
        road_w_far = w * 0.08
        curve_offset = self._road_curve * w * 0.18

        sorted_obs = sorted(self._obstacles, key=lambda o: o["z"], reverse=True)
        for obs in sorted_obs:
            z = obs["z"]
            if z <= 0.05:
                continue
            frac = 1 - z
            y = horizon + int((h - horizon) * frac)
            scale = 0.3 + frac * 0.7
            cx_off = curve_offset * frac
            rw = road_w_far + (road_w_near - road_w_far) * frac
            obs_x = center_x + cx_off + obs["x"] * rw
            obs_w = int(35 * scale)
            obs_h = int(50 * scale) if obs["type"] == "truck" else int(40 * scale) if obs["type"] == "car" else int(25 * scale)

            if obs["type"] == "cone":
                pts = QPolygon([
                    QPoint(int(obs_x), int(y - obs_h)),
                    QPoint(int(obs_x - obs_w / 2), int(y)),
                    QPoint(int(obs_x + obs_w / 2), int(y)),
                ])
                p.setBrush(QColor("#ff6600"))
                p.setPen(QPen(QColor("#ffffff"), max(1, int(2 * scale))))
                p.drawPolygon(pts)
            else:
                p.setBrush(QColor(obs["color"]))
                p.setPen(QPen(QColor(0, 0, 0, 100), max(1, int(2 * scale))))
                p.drawRoundedRect(int(obs_x - obs_w / 2), int(y - obs_h), obs_w, obs_h, 3 * scale, 3 * scale)
                window_h = int(obs_h * 0.35)
                window_y = int(y - obs_h + obs_h * 0.15)
                p.setBrush(QColor(100, 150, 200, 180))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawRect(int(obs_x - obs_w * 0.35), window_y, int(obs_w * 0.7), window_h)
                wheel_r = max(2, int(4 * scale))
                wheel_y = int(y - wheel_r)
                p.setBrush(QColor("#222222"))
                p.drawEllipse(int(obs_x - obs_w * 0.3), wheel_y, wheel_r * 2, wheel_r * 2)
                p.drawEllipse(int(obs_x + obs_w * 0.3 - wheel_r * 2), wheel_y, wheel_r * 2, wheel_r * 2)

    def _draw_coins_3d(self, p, w, h, t):
        horizon = int(h * 0.42)
        center_x = w / 2
        road_w_near = w * 0.72
        road_w_far = w * 0.08
        curve_offset = self._road_curve * w * 0.18

        for coin in self._coin_objects:
            if coin["collected"]:
                continue
            z = coin["z"]
            if z <= 0.05:
                continue
            frac = 1 - z
            y = horizon + int((h - horizon) * frac)
            scale = 0.3 + frac * 0.7
            cx_off = curve_offset * frac
            rw = road_w_far + (road_w_near - road_w_far) * frac
            coin_x = center_x + cx_off + coin["x"] * rw
            coin_r = int(12 * scale)
            
            glow_grad = QRadialGradient(coin_x, y, coin_r * 2.5)
            glow_grad.setColorAt(0, QColor(255, 215, 0, 100))
            glow_grad.setColorAt(1, QColor(255, 215, 0, 0))
            p.setBrush(glow_grad)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(int(coin_x - coin_r * 2.5), int(y - coin_r * 2.5), int(coin_r * 5), int(coin_r * 5))
            
            coin_grad = QRadialGradient(coin_x, y, coin_r)
            coin_grad.setColorAt(0, QColor(255, 235, 100))
            coin_grad.setColorAt(0.7, QColor(255, 200, 0))
            coin_grad.setColorAt(1, QColor(200, 150, 0))
            p.setBrush(coin_grad)
            p.setPen(QPen(QColor(180, 130, 0), max(1, int(2 * scale))))
            p.drawEllipse(int(coin_x - coin_r), int(y - coin_r), coin_r * 2, coin_r * 2)
            
            font = QFont("Arial", max(6, int(10 * scale)), QFont.Weight.Bold)
            p.setFont(font)
            p.setPen(QColor(150, 100, 0))
            p.drawText(QRectF(coin_x - coin_r, y - coin_r, coin_r * 2, coin_r * 2), Qt.AlignmentFlag.AlignCenter, "$")

    def _draw_car(self, p, w, h, t):
        car_y = int(h * 0.72)
        car_x = int(w / 2 + self._car_x * w * 0.32)
        car_w = 55
        car_h = 85

        if self._invincible > 0 and self._invincible % 8 < 4:
            return

        shadow_offset = 8
        p.setBrush(QColor(0, 0, 0, 80))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(car_x - car_w // 2 + shadow_offset, car_y + car_h - 10, car_w, 15)

        body_color = QColor(t["accent"])
        if self._nitro_active:
            body_color = QColor(t["nitro_color"])
        
        body_grad = QLinearGradient(car_x, car_y - car_h, car_x, car_y)
        body_grad.setColorAt(0, body_color.lighter(130))
        body_grad.setColorAt(0.5, body_color)
        body_grad.setColorAt(1, body_color.darker(120))
        p.setBrush(body_grad)
        p.setPen(QPen(QColor(0, 0, 0, 150), 2))
        p.drawRoundedRect(car_x - car_w // 2, car_y - car_h, car_w, car_h, 8, 8)

        window_h = int(car_h * 0.35)
        window_y = car_y - car_h + int(car_h * 0.15)
        p.setBrush(QColor(80, 120, 180, 200))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(car_x - int(car_w * 0.35), window_y, int(car_w * 0.7), window_h, 4, 4)

        wheel_w = 12
        wheel_h = 18
        wheel_color = QColor("#1a1a1a")
        p.setBrush(wheel_color)
        p.setPen(QPen(QColor("#444444"), 1))
        p.drawRoundedRect(car_x - car_w // 2 - 3, car_y - car_h + 15, wheel_w, wheel_h, 2, 2)
        p.drawRoundedRect(car_x + car_w // 2 - wheel_w + 3, car_y - car_h + 15, wheel_w, wheel_h, 2, 2)
        p.drawRoundedRect(car_x - car_w // 2 - 3, car_y - 25, wheel_w, wheel_h, 2, 2)
        p.drawRoundedRect(car_x + car_w // 2 - wheel_w + 3, car_y - 25, wheel_w, wheel_h, 2, 2)

        light_size = 6
        p.setBrush(QColor(255, 255, 200))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(car_x - car_w // 2 + 8, car_y - 12, light_size, light_size)
        p.drawEllipse(car_x + car_w // 2 - 8 - light_size, car_y - 12, light_size, light_size)

        if self._nitro_active:
            for i in range(5):
                flame_y = car_y + i * 8
                flame_w = 20 - i * 3
                flame_h = 12
                flame_alpha = 255 - i * 40
                flame_color = QColor(0, 200, 255, flame_alpha) if i % 2 == 0 else QColor(100, 220, 255, flame_alpha)
                p.setBrush(flame_color)
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(car_x - flame_w // 2, flame_y, flame_w, flame_h)

    def _draw_particles(self, p):
        p.setPen(Qt.PenStyle.NoPen)
        for part in self._particles:
            alpha = int(255 * (part["life"] / part["max_life"]))
            color = QColor(part["color"])
            color.setAlpha(alpha)
            p.setBrush(color)
            p.drawEllipse(int(part["x"] - part["size"] / 2), int(part["y"] - part["size"] / 2), int(part["size"]), int(part["size"]))

    def _draw_coin_anim(self, p, w, h, t):
        for ca in self._coin_anim:
            alpha = int(255 * (ca["life"] / 40))
            font = QFont("Arial", 20, QFont.Weight.Bold)
            p.setFont(font)
            p.setPen(QColor(255, 215, 0, alpha))
            p.drawText(ca["x"] - 30, ca["y"], 60, 30, Qt.AlignmentFlag.AlignCenter, "+50")

    def _draw_start_screen(self, p, w, h, t):
        overlay = QColor(t["bg"])
        overlay.setAlpha(240)
        p.fillRect(0, 0, w, h, overlay)
        
        title_font = QFont("Arial", max(24, w // 25), QFont.Weight.Bold)
        p.setFont(title_font)
        p.setPen(QColor(t["accent"]))
        title_rect = QRectF(0, h * 0.25, w, 60)
        p.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "3D RACING")
        
        subtitle_font = QFont("Arial", max(12, w // 50))
        p.setFont(subtitle_font)
        p.setPen(QColor(t["text2"]))
        subtitle_rect = QRectF(0, h * 0.25 + 70, w, 30)
        p.drawText(subtitle_rect, Qt.AlignmentFlag.AlignCenter, "Press START to begin")

    def _draw_pause_screen(self, p, w, h, t):
        overlay = QColor(t["bg"])
        overlay.setAlpha(200)
        p.fillRect(0, 0, w, h, overlay)
        
        font = QFont("Arial", max(28, w // 20), QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(QColor(t["accent"]))
        pause_rect = QRectF(0, h * 0.4, w, 60)
        p.drawText(pause_rect, Qt.AlignmentFlag.AlignCenter, "PAUSED")

    def _draw_game_over(self, p, w, h, t):
        overlay = QColor(t["bg"])
        overlay.setAlpha(230)
        p.fillRect(0, 0, w, h, overlay)
        
        title_font = QFont("Arial", max(32, w // 18), QFont.Weight.Bold)
        p.setFont(title_font)
        p.setPen(QColor(t["danger"]))
        title_rect = QRectF(0, h * 0.3, w, 60)
        p.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "GAME OVER")
        
        score_font = QFont("Arial", max(18, w // 35), QFont.Weight.Bold)
        p.setFont(score_font)
        p.setPen(QColor(t["text"]))
        score_rect = QRectF(0, h * 0.3 + 80, w, 40)
        p.drawText(score_rect, Qt.AlignmentFlag.AlignCenter, f"Score: {self._score}")
        
        if self._score == self._best_score and self._best_score > 0:
            p.setPen(QColor(t["success"]))
            record_rect = QRectF(0, h * 0.3 + 130, w, 30)
            p.drawText(record_rect, Qt.AlignmentFlag.AlignCenter, "NEW RECORD!")

    def keyPressEvent(self, event):
        self._keys.add(event.key())

    def keyReleaseEvent(self, event):
        self._keys.discard(event.key())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()


# ─── Main Window ─────────────────────────────────────────────────────────────────
class RacingGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self._lang = "en"
        self._theme_name = "dark"
        self._init_ui()
        self.resize(1200, 800)
        self.setMinimumSize(600, 400)

    def _init_ui(self):
        self.setWindowTitle(self._t("title"))
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._canvas = GameCanvas()
        self._canvas.score_changed.connect(self._update_score)
        self._canvas.speed_changed.connect(self._update_speed)
        self._canvas.lap_changed.connect(self._update_lap)
        self._canvas.lives_changed.connect(self._update_lives)
        self._canvas.nitro_changed.connect(self._update_nitro)
        self._canvas.coins_changed.connect(self._update_coins)
        self._canvas.game_over_signal.connect(self._on_game_over)

        self._hud = self._create_hud()
        self._control_panel = self._create_control_panel()

        main_layout.addWidget(self._hud)
        main_layout.addWidget(self._canvas, 1)
        main_layout.addWidget(self._control_panel)

        self._apply_theme()

    def _create_hud(self):
        hud = QWidget()
        hud.setFixedHeight(80)
        layout = QHBoxLayout(hud)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(20)

        self._speed_label = self._create_hud_item(self._t("speed"), "0", self._t("km_h"))
        self._score_label = self._create_hud_item(self._t("score"), "0", "")
        self._lap_label = self._create_hud_item(self._t("lap"), "1", "")
        self._lives_label = self._create_hud_item(self._t("lives"), "3", "❤")
        self._coins_label = self._create_hud_item(self._t("coins"), "0", "🪙")

        nitro_container = QWidget()
        nitro_layout = QVBoxLayout(nitro_container)
        nitro_layout.setContentsMargins(0, 0, 0, 0)
        nitro_layout.setSpacing(3)
        nitro_title = QLabel(self._t("nitro"))
        nitro_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._nitro_bar = QProgressBar()
        self._nitro_bar.setRange(0, 100)
        self._nitro_bar.setValue(100)
        self._nitro_bar.setTextVisible(False)
        self._nitro_bar.setFixedHeight(12)
        nitro_layout.addWidget(nitro_title)
        nitro_layout.addWidget(self._nitro_bar)

        layout.addWidget(self._speed_label)
        layout.addWidget(self._score_label)
        layout.addWidget(self._lap_label)
        layout.addWidget(self._lives_label)
        layout.addWidget(self._coins_label)
        layout.addStretch()
        layout.addWidget(nitro_container)

        return hud

    def _create_hud_item(self, title, value, unit):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label = QLabel(f"{value} {unit}")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setProperty("hudValue", True)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        container._value_label = value_label
        container._unit = unit
        return container

    def _create_control_panel(self):
        panel = QWidget()
        panel.setFixedHeight(70)
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        self._start_btn = self._create_button(self._t("start"), self._on_start)
        self._pause_btn = self._create_button(self._t("pause"), self._on_pause)
        self._restart_btn = self._create_button(self._t("restart"), self._on_restart)
        self._settings_btn = self._create_button("⚙", self._on_settings)

        layout.addWidget(self._start_btn)
        layout.addWidget(self._pause_btn)
        layout.addWidget(self._restart_btn)
        layout.addStretch()
        layout.addWidget(self._settings_btn)

        return panel

    def _create_button(self, text, callback):
        btn = QPushButton(text)
        btn.setFixedHeight(45)
        btn.setMinimumWidth(100)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        return btn

    def _on_start(self):
        self._canvas.start_game()
        self._start_btn.setEnabled(False)
        self._pause_btn.setEnabled(True)
        self._restart_btn.setEnabled(True)

    def _on_pause(self):
        self._canvas.pause_game()
        if self._canvas._paused:
            self._pause_btn.setText(self._t("resume"))
        else:
            self._pause_btn.setText(self._t("pause"))

    def _on_restart(self):
        self._canvas.restart_game()
        self._start_btn.setEnabled(False)
        self._pause_btn.setEnabled(True)
        self._pause_btn.setText(self._t("pause"))

    def _on_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self._t("settings"))
        dialog.setModal(True)
        dialog.setFixedSize(350, 250)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)

        lang_group = QGroupBox(self._t("language"))
        lang_layout = QVBoxLayout(lang_group)
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(["English", "فارسی", "中文"])
        self._lang_combo.setCurrentIndex(["en", "fa", "zh"].index(self._lang))
        lang_layout.addWidget(self._lang_combo)

        theme_group = QGroupBox(self._t("theme"))
        theme_layout = QVBoxLayout(theme_group)
        self._theme_combo = QComboBox()
        self._theme_combo.addItems([self._t("dark"), self._t("light")])
        self._theme_combo.setCurrentIndex(0 if self._theme_name == "dark" else 1)
        theme_layout.addWidget(self._theme_combo)

        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        cancel_btn = QPushButton("Cancel")
        apply_btn.clicked.connect(lambda: self._apply_settings(dialog))
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addWidget(lang_group)
        layout.addWidget(theme_group)
        layout.addStretch()
        layout.addLayout(btn_layout)

        dialog.exec()

    def _apply_settings(self, dialog):
        lang_map = {0: "en", 1: "fa", 2: "zh"}
        self._lang = lang_map[self._lang_combo.currentIndex()]
        self._theme_name = "dark" if self._theme_combo.currentIndex() == 0 else "light"
        self._canvas.set_theme(self._theme_name)
        self._apply_theme()
        self._update_texts()
        dialog.accept()

    def _apply_theme(self):
        t = THEMES[self._theme_name]
        style = f"""
        QMainWindow, QWidget {{
            background-color: {t['bg']};
            color: {t['text']};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        QLabel {{
            color: {t['text']};
        }}
        QLabel[hudValue="true"] {{
            font-size: 18px;
            font-weight: bold;
            color: {t['accent']};
        }}
        QPushButton {{
            background-color: {t['btn_bg']};
            color: {t['text']};
            border: 2px solid {t['border']};
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {t['btn_hover']};
            border-color: {t['accent']};
        }}
        QPushButton:pressed {{
            background-color: {t['accent']};
        }}
        QPushButton:disabled {{
            background-color: {t['panel']};
            color: {t['text2']};
            border-color: {t['border']};
        }}
        QProgressBar {{
            border: 2px solid {t['border']};
            border-radius: 6px;
            background-color: {t['panel']};
            text-align: center;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {t['nitro_color']}, stop:1 {t['accent']});
            border-radius: 4px;
        }}
        QGroupBox {{
            border: 2px solid {t['border']};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}
        QComboBox {{
            background-color: {t['panel']};
            border: 2px solid {t['border']};
            border-radius: 6px;
            padding: 5px;
            color: {t['text']};
        }}
        QComboBox:hover {{
            border-color: {t['accent']};
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: {t['panel']};
            color: {t['text']};
            selection-background-color: {t['accent']};
        }}
        QDialog {{
            background-color: {t['bg']};
        }}
        """
        self.setStyleSheet(style)

    def _update_texts(self):
        self.setWindowTitle(self._t("title"))
        self._start_btn.setText(self._t("start"))
        self._pause_btn.setText(self._t("pause") if not self._canvas._paused else self._t("resume"))
        self._restart_btn.setText(self._t("restart"))

    def _t(self, key):
        return TRANSLATIONS[self._lang].get(key, key)

    def _update_score(self, score):
        self._score_label._value_label.setText(f"{score} ")

    def _update_speed(self, speed):
        self._speed_label._value_label.setText(f"{int(speed)} {self._t('km_h')}")

    def _update_lap(self, lap):
        self._lap_label._value_label.setText(f"{lap} ")

    def _update_lives(self, lives):
        self._lives_label._value_label.setText(f"{lives} ❤")

    def _update_nitro(self, nitro):
        self._nitro_bar.setValue(int(nitro))

    def _update_coins(self, coins):
        self._coins_label._value_label.setText(f"{coins} 🪙")

    def _on_game_over(self, is_record):
        self._start_btn.setEnabled(True)
        self._pause_btn.setEnabled(False)
        msg = QMessageBox(self)
        msg.setWindowTitle(self._t("game_over"))
        text = f"{self._t('score')}: {self._canvas._score}\n"
        if is_record:
            text += f"\n{self._t('new_record')}"
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._canvas.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RacingGame()
    window.show()
    sys.exit(app.exec())
