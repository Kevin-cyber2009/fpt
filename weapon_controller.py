"""
═══════════════════════════════════════════════════════════════════
WEAPON ANIMATION CONTROLLER
═══════════════════════════════════════════════════════════════════
Manages weapon rendering, animation, and visual effects for
first-person shooter gameplay.

Features:
- State-based animation system (idle, firing, reloading)
- Smooth animation blending
- Procedural recoil with realistic recovery
- Muzzle flash with screen-space glow
- Dynamic lighting response
- Performance-optimized rendering
═══════════════════════════════════════════════════════════════════
"""

import pygame
import math
import random


class WeaponState:
    """Weapon animation states"""
    IDLE = "idle"
    FIRING = "firing"
    RELOADING = "reloading"
    DRAWING = "drawing"


class WeaponController:
    """
    Controls weapon rendering and animation in first-person view
    """
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        # ═══ WEAPON STATE ═══
        self.current_state = WeaponState.IDLE
        self.previous_state = WeaponState.IDLE
        self.state_time = 0.0  # Time in current state
        self.blend_time = 0.15  # Animation blend duration
        
        # ═══ WEAPON POSITION (normalized screen space) ═══
        # Base position: lower center-right
        self.base_position = pygame.math.Vector2(0.55, 0.85)  # (0-1 range)
        self.current_position = pygame.math.Vector2(0.55, 0.85)
        self.target_position = pygame.math.Vector2(0.55, 0.85)
        
        # ═══ WEAPON ROTATION ═══
        self.base_rotation = -5.0  # Slight tilt for natural feel
        self.current_rotation = -5.0
        
        # ═══ RECOIL ANIMATION ═══
        self.recoil_offset = pygame.math.Vector2(0, 0)
        self.recoil_rotation = 0.0
        self.recoil_strength = 1.0  # Current recoil intensity (0-1)
        self.recoil_recovery_rate = 6.0  # Recovery speed
        
        # Recoil pattern (adds variety)
        self.recoil_pattern_x = 0.0
        self.recoil_pattern_y = 0.0
        
        # ═══ IDLE ANIMATION ═══
        self.idle_sway_timer = 0.0
        self.idle_sway_speed = 0.6  # Hz
        self.idle_sway_amount = 0.01  # Normalized screen space
        
        # ═══ MOVEMENT BOB ═══
        self.bob_timer = 0.0
        self.bob_speed = 2.8  # Hz
        self.bob_amount_vertical = 0.03  # Normalized
        self.bob_amount_horizontal = 0.015
        self.is_moving = False
        
        # ═══ MUZZLE FLASH ═══
        self.muzzle_flash_active = False
        self.muzzle_flash_timer = 0.0
        self.muzzle_flash_duration = 0.08  # seconds
        self.muzzle_flash_intensity = 1.0
        
        # ═══ VISUAL EFFECTS ═══
        self.dynamic_light_intensity = 0.0  # 0-1, from scene lights
        self.ambient_light = 0.85  # Base lighting
        
        # ═══ ANIMATION TIMING ═══
        self.fire_animation_duration = 0.15
        self.reload_animation_duration = 1.8
        self.draw_animation_duration = 0.5
        
        # ═══ SMOOTHING ═══
        self.position_smoothing = 12.0  # Higher = more responsive
        self.rotation_smoothing = 10.0
        
        # ═══ PERFORMANCE ═══
        self.render_weapon = True  # Can be toggled for performance
        self.detail_level = 1.0  # 0-1, affects visual quality
    
    # ══════════════════════════════════════════════════════════
    #   UPDATE METHODS
    # ══════════════════════════════════════════════════════════
    
    def update(self, dt):
        """
        Update weapon animation for current frame
        
        Args:
            dt: Delta time in seconds
        """
        self.state_time += dt
        
        # Update state-specific animations
        if self.current_state == WeaponState.IDLE:
            self._update_idle(dt)
        elif self.current_state == WeaponState.FIRING:
            self._update_firing(dt)
        elif self.current_state == WeaponState.RELOADING:
            self._update_reloading(dt)
        elif self.current_state == WeaponState.DRAWING:
            self._update_drawing(dt)
        
        # Update recoil recovery
        self._update_recoil(dt)
        
        # Update movement bob
        if self.is_moving:
            self._update_movement_bob(dt)
        
        # Update muzzle flash
        self._update_muzzle_flash(dt)
        
        # Smooth position and rotation interpolation
        self._smooth_transform(dt)
    
    def _update_idle(self, dt):
        """Idle breathing/sway animation"""
        self.idle_sway_timer += dt * self.idle_sway_speed * math.pi * 2
        
        # Subtle figure-8 pattern
        sway_x = math.sin(self.idle_sway_timer) * self.idle_sway_amount
        sway_y = math.sin(self.idle_sway_timer * 0.5) * self.idle_sway_amount * 0.6
        
        self.target_position.x = self.base_position.x + sway_x
        self.target_position.y = self.base_position.y + sway_y
    
    def _update_firing(self, dt):
        """Firing animation"""
        # Auto-return to idle after fire animation
        if self.state_time >= self.fire_animation_duration:
            self._change_state(WeaponState.IDLE)
    
    def _update_reloading(self, dt):
        """Reload animation"""
        # Animate weapon lowering during reload
        progress = self.state_time / self.reload_animation_duration
        
        if progress < 0.3:
            # Lower weapon
            offset = (progress / 0.3) * 0.2
            self.target_position.y = self.base_position.y + offset
        elif progress < 0.7:
            # Keep lowered
            self.target_position.y = self.base_position.y + 0.2
        else:
            # Raise back up
            offset = (1.0 - (progress - 0.7) / 0.3) * 0.2
            self.target_position.y = self.base_position.y + offset
        
        if self.state_time >= self.reload_animation_duration:
            self._change_state(WeaponState.IDLE)
    
    def _update_drawing(self, dt):
        """Draw weapon (pull out) animation"""
        progress = self.state_time / self.draw_animation_duration
        
        # Slide up from bottom
        if progress < 1.0:
            offset = (1.0 - progress) * 0.3
            self.target_position.y = self.base_position.y + offset
        else:
            self._change_state(WeaponState.IDLE)
    
    def _update_recoil(self, dt):
        """Update and recover from recoil"""
        if self.recoil_strength > 0:
            # Smooth recovery curve
            self.recoil_strength = max(0, self.recoil_strength - self.recoil_recovery_rate * dt)
            
            # Calculate recoil offset with pattern
            intensity = self.recoil_strength
            
            # Vertical kick (primary)
            self.recoil_offset.y = -intensity * 0.08  # Move up
            
            # Horizontal deviation (secondary)
            self.recoil_offset.x = self.recoil_pattern_x * intensity * 0.03
            
            # Rotation kick
            self.recoil_rotation = intensity * 8.0 + self.recoil_pattern_y * intensity * 3.0
        else:
            self.recoil_offset.x = 0
            self.recoil_offset.y = 0
            self.recoil_rotation = 0
    
    def _update_movement_bob(self, dt):
        """Update weapon bob during movement"""
        self.bob_timer += dt * self.bob_speed * math.pi * 2
        
        # Vertical bob
        bob_y = math.sin(self.bob_timer) * self.bob_amount_vertical
        
        # Horizontal bob (half frequency)
        bob_x = math.sin(self.bob_timer * 0.5) * self.bob_amount_horizontal
        
        # Apply to target position
        self.target_position.x = self.base_position.x + bob_x
        self.target_position.y = self.base_position.y + bob_y
    
    def _update_muzzle_flash(self, dt):
        """Update muzzle flash effect"""
        if self.muzzle_flash_active:
            self.muzzle_flash_timer += dt
            
            # Calculate intensity falloff
            progress = self.muzzle_flash_timer / self.muzzle_flash_duration
            self.muzzle_flash_intensity = max(0, 1.0 - progress)
            
            if self.muzzle_flash_timer >= self.muzzle_flash_duration:
                self.muzzle_flash_active = False
                self.muzzle_flash_timer = 0.0
    
    def _smooth_transform(self, dt):
        """Smooth interpolation for position and rotation"""
        # Position smoothing (exponential)
        alpha_pos = 1.0 - math.exp(-self.position_smoothing * dt)
        
        target_x = self.target_position.x + self.recoil_offset.x
        target_y = self.target_position.y + self.recoil_offset.y
        
        self.current_position.x += (target_x - self.current_position.x) * alpha_pos
        self.current_position.y += (target_y - self.current_position.y) * alpha_pos
        
        # Rotation smoothing
        alpha_rot = 1.0 - math.exp(-self.rotation_smoothing * dt)
        target_rot = self.base_rotation + self.recoil_rotation
        self.current_rotation += (target_rot - self.current_rotation) * alpha_rot
    
    # ══════════════════════════════════════════════════════════
    #   PUBLIC API - WEAPON CONTROL
    # ══════════════════════════════════════════════════════════
    
    def fire(self, recoil_multiplier=1.0):
        """
        Trigger weapon fire
        
        Args:
            recoil_multiplier: Scales recoil intensity (default 1.0)
        """
        self._change_state(WeaponState.FIRING)
        
        # Apply recoil
        self.recoil_strength = 1.0 * recoil_multiplier
        
        # Randomize recoil pattern for variety
        self.recoil_pattern_x = random.uniform(-1.0, 1.0)
        self.recoil_pattern_y = random.uniform(-0.5, 0.5)
        
        # Activate muzzle flash
        self.muzzle_flash_active = True
        self.muzzle_flash_timer = 0.0
        self.muzzle_flash_intensity = 1.0
    
    def reload(self):
        """Start reload animation"""
        if self.current_state != WeaponState.RELOADING:
            self._change_state(WeaponState.RELOADING)
    
    def draw_weapon(self):
        """Start draw/equip animation"""
        self._change_state(WeaponState.DRAWING)
    
    def set_moving(self, moving):
        """Set whether player is moving"""
        self.is_moving = moving
    
    def _change_state(self, new_state):
        """Internal: Change animation state"""
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_time = 0.0
    
    # ══════════════════════════════════════════════════════════
    #   RENDERING
    # ══════════════════════════════════════════════════════════
    
    def render(self, screen, camera_offset=(0, 0), camera_rotation=0.0):
        """
        Render weapon to screen
        
        Args:
            screen: pygame.Surface
            camera_offset: (x, y) tuple for camera offset
            camera_rotation: Camera rotation in degrees
        """
        if not self.render_weapon:
            return
        
        # Convert normalized position to screen coordinates
        screen_x = int(self.current_position.x * self.width)
        screen_y = int(self.current_position.y * self.height)
        
        # Apply camera offset (amplified for foreground)
        screen_x += int(camera_offset[0] * 0.5)
        screen_y += int(camera_offset[1] * 0.5)
        
        # Total rotation
        total_rotation = self.current_rotation + camera_rotation
        
        # Draw weapon (delegated to rendering function)
        self._render_weapon_model(screen, screen_x, screen_y, total_rotation)
        
        # Draw muzzle flash effect
        if self.muzzle_flash_active:
            self._render_muzzle_flash(screen, screen_x, screen_y)
    
    def _render_weapon_model(self, screen, x, y, rotation):
        """
        Render the actual weapon model
        This is a placeholder - integrate with your existing weapon rendering
        """
        # This would call your existing draw_gun_doom() function
        # or any custom weapon rendering
        
        # For now, just a visual indicator
        # (Your actual implementation will replace this)
        pass
    
    def _render_muzzle_flash(self, screen, x, y):
        """Render muzzle flash effect"""
        if self.muzzle_flash_intensity <= 0:
            return
        
        # Flash position (offset from weapon)
        flash_x = x - 80
        flash_y = y - 80
        
        intensity = self.muzzle_flash_intensity
        
        # Bright core
        core_size = int(25 * intensity)
        if core_size > 0:
            core_surf = pygame.Surface((core_size * 2, core_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(core_surf, (255, 255, 235, int(255 * intensity)), 
                             (core_size, core_size), core_size)
            screen.blit(core_surf, (flash_x - core_size, flash_y - core_size))
        
        # Outer glow layers
        for i in range(3):
            glow_size = int((40 + i * 20) * intensity)
            if glow_size > 0:
                alpha = int((120 - i * 40) * intensity)
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 230, 180, alpha), 
                                 (glow_size, glow_size), glow_size)
                screen.blit(glow_surf, (flash_x - glow_size, flash_y - glow_size))
        
        # Screen-space glow (additive blend simulation)
        if intensity > 0.5:
            glow_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            glow_alpha = int(20 * (intensity - 0.5) * 2)
            glow_overlay.fill((255, 240, 200, glow_alpha))
            screen.blit(glow_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    
    def get_muzzle_flash_intensity(self):
        """Get current muzzle flash intensity for lighting effects"""
        return self.muzzle_flash_intensity if self.muzzle_flash_active else 0.0
    
    # ══════════════════════════════════════════════════════════
    #   UTILITY
    # ══════════════════════════════════════════════════════════
    
    def reset(self):
        """Reset weapon to default state"""
        self.current_state = WeaponState.IDLE
        self.state_time = 0.0
        self.current_position = pygame.math.Vector2(self.base_position)
        self.target_position = pygame.math.Vector2(self.base_position)
        self.current_rotation = self.base_rotation
        self.recoil_strength = 0.0
        self.muzzle_flash_active = False
        self.is_moving = False
        self.bob_timer = 0.0
        self.idle_sway_timer = 0.0