#!/usr/bin/env python3
"""Neon birthday ball: a glowing crystal ball with a rotating 3D cake.

Usage:
    python3 birthday_cake.py             # open the birthday ball window
    python3 birthday_cake.py --selftest  # run a headless self check

Controls:
    Click a candle to blow it out, or press the blow-all button.
    Relight, launch fireworks, play music, drag the window, and press ESC to close.
"""
from __future__ import annotations

import argparse
import math
import os
import random
import struct
import subprocess
import sys
import tempfile
import wave

try:
    import tkinter as tk
except ImportError:  # pragma: no cover
    sys.exit("需要 tkinter。请安装带 Tk 支持的 Python 后重试。")


FONT = ("PingFang SC", 13, "bold")
NIGHT = "#0b1026"
PINK = "#ff2d95"
CYAN = "#00f0ff"
GOLD = "#ffc53d"
PURPLE = "#a06bff"
GREEN = "#39ffa0"
WHITE = "#ffffff"
FLAME_COLORS = ["#fff7cc", "#ffe066", "#ffd166", "#ff9f43"]
NEON_PALETTE = [PINK, CYAN, GOLD, PURPLE, GREEN, WHITE]


class BirthdayBallApp:
    W = 640
    H = 860

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.frame = 0
        self.rot = 0.0
        self.music_proc: subprocess.Popen | None = None
        self.music_on = False
        self.song_path = ""
        self.wish_shown = False
        self.wish_frame = -100
        self.candle_screen_pos: list[tuple[float, float, bool]] = []
        self.embers: list[dict] = []
        self.fireworks: list[dict] = []
        self.shooting: list[dict] = []

        root.title("生日快乐 · 生日球")
        root.geometry(f"{self.W}x{self.H}")
        root.eval("tk::PlaceWindow . center")

        self.canvas = tk.Canvas(root, width=self.W, height=self.H,
                                highlightthickness=0, bg=NIGHT)
        self.canvas.pack(fill="both", expand=True)
        self.setup_transparent_window()

        self.cx = self.W / 2
        self.ball_r = 224
        self.cy = 330

        self.build_background()
        self.build_ball_glass()
        self.build_dynamic()
        self.build_stand_and_text()
        self.build_controls()

        self.drag_data = {"press_x": 0, "press_y": 0,
                          "win_x": 0, "win_y": 0, "moved": False}
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        root.bind("<Escape>", lambda _e: root.destroy())
        self.canvas.focus_set()

        self.tick()

    # ------------------------------------------------------------------
    # Static scene
    # ------------------------------------------------------------------

    def setup_transparent_window(self) -> None:
        if sys.platform == "darwin":
            self.root.overrideredirect(True)
            self.root.attributes("-alpha", 0.94)
            self.root.attributes("-topmost", True)
            self.root.config(bg=NIGHT)
            self.canvas.config(bg=NIGHT)
        elif sys.platform.startswith("win"):
            self.root.overrideredirect(True)
            self.root.attributes("-topmost", True)
            self.root.attributes("-transparentcolor", "#010101")
            self.root.config(bg="#010101")
            self.canvas.config(bg="#010101")
        else:
            self.root.overrideredirect(True)
            self.root.attributes("-topmost", True)
            self.root.attributes("-alpha", 0.9)

    def build_background(self) -> None:
        c = self.canvas
        self.stars = []
        for _ in range(70):
            x = random.uniform(8, self.W - 8)
            y = random.uniform(8, self.H * 0.78)
            size = random.uniform(1.2, 3.4)
            color = random.choice([WHITE, PINK, CYAN, GOLD])
            sid = c.create_oval(x - size, y - size, x + size, y + size,
                                fill=color, outline="", tags="bg")
            self.stars.append({"id": sid, "phase": random.uniform(0, math.tau),
                               "color": color})

    def build_ball_glass(self) -> None:
        c = self.canvas
        r = self.ball_r
        cx, cy = self.cx, self.cy
        edge = (20, 30, 74)
        center = (255, 218, 240)
        for i in range(30):
            t = i / 29
            rad = r * (1 - t * 0.97)
            rgb = tuple(round(edge[k] + (center[k] - edge[k]) * t) for k in range(3))
            c.create_oval(cx - rad, cy - rad, cx + rad, cy + rad,
                          fill=self._hex(rgb), outline="", tags="glass")

        self.rim_id = c.create_oval(cx - r, cy - r, cx + r, cy + r,
                                    outline=CYAN, width=2, tags="glass")
        self.highlight_id = c.create_arc(cx - r * 0.72, cy - r * 1.05,
                                         cx + r * 0.44, cy - r * 0.06,
                                         start=150, extent=115, style=tk.ARC,
                                         outline=WHITE, width=9, tags="glass")
        c.create_oval(cx - r * 0.44, cy - r * 0.84, cx - r * 0.08, cy - r * 0.56,
                      fill=WHITE, outline="", stipple="gray50", tags="glass")
        c.create_arc(cx - r * 0.8, cy + r * 0.5, cx + r * 0.6, cy + r * 1.08,
                     start=10, extent=92, style=tk.CHORD,
                     fill=WHITE, outline="", stipple="gray50", tags="glass")

        orbit_box = (cx - r - 18, cy - r * 0.42, cx + r + 18, cy + r * 0.42)
        c.create_oval(*orbit_box, outline="#33406e", width=2, tags="glass")
        self.comet_id = c.create_arc(*orbit_box, start=30, extent=90,
                                     style=tk.ARC, outline=GOLD, width=4,
                                     tags="glass")

    def build_dynamic(self) -> None:
        c = self.canvas
        self.layer_items = []
        layers = [
            (104, 54, 76, (255, 45, 149), "#ff8fab"),
            (82, 42, 130, (255, 183, 3), "#ffd166"),
            (60, 34, 172, (255, 255, 255), "#ffffff"),
        ]
        for _r, _h, _y0, _body, top in layers:
            bottom = c.create_oval(0, 0, 0, 0, fill="#ffffff", outline="", tags="dyn")
            body = c.create_rectangle(0, 0, 0, 0, fill="#ffffff",
                                      outline="", tags="dyn")
            top_el = c.create_oval(0, 0, 0, 0, fill=top, outline="", tags="dyn")
            stripe = c.create_rectangle(0, 0, 0, 0, fill="#ffffff",
                                        outline="", tags="dyn")
            self.layer_items.append({
                "r": _r, "h": _h, "y0": _y0, "body_rgb": _body,
                "bottom": bottom, "body": body, "top": top_el, "stripe": stripe,
            })

        cherry_y = self.cy - (172 + 34 + 12)
        self.cherry_id = c.create_oval(self.cx - 9, cherry_y - 9,
                                       self.cx + 9, cherry_y + 9,
                                       fill="#ff1744", outline="#ff8a80",
                                       width=1, tags="dyn")
        self.cherry_stem = c.create_line(self.cx, cherry_y - 8, self.cx + 5,
                                         cherry_y - 18, fill="#5d4037",
                                         width=2, tags="dyn")

        self.candles = []
        top_layer = layers[2]
        for i in range(5):
            body = c.create_rectangle(0, 0, 0, 0, fill="#ffffff",
                                      outline="", tags="dyn")
            stripe = c.create_rectangle(0, 0, 0, 0, fill=PINK, outline="", tags="dyn")
            wick = c.create_line(0, 0, 0, 0, fill="#5d4037", width=2, tags="dyn")
            glow = c.create_oval(0, 0, 0, 0, fill="#ff9f43", outline="", tags="dyn")
            flame = c.create_oval(0, 0, 0, 0, fill="#ffd166", outline="", tags="dyn")
            inner = c.create_oval(0, 0, 0, 0, fill="#fff7cc", outline="", tags="dyn")
            self.candles.append({
                "angle": i * math.tau / 5,
                "body": body, "stripe": stripe, "wick": wick,
                "glow": glow, "flame": flame, "inner": inner, "lit": True,
            })

        self.sparkles = []
        for _ in range(26):
            pid = c.create_polygon(0, 0, 0, 0, 0, 0, 0, 0,
                                   fill=WHITE, outline="", tags="dyn")
            self.sparkles.append({
                "id": pid,
                "a": random.uniform(0, math.tau),
                "rad": random.uniform(self.ball_r * 0.22, self.ball_r * 0.88),
                "y": random.uniform(-self.ball_r * 0.8, self.ball_r * 0.7),
                "phase": random.uniform(0, math.tau),
                "speed": random.uniform(0.6, 1.9),
                "size": random.uniform(4, 9),
                "color": random.choice(NEON_PALETTE),
            })

        self.snow = []
        for _ in range(20):
            pid = c.create_oval(0, 0, 0, 0, fill=WHITE, outline="", tags="dyn")
            self.snow.append({
                "id": pid,
                "a": random.uniform(0, math.tau),
                "rad": random.uniform(10, self.ball_r * 0.92),
                "y": random.uniform(-self.ball_r * 0.85, self.ball_r * 0.85),
                "speed": random.uniform(0.7, 1.7),
                "size": random.uniform(2, 4.2),
            })

        self.wish_id = c.create_text(
            self.cx, self.cy + self.ball_r + 118,
            text="\U0001F389 愿望成真 \U0001F389",
            font=("PingFang SC", 32, "bold"), fill=GOLD,
            state="hidden", tags="wish")

    def build_stand_and_text(self) -> None:
        c = self.canvas
        cx = self.cx
        ground = self.cy + self.ball_r - 6

        for i in range(4):
            rad = 126 - i * 24
            c.create_oval(cx - rad, ground + 66 - i * 5,
                          cx + rad, ground + 92 - i * 5,
                          fill="#12203f", outline="", tags="stand")

        c.create_oval(cx - 96, ground + 76, cx + 96, ground + 92,
                      fill=GOLD, outline="", tags="stand")
        c.create_rectangle(cx - 66, ground + 16, cx + 66, ground + 84,
                           fill="#2a1e52", outline=CYAN, width=1, tags="stand")
        c.create_oval(cx - 78, ground + 4, cx + 78, ground + 24,
                      fill="#4a3a8a", outline="", tags="stand")
        c.create_rectangle(cx - 60, ground + 26, cx + 60, ground + 33,
                           fill=GOLD, outline="", tags="stand")

        self.title_id = c.create_text(cx, ground + 130, text="生日快乐",
                                      font=("PingFang SC", 38, "bold"),
                                      fill=PINK, tags="text")
        self.letters = []
        text = "HAPPY BIRTHDAY"
        start_x = cx - (len(text) - 1) * 14.5
        for i, ch in enumerate(text):
            lid = c.create_text(start_x + i * 29, ground + 170, text=ch,
                                font=("Arial", 13, "bold"),
                                fill=NEON_PALETTE[i % len(NEON_PALETTE)],
                                tags="text")
            self.letters.append(lid)

    def build_controls(self) -> None:
        self.blow_btn = tk.Button(self.root, text="\U0001F56F\uFE0F 吹蜡烛",
                                  command=self.blow_all, font=FONT,
                                  bg="#16224a", fg=WHITE, activebackground=PINK,
                                  relief="flat", padx=12, pady=4, cursor="hand2")
        self.relight_btn = tk.Button(self.root, text="\u2728 重新点亮",
                                     command=self.relight, font=FONT,
                                     bg="#16224a", fg=WHITE, activebackground=GREEN,
                                     relief="flat", padx=12, pady=4, cursor="hand2")
        self.firework_btn = tk.Button(self.root, text="\U0001F386 烟花",
                                      command=self.fireworks_show, font=FONT,
                                      bg="#16224a", fg=WHITE, activebackground=GOLD,
                                      relief="flat", padx=12, pady=4, cursor="hand2")
        self.music_btn = tk.Button(self.root, text="\U0001F3B5 音乐",
                                   command=self.toggle_music, font=FONT,
                                   bg="#16224a", fg=WHITE, activebackground=CYAN,
                                   relief="flat", padx=12, pady=4, cursor="hand2")
        self.close_btn = tk.Button(self.root, text="\u2715", command=self.root.destroy,
                                   font=("PingFang SC", 12, "bold"),
                                   bg="#16224a", fg=PINK, activebackground="#3a2a5a",
                                   relief="flat", padx=8, pady=2, cursor="hand2")

        self.canvas.create_window(self.W - 10, self.H - 10, anchor="se",
                                  window=self.blow_btn)
        self.canvas.create_window(self.W - 10, self.H - 58, anchor="se",
                                  window=self.relight_btn)
        self.canvas.create_window(self.W - 10, self.H - 106, anchor="se",
                                  window=self.firework_btn)
        self.canvas.create_window(self.W - 10, self.H - 154, anchor="se",
                                  window=self.music_btn)
        self.canvas.create_window(self.W - 12, 12, anchor="ne",
                                  window=self.close_btn)

    # ------------------------------------------------------------------
    # Projection helpers
    # ------------------------------------------------------------------

    def _rot(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        cos_a, sin_a = math.cos(self.rot), math.sin(self.rot)
        xr = x * cos_a + z * sin_a
        zr = -x * sin_a + z * cos_a
        return self.cx + xr, self.cy - y, zr

    def _shaded(self, rgb: tuple[int, int, int], factor: float) -> str:
        return self._hex(tuple(min(255, max(0, round(ch * factor))) for ch in rgb))

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------

    def tick(self) -> None:
        self.advance()
        self.root.after(42, self.tick)

    def advance(self) -> None:
        self.frame += 1
        self.rot += 0.02
        self.update_stars()
        self.update_glass()
        self.update_cake()
        self.update_candles()
        self.update_sparkles()
        self.update_snow()
        self.update_embers()
        self.update_fireworks()
        self.update_shooting()
        self.update_text()

    def update_stars(self) -> None:
        c = self.canvas
        for s in self.stars:
            bright = (math.sin(self.frame * 0.09 + s["phase"]) + 1) / 2
            fill = s["color"] if bright > 0.5 else "#3a4a7a"
            c.itemconfigure(s["id"], fill=fill)

    def update_glass(self) -> None:
        c = self.canvas
        color = NEON_PALETTE[(self.frame // 12) % len(NEON_PALETTE)]
        c.itemconfigure(self.rim_id, outline=color)
        c.itemconfigure(self.highlight_id, start=150 + self.frame % 360 * 0.2)
        c.itemconfigure(self.comet_id, start=(self.frame * 2) % 360,
                        outline=NEON_PALETTE[(self.frame // 10) % len(NEON_PALETTE)])

    def update_cake(self) -> None:
        c = self.canvas
        for layer in self.layer_items:
            r, h, y0 = layer["r"], layer["h"], layer["y0"]
            y1 = y0 + h
            shade = 0.76 + 0.24 * (0.5 + 0.5 * math.cos(self.rot + 1.2))
            body_color = self._shaded(layer["body_rgb"], shade)
            cx = self.cx
            sy0 = self.cy - y0
            sy1 = self.cy - y1
            c.coords(layer["bottom"], cx - r, sy0 - r * 0.3, cx + r, sy0 + r * 0.3)
            c.itemconfigure(layer["bottom"], fill=body_color)
            c.coords(layer["body"], cx - r, sy0, cx + r, sy1)
            c.itemconfigure(layer["body"], fill=body_color)
            c.coords(layer["top"], cx - r, sy1 - r * 0.3, cx + r, sy1 + r * 0.3)
            stripe_w = r * 0.2
            stripe_color = NEON_PALETTE[(self.frame // 8) % len(NEON_PALETTE)]
            c.coords(layer["stripe"], cx - stripe_w / 2, sy0 + 5,
                     cx + stripe_w / 2, sy1 - 5)
            c.itemconfigure(layer["stripe"], fill=stripe_color)
            c.itemconfigure(layer["stripe"], stipple="gray50")

    def update_candles(self) -> None:
        c = self.canvas
        self.candle_screen_pos = []
        top_layer = self.layer_items[2]
        radius = top_layer["r"] * 0.52
        y = top_layer["y0"] + top_layer["h"] + 2

        for i, cd in enumerate(self.candles):
            a = cd["angle"] + self.rot
            x = math.cos(a) * radius
            z = math.sin(a) * radius
            sx, sy, zr = self._rot(x, y, z)
            self.candle_screen_pos.append((sx, sy, cd["lit"]))

            depth = (zr / radius + 1) / 2
            scale = 0.8 + 0.28 * depth
            w = 4.8 * scale
            ch = 32 * scale
            if zr < -6:
                for item in ("body", "stripe", "wick", "glow", "flame", "inner"):
                    c.itemconfigure(cd[item], state="hidden")
                continue

            for item in ("body", "stripe", "wick"):
                c.itemconfigure(cd[item], state="normal")
            c.coords(cd["body"], sx - w, sy - ch, sx + w, sy)
            c.coords(cd["stripe"], sx - w, sy - ch * 0.55, sx + w, sy - ch * 0.3)
            c.coords(cd["wick"], sx, sy - 2, sx, sy - 8 * scale)

            if cd["lit"]:
                for item in ("glow", "flame", "inner"):
                    c.itemconfigure(cd[item], state="normal")
                sway = math.sin(self.frame * 0.22 + i) * 1.8
                pulse = random.uniform(0, 2.6)
                c.coords(cd["glow"], sx - 9 * scale + sway, sy - ch - 26 * scale,
                         sx + 9 * scale + sway, sy - ch + 3 * scale)
                c.itemconfigure(cd["glow"], fill=random.choice(FLAME_COLORS))
                c.coords(cd["flame"], sx - 5.5 * scale + sway, sy - ch - 23 * scale + pulse * 0.3,
                         sx + 5.5 * scale + sway, sy - ch + pulse * 0.2)
                c.coords(cd["inner"], sx - 2.4 * scale + sway, sy - ch - 16 * scale,
                         sx + 2.4 * scale + sway, sy - ch - 4 * scale)
                c.itemconfigure(cd["flame"], fill=random.choice(FLAME_COLORS))
                if self.frame % 2 == 0 and random.random() < 0.5:
                    self._spawn_ember(sx, sy - ch - 18, scale)
            else:
                for item in ("glow", "flame", "inner"):
                    c.itemconfigure(cd[item], state="hidden")

    def update_sparkles(self) -> None:
        c = self.canvas
        for p in self.sparkles:
            a = p["a"] + self.frame * 0.013 * p["speed"]
            x = math.cos(a) * p["rad"]
            z = math.sin(a) * p["rad"]
            y = p["y"] + math.sin(self.frame * 0.05 + p["phase"]) * 10
            sx, sy, zr = self._rot(x, y, z)
            if (sx - self.cx) ** 2 + (sy - self.cy) ** 2 > (self.ball_r * 0.94) ** 2:
                c.itemconfigure(p["id"], state="hidden")
                continue
            twinkle = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(self.frame * 0.12 + p["phase"]))
            size = p["size"] * (0.75 + 0.3 * (zr / self.ball_r + 1) / 2) * twinkle
            c.coords(p["id"], *self._star_points(sx, sy, size))
            c.itemconfigure(p["id"], state="normal", fill=p["color"])

    def update_snow(self) -> None:
        c = self.canvas
        for s in self.snow:
            s["y"] -= s["speed"]
            if s["y"] < -self.ball_r * 0.88:
                s["y"] = self.ball_r * 0.88
                s["a"] = random.uniform(0, math.tau)
            s["a"] += 0.007
            x = math.cos(s["a"]) * s["rad"]
            z = math.sin(s["a"]) * s["rad"]
            sx, sy, zr = self._rot(x, s["y"], z)
            if (sx - self.cx) ** 2 + (sy - self.cy) ** 2 > (self.ball_r * 0.95) ** 2:
                c.itemconfigure(s["id"], state="hidden")
                continue
            size = s["size"] * (0.75 + 0.35 * (zr / self.ball_r + 1) / 2)
            c.coords(s["id"], sx - size, sy - size, sx + size, sy + size)
            c.itemconfigure(s["id"], state="normal", fill=WHITE)

    def update_embers(self) -> None:
        c = self.canvas
        for p in list(self.embers):
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] -= 0.03
            p["life"] -= 1
            if p["life"] <= 0:
                c.delete(p["id"])
                self.embers.remove(p)
                continue
            c.coords(p["id"], p["x"] - p["size"], p["y"] - p["size"],
                     p["x"] + p["size"], p["y"] + p["size"])

    def update_fireworks(self) -> None:
        c = self.canvas
        for p in list(self.fireworks):
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.14
            p["life"] -= 1
            if p["life"] <= 0:
                c.delete(p["id"])
                self.fireworks.remove(p)
                continue
            c.coords(p["id"], *self._star_points(p["x"], p["y"], p["size"]))
            c.itemconfigure(p["id"], fill=p["color"])

    def update_shooting(self) -> None:
        c = self.canvas
        if random.random() < 0.008 and len(self.shooting) < 3:
            x, y = -20, random.uniform(60, 300)
            vx = random.uniform(9, 15)
            vy = random.uniform(3, 6)
            sid = c.create_line(x, y, x - vx * 3, y - vy * 3,
                                fill=random.choice([CYAN, GOLD, PINK]),
                                width=2, tags="fx")
            self.shooting.append({"id": sid, "x": x, "y": y,
                                  "vx": vx, "vy": vy, "life": 90})
        for p in list(self.shooting):
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["x"] > self.W + 30 or p["y"] > self.H + 30 or p["life"] <= 0:
                c.delete(p["id"])
                self.shooting.remove(p)
                continue
            c.coords(p["id"], p["x"], p["y"],
                     p["x"] - p["vx"] * 3, p["y"] - p["vy"] * 3)

    def update_text(self) -> None:
        c = self.canvas
        color = NEON_PALETTE[(self.frame // 10) % len(NEON_PALETTE)]
        size = 38 + int(2 * math.sin(self.frame * 0.1))
        c.itemconfigure(self.title_id, fill=color,
                        font=("PingFang SC", size, "bold"))
        for i, lid in enumerate(self.letters):
            c.itemconfigure(lid, fill=NEON_PALETTE[
                (self.frame // 6 + i) % len(NEON_PALETTE)])

        if not self.wish_shown:
            return
        age = self.frame - self.wish_frame
        if age < 22:
            size = 12 + int(20 * (age / 22))
            c.itemconfigure(self.wish_id, font=("PingFang SC", size, "bold"))
        elif age % 36 < 18:
            c.itemconfigure(self.wish_id, fill=GOLD)
        else:
            c.itemconfigure(self.wish_id, fill=PINK)

    # ------------------------------------------------------------------
    # Interactions
    # ------------------------------------------------------------------

    def on_press(self, event: tk.Event) -> None:
        self.drag_data["press_x"] = event.x_root
        self.drag_data["press_y"] = event.y_root
        self.drag_data["win_x"] = self.root.winfo_x()
        self.drag_data["win_y"] = self.root.winfo_y()
        self.drag_data["moved"] = False

    def on_drag(self, event: tk.Event) -> None:
        dx = event.x_root - self.drag_data["press_x"]
        dy = event.y_root - self.drag_data["press_y"]
        if abs(dx) + abs(dy) > 6:
            self.drag_data["moved"] = True
            self.root.geometry(f"+{self.drag_data['win_x'] + dx}+{self.drag_data['win_y'] + dy}")

    def on_release(self, event: tk.Event) -> None:
        if not self.drag_data["moved"]:
            self.on_click(event)

    def on_click(self, event: tk.Event) -> None:
        best = None
        best_d = 26 ** 2
        for i, (x, y, lit) in enumerate(self.candle_screen_pos):
            if not lit:
                continue
            d = (x - event.x) ** 2 + (y - event.y) ** 2
            if d < best_d:
                best = i
                best_d = d
        if best is not None:
            self.blow_out(best)

    def blow_out(self, idx: int) -> None:
        cd = self.candles[idx]
        if not cd["lit"]:
            return
        cd["lit"] = False
        sx, sy, _ = self._rot(
            math.cos(cd["angle"] + self.rot) * self.layer_items[2]["r"] * 0.52,
            self.layer_items[2]["y0"] + self.layer_items[2]["h"] + 2,
            math.sin(cd["angle"] + self.rot) * self.layer_items[2]["r"] * 0.52)
        self._spawn_smoke(sx, sy - 24)
        self._burst(sx, sy - 30, 16)
        if all(not c2["lit"] for c2 in self.candles):
            self.show_wish()

    def blow_all(self) -> None:
        for i in range(len(self.candles)):
            self.blow_out(i)

    def relight(self) -> None:
        for cd in self.candles:
            cd["lit"] = True
        self.wish_shown = False
        self.canvas.itemconfigure(self.wish_id, state="hidden")

    def show_wish(self) -> None:
        if self.wish_shown:
            return
        self.wish_shown = True
        self.wish_frame = self.frame
        self.canvas.itemconfigure(self.wish_id, state="normal")
        self.fireworks_show()

    def fireworks_show(self) -> None:
        for _ in range(6):
            self._burst(random.uniform(40, self.W - 40),
                        random.uniform(80, self.H * 0.55), 28)

    # ------------------------------------------------------------------
    # Particles
    # ------------------------------------------------------------------

    def _spawn_smoke(self, x: float, y: float) -> None:
        pid = self.canvas.create_oval(x - 8, y - 8, x + 8, y + 8,
                                      fill="#8899bb", outline="", tags="fx")
        self.embers.append({"id": pid, "x": x, "y": y, "vx": 0, "vy": 1.2,
                            "size": 8, "life": 26})

    def _spawn_ember(self, x: float, y: float, scale: float) -> None:
        pid = self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2,
                                      fill=random.choice([GOLD, PINK, CYAN]),
                                      outline="", tags="fx")
        self.embers.append({"id": pid, "x": x, "y": y,
                            "vx": random.uniform(-0.4, 0.4) * scale,
                            "vy": random.uniform(-1.6, -0.8) * scale,
                            "size": random.uniform(1.2, 2.4) * scale,
                            "life": random.randint(14, 24)})

    def _burst(self, x: float, y: float, count: int) -> None:
        for _ in range(count):
            a = random.uniform(0, math.tau)
            speed = random.uniform(2, 9)
            size = random.uniform(4, 10)
            pid = self.canvas.create_polygon(
                *self._star_points(x, y, size),
                fill=random.choice(NEON_PALETTE), outline="", tags="fx")
            self.fireworks.append({
                "id": pid, "x": x, "y": y,
                "vx": math.cos(a) * speed,
                "vy": math.sin(a) * speed - 1,
                "size": size, "life": random.randint(18, 32),
                "color": random.choice(NEON_PALETTE),
            })

    # ------------------------------------------------------------------
    # Music
    # ------------------------------------------------------------------

    def toggle_music(self) -> None:
        if self.music_on:
            self.stop_music()
            self.music_btn.config(text="\U0001F3B5 音乐")
            return
        try:
            path = self.ensure_song()
            self.play_song(path)
            self.music_on = True
            self.music_btn.config(text="\u23F9 音乐关")
        except Exception:
            self.music_btn.config(text="\u26A0 无音乐")

    def ensure_song(self) -> str:
        if self.song_path:
            return self.song_path
        notes = [
            (262, 0.42), (262, 0.18), (294, 0.6), (262, 0.6), (349, 0.6), (330, 0.82),
            (262, 0.42), (262, 0.18), (294, 0.6), (262, 0.6), (392, 0.6), (349, 0.82),
            (262, 0.42), (262, 0.18), (523, 0.6), (440, 0.6), (349, 0.6), (330, 0.6),
            (294, 0.82), (466, 0.42), (466, 0.18), (440, 0.6), (349, 0.6), (392, 0.6),
            (349, 0.9),
        ]
        rate = 22050
        samples: list[int] = []
        for _ in range(3):
            for freq, dur in notes:
                n = int(rate * dur)
                for i in range(n):
                    t = i / rate
                    env = math.exp(-3.2 * t / dur)
                    wave_val = (math.sin(2 * math.pi * freq * t)
                                + 0.35 * math.sin(4 * math.pi * freq * t)) * 0.4 * env
                    samples.append(int(max(-1, min(1, wave_val)) * 32767))
        path = os.path.join(tempfile.gettempdir(), "happy_birthday_bgm.wav")
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            wf.writeframes(b"".join(struct.pack("<h", s) for s in samples))
        self.song_path = path
        return path

    def play_song(self, path: str) -> None:
        if sys.platform == "darwin":
            self.music_proc = subprocess.Popen(
                ["afplay", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform.startswith("win"):
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        else:
            for player in ("aplay", "paplay"):
                try:
                    self.music_proc = subprocess.Popen(
                        [player, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return
                except OSError:
                    continue
            raise RuntimeError("no audio player found")

    def stop_music(self) -> None:
        if sys.platform.startswith("win"):
            try:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
        if self.music_proc is not None:
            self.music_proc.terminate()
            self.music_proc = None
        self.music_on = False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _hex(rgb: tuple[int, int, int]) -> str:
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    @staticmethod
    def _star_points(x: float, y: float, size: float) -> list[float]:
        return [
            x, y - size,
            x + size * 0.28, y - size * 0.28,
            x + size, y,
            x + size * 0.28, y + size * 0.28,
            x, y + size,
            x - size * 0.28, y + size * 0.28,
            x - size, y,
            x - size * 0.28, y - size * 0.28,
        ]

    def selftest(self) -> int:
        assert len(self.candles) == 5, "expected 5 candles"
        assert len(self.layer_items) == 3, "expected 3 cake layers"
        assert len(self.sparkles) == 26, "sparkles missing"
        assert self.canvas.find_withtag("glass"), "ball not drawn"
        for _ in range(12):
            self.advance()
        assert all(cd["lit"] for cd in self.candles), "candles should be lit"
        self.blow_all()
        assert all(not cd["lit"] for cd in self.candles), "candles should be out"
        assert self.wish_shown, "wish should be shown"
        self.relight()
        assert all(cd["lit"] for cd in self.candles), "relight failed"
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Neon birthday ball")
    parser.add_argument("--selftest", action="store_true", help="run checks without showing the window")
    args = parser.parse_args()

    root = tk.Tk()
    if args.selftest:
        root.withdraw()
        app = BirthdayBallApp(root)
        code = app.selftest()
        root.destroy()
        print("selftest passed")
        return code

    BirthdayBallApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
