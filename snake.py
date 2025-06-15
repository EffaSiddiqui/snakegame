import pygame
import sys
import random
import time
from collections import deque
import heapq

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ENHANCED SNAKE GAME")

# Fonts
FONT = pygame.font.SysFont('consolas', 22, bold=True)
BIG_FONT = pygame.font.SysFont('arial', 32, bold=True)
BUTTON_FONT = pygame.font.SysFont('arial', 28, bold=True)

# Colors
BG_COLOR = (20, 20, 20)
HEAD_COLOR = (0, 255, 100)
BODY_COLOR = (0, 180, 80)
FOOD_COLOR = (255, 60, 60)
OBSTACLE_COLOR = (100, 100, 100)
ENEMY_COLOR = (255, 200, 0)
EYE_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

# Load background image
try:
    bg_image = pygame.image.load("bgimage.png")
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    bg_image = None

# Load game over background image
try:
    gameover_bg = pygame.image.load("snakeimage.png")
    gameover_bg = pygame.transform.scale(gameover_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    gameover_bg = None

# Load sounds
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except:
        print(f"Failed to load {path}")
        return None

click_sound = load_sound("click.mp3")
bite_sound = load_sound("snakesound.mp3")
gameover_sound = load_sound("gamefinish.wav")

def play_click():
    if click_sound:
        click_sound.play()

def play_background_music():
    try:
        pygame.mixer.music.load("bg_music.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Failed to play background music:", e)

def play_gameover_music():
    try:
        pygame.mixer.music.stop()
        if gameover_sound:
            gameover_sound.play()
    except Exception as e:
        print("Game Over sound error:", e)

# High score heap
high_scores = []

class Snake:
    def __init__(self, color=HEAD_COLOR):
        self.body = deque([[10, 10]])
        self.direction = [1, 0]
        self.grow_amount = 0
        self.color = color
        self.history = []  # Stack for storing movement history

    def move(self):
        new_head = [self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1]]
        self.body.appendleft(new_head)
        self.history.append(list(self.body))  # Store move history (stack)
        if len(self.history) > 20:
            self.history.pop(0)
        if self.grow_amount > 0:
            self.grow_amount -= 1
        else:
            self.body.pop()

    def grow(self, amount=2):
        self.grow_amount += amount

    def draw(self):
        for i, segment in enumerate(self.body):
            x, y = segment[0] * GRID_SIZE, segment[1] * GRID_SIZE
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, self.color, rect, border_radius=5 if i else 8)
            if i == 0:
                pygame.draw.circle(screen, EYE_COLOR, (x + 6, y + 6), 3)
                pygame.draw.circle(screen, EYE_COLOR, (x + 14, y + 6), 3)

    def collides_with_self(self):
        return list(self.body)[0] in list(self.body)[1:]

    def length(self):
        return len(self.body)

class Food:
    def __init__(self):
        self.position = self.random_position([])

    def random_position(self, snake_body):
        while True:
            pos = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
            if pos not in snake_body:
                return pos

    def respawn(self, snake_body):
        self.position = self.random_position(snake_body)

    def draw(self):
        x, y = self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE
        pygame.draw.rect(screen, FOOD_COLOR, (x, y, GRID_SIZE, GRID_SIZE), border_radius=6)

class Obstacle:
    def __init__(self, count):
        self.positions = []
        self.positions_set = set()
        self.count = count

    def spawn(self, snake_body, food_pos):
        self.positions.clear()
        self.positions_set.clear()
        while len(self.positions) < self.count:
            pos = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
            if pos not in snake_body and pos != food_pos:
                self.positions.append(pos)
                self.positions_set.add(tuple(pos))

    def draw(self):
        for pos in self.positions:
            x, y = pos[0] * GRID_SIZE, pos[1] * GRID_SIZE
            pygame.draw.rect(screen, OBSTACLE_COLOR, (x, y, GRID_SIZE, GRID_SIZE), border_radius=4)

def draw_score(score):
    text = FONT.render(f"SCORE: {score}", True, TEXT_COLOR)
    screen.blit(text, (SCREEN_WIDTH - text.get_width() - 20, 10))

def move_enemy(enemy, target, move_queue):
    head = enemy.body[0]
    dx, dy = 0, 0
    if head[0] < target[0]: dx = 1
    elif head[0] > target[0]: dx = -1
    elif head[1] < target[1]: dy = 1
    elif head[1] > target[1]: dy = -1
    enemy.direction = [dx, dy]
    move_queue.append(tuple(head))
    if len(move_queue) > 30:
        move_queue.popleft()
    enemy.move()

def show_menu():
    while True:
        screen.blit(bg_image, (0, 0)) if bg_image else screen.fill((30, 30, 30))
        title = BIG_FONT.render("SNAKE GAME", True, TEXT_COLOR)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        play_button = pygame.Rect(200, 250, 200, 60)
        quit_button = pygame.Rect(200, 330, 200, 60)

        for rect, label, color in zip([play_button, quit_button], ["PLAY", "QUIT"], [(0, 200, 0), (200, 0, 0)]):
            pygame.draw.rect(screen, color, rect, border_radius=12)
            text = BUTTON_FONT.render(label, True, TEXT_COLOR)
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    play_click()
                    time.sleep(1)
                    play_background_music()
                    return
                elif quit_button.collidepoint(event.pos):
                    play_click()
                    pygame.quit()
                    sys.exit()

def game_over_screen(score):
    play_gameover_music()
    heapq.heappush(high_scores, score)
    if len(high_scores) > 5:
        heapq.heappop(high_scores)

    restart_btn = pygame.Rect(SCREEN_WIDTH // 2 - 180 - 30, 470, 180, 60)
    quit_btn = pygame.Rect(SCREEN_WIDTH // 2 + 30, 470, 180, 60)

    while True:
        screen.blit(gameover_bg, (0, 0)) if gameover_bg else screen.fill(BG_COLOR)

        title = BIG_FONT.render(f"GAME OVER! SCORE: {score}", True, (255, 0, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        pygame.draw.rect(screen, (0, 200, 0), restart_btn, border_radius=10)
        restart_text = BUTTON_FONT.render("PLAY AGAIN", True, TEXT_COLOR)
        screen.blit(restart_text, (restart_btn.centerx - restart_text.get_width() // 2, restart_btn.centery - restart_text.get_height() // 2))

        pygame.draw.rect(screen, (200, 0, 0), quit_btn, border_radius=10)
        quit_text = BUTTON_FONT.render("QUIT", True, TEXT_COLOR)
        screen.blit(quit_text, (quit_btn.centerx - quit_text.get_width() // 2, quit_btn.centery - quit_text.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn.collidepoint(event.pos):
                    play_click()
                    return True
                elif quit_btn.collidepoint(event.pos):
                    play_click()
                    pygame.quit()
                    sys.exit()

def main():
    while True:
        show_menu()
        snake = Snake()
        enemy = Snake(color=ENEMY_COLOR)
        food = Food()
        obstacles = Obstacle(5)
        obstacles.spawn(list(snake.body) + list(enemy.body), food.position)
        score = 0
        enemy_move_counter = 0
        enemy_move_queue = deque()

        while True:
            screen.fill(BG_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and snake.direction != [0, 1]: snake.direction = [0, -1]
            if keys[pygame.K_DOWN] and snake.direction != [0, -1]: snake.direction = [0, 1]
            if keys[pygame.K_LEFT] and snake.direction != [1, 0]: snake.direction = [-1, 0]
            if keys[pygame.K_RIGHT] and snake.direction != [-1, 0]: snake.direction = [1, 0]

            snake.move()
            if enemy_move_counter >= 3:
                move_enemy(enemy, food.position, enemy_move_queue)
                enemy_move_counter = 0
            enemy_move_counter += 1

            if list(snake.body)[0] == food.position:
                bite_sound and bite_sound.play()
                snake.grow()
                score += 1
                food.respawn(list(snake.body) + list(enemy.body) + obstacles.positions)
                obstacles.spawn(list(snake.body) + list(enemy.body), food.position)

            if list(enemy.body)[0] == food.position:
                enemy.grow()
                food.respawn(list(snake.body) + list(enemy.body) + obstacles.positions)
                obstacles.spawn(list(snake.body) + list(enemy.body), food.position)

            if (list(snake.body)[0] in list(enemy.body) and enemy.length() >= snake.length()) or \
               snake.collides_with_self() or \
               tuple(snake.body[0]) in obstacles.positions_set or \
               not (0 <= snake.body[0][0] < GRID_WIDTH and 0 <= snake.body[0][1] < GRID_HEIGHT):
                if not game_over_screen(score): return
                break

            if list(snake.body)[0] in list(enemy.body) and snake.length() > enemy.length():
                bite_sound and bite_sound.play()
                extra = enemy.length()
                snake.grow(extra)
                score += extra
                enemy = Snake(color=ENEMY_COLOR)

            food.draw()
            obstacles.draw()
            snake.draw()
            enemy.draw()
            draw_score(score)

            pygame.display.flip()
            clock.tick(10 + score // 5)

if __name__ == '__main__':
    main()
