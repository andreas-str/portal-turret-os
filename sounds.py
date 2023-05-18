import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import random
import utils
import time

sounds_delay_counter = 0
sounds_delay_enable = False


pygame.mixer.init(buffer=3072)

deploy_sound = pygame.mixer.Sound("sounds/Deploy.wav")
error_sound = pygame.mixer.Sound("sounds/Error.wav")
guns_sound = pygame.mixer.Sound("sounds/Gun.wav")

activated = []
activated.append(pygame.mixer.Sound("sounds/activated1.wav"))
activated.append(pygame.mixer.Sound("sounds/activated2.wav"))
activated.append(pygame.mixer.Sound("sounds/activated3.wav"))
activated.append(pygame.mixer.Sound("sounds/activated4.wav"))
activated.append(pygame.mixer.Sound("sounds/activated5.wav"))
deactivated = []
deactivated.append(pygame.mixer.Sound("sounds/deactivated1.wav"))
deactivated.append(pygame.mixer.Sound("sounds/deactivated2.wav"))
deactivated.append(pygame.mixer.Sound("sounds/deactivated3.wav"))
deactivated.append(pygame.mixer.Sound("sounds/deactivated4.wav"))
deactivated.append(pygame.mixer.Sound("sounds/deactivated5.wav"))
deactivated.append(pygame.mixer.Sound("sounds/deactivated6.wav"))
searching = []
searching.append(pygame.mixer.Sound("sounds/searching1.wav"))
searching.append(pygame.mixer.Sound("sounds/searching2.wav"))
searching.append(pygame.mixer.Sound("sounds/searching3.wav"))
searching.append(pygame.mixer.Sound("sounds/searching4.wav"))
taget_found = []
taget_found.append(pygame.mixer.Sound("sounds/target_found1.wav"))
taget_found.append(pygame.mixer.Sound("sounds/target_found2.wav"))
taget_found.append(pygame.mixer.Sound("sounds/target_found3.wav"))
taget_found.append(pygame.mixer.Sound("sounds/target_found4.wav"))
taget_found.append(pygame.mixer.Sound("sounds/target_found5.wav"))
taget_found.append(pygame.mixer.Sound("sounds/target_found6.wav"))
taget_found.append(pygame.mixer.Sound("sounds/target_found7.wav"))
target_lost = []
target_lost.append(pygame.mixer.Sound("sounds/target_lost1.wav"))
target_lost.append(pygame.mixer.Sound("sounds/target_lost2.wav"))
target_lost.append(pygame.mixer.Sound("sounds/target_lost3.wav"))
target_lost.append(pygame.mixer.Sound("sounds/target_lost4.wav"))

def play_party(selected_party):
    music_location = ""
    if selected_party == utils.OPERA:
        music_location = "sounds/opera.mp3"
    elif selected_party == utils.WIFE:
        music_location = "sounds/wife.mp3"
    pygame.mixer.music.load(music_location)
    pygame.mixer.music.play()
    return 0

def sounds_delay_worker(max_delay):
    global sounds_delay_counter
    global sounds_delay_enable
    if sounds_delay_enable == True:
        sounds_delay_counter = sounds_delay_counter + 1
    if sounds_delay_counter > max_delay:
        sounds_delay_counter = 0
        sounds_delay_enable == False

# add rest
def play_deploy_sound():
    deploy_sound.play()

def play_error_sound():
    error_sound.play()

def play_activated():
    random.shuffle(activated)
    activated[0].play()

def play_deactivated():
    random.shuffle(deactivated)
    deactivated[0].play()

def play_searching(delay_between_sounds):
    global sounds_delay_counter
    global sounds_delay_enable
    if sounds_delay_counter == 0 and sounds_delay_enable == False:
        random.shuffle(searching)
        searching[0].play()
        sounds_delay_enable = True
        sounds_delay_counter = 1
    if sounds_delay_counter >= delay_between_sounds:
        random.shuffle(searching)
        searching[0].play()
        sounds_delay_counter = 1

def stop_searching():
    global sounds_delay_counter
    global sounds_delay_enable
    sounds_delay_enable = False
    sounds_delay_counter = 0

def play_target_found():
    random.shuffle(taget_found)
    taget_found[0].play()

def play_firing():
    guns_sound.play(-1)

def stop_firing():
    guns_sound.stop()

def play_target_lost():
    random.shuffle(target_lost)
    target_lost[0].play()
