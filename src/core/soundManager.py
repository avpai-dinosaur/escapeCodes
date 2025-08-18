import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()

        # Preload sound effects
        self.sounds = {
            "run": pygame.mixer.Sound("assets/sounds/Footstep_Left_Stone.ogg"),
            "walk": pygame.mixer.Sound("assets/sounds/Footstep_Right_Stone.ogg"),
        }

        # Background music files
        self.music_tracks = {
            "menu": "assets/music/MenuMusic.mp3",
            "level1": "assets/music/level1_theme.mp3",
        }

        # Set volume defaults
        for sound in self.sounds.values():
            sound.set_volume(0.5)  # 50% volume

    def play_sound(self, name: str):
        if name in self.sounds:
            self.sounds[name].play()

    def play_music(self, name: str, loops=-1):
        if name in self.music_tracks:
            pygame.mixer.music.load(self.music_tracks[name])
            pygame.mixer.music.play(loops)

    def stop_music(self):
        pygame.mixer.music.stop()

    def set_music_volume(self, volume: float):
        pygame.mixer.music.set_volume(volume)

    def set_sound_volume(self, name: str, volume: float):
        if name in self.sounds:
            self.sounds[name].set_volume(volume)
