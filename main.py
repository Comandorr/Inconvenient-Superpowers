import arcade
import random
from pyglet.math import Vec2
import math
import PIL
from PIL import Image


class Player(arcade.AnimatedTimeBasedSprite):
	def __init__(self, filename, screen, scale):
		super().__init__(filename, scale=1.5)
		self.keys = {'w':False, 's':False, 'a':False, 'd':False}
		self.screen = screen
		self.speed = 2
		self.jump_speed = 8
		self.timer = 0
		self.timer_len = 1
		self.superpower = 'none'
		self.superlist = ['superspeed', 'antigravity', 'teleportation', 'earthquake']
		self.look = 1
		self.shoot = False

	def setup(self):
		keyframes = []
		for i in range(len(self.frames)):
			frame = self.frames[i]
			img = frame.texture.image
			img = img.transpose(PIL.Image.Transpose.FLIP_LEFT_RIGHT)
			texture = arcade.Texture('player_img_'+str(i),image = img)
			key = arcade.AnimationKeyframe(i, 200, texture)
			keyframes.append(key)
		self.frames_left = keyframes
		self.frames_right = self.frames

	def update(self, delta_time = 1/60):
		if self.superpower == 'teleportation':
			self.timer += delta_time
			if self.timer >= self.timer_len:
				self.timer = 0
				self.center_x += random.randint(-500, 500)
				self.center_y = 150+random.randint(0, 200)
			
		if self.superpower == 'superspeed':
			self.speed = 16
		else:
			self.speed = 2

		if self.superpower == 'antigravity':
			g = random.randint(-1, 1)/10
			self.screen.physics_engine.gravity_constant = g
			for sprite in self.screen.scene['Enemies']:
				sprite.physics_engine.gravity_constant = g
		else:
			self.screen.physics_engine.gravity_constant = 0.5
			for sprite in self.screen.scene['Enemies']:
				sprite.physics_engine.gravity_constant = 0.5
		
		self.change_x = 0
		if self.keys['d'] and not self.keys['a']:
			self.change_x = self.speed
			if self.look == -1:
				self.time_counter = self.frames[self.cur_frame_idx].duration / 1000.0
				self.look = 1
				self.frames = self.frames_right
				self.set_hit_box(self.frames[0].texture.hit_box_points)
				self.center_x+=16
		if self.keys['a'] and not self.keys['d']:
			self.change_x = -self.speed
			if self.look == 1:
				self.time_counter = self.frames[self.cur_frame_idx].duration / 1000.0
				self.look = -1
				self.frames = self.frames_left
				self.set_hit_box(self.frames[0].texture.hit_box_points)
				self.center_x-=16
				
		#self.change_x = 0
		super().update()	
	
	def use_superpower(self):
		if self.superpower == 'teleportation':
			self.left = random.randint(int(self.screen.camera.position[0]), int(self.screen.camera.position[0]+self.screen.width-self.width))
			self.bottom = random.randint(0, self.screen.height-self.height)

	def get_superpower(self):
		if self.superpower in self.superlist:
			self.superlist.remove(self.superpower)
		self.superpower = random.choice(self.superlist)
		self.superlist = ['superspeed', 'antigravity', 'teleportation', 'earthquake']


class Enemy(arcade.AnimatedTimeBasedSprite):
	def __init__(self, filename, screen, **kwargs):
		for i in ['flipped_horizontally', 'flipped_vertically', 'flipped_diagonally', 'hit_box_algorithm', 'hit_box_detail']:
			del kwargs[i]
		super().__init__(filename, **kwargs)
		self.screen = screen
		self.speed = 2
		self.pos = 0
		self.hp = 3		

	def update(self, delta_time = 1/60):
		if self. hp <= 0:
			self.kill()
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

			if distance <= self.speed:
				self.pos += 1
			if self.pos >= len(self.path):
				self.pos = 0
			

class Bullet(arcade.Sprite):
	def __init__(self, x, y, speed, scene):
		if speed > 0:
			super().__init__(":resources:images/space_shooter/laserBlue01.png", center_x=x, center_y=y)
		else:
			super().__init__(":resources:images/space_shooter/laserBlue01.png", center_x=x, center_y=y, flipped_horizontally=True)
		self.change_x = speed
		self.scene = scene

	def update(self):
		if arcade.check_for_collision_with_list(self, self.scene['Platforms']):
			self.kill()
		for enemy in arcade.check_for_collision_with_list(self, self.scene['Enemies']):
			self.kill()
			enemy.hp -= 1
		super().update()


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
		self.tile_map = arcade.load_tilemap('map.tmx', 1.5, lp)
		self.scene = arcade.Scene.from_tilemap(self.tile_map)
		self.player = self.scene["Hero"][0]
		self.player.setup()
		
		self.scene.add_sprite('Player',self.player)
		for sprite in self.scene['Enemies']:
			sprite.physics_engine = arcade.PhysicsEnginePlatformer(sprite, self.scene['Platforms'], gravity_constant=0.5)
			sprite.bar_list = arcade.AStarBarrierList(sprite, self.scene['Platforms'], 32, 0, 1280*10, 0, 720*10)
		self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.scene['Platforms'], gravity_constant=0.5)
		self.scene.add_sprite_list('Bullets')

		self.superpower_txt = arcade.Text(
			self.player.superpower,
			self.camera.position[0]+self.width/2,
			self.height-100,
			font_size=30,
			bold = True)

	def on_update(self, delta_time):
		self.player.update_animation()
		self.scene.update()
		for sprite in self.scene['Enemies']:
			sprite.physics_engine.update()
		self.physics_engine.update()
		position = Vec2(self.player.center_x - self.width / 2, 0)
		self.camera.move_to(position, 0.05)
		if self.player.superpower == 'earthquake':
			self.camera.shake(Vec2(random.randint(-2, 2), random.randint(-5, 5)), speed=1, damping=0.95)
			self.camera.update()
		self.superpower_txt.text = self.player.superpower
		self.superpower_txt.x = self.camera.position[0]+self.width/2

	def on_draw(self):
		self.camera.use()
		self.clear()
		self.scene.draw()
		for enemy in self.scene['Enemies']:
			if enemy.path:
				arcade.draw_line_strip(enemy.path, arcade.color.BLUE, 2)
		#self.scene.draw_hit_boxes()
		self.superpower_txt.draw()

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
			b = Bullet(self.player.center_x, self.player.center_y, 50*self.player.look, self.scene)
			self.scene['Bullets'].append(b)
		
	def on_key_release(self, key, modifiers):
		if key == arcade.key.W:
			self.player.keys['w'] = False
		if key == arcade.key.D:
			self.player.keys['d'] = False
		if key == arcade.key.A:
			self.player.keys['a'] = False


Game().run()
