"""Star Abyss: Dragon Legacy — Standalone pygame demo.

A side-scrolling pixel-action roguelike blending NES Ninja Gaiden combat
with infinite procedural depth and cartoon pixel visuals.

Single-file build. Run: python star_abyss.py
"""

import pygame
import sys
import random

# ═══════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
FPS = 60
BG_COLOR = (18, 18, 36)

GRAVITY = 0.7
FRICTION = 0.85
PLAYER_SPEED = 4.5
JUMP_VEL = -13
WALL_JUMP_X = 7
WALL_JUMP_Y = -11
WALL_SLIDE_SPEED = 1.8
AIR_CONTROL = 0.6
MAX_FALL = 14
ATTACK_DURATION = 8
HURT_DURATION = 20
INVINCIBLE_DURATION = 45
PLAYER_W = 32
PLAYER_H = 48
PLAYER_MAX_HP = 5

PLAYER_COLOR = (0, 200, 180)
PLAYER_ACCENT = (240, 240, 255)
HURT_COLOR = (255, 80, 80)
DEAD_COLOR = (60, 60, 60)
ATTACK_COLOR = (255, 255, 150)

CAMERA_LERP = 0.08
ROOM_WIDTH = 3000

ENEMY_ATTACK_COOLDOWN = 40

ENEMY_TYPES = {
    "grunt": {
        "hp": 3,
        "speed": 1.8,
        "w": 28,
        "h": 40,
        "color": (220, 70, 50),
        "detect_range": 250,
        "attack_range": 40,
        "damage": 1,
        "patrol_speed": 0.8,
    },
    "runner": {
        "hp": 2,
        "speed": 3.5,
        "w": 24,
        "h": 34,
        "color": (240, 140, 30),
        "detect_range": 350,
        "attack_range": 35,
        "damage": 1,
        "patrol_speed": 1.2,
    },
    "heavy": {
        "hp": 6,
        "speed": 1.2,
        "w": 40,
        "h": 52,
        "color": (160, 40, 80),
        "detect_range": 200,
        "attack_range": 48,
        "damage": 2,
        "patrol_speed": 0.4,
    },
}

# ═══════════════════════════════════════════════════════════════════
# Camera
# ═══════════════════════════════════════════════════════════════════


class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.lerp = CAMERA_LERP
        self.room_width = ROOM_WIDTH
        self.room_height = WINDOW_HEIGHT

    def follow(self, player):
        self.target_x = player.x - self.width // 2 + player.width // 2
        self.target_y = player.y - self.height // 2 + player.height // 2
        self.x += (self.target_x - self.x) * self.lerp
        self.y += (self.target_y - self.y) * self.lerp
        self.x = max(0, min(self.x, self.room_width - self.width))
        self.y = max(0, min(self.y, self.room_height - self.height))

    def offset(self):
        return (int(self.x), int(self.y))


# ═══════════════════════════════════════════════════════════════════
# Platform & Room Generator
# ═══════════════════════════════════════════════════════════════════


class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (80, 60, 40)
        self.color_highlight = (140, 110, 70)

    def copy(self):
        return self.rect


class RoomGenerator:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.room_w = ROOM_WIDTH

    def generate(self, layer_num):
        platforms = []
        enemy_spawns = []

        # Ground floor — always present
        platforms.append(Platform(0, self.screen_h - 32, self.room_w, 64))
        platforms[-1].color = (50, 90, 50)
        platforms[-1].color_highlight = (100, 160, 100)

        num_sections = 3 + layer_num // 3
        section_w = self.room_w // num_sections

        for s in range(num_sections):
            base_x = s * section_w + random.randint(100, section_w - 400)

            for _ in range(3 + min(layer_num, 8)):
                px = base_x + random.randint(0, section_w - 200)
                py = random.randint(100, self.screen_h - 160)
                pw = random.randint(80, 280)
                ph = 20
                platforms.append(Platform(px, py, pw, ph))

                if random.random() < 0.35:
                    wx = px + random.choice((-20, pw))
                    wh = random.randint(60, 180)
                    wy = py - wh + 10
                    platforms.append(Platform(wx, wy, 24, wh))

            num_enemies = 1 + layer_num // 2
            for _ in range(num_enemies):
                ex = base_x + random.randint(100, section_w - 200)
                ey = self.screen_h - 100
                enemy_spawns.append((ex, ey))

        player_spawn = (100, self.screen_h - 100)

        return {
            "platforms": platforms,
            "player_spawn": player_spawn,
            "enemy_spawns": enemy_spawns,
        }


# ═══════════════════════════════════════════════════════════════════
# Player
# ═══════════════════════════════════════════════════════════════════


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.width = PLAYER_W
        self.height = PLAYER_H
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.on_wall = False
        self.wall_dir = 0
        self.facing = 1

        self.state = "IDLE"
        self.state_timer = 0
        self.attack_timer = 0
        self.hurt_timer = 0
        self.invincible_timer = 0

        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.attack_hitbox = None
        self.wall_jump_cooldown = 0

    def handle_input(self, keys):
        if self.state in ("ATTACKING", "HURT", "DEAD"):
            return
        if keys[pygame.K_LEFT]:
            self.vx -= PLAYER_SPEED * (1.0 if self.on_ground else AIR_CONTROL)
            self.facing = -1
        elif keys[pygame.K_RIGHT]:
            self.vx += PLAYER_SPEED * (1.0 if self.on_ground else AIR_CONTROL)
            self.facing = 1
        else:
            if self.on_ground:
                self.vx *= FRICTION

    def try_jump(self):
        if self.state in ("ATTACKING", "HURT", "DEAD"):
            return
        if self.on_ground:
            self.vy = JUMP_VEL
            self.on_ground = False
            self.state = "JUMPING"
        elif self.on_wall and self.wall_jump_cooldown <= 0:
            self.vy = WALL_JUMP_Y
            self.vx = -self.wall_dir * WALL_JUMP_X
            self.on_wall = False
            self.state = "JUMPING"
            self.wall_jump_cooldown = 15

    def start_attack(self):
        if self.state in ("ATTACKING", "HURT", "DEAD"):
            return
        self.state = "ATTACKING"
        self.attack_timer = ATTACK_DURATION
        self.vx *= 0.3
        hx = self.x + self.width * self.facing if self.facing > 0 else self.x - 28
        self.attack_hitbox = pygame.Rect(hx, self.y + 4, 28, self.height - 8)

    def take_damage(self, amount):
        if self.invincible_timer > 0 or self.state == "DEAD":
            return False
        self.hp -= amount
        if self.hp <= 0:
            self.state = "DEAD"
            return True
        self.state = "HURT"
        self.hurt_timer = HURT_DURATION
        self.invincible_timer = INVINCIBLE_DURATION
        self.vx = -self.facing * 6
        self.vy = -6
        self.on_ground = False
        return False

    def update(self, dt, platforms):
        if self.wall_jump_cooldown > 0:
            self.wall_jump_cooldown -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        if self.state == "ATTACKING":
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.state = "IDLE"
                self.attack_hitbox = None
        elif self.state == "HURT":
            self.hurt_timer -= 1
            if self.hurt_timer <= 0:
                self.state = "IDLE"

        if self.state == "DEAD":
            return

        if not self.on_ground and self.state != "WALL_SLIDING":
            self.vy += GRAVITY
        if self.vy > MAX_FALL:
            self.vy = MAX_FALL
        if self.on_ground and self.state != "ATTACKING":
            self.vx *= FRICTION
        if abs(self.vx) > 8:
            self.vx = 8 if self.vx > 0 else -8

        self.x += self.vx
        self._resolve_collision_x(platforms)
        self.y += self.vy
        self._resolve_collision_y(platforms)

        self._update_state()

    def _update_state(self):
        if self.state in ("ATTACKING", "HURT", "DEAD"):
            return
        if self.on_wall and self.vy > 0 and not self.on_ground:
            self.state = "WALL_SLIDING"
        elif not self.on_ground:
            self.state = "JUMPING"
        elif abs(self.vx) > 0.3:
            self.state = "RUNNING"
        else:
            self.state = "IDLE"

    def _resolve_collision_x(self, platforms):
        rect = self._rect()
        self.on_wall = False
        self.wall_dir = 0
        for plat in platforms:
            if rect.colliderect(plat.rect):
                if self.vx > 0:
                    rect.right = plat.rect.left
                    self.on_wall = True
                    self.wall_dir = -1
                elif self.vx < 0:
                    rect.left = plat.rect.right
                    self.on_wall = True
                    self.wall_dir = 1
                self.x = float(rect.x)
                self.vx = 0

    def _resolve_collision_y(self, platforms):
        rect = self._rect()
        self.on_ground = False
        for plat in platforms:
            if rect.colliderect(plat.rect):
                if self.vy > 0:
                    rect.bottom = plat.rect.top
                    self.on_ground = True
                elif self.vy < 0:
                    rect.top = plat.rect.bottom
                self.y = float(rect.y)
                self.vy = 0

    def _rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, screen, cam_x, cam_y):
        sx = int(self.x) - cam_x
        sy = int(self.y) - cam_y

        if self.invincible_timer > 0 and self.invincible_timer % 4 < 2:
            return

        color = PLAYER_COLOR
        if self.state == "HURT":
            color = HURT_COLOR
        elif self.state == "DEAD":
            color = DEAD_COLOR

        # Body
        body = pygame.Rect(sx + 4, sy + 8, 24, 36)
        pygame.draw.rect(screen, color, body, border_radius=3)
        # Head
        pygame.draw.rect(screen, color, (sx + 6, sy, 20, 14), border_radius=3)
        # Eyes
        eye_x = sx + 20 if self.facing > 0 else sx + 8
        pygame.draw.rect(screen, PLAYER_ACCENT, (eye_x, sy + 4, 5, 4), border_radius=1)
        # Arms
        arm_color = tuple(max(0, c - 30) for c in color)
        pygame.draw.rect(screen, arm_color, (sx, sy + 12, 6, 20), border_radius=2)
        pygame.draw.rect(screen, arm_color, (sx + 26, sy + 12, 6, 20), border_radius=2)
        # Legs
        leg_color = tuple(max(0, c - 50) for c in color)
        pygame.draw.rect(screen, leg_color, (sx + 6, sy + 40, 8, 10), border_radius=2)
        pygame.draw.rect(screen, leg_color, (sx + 18, sy + 40, 8, 10), border_radius=2)

        # Wall slide particles
        if self.state == "WALL_SLIDING":
            for i in range(3):
                px = sx + (self.width + 2) if self.wall_dir > 0 else sx - 6
                py = sy + 20 + i * 10
                pygame.draw.circle(screen, (200, 200, 200), (int(px + i * 2), py), 2)

        # Attack slash
        if self.attack_hitbox is not None:
            ax = self.attack_hitbox.x - cam_x
            ay = self.attack_hitbox.y - cam_y
            slash = pygame.Rect(
                ax, ay, self.attack_hitbox.width, self.attack_hitbox.height
            )
            pygame.draw.rect(screen, ATTACK_COLOR, slash, border_radius=2)
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (ax + slash.width // 2, ay + 4),
                (ax + slash.width // 2 - 4 * self.facing, ay + slash.height - 4),
                3,
            )


# ═══════════════════════════════════════════════════════════════════
# Enemy
# ═══════════════════════════════════════════════════════════════════


class Enemy:
    def __init__(self, x, y, enemy_type="grunt"):
        cfg = ENEMY_TYPES[enemy_type]
        self.x = float(x)
        self.y = float(y)
        self.width = cfg["w"]
        self.height = cfg["h"]
        self.type = enemy_type
        self.hp = cfg["hp"]
        self.speed = cfg["speed"]
        self.color = cfg["color"]
        self.detect_range = cfg["detect_range"]
        self.attack_range = cfg["attack_range"]
        self.damage = cfg["damage"]
        self.patrol_speed = cfg["patrol_speed"]

        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1
        self.on_ground = False

        self.state = "PATROL"
        self.state_timer = 0
        self.attack_cooldown = 0
        self.hurt_timer = 0
        self.patrol_dir = random.choice((-1, 1))
        self.origin_x = float(x)
        self.invincible_timer = 0

    def update(self, dt, platforms, player):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.state == "HURT":
            self.hurt_timer -= 1
            if self.hurt_timer <= 0:
                self.state = "CHASE"

        dx = player.x - self.x
        dy = player.y - self.y
        dist = (dx * dx + dy * dy) ** 0.5

        if self.state == "PATROL":
            if dist < self.detect_range and abs(dy) < 200:
                self.state = "CHASE"
        elif self.state == "CHASE":
            if dist < self.attack_range:
                self.state = "ATTACK"
            elif dist > self.detect_range * 1.5:
                self.state = "RETURN"
        elif self.state == "ATTACK":
            if self.attack_cooldown <= 0 and dist < self.attack_range:
                self._attack(player)
                self.attack_cooldown = 40
            elif dist > self.attack_range * 1.5:
                self.state = "CHASE"
        elif self.state == "RETURN":
            if abs(self.x - self.origin_x) < 10:
                self.state = "PATROL"

        if self.state == "PATROL":
            self.vx = self.patrol_speed * self.patrol_dir
            if random.random() < 0.005:
                self.patrol_dir *= -1
        elif self.state == "CHASE":
            self.vx = self.speed * (1 if dx > 0 else -1)
            self.facing = 1 if dx > 0 else -1
        elif self.state == "ATTACK":
            self.vx *= 0.85
        elif self.state == "RETURN":
            odx = self.origin_x - self.x
            self.vx = self.patrol_speed * (1 if odx > 0 else -1)
        elif self.state == "HURT":
            self.vx *= 0.9

        self.vy += 0.7
        if self.vy > 14:
            self.vy = 14
        if abs(self.vx) > 6:
            self.vx = 6 if self.vx > 0 else -6

        self.x += self.vx
        self._collide_x(platforms)
        self.y += self.vy
        self._collide_y(platforms)

    def _attack(self, player):
        self.vx = self.facing * 4

    def take_hit(self, damage):
        if self.invincible_timer > 0:
            return False
        self.hp -= damage
        self.state = "HURT"
        self.hurt_timer = 10
        self.invincible_timer = 10
        self.vx = -self.facing * 3
        self.vy = -4
        return self.hp <= 0

    def _collide_x(self, platforms):
        rect = self._rect()
        for plat in platforms:
            if rect.colliderect(plat.rect):
                if self.vx > 0:
                    rect.right = plat.rect.left
                    self.patrol_dir *= -1
                elif self.vx < 0:
                    rect.left = plat.rect.right
                    self.patrol_dir *= -1
                self.x = float(rect.x)
                self.vx = 0

    def _collide_y(self, platforms):
        rect = self._rect()
        self.on_ground = False
        for plat in platforms:
            if rect.colliderect(plat.rect):
                if self.vy > 0:
                    rect.bottom = plat.rect.top
                    self.on_ground = True
                elif self.vy < 0:
                    rect.top = plat.rect.bottom
                self.y = float(rect.y)
                self.vy = 0

    def _rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, screen, cam_x, cam_y):
        sx = int(self.x) - cam_x
        sy = int(self.y) - cam_y

        if self.invincible_timer > 0 and self.invincible_timer % 4 < 2:
            return

        dark = tuple(max(0, c - 40) for c in self.color)
        light = tuple(min(255, c + 40) for c in self.color)

        pygame.draw.rect(
            screen,
            self.color,
            (sx + 3, sy + 6, self.width - 6, self.height - 12),
            border_radius=2,
        )
        hw = self.width - 8
        pygame.draw.rect(
            screen, self.color, (sx + 4, sy, hw, self.height // 3), border_radius=2
        )
        ex = sx + self.width - 12 if self.facing > 0 else sx + 4
        pygame.draw.rect(screen, (255, 50, 50), (ex, sy + 4, 6, 5), border_radius=1)
        pygame.draw.rect(screen, dark, (sx, sy + 10, 5, 16), border_radius=2)
        pygame.draw.rect(
            screen, dark, (sx + self.width - 5, sy + 10, 5, 16), border_radius=2
        )
        pygame.draw.rect(
            screen, dark, (sx + 4, sy + self.height - 14, 8, 12), border_radius=2
        )
        pygame.draw.rect(
            screen,
            dark,
            (sx + self.width - 12, sy + self.height - 14, 8, 12),
            border_radius=2,
        )

        if self.type == "heavy":
            pygame.draw.rect(screen, light, (sx + 8, sy + 2, self.width - 16, 3))


class EnemyManager:
    def __init__(self):
        self.enemies = []

    def spawn_for_layer(self, spawn_points, layer_num):
        self.enemies.clear()
        type_pool = ["grunt", "grunt", "grunt", "runner", "heavy"]
        if layer_num > 5:
            type_pool.append("runner")
            type_pool.append("heavy")
        for sp in spawn_points:
            etype = random.choice(type_pool)
            self.enemies.append(Enemy(sp[0], sp[1], etype))

    def update(self, dt, platforms, player):
        for enemy in self.enemies:
            enemy.update(dt, platforms, player)

    def remove(self, dead_list):
        for e in dead_list:
            if e in self.enemies:
                self.enemies.remove(e)


# ═══════════════════════════════════════════════════════════════════
# Combat System
# ═══════════════════════════════════════════════════════════════════


class CombatSystem:
    def check_player_attacks(self, player, enemies):
        if player.attack_hitbox is None:
            return []
        killed = []
        for enemy in enemies:
            er = pygame.Rect(int(enemy.x), int(enemy.y), enemy.width, enemy.height)
            if player.attack_hitbox.colliderect(er):
                if enemy.take_hit(1):
                    killed.append(enemy)
        return killed

    def check_enemy_hits(self, player, enemies):
        pr = pygame.Rect(int(player.x), int(player.y), player.width, player.height)
        for enemy in enemies:
            if enemy.state == "HURT":
                continue
            er = pygame.Rect(int(enemy.x), int(enemy.y), enemy.width, enemy.height)
            if pr.colliderect(er):
                return True
        return False


# ═══════════════════════════════════════════════════════════════════
# HUD
# ═══════════════════════════════════════════════════════════════════


def _shadow_text(screen, text, x, y, font, color=(255, 255, 255)):
    img = font.render(text, True, (0, 0, 0))
    screen.blit(img, (x + 1, y + 1))
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


class HUD:
    def __init__(self, screen_w):
        self.font_sm = pygame.font.Font(None, 20)
        self.font_lg = pygame.font.Font(None, 32)
        self.screen_w = screen_w

    def draw(self, screen, depth, kills, hp, max_hp):
        _shadow_text(
            screen, f"Depth: {depth}", self.screen_w // 2 - 50, 8, self.font_lg
        )
        _shadow_text(
            screen,
            f"Slain: {kills}",
            self.screen_w - 120,
            10,
            self.font_lg,
            (255, 220, 100),
        )

        bar_w = 140
        bar_h = 14
        bar_x = 12
        bar_y = 10
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
        ratio = max(0, hp / max_hp)
        fill_w = int(bar_w * ratio)
        if ratio > 0.5:
            hp_color = (80, 200, 80)
        elif ratio > 0.25:
            hp_color = (220, 180, 40)
        else:
            hp_color = (220, 50, 50)
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(screen, (180, 180, 180), (bar_x, bar_y, bar_w, bar_h), 1)
        _shadow_text(screen, f"HP {hp}/{max_hp}", bar_x + 4, bar_y - 1, self.font_sm)

        hint = "[Arrows] Move  [X] Jump  [Z] Attack  -- Wall-Climb the Abyss"
        _shadow_text(
            screen,
            hint,
            self.screen_w // 2 - 180,
            screen.get_height() - 22,
            self.font_sm,
        )


# ═══════════════════════════════════════════════════════════════════
# Menu
# ═══════════════════════════════════════════════════════════════════


def _centered_text(screen, text, y, font, color=(255, 255, 255)):
    img = font.render(text, True, (0, 0, 0))
    screen.blit(img, (screen.get_width() // 2 - img.get_width() // 2 + 1, y + 1))
    img = font.render(text, True, color)
    screen.blit(img, (screen.get_width() // 2 - img.get_width() // 2, y))


class Menu:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.title_font = pygame.font.Font(None, 56)
        self.sub_font = pygame.font.Font(None, 24)
        self.body_font = pygame.font.Font(None, 28)

    def render_title(self, screen):
        screen.fill((12, 12, 30))

        _centered_text(
            screen,
            "Dragon Ninja Legacy",
            self.screen_h // 2 - 100,
            self.title_font,
            (0, 220, 200),
        )
        _centered_text(
            screen,
            "Star Abyss",
            self.screen_h // 2 - 55,
            self.sub_font,
            (140, 200, 220),
        )

        _centered_text(
            screen,
            "One Life . Infinite Depth . No Ending",
            self.screen_h // 2 - 10,
            self.body_font,
            (180, 180, 200),
        )
        _centered_text(
            screen,
            "Precision Combat . Procedural Abyss . Pixel Art",
            self.screen_h // 2 + 25,
            self.sub_font,
            (160, 160, 180),
        )

        _centered_text(
            screen,
            "-- PRESS ENTER TO DESCEND --",
            self.screen_h // 2 + 80,
            self.body_font,
            (255, 255, 150),
        )

        margin = 40
        pygame.draw.rect(
            screen,
            (40, 60, 80),
            (margin, margin, self.screen_w - 2 * margin, self.screen_h - 2 * margin),
            2,
        )

    def render_death(self, screen, depth, kills):
        overlay = pygame.Surface((self.screen_w, self.screen_h))
        overlay.set_alpha(180)
        overlay.fill((8, 8, 8))
        screen.blit(overlay, (0, 0))

        _centered_text(
            screen,
            "YOU HAVE FALLEN",
            self.screen_h // 2 - 60,
            self.title_font,
            (220, 60, 60),
        )
        _centered_text(
            screen, f"Deepest Layer: {depth}", self.screen_h // 2 - 5, self.body_font
        )
        _centered_text(
            screen,
            f"Enemies Slain: {kills}",
            self.screen_h // 2 + 30,
            self.body_font,
            (220, 180, 60),
        )
        _centered_text(
            screen,
            "-- PRESS ENTER TO RISE AGAIN --",
            self.screen_h // 2 + 80,
            self.body_font,
            (200, 200, 200),
        )


# ═══════════════════════════════════════════════════════════════════
# Game Controller
# ═══════════════════════════════════════════════════════════════════


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU"

        self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.player = Player(200, 300)
        self.enemy_manager = EnemyManager()
        self.room_gen = RoomGenerator(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.combat = CombatSystem()
        self.hud = HUD(WINDOW_WIDTH)
        self.menu = Menu(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.platforms = []
        self.depth = 0
        self.kills = 0
        self._generate_layer(1)

    def _generate_layer(self, layer_num):
        data = self.room_gen.generate(layer_num)
        self.platforms = data["platforms"]
        self.player.x, self.player.y = data["player_spawn"]
        self.player.vx = self.player.vy = 0
        self.player.state = "IDLE"
        self.enemy_manager.spawn_for_layer(data["enemy_spawns"], layer_num)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()

            if self.state == "PLAYING":
                self._update(dt)
                self._render()
            elif self.state == "MENU":
                self.menu.render_title(self.screen)
            elif self.state == "DEAD":
                self._render()
                self.menu.render_death(self.screen, self.depth, self.kills)

            pygame.display.flip()

    def _handle_events(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.state == "MENU" and event.key == pygame.K_RETURN:
                    self.state = "PLAYING"
                    self.depth = 0
                    self.kills = 0
                    self._generate_layer(1)
                elif self.state == "DEAD" and event.key == pygame.K_RETURN:
                    self.state = "MENU"
                elif self.state == "PLAYING":
                    if event.key == pygame.K_z:
                        self.player.start_attack()
                    elif event.key == pygame.K_x:
                        self.player.try_jump()

        if self.state == "PLAYING":
            self.player.handle_input(keys)

    def _update(self, dt):
        self.player.update(dt, self.platforms)
        self.enemy_manager.update(dt, self.platforms, self.player)
        self.camera.follow(self.player)

        hits = self.combat.check_player_attacks(self.player, self.enemy_manager.enemies)
        if hits:
            self.kills += len(hits)
            self.enemy_manager.remove(hits)

        if self.combat.check_enemy_hits(self.player, self.enemy_manager.enemies):
            if self.player.take_damage(1):
                self.state = "DEAD"

        if not self.enemy_manager.enemies:
            self.depth += 1
            self._generate_layer(self.depth + 1)

    def _render(self):
        self.screen.fill(BG_COLOR)
        cam_x, cam_y = self.camera.offset()

        for plat in self.platforms:
            r = plat.copy()
            r.x -= cam_x
            r.y -= cam_y
            pygame.draw.rect(self.screen, plat.color, r)
            pygame.draw.line(
                self.screen, plat.color_highlight, r.topleft, r.topright, 2
            )

        for enemy in self.enemy_manager.enemies:
            enemy.draw(self.screen, cam_x, cam_y)

        self.player.draw(self.screen, cam_x, cam_y)
        self.hud.draw(
            self.screen, self.depth, self.kills, self.player.hp, self.player.max_hp
        )


# ═══════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════


def main():
    pygame.init()
    pygame.display.set_caption("Dragon Ninja Legacy: Star Abyss")
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
