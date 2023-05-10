import arcade
import random
from pyglet.math import Vec2
import math
import PIL
from PIL import Image
# import os


class Player(arcade.AnimatedTimeBasedSprite):
	def __init__(self, filename, screen, scale):
		super().__init__(filename, scale=1.5)
		self.keys = {'a':False, 'd':False}
		self.screen = screen
		self.speed = 4
		self.timer = 0
		self.timer_len = 1
		self.superpower = 'none'
		self.superlist = ['superspeed', 'antigravity', 'teleportation', 'earthquake', 'big', 'small', 'x-ray']
		self.look = 'right'
		self.shoot = False
		self.animation = 'idle'

	def setup(self):
		frames_left = []
		for i in range(len(self.frames)):
			frame = self.frames[i]
			img = frame.texture.image.transpose(PIL.Image.Transpose.FLIP_LEFT_RIGHT).convert('RGBA')
			texture = arcade.Texture('player_img_'+str(i),image = img)
			frames_left.append(arcade.AnimationKeyframe(i+4, 200, texture))
		frames_right = self.frames

		frames_run_right = []
		frames_run_left = []
		id = 8
		for i in range(10):
			frame = 'character_run/tile00'+str(i)+'.png'
			texture = arcade.Texture(frame+str(id), PIL.Image.open(frame).convert('RGBA'))
			keyframe = arcade.AnimationKeyframe(id, 100, texture)
			id+=1
			texture2 = arcade.Texture(frame+str(id), PIL.Image.open(frame).transpose(PIL.Image.Transpose.FLIP_LEFT_RIGHT).convert('RGBA'))
			keyframe2 = arcade.AnimationKeyframe(id, 100, texture2)
			id+=1
			frames_run_right.append(keyframe)
			frames_run_left.append(keyframe2)


		self.animations = {
			'idle': {'left':frames_left, 	 'right':frames_right},
			'run' : {'left':frames_run_left, 'right':frames_run_right},
		}

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
			self.speed = 4

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
			if self.look != 'right':
				self.look = 'right'
				self.change_animation()
		elif self.keys['a'] and not self.keys['d']:
			self.change_x = -self.speed
			if self.look != 'left':
				self.look = 'left'
				self.change_animation()
		if self.change_x != 0:
			if self.animation != 'run':
				self.animation = 'run'
				self.change_animation()
		else:
			if self.animation != 'idle':
				self.animation = 'idle'
				self.change_animation()
		#self.texture.draw = self.texture.draw_scaled(self.center_x, self.center_y, scale=5)


	def use_superpower(self):
		if self.superpower == 'teleportation':
			self.left = random.randint(int(self.screen.camera.position[0]), int(self.screen.camera.position[0]+self.screen.width-self.width))
			self.bottom = random.randint(0, self.screen.height-self.height)

	def get_superpower(self):
		if self.superpower in self.superlist:
			self.superlist.remove(self.superpower)
		self.superpower = random.choice(self.superlist)
		if self.superpower == 'big':
			self.scale = 7
			self.collision_radius =150
			self.change_animation()
		elif self.superpower == 'small':
			self.scale = 0.1
			self.change_animation()
		else:
			self.scale = 1.5
			self.change_animation()
		if self.superpower == 'x-ray':
			for sprite in self.screen.scene['Platforms']:
				sprite.visible = False
		else:
			for sprite in self.screen.scene['Platforms']:
				sprite.visible = True
		self.superlist = ['superspeed', 'antigravity', 'teleportation', 'earthquake', 'big', 'small', 'x-ray']

	def change_animation(self):
		self.frames = self.animations[self.animation][self.look]
		self.cur_frame_idx = len(self.frames)-1
		self.time_counter = self.frames[self.cur_frame_idx].duration / 1000.0
		self.set_hit_box(self.frames[-2].texture.hit_box_points)


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

		self.change_x = 0
		distance = arcade.get_distance_between_sprites(self, self.screen.player)
		pos1 = (self.center_x, self.center_y)
		pos2 = (self.screen.player.center_x, self.screen.player.center_y)
		if  distance< 500 and arcade.has_line_of_sight(pos1, pos2, self.screen.scene['Platforms']):
			if self.screen.player.center_x > self.center_x:
				self.change_x = min(self.speed, distance)
			if self.screen.player.center_x < self.center_x:
				self.change_x = -min(self.speed, distance)
			

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
		self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.scene['Platforms'], gravity_constant=0.5)
		self.scene.add_sprite_list('Bullets')

		self.superpower_txt = arcade.Text(
			self.player.superpower,
			self.camera.position[0]+self.width/2,
			self.height-100,
			font_size=30,
			bold = True)

	def on_update(self, delta_time):
		self.scene.update()
		self.player.update_animation()
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
		#self.scene.draw_hit_boxes()
		self.superpower_txt.draw()

	def on_key_press(self, key, modifiers):
		if key == arcade.key.W:
			if self.physics_engine.can_jump():
				self.physics_engine.jump(8)
		if key == arcade.key.D:
			self.player.keys['d'] = True
		if key == arcade.key.A:
			self.player.keys['a'] = True
		if key == arcade.key.F:
			self.player.use_superpower()
		if key == arcade.key.E:
			self.player.get_superpower()
		if key == arcade.key.SPACE:
			if self.player.look == 'right':
				b = Bullet(self.player.center_x, self.player.center_y, 50, self.scene)
			else:
				b = Bullet(self.player.center_x, self.player.center_y, -50, self.scene)
			self.scene['Bullets'].append(b)
		
	def on_key_release(self, key, modifiers):
		if key == arcade.key.D:
			self.player.keys['d'] = False
		if key == arcade.key.A:
			self.player.keys['a'] = False

Game().run()
