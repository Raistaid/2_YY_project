import os, sys
from pygame import*
from random import randint
from time import time as timer


intro_text = ['Space Shooter',
              'Для передвижения влева и вправо используйте стрелочки,',
              'Чтобы стрелять нажимайте пробел.',
              'У вас ограниченное количество пуль',
              'поэтому периодически происходит перезарядка',
              '10, пролетевших мимо целей = поражение',
              'Берегитесь астероидов',
              'Они не уничтожаются выстрелами',
              '20 попаданий = победа',
              'Приятной игры!']
font.init()
font1 = font.SysFont('Arial', 80)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))
font2 = font.SysFont('Arial', 36)

clock = time.Clock()
win_width = 700
win_height = 500
screen_size = (700, 500)
screen = display.set_mode(screen_size)
FPS = 50

score = 0
goal = 20
lost = 0
max_lost = 10
life = 3


def terminate():
    quit()
    sys.exit


def load_image(name, color_key=None):
    fullname = os.path.join('imag', name)
    try:
        imagee = image.load(fullname)
    except error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    imagee = imagee.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return imagee

mixer.init()
mixer.music.load('space.mp3')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')
img_back = load_image('galaxy.jpg')
img_bullet = load_image('bullet.png')
img_hero = load_image('rocket.png')
img_enemy = load_image('ufo.png')
img_ast = load_image('asteroid.png')
img_exp = load_image('explosion.png')

def show_screen(text, fon_file):
    fon = transform.scale(load_image(fon_file), screen_size)
    screen.blit(fon, (0, 0))
    fontt = font.Font(None, 30)
    text_coord = 50
    for line in text:
        string_rendered = fontt.render(line, True, Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for ev in event.get():
            if ev.type == QUIT:
                terminate()
            elif ev.type == KEYDOWN or \
                    ev.type == MOUSEBUTTONDOWN:
                return
        display.flip()
        clock.tick(FPS)


class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(player_image,(size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)


class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            if self not in asteroids:
               lost = lost + 1


class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()


show_screen(intro_text, 'fon.jpg')
display.set_caption('Shooter')
window = display.set_mode((win_width,win_height))
background = transform.scale(img_back,(win_width, win_height))
ship = Player(img_hero, 5, win_height - 100,80, 100, 10)
monsters = sprite.Group()
asteroids = sprite.Group()

for i in range(1, 3):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40,80, 50, randint(1, 5))
    monsters.add(monster)
for i in range(1, 6):
    asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 5))
    asteroids.add(asteroid)

bullets = sprite.Group()
finish = False
run = True
rel_time = False
num_fire = 0
while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < 5 and rel_time == False:
                    num_fire = num_fire + 1
                    fire_sound.play()
                    ship.fire()
                if num_fire >= 5 and rel_time == False:
                    last_time = timer()
                    rel_time = True
    if not finish:
        window.blit(background,(0,0))
        ship.update()
        monsters.update()
        asteroids.update()
        bullets.update()
        ship.reset()
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)
        if rel_time is True:
            now_time = timer()
            if now_time - last_time < 3:
                reload = font2.render('Wait,reload...', 1, (150, 0, 0))
                window.blit(reload, (260, 460))
            else:
                num_fire = 0
                rel_time = False
        collides = sprite.groupcollide(monsters, bullets, True, True)

        for c in collides:
            score = score + 1
            monster = Enemy(img_enemy,randint(80, win_width - 80), -40, 80, 50, randint(1,5))
            monsters.add(monster)
        if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(ship, asteroids, False):
            sprite.spritecollide(ship, monsters, True)
            sprite.spritecollide(ship, asteroids, True)
            life = life - 1
        if life == 0 or lost >= max_lost:
            finish = True
            window.blit(lose, (200, 200))
        if score >= goal:
            finish = True
            window.blit(win, (200, 200))
        text = font2.render('Счет' + ' ' + str(score),1, (255, 255, 255))
        window.blit(text, (10, 20))
        text_lose = font2.render('Пропущено' + ' ' + str(lost), 1, (255, 55, 255))
        window.blit(text_lose,(10, 50))
        if life == 3:
            life_color=(0, 150, 0)
        if life == 2:
            life_color=(150, 150, 0)
        if life == 1:
            life_color = (150, 0, 0)
        text_life = font1.render(str(life), 1, life_color)
        window.blit(text_life,(650, 10))
        display.update()
    else:
        finish = False
        score = 0
        lost = 0
        num_fire = 0
        life = 3
        for b in bullets:
            b.kill()
        for m in monsters:
            m.kill()
        for a in asteroids:
            a.kill()
        time.delay(3000)
        for i in range(1, 5):
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)
        for i in range(1, 6):
            asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
            asteroids.add(asteroid)
    time.delay(50)

