import pygame
import pygame.freetype
import os
from typing import Tuple, Callable, Optional

class Button:
    def __init__(self, 
                 x: int, 
                 y: int, 
                 width: int, 
                 height: int, 
                 text: str,
                 font: pygame.freetype.Font,
                 text_color: Tuple[int, int, int] = (255, 255, 255),
                 bg_color: Tuple[int, int, int] = (70, 130, 180),
                 hover_color: Tuple[int, int, int] = (100, 160, 210),
                 border_color: Tuple[int, int, int] = (50, 100, 150),
                 border_radius: int = 8):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.is_hovered = False
        self.on_click: Optional[Callable] = None
    
    def draw(self, surface: pygame.Surface):
        color = self.hover_color if self.is_hovered else self.bg_color
        
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=self.border_radius)
        
        text_surf, text_rect = self.font.render(self.text, self.text_color)
        text_rect.center = self.rect.center
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        
        return False


def find_chinese_font() -> Optional[pygame.freetype.Font]:
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/AppleGothic.ttf",
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = pygame.freetype.Font(path, 24)
                test_text = "测试中文"
                surf, _ = font.render(test_text, (0, 0, 0))
                if surf.get_width() > 20:
                    print(f"成功加载中文字体: {path}")
                    return font
            except Exception as e:
                print(f"尝试加载字体 {path} 失败: {e}")
                continue
    
    return None


class UI:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.panel_x = screen_width - 200
        self.panel_width = 180
        self.panel_height = screen_height - 40
        
        chinese_font = find_chinese_font()
        
        if chinese_font:
            self.font_large = pygame.freetype.Font(chinese_font.path, 22)
            self.font_medium = pygame.freetype.Font(chinese_font.path, 18)
            self.font_small = pygame.freetype.Font(chinese_font.path, 14)
        else:
            print("警告: 未找到中文字体，使用默认字体")
            try:
                self.font_large = pygame.freetype.SysFont('simhei, microsoftyahei, pingfang', 22)
                self.font_medium = pygame.freetype.SysFont('simhei, microsoftyahei, pingfang', 18)
                self.font_small = pygame.freetype.SysFont('simhei, microsoftyahei, pingfang', 14)
            except:
                self.font_large = pygame.freetype.Font(None, 22)
                self.font_medium = pygame.freetype.Font(None, 18)
                self.font_small = pygame.freetype.Font(None, 14)
        
        self.buttons: list[Button] = []
        self._create_buttons()
        
        self.status_text = ""
        self.status_color = (255, 255, 255)
        self.activation_info = ""
    
    def _create_buttons(self):
        button_width = 140
        button_height = 45
        button_x = self.panel_x + (self.panel_width - button_width) // 2
        button_y = 80
        
        self.scramble_button = Button(
            x=button_x,
            y=button_y,
            width=button_width,
            height=button_height,
            text="打乱魔方",
            font=self.font_medium,
            bg_color=(70, 130, 180),
            hover_color=(100, 160, 210),
            border_color=(50, 100, 150)
        )
        self.buttons.append(self.scramble_button)
        
        reset_y = button_y + button_height + 20
        self.reset_button = Button(
            x=button_x,
            y=reset_y,
            width=button_width,
            height=button_height,
            text="重置魔方",
            font=self.font_medium,
            bg_color=(60, 179, 113),
            hover_color=(90, 209, 143),
            border_color=(40, 149, 83)
        )
        self.buttons.append(self.reset_button)
    
    def draw(self, surface: pygame.Surface):
        panel_rect = pygame.Rect(
            self.panel_x - 10, 
            20, 
            self.panel_width + 20, 
            self.panel_height
        )
        
        s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (245, 248, 255, 240), (0, 0, panel_rect.width, panel_rect.height), border_radius=12)
        surface.blit(s, panel_rect.topleft)
        pygame.draw.rect(surface, (180, 180, 180), panel_rect, 2, border_radius=12)
        
        title_surf, title_rect = self.font_large.render("控制面板", (50, 50, 50))
        title_rect.centerx = self.panel_x + self.panel_width // 2
        title_rect.y = 35
        surface.blit(title_surf, title_rect)
        
        for button in self.buttons:
            button.draw(surface)
        
        info_y = self.reset_button.rect.bottom + 30
        
        if self.activation_info:
            label_surf, label_rect = self.font_small.render("当前选中:", (80, 80, 80))
            label_rect.topleft = (self.panel_x + 10, info_y)
            surface.blit(label_surf, label_rect)
            info_y += label_rect.height + 5
            
            info_surf, info_rect = self.font_small.render(self.activation_info, (60, 120, 60))
            info_rect.topleft = (self.panel_x + 10, info_y)
            surface.blit(info_surf, info_rect)
            info_y += info_rect.height + 25
        else:
            hint_surf, hint_rect = self.font_small.render("点击魔方选择层", (120, 120, 120))
            hint_rect.topleft = (self.panel_x + 10, info_y)
            surface.blit(hint_surf, hint_rect)
            info_y += hint_rect.height + 25
        
        help_title_surf, help_title_rect = self.font_medium.render("操作说明", (50, 50, 50))
        help_title_rect.topleft = (self.panel_x + 10, info_y)
        surface.blit(help_title_surf, help_title_rect)
        info_y += help_title_rect.height + 12
        
        help_texts = [
            ("左键拖空白", "旋转视角"),
            ("左键点魔方", "选择层"),
            ("双击", "切换行/列"),
            ("右键", "旋转层"),
        ]
        
        for label, desc in help_texts:
            line_y = info_y
            
            label_surf, label_rect = self.font_small.render(label, (70, 70, 180))
            label_rect.topleft = (self.panel_x + 10, line_y)
            surface.blit(label_surf, label_rect)
            
            desc_surf, desc_rect = self.font_small.render(desc, (100, 100, 100))
            desc_rect.topleft = (self.panel_x + 10 + label_rect.width + 8, line_y)
            surface.blit(desc_surf, desc_rect)
            
            info_y += max(label_rect.height, desc_rect.height) + 8
        
        if self.status_text:
            status_surf, status_rect = self.font_medium.render(self.status_text, self.status_color)
            status_rect.centerx = self.screen_width // 2 - 100
            status_rect.bottom = self.screen_height - 25
            
            bg_rect = status_rect.inflate(24, 12)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (0, 0, 0, 200), (0, 0, bg_rect.width, bg_rect.height), border_radius=6)
            surface.blit(bg_surf, bg_rect.topleft)
            
            surface.blit(status_surf, status_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False
    
    def set_status(self, text: str, color: Tuple[int, int, int] = (255, 255, 255)):
        self.status_text = text
        self.status_color = color
    
    def set_activation_info(self, info: str):
        self.activation_info = info
    
    def clear_status(self):
        self.status_text = ""
