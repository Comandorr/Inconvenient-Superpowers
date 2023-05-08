import arcade
import random
import pyglet

class Player(arcade.Sprite):
	def __init__(self, screen):
		super().__init__('character.png', center_x = screen.width/2, center_y = 50)
		self.keys = {'w':False, 's':False, 'a':False, 'd':False}
		self.screen = screen
		self.speed = 2
		self.jump_speed = 7

	def update(self):
		self.update_player_speed()
		super().update()
		

	def update_player_speed(self):
		self.change_x = 0
		if self.keys['d'] and not self.keys['a']:
			self.change_x = self.speed
		if self.keys['a'] and not self.keys['d']:
			self.change_x = -self.speed




class Game(arcade.Window):
	def __init__(self):
		super().__init__(800, 600, vsync=True)
		arcade.set_background_color(arcade.color.AMAZON)
		self.player = Player(self)
		self.player_list = arcade.SpriteList()
		self.player_list.append(self.player)

		self.wall_list = arcade.SpriteList()
		for x in range(50):
			a = arcade.Sprite('tile_1.png')
			a.bottom = 0
			a.left = x*a.width
			self.wall_list.append(a)

		self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.wall_list, gravity_constant=0.5)
		
		
		

	def on_update(self, delta_time):
		self.player.update()
		self.physics_engine.update()

	def on_draw(self):
		self.clear()
		self.player.draw()
		self.wall_list.draw()


	def on_key_press(self, key, modifiers):
		if key == arcade.key.W:
			if self.physics_engine.can_jump():
				self.player.change_y = self.player.jump_speed
		if key == arcade.key.D:
			self.player.keys['d'] = True
		if key == arcade.key.A:
			self.player.keys['a'] = True
		
	def on_key_release(self, key, modifiers):
		if key == arcade.key.W:
			self.player.keys['w'] = False
		if key == arcade.key.D:
			self.player.keys['d'] = False
		if key == arcade.key.A:
			self.player.keys['a'] = False



game = Game()
game.run()
