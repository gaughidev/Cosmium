import math
import random
import time
import tkinter as tk

WIDTH = 900
HEIGHT = 600
FPS = 60

BLACK = '#070912'
WHITE = '#f6f7fb'
BLUE = '#7ec8ff'
GOLD = '#ffd166'
RED = '#ff5f5f'
GRAY = '#a1a9bb'


class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Rocket Run: Stardust Escape')
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg=BLACK, highlightthickness=0)
        self.canvas.pack()

        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        self.root.bind('<space>', self.restart_if_game_over)

        self.keys = {'left': False, 'right': False, 'up': False, 'down': False}
        self.reset()
        self.last_time = time.time()
        self.tick()
        self.root.mainloop()

    def reset(self):
        self.rocket = {
            'x': WIDTH / 2,
            'y': HEIGHT - 70,
            'radius': 18,
            'speed': 330,
            'angle': 0,
        }
        self.asteroids = []
        self.stardust = []
        self.score = 0
        self.game_over = False
        self.asteroid_timer = 0
        self.dust_timer = 0
        self.stars = []
        for _ in range(120):
            self.stars.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(1, 3),
                'speed': random.uniform(10, 70),
            })

    def on_key_press(self, event):
        key = event.keysym.lower()
        if key == 'left' or key == 'a':
            self.keys['left'] = True
        elif key == 'right' or key == 'd':
            self.keys['right'] = True
        elif key == 'up' or key == 'w':
            self.keys['up'] = True
        elif key == 'down' or key == 's':
            self.keys['down'] = True

    def on_key_release(self, event):
        key = event.keysym.lower()
        if key == 'left' or key == 'a':
            self.keys['left'] = False
        elif key == 'right' or key == 'd':
            self.keys['right'] = False
        elif key == 'up' or key == 'w':
            self.keys['up'] = False
        elif key == 'down' or key == 's':
            self.keys['down'] = False

    def restart_if_game_over(self, event):
        if self.game_over:
            self.reset()

    def spawn_asteroid(self):
        size = random.randint(18, 42)
        asteroid = {
            'x': random.randint(size, WIDTH - size),
            'y': -size - 20,
            'size': size,
            'speed': random.randint(140, 250),
            'rotation': random.uniform(0, 2 * math.pi),
            'spin': random.uniform(-1.5, 1.5),
            'shape': [],
        }
        for i in range(8):
            angle = (i / 8) * (2 * math.pi)
            radius = size * random.uniform(0.7, 1.2)
            asteroid['shape'].append((math.cos(angle) * radius, math.sin(angle) * radius))
        self.asteroids.append(asteroid)

    def spawn_stardust(self):
        self.stardust.append({
            'x': random.randint(10, WIDTH - 10),
            'y': -12,
            'radius': 7,
            'speed': random.randint(90, 190),
            'phase': random.uniform(0, 2 * math.pi),
            'twinkle': random.uniform(0.6, 1.5),
        })

    def update(self, dt):
        if self.game_over:
            for star in self.stars:
                star['y'] += star['speed'] * dt
                if star['y'] > HEIGHT:
                    star['y'] = -5
                    star['x'] = random.randint(0, WIDTH)
            return

        move_x = (1 if self.keys['right'] else 0) - (1 if self.keys['left'] else 0)
        move_y = (1 if self.keys['down'] else 0) - (1 if self.keys['up'] else 0)

        if move_x or move_y:
            length = math.hypot(move_x, move_y)
            move_x /= length
            move_y /= length
            self.rocket['x'] += move_x * self.rocket['speed'] * dt
            self.rocket['y'] += move_y * self.rocket['speed'] * dt

        self.rocket['x'] = max(self.rocket['radius'], min(WIDTH - self.rocket['radius'], self.rocket['x']))
        self.rocket['y'] = max(self.rocket['radius'], min(HEIGHT - self.rocket['radius'], self.rocket['y']))

        if move_x or move_y:
            self.rocket['angle'] = math.degrees(math.atan2(move_y, move_x)) + 90

        for star in self.stars:
            star['y'] += star['speed'] * dt
            if star['y'] > HEIGHT:
                star['y'] = -5
                star['x'] = random.randint(0, WIDTH)

        self.asteroid_timer += dt * 1000
        self.dust_timer += dt * 1000

        spawn_interval = max(500, 1500 - self.score * 28)
        if self.asteroid_timer >= spawn_interval:
            self.spawn_asteroid()
            self.asteroid_timer = 0

        if self.dust_timer >= 1100:
            self.spawn_stardust()
            self.dust_timer = 0

        for asteroid in self.asteroids:
            asteroid['y'] += asteroid['speed'] * dt
            asteroid['rotation'] += asteroid['spin'] * dt

            dx = asteroid['x'] - self.rocket['x']
            dy = asteroid['y'] - self.rocket['y']
            if math.hypot(dx, dy) < asteroid['size'] + self.rocket['radius']:
                self.game_over = True

        for dust in self.stardust:
            dust['y'] += dust['speed'] * dt
            dust['phase'] += dt * 8
            dx = dust['x'] - self.rocket['x']
            dy = dust['y'] - self.rocket['y']
            if math.hypot(dx, dy) < dust['radius'] + self.rocket['radius']:
                self.score += 1
                self.stardust.remove(dust)
                break

        self.asteroids = [a for a in self.asteroids if a['y'] < HEIGHT + 100]
        self.stardust = [d for d in self.stardust if d['y'] < HEIGHT + 40]

    def draw_rocket(self):
        x = int(self.rocket['x'])
        y = int(self.rocket['y'])
        angle = math.radians(self.rocket['angle'])
        base = [
            (0, -22),
            (-12, 18),
            (0, 8),
            (12, 18),
        ]

        points = []
        for px, py in base:
            rx = px * math.cos(angle) - py * math.sin(angle)
            ry = px * math.sin(angle) + py * math.cos(angle)
            points.append((x + rx, y + ry))

        self.canvas.create_polygon(points, fill=WHITE, outline=BLUE, width=2)

        flame = []
        for px, py in [( -6, 18), (6, 18), (0, 24 + random.randint(0, 6))]:
            rx = px * math.cos(angle) - py * math.sin(angle)
            ry = px * math.sin(angle) + py * math.cos(angle)
            flame.append((x + rx, y + ry))
        if random.random() < 0.9:
            self.canvas.create_polygon(flame, fill=GOLD, outline='')

    def draw_asteroid(self, asteroid):
        points = []
        cx = asteroid['x']
        cy = asteroid['y']
        rotation = asteroid['rotation']
        for px, py in asteroid['shape']:
            x = cx + px * math.cos(rotation) - py * math.sin(rotation)
            y = cy + px * math.sin(rotation) + py * math.cos(rotation)
            points.append((x, y))
        self.canvas.create_polygon(points, fill=GRAY, outline=RED, width=2)

    def draw_stardust(self, dust):
        shimmer = 0.5 + 0.5 * math.sin(dust['phase'])
        radius = int(dust['radius'] * (0.8 + shimmer * 0.8))
        self.canvas.create_oval(
            dust['x'] - radius,
            dust['y'] - radius,
            dust['x'] + radius,
            dust['y'] + radius,
            fill=GOLD,
            outline=WHITE,
            width=2,
        )

    def draw(self):
        self.canvas.delete('all')

        for star in self.stars:
            self.canvas.create_oval(star['x'], star['y'], star['x'] + star['size'], star['y'] + star['size'], fill=WHITE)

        for asteroid in self.asteroids:
            self.draw_asteroid(asteroid)

        for dust in self.stardust:
            self.draw_stardust(dust)

        self.draw_rocket()

        self.canvas.create_text(30, 20, anchor='w', text=f'Stardust: {self.score}', fill=WHITE, font=('Arial', 20, 'bold'))

        if self.game_over:
            self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill='#0b0d1a', stipple='gray25')
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2 - 30, text='Mission Failed', fill=RED, font=('Arial', 36, 'bold'))
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2 + 25, text='Press SPACE to restart', fill=WHITE, font=('Arial', 22))

    def tick(self):
        now = time.time()
        dt = min(0.033, now - self.last_time)
        self.last_time = now
        self.update(dt)
        self.draw()
        self.root.after(int(1000 / FPS), self.tick)


if __name__ == '__main__':
    Game()