import arcade
import random
from pyglet.math import Vec2
import math

class Player(arcade.AnimatedTimeBasedSprite):
	def __init__(self, filename, screen, scale):
		super().__init__(filename, scale=2, center_x = screen.width/2, center_y = 150)
		self.keys = {'w':False, 's':False, 'a':False, 'd':False}
		self.screen = screen
		self.speed = 4
		self.jump_speed = 8
		self.timer = 0
		self.timer_len = 1
		self.superpower = 'none'
		self.superlist = ['superspeed', 'antigravity', 'teleportation', 'earthquake']
		self.look = 1
		self.shoot = False

	def update(self, delta_time = 1/60):
		if self.superpower == 'teleportation':
			self.timer += delta_time
			if self.timer >= self.timer_len:
				self.timer = 0
				self.center_x += random.randint(-500, 500)
				self.center_y = 150+random.randint(0, 200)
			
		if self.superpower == 'superspeed':
			self.speed = 35
		else:
			self.speed = 4

		if self.superpower == 'antigravity':
			self.screen.physics_engine.gravity_constant = random.randint(-1, 1)/10
		else:
			self.screen.physics_engine.gravity_constant = 0.5
		
		self.change_x = 0
		if self.keys['d'] and not self.keys['a']:
			self.change_x = self.speed
			self.look = 1
		if self.keys['a'] and not self.keys['d']:
			self.change_x = -self.speed
			self.look = -1
		super().update()
	
	def use_superpower(self):
		if self.superpower == 'teleportation':
			self.left = random.randint(int(self.screen.camera.position[0]), int(self.screen.camera.position[0]+self.screen.width-self.width))
			self.bottom = random.randint(0, self.screen.height-self.height)

	def get_superpower(self):
		self.superpower = random.choice(self.superlist)
		if self.superpower == 'teleportation':
			self.timer_len = 10000


class Enemy(arcade.AnimatedTimeBasedSprite):
	def __init__(self, filename, screen, **kwargs):
		for i in ['flipped_horizontally', 'flipped_vertically', 'flipped_diagonally', 'hit_box_algorithm', 'hit_box_detail']:
			del kwargs[i]
		super().__init__(filename, **kwargs)
		self.screen = screen
		self.speed = 2
		self.pos = 0
		

	def update(self, delta_time = 1/60):
		self.bar_list = self.screen.bar_list
		self.path = arcade.astar_calculate_path([self.center_x, self.center_y], [self.screen.player.center_x, self.screen.player.center_y], self.bar_list)
		self.change_x = 0
		self.change_y = 0
		if self.path and len(self.path) > 2:


			dest_x = self.path[self.pos][0]
			dest_y = self.path[self.pos][1]

			x_diff = dest_x - self.center_x
			y_diff = dest_y - self.center_y

			angle = math.atan2(y_diff, x_diff)

			distance = arcade.get_distance(self.center_x, self.center_y, dest_x, dest_y)

			speed = min(self.speed, distance)

			self.change_x = math.cos(angle) * speed
			self.change_y = math.sin(angle) * speed


			distance = arcade.get_distance(self.center_x, self.center_y, dest_x, dest_y)

			if distance <= self.speed:
				self.pos += 1
			if self.pos >= len(self.path):
				self.pos = 0
					
		super().update()


class Bullet(arcade.Sprite):
	def __init__(self, x, y, speed):
		if speed > 0:
			super().__init__(":resources:images/space_shooter/laserBlue01.png", center_x=x, center_y=y)
		else:
			super().__init__(":resources:images/space_shooter/laserBlue01.png", center_x=x, center_y=y, flipped_horizontally=True)
		self.change_x = speed


class Game(arcade.Window):
	def __init__(self):
		super().__init__(1280, 720, vsync=True)
		self.set_mouse_visible(False)
		arcade.set_background_color((40, 44, 56))

		self.camera = arcade.Camera()
		lp = {
			"Platforms": {"use_spatial_hash": True},
			"Hero":{"custom_class": Player, "custom_class_args": {"screen": self}},
			"Enemies":{"custom_class": Enemy, "custom_class_args": {"screen": self}},
		}
		self.tile_map = None
		self.tile_map = arcade.load_tilemap('map.tmx', 1.5, lp)
		self.scene = arcade.Scene.from_tilemap(self.tile_map)
		self.player = self.scene["Hero"][0]
		self.scene.add_sprite('Player',self.player)
		self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.scene['Platforms'], gravity_constant=0.5)
		self.bar_list = arcade.AStarBarrierList(self.scene['Enemies'][0], self.scene['Platforms'], 32, 0, 1280, 0, 720)

		self.bullet_list = arcade.SpriteList()
		self.scene.add_sprite_list('Bullets')

	def on_update(self, delta_time):
		self.player.update_animation()
		#self.player.update()
		self.scene.update()
		self.physics_engine.update()
		position = Vec2(self.player.center_x - self.width / 2, 0)
		self.camera.move_to(position, 0.05)
		if self.player.superpower == 'earthquake':
			self.camera.shake(Vec2(random.randint(-2, 2), random.randint(-5, 5)), speed=1, damping=0.95)
			self.camera.update()

	def on_draw(self):
		self.camera.use()
		self.clear()
		self.scene.draw()
		if self.scene['Enemies'][0].path:
			arcade.draw_line_strip(self.scene['Enemies'][0].path, arcade.color.BLUE, 2)

	def on_key_press(self, key, modifiers):
		if key == arcade.key.W:
			if self.physics_engine.can_jump():
				self.player.change_y = self.player.jump_speed
		if key == arcade.key.D:
			self.player.keys['d'] = True
		if key == arcade.key.A:
			self.player.keys['a'] = True
		if key == arcade.key.F:
			self.player.use_superpower()
		if key == arcade.key.E:
			self.player.get_superpower()
		if key == arcade.key.SPACE:
			b = Bullet(self.player.center_x, self.player.center_y, 50*self.player.look)
			self.scene['Bullets'].append(b)
		
	def on_key_release(self, key, modifiers):
		if key == arcade.key.W:
			self.player.keys['w'] = False
		if key == arcade.key.D:
			self.player.keys['d'] = False
		if key == arcade.key.A:
			self.player.keys['a'] = False


Game().run()
