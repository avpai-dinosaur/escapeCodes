import pygame
from src.core.ecodeEvents import EventManager, EcodeEvent

class SoundManager:
    def __init__(self):
        pygame.mixer.init()

        # Preload sound effects
        self.sounds = {
            "walk": pygame.mixer.Sound("assets/sounds/Footstep_Left_Stone.ogg")
        }
        self.sounds["walk"].set_volume(0.5)
        self.walk_channel = pygame.mixer.Channel(1)

        # Background music files
        self.music_tracks = {
            "menu": "assets/music/MenuMusic.mp3",
            "level1": "assets/music/level1_theme.mp3",
        }
        #start with menu music
        self.current_music = "menu"
        self.play_music("menu")
        

        
         #music changes
        EventManager.subscribe(EcodeEvent.PAUSE_MENU, self.menu_music)
        EventManager.subscribe(EcodeEvent.PLAYER_DIED, self.menu_music)
        '''
        EventManager.subscribe(EcodeEvent.LEVEL_ENDED, self.next_level)
        EventManager.subscribe(EcodeEvent.ENTERED_DANCE_FLOOR, self.dance(True))
        EventManager.subscribe(EcodeEvent.LEFT_DANCE_FLOOR, self.dance(False))
        '''

        
       

        #sound effects
        EventManager.subscribe(EcodeEvent.PLAYER_MOVED, self.moved)
        self.last_step_time = 0
        self.step_delay = 0.1  # seconds between steps
        '''
        EventManager.subscribe(EcodeEvent.CAMERA_ALARM, self.alarm)
        EventManager.subscribe(EcodeEvent.CAMERA_SHAKE, self.takeoff)
        EventManager.subscribe(EcodeEvent.OPEN_DOOR, self.door_opening)

        #boss stuff
        EventManager.subscribe(EcodeEvent.START_BOSS_FIGHT, self.boss_fight)
        EventManager.subscribe(EcodeEvent.START_BOSS_FIGHT, self.boss_charge)
        EventManager.subscribe(EcodeEvent.START_BOSS_FIGHT, self.boss_attack)
        EventManager.subscribe(EcodeEvent.START_BOSS_FIGHT, self.boss_death)
        '''


    def play_sound(self, name: str):
        if name in self.sounds:
            self.sounds[name].play()

    def play_music(self, name: str, loop=True):
        if name not in self.music_tracks:
            return 

        if self.current_music != name:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.music_tracks[name])
            loops = -1 if loop else 0
            pygame.mixer.music.play(loops=loops)
            self.current_music = name
    
    def moved(self, target: pygame.Rect):
        now = pygame.time.get_ticks()
        if now - self.last_step_time >= self.step_delay:
            if not self.walk_channel.get_busy():
                self.walk_channel.play(self.sounds["walk"])
            self.last_step_time = now

    def menu_music(self):
        self.play_music("menu")


    def stop_music(self):
        pygame.mixer.music.stop()

    
