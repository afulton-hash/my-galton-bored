import pygame
import random
import math
import sys
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
BALL_RADIUS = 8
PEG_RADIUS = 5
BIN_WIDTH = 40
MAX_BAR_HEIGHT = 120
PEG_SPACING = 40
FONT_SIZE = 22  # Slightly smaller font
SMALL_FONT_SIZE = 18  # Smaller for percentages

# Colors
DARK_BLUE = (20, 25, 40)
WHITE = (255, 255, 255)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
CURVE_COLOR = (0, 200, 200)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galton Board Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', FONT_SIZE)
small_font = pygame.font.SysFont('Arial', SMALL_FONT_SIZE)

class GaltonBoard:
    def __init__(self, rows=10, ball_count=100):
        self.rows = rows
        self.ball_count = ball_count
        self.reset()
        
    def reset(self):
        self.balls = []
        self.bins = [0] * (self.rows + 1)
        self.dropped_balls = 0
        self.dropping = False
        self.setup_pegs()
        
    def setup_pegs(self):
        self.pegs = []
        self.bottom_y = 150 + self.rows * PEG_SPACING
        for row in range(self.rows):
            for col in range(row + 1):
                x = WIDTH//2 - row*(PEG_SPACING//2) + col*PEG_SPACING
                y = 150 + row * PEG_SPACING
                self.pegs.append((x, y))
    
    def add_ball(self):
        if self.dropped_balls < self.ball_count:
            self.balls.append({
                'x': WIDTH//2,
                'y': 100,
                'speed': 3,
                'direction': 0,
                'falling': True
            })
            self.dropped_balls += 1
    
    def update(self):
        for ball in self.balls[:]:
            if ball['falling']:
                ball['y'] += ball['speed']
                
                if ball['y'] >= self.bottom_y:
                    ball['falling'] = False
                    bin_idx = min(max(0, (ball['x'] - (WIDTH//2 - self.rows*PEG_SPACING//2)) // BIN_WIDTH), len(self.bins)-1)
                    self.bins[bin_idx] += 1
                    self.balls.remove(ball)
                    continue
                    
                for peg_x, peg_y in self.pegs:
                    dist = math.sqrt((peg_x-ball['x'])**2 + (peg_y-ball['y'])**2)
                    if dist < PEG_RADIUS + BALL_RADIUS:
                        ball['direction'] = random.choice([-1, 1])
                
                ball['x'] += ball['direction'] * 2
    
    def draw_normal_curve(self):
        if self.dropped_balls == 0:
            return
            
        points = []
        for i in range(self.rows + 1):
            x = WIDTH//2 - (self.rows * BIN_WIDTH)//2 + i * BIN_WIDTH + BIN_WIDTH//2
            prob = math.comb(self.rows, i) * (0.5**self.rows)
            y = HEIGHT - 170 - (prob * 300)
            points.append((x, y))
        
        if len(points) > 1:
            pygame.draw.lines(screen, CURVE_COLOR, False, points, 2)
    
    def draw(self):
        screen.fill(DARK_BLUE)
        
        # Draw pegs
        for x, y in self.pegs:
            pygame.draw.circle(screen, BLUE, (x, y), PEG_RADIUS)
        
        # Draw bins with perfectly spaced percentages
        max_bin = max(self.bins) if max(self.bins) > 0 else 1
        for i in range(self.rows + 1):
            x = WIDTH//2 - (self.rows * BIN_WIDTH)//2 + i * BIN_WIDTH
            height = (self.bins[i]/max_bin) * MAX_BAR_HEIGHT
            
            # Bin bar
            pygame.draw.rect(screen, RED, (x, HEIGHT-150-height, BIN_WIDTH-4, height), 0, 3)
            
            # Ball count
            count_text = font.render(str(self.bins[i]), True, WHITE)
            screen.blit(count_text, (x + BIN_WIDTH//2 - count_text.get_width()//2, HEIGHT-170-height))
            
            # Theoretical probability - staggered positioning
            prob = math.comb(self.rows, i) * (0.5**self.rows)
            prob_text = small_font.render(f"{prob*100:.1f}%", True, YELLOW)
            screen.blit(prob_text, (x + BIN_WIDTH//2 - prob_text.get_width()//2, HEIGHT-120 if i % 2 else HEIGHT-135))
            
            # Actual percentage - staggered with more spacing
            if self.dropped_balls > 0:
                actual = (self.bins[i]/self.dropped_balls)*100
                actual_text = small_font.render(f"{actual:.1f}%", True, GREEN)
                screen.blit(actual_text, (x + BIN_WIDTH//2 - actual_text.get_width()//2, HEIGHT-90 if i % 2 else HEIGHT-105))
        
        # Draw curve
        self.draw_normal_curve()
        
        # Draw balls
        for ball in self.balls:
            pygame.draw.circle(screen, WHITE, (int(ball['x']), int(ball['y'])), BALL_RADIUS)
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        # Draw buttons
        pygame.draw.rect(screen, BLUE, (20, 20, 120, 40), border_radius=5)
        start_text = font.render("START", True, WHITE)
        screen.blit(start_text, (70 - start_text.get_width()//2, 30))
        
        pygame.draw.rect(screen, RED, (20, 70, 120, 40), border_radius=5)
        reset_text = font.render("RESET", True, WHITE)
        screen.blit(reset_text, (70 - reset_text.get_width()//2, 80))
        
        # Row controls
        pygame.draw.rect(screen, BLUE, (20, 120, 50, 30), border_radius=3)
        pygame.draw.rect(screen, BLUE, (90, 120, 50, 30), border_radius=3)
        plus_text = font.render("+", True, WHITE)
        minus_text = font.render("-", True, WHITE)
        screen.blit(plus_text, (45 - plus_text.get_width()//2, 125))
        screen.blit(minus_text, (115 - minus_text.get_width()//2, 125))
        row_text = font.render(f"Rows: {self.rows}", True, WHITE)
        screen.blit(row_text, (20, 160))
        
        # Ball controls
        pygame.draw.rect(screen, BLUE, (20, 200, 50, 30), border_radius=3)
        pygame.draw.rect(screen, BLUE, (90, 200, 50, 30), border_radius=3)
        screen.blit(plus_text, (45 - plus_text.get_width()//2, 205))
        screen.blit(minus_text, (115 - minus_text.get_width()//2, 205))
        ball_text = font.render(f"Balls: {self.ball_count}", True, WHITE)
        screen.blit(ball_text, (20, 240))
        
        # Stats
        dropped_text = font.render(f"Dropped: {self.dropped_balls}/{self.ball_count}", True, WHITE)
        screen.blit(dropped_text, (20, 280))

def main():
    board = GaltonBoard()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                # START button
                if 20 <= x <= 140 and 20 <= y <= 60:
                    board.reset()
                    board.dropping = True
                
                # RESET button
                elif 20 <= x <= 140 and 70 <= y <= 110:
                    board.reset()
                
                # Row +
                elif 20 <= x <= 70 and 120 <= y <= 150 and board.rows < 15:
                    board.rows += 1
                    board.reset()
                
                # Row -
                elif 90 <= x <= 140 and 120 <= y <= 150 and board.rows > 5:
                    board.rows -= 1
                    board.reset()
                
                # Balls +
                elif 20 <= x <= 70 and 200 <= y <= 230 and board.ball_count < 500:
                    board.ball_count += 50
                    board.reset()
                
                # Balls -
                elif 90 <= x <= 140 and 200 <= y <= 230 and board.ball_count > 50:
                    board.ball_count -= 50
                    board.reset()
        
        # Add new balls if dropping
        if board.dropping and random.random() < 0.1 and board.dropped_balls < board.ball_count:
            board.add_ball()
        
        board.update()
        board.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
