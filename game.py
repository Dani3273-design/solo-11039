import pygame
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kernel.check import Cube2x2, scramble_cube
from kernel.ui import UI
from kernel.control import CubeRenderer

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
BACKGROUND_COLOR = (40, 44, 52)
FPS = 60

class Game:
    def __init__(self):
        pygame.init()
        
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2阶魔方游戏")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.cube = Cube2x2()
        self.renderer = CubeRenderer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        self.ui.scramble_button.on_click = self._on_scramble
        self.ui.reset_button.on_click = self._on_reset
        
        self.scramble_thread: Optional[threading.Thread] = None
        
        print("=" * 40)
        print("2阶魔方游戏已启动")
        print("=" * 40)
    
    def _on_scramble(self):
        if self.scramble_thread and self.scramble_thread.is_alive():
            return
        if self.renderer.animating:
            return
        
        self.ui.set_status("正在打乱...", (200, 200, 100))
        
        def task():
            temp_cube = Cube2x2()
            scramble_cube(temp_cube, 30)
            
            for face in ['U', 'D', 'F', 'B', 'L', 'R']:
                for i in range(2):
                    for j in range(2):
                        self.cube.state[face][i][j] = temp_cube.state[face][i][j]
            
            self.renderer.selected_layer = None
            self.ui.set_activation_info("")
            self.ui.set_status("已打乱", (100, 200, 100))
        
        self.scramble_thread = threading.Thread(target=task, daemon=True)
        self.scramble_thread.start()
    
    def _on_reset(self):
        if self.renderer.animating:
            return
        
        self.cube.reset()
        self.renderer.selected_layer = None
        self.ui.set_activation_info("")
        self.ui.set_status("已重置", (100, 200, 100))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.renderer.animating:
                continue
            
            if self.ui.handle_event(event):
                continue
            
            handled, action, data = self.renderer.handle_event(event, self.cube)
            
            if action == 'select':
                self.ui.set_activation_info(data if data else "")
                self.ui.clear_status()
            elif action == 'deselect':
                self.ui.set_activation_info("")
            elif action == 'rotate' and data:
                self.renderer.start_animation(data)
    
    def update(self):
        anim_done, move = self.renderer.update_animation()
        
        if anim_done and move:
            self.cube.apply_move(move)
            
            if self.cube.is_solved():
                self.ui.set_status("恭喜！魔方已还原！", (100, 255, 100))
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        self.renderer.draw(self.screen, self.cube)
        
        self.ui.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
