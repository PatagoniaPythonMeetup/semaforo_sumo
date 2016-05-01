# -*- coding: utf-8 -*-
import sys
from time import time

try:
    import kivy
except ImportError:
    from utils import encontrar_kivy
    encontrar_kivy()


from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.uix.label import Label
# from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.animation import Animation
from kivy.core.window import Window
# from kivy.factory import Factory

# Configuración de fullscreen
# No funcioan bien en OS X
if sys.platform == 'darwin':
    pass
else:
    Window.fullscreen = 'auto'
Window.set_title("Semáforo")

try:
    from kivy.core.audio import SoundLoader
    light_1_sound = SoundLoader.load('data/light_1.wav')
    light_2_sound = SoundLoader.load('data/light_2.wav')
except:
    light_1_sound = light_2_sound = None


class LightLabel(Label):
    """
    Luz verde
    """
    red   = NumericProperty(0)
    green = NumericProperty(.9)
    blue  = NumericProperty(0)
    alpha = NumericProperty(0)


class SemaforoSumo(Screen):
    '''
    Este widget es una pantalla, por lo que es el root para el cálculo
    de los IDs
    Intenta emular a https://www.youtube.com/watch?v=L9SEuYpGrjg
    '''

    counter = 0
    mins = NumericProperty(3)
    countdown = 0

    def start(self):
        self.counter = 0
        Clock.schedule_interval(self.tick, 1)
        self.ids.start_button.disabled = True
        self.ids.stop_button.disabled = False
        # Arreglo disperso de leds
        # {1: Led1, 2: Led2, 3: Led3}
        self.leds = {i: getattr(self.ids, 'led%d' % i, None) for i in range(1, 4)}

    # Countdown
    CONTADOR_INICIAL = 4
    CONTADOR_APAGADO = 4 + 5
    CONTADOR_FLASH = 4 + 5 + 1
    ANIMATION_DELAY = 0.3
    #
    # CONTADOR_INICIAL = 1
    # CONTADOR_APAGADO = 2
    # CONTADOR_FLASH = 3
    # ANIMATION_DELAY = 0.3

    def tick(self, elapsed):
        self.counter += 1

        if self.counter < self.CONTADOR_INICIAL:
            # Iluminación progresiva de los leds
            anim = Animation(alpha=0.8, duration=self.ANIMATION_DELAY)
            anim.start(self.leds[self.counter])  # 1, 2, 3
            if light_1_sound:
                light_1_sound.play()
        elif self.counter == self.CONTADOR_INICIAL:
            for n, led in self.leds.items():
                anim = Animation(alpha=0, duration=self.ANIMATION_DELAY)
                anim.start(led)
        # 5 segundos apagado
        elif self.counter == self.CONTADOR_APAGADO:
            for n, led in self.leds.items():
                anim = Animation(
                    alpha=1, duration=self.ANIMATION_DELAY * .5
                ) + Animation(
                    alpha=0, duration=self.ANIMATION_DELAY * 2
                )
                anim.start(led)
                if light_2_sound:
                    light_2_sound.play()
        elif self.counter == self.CONTADOR_FLASH:
            Clock.unschedule(self.tick)
            self.ids.start_button.disabled = False
            self.ids.sem_screen_mgr.current = 'contador'

            self.countdown = time() + (self.mins * 60)
            self.counter += elapsed
            mins, secs = divmod(self.countdown, 60)
            self.ids.coundown_label.text = '3:00.000'
            Clock.schedule_interval(self.tick, 0.01)
        else: # self.counter >= self.CONTADOR_FLASH:
            remaining = self.countdown - time()
            mins, secs = divmod(remaining, 60)
            self.ids.coundown_label.text = '%d:%2.3f' % (mins, secs)

class TorneoApp(App):
    """Aplicacion de light app"""


if __name__ == '__main__':
    app = TorneoApp()
    app.run()
