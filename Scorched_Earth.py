import random
import pygame
import math
from levels_desigs import levels
import copy

# General setup
pygame.init()
pygame.mixer.init()
channel1 = pygame.mixer.Channel(0)
channel2 = pygame.mixer.Channel(1)
clock = pygame.time.Clock()

# Setting up the main window
screen_width = 1536
screen_height = 864
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("TanksWarEZ")
# -----------------------------------------------------------------------------------------------------------------
strait_grass = pygame.image.load("assets/grass.png").convert_alpha()
strait_grass = pygame.transform.scale(strait_grass, (96, 96))

strait_dirt = pygame.image.load("assets/dirt.png").convert_alpha()
strait_dirt = pygame.transform.scale(strait_dirt, (96, 96))

box_image = pygame.image.load("assets/box.png").convert_alpha()
box_image = pygame.transform.scale(box_image, (32, 32))

HE1 = pygame.image.load("assets/hand_grenade_01.png").convert_alpha()
HE1 = pygame.transform.scale(HE1, (16, 16))
HE2 = pygame.image.load("assets/hand_grenade_02.png").convert_alpha()
HE2 = pygame.transform.scale(HE2, (16, 16))
HE3 = pygame.image.load("assets/hand_grenade_03.png").convert_alpha()
HE3 = pygame.transform.scale(HE3, (16, 16))

helicopter_animation1 = pygame.image.load("assets/chopper1.gif").convert_alpha()
helicopter_animation1 = pygame.transform.rotozoom(helicopter_animation1, 0, 1.5)
helicopter_animation2 = pygame.image.load("assets/chopper2.gif").convert_alpha()
helicopter_animation2 = pygame.transform.rotozoom(helicopter_animation2, 0, 1.5)
helicopter_animation3 = pygame.image.load("assets/chopper3.gif").convert_alpha()
helicopter_animation3 = pygame.transform.rotozoom(helicopter_animation3, 0, 1.5)
helicopter_animation4 = pygame.image.load("assets/chopper4.gif").convert_alpha()
helicopter_animation4 = pygame.transform.rotozoom(helicopter_animation4, 0, 1.5)
helicopter_animation5 = pygame.image.load("assets/chopper5.gif").convert_alpha()
helicopter_animation5 = pygame.transform.rotozoom(helicopter_animation5, 0, 1.5)
helicopter_animations = [helicopter_animation1, helicopter_animation2, helicopter_animation3, helicopter_animation4,
                         helicopter_animation5]

background = pygame.image.load("assets/bg.jpg").convert_alpha()
background = pygame.transform.scale(background, (screen_width, screen_height))
space_background = pygame.image.load("assets/space_background.png").convert_alpha()
space_background = pygame.transform.scale(space_background, (screen_width, screen_height))
# -----------------------------------------------------------------------------------------------------------------
helicopter_sound = pygame.mixer.Sound("assets/sounds/helicopter_sound.mp3")
helicopter_sound.set_volume(1)
hit_sound = pygame.mixer.Sound("assets/sounds/hit_sound.mp3")
hit_sound.set_volume(1)
upgrade_sound = pygame.mixer.Sound("assets/sounds/upgrade_sound.mp3")
pick_up_sound = pygame.mixer.Sound("assets/sounds/interface.mp3")
winning_sound = pygame.mixer.Sound("assets/sounds/winning_sound.mp3")
explode_sound = pygame.mixer.Sound("assets/sounds/tank_explode.mp3")
shoot_sound = pygame.mixer.Sound("assets/sounds/gun_shoot.mp3")
change_ammo_sound = pygame.mixer.Sound("assets/sounds/reload.mp3")
moving_sound = pygame.mixer.Sound("assets/sounds/move.mp3")
click_sound = pygame.mixer.Sound("assets/sounds/click_sound.mp3")
background_music = pygame.mixer.Sound("assets/sounds/background_music.mp3")
risk = pygame.mixer.Sound("assets/sounds/risk.mp3")
cinematic = pygame.mixer.Sound("assets/sounds/cinematic.mp3")
# -----------------------------------------------------------------------------------------------------------------

tracks = [background_music, risk, cinematic]
tracks_index = 1
background_music.set_volume(0.6)

font = pygame.font.Font(None, 30)


# -----------------------------------------------------------------------------------------------------------------

class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        super().__init__()
        self.money = 0
        self.name = name
        self.x = x
        self.y = y
        self.image = pygame.image.load("assets/tank.gif").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)
        self.tank_rect = pygame.Rect(self.x, self.y, 90, 46)
        self.gun = pygame.image.load("assets/gun.gif").convert_alpha()
        self.gun = pygame.transform.rotozoom(self.gun, 0, 2)
        self.gun_rect = pygame.Rect(self.tank_rect.right - 3, self.tank_rect.top + 14, 48, 14)
        self.health = 100
        self.max_health = 100
        self.shield = 0
        self.fuel = 50
        self.max_fuel = 50
        self.gun_angle = 0
        self.velocity_x = 2
        self.velocity_y = 0
        self.fall_count = 0
        self.gun_power = 8
        self.max_gun_power = 10
        self.direction = "right"
        self.arsenal = ["normal", "HE1", "HE2", "HE3", "drill"]
        self.arsenal_index = 0
        self.ammo_count = {"normal": 10, "HE1": 2, "HE2": 0, "HE3": 0, "drill": 0}

    # -----------------------------------------------------------------------------------------------------------------

    def hit(self, damage):
        hit_through = damage - self.shield
        if hit_through > 0:
            self.shield = 0
            self.health -= hit_through
            if self.health <= 0:
                self.die()
        else:
            self.shield -= damage

    # -----------------------------------------------------------------------------------------------------------------

    def change_ammo_type(self, direction):
        while True:
            if direction == 1:
                if self.arsenal_index == len(self.arsenal) - 1:
                    self.arsenal_index = 0
                else:
                    self.arsenal_index += 1
            else:
                if self.arsenal_index == 0:
                    self.arsenal_index = len(self.arsenal) - 1
                else:
                    self.arsenal_index -= 1

            # Check if the current ammo type is not "normal" and its quantity is greater than 0
            current_ammo_type = self.arsenal[self.arsenal_index]
            if current_ammo_type == "normal" or self.ammo_count[current_ammo_type] > 0:
                change_ammo_sound.play()
                break

    # -----------------------------------------------------------------------------------------------------------------

    def die(self):
        global tanks_playing
        explode_sound.play()
        if len(tanks_playing.sprites()) > 1:
            tanks_playing.remove(self)

    # -----------------------------------------------------------------------------------------------------------------

    def spawn(self):
        global tanks_playing
        self.tank_rect = pygame.Rect(self.x, self.y, 90, 46)

    # -----------------------------------------------------------------------------------------------------------------

    def move(self, direction):
        if self.fuel > 0:
            if direction == "left":
                self.tank_rect.x -= self.velocity_x
                self.update_image(direction)
            elif direction == "right":
                self.tank_rect.x += self.velocity_x
                self.update_image(direction)
            self.fuel -= 1

    # -----------------------------------------------------------------------------------------------------------------

    def update_image(self, direction):
        if direction != self.direction:
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction = direction
            self.gun = pygame.transform.flip(self.gun, True, False)
            self.gun_angle = 180 - self.gun_angle

    # -----------------------------------------------------------------------------------------------------------------

    def update(self, screen, objects):
        self.velocity_y += min(1, (self.fall_count / 60))
        self.fall_count += 1
        self.tank_rect.y += self.velocity_y
        if self.tank_rect.bottom > screen_height:
            self.die()
        collided_object = collision(self.tank_rect, floor_rect + underground_rect)
        if collided_object is not None:
            if self.velocity_y > 5:
                self.hit(3 * int(self.velocity_y))
            self.velocity_y = 0
            self.fall_count = 0
            self.tank_rect.bottom = collided_object.top
        if self.direction == "right":
            self.gun_rect.center = (self.tank_rect.centerx + 14, self.tank_rect.centery - 3)
        else:
            self.gun_rect.center = (self.tank_rect.centerx - 14, self.tank_rect.centery - 3)

    # -----------------------------------------------------------------------------------------------------------------

    def shoot(self):
        shoot_sound.play()
        self.fuel = self.max_fuel
        Bullet(self, self.gun_power, self.gun_angle, self.arsenal[self.arsenal_index])
        self.arsenal_index = 0

    # -----------------------------------------------------------------------------------------------------------------

    def draw(self, screen):
        screen.blit(self.gun, self.gun_rect)
        screen.blit(self.image, self.tank_rect)
        pygame.draw.rect(screen, (200, 0, 0), (
            self.tank_rect.centerx - 50, self.tank_rect.top - 12, self.health * 100 / self.max_health, 10))
        pygame.draw.rect(screen, (255, 0, 0), (self.tank_rect.centerx - 50, self.tank_rect.top - 12, 100, 10), 2)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.name, True, (50, 50, 50))
        text_surface_rect = text_surface.get_rect(center=(self.tank_rect.centerx, self.tank_rect.centery - 50))
        screen.blit(text_surface,text_surface_rect)
        if self.shield > 0:
            pygame.draw.circle(screen, "#89CFF0", (self.tank_rect.centerx, self.tank_rect.centery + 5), 55, 4)

    # -----------------------------------------------------------------------------------------------------------------

    def draw_parabola(self, screen):
        initial_x = self.gun_rect.centerx
        initial_y = self.gun_rect.centery
        velocity_x = self.gun_power * math.cos(self.gun_angle * (math.pi / 180))
        velocity_y = self.gun_power * math.sin(self.gun_angle * (math.pi / 180))
        acceleration = 0.2

        max_time = 10

        for time in range(0, max_time):
            x = initial_x + velocity_x * time
            y = initial_y - velocity_y * time + (0.5 * acceleration * time ** 2)
            pygame.draw.circle(screen, (255, 0, 0), (x, y), 2)

    # -----------------------------------------------------------------------------------------------------------------

    def rotate_gun(self, angle):
        if self.direction == "right":
            if 90 >= self.gun_angle + angle >= -60:
                self.gun_angle += angle
            elif self.gun_angle <= -60:
                self.gun_angle = -60
            else:
                self.gun_angle = 90
        else:
            if 240 >= self.gun_angle - angle >= 90:
                self.gun_angle -= angle
            elif self.gun_angle <= 90:
                self.gun_angle = 90
            else:
                self.gun_angle = 240


# -----------------------------------------------------------------------------------------------------------------

class Bullet(pygame.sprite.Sprite):
    def __init__(self, tank, speed, angle, bullet_type):
        super().__init__()
        self.speed = speed
        self.angle = math.radians(angle)
        self.bullet_type = bullet_type
        self.sender = tank
        self.image = self.get_image(angle)
        self.image = pygame.transform.scale2x(self.image)
        self.rect = pygame.rect.Rect(tank.gun_rect.centerx, tank.gun_rect.centery, 32, 16)
        self.velocity_x = self.speed * math.cos(self.angle)
        self.velocity_y = -self.speed * math.sin(self.angle)
        self.explosion_time_red = 60
        self.explode = False
        bullets.add(self)
        self.use_ammo()

    # -----------------------------------------------------------------------------------------------------------------

    def use_ammo(self):
        if self.bullet_type != "normal":
            self.sender.ammo_count[self.bullet_type] -= 1

    # -----------------------------------------------------------------------------------------------------------------

    def get_image(self, angle):
        if self.bullet_type == "HE1":
            return HE1
        elif self.bullet_type == "HE2":
            return HE2
        elif self.bullet_type == "HE3":
            return HE3
        if -90 < angle < 90:
            return pygame.image.load("assets/shell.gif").convert_alpha()
        return pygame.transform.flip(pygame.image.load("assets/shell.gif").convert_alpha(), True, False)

    # -----------------------------------------------------------------------------------------------------------------

    def draw(self):
        if self.explode:
            if self.explosion_time_red >= 0:
                pygame.draw.circle(screen, (255, 0, 0), self.rect.center, 20)
                self.explosion_time_red -= 1
            else:
                self.kill()
        else:
            screen.blit(self.image, self.rect)

    # -----------------------------------------------------------------------------------------------------------------

    def update_bullet(self):
        global current_tank_index, tanks_playing
        if not self.explode:
            self.rect.centerx += self.velocity_x
            self.rect.centery += self.velocity_y

            self.velocity_y += 0.2

            if self.rect.left <= 0 or self.rect.right >= screen_width or self.rect.top <= 0 or self.rect.bottom >= screen_height:
                self.kill()

            for tank in tanks_playing.sprites():
                if tank != self.sender:
                    if self.rect.colliderect(tank.tank_rect):
                        if self.bullet_type == "normal":
                            tank.hit(30)
                        elif self.bullet_type == "HE1":
                            tank.hit(45)
                        elif self.bullet_type == "HE2":
                            tank.hit(70)
                        elif self.bullet_type == "HE3":
                            tank.hit(90)
                            try:
                                if tanks_playing.sprites()[current_tank_index] == tank:
                                    current_tank_index = (1 + current_tank_index) % len(tanks_playing.sprites())
                            except IndexError:
                                pass
                        self.explode = True
                        hit_sound.play()
            for block_rect in floor_rect + underground_rect:
                if self.rect.colliderect(block_rect):
                    self.explode = True
                    destroy_ground(self.rect.center, self.bullet_type, 70)
                    hit_sound.play()
                    self.kill()


# -----------------------------------------------------------------------------------------------------------------

class Helicopter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animations = helicopter_animations
        self.animations_index = 0
        self.sprite = self.animations[self.animations_index]
        self.powerup = None
        self.distanation = None
        self.rect = self.sprite.get_rect()
        self.rect.top = 150
        self.timer = 120
        self.is_dropping = False

    # -----------------------------------------------------------------------------------------------------------------

    def spawn(self):
        self.pick_random_spot()
        self.get_powerup()
        channel2.play(helicopter_sound)
        # helicopter_sound.play()

    # -----------------------------------------------------------------------------------------------------------------

    def pick_random_spot(self):
        self.distanation = random.randint(100, screen_width - 100)

    # -----------------------------------------------------------------------------------------------------------------

    def update_sprite(self):
        sprite_index = (self.animations_index // 3) % 5
        self.sprite = self.animations[sprite_index]
        self.animations_index += 1
        if self.animations_index >= 100:
            self.animations_index = 0

    # -----------------------------------------------------------------------------------------------------------------

    def update(self):
        self.update_sprite()

        if self.rect.right == self.distanation:
            if not self.is_dropping:
                self.drop()
            else:
                if self.timer > 0:
                    self.timer -= 1
                else:
                    self.rect.right += 1
        else:
            self.rect.right += 1

        if self.rect.left >= screen_width:
            self.die()

    def draw(self):
        screen.blit(self.sprite, self.rect)

    # -----------------------------------------------------------------------------------------------------------------

    def die(self):
        self.kill()

    # -----------------------------------------------------------------------------------------------------------------

    def drop(self):
        self.is_dropping = True
        boxes.add(Box(self.rect.centerx, self.rect.centery, self.powerup))

    # -----------------------------------------------------------------------------------------------------------------

    def get_powerup(self):
        powerups = ["health", "shield", "HE1", "HE2", "HE3", "bomb"]
        probabilities = [35, 25, 15, 7, 3, 15]
        total_probability = sum(probabilities)
        random_num = random.randint(1, total_probability)
        cumulative_prob = 0
        for item, probability in zip(powerups, probabilities):
            cumulative_prob += probability
            if random_num <= cumulative_prob:
                selected_powerup = item
                break
        self.powerup = selected_powerup

    # -----------------------------------------------------------------------------------------------------------------


class Box(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup):
        super().__init__()
        self.x = x
        self.y = y
        self.powerup = powerup
        self.image = box_image
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y
        self.rounds_alive = 6

    # -----------------------------------------------------------------------------------------------------------------

    def draw(self):
        screen.blit(self.image, self.rect)

    # -----------------------------------------------------------------------------------------------------------------

    def pick_up(self, tank):
        global show_picked_item
        show_picked_item = [tank.name, self.powerup, 100]
        if self.powerup == "health":
            missing_health = tank.max_health - tank.health
            heal = tank.max_health // 5
            if missing_health < heal:
                heal = missing_health
            tank.health += heal
            pick_up_sound.play()
        elif self.powerup == "shield":
            tank.shield = tank.max_health // 3
            pick_up_sound.play()
        elif self.powerup == "HE1":
            tank.ammo_count["HE1"] += 1
            pick_up_sound.play()
        elif self.powerup == "HE2":
            tank.ammo_count["HE2"] += 1
            pick_up_sound.play()
        elif self.powerup == "HE3":
            tank.ammo_count["HE3"] += 1
            pick_up_sound.play()
        elif self.powerup == "bomb":
            tank.health -= tank.max_health // 5
            if tank.health <= 0:
                tank.die()
            else:
                hit_sound.play()
        self.kill()

    # -----------------------------------------------------------------------------------------------------------------

    def update(self):
        self.rect.y += 1
        if self.rect.bottom > screen_height:
            self.kill()
        collided_object = collision(self.rect, floor_rect + underground_rect)
        if collided_object is not None:
            self.rect.bottom = collided_object.top
        collided_tank = None
        for tank in tanks_playing.sprites():
            if tank.tank_rect.colliderect(self.rect):
                collided_tank = tank
        if collided_tank is not None:
            self.pick_up(collided_tank)


# -----------------------------------------------------------------------------------------------------------------


def destroy_ground(center_of_explosion, type, radius):
    if type == "HE1":
        radius = 100
    elif type == "HE2":
        radius = 120
    elif type == "HE3":
        radius = 150
    destroyed_blocks = []

    floor_rect_copy = floor_rect.copy()
    underground_rect_copy = underground_rect.copy()

    for block_rect in floor_rect_copy:
        if math.hypot(center_of_explosion[0] - block_rect.centerx,
                      center_of_explosion[1] - block_rect.centery) < radius:
            destroyed_blocks.append(block_rect)
            floor_rect.remove(block_rect)

    for block_rect in underground_rect_copy:
        if math.hypot(center_of_explosion[0] - block_rect.centerx,
                      center_of_explosion[1] - block_rect.centery) < radius:
            destroyed_blocks.append(block_rect)
            underground_rect.remove(block_rect)

    return destroyed_blocks


# -----------------------------------------------------------------------------------------------------------------

def display_stats(screen, current_tank):
    font = pygame.font.Font(None, 30)
    text = font.render("Current Tank: " + current_tank.name, True, '#FDDC5C')
    screen.blit(text, (35, 35))
    text = font.render("Health: " + str(current_tank.health) + "/" + str(current_tank.max_health), True, '#FDDC5C')
    screen.blit(text, (35, 65))
    text = font.render("Fuel: " + str(current_tank.fuel) + "/" + str(current_tank.max_fuel), True, '#FDDC5C')
    screen.blit(text, (35, 95))
    text = font.render("Gun Power: " + str(current_tank.gun_power), True, '#FDDC5C')
    screen.blit(text, (35, 125))
    text = font.render("Gun Angle: " + str(current_tank.gun_angle), True, '#FDDC5C')
    screen.blit(text, (35, 155))
    text = font.render("Bullet Type: " + str(current_tank.arsenal[current_tank.arsenal_index]), True, '#FDDC5C')
    screen.blit(text, (35, 185))

    big_HE1 = pygame.transform.scale2x(HE1)
    big_HE2 = pygame.transform.scale2x(HE2)
    big_HE3 = pygame.transform.scale2x(HE3)

    for i in range(int(current_tank.ammo_count['HE1'])):
        screen.blit(big_HE1, (screen_width - 65 - 35 * i, 35))
    for i in range(int(current_tank.ammo_count['HE2'])):
        screen.blit(big_HE2, (screen_width - 65 - 35 * i, 75))
    for i in range(int(current_tank.ammo_count['HE3'])):
        screen.blit(big_HE3, (screen_width - 65 - 35 * i, 115))


# -----------------------------------------------------------------------------------------------------------------

def between_rounds_screen():
    global tanks_playing, tanks, screen, floor_rect, underground_rect, level_number, space_background
    background_music.set_volume(0.3)
    risk.set_volume(0.3)
    channel2.stop()
    font = pygame.font.Font(None, 50)
    font_mid = pygame.font.Font(None, 75)
    font_big = pygame.font.Font(None, 100)

    for i in range(len(tanks.sprites())):
        buying = True
        if tanks.sprites()[i] == tanks_playing.sprites()[0]:
            tanks.sprites()[i].money += int(1.3 * (100 + (50 * (current_round - 1))))
        else:
            tanks.sprites()[i].money += 100 + (50 * (current_round - 1))
        while buying:
            screen.blit(space_background, (0, 0))

            text = font_big.render(f"PLAYER {tanks_playing.sprites()[0].name} WON!!!", True, "Cyan")
            text_rect = text.get_rect(center=(screen_width / 2, 100))
            screen.blit(text, text_rect)

            text = font_mid.render(f"UPGRADES for {tanks.sprites()[i].name}:", True, "Cyan")
            text_rect = text.get_rect(center=(screen_width / 2, 200))
            screen.blit(text, text_rect)
            # top
            text = font.render(f"HP +30 [COST {int(tanks.sprites()[i].max_health / 2)}     PRESS H]", True, "Red")
            screen.blit(text, (screen_width / 2 - 400, screen_height / 2 - 100))
            text = font.render(f"FUEL +30 [COST {int(tanks.sprites()[i].max_fuel / 2)}    PRESS F]", True, "Black")
            screen.blit(text, (screen_width / 2 - 400, screen_height / 2))
            text = font.render(f"HE1_AMMO +1 [COST 30]     PRESS 1", True, "Green")
            screen.blit(text, (screen_width / 2 - 400, screen_height / 2 + 100))
            text = font.render(f"HE2_AMMO +1 [COST 50]     PRESS 2", True, "Green")
            screen.blit(text, (screen_width / 2 - 400, screen_height / 2 + 200))
            text = font.render(f"HE3_AMMO +1 [COST 100]     PRESS 3", True, "Green")
            screen.blit(text, (screen_width / 2 - 400, screen_height / 2 + 300))
            # middle
            text = font.render(f"player {tanks.sprites()[i].name} is buying    [{tanks.sprites()[i].money}$ left]",
                               True, "Cyan")
            text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2 + 400))
            screen.blit(text, text_rect)
            pygame.draw.rect(screen, (50, 50, 50), text_rect, 2)
            text = font.render(f"PRESS ENTER TO GO TO NEXT PLAYER", True, "Black")
            screen.blit(text, (screen_width / 2 - 350, screen_height / 2 + 500))

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        buying = False
                    if event.key == pygame.K_h:
                        if int(tanks.sprites()[i].max_health / 2) <= tanks.sprites()[i].money:
                            upgrade_sound.play()
                            tanks.sprites()[i].money -= int(tanks.sprites()[i].max_health / 2)
                            tanks.sprites()[i].max_health += 30
                    if event.key == pygame.K_f:
                        if int(tanks.sprites()[i].max_fuel / 2) <= tanks.sprites()[i].money:
                            upgrade_sound.play()
                            tanks.sprites()[i].money -= int(tanks.sprites()[i].max_fuel / 2)
                            tanks.sprites()[i].max_fuel += 30
                    if event.key == pygame.K_1:
                        if 30 <= tanks.sprites()[i].money:
                            tanks.sprites()[i].money -= 30
                            tanks.sprites()[i].ammo_count["HE1"] += 1
                    if event.key == pygame.K_2:
                        if 50 <= tanks.sprites()[i].money:
                            tanks.sprites()[i].money -= 50
                            tanks.sprites()[i].ammo_count["HE2"] += 1
                    if event.key == pygame.K_3:
                        if 100 <= tanks.sprites()[i].money:
                            tanks.sprites()[i].money -= 100
                            tanks.sprites()[i].ammo_count["HE3"] += 1

            pygame.display.update()
            clock.tick(60)

    floor_rect, underground_rect, _, spawn_points, level_number = get_random_level(level_number)

    for i, tank in enumerate(tanks.sprites()):
        tank.health = tank.max_health
        tank.fuel = tank.max_fuel
        tank.velocity_y = 0
        tanks_playing = tanks.copy()
        tank.x = spawn_points[i][0]
        tank.y = spawn_points[i][1]
        tank.spawn()

    draw_background(screen)
    draw_borders(screen)
    draw_blocks(screen, floor_rect, strait_grass)
    draw_blocks(screen, underground_rect, strait_dirt)

    bullets.empty()
    boxes.empty()
    background_music.set_volume(0.6)
    risk.set_volume(0.6)


# -----------------------------------------------------------------------------------------------------------------

def sandbox_menu():
    global space_background
    pygame.mixer.pause()
    font = pygame.font.Font(None, 50)
    while True:
        screen.blit(space_background, (0, 0))

        text = font.render("This is the sandbox, a place to create levels designs and add them to the game.", True,
                           "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 100))
        screen.blit(text, text_rect)

        text = font.render("You have an empty space to place blocks and spawn points wherever you want.", True,
                           "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 200))
        screen.blit(text, text_rect)

        text = font.render("CONTROLLERS:", True, "RED")
        text_rect = text.get_rect(center=(screen_width / 2 - 550, 400))
        screen.blit(text, text_rect)

        text = font.render("Press left mouse button to place grass blocks", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 400))
        screen.blit(text, text_rect)

        text = font.render("Press right mouse button to place dirt blocks", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 500))
        screen.blit(text, text_rect)

        text = font.render("Press w to set a spawn point to a tank, you need 3 of them at list", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 600))
        screen.blit(text, text_rect)

        text = font.render("Press q to delete a block/spawn point, its a little buggy on spawn point sorry", True,
                           "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 700))
        screen.blit(text, text_rect)

        text = font.render("Press 9 to go back to starting screen", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 800))
        screen.blit(text, text_rect)

        text = font.render("press ESC to exit", True, "RED")
        screen.blit(text, (screen_width - 300, screen_height - 35))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.unpause()
                    return

        pygame.display.update()
        clock.tick(10)


# -----------------------------------------------------------------------------------------------------------------

def back_to_main_menu():
    global show_picked_item, tanks, tanks_playing, heli, was_helicopter, floor_rect, underground_rect, terrain, spawn_points, level_number
    pygame.mixer.pause()
    font_big = pygame.font.Font(None, 80)
    font_big_big = pygame.font.Font(None, 150)
    while True:
        text = font_big.render("ARE YOU SURE YOU WANT TO GO TO MAIN MENU?", True, "RED")
        text_rect = text.get_rect(center=(screen_width / 2, 100))
        screen.blit(text, text_rect)

        yes_text = font_big_big.render("YES", True, "RED")
        yes_text_rect = yes_text.get_rect(center=(screen_width / 2 - 200, screen_height / 2))
        screen.blit(yes_text, yes_text_rect)
        pygame.draw.rect(screen, (50, 50, 50), yes_text_rect, 2)

        no_text = font_big_big.render("NO", True, "RED")
        no_text_rect = no_text.get_rect(center=(screen_width / 2 + 200, screen_height / 2))
        screen.blit(no_text, no_text_rect)
        pygame.draw.rect(screen, (50, 50, 50), no_text_rect, 2)

        text = font_big.render("press ESC to go back (did not reset it is ok)", True, "RED")
        text_rect = text.get_rect(center=(screen_width / 2, screen_height - 100))
        screen.blit(text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.unpause()
                    return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if no_text_rect.collidepoint(mouse_pos):
                    pygame.mixer.unpause()
                    click_sound.play()
                    return True
                elif yes_text_rect.collidepoint(mouse_pos):
                    pygame.mixer.unpause()
                    click_sound.play()
                    channel1.stop()
                    channel2.stop()
                    show_picked_item = None

                    bullets.empty()
                    boxes.empty()

                    number_of_players, yes_or_no, names = starting_screen()

                    if yes_or_no == "YES":
                        draw_level()

                    floor_rect, underground_rect, terrain, spawn_points, level_number = get_random_level()

                    tanks = pygame.sprite.Group()
                    if number_of_players == 2:
                        tanks.add(Tank(spawn_points[0][0], spawn_points[0][1], names[0]))
                        tanks.add(Tank(spawn_points[1][0], spawn_points[1][1], names[1]))
                    elif number_of_players == 3:
                        tanks.add(Tank(spawn_points[0][0], spawn_points[0][1], names[0]))
                        tanks.add(Tank(spawn_points[1][0], spawn_points[1][1], names[1]))
                        tanks.add(Tank(spawn_points[2][0], spawn_points[2][1], names[2]))

                    tanks_playing = tanks.copy()

                    heli = pygame.sprite.GroupSingle()
                    heli.add(Helicopter())
                    heli.sprite.spawn()
                    was_helicopter = True

                    channel1.play(tracks[tracks_index], -1)

                    return False

        pygame.display.update()
        clock.tick(10)


# -----------------------------------------------------------------------------------------------------------------


def show_menu():
    global space_background
    pygame.mixer.pause()
    while True:
        # top
        screen.blit(space_background, (0, 0))
        font = pygame.font.Font(None, 50)

        text = font.render("The game is called Tank Fight, in the game there are a number of unique tanks and maps,",
                           True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 100))
        screen.blit(text, text_rect)

        text = font.render("Every round the tanks will spawn and take turns in shooting each other to DEATH !!!", True,
                           "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 175))
        screen.blit(text, text_rect)

        text = font.render("random powerups will drop from a helicopter once in a while (could be bad)", True,
                           "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 250))
        screen.blit(text, text_rect)

        text = font.render("fuel will recharge every round to its max and shield is 33% of max health", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 325))
        screen.blit(text, text_rect)

        text = font.render("HOW TO PLAY:", True, "RED")
        text_rect = text.get_rect(center=(screen_width / 2 - 600, 425))
        screen.blit(text, text_rect)

        text = font.render("Press A/D to move the tank left/right (as long as you have enough fuel)", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2 + 110, 425))
        screen.blit(text, text_rect)

        text = font.render("Press W/S to rotate the gun up/down (cannot go over 90 or under -60 degrees)", True,
                           "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 500))
        screen.blit(text, text_rect)

        text = font.render("Press UP/DOWN keys to add/remove power (cannot go over 10 or under 6)", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 575))
        screen.blit(text, text_rect)

        text = font.render("Press LEFT/RIGHT keys to change ammo type", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 650))
        screen.blit(text, text_rect)

        text = font.render("Press SPASS to shoot OR Press ENTER to skip the turn", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 725))
        screen.blit(text, text_rect)

        text = font.render("Press 9 to go back to starting screen", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, 825))
        screen.blit(text, text_rect)

        text = font.render("press ESC to exit", True, "RED")
        screen.blit(text, (screen_width - 300, screen_height - 35))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.unpause()
                    return

        pygame.display.update()
        clock.tick(10)


# -----------------------------------------------------------------------------------------------------------------

def starting_screen():
    global space_background
    number_of_players = 2
    yes_or_no = "NO"
    name1 = "Alice"
    name2 = "Bob"
    name3 = "Jerry"
    color_passive = pygame.Color('grey15')
    color_active = pygame.Color('lightskyblue3')
    name1_color = color_passive
    name2_color = color_passive
    name3_color = color_passive
    input_name = ""
    input_name_index = 0
    name_is_active = False
    while True:
        # top
        screen.blit(space_background, (0, 0))
        font = pygame.font.Font(None, 50)
        font_big = pygame.font.Font(None, 150)

        text = font.render("How many players are playing?", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2 - 300))
        screen.blit(text, text_rect)

        text = font.render("press ENTER to start", True, "#FFBA00")
        screen.blit(text, (screen_width - 400, screen_height - 200))

        text = font_big.render(f"{number_of_players}", True, (205, 205, 105))
        text_rect_players = text.get_rect(center=(screen_width / 2, screen_height / 2 - 100))
        screen.blit(text, text_rect_players)
        pygame.draw.rect(screen, (50, 50, 50), text_rect_players, 2)

        text = font.render("Enter name for tank 1:", True, "#FFBA00")
        text_rect = text.get_rect(topleft=(50, screen_height / 2 - 150))
        screen.blit(text, text_rect)

        text_name1 = font.render(f"{name1}", True, name1_color)
        text_rect_name1 = text_name1.get_rect(topleft=(screen_width / 2 - 300, screen_height / 2 - 150))
        screen.blit(text_name1, text_rect_name1)
        pygame.draw.rect(screen, (50, 50, 50), text_rect_name1, 2)

        text = font.render("Enter name for tank 2:", True, "#FFBA00")
        text_rect = text.get_rect(topleft=(50, screen_height / 2 - 100))
        screen.blit(text, text_rect)

        text_name2 = font.render(f"{name2}", True, name2_color)
        text_rect_name2 = text_name2.get_rect(topleft=(screen_width / 2 - 300, screen_height / 2 - 100))
        screen.blit(text_name2, text_rect_name2)
        pygame.draw.rect(screen, (50, 50, 50), text_rect_name2, 2)

        text = font.render("Enter name for tank 3:", True, "#FFBA00")
        text_rect = text.get_rect(topleft=(50, screen_height / 2 - 50))
        if number_of_players > 2:
            screen.blit(text, text_rect)

        text_name3 = font.render(f"{name3}", True, name3_color)
        text_rect_name3 = text_name3.get_rect(topleft=(screen_width / 2 - 300, screen_height / 2 - 50))
        if number_of_players > 2:
            screen.blit(text_name3, text_rect_name3)
            pygame.draw.rect(screen, (50, 50, 50), text_rect_name3, 2)

        text = font.render("do you want to go into sandbox?", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2 + 100))
        screen.blit(text, text_rect)

        text = font.render("(create a new level design)", True, "#FFBA00")
        text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2 + 150))
        screen.blit(text, text_rect)

        text = font_big.render(f"{yes_or_no}", True, (205, 205, 105))
        text_rect_sandbox = text.get_rect(center=(screen_width / 2, screen_height / 2 + 250))
        screen.blit(text, text_rect_sandbox)
        pygame.draw.rect(screen, (50, 50, 50), text_rect_sandbox, 2)

        text = font.render("EXIT", True, (205, 205, 105))
        text_rect_exit = text.get_rect(center=(screen_width - 100, 100))
        screen.blit(text, text_rect_exit)
        pygame.draw.rect(screen, (50, 50, 50), text_rect_exit, 2)

        if name1 == "" and input_name_index != 1:
            name1 = "Alice"
        if name2 == "" and input_name_index != 2:
            name2 = "Bob"
        if name3 == "" and input_name_index != 3:
            name3 = "Jerry"

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not name_is_active:
                    return number_of_players, yes_or_no, [name1, name2, name3]
                elif event.key == pygame.K_BACKSPACE and 12 > len(input_name) > 0 and name_is_active:
                    input_name = input_name[:-1]
                    if input_name_index == 1:
                        name1 = input_name
                    elif input_name_index == 2:
                        name2 = input_name
                    elif input_name_index == 3:
                        name3 = input_name
                elif 10 > len(input_name):
                    input_name += event.unicode
                    if input_name_index == 1:
                        name1 = input_name
                    elif input_name_index == 2:
                        name2 = input_name
                    elif input_name_index == 3:
                        name3 = input_name
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if text_rect_players.collidepoint(mouse_pos):
                    if number_of_players == 2:
                        number_of_players = 3
                    elif number_of_players == 3:
                        number_of_players = 2
                    click_sound.play()
                elif text_rect_sandbox.collidepoint(mouse_pos):
                    if yes_or_no == "YES":
                        yes_or_no = "NO"
                        click_sound.play()
                    else:
                        yes_or_no = "YES"
                        click_sound.play()
                elif text_rect_exit.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()

                if text_rect_name1.collidepoint(mouse_pos):
                    name1_color = color_active
                    name2_color = color_passive
                    name3_color = color_passive
                    name_is_active = True
                    input_name = name1
                    input_name_index = 1
                elif text_rect_name2.collidepoint(mouse_pos):
                    name1_color = color_passive
                    name2_color = color_active
                    name3_color = color_passive
                    name_is_active = True
                    input_name = name2
                    input_name_index = 2
                elif text_rect_name3.collidepoint(mouse_pos):
                    name1_color = color_passive
                    name2_color = color_passive
                    name3_color = color_active
                    name_is_active = True
                    input_name = name3
                    input_name_index = 3
                else:
                    name1_color = color_passive
                    name2_color = color_passive
                    name3_color = color_passive
                    name_is_active = False
                    input_name_index = 0

        pygame.display.update()
        clock.tick(60)


# -----------------------------------------------------------------------------------------------------------------

def collision(tank_rect, objects):
    for obj in objects:
        if obj.colliderect(tank_rect):
            return obj
    return None


# -----------------------------------------------------------------------------------------------------------------

def next_round(was_helicopter):
    global current_tank_index, tanks_playing, boxes, heli
    current_tank_index = (1 + current_tank_index) % len(tanks_playing.sprites())
    for box in boxes:
        box.rounds_alive -= 1
        if box.rounds_alive <= 0:
            box.kill()

    if not was_helicopter:
        if not heli.sprite:
            random_number = random.random()
            if random_number <= 0.25:
                heli.add(Helicopter())
                heli.sprite.spawn()
                return True
    return False


# -----------------------------------------------------------------------------------------------------------------

def crop_image(image, x, y, width, height):
    cropped = pygame.Surface((width, height), pygame.SRCALPHA)
    cropped.blit(image, (0, 0), (x, y, width, height))
    return cropped


# -----------------------------------------------------------------------------------------------------------------

def draw_blocks(screen, rects, image):
    for i in range(len(rects)):
        cropped_image = crop_image(image, 0, 0, 31, 31)
        # cropped_image_rect = cropped_image.get_rect(topleft=(i * 31 + 25, screen_height - 200))
        screen.blit(image, rects[i])


# -----------------------------------------------------------------------------------------------------------------

def draw_borders(screen, sandbox=False):
    global show_picked_item
    pygame.draw.rect(screen, (50, 50, 50), (0, screen_height - 50, screen_width, 50))
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, 25, screen_height))
    pygame.draw.rect(screen, (50, 50, 50), (screen_width - 25, 0, 25, screen_height))
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, screen_width, 25))

    font = pygame.font.Font(None, 75)
    text = font.render(f"ROUND {current_round}", True, "Black")
    if sandbox:
        text = font.render(f"SANDBOX", True, "Black")
    screen.blit(text, (screen_width / 2 - 125, 100))
    if show_picked_item != None:
        if show_picked_item[2] > 0:
            text = font.render(f"{show_picked_item[0]} picked up {show_picked_item[1]}", True, '#FDDC5C')
            text_rect = text.get_rect(center=(screen_width / 2, 200))
            screen.blit(text, text_rect)
            show_picked_item[2] -= 1
        else:
            show_picked_item = None


# -----------------------------------------------------------------------------------------------------------------

def draw_background(screen):
    global background
    screen.blit(background, (0, 0))
    cloud = pygame.image.load("assets/cloud1.gif").convert_alpha()
    cloud = pygame.transform.rotozoom(cloud, 0, 3)
    screen.blit(cloud, (100, 100))
    screen.blit(cloud, (800, 200))


current_tank_index = 0
current_round = 1


# -----------------------------------------------------------------------------------------------------------------

def draw_level():
    font_big = pygame.font.Font(None, 80)

    floor_rect = []
    underground_rect = []

    floor_rect_pos = []
    underground_rect_pos = []

    spawn_points = []

    timer = 100

    is_timer = False

    drawing = True
    while drawing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(spawn_points) > 2:
                        drawing = False
                    else:
                        is_timer = True

                elif event.key == pygame.K_q:
                    mouse_pos = pygame.mouse.get_pos()
                    x = (mouse_pos[0] - 25) // 31
                    y = (mouse_pos[1] - 35) // 30
                    if pygame.Rect(x * 31 + 25, y * 30 + 35, 31, 31) in underground_rect:
                        underground_rect.remove(pygame.Rect(x * 31 + 25, y * 30 + 35, 31, 31))
                        underground_rect_pos.remove([x * 31 + 25, y * 30 + 35])
                    elif pygame.Rect(x * 31 + 25, y * 30 + 35, 31, 31) in floor_rect:
                        floor_rect.remove(pygame.Rect(x * 31 + 25, y * 30 + 35, 31, 31))
                        floor_rect_pos.remove([x * 31 + 25, y * 30 + 35])
                    elif [x, y] in spawn_points:
                        spawn_points.remove([x, y])
                elif event.key == pygame.K_w:
                    mouse_pos = pygame.mouse.get_pos()
                    x = (mouse_pos[0] - 25) // 31
                    y = (mouse_pos[1] - 35) // 30
                    spawn_points.append([x, y])
                elif event.key == pygame.K_ESCAPE:
                    sandbox_menu()
                elif event.key == pygame.K_9:
                    if not back_to_main_menu():
                        return

        mouse_click = pygame.mouse.get_pressed()
        if mouse_click[0] == 1:
            mouse_pos = pygame.mouse.get_pos()
            x = (mouse_pos[0] - 25) // 31
            y = (mouse_pos[1] - 35) // 30
            if x >= 0 and y >= 0 and pygame.Rect(x * 31 + 25, y * 30 + 35, 31,
                                                 31) not in underground_rect + floor_rect:
                floor_rect.append(pygame.Rect(x * 31 + 25, y * 30 + 35, 31, 31))
                floor_rect_pos.append([x * 31 + 25, y * 30 + 35])
        elif mouse_click[2] == 1:
            mouse_pos = pygame.mouse.get_pos()
            x = (mouse_pos[0] - 25) // 31
            y = (mouse_pos[1] - 35) // 30
            if x >= 0 and y >= 0 and pygame.Rect(x * 31 + 25, y * 30 + 35, 31,
                                                 31) not in underground_rect + floor_rect:
                underground_rect.append(pygame.Rect(x * 31 + 25, y * 30 + 35, 31, 31))
                underground_rect_pos.append([x * 31 + 25, y * 30 + 35])
        draw_background(screen)
        draw_borders(screen, True)
        draw_blocks(screen, floor_rect, strait_grass)
        draw_blocks(screen, underground_rect, strait_dirt)

        text = font.render("press ESC for controllers", True, "RED")
        screen.blit(text, (screen_width - 300, screen_height - 35))

        if is_timer:
            if timer > 0:
                text = font_big.render("YOU NEED AT LIST 3 SPAWN POINTS", True, "RED")
                text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2))
                screen.blit(text, text_rect)
                timer -= 1
            else:
                is_timer = False
                timer = 100

        for spawn in spawn_points:
            pygame.draw.circle(screen, "BLUE", (spawn[0] * 31 + 25, spawn[1] * 30 + 35), 10)

        pygame.display.update()
        clock.tick(60)

    with open("new_level_data.txt", "a") as file:
        file.write(
            f"\nfloor_rect_pos = {floor_rect_pos}\nunderground_rect_pos = {underground_rect_pos}\nspawn positions = {spawn_points}\n\nlevel =\n[{underground_rect_pos},{underground_rect_pos},{spawn_points}]\n-----------------------------------------------")


# -----------------------------------------------------------------------------------------------------------------
def get_random_level(previous_level_number=None):
    while True:
        level_number = random.randint(0, len(levels) - 1)
        if level_number != previous_level_number:
            break

    floor_rect_pos = levels[level_number][0]
    underground_rect_pos = levels[level_number][1]
    spawn_points = copy.deepcopy(levels[level_number][2])
    spawn1 = spawn_points[random.randint(0, len(spawn_points) - 1)]
    spawn_points.remove(spawn1)
    spawn2 = spawn_points[random.randint(0, len(spawn_points) - 1)]
    spawn_points.remove(spawn2)
    spawn3 = spawn_points[random.randint(0, len(spawn_points) - 1)]
    random_spawn_points = [spawn1, spawn2, spawn3]

    floor_rect = [pygame.Rect(floor_rect_pos[i][0], floor_rect_pos[i][1], 31, 31) for i in range(len(floor_rect_pos))]
    underground_rect = [pygame.Rect(underground_rect_pos[i][0], underground_rect_pos[i][1], 31, 31) for i in
                        range(len(underground_rect_pos))]

    terrain = floor_rect + underground_rect
    return floor_rect, underground_rect, terrain, random_spawn_points, level_number


# -----------------------------------------------------------------------------------------------------------------

show_picked_item = None

bullets = pygame.sprite.Group()

boxes = pygame.sprite.Group()

heli = pygame.sprite.GroupSingle()

number_of_players, yes_or_no, names = starting_screen()

if yes_or_no == "YES":
    draw_level()

floor_rect, underground_rect, terrain, spawn_points, level_number = get_random_level()

tanks = pygame.sprite.Group()
if number_of_players == 2:
    tanks.add(Tank(spawn_points[0][0], spawn_points[0][1], names[0]))
    tanks.add(Tank(spawn_points[1][0], spawn_points[1][1], names[1]))
elif number_of_players == 3:
    tanks.add(Tank(spawn_points[0][0], spawn_points[0][1], names[0]))
    tanks.add(Tank(spawn_points[1][0], spawn_points[1][1], names[1]))
    tanks.add(Tank(spawn_points[2][0], spawn_points[2][1], names[2]))

tanks_playing = tanks.copy()

heli.add(Helicopter())
heli.sprite.spawn()
was_helicopter = True

channel1.play(tracks[tracks_index], -1)
# -----------------------------------------------------------------------------------------------------------------


while True:
    if len(tanks_playing.sprites()) < 2:
        if heli.sprite:
            heli.sprite.die()
        winning_sound.play()
        between_rounds_screen()
        current_round += 1
        heli.add(Helicopter())
        heli.sprite.spawn()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                try:
                    tanks_playing.sprites()[current_tank_index].shoot()
                    was_helicopter = next_round(was_helicopter)
                except IndexError:
                    pass
            if event.key == pygame.K_RETURN:
                try:
                    tanks_playing.sprites()[current_tank_index].fuel = tanks_playing.sprites()[
                        current_tank_index].max_fuel
                except IndexError:
                    pass
                current_tank_index = (current_tank_index + 1) % len(tanks_playing)
            elif event.key == pygame.K_RIGHT:
                tanks_playing.sprites()[current_tank_index].change_ammo_type(1)
            elif event.key == pygame.K_LEFT:
                tanks_playing.sprites()[current_tank_index].change_ammo_type(-1)
            elif event.key == pygame.K_ESCAPE:
                show_menu()
            elif event.key == pygame.K_9:
                if not back_to_main_menu():
                    break

    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]:
        try:
            tanks_playing.sprites()[current_tank_index].move("right")
        except IndexError:
            pass
    elif keys[pygame.K_a]:
        try:
            tanks_playing.sprites()[current_tank_index].move("left")
        except IndexError:
            pass
    elif keys[pygame.K_w]:
        try:
            tanks_playing.sprites()[current_tank_index].rotate_gun(1)
        except IndexError:
            pass
    elif keys[pygame.K_s]:
        try:
            tanks_playing.sprites()[current_tank_index].rotate_gun(-1)
        except IndexError:
            pass
    elif keys[pygame.K_UP]:
        try:
            if tanks_playing.sprites()[current_tank_index].gun_power < tanks_playing.sprites()[
                current_tank_index].max_gun_power:
                tanks_playing.sprites()[current_tank_index].gun_power += 0.25
        except IndexError:
            pass
    elif keys[pygame.K_DOWN]:
        try:
            if tanks_playing.sprites()[current_tank_index].gun_power > 6:
                tanks_playing.sprites()[current_tank_index].gun_power -= 0.25
        except IndexError:
            pass

    draw_background(screen)
    draw_borders(screen)

    draw_blocks(screen, floor_rect, strait_grass)
    draw_blocks(screen, underground_rect, strait_dirt)

    for tank in tanks_playing.sprites():
        try:
            if tank == tanks_playing.sprites()[current_tank_index]:
                display_stats(screen, tank)
                tank.draw_parabola(screen)
        except IndexError:
            pass
        tank.update(screen, floor_rect + underground_rect)
        tank.draw(screen)

    for bullet in bullets.sprites():
        bullet.update_bullet()
        bullet.draw()

    if heli.sprite:
        heli.sprite.draw()
        heli.sprite.update()

    for box in boxes.sprites():
        box.update()
        box.draw()

    text = font.render("press ESC for controllers", True, "RED")
    screen.blit(text, (screen_width - 300, screen_height - 35))

    pygame.display.update()
    clock.tick(60)
