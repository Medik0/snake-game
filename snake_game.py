import pygame
import sys
import random
import json
from heapq import heappop, heappush

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

UP = (0, -GRID_SIZE)
DOWN = (0, GRID_SIZE)
LEFT = (-GRID_SIZE, 0)
RIGHT = (GRID_SIZE, 0)

POWER_UP_TYPES = {
    'speed': {'color': GREEN},
    'slow': {'color': BLUE},
    'reverse': {'color': RED}
}

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.high_score = self.load_high_score()
        self.reset_game()

    def load_high_score(self):
        try:
            with open('high_score.json', 'r') as f:
                return json.load(f).get('high_score', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def save_high_score(self):
        with open('high_score.json', 'w') as f:
            json.dump({'high_score': self.high_score}, f)

    def reset_game(self):
        self.snake = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.food = self.generate_food()
        self.power_ups = []
        self.game_over = False
        self.auto_play = False
        self.ai_path = []
        self.score = 0
        self.base_speed = 10
        self.current_speed = self.base_speed

    def generate_food(self):
        while True:
            pos = (random.randrange(0, SCREEN_WIDTH // GRID_SIZE) * GRID_SIZE,
                   random.randrange(0, SCREEN_HEIGHT // GRID_SIZE) * GRID_SIZE)
            if pos not in self.snake:
                return pos

    def generate_power_up(self):
        p_type = random.choice(list(POWER_UP_TYPES.keys()))
        while True:
            pos = (random.randrange(0, SCREEN_WIDTH // GRID_SIZE) * GRID_SIZE,
                   random.randrange(0, SCREEN_HEIGHT // GRID_SIZE) * GRID_SIZE)
            if pos not in self.snake and pos != self.food:
                return (pos, p_type)

    def get_neighbors(self, node):
        result = []
        for dx, dy in [(-GRID_SIZE, 0), (GRID_SIZE, 0), (0, -GRID_SIZE), (0, GRID_SIZE)]:
            nx, ny = node[0] + dx, node[1] + dy
            if 0 <= nx < SCREEN_WIDTH and 0 <= ny < SCREEN_HEIGHT:
                if (nx, ny) not in self.snake[:-1]:
                    result.append((nx, ny))
        return result

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star_pathfinding(self, start, end):
        open_list = []
        heappush(open_list, (0, start))
        came_from = {}
        g_score = {start: 0}

        while open_list:
            _, current = heappop(open_list)

            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, end)
                    heappush(open_list, (f_score, neighbor))

        return []

    def move_snake(self):
        head = self.snake[0]

        if self.auto_play:
            self.ai_path = self.a_star_pathfinding(head, self.food)
            if self.ai_path:
                next_pos = self.ai_path[0]
                self.direction = (next_pos[0] - head[0], next_pos[1] - head[1])

        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        if (new_head in self.snake or 
            new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or 
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT):
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
            if random.random() < 0.4:
                self.power_ups.append(self.generate_power_up())
        else:
            self.snake.pop()

        for power_up in self.power_ups[:]:
            if new_head == power_up[0]:
                p_type = power_up[1]
                if p_type == 'speed':
                    self.current_speed = min(25, self.current_speed + 3)
                elif p_type == 'slow':
                    self.current_speed = max(5, self.current_speed - 3)
                elif p_type == 'reverse':
                    self.direction = (-self.direction[0], -self.direction[1])
                self.power_ups.remove(power_up)

    def draw(self):
        self.screen.fill(WHITE)
        
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, (230, 230, 230), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, (230, 230, 230), (0, y), (SCREEN_WIDTH, y))

        for pos in self.snake:
            pygame.draw.rect(self.screen, BLACK, pygame.Rect(pos[0], pos[1], GRID_SIZE, GRID_SIZE))

        pygame.draw.rect(self.screen, RED, pygame.Rect(self.food[0], self.food[1], GRID_SIZE, GRID_SIZE))

        for pos, p_type in self.power_ups:
            pygame.draw.rect(self.screen, POWER_UP_TYPES[p_type]['color'], pygame.Rect(pos[0], pos[1], GRID_SIZE, GRID_SIZE))

        text_score = self.font.render(f"Score: {self.score}", True, BLACK)
        text_high = self.font.render(f"High Score: {self.high_score}", True, BLACK)
        text_ai = self.font.render(f"AI Auto-Play (A): {'ON' if self.auto_play else 'OFF'}", True, BLUE)
        
        self.screen.blit(text_score, (10, 10))
        self.screen.blit(text_high, (10, 40))
        self.screen.blit(text_ai, (10, 70))

        pygame.display.flip()

    def main_menu(self):
        while True:
            self.screen.fill(WHITE)
            title = self.font.render("Snake Game", True, BLACK)
            play_text = self.font.render("Press Enter to Play", True, BLACK)
            quit_text = self.font.render("Press Q to Quit", True, BLACK)

            self.screen.blit(title, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(play_text, (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2))
            self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 40))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

    def play_game(self):
        self.reset_game()

        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.auto_play = not self.auto_play
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif not self.auto_play:
                        if event.key == pygame.K_LEFT and self.direction != RIGHT:
                            self.direction = LEFT
                        elif event.key == pygame.K_RIGHT and self.direction != LEFT:
                            self.direction = RIGHT
                        elif event.key == pygame.K_UP and self.direction != DOWN:
                            self.direction = UP
                        elif event.key == pygame.K_DOWN and self.direction != UP:
                            self.direction = DOWN

            self.move_snake()
            self.draw()
            self.clock.tick(self.current_speed)

        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

if __name__ == "__main__":
    game = SnakeGame()
    while True:
        game.main_menu()
        game.play_game()
