import pygame
import sys
import time
import json
import os

pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Towers of Hanoi")
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Load game start sound
game_start_sound = pygame.mixer.Sound("game-start-6104.mp3")
button_click_sound = pygame.mixer.Sound("button-click.mp3")
click_game_sound = pygame.mixer.Sound("click-game.mp3")

# Load background music
pygame.mixer.music.load("game-music.mp3")


game_done = False
framerate = 60

# Game variables
steps = 0
n_disks = 3
disks = []
towers_midx = [150, 400, 650]  # Adjusted tower positions for better spacing
pointing_at = 0
floating = False
floater = 0
is_dark_mode = True  # Start in Dark Mode
in_settings = False  # Flag to track if settings screen is active
auto_solving = False  # Flag for automatic solving mode
solve_moves = []  # List of moves for automatic solving
solve_index = 0  # Current move index in automatic solving
last_move_time = 0  # Time of last move in auto solving
start_time = 0  # Timer start time
elapsed_time = 0  # Elapsed time

scores_file = "top_scores.json"

# Define colors for Light and Dark modes
colors = {
    "dark": {
        "background": (10, 10, 50),
        "platform": (0, 128, 0),
        "base": (255, 204, 102),
        "tower": (255, 204, 102),
        "text": (255, 255, 255),
        "highlight": (239, 229, 51),
        "pointer": (255, 0, 0),
        "button": (80, 80, 120),
        "button_hover": (100, 100, 140),
        "disk_colors": [(0, 255, 0), (255, 0, 255), (255, 255, 0), (139, 69, 19), (0, 0, 255), (255, 0, 0)],
    },
    "light": {
        "background": (220, 220, 220),
        "platform": (0, 180, 0),
        "base": (200, 150, 100),
        "tower": (200, 150, 100),
        "text": (0, 0, 0),
        "highlight": (255, 165, 0),
        "pointer": (255, 0, 0),
        "button": (180, 180, 200),
        "button_hover": (200, 200, 220),
        "disk_colors": [(50, 150, 50), (180, 50, 180), (180, 180, 50), (100, 50, 0), (50, 50, 180), (180, 50, 50)],
    }
}

def get_color(key):
    """Get the current color based on the selected mode."""

    return colors["dark" if is_dark_mode else "light"][key]
player_id = ""  # Variable to store the player's ID

def load_scores():
    global scores
    if os.path.exists(scores_file):
        try:
            with open(scores_file, "r") as f:
                scores = json.load(f)
        except Exception:
            scores = []
    else:
        scores = []

def save_scores():
    global scores
    try:
        with open(scores_file, "w") as f:
            json.dump(scores, f)
    except Exception:
        pass

def get_player_id():
    """Prompt the player to enter their ID using pygame input."""
    global player_id
    input_active = True
    input_text = ""
    font = pygame.font.SysFont('sans serif', 40)
    prompt_text = "Enter Player ID: "
    clock = pygame.time.Clock()

    while input_active:
        screen.fill(get_color("background"))
        draw_background()
        blit_text(screen, prompt_text + input_text, (400, 250), size=40, color=get_color("highlight"))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text.strip() != "":
                        player_id = input_text.strip()
                        click_game_sound.play()
                        input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < 20:
                        input_text += event.unicode
        clock.tick(30)

def rename_player():
    global player_id
    input_active = True
    input_text = ""
    font = pygame.font.SysFont('sans serif', 40)
    prompt_text = "Enter New Player Name: "
    clock = pygame.time.Clock()

    while input_active:
        screen.fill(get_color("background"))
        draw_background()
        blit_text(screen, prompt_text + input_text, (400, 250), size=40, color=get_color("highlight"))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text.strip() != "":
                        player_id = input_text.strip()
                        click_game_sound.play()
                        input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < 20:
                        input_text += event.unicode
        clock.tick(30)

def draw_background():
    screen.fill(get_color("background"))
    pygame.draw.rect(screen, get_color("platform"), pygame.Rect(0, 500, 800, 100))  # Platform
    pygame.draw.rect(screen, get_color("base"), pygame.Rect(50, 500, 700, 20))  # Base

def blit_text(screen, text, midtop, font_name='sans serif', size=30, color=None):
    if color is None:
        color = get_color("text")
    font = pygame.font.SysFont(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(midtop=midtop)
    screen.blit(text_surface, text_rect)
    return text_rect

def create_button(text, rect, action=None, font_size=24):
    """Create a button with hover effect and click action."""
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]
    
    hover = rect.collidepoint(mouse_pos)
    color = get_color("button_hover") if hover else get_color("button")
    
    pygame.draw.rect(screen, color, rect, border_radius=5)
    pygame.draw.rect(screen, get_color("text"), rect, 2, border_radius=5)  # Border
    
    # Center text on button
    font = pygame.font.SysFont('sans serif', font_size)
    text_surf = font.render(text, True, get_color("text"))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    
    # Check for click
    if hover and mouse_clicked and action:
        action()  # Call the action function directly
        return True
    return False

def menu_screen():
    global screen, n_disks, game_done, start_time
    menu_done = False
    difficulty_levels = ["Easy", "Medium", "Hard"]
    difficulty_index = 0  

    while not menu_done:
        draw_background()
        blit_text(screen, 'Towers of Hanoi', (400, 150), size=90, color=get_color("highlight"))
        blit_text(screen, 'Use arrow keys to select difficulty:', (400, 250), size=30)
        blit_text(screen, difficulty_levels[difficulty_index], (400, 300), size=40, color=get_color("highlight"))
        blit_text(screen, 'Press ENTER to start', (400, 400), size=30)
        blit_text(screen, 'Press L for Light Mode, D for Dark Mode', (400, 450), size=25)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_done = True
                game_done = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    menu_done = True
                    game_done = True
                elif event.key == pygame.K_RETURN:
                    get_player_id()  
                    game_start_sound.play()  # Play game start sound
                    pygame.mixer.music.play(-1)  # Start background music loop
                    menu_done = True
                    start_time = time.time()
                elif event.key in [pygame.K_RIGHT, pygame.K_UP]:
                    difficulty_index = (difficulty_index + 1) % 3  
                    button_click_sound.play()
                elif event.key in [pygame.K_LEFT, pygame.K_DOWN]:
                    difficulty_index = (difficulty_index - 1) % 3  
                    button_click_sound.play()
                elif event.key == pygame.K_l:
                    toggle_mode(False)
                    click_game_sound.play()
                elif event.key == pygame.K_d:
                    toggle_mode(True)
                    click_game_sound.play()

        # Update n_disks based on current selection
        if difficulty_levels[difficulty_index] == "Easy":
            n_disks = 3
        elif difficulty_levels[difficulty_index] == "Medium":
            n_disks = 5
        elif difficulty_levels[difficulty_index] == "Hard":
            n_disks = 8

        pygame.display.flip()
        clock.tick(60)

        

     

def instructions_screen():
    instructions_done = False
    while not instructions_done:
        draw_background()
        blit_text(screen, 'Game Instructions', (400, 100), font_name='sans serif', size=50, color=get_color("highlight"))
        blit_text(screen, '1. Move all disks from the first tower to the last tower.', (400, 200), font_name='sans serif', size=24)
        blit_text(screen, '2. Only one disk can be moved at a time.', (400, 250), font_name='sans serif', size=24)
        blit_text(screen, '3. A larger disk cannot be placed on a smaller disk.', (400, 300), font_name='sans serif', size=24)
        blit_text(screen, '4. Use arrow keys to move, UP to pick up, DOWN to drop.', (400, 350), font_name='sans serif', size=24)
        blit_text(screen, '5. Press ESC to access settings during game.', (400, 400), font_name='sans serif', size=24)
        blit_text(screen, 'Press ENTER to Start', (400, 450), font_name='sans serif', size=30, color=get_color("highlight"))
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    instructions_done = True  # Exit instructions when Enter is pressed
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()
        clock.tick(60)

def settings_screen():
    """Display settings screen with interactive buttons."""
    global is_dark_mode, in_settings, game_done, auto_solving, solve_moves, solve_index
    
    restart_button = pygame.Rect(300, 200, 200, 50)
    resume_button = pygame.Rect(300, 270, 200, 50)
    solve_button = pygame.Rect(300, 340, 200, 50)
    menu_button = pygame.Rect(300, 410, 200, 50)
    
    settings_active = True
    while settings_active:
        draw_background()
        blit_text(screen, 'Settings', (400, 100), size=60, color=get_color("highlight"))
        
        # Draw buttons and check for clicks
        if create_button("Restart Game", restart_button, restart_game):
            settings_active = False  # Exit settings
            in_settings = False  # Return to game after restart
            
        def resume_game():
            nonlocal settings_active
            settings_active = False
            global in_settings
            in_settings = False  # Return to game after resume
        
        if create_button("Resume Game", resume_button, resume_game):
            settings_active = False  # Resume game
            
        def start_solving():
            global auto_solving, solve_moves, solve_index, in_settings
            nonlocal settings_active
            settings_active = False
            in_settings = False  # Close settings to return to game
            auto_solving = True
            solve_moves = []
            solve_index = 0
            # Generate solve moves
            def hanoi_solver(n, start, end, temp):
                if n == 1:
                    solve_moves.append((start, end))
                else:
                    hanoi_solver(n-1, start, temp, end)
                    solve_moves.append((start, end))
                    hanoi_solver(n-1, temp, end, start)
            hanoi_solver(n_disks, 0, 2, 1)
        
        if create_button("Solve", solve_button, start_solving):
            settings_active = False
        
        if create_button("Main Menu", menu_button, return_to_menu):
            settings_active = False
            game_done = True  # This will restart the game loop
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    settings_active = False  # Close settings when ESC is pressed
        
        pygame.display.flip()
        clock.tick(60)


def restart_game():
    """Reset the game state to start a new game with the same settings."""
    global steps, floating, floater, disks, pointing_at, start_time, elapsed_time, in_settings
    steps = 0
    floating = False
    floater = 0
    pointing_at = 0  # Reset pointer position
    start_time = time.time()  # Reset timer
    elapsed_time = 0  # Reset elapsed time
    make_disks()  # Recreate disks
    in_settings = False  # Return to game screen after restart

def return_to_menu():
    """Return to the main menu and restart the game flow."""
    global game_done, in_settings
    game_done = True  # End current game loop to restart from menu
    in_settings = False  # Ensure settings mode is turned off

scores = []

def results_screen():
    global screen, steps, elapsed_time, player_id, scores
    screen.fill(get_color("background"))
    min_steps = 2**n_disks - 1

    # Pause background music
    pygame.mixer.music.pause()

    # Add current score to scores list
    scores.append({
        "player_id": player_id,
        "steps": steps,
        "elapsed_time": elapsed_time
    })

    # Sort scores by steps ascending, then elapsed_time ascending
    scores.sort(key=lambda x: (x["steps"], x["elapsed_time"]))

    # Keep only top 5 scores
    if len(scores) > 5:
        scores[:] = scores[:5]

    # Save scores to file
    save_scores()

    result_text = "You Win!" if steps == min_steps else "Good Job!"
    result_color = (0, 255, 0) if steps == min_steps else get_color("highlight")

    pygame.mixer.music.unpause()

    # Dynamic vertical positioning
    y = 150
    line_spacing = 60  # Increased spacing to avoid overlap

    blit_text(screen, result_text, (400, y), size=72, color=result_color)
    y += line_spacing + 20

    blit_text(screen, f'Your Steps: {steps}', (400, y), size=30)
    y += line_spacing

    blit_text(screen, f'Minimum Steps: {min_steps}', (400, y), size=30)
    y += line_spacing

    blit_text(screen, f'Time: {int(elapsed_time)}s', (400, y), size=30)
    y += line_spacing + 20

    # Position the restart button centered horizontally and with 40px margin from bottom
    restart_button = pygame.Rect(300, 510, 200, 50)

    # Timer for automatic transition to top scores screen
    transition_start = time.time()
    transition_delay = 3  # seconds

    results_active = True
    while results_active:
        if create_button("Play Again", restart_button, lambda: setattr(sys.modules[__name__], 'results_active', False)):
            results_active = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    results_active = False

        # Automatic transition after delay
        if time.time() - transition_start > transition_delay:
            results_active = False

        pygame.display.flip()
        clock.tick(60)

    top_scores_screen()

def top_scores_screen():
    global screen, scores, game_done
    screen.fill(get_color("background"))

    blit_text(screen, "Top 5 Best Scores", (400, 100), size=60, color=get_color("highlight"))

    y = 180
    line_spacing = 45

    for i, score in enumerate(scores, start=1):
        score_text = f"{i}. {score['player_id']} - Steps: {score['steps']}, Time: {int(score['elapsed_time'])}s"
        blit_text(screen, score_text, (400, y), size=32)
        y += line_spacing

    # Position the back button centered horizontally and with 40px margin from bottom
    back_button = pygame.Rect(300, 510, 200, 50)

    top_scores_active = True
    while top_scores_active:
        if create_button("Back to Menu", back_button, return_to_menu):
            top_scores_active = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    top_scores_active = False

        pygame.display.flip()
        clock.tick(60)


def draw_towers():
    for xpos in towers_midx:
        pygame.draw.rect(screen, get_color("platform"), pygame.Rect(xpos - 80, 500, 160, 20))  # Platform
        pygame.draw.rect(screen, get_color("tower"), pygame.Rect(xpos, 200, 10, 300))  # Tower
    blit_text(screen, 'Start', (towers_midx[0], 505), size=14)
    blit_text(screen, 'Finish', (towers_midx[2], 505), size=14)

def make_disks():
    global n_disks, disks
    disks = []
    height = 20  # Height of the disk (cylinder)
    ypos = 477 - height  # Starting position for the first disk
    width = n_disks * 40  # Increased width of the disk based on the number of disks
    for i in range(n_disks):
        disk = {
            'rect': pygame.Rect(0, 0, width, height),  # Keep the rect for positioning
            'val': n_disks - i,
            'tower': 0,
            'color': get_color("disk_colors")[i % len(get_color("disk_colors"))]
        }
        # Center the disk on the first tower
        disk['rect'].midtop = (towers_midx[0], ypos)  # Set the initial position
        disks.append(disk)
        ypos -= height + 3  # Move the position for the next disk
        width -= 40  # Decrease the width for the next disk

def draw_disks():
    for disk in disks:
        # Draw the disk as a rectangle (cylindrical shape)
        pygame.draw.rect(screen, disk['color'], disk['rect'])

def draw_ptr():
    # Draw the pointer triangle aligned properly above the tower
    ptr_points = [
        (towers_midx[pointing_at] - 7, 520),
        (towers_midx[pointing_at] + 7, 520),
        (towers_midx[pointing_at], 513)
    ]
    pygame.draw.polygon(screen, get_color("pointer"), ptr_points)

def toggle_mode(dark):
    global is_dark_mode
    is_dark_mode = dark

def check_won():
    """Check if all disks have been moved to the last tower."""
    return all(disk['tower'] == 2 for disk in disks)

def handle_game_input(event):
    global pointing_at, floating, floater, steps, in_settings, drag_active, drag_offset_x
    
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Left mouse button
            # Check if clicking on a disk to pick it up
            mouse_pos = event.pos
            for i, disk in enumerate(disks):
                if disk['rect'].collidepoint(mouse_pos):
                    # Only pick up the top disk on the tower
                    tower_disks = [d for d in disks if d['tower'] == disk['tower']]
                    smallest_disk = min(tower_disks, key=lambda x: x['val'])
                    if disk == smallest_disk and not floating:
                        floating = True
                        floater = i
                        drag_active = True
                        drag_offset_x = disk['rect'].x - mouse_pos[0]
                        # Remove the disk from its position (visually)
                        disks[floater]['rect'].centerx = mouse_pos[0]
                        disks[floater]['rect'].top = mouse_pos[1]
                        pointing_at = disk['tower']
                        break
    elif event.type == pygame.MOUSEMOTION:
        if drag_active and floating:
            mouse_pos = event.pos
            disks[floater]['rect'].centerx = mouse_pos[0] + drag_offset_x
            disks[floater]['rect'].top = mouse_pos[1]
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1 and drag_active and floating:
            drag_active = False
            mouse_pos = event.pos
            # Determine which tower the disk is dropped on
            closest_tower = min(range(3), key=lambda i: abs(towers_midx[i] - mouse_pos[0]))
            current_tower = [disk for disk in disks if disk['tower'] == closest_tower]
            can_place = True
            if current_tower:
                smallest_on_tower = min(current_tower, key=lambda x: x['val'])
                if smallest_on_tower['val'] < disks[floater]['val']:
                    can_place = False
            if can_place:
                tower_height = len(current_tower)
                ypos = 477 - (tower_height * 23)
                disks[floater]['rect'].centerx = towers_midx[closest_tower]
                disks[floater]['rect'].top = ypos
                disks[floater]['tower'] = closest_tower
                floating = False
                steps += 1
                button_click_sound.play()
                pointing_at = closest_tower
            else:
                # Return the disk to its original position
                original_tower = disks[floater]['tower']
                original_tower_disks = [d for d in disks if d['tower'] == original_tower and d != disks[floater]]
                ypos = 477 - (len(original_tower_disks) * 23)
                disks[floater]['rect'].centerx = towers_midx[original_tower]
                disks[floater]['rect'].top = ypos
                floating = False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            in_settings = True
            button_click_sound.play()
        elif event.key == pygame.K_LEFT:
            pointing_at = (pointing_at - 1) % 3
            button_click_sound.play()
        elif event.key == pygame.K_RIGHT:
            pointing_at = (pointing_at + 1) % 3
            button_click_sound.play()
        elif event.key == pygame.K_UP and not floating:
            # Try to pick up a disk from the current tower
            current_tower = [disk for disk in disks if disk['tower'] == pointing_at]
            if current_tower:  # If there are disks on this tower
                smallest_disk = min(current_tower, key=lambda x: x['val'])
                smallest_index = disks.index(smallest_disk)
                floating = True
                floater = smallest_index
                # Remove the disk from its position (visually)
                disks[floater]['rect'].midtop = (towers_midx[pointing_at], 100)
        elif event.key == pygame.K_DOWN and floating:
            # Try to place the disk on the current tower
            current_tower = [disk for disk in disks if disk['tower'] == pointing_at]
            can_place = True
            
            if current_tower:
                smallest_on_tower = min(current_tower, key=lambda x: x['val'])
                if smallest_on_tower['val'] < disks[floater]['val']:
                    can_place = False
                    
            if can_place:
                # Calculate the new position for the disk
                tower_height = len(current_tower)
                ypos = 477 - (tower_height * 23)
                disks[floater]['rect'].midtop = (towers_midx[pointing_at], ypos)
                disks[floater]['tower'] = pointing_at
                floating = False
                steps += 1
                button_click_sound.play()
            else:
                # Return the disk to its original position
                original_tower = disks[floater]['tower']
                original_tower_disks = [d for d in disks if d['tower'] == original_tower and d != disks[floater]]
                ypos = 477 - (len(original_tower_disks) * 23)
                disks[floater]['rect'].midtop = (towers_midx[original_tower], ypos)
                floating = False

def update_disk_positions():
    """Update positions of disks to maintain proper stacking."""
    global auto_solving, solve_moves, solve_index, floating, floater, steps, pointing_at
    
    if floating:
        # Update the position of the floating disk to follow the pointer
        disks[floater]['rect'].centerx = towers_midx[pointing_at]
        disks[floater]['rect'].top = 100
    
    # For each tower, stack the disks from bottom to top
    for tower_idx in range(3):
        tower_disks = [disk for disk in disks if disk['tower'] == tower_idx and 
                      (not floating or disks.index(disk) != floater)]
        tower_disks.sort(key=lambda x: x['val'], reverse=True)  # Sort by size (largest at bottom)
        
        ypos = 477 - 20  # Starting position (bottom of tower)
        
        for disk in tower_disks:
            disk['rect'].centerx = towers_midx[tower_idx]
            disk['rect'].top = ypos
            ypos -= 23  # Move up for the next disk
    
    global last_move_time
    # Handle automatic solving animation with delay
    if auto_solving and solve_index < len(solve_moves):
        current_time = time.time()
        if current_time - last_move_time >= 0.3:  # 0.3 seconds delay between moves
            start_tower, end_tower = solve_moves[solve_index]
            # Find the top disk on the start tower
            start_tower_disks = [d for d in disks if d['tower'] == start_tower]
            if not start_tower_disks:
                solve_index += 1
                last_move_time = current_time
                return
            moving_disk = min(start_tower_disks, key=lambda d: d['val'])
            # Move the disk to the end tower
            end_tower_disks = [d for d in disks if d['tower'] == end_tower]
            tower_height = len(end_tower_disks)
            ypos = 477 - (tower_height * 23)
            moving_disk['rect'].centerx = towers_midx[end_tower]
            moving_disk['rect'].midtop = (towers_midx[end_tower], ypos)
            moving_disk['tower'] = end_tower
            steps += 1
            pointing_at = end_tower
            solve_index += 1
            last_move_time = current_time
    elif auto_solving and solve_index >= len(solve_moves):
        auto_solving = False

def draw_settings_button():
    # Draw a small settings icon in the top right corner
    settings_text = blit_text(screen, "⚙️ ESC for Settings", (750, 10), size=16)
    return settings_text

def main():
    # Main game loop and management
    while True:  # Outer loop to handle returning to menu
        # Call menu screen
        game_done = False
        steps = 0
        menu_screen()
        instructions_screen()  # Show instructions after menu
        make_disks()
        
        global start_time
        start_time = time.time()  # Set start_time when game loop starts
        
        # Main game loop
        while not game_done:
            elapsed_time = time.time() - start_time  # Update elapsed time
            
            draw_background()
            draw_towers()
            update_disk_positions()  # Update disk positions before drawing
            draw_disks()
            draw_ptr()
            
            blit_text(screen, f'Steps: {steps}', (400, 20), size=30)
            blit_text(screen, f'Time: {int(elapsed_time)}s', (400, 50), size=30)  # Display timer
            player_text_rect = blit_text(screen, f'Player: {player_id}', (700, 20), size=24)  # Display player name and get rect
            draw_settings_button()  # Show settings button
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if player_text_rect and player_text_rect.collidepoint(event.pos):
                            rename_player()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l:
                        toggle_mode(False)
                    elif event.key == pygame.K_d:
                        toggle_mode(True)
                    elif event.key == pygame.K_q:
                        game_done = True
                        pygame.mixer.music.stop()  # Stop background music when quitting game
                    else:
                        handle_game_input(event)  # Handle game controls
            
            # Check if settings screen should be shown
            if in_settings:
                settings_screen()
                continue
            
            # Check if the game is won
            if check_won():
                pygame.display.flip()
                time.sleep(1)  # Short pause before results screen
                results_screen()
                break  # Break inner game loop to return to menu
            
            pygame.display.flip()
            clock.tick(framerate)


if __name__ == '__main__':
    main()

pygame.quit()
sys.exit()
