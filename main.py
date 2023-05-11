import arcade
import random
from pyglet.math import Vec2
import math
import PIL
from PIL import Image
# pyinstaller --onefile --noconsole --clean main.py


class Player(arcade.AnimatedTimeBasedSprite):
	def __init__(self, filename, screen, scale):
		super().__init__(filename, scale=1.5)
		self.keys = {arcade.key.A:False, arcade.key.D:False}
		self.screen = screen
		self.speed = 4
		self.timer = 0

		self.superlist = [
			'superspeed', 'antigravity', 'teleportation',
			'earthquake', 'big', 'small', 'x-ray', 
			'explosion', 'freeze', 'sound',
			'stone', 'telepathy']
		self.used_superlist = []
		self.superpower = 'start'

		self.timer_superpower = 0
		self.timer_change = 0
		self.look = 'right'
		self.shoot = False
		self.animation = 'idle'
		self.hp = 50

		frames_right = []
		frames_left = []
		frames_run_right = []
		frames_run_left = []
		for i in range(4):
			image = 'hero_idle/tile00'+str(i)+'.png'
			texture1, texture2 = arcade.load_texture_pair(image)
			frames_right.append(arcade.AnimationKeyframe(i, 150, texture1))
			frames_left.append(arcade.AnimationKeyframe(i+4, 150, texture2))
		for i in range(10):
			image = 'character_run/tile00'+str(i)+'.png'
			texture1, texture2 = arcade.load_texture_pair(image)
			frames_run_right.append(arcade.AnimationKeyframe(i+8, 50, texture1))
			frames_run_left.append(arcade.AnimationKeyframe(i+16, 50, texture2))

		self.animations = {
			'idle': {'left':frames_left, 	 'right':frames_right},
			'run' : {'left':frames_run_left, 'right':frames_run_right},
		}
		stone = arcade.load_texture('effects/stone.png')
		self.stone = [arcade.AnimationKeyframe(i, 150, stone)]
		
	def update(self, delta_time = 1/60):
		self.timer_change += delta_time

		if self.timer_change >= 3:
			self.timer_change = 0
			if self.superpower == '-':
				self.get_superpower()
			else:
				self.remove_superpower()

		if self.hp <= 0 or self.center_y < 0:
			self.kill()

		# остановка времени
		if self.superpower != 'freeze':
			self.screen.physics_engine.update()
			self.update_animation()

		# телепортация
		if self.superpower == 'teleportation':
			self.timer += delta_time
			if self.timer >= 0.5:
				self.timer = 0
				self.center_x += random.randint(-400, 400)
				self.center_y +=random.randint(-50, 100)

		# антигравитация
		if self.superpower == 'antigravity':
			g = random.randint(-2, 2)/10
			self.screen.physics_engine.gravity_constant = g

		# телепатия
		if self.superpower == 'telepathy':
			g = random.randint(-2, 2)/10
			for sprite in self.screen.scene['Enemies']:
				sprite.physics_engine.gravity_constant = g

		# движение
		self.change_x = 0
		if self.superpower != 'stone':
			if self.keys[arcade.key.D] and not self.keys[arcade.key.A]:
				self.change_x = self.speed
			elif self.keys[arcade.key.A] and not self.keys[arcade.key.D]:
				self.change_x = -self.speed

			# смена анимации
			if self.change_x != 0:
				if self.change_x > 0:
					self.look = 'right'
				else:
					self.look = 'left'
				if self.animation != 'run':
					self.change_animation('run', self.look)
			else:
				if self.animation != 'idle':
					self.change_animation('idle', self.look)
		
	def get_superpower(self):
		self.remove_superpower()
		if not self.superlist:
			self.superlist, self.used_superlist = self.used_superlist, self.superlist
		self.superpower = random.choice(self.superlist)
		#self.superpower = 'teleportation'

		# суперскорость		
		if self.superpower == 'superspeed':
			self.speed = 40

		# размер
		if self.superpower == 'big':
			self.center_y += 100
			self.scale = 5.5
			self.collision_radius =150
			for sp in arcade.check_for_collision_with_list(self, self.screen.scene['Platforms']):
				sp.kill()
			self.collision_radius =100
		elif self.superpower == 'small':
			self.scale = 0.1
			self.center_y += 32
		
		# рентген
		if self.superpower == 'x-ray':
			for sprite in self.screen.scene['Platforms']:
				sprite.visible = False

		# землетрясение
		if self.superpower == 'earthquake':
			self.screen.mediaplayer = self.screen.earthquake_sound.play(loop=True)

		# камень
		if self.superpower == 'stone':
			self.frames = self.stone
			self.cur_frame_idx = 0
			self.update_animation()
		else:
			self.change_animation(self.animation, self.look)

	def remove_superpower(self):
		for sprite in self.screen.scene['Platforms']:
			sprite.visible = True
		self.scale = 1.5
		self.speed = 4	
		self.screen.physics_engine.gravity_constant = 0.5
		for sprite in self.screen.scene['Enemies']:
			sprite.physics_engine.gravity_constant = 0.5
		if self.superpower in ['big', 'small']:
			self.center_y += 100
		if self.screen.mediaplayer:
			arcade.stop_sound(self.screen.mediaplayer)
		if self.superpower in self.superlist:
			self.superlist.remove(self.superpower)
			self.used_superlist.append(self.superpower)
		self.change_animation(self.animation, self.look)
		self.superpower = '-'

	def change_animation(self, animation, look):
		if self.animation != animation and self.superpower == 'big':
			self.collision_radius =125
			self.center_y += 25
			for sp in arcade.check_for_collision_with_list(self, self.screen.scene['Platforms']):
				sp.kill()
			self.collision_radius =100
		self.animation, self.look = animation, look
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
		self.hp = 10
		self.timer_shoot = 0

	def update(self, delta_time = 1/60):
		if self.screen.scene['Player']:
			self.physics_engine.update()
			self.timer_shoot += delta_time

			if self. hp <= 0:
				self.kill()

			distance = arcade.get_distance_between_sprites(self, self.screen.player)
			self.change_x = 0
			pos1 = (self.center_x, self.center_y)
			pos2 = (self.screen.player.center_x, self.screen.player.center_y)
			if 0 < distance < 700 and arcade.has_line_of_sight(pos1, pos2, self.screen.scene['Platforms'], 500, 31) :
				if self.timer_shoot >= 1:
					pos3 = (self.screen.player.center_x, self.center_y)
					self.timer_shoot = 0
					if pos3[0] > pos1[0]:
						self.screen.scene['Bullets'].append(Bullet(self.right+1, self.center_y, 40, self.screen))
					else:
						self.screen.scene['Bullets'].append(Bullet(self.left-1, self.center_y, -40, self.screen))
				if distance > 100:
					if self.screen.player.center_x > self.center_x:
						self.change_x = min(self.speed, distance)
					if self.screen.player.center_x < self.center_x:
						self.change_x = -min(self.speed, distance)


class Bullet(arcade.Sprite):
	def __init__(self, x, y, speed, screen):
		if speed > 0:
			super().__init__(
				":resources:images/space_shooter/laserBlue01.png", 
				center_y=y, hit_box_algorithm=None, scale=0.85)
			self.left = x
		else:
			super().__init__(
				":resources:images/space_shooter/laserBlue01.png", 
				center_y=y, hit_box_algorithm=None, scale=0.85,
				flipped_horizontally=True)
			self.right = x
		self.change_x = speed
		self.screen = screen
		if self.screen.player.superpower == 'sound':
			arcade.play_sound(self.screen.shoot_sound, 500)
		else:
			arcade.play_sound(self.screen.shoot_sound, 1)

	def update(self):
		for wall in arcade.check_for_collision_with_list(self, self.screen.scene['Platforms']):
			self.kill()
			if self.screen.scene['Player'] and self.screen.scene['Player'][0].superpower == 'explosion':
				wall.kill()
				Explosion(self)
		for enemy in arcade.check_for_collision_with_list(self, self.screen.scene['Enemies']):
			self.kill()
			enemy.hp -= 1
			if self.screen.player and self.screen.player.superpower == 'explosion':
				enemy.kill()
				Explosion(self)
		for player in arcade.check_for_collision_with_list(self, self.screen.scene['Player']):
			self.kill()
			player.hp -= 1
			if self.screen.scene['Player'][0].superpower == 'explosion':
				Explosion(self)
		super().update()


class Explosion(arcade.AnimatedTimeBasedSprite):
	def __init__(self, bullet):
		super().__init__()
		self.screen = bullet.screen
		self.frames = bullet.screen.explosion_frames
		self.set_hit_box(self.frames[0].texture.hit_box_points)
		self.center_x = bullet.center_x
		self.center_y = bullet.center_y
		self.screen.scene['Explosions'].append(self)
		self.screen.camera.shake(Vec2(random.randint(-2, 2), random.randint(-5, 5)), speed=1, damping=0.95)
		self.screen.camera.update()
		self.scale = 3.5
		if self.screen.player.superpower == 'sound':
			arcade.play_sound(bullet.screen.explosion_sound, 500)
		else:
			arcade.play_sound(bullet.screen.explosion_sound, 1)

	def update(self):
		for player in arcade.check_for_collision_with_list(self, self.screen.scene['Player']):
			player.hp -= 0.75
		for wall in arcade.check_for_collision_with_list(self, self.screen.scene['Platforms']):
			wall.kill()
		for enemy in arcade.check_for_collision_with_list(self, self.screen.scene['Enemies']):
			enemy.kill()
			
	def update_animation(self):
		if self.cur_frame_idx >= len(self.frames)-1:
			self.kill()
		super().update_animation()


class Game(arcade.Window):
	def __init__(self):
		super().__init__(1280, 720, vsync=False)
		self.center_window()
		self.set_mouse_visible(False)
		arcade.set_background_color((40, 44, 65))
		arcade.enable_timings()

		self.camera = arcade.Camera()
		lp = {
			"Platforms": {"use_spatial_hash": True, 'spatial_hash_cell_size' : 8},
			"Hero":{"custom_class": Player, "custom_class_args": {"screen": self}},
			"Enemies":{'hit_box_algorithm' : None, "custom_class": Enemy, "custom_class_args": {"screen": self}},
		}
		self.tile_map = arcade.load_tilemap('map.tmx', 1.5, lp)
		self.scene = arcade.Scene.from_tilemap(self.tile_map)
		self.player = self.scene["Hero"][0]
		
		self.scene.add_sprite('Player',self.player)
		for sprite in self.scene['Enemies']:
			sprite.physics_engine = arcade.PhysicsEnginePlatformer(sprite, walls = self.scene['Platforms'], gravity_constant=0.5)
		self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, walls = self.scene['Platforms'], gravity_constant=0.5)
		self.scene.add_sprite_list('Bullets')
		self.scene.add_sprite_list('Explosions')

		self.superpower_txt = arcade.Text(
			self.player.superpower,
			self.camera.position[0]+self.width/2,
			self.height-100,
			font_size=30,
			bold = True,
			width = 1200,
			multiline=True,
			align = 'center',
			anchor_x = 'center')

		self.hp_bar = arcade.Texture.create_filled('hpbar', (200, 20), (192, 57, 43))

		self.explosion_frames = []
		for id in range(1,10):
			frame = 'effects/explosion-animation'+str(id)+'.png'
			texture = arcade.Texture(frame+str(id), PIL.Image.open(frame).convert('RGBA'))
			keyframe = arcade.AnimationKeyframe(10+id, 50, texture)
			self.explosion_frames.append(keyframe)

		self.shoot_sound = arcade.load_sound('sounds/shoot.ogg')
		self.explosion_sound = arcade.load_sound('sounds/explosion.ogg')
		self.earthquake_sound = arcade.load_sound('sounds/earthquake.ogg')
		self.mediaplayer = None

		self.descriptions = {
			'superspeed' : 'ты супер-быстрый!',
			'antigravity' : 'ты не подчиняешься гравитации!',
			'teleportation' : 'ты можешь телепортироваться!',
			'earthquake' : 'ты можешь вызывать землетрясения!',
			'big' : 'ты супер-большой!',
			'small' : 'ты супер-маленький!',
			'x-ray' : 'ты можешь видеть сквозь стены!',
			'explosion' : 'пули взрываются!',
			'freeze' : 'ты останавливаешь время!',
			'sound' : 'у тебя супер-слух!',
			'-' : '',
			'start' : 'каждые 3 секунды ты будешь получать супер-силу\nнадеюсь, это поможет тебе пройти уровень!',
			'stone' : 'ты можешь превращаться в камень!',
			'telepathy' : 'ты можешь поднимать врагов в воздух!'
		}

	def on_update(self, delta_time):
		self.camera.use()
		if self.player and self.player.superpower != 'freeze':
			self.scene['Bullets'].update()
			self.scene['Player'].update()
			self.scene['Enemies'].update()
			self.scene['Explosions'].update()
			for exp in self.scene['Explosions']:
				exp.update_animation()
			position = Vec2(self.player.center_x - self.width / 2, self.player.center_y - self.height/3)
			self.camera.move_to(position, 0.05)
			if self.player.superpower == 'earthquake':
				self.camera.shake(Vec2(random.randint(-2, 2), random.randint(-5, 5)), speed=1, damping=0.95)
				self.camera.update()
		else:
			self.player.update()
		self.superpower_txt.text = self.descriptions[self.player.superpower]
		#self.superpower_txt.text = int(arcade.get_fps())
		if not self.scene['Player']:
			self.superpower_txt.text = 'Ты умер'
		self.superpower_txt.x = self.camera.position[0]+self.width/2
		self.superpower_txt.y = self.camera.position[1]+self.height-100

	def on_draw(self):
		self.clear()
		self.scene.draw()
		self.superpower_txt.draw()
		if self.scene['Player']:
			self.hp_bar.draw_sized(
				self.camera.position[0]+self.width/2, 
				self.camera.position[1]+20, 
				self.player.hp*10, 10)
		#self.scene.draw_hit_boxes()

	def on_key_press(self, key, modifiers):
		if key == arcade.key.W and self.physics_engine.can_jump() and self.player.superpower != 'stone':
			self.physics_engine.jump(8)
		elif key in self.player.keys:
			self.player.keys[key] = True
		elif key == arcade.key.E:
			self.player.get_superpower()
		elif key == arcade.key.F:
			self.player.remove_superpower()
		elif key == arcade.key.SPACE and self.player.superpower not in ['freeze', 'stone']:
			if self.player.look == 'right':
				self.scene['Bullets'].append(Bullet(self.player.right+1, self.player.center_y, 40, self))
			else:
				self.scene['Bullets'].append(Bullet(self.player.left-1, self.player.center_y, -40, self))
		
	def on_key_release(self, key, modifiers):
		if key in self.player.keys:
			self.player.keys[key] = False


Game().run()
