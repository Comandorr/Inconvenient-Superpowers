import arcade
import random
from pyglet.math import Vec2

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
		if self.keys['a'] and not self.keys['d']:
			self.change_x = -self.speed
		super().update()
	
	def use_superpower(self):
		if self.superpower == 'teleportation':
			self.left = random.randint(int(self.screen.camera.position[0]), int(self.screen.camera.position[0]+self.screen.width-self.width))
			self.bottom = random.randint(0, self.screen.height-self.height)

	def get_superpower(self):
		self.superpower = random.choice(self.superlist)
		if self.superpower == 'teleportation':
			self.timer_len = 10000

class Game(arcade.Window):
	def __init__(self):
		super().__init__(1280, 720, vsync=True)
		arcade.set_background_color((40, 44, 56))

		self.camera = arcade.Camera()
		lp = {
            "Platforms": {"use_spatial_hash": True},
			"Hero":{"custom_class": Player, "custom_class_args": {"screen": self}},
        }
		self.tile_map = None
		self.tile_map = arcade.load_tilemap('map.tmx', 1.5, lp)
		self.scene = arcade.Scene.from_tilemap(self.tile_map)
		self.player = self.scene["Hero"][0]
		self.scene.add_sprite('Player',self.player)
		self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.scene['Platforms'], gravity_constant=0.5)
		
	def on_update(self, delta_time):
		self.player.update_animation()
		self.player.update()
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
		
	def on_key_release(self, key, modifiers):
		if key == arcade.key.W:
			self.player.keys['w'] = False
		if key == arcade.key.D:
			self.player.keys['d'] = False
		if key == arcade.key.A:
			self.player.keys['a'] = False


Game().run()
