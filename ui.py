import pygame
import sys
import datetime
import time
import socket
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("iPod UI Clone")

COLORS = {
    "background": (30, 30, 30),
    "text": (255, 255, 255),
    "highlight": (255, 66, 69),
    "status_bar": (45, 45, 45),
    "battery_text": (45, 45, 45),
    "battery_fill": (255, 255, 255),
    "battery_warning": (255, 200, 0),
    "battery_critical": (255, 50, 50),
    "battery_charging": (0, 145, 255),
    "art_cover_fallback": (65, 65, 65)
}

FONT = pygame.font.SysFont("Helvetica", 32)
SMALL_FONT = pygame.font.SysFont("Helvetica", 24)
BATTERY_FONT = pygame.font.SysFont("Roboto", 26)

menu_items = ["Music", "History", "Artists", "Albums", "Settings", "Shuffle"]
selected_index = 0
ITEM_HEIGHT = 60
highlight_y = 60
highlight_start_y = 60
highlight_target_y = 60
highlight_anim_start = 0
highlight_anim_duration = 0.2
art_cover_width = int(WIDTH * 0.55)
art_cover_height = int(HEIGHT - 40)
art_cover_x = WIDTH - art_cover_width
art_cover_y = 40

MUSIC_DIR = "music"
songs = []
song_index = 0
in_songs_menu = False
playing = False

clock = pygame.time.Clock()

def send_to_backend(command):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 5555))
        s.sendall(command.encode())
        s.close()
    except Exception as e:
        print(f"Backend send error: {e}")

def draw_status_bar(surface, battery_level=85, is_charging=False):
    pygame.draw.rect(surface, COLORS["status_bar"], (0, 0, WIDTH, 40))
    margin = 10
    time_text = datetime.datetime.now().strftime("%H:%M")
    time_surf = SMALL_FONT.render(time_text, True, COLORS["text"])
    surface.blit(time_surf, (margin, 10))

    batt_width, batt_height = 60, 24
    batt_radius = 7
    batt_x = WIDTH - margin - batt_width
    batt_y = 8

    if is_charging:
        fill_color = COLORS["battery_charging"]
    elif battery_level < 10:
        fill_color = COLORS["battery_critical"]
    elif battery_level < 20:
        fill_color = COLORS["battery_warning"]
    else:
        fill_color = COLORS["battery_fill"]

    terminal_width = 5
    terminal_gap = 2
    terminal_height = batt_height - 8
    terminal_y = batt_y + (batt_height - terminal_height) // 2
    terminal_rect = pygame.Rect(batt_x, terminal_y, terminal_width, terminal_height)
    pygame.draw.rect(surface, fill_color, terminal_rect, border_radius=2)

    fill_width = int((battery_level / 100) * (batt_width - terminal_width - terminal_gap))
    fill_rect = pygame.Rect(batt_x + terminal_width + terminal_gap, batt_y, fill_width, batt_height)
    pygame.draw.rect(surface, fill_color, fill_rect, border_radius=batt_radius)

    percent_text = BATTERY_FONT.render(f"{battery_level}", True, COLORS["battery_text"])
    text_rect = percent_text.get_rect(center=(batt_x + batt_width // 2 - 2, batt_y + batt_height // 2 + 1))
    surface.blit(percent_text, text_rect)

def draw_menu(surface, items, highlight_y, in_songs=False):
    start_y = 60
    pygame.draw.rect(surface, COLORS["highlight"], (0, highlight_y, WIDTH * 0.45, ITEM_HEIGHT))
    if in_songs:
        items_to_draw = [os.path.splitext(f)[0] for f in songs]
    else:
        items_to_draw = items

    for i, item in enumerate(items_to_draw):
        y = start_y + i * ITEM_HEIGHT
        text = FONT.render(item, True, COLORS["text"])
        surface.blit(text, (40, y + 10))

def draw_art_cover(surface):
    pygame.draw.rect(surface, COLORS["art_cover_fallback"], (art_cover_x, art_cover_y, art_cover_width, art_cover_height))

def main():
    global selected_index, highlight_y, highlight_start_y, highlight_target_y, highlight_anim_start
    global songs, song_index, in_songs_menu, playing

    running = True
    while running:
        dt = clock.tick(60)
        screen.fill(COLORS["background"])
        draw_art_cover(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if not in_songs_menu:
                    if event.key == pygame.K_q:
                        selected_index = (selected_index - 1) % len(menu_items)
                        highlight_start_y = highlight_y
                        highlight_target_y = 60 + selected_index * ITEM_HEIGHT
                        highlight_anim_start = time.time()
                    elif event.key == pygame.K_w:
                        selected_index = (selected_index + 1) % len(menu_items)
                        highlight_start_y = highlight_y
                        highlight_target_y = 60 + selected_index * ITEM_HEIGHT
                        highlight_anim_start = time.time()
                    elif event.key == pygame.K_u:
                        if menu_items[selected_index] == "Music":
                            songs = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith((".mp3", ".wav", ".flac"))]
                            songs.sort()
                            in_songs_menu = True
                            song_index = 0
                            highlight_start_y = highlight_y
                            highlight_target_y = 60 + song_index * ITEM_HEIGHT
                            highlight_anim_start = time.time()
                    elif event.key == pygame.K_e:
                        pass
                else:
                    if event.key == pygame.K_q:
                        song_index = (song_index - 1) % len(songs)
                        highlight_start_y = highlight_y
                        highlight_target_y = 60 + song_index * ITEM_HEIGHT
                        highlight_anim_start = time.time()
                    elif event.key == pygame.K_w:
                        song_index = (song_index + 1) % len(songs)
                        highlight_start_y = highlight_y
                        highlight_target_y = 60 + song_index * ITEM_HEIGHT
                        highlight_anim_start = time.time()
                    elif event.key == pygame.K_u:
                        song_file = f"{MUSIC_DIR}/{songs[song_index]}"
                        send_to_backend(f"play:{song_file}")
                        playing = True
                    elif event.key == pygame.K_t:
                        if playing:
                            send_to_backend("pause")
                            playing = False
                        else:
                            send_to_backend("resume")
                            playing = True
                    elif event.key == pygame.K_r:
                        song_index = (song_index + 1) % len(songs)
                        song_file = f"{MUSIC_DIR}/{songs[song_index]}"
                        send_to_backend(f"play:{song_file}")
                        playing = True
                        highlight_start_y = highlight_y
                        highlight_target_y = 60 + song_index * ITEM_HEIGHT
                        highlight_anim_start = time.time()
                    elif event.key == pygame.K_y:
                        song_index = (song_index - 1) % len(songs)
                        song_file = f"{MUSIC_DIR}/{songs[song_index]}"
                        send_to_backend(f"play:{song_file}")
                        playing = True
                        highlight_start_y = highlight_y
                        highlight_target_y = 60 + song_index * ITEM_HEIGHT
                        highlight_anim_start = time.time()
                    elif event.key == pygame.K_e:
                        in_songs_menu = False
                        highlight_start_y = highlight_y
                        highlight_target_y = 60 + selected_index * ITEM_HEIGHT
                        highlight_anim_start = time.time()

        t = (time.time() - highlight_anim_start) / highlight_anim_duration
        t = min(max(t, 0), 1)
        t_ease = 1 - (1 - t) ** 3
        highlight_y = highlight_start_y + (highlight_target_y - highlight_start_y) * t_ease

        draw_status_bar(screen)
        draw_menu(screen, menu_items, highlight_y, in_songs_menu)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
