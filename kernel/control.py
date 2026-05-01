import pygame
import math
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from .check import Cube2x2, COLORS

@dataclass
class Vec3:
    x: float
    y: float
    z: float

CUBIE_SIZE = 80
GAP = 4

class CubeRenderer:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.center_x = screen_width // 2 - 100
        self.center_y = screen_height // 2
        
        self.angle_x = -0.6
        self.angle_y = 0.5
        
        self.is_dragging = False
        self.last_mouse: Optional[Tuple[int, int]] = None
        
        self.selected_layer: Optional[Dict] = None
        self.is_row_mode = True
        
        self.clicked_face: Optional[Dict] = None
        self.click_time = 0
        self.DOUBLE_CLICK_TIME = 400
        
        self.animating = False
        self.anim_axis: Optional[str] = None
        self.anim_layer_idx: Optional[int] = None
        self.anim_angle = 0.0
        self.anim_target = 0.0
        self.anim_speed = 6.0
        self.anim_move: Optional[str] = None
        
        self.cubie_positions = [
            (-1, -1, -1), (-1, -1, 1),
            (-1, 1, -1), (-1, 1, 1),
            (1, -1, -1), (1, -1, 1),
            (1, 1, -1), (1, 1, 1),
        ]
    
    def _rotate_x(self, p: Vec3, angle_deg: float) -> Vec3:
        rad = math.radians(angle_deg)
        cos = math.cos(rad)
        sin = math.sin(rad)
        return Vec3(p.x, p.y * cos - p.z * sin, p.y * sin + p.z * cos)
    
    def _rotate_y(self, p: Vec3, angle_deg: float) -> Vec3:
        rad = math.radians(angle_deg)
        cos = math.cos(rad)
        sin = math.sin(rad)
        return Vec3(p.x * cos + p.z * sin, p.y, -p.x * sin + p.z * cos)
    
    def _rotate_z(self, p: Vec3, angle_deg: float) -> Vec3:
        rad = math.radians(angle_deg)
        cos = math.cos(rad)
        sin = math.sin(rad)
        return Vec3(p.x * cos - p.y * sin, p.x * sin + p.y * cos, p.z)
    
    def _apply_view_rotation(self, p: Vec3) -> Vec3:
        p = self._rotate_x(p, math.degrees(self.angle_x))
        p = self._rotate_y(p, math.degrees(self.angle_y))
        return p
    
    def _is_in_anim_layer(self, cubie_idx: Tuple[int, int, int]) -> bool:
        if not self.animating:
            return False
        x, y, z = cubie_idx
        if self.anim_axis == 'x':
            return x == self.anim_layer_idx
        elif self.anim_axis == 'y':
            return y == self.anim_layer_idx
        elif self.anim_axis == 'z':
            return z == self.anim_layer_idx
        return False
    
    def _apply_anim_rotation(self, p: Vec3, cubie_idx: Tuple[int, int, int], cubie_center: Vec3) -> Vec3:
        if not self._is_in_anim_layer(cubie_idx):
            return p
        
        local = Vec3(p.x - cubie_center.x, p.y - cubie_center.y, p.z - cubie_center.z)
        
        if self.anim_axis == 'x':
            rotated = self._rotate_x(local, self.anim_angle)
        elif self.anim_axis == 'y':
            rotated = self._rotate_y(local, self.anim_angle)
        elif self.anim_axis == 'z':
            rotated = self._rotate_z(local, self.anim_angle)
        else:
            rotated = local
        
        return Vec3(cubie_center.x + rotated.x, cubie_center.y + rotated.y, cubie_center.z + rotated.z)
    
    def _project(self, p: Vec3) -> Tuple[int, int]:
        scale = 600.0 / (600.0 + p.z) if (600.0 + p.z) > 0 else 0.1
        x = int(self.center_x + p.x * scale)
        y = int(self.center_y - p.y * scale)
        return (x, y)
    
    def _get_cubie_center(self, idx: Tuple[int, int, int]) -> Vec3:
        x, y, z = idx
        step = CUBIE_SIZE + GAP
        return Vec3(x * step / 2, y * step / 2, z * step / 2)
    
    def _get_cubie_faces(self, cubie_idx: Tuple[int, int, int], cube: Cube2x2) -> List[Dict]:
        faces = []
        x, y, z = cubie_idx
        s = CUBIE_SIZE / 2
        center = self._get_cubie_center(cubie_idx)
        
        face_defs = [
            ('U', [
                Vec3(center.x - s, center.y + s, center.z - s),
                Vec3(center.x + s, center.y + s, center.z - s),
                Vec3(center.x + s, center.y + s, center.z + s),
                Vec3(center.x - s, center.y + s, center.z + s),
            ]),
            ('D', [
                Vec3(center.x - s, center.y - s, center.z + s),
                Vec3(center.x + s, center.y - s, center.z + s),
                Vec3(center.x + s, center.y - s, center.z - s),
                Vec3(center.x - s, center.y - s, center.z - s),
            ]),
            ('F', [
                Vec3(center.x - s, center.y - s, center.z + s),
                Vec3(center.x + s, center.y - s, center.z + s),
                Vec3(center.x + s, center.y + s, center.z + s),
                Vec3(center.x - s, center.y + s, center.z + s),
            ]),
            ('B', [
                Vec3(center.x + s, center.y - s, center.z - s),
                Vec3(center.x - s, center.y - s, center.z - s),
                Vec3(center.x - s, center.y + s, center.z - s),
                Vec3(center.x + s, center.y + s, center.z - s),
            ]),
            ('L', [
                Vec3(center.x - s, center.y - s, center.z - s),
                Vec3(center.x - s, center.y - s, center.z + s),
                Vec3(center.x - s, center.y + s, center.z + s),
                Vec3(center.x - s, center.y + s, center.z - s),
            ]),
            ('R', [
                Vec3(center.x + s, center.y - s, center.z + s),
                Vec3(center.x + s, center.y - s, center.z - s),
                Vec3(center.x + s, center.y + s, center.z - s),
                Vec3(center.x + s, center.y + s, center.z + s),
            ]),
        ]
        
        for face_name, corners in face_defs:
            color_code = cube.get_sticker(cubie_idx, face_name)
            if color_code and color_code in COLORS:
                faces.append({
                    'name': face_name,
                    'corners': corners,
                    'color': COLORS[color_code],
                    'cubie_idx': cubie_idx,
                })
        
        return faces
    
    def _face_visible(self, face: Dict) -> bool:
        corners = face['corners']
        cubie_idx = face['cubie_idx']
        cubie_center = self._get_cubie_center(cubie_idx)
        
        transformed = []
        for p in corners:
            anim_p = self._apply_anim_rotation(p, cubie_idx, cubie_center)
            view_p = self._apply_view_rotation(anim_p)
            transformed.append(view_p)
        
        if len(transformed) < 3:
            return False
        
        v1 = Vec3(
            transformed[1].x - transformed[0].x,
            transformed[1].y - transformed[0].y,
            transformed[1].z - transformed[0].z
        )
        v2 = Vec3(
            transformed[2].x - transformed[0].x,
            transformed[2].y - transformed[0].y,
            transformed[2].z - transformed[0].z
        )
        
        cross_z = v1.x * v2.y - v1.y * v2.x
        return cross_z > 0
    
    def _face_depth(self, face: Dict) -> float:
        corners = face['corners']
        cubie_idx = face['cubie_idx']
        cubie_center = self._get_cubie_center(cubie_idx)
        
        avg_z = 0.0
        for p in corners:
            anim_p = self._apply_anim_rotation(p, cubie_idx, cubie_center)
            view_p = self._apply_view_rotation(anim_p)
            avg_z += view_p.z
        
        return avg_z / 4
    
    def _point_in_poly(self, px: int, py: int, poly: List[Tuple[int, int]]) -> bool:
        n = len(poly)
        inside = False
        x1, y1 = poly[0]
        for i in range(n + 1):
            x2, y2 = poly[i % n]
            if py > min(y1, y2):
                if py <= max(y1, y2):
                    if px <= max(x1, x2):
                        if y1 != y2:
                            xinters = (py - y1) * (x2 - x1) / (y2 - y1) + x1
                        if x1 == x2 or px <= xinters:
                            inside = not inside
            x1, y1 = x2, y2
        return inside
    
    def _is_layer_selected(self, cubie_idx: Tuple[int, int, int]) -> bool:
        if not self.selected_layer:
            return False
        
        x, y, z = cubie_idx
        axis = self.selected_layer['axis']
        layer = self.selected_layer['layer']
        
        if axis == 'x':
            return x == layer
        elif axis == 'y':
            return y == layer
        elif axis == 'z':
            return z == layer
        return False
    
    def get_all_faces(self, cube: Cube2x2) -> List[Dict]:
        all_faces = []
        for idx in self.cubie_positions:
            faces = self._get_cubie_faces(idx, cube)
            all_faces.extend(faces)
        return all_faces
    
    def handle_event(self, event: pygame.event.Event, cube: Cube2x2) -> Tuple[bool, Optional[str], Any]:
        if self.animating:
            return (False, None, None)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                faces = self.get_all_faces(cube)
                clickable = []
                
                for face in faces:
                    if not self._face_visible(face):
                        continue
                    
                    cubie_idx = face['cubie_idx']
                    cubie_center = self._get_cubie_center(cubie_idx)
                    
                    screen_points = []
                    for p in face['corners']:
                        anim_p = self._apply_anim_rotation(p, cubie_idx, cubie_center)
                        view_p = self._apply_view_rotation(anim_p)
                        screen_points.append(self._project(view_p))
                    
                    if self._point_in_poly(event.pos[0], event.pos[1], screen_points):
                        clickable.append({
                            'face': face,
                            'depth': self._face_depth(face),
                            'screen_points': screen_points
                        })
                
                if clickable:
                    clickable.sort(key=lambda f: f['depth'])
                    clicked = clickable[-1]
                    face = clicked['face']
                    
                    current_time = pygame.time.get_ticks()
                    
                    if self.clicked_face and \
                       self.clicked_face['name'] == face['name'] and \
                       self.clicked_face['cubie_idx'] == face['cubie_idx'] and \
                       (current_time - self.click_time) < self.DOUBLE_CLICK_TIME:
                        self.is_row_mode = not self.is_row_mode
                    
                    self._select_layer(face)
                    self.clicked_face = face
                    self.click_time = current_time
                    
                    return (True, 'select', self._get_selection_text())
                else:
                    self.is_dragging = True
                    self.last_mouse = event.pos
                    self.selected_layer = None
                    return (True, 'deselect', "")
            
            elif event.button == 3:
                move = self._get_move()
                if move:
                    return (True, 'rotate', move)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
                self.last_mouse = None
        
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging and self.last_mouse:
                dx = event.pos[0] - self.last_mouse[0]
                dy = event.pos[1] - self.last_mouse[1]
                self.angle_y += dx * 0.008
                self.angle_x += dy * 0.008
                self.angle_x = max(-math.pi / 2.5, min(math.pi / 2.5, self.angle_x))
                self.last_mouse = event.pos
                return (True, 'view', None)
        
        return (False, None, None)
    
    def _select_layer(self, face: Dict):
        face_name = face['name']
        x, y, z = face['cubie_idx']
        
        if face_name in ['U', 'D']:
            if self.is_row_mode:
                self.selected_layer = {'axis': 'z', 'layer': z}
            else:
                self.selected_layer = {'axis': 'x', 'layer': x}
        elif face_name in ['F', 'B']:
            if self.is_row_mode:
                self.selected_layer = {'axis': 'y', 'layer': y}
            else:
                self.selected_layer = {'axis': 'x', 'layer': x}
        elif face_name in ['L', 'R']:
            if self.is_row_mode:
                self.selected_layer = {'axis': 'y', 'layer': y}
            else:
                self.selected_layer = {'axis': 'z', 'layer': z}
    
    def _get_selection_text(self) -> str:
        if not self.selected_layer:
            return ""
        
        axis = self.selected_layer['axis']
        mode = "行模式" if self.is_row_mode else "列模式"
        
        axis_names = {'x': 'X轴', 'y': 'Y轴', 'z': 'Z轴'}
        return f"已选中: {axis_names[axis]}层 ({mode})"
    
    def _get_move(self) -> Optional[str]:
        if not self.selected_layer:
            return None
        
        axis = self.selected_layer['axis']
        layer = self.selected_layer['layer']
        
        if axis == 'y':
            if layer == 1:
                return 'U'
            else:
                return "D'"
        elif axis == 'x':
            if layer == 1:
                return 'R'
            else:
                return "L'"
        elif axis == 'z':
            if layer == 1:
                return 'F'
            else:
                return "B'"
        
        return None
    
    def start_animation(self, move: str):
        self.animating = True
        self.anim_angle = 0.0
        self.anim_move = move
        
        if move == 'U':
            self.anim_axis = 'y'
            self.anim_layer_idx = 1
            self.anim_target = -90.0
        elif move == "U'":
            self.anim_axis = 'y'
            self.anim_layer_idx = 1
            self.anim_target = 90.0
        elif move == 'D':
            self.anim_axis = 'y'
            self.anim_layer_idx = -1
            self.anim_target = 90.0
        elif move == "D'":
            self.anim_axis = 'y'
            self.anim_layer_idx = -1
            self.anim_target = -90.0
        elif move == 'R':
            self.anim_axis = 'x'
            self.anim_layer_idx = 1
            self.anim_target = 90.0
        elif move == "R'":
            self.anim_axis = 'x'
            self.anim_layer_idx = 1
            self.anim_target = -90.0
        elif move == 'L':
            self.anim_axis = 'x'
            self.anim_layer_idx = -1
            self.anim_target = -90.0
        elif move == "L'":
            self.anim_axis = 'x'
            self.anim_layer_idx = -1
            self.anim_target = 90.0
        elif move == 'F':
            self.anim_axis = 'z'
            self.anim_layer_idx = 1
            self.anim_target = 90.0
        elif move == "F'":
            self.anim_axis = 'z'
            self.anim_layer_idx = 1
            self.anim_target = -90.0
        elif move == 'B':
            self.anim_axis = 'z'
            self.anim_layer_idx = -1
            self.anim_target = -90.0
        elif move == "B'":
            self.anim_axis = 'z'
            self.anim_layer_idx = -1
            self.anim_target = 90.0
    
    def update_animation(self) -> Tuple[bool, Optional[str]]:
        if not self.animating:
            return (False, None)
        
        step = self.anim_speed if self.anim_target > 0 else -self.anim_speed
        self.anim_angle += step
        
        done = False
        if (self.anim_target > 0 and self.anim_angle >= self.anim_target) or \
           (self.anim_target < 0 and self.anim_angle <= self.anim_target):
            self.animating = False
            self.anim_angle = 0.0
            done = True
        
        return (done, self.anim_move if done else None)
    
    def draw(self, surface: pygame.Surface, cube: Cube2x2):
        all_faces = self.get_all_faces(cube)
        
        draw_list = []
        for face in all_faces:
            if not self._face_visible(face):
                continue
            
            cubie_idx = face['cubie_idx']
            cubie_center = self._get_cubie_center(cubie_idx)
            
            is_selected = self._is_layer_selected(cubie_idx)
            is_animating = self._is_in_anim_layer(cubie_idx)
            
            screen_points = []
            avg_z = 0.0
            for p in face['corners']:
                anim_p = self._apply_anim_rotation(p, cubie_idx, cubie_center)
                view_p = self._apply_view_rotation(anim_p)
                screen_points.append(self._project(view_p))
                avg_z += view_p.z
            
            avg_z /= 4
            
            color = face['color']
            if is_selected and not is_animating:
                color = tuple(min(255, c + 50) for c in color)
            
            draw_list.append({
                'points': screen_points,
                'color': color,
                'depth': avg_z,
            })
        
        draw_list.sort(key=lambda f: f['depth'])
        
        for item in draw_list:
            pygame.draw.polygon(surface, item['color'], item['points'])
            pygame.draw.polygon(surface, (30, 30, 30), item['points'], 2)
