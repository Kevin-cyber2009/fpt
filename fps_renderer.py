"""
═══════════════════════════════════════════════════════════════════
FPS RENDERER - INTEGRATION LAYER
═══════════════════════════════════════════════════════════════════
Integrates camera system and weapon controller with existing UI
Provides high-level rendering coordination and visual effects

This acts as the bridge between your existing game code and the
new camera/weapon systems without breaking current functionality.
═══════════════════════════════════════════════════════════════════
"""

import pygame
from camera_system import CameraSystem
from weapon_controller import WeaponController


class FPSRenderer:
    """
    Coordinates premium FPS rendering with existing game systems
    """
    
    def __init__(self, screen_width, screen_height, ui_instance):
        """
        Initialize FPS renderer
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            ui_instance: Your existing UI instance (for compatibility)
        """
        self.width = screen_width
        self.height = screen_height
        self.ui = ui_instance
        
        # ═══ INITIALIZE SUBSYSTEMS ═══
        self.camera = CameraSystem(screen_width, screen_height)
        self.weapon = WeaponController(screen_width, screen_height)
        
        # ═══ RENDERING STATE ═══
        self.enabled = True  # Can be toggled for performance
        self.show_weapon = True
        self.show_effects = True
        
        # ═══ VISUAL EFFECTS ═══
        self.vignette_intensity = 0.3
        self.color_grading_enabled = False
        
        # ═══ PERFORMANCE MONITORING ═══
        self.render_stats = {
            'frame_time': 0.0,
            'weapon_render_time': 0.0,
            'effects_render_time': 0.0
        }
    
    # ══════════════════════════════════════════════════════════
    #   UPDATE
    # ══════════════════════════════════════════════════════════
    
    def update(self, dt, is_moving=False):
        """
        Update all FPS systems
        
        Args:
            dt: Delta time in seconds
            is_moving: Whether player is moving
        """
        if not self.enabled:
            return
        
        # Update camera
        self.camera.set_moving(is_moving)
        self.camera.update(dt)
        
        # Update weapon
        self.weapon.set_moving(is_moving)
        self.weapon.update(dt)
    
    # ══════════════════════════════════════════════════════════
    #   RENDERING - INTEGRATION WITH EXISTING DRAW CALLS
    # ══════════════════════════════════════════════════════════
    
    def render_background(self, screen):
        """
        Render background layer with camera effects
        Wraps your existing draw_background() call
        """
        camera_offset = self.camera.get_camera_offset()
        
        # Call existing UI background render with camera offset
        self.ui.draw_background(screen)
        
        # Apply subtle vignette
        if self.show_effects:
            self._render_vignette(screen)
    
    def render_monster(self, screen, monster, target_part=None):
        """
        Render monster in midground layer
        Wraps your existing monster.draw() call
        
        Args:
            screen: pygame.Surface
            monster: Monster instance
            target_part: Currently targeted body part
        """
        camera_offset = self.camera.get_camera_offset()
        
        # Apply camera offset to monster rendering
        # (Your monster class would need to accept offset parameter)
        monster.draw(screen, target_part)
    
    def render_weapon(self, screen, show_flash=False):
        """
        Render weapon in foreground layer with premium effects
        
        Args:
            screen: pygame.Surface
            show_flash: Whether to show muzzle flash
        """
        if not self.show_weapon:
            return
        
        camera_offset = self.camera.get_camera_offset()
        camera_rotation = self.camera.get_camera_rotation()
        
        # Render weapon with camera transforms
        self.weapon.render(screen, camera_offset, camera_rotation)
        
        # Call existing gun rendering (if using original style)
        # This maintains compatibility with your existing draw_gun_doom()
        recoil_offset = int(self.weapon.recoil_strength * 25)
        
        # Delegate to UI's gun rendering with enhanced positioning
        if hasattr(self.ui, 'draw_gun_doom'):
            # Store original values
            orig_recoil = self.ui._gun_recoil
            orig_kickback = self.ui._gun_kickback
            orig_flash = self.ui._muzzle_flash_timer
            
            # Apply our weapon controller values
            self.ui._gun_recoil = self.weapon.recoil_strength
            self.ui._gun_kickback = recoil_offset
            
            if show_flash or self.weapon.muzzle_flash_active:
                self.ui._muzzle_flash_timer = self.weapon.muzzle_flash_duration * \
                                             self.weapon.muzzle_flash_intensity
            
            # Render gun
            self.ui.draw_gun_doom(screen, show_flash or self.weapon.muzzle_flash_active)
            
            # Restore original values
            self.ui._gun_recoil = orig_recoil
            self.ui._gun_kickback = orig_kickback
            self.ui._muzzle_flash_timer = orig_flash
    
    def render_hud(self, screen, *args, **kwargs):
        """
        Render HUD in UI layer (no camera offset)
        Wraps your existing draw_hud() call
        """
        # HUD is screen-space, no camera offset
        self.ui.draw_hud(screen, *args, **kwargs)
    
    def render_crosshair(self, screen, crosshair_pos, show_targeting=False):
        """
        Render crosshair with camera effects
        
        Args:
            screen: pygame.Surface
            crosshair_pos: (x, y) position
            show_targeting: Whether showing targeting reticle
        """
        # Apply camera shake to crosshair for immersion
        camera_offset = self.camera.get_camera_offset()
        
        adjusted_x = crosshair_pos[0] + int(camera_offset[0] * 0.2)
        adjusted_y = crosshair_pos[1] + int(camera_offset[1] * 0.2)
        
        if show_targeting:
            # Targeting crosshair (red)
            pygame.draw.circle(screen, (255, 0, 0), (adjusted_x, adjusted_y), 15, 2)
            pygame.draw.circle(screen, (255, 0, 0), (adjusted_x, adjusted_y), 2)
            
            # Crosshair lines
            line_length = 10
            line_gap = 10
            pygame.draw.line(screen, (255, 0, 0),
                           (adjusted_x - line_gap - line_length, adjusted_y),
                           (adjusted_x - line_gap, adjusted_y), 2)
            pygame.draw.line(screen, (255, 0, 0),
                           (adjusted_x + line_gap, adjusted_y),
                           (adjusted_x + line_gap + line_length, adjusted_y), 2)
            pygame.draw.line(screen, (255, 0, 0),
                           (adjusted_x, adjusted_y - line_gap - line_length),
                           (adjusted_x, adjusted_y - line_gap), 2)
            pygame.draw.line(screen, (255, 0, 0),
                           (adjusted_x, adjusted_y + line_gap),
                           (adjusted_x, adjusted_y + line_gap + line_length), 2)
        else:
            # Normal crosshair (white/blue)
            pygame.draw.circle(screen, (255, 255, 255), (adjusted_x, adjusted_y), 10, 3)
            pygame.draw.circle(screen, (100, 150, 255), (adjusted_x, adjusted_y), 6)
            pygame.draw.circle(screen, (150, 200, 255), (adjusted_x, adjusted_y), 15, 1)
    
    # ══════════════════════════════════════════════════════════
    #   VISUAL EFFECTS
    # ══════════════════════════════════════════════════════════
    
    def _render_vignette(self, screen):
        """Render subtle vignette effect"""
        if self.vignette_intensity <= 0:
            return
        
        # Create radial gradient vignette
        vignette = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        center_x = self.width // 2
        center_y = self.height // 2
        max_radius = max(self.width, self.height) * 0.7
        
        # Sample points for gradient (performance optimization)
        for i in range(0, self.width, 8):
            for j in range(0, self.height, 8):
                dx = i - center_x
                dy = j - center_y
                dist = (dx * dx + dy * dy) ** 0.5
                
                if dist > max_radius * 0.5:
                    alpha = min(255, int((dist - max_radius * 0.5) / (max_radius * 0.5) * 
                                       self.vignette_intensity * 180))
                    pygame.draw.rect(vignette, (0, 0, 0, alpha), (i, j, 8, 8))
        
        screen.blit(vignette, (0, 0))
    
    def apply_screen_shake(self, intensity=10.0):
        """
        Apply screen shake effect
        
        Args:
            intensity: Shake intensity in pixels
        """
        self.camera.apply_shake(intensity)
    
    def apply_recoil(self, intensity=1.0):
        """
        Apply recoil to both camera and weapon
        
        Args:
            intensity: Recoil strength (0-1)
        """
        self.camera.apply_recoil(intensity)
        self.weapon.fire(intensity)
    
    # ══════════════════════════════════════════════════════════
    #   PUBLIC API - EASY INTEGRATION
    # ══════════════════════════════════════════════════════════
    
    def fire_weapon(self, intensity=1.0, shake=True):
        """
        Unified fire command - handles weapon, camera, and effects
        
        Args:
            intensity: Shot intensity (0-1)
            shake: Whether to apply camera shake
        """
        # Fire weapon (triggers animation + muzzle flash)
        self.weapon.fire(intensity)
        
        # Apply camera recoil
        self.camera.apply_recoil(intensity * 0.8)
        
        # Optional camera shake
        if shake:
            self.camera.apply_shake(intensity * 12.0)
    
    def set_movement(self, moving):
        """
        Set movement state for camera and weapon
        
        Args:
            moving: Boolean, whether player is moving
        """
        self.camera.set_moving(moving)
        self.weapon.set_moving(moving)
    
    def get_render_stats(self):
        """Get performance statistics"""
        return {
            'camera_offset': self.camera.get_camera_offset(),
            'weapon_state': self.weapon.current_state,
            'weapon_recoil': self.weapon.recoil_strength,
            'muzzle_flash_active': self.weapon.muzzle_flash_active,
            **self.render_stats
        }
    
    def reset(self):
        """Reset all systems to default state"""
        self.camera.reset()
        self.weapon.reset()
    
    # ══════════════════════════════════════════════════════════
    #   COMPATIBILITY HELPERS
    # ══════════════════════════════════════════════════════════
    
    def get_camera_offset_for_legacy(self):
        """
        Get camera offset in format compatible with existing code
        
        Returns:
            tuple: (offset_x, offset_y)
        """
        return self.camera.get_camera_offset()
    
    def trigger_shoot_effect_legacy(self):
        """
        Compatibility wrapper for existing trigger_shoot_effect() calls
        """
        self.fire_weapon(intensity=1.0, shake=True)
    
    def update_movement_animation_legacy(self, dt, is_moving):
        """
        Compatibility wrapper for existing update_movement_animation() calls
        """
        self.update(dt, is_moving)