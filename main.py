import os
import random
import pygame
import configparser
import sys

os.system('clear')
print("Debugging messages will be shown here.")

# Define globally used variables
snake_length = 3
score = 0
starting_speed = 5
speed = starting_speed
speed_percent = 1.02
snake_coords = [0, 0]
snake_rect = [(0, 0)]
snake_head = ""
state = "right"
fruits = []

# Gets the variables from the save file
save = configparser.ConfigParser()
save.read('save.ini')
# Checks if the config file is empty, then creates it if it is.
if not save.sections():
    #print("Config file is empty (no sections).")
    save['Save'] = {
    'highscore': score
    }
    with open('save.ini', 'w') as configfile:
        save.write(configfile)
# Assign the highscore variable in the save file to the highscore variable in the script
save.read('save.ini')
highscore = save['Save']['highscore']


# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Initialize the display and assign other pygame-related variables
pygame.init()
pygame.mixer.init()
canvas = pygame.display.get_desktop_sizes()
# Assign display flags
display = pygame.display.set_mode(size=canvas[0], flags=pygame.FULLSCREEN, depth=0, display=0, vsync=0)
surface = pygame.Surface(canvas[0])
clock = pygame.time.Clock()
screen_width = pygame.Surface.get_width(surface)
screen_height = pygame.Surface.get_height(surface)
screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

# Get initial value for scale for scaling default fonts
config = configparser.ConfigParser()
config.read('config.ini')
scale_percent = int(config['Settings']["scale"])

# Pick game music
music_list = ["./audio/03 - Toby Fox - Pirate Dojo.flac"]
song_pick = random.choice(music_list)
music = pygame.mixer.Sound(song_pick)

# Menu music
menu_music = pygame.mixer.Sound("./audio/33 - Toby Fox - Running Sky.flac")

# Assign default font
font = pygame.font.SysFont("Ubuntu Mono", scale_percent * 24)
# Print screen details for debugging purposes
print(canvas)
print(surface)

def menu(title, subtitle, subtitle2, options, functions):
    # Create a variable menu
    global state
    global snake_coords
    
    # Start music
    menu_music.set_volume(volume)
    menu_music_obj = menu_music.play()
    
    # Create a fruit randomly for visual effect
    create_fruit()

    # Default selection
    selection = 0

    # Default color for the different text
    default_color = (255, 255, 255)
    selected_color = (255, 0, 0)
    subtitle_color = (173, 216, 230)
    subtitle2_color = (144, 238, 144)

    # Calculate the middle of the screen
    middle_height = screen_height / 2

    # Define fonts
    title_font = pygame.font.SysFont("Ubuntu Mono, Bold", scale_percent * 52)
    button_font = pygame.font.SysFont("Ubuntu Mono", scale_percent * 36)
    subtitle_font = pygame.font.SysFont("Ubuntu Mono, Bold Italic", scale_percent * 40)
    subtitle2_font = pygame.font.SysFont("Ubuntu Mono, Regular Italic", scale_percent * 38)

    # Define text
    title_text = title_font.render(title , True, default_color)
    subtitle_text = subtitle_font.render(subtitle , True, subtitle_color)
    subtitle2_text = subtitle2_font.render(subtitle2 , True, subtitle2_color)

    while True:
        # Poll arrow keys for inputs
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                   #print("Up arrow pressed")
                   if selection != 0:
                        selection -= 1
                elif event.key == pygame.K_DOWN:
                   #print("Down arrow pressed")
                   if selection != len(options) - 1:
                        selection += 1
                elif event.key == pygame.K_RETURN:
                    #print("Enter key pressed")
                    functions[selection]()

        # Blank the display
        display.fill((0, 0, 0))

        # Calculate the snake's movements randomly
        # For visual effect only, can be removed cleanly
        snake_motion = random.randint(0, 150)
        if snake_motion == 1 and state != 'down':
            state = 'up'
        elif snake_motion == 2 and state != 'up':
            state = 'down'
        elif snake_motion == 3 and state != 'left':
            state = 'right'
        elif snake_motion == 4 and state != 'right':
            state = 'left'
        game()

        # Render text objects created above
        display.blit(title_text, (20, scale_percent * 50))
        display.blit(subtitle_text, (20, scale_percent * 120))
        display.blit(subtitle2_text, (20, scale_percent * 180))
        for i in range(0, len(options)):
            if i == selection:
                display_text = button_font.render(str(options[i]), True, selected_color)
                display.blit(display_text, (20, middle_height + (i * 100)))
            else:
                display_text = button_font.render(str(options[i]), True, default_color)
                display.blit(display_text, (20, middle_height + (i * 100)))

        
        pygame.display.flip()

def load_settings():
    # Load settings from the config file and assign them to variables to be used later in the script
    global volume
    global speed_percent
    global fruits_spawned
    global fruits
    global scale_percent
    # Load and read from the config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    # Assign variables
    volume = float(config['Settings']["volume"])
    fruits = []
    fruits_spawned = int(config['Settings']["fruits spawned"])
    speed_percent = config['Settings']["difficulty"]
    scale_percent = int(config['Settings']["scale"])

def load_config_options(section="Settings"):
    # Function used to load and create a sample config file to be used in the options menu

    # Load the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Define your schema with types and constraints
    schema = {
        "Volume": {"type": "number", "step": 0.1, "min": 0.0, "max": 1.0},
        "Difficulty": {"type": "number", "step": 0.01, "min": 1.01, "max": 2.0},
        "Fruits Spawned": {"type": "integer", "step": 1, "min": 1, "max": 50},
        "Scale": {"type": "integer", "step": 1, "min": 1, "max": 5}
    }

    # Empty the config options or create the variable
    config_options = []
    # Loop to gather items in schema
    for key, meta in schema.items():
        raw_value = config.get(section, key, fallback=str(meta["min"] if meta["type"] == "number" else "False"))
        if meta["type"] == "number":
            value = float(raw_value)
        elif meta["type"] == "integer":
            value = int(raw_value)
        elif meta["type"] == "bool":
            value = raw_value.lower() == "true"
        else:
            value = raw_value

        config_options.append({
            "name": key,
            "type": meta["type"],
            "value": value,
            **meta
        })

    # Return the loaded config to the place it was called
    return config_options

def save_to_ini(config_options, section="Settings"):
    # Function used to write changes to the config file
    
    # Open the config file and read it
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Add the section if it doesn't already exist
    if section not in config:  
        config[section] = {}

    for option in config_options:
        name = option["name"]
        value = option["value"]
        config[section][name] = str(value)

    # Actually write changes from ram to the config file
    with open("config.ini", "w") as configfile:
        config.write(configfile)

def options_menu(title, subtitle, config_options, section="Settings"):
    global state
    global snake_coords

    # Default selection
    # Can be changed cleanly
    selection = 0

    # Define colors
    default_color = (255, 255, 255)
    selected_color = (255, 0, 0)
    subtitle_color = (173, 216, 230)
    
    # Defines the middle of the screen vertically
    middle_height = screen_height / 2

    # Define fonts
    title_font = pygame.font.SysFont("Ubuntu Mono, Bold", scale_percent * 52)
    subtitle_font = pygame.font.SysFont("Ubuntu Mono, Bold Italic", scale_percent * 40)
    button_font = pygame.font.SysFont("Ubuntu Mono", scale_percent * 36)

    # Define the title text used at the top of the screen using the parameter defined above
    title_text = title_font.render(title , True, default_color)
    subtitle_text = subtitle_font.render(subtitle , True, subtitle_color)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_to_ini(config_options, section)
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Runs the function to save the config file
                    save_to_ini(config_options, section)
                    return
                elif event.key == pygame.K_UP:
                    selection = (selection - 1) % len(config_options)
                elif event.key == pygame.K_DOWN:
                    selection = (selection + 1) % len(config_options)
                elif event.key == pygame.K_LEFT:
                    # Runs the modify config function below to handle changing the variables
                    modify_config(config_options[selection], -1)
                elif event.key == pygame.K_RIGHT:
                    modify_config(config_options[selection], 1)

        # Clear the screen
        display.fill((0, 0, 0))

        # Snake visual effect
        snake_motion = random.randint(0, 150)
        if snake_motion == 1 and state != 'down':
            state = 'up'
        elif snake_motion == 2 and state != 'up':
            state = 'down'
        elif snake_motion == 3 and state != 'left':
            state = 'right'
        elif snake_motion == 4 and state != 'right':
            state = 'left'
        game()

        # Render text
        display.blit(title_text, (20, scale_percent * 50))
        display.blit(subtitle_text, (20, scale_percent * 120))

        for i, option in enumerate(config_options):
            name = option["name"]
            value = option["value"]
            color = selected_color if i == selection else default_color
            text = button_font.render(f"{name}: {value}", True, color)
            display.blit(text, (20, middle_height + (i * 60)))

        pygame.display.flip()

def modify_config(option, direction):
    # Modify the variables used in the config based on what you selected in the config menu above

    # Does operations to the variable based on what type it is
    if option["type"] == "number":
        # Step is defined in the schema
        step = option.get("step", 1)
        min_val = option.get("min", 0)
        max_val = option.get("max", 100)
        new_val = round(option["value"] + direction * step, 2)
        option["value"] = max(min(new_val, max_val), min_val)
    elif option["type"] == "integer":
        step = option.get("step", 1)
        min_val = option.get("min", 0)
        max_val = option.get("max", 100)
        new_val = round(option["value"] + direction * step, 2)
        option["value"] = max(min(new_val, max_val), min_val)
    elif option["type"] == "bool":
        option["value"] = not option["value"]

def game_over():
    global save
    global highscore
    # Plays the sound effect
    # Paths are relative, based on the folder the script is run inside
    sound = pygame.mixer.Sound("./audio/womp.mp3")
    sound.set_volume(volume)
    sound.play()
    
    # Pause game music
    music.stop()
    
    # Play menu music
    menu_music.play()
    
    # Checks if the score you got is higher than the high score, if so save the new high score
    if score > int(highscore):
        # Save the high score to the save.ini file
        #print("Saving new high score")
        save['Save'] = {
            'highscore': score
        }
        with open('save.ini', 'w') as configfile:
            save.write(configfile)
        while True:
            # Display a different menu if you get a new high score
            menu("Game Over!", "Your Score: " + str(score), "You got a new high score!", ["Play Again", "Options", "Quit Game"], [play, start_options, sys.exit])
    else:
        while True:
            menu("Game Over!", "Your Score: " + str(score), "Your High Score: " + highscore, ["Play Again", "Options", "Quit Game"], [play, start_options, sys.exit])

def start_options():
    # Load the config file and start the main options menu
    config = load_config_options()
    options_menu("Options", "Some options may not apply until game is restarted", config)
    
def draw(rect, color):
    # Draw the rectangle given as a parameter
    pygame.draw.rect(display, color, rect)

def create_fruit():
    # Function used to create a fruit randomly
    global fruits
    for i in range(0, fruits_spawned):
        if len(fruits) < fruits_spawned:
            while True:
               # Calculate where the fruit will be
               # The -50 in the random makes sure that the fruit won't spawn too close to the edge of the screen
               # Otherwise it could potentially be impossible to obtain the fruit
               x = random.randint(0, screen_width - scale_percent * 50)
               y = random.randint(0, screen_height - scale_percent * 50)
               # Make sure that the coordinates fall into the 5x5 grid size
               # Otherwise the fruit may be very hard to hit
               if x % 5 == 0 and y % 5 == 0:
                  break
            # Generate the fruit object
            fruits.insert(i, pygame.Rect(x, y, scale_percent * 20, scale_percent * 20))


def snake():
    global snake_coords
    global snake_rect
    global snake_head
    global speed

    x, y = snake_rect[0]  # current head
    # Update the snake's coordinates based on the direction (state variable)
    if state == "right":
        # Add the speed variable, which is modified in other parts of the script to the snake coords list
        snake_coords[0] += speed
        # Update the head variable for parts of the program using contact with the head
        # Eg. fruit collision
        new_head = (x + speed, y)
    elif state == "left":
        snake_coords[0] -= speed
        new_head = (x - speed, y)
    elif state == "up":
        snake_coords[1] -= speed
        new_head = (x, y - speed)
    elif state == "down":
        snake_coords[1] += speed
        new_head = (x, y + speed)
    # Add the newly generated head to the list
    snake_head = pygame.Rect(new_head[0], new_head[1], scale_percent * 20, scale_percent * 20)
    snake_rect.insert(0, new_head)  # add new head
    if len(snake_rect) >= snake_length:
        # Remove previous heads only if there are more items in the list than the snake's intended length
        # This keeps the snake from either extending infinitely or erroring because the list isn't long enough for
        # other parts of the script
        for i in range(0, (len(snake_rect) - snake_length)):
            snake_rect.pop()

def game():
    global snake_length
    global snake_coords
    global snake_rect
    global screen_rect
    global snake_head

    # Calculate the snake's position
    snake()

    # Draw objects
    for i in range(0, len(fruits)):
        # Depending on how many fruits are generated, as defined in the config, tells the loop how many to draw
        draw(fruits[i], RED)

    # Draw the current snake
    for i in range(0, len(snake_rect)):
        rect = snake_rect[i]
        draw(pygame.Rect(rect[0], rect[1], scale_percent * 20, scale_percent * 20), WHITE)
    
    # Set the framerate to 60 fps to prevent the snake from going too fast or the program lagging on weaker hardware
    clock.tick(60)

def play():
    global speed
    global score
    global snake_coords
    global snake_rect
    global snake_head
    global state
    global fruits
    global snake_length
    global volume

    # Load the configuration file
    load_settings()
    
    # Reinitialize the variables
    snake_coords = [0, 0]
    snake_rect = [(0, 0)]
    snake_head = ""
    score = 0
    speed = starting_speed + scale_percent
    snake_length = 3
    state = "right"

    # Draw the initial fruit(s)
    create_fruit()
    
    # Pause menu music
    menu_music.stop()
    
    # Start randomly picked music
    music.set_volume(volume)
    music.play()
    
    # Main game loop
    while True:
        # Poll arrow keys for inputs
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # Makes sure that the opposite state is not already in use
                # This prevents false positives in the snake collision system below
                if event.key == pygame.K_UP and state != 'down':
                    #print("Up arrow pressed")
                    # Change the direction of the snake (used in the snake function) to whichever arrow key the user
                    # pressed
                    state = 'up'
                elif event.key == pygame.K_DOWN and state != 'up':
                    #print("Down arrow pressed")
                    state = 'down'
                elif event.key == pygame.K_LEFT and state != 'right':
                    #print("Left arrow pressed")
                    state = 'left'
                elif event.key == pygame.K_RIGHT and state != 'left':
                    #print("Right arrow pressed")
                    state = 'right'

        # Clear the display
        display.fill((0, 0, 0))
        # Calculate game logic
        game()

        # Render score text
        score_text = font.render("Score: " + str(score), True, (255, 255, 255))
        display.blit(score_text, (0, 0))

        # Update the display
        pygame.display.flip()
        pygame.display.update()

        # Check for collisions

        # Fruit collision check
        for i in range(0, len(fruits)):
            if snake_head.colliderect(fruits[i]):
                 #print("Fruit hit!")
                 # Add three to the snake's length
                 snake_length += scale_percent * 3
                 # Add 1 to the score
                 score += 1
                 # Add a percentage to the speed of the snake, defined in the config file
                 speed = speed * float(speed_percent)
                 # Play sound effect
                 sound = pygame.mixer.Sound("./audio/eating.mp3")
                 sound.set_volume(volume)
                 sound.play()
                 # Remove the old fruit from the list
                 fruits.remove(fruits[i])
                 # Generate a new fruit
                 create_fruit()
        # Wall collision check
        if not screen_rect.contains(snake_head):
            #print("Wall collision! Game over!")
            game_over()
            
        # Body collision check
        head_temp = snake_rect[0]
        if head_temp in snake_rect[1:]:
            #print("You hit youself! Game over!")
            game_over()
    

# Activate the initial menu

# List of subtitles for the main menu
subtitle_list = ["Snake goes hiss", "The greatest game to ever be played on a Nokia phone", "The snake's name is 'Gary'",
                 "Try not to give Gary TBI", "Snakes aren't supposed to eat apples", "TBI is Traumatic Brain Injury",
                  "Gary's metabolism is off the charts!", "Gary is a snake", "It's not the tail that's growing", "Eat Apples. Get Long. Question Reality.", 
                  "He’s Long. He’s Wrong. He’s Gary."]
# Randomly pick one of the strings from the list above
choice = random.choice(subtitle_list)

# Initially load the settings from the configuration, used to generate the menu
load_settings()
while True:
    menu("SNAKE", choice, "High Score: " + highscore, ["Play", "Options", "Quit Game"], [play, start_options, sys.exit])


