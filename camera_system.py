"""
═══════════════════════════════════════════════════════════════════
FIRST-PERSON CAMERA SYSTEM
═══════════════════════════════════════════════════════════════════
Manages true first-person perspective with depth layers:
- Background layer (environment)
- Midground layer (enemies, objects)
- Foreground layer (weapon, hands)
- UI layer (HUD, crosshair)

Features:
- Player-centered camera with smooth interpolation
- Weapon sway and head bobbing
- Recoil and camera shake
- Focus depth separation
- Performance-optimized rendering
═══════════════════════════════════════════════════════════════════
"""

import pygame
import math
import random


class CameraSystem:
    """
    First-person camera controller with layered rendering
    """
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        # ═══ CAMERA STATE ═══
        self.position = pygame.math.Vector2(0, 0)  # Camera world position
        self.rotation = 0.0  # Camera rotation (degrees)
        self.fov = 75.0  # Field of view
        
        # ═══ MOVEMENT STATE ═══
        self.velocity = pygame.math.Vector2(0, 0)
        self.is_moving = False
        self.move_speed = 200.0  # pixels/second
        
        # ═══ HEAD BOBBING ═══
        self.bob_timer = 0.0
        self.bob_frequency = 2.5  # Hz
        self.bob_amplitude_vertical = 8.0  # pixels
        self.bob_amplitude_horizontal = 4.0  # pixels
        self.bob_offset = pygame.math.Vector2(0, 0)
        
        # ═══ IDLE SWAY ═══
        self.sway_timer = 0.0
        self.sway_frequency = 0.8  # Hz (slow breathing)
        self.sway_amplitude = 2.5  # pixels
        self.sway_offset = pygame.math.Vector2(0, 0)
        
        # ═══ RECOIL SYSTEM ═══
        self.recoil_amount = 0.0  # Current recoil intensity (0-1)
        self.recoil_recovery_rate = 4.0  # How fast recoil recovers
        self.recoil_offset = pygame.math.Vector2(0, 0)
        self.recoil_rotation = 0.0  # Camera tilt during recoil
        
        # ═══ CAMERA SHAKE ═══
        self.shake_amount = 0.0
        self.shake_decay_rate = 5.0
        self.shake_offset = pygame.math.Vector2(0, 0)
        
        # ═══ SMOOTHING & INTERPOLATION ═══
        self.smooth_position = pygame.math.Vector2(0, 0)
        self.smooth_rotation = 0.0
        self.smoothing_factor = 8.0  # Higher = more responsive
        
        # ═══ DEPTH LAYERS ═══
        self.layers = {
            'background': [],  # Environment, skybox
            'midground': [],   # Enemies, objects
            'foreground': [],  # Weapon, hands
            'ui': []          # HUD elements
        }
        
        # ═══ FOCUS & DEPTH OF FIELD ═══
        self.focus_distance = 500.0  # Focus plane distance
        self.dof_enabled = True
        self.dof_intensity = 0.3  # 0-1, how much blur
        
        # ═══ PERFORMANCE TRACKING ═══
        self.frame_count = 0
        self.render_time = 0.0
    
    # ══════════════════════════════════════════════════════════
    #   UPDATE METHODS
    # ══════════════════════════════════════════════════════════
    
    def update(self, dt):
        """
        Update camera state for current frame
        
        Args:
            dt: Delta time in seconds
        """
        # Update movement-based effects
        if self.is_moving:
            self._update_head_bob(dt)
        else:
            self._update_idle_sway(dt)
            self._decay_head_bob(dt)
        
        # Update recoil recovery
        self._update_recoil(dt)
        
        # Update camera shake
        self._update_shake(dt)
        
        # Smooth interpolation for final camera transform
        self._smooth_camera(dt)
    
    def _update_head_bob(self, dt):
        """Simulate head bobbing during movement"""
        self.bob_timer += dt * self.bob_frequency * math.pi * 2
        
        # Vertical bob (up-down)
        self.bob_offset.y = math.sin(self.bob_timer) * self.bob_amplitude_vertical
        
        # Horizontal bob (side-to-side at half frequency)
        self.bob_offset.x = math.sin(self.bob_timer * 0.5) * self.bob_amplitude_horizontal
    
    def _decay_head_bob(self, dt):
        """Smoothly decay head bob when stopping"""
        decay_rate = 5.0
        self.bob_offset.x *= max(0, 1.0 - decay_rate * dt)
        self.bob_offset.y *= max(0, 1.0 - decay_rate * dt)
        self.bob_timer *= max(0, 1.0 - decay_rate * dt)
    
    def _update_idle_sway(self, dt):
        """Subtle breathing/idle sway when stationary"""
        self.sway_timer += dt * self.sway_frequency * math.pi * 2
        
        # Smooth sine wave motion
        self.sway_offset.x = math.sin(self.sway_timer) * self.sway_amplitude
        self.sway_offset.y = math.sin(self.sway_timer * 0.7) * self.sway_amplitude * 0.6
    
    def _update_recoil(self, dt):
        """Update and recover from recoil"""
        if self.recoil_amount > 0:
            # Smooth recovery
            self.recoil_amount = max(0, self.recoil_amount - self.recoil_recovery_rate * dt)
            
            # Calculate recoil offset (upward and slight side-to-side)
            recoil_intensity = self.recoil_amount
            self.recoil_offset.y = -recoil_intensity * 45  # Kick up
            self.recoil_offset.x = math.sin(recoil_intensity * 3) * recoil_intensity * 8  # Side sway
            
            # Camera tilt during recoil
            self.recoil_rotation = math.sin(recoil_intensity * 2) * recoil_intensity * 2.5
        else:
            self.recoil_offset.x = 0
            self.recoil_offset.y = 0
            self.recoil_rotation = 0
    
    def _update_shake(self, dt):
        """Update camera shake effect"""
        if self.shake_amount > 0:
            # Random shake direction
            angle = random.uniform(0, math.pi * 2)
            magnitude = self.shake_amount
            
            self.shake_offset.x = math.cos(angle) * magnitude * random.uniform(0.7, 1.0)
            self.shake_offset.y = math.sin(angle) * magnitude * random.uniform(0.7, 1.0)
            
            # Decay shake
            self.shake_amount = max(0, self.shake_amount - self.shake_decay_rate * dt)
        else:
            self.shake_offset.x = 0
            self.shake_offset.y = 0
    
    def _smooth_camera(self, dt):
        """Apply smooth interpolation to camera movement"""
        # Combine all offsets
        target_x = self.position.x + self.bob_offset.x + self.sway_offset.x + self.recoil_offset.x + self.shake_offset.x
        target_y = self.position.y + self.bob_offset.y + self.sway_offset.y + self.recoil_offset.y + self.shake_offset.y
        
        # Smooth interpolation (exponential smoothing)
        alpha = 1.0 - math.exp(-self.smoothing_factor * dt)
        self.smooth_position.x += (target_x - self.smooth_position.x) * alpha
        self.smooth_position.y += (target_y - self.smooth_position.y) * alpha
        
        # Smooth rotation
        target_rotation = self.rotation + self.recoil_rotation
        self.smooth_rotation += (target_rotation - self.smooth_rotation) * alpha
    
    # ══════════════════════════════════════════════════════════
    #   PUBLIC API - CAMERA CONTROL
    # ══════════════════════════════════════════════════════════
    
    def set_moving(self, moving):
        """Set whether camera is moving"""
        self.is_moving = moving
    
    def apply_recoil(self, intensity=1.0):
        """
        Apply recoil impulse to camera
        
        Args:
            intensity: Recoil strength (0-1), default 1.0 for full recoil
        """
        self.recoil_amount = min(1.0, intensity)
    
    def apply_shake(self, intensity=10.0):
        """
        Apply camera shake
        
        Args:
            intensity: Shake magnitude in pixels
        """
        self.shake_amount = intensity
    
    def get_camera_offset(self):
        """
        Get current camera offset for rendering
        
        Returns:
            tuple: (offset_x, offset_y) in pixels
        """
        return (int(self.smooth_position.x), int(self.smooth_position.y))
    
    def get_camera_rotation(self):
        """
        Get current camera rotation
        
        Returns:
            float: Rotation in degrees
        """
        return self.smooth_rotation
    
    # ══════════════════════════════════════════════════════════
    #   LAYER MANAGEMENT
    # ══════════════════════════════════════════════════════════
    
    def clear_layers(self):
        """Clear all render layers"""
        for layer in self.layers.values():
            layer.clear()
    
    def add_to_layer(self, layer_name, render_callable):
        """
        Add a render function to a layer
        
        Args:
            layer_name: 'background', 'midground', 'foreground', or 'ui'
            render_callable: Function that takes (surface, camera_offset)
        """
        if layer_name in self.layers:
            self.layers[layer_name].append(render_callable)
    
    def render_all_layers(self, screen):
        """
        Render all layers in correct order with depth effects
        
        Args:
            screen: pygame.Surface to render to
        """
        offset = self.get_camera_offset()
        rotation = self.get_camera_rotation()
        
        # ═══ BACKGROUND LAYER ═══
        # Parallax: moves slower than camera (creates depth)
        bg_offset = (int(offset[0] * 0.3), int(offset[1] * 0.3))
        for render_func in self.layers['background']:
            render_func(screen, bg_offset)
        
        # Apply subtle DOF blur to background if enabled
        if self.dof_enabled and self.dof_intensity > 0:
            self._apply_background_dof(screen)
        
        # ═══ MIDGROUND LAYER ═══
        # Normal camera movement (enemies, objects)
        for render_func in self.layers['midground']:
            render_func(screen, offset)
        
        # ═══ FOREGROUND LAYER ═══
        # Weapon layer - enhanced movement (feels closer)
        # Amplify sway and bob for tactile feel
        fg_offset = (
            int(offset[0] * 1.0 + self.sway_offset.x * 1.5 + self.bob_offset.x * 0.8),
            int(offset[1] * 1.0 + self.sway_offset.y * 1.5 + self.bob_offset.y * 0.8)
        )
        
        for render_func in self.layers['foreground']:
            render_func(screen, fg_offset, rotation)
        
        # ═══ UI LAYER ═══
        # No camera offset (screen-space)
        for render_func in self.layers['ui']:
            render_func(screen, (0, 0))
    
    def _apply_background_dof(self, screen):
        """
        Apply subtle depth-of-field blur to background
        (Simplified for performance)
        """
        # Create a darkened/desaturated overlay for DOF effect
        dof_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        alpha = int(self.dof_intensity * 30)  # Subtle darkening
        dof_surf.fill((0, 0, 0, alpha))
        screen.blit(dof_surf, (0, 0))
    
    # ══════════════════════════════════════════════════════════
    #   UTILITY METHODS
    # ══════════════════════════════════════════════════════════
    
    def world_to_screen(self, world_pos):
        """
        Convert world coordinates to screen coordinates
        
        Args:
            world_pos: tuple (x, y) in world space
            
        Returns:
            tuple: (x, y) in screen space
        """
        offset = self.get_camera_offset()
        return (
            int(world_pos[0] - offset[0] + self.width // 2),
            int(world_pos[1] - offset[1] + self.height // 2)
        )
    
    def screen_to_world(self, screen_pos):
        """
        Convert screen coordinates to world coordinates
        
        Args:
            screen_pos: tuple (x, y) in screen space
            
        Returns:
            tuple: (x, y) in world space
        """
        offset = self.get_camera_offset()
        return (
            int(screen_pos[0] + offset[0] - self.width // 2),
            int(screen_pos[1] + offset[1] - self.height // 2)
        )
    
    def reset(self):
        """Reset camera to default state"""
        self.position = pygame.math.Vector2(0, 0)
        self.rotation = 0.0
        self.velocity = pygame.math.Vector2(0, 0)
        self.is_moving = False
        self.bob_timer = 0.0
        self.sway_timer = 0.0
        self.recoil_amount = 0.0
        self.shake_amount = 0.0
        self.bob_offset = pygame.math.Vector2(0, 0)
        self.sway_offset = pygame.math.Vector2(0, 0)
        self.recoil_offset = pygame.math.Vector2(0, 0)
        self.shake_offset = pygame.math.Vector2(0, 0)
        self.smooth_position = pygame.math.Vector2(0, 0)
        self.smooth_rotation = 0.0