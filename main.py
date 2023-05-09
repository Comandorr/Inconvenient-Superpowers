import arcade
import random
from pyglet.math import Vec2

class Player(arcade.Sprite):
	def __init__(self, screen):
		super().__init__('character.png', scale=2, center_x = screen.width/2, center_y = 50)
		self.keys = {'w':False, 's':False, 'a':False, 'd':False}
		self.screen = screen
		self.speed = 2
		self.jump_speed = 7
		self.superpower = None
		self.superlist = ['superspeed', 'antigravity', 'teleportation', 'earthquake']

	def update(self):
		if self.superpower == 'superspeed':
			self.speed = 20
		if self.superpower == 'antigravity':
			self.screen.physics_engine.gravity_constant = -0.01
		self.change_x = 0
		if self.keys['d'] and not self.keys['a']:
			self.change_x = self.speed
		if self.keys['a'] and not self.keys['d']:
			self.change_x = -self.speed
		super().update()
	
	def use_superpower(self):
		if self.superpower == 'teleportation':
			self.left = random.randint(0, self.screen.width-self.width)
			self.bottom = random.randint(0, self.screen.height-self.height)
		if self.superpower == 'earthquake':
			self.screen.camera.shake(Vec2(random.randint(-2, 2), random.randint(-10, 10)), speed=1, damping=0.95)
			self.screen.camera.update()


class Game(arcade.Window):
	def __init__(self):
		super().__init__(1280, 720, vsync=True)
		arcade.set_background_color((86, 101, 115))
		self.player = Player(self)
		self.player_list = arcade.SpriteList()
		self.player_list.append(self.player)


		
		self.camera = arcade.Camera()
		lp = {
            "Platforms": {"use_spatial_hash": True},
        }
		self.tile_map = None
		self.tile_map = arcade.load_tilemap('map.tmx', 3, lp)
		self.scene = arcade.Scene.from_tilemap(self.tile_map)
		self.scene.add_sprite('Player', self.player)
		self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.scene['Platforms'], gravity_constant=0.5)
		
	def on_update(self, delta_time):
		self.player.update()
		self.physics_engine.update()
		position = Vec2(self.player.center_x - self.width / 2, 0)
		self.camera.move_to(position, 0.05)


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
		
	def on_key_release(self, key, modifiers):
		if key == arcade.key.W:
			self.player.keys['w'] = False
		if key == arcade.key.D:
			self.player.keys['d'] = False
		if key == arcade.key.A:
			self.player.keys['a'] = False


Game().run()
