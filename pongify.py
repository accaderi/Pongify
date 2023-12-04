# %%
# Main datas, imports, variables 
from PIL import Image
import pygame
import sys
import random
import inflect
p = inflect.engine()

# General variables
PHOTO_WIDTH = 800
HEIGHT = 600
WIDTH = PHOTO_WIDTH + 30
UNIT_SIZE = 40 # Size of each unit, set to 40 pixels
assert PHOTO_WIDTH % UNIT_SIZE == 0, 'WIDTH must be a multiple of UNITT_SIZE'
assert HEIGHT % UNIT_SIZE == 0, 'HEIGHT must be a multiple of UNITT_SIZE'
OBST_SIDE_MIN = 1
OBST_SIDE_MAX = 6
unit = UNIT_SIZE * UNIT_SIZE
total_units = int(PHOTO_WIDTH * HEIGHT / unit)
row_length = int(PHOTO_WIDTH / UNIT_SIZE)
column_height = int(HEIGHT / UNIT_SIZE)
all_rectangles = [] # The all_rectanles contains all the rectangles generated, list  of width, height, x, y coordinates.
orig_bgnd_img_input_path = 'bgnd_img_orig_pexels-nate-hovee-4659963.jpg'
user_img_input_path = ''
height_value = 0
width_value = 0
background_im_path = 'background_im.jpg'

# Constants for pygame
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 150
BALL_SIZE = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
FPS = 60
BALL_SPEED = 4
PADDLE_SPEED = 4
collision_tolerance = 10 # Tolerance for the obstacle collision only
point_to_win = 200

rectangle_to_hit = [] # Temp for hitable rectangle
whose_turn = 0 # Tracking who tuched the ball last in order to determine who receives the point for rectangle hit

player1_rects = [] # Rectangles hit by player 1, use this to draw the rectangles hit by player 1
player2_rects = [] # Rectangles hit by player 2, use this to draw the rectangles hit by player 2

player1_score = 0 # Track the score for player 1, score of the area of all the rectangles hit by player 1 and +50 if the ball left the screen on the player 2 side 
player2_score = 0 # Track the score for player 2, score of the area of all the rectangles hit by player 1 and +50 if the ball left the screen on the player 1 side

player1_color = (0, 0, 255)
player2_color = (255, 0, 0)

right_player_computer = True
game_state = 'start' # Track the game state: 'start', 'play', 'over'

music_on = 0.5
sound_fx_on = 1.0

# %%
# Check for possible way to cover the given length with the given pieces
# Although in this case negativ numbers are not considered but the function can produce a 'RecursionError: maximum recursion depth exceeded in comparison'.
def has_combination_sum_recursive(numbers, target_sum, current_sum=0):
    if current_sum == target_sum:
        return True
    if current_sum > target_sum:
        return False

    for num in numbers:
        new_sum = current_sum + num
        if has_combination_sum_recursive(numbers, target_sum, new_sum):
            return True

    return False

assert has_combination_sum_recursive([elem for elem in range(OBST_SIDE_MIN, OBST_SIDE_MAX + 1)], row_length) == True, 'Row cannot be covered with the given min and max values!'
assert has_combination_sum_recursive([elem for elem in range(OBST_SIDE_MIN, OBST_SIDE_MAX + 1)], column_height) == True, 'Column cannot be covered with the given min and max values!'


# %%
# Function for background image manipulation
def resize_and_crop(input_path = orig_bgnd_img_input_path, output_path = 'background_im.jpg', target_width=800, target_height=600):
    # Open the image
    original_image = Image.open(input_path)

    # Get the original image size
    original_width, original_height = original_image.size

    # 1. If x size is not 800 px, upscale or downscale the image
    if original_width != target_width:
        new_width = target_width
        new_height = int(target_width * (original_height / original_width))
        # temp_image = original_image.resize((new_width, new_height), Image.LANCZOS)

    # 2. Check if y size is less or more than 600 px
    if new_height:
        if new_height < target_height:
        # 3. If y size is less, upscale image to meet the target height
            final_height = target_height
            new_width = int(target_height * (new_width / new_height))
            new_height = final_height
    else:
        if original_height < target_height:
            final_height = target_height
            new_width = int(target_height * (original_width / original_height))
            new_height = final_height

    if new_height:
        temp_image = original_image.resize((new_width, new_height), Image.LANCZOS)
    else:
        pass

    # 4. Cut the 800 x 600 px size image from the transformed image, centered
    if temp_image:
        if new_height == target_height:
            if new_width == target_width:
                pass
            else:
                left = (new_width - target_width) / 2
                right = target_width + left
                bottom = target_height
                top = 0
        if new_width == target_width:
            left = 0
            right = target_width
            top = (new_height - target_height) / 2
            bottom = target_height + top

        cropped_image = temp_image.crop((left, top, right, bottom))

        # Save the result
        cropped_image.save(output_path)
        # temp_image.save('temp.jpg')

# %%
# Getting sys arguments
width_provided = False
height_provided = False
min_value = 0
max_value = 0


for i in range(1, len(sys.argv), 2):
    option = sys.argv[i].lower()
    if i + 1 < len(sys.argv):
        value = sys.argv[i + 1]
    else:
        value = 'na'
    if option == 'img':
        try:
            user_img_input_path = str(value)
            resize_and_crop(input_path = user_img_input_path, output_path = background_im_path, target_width = PHOTO_WIDTH, target_height = HEIGHT)
        except:
            print('Invalid image format. Using the default background image.')
    elif option == 'width':
        try:
            width_value = int(value)
            if not width_value % 40 and width_value > 1800:
                width_value = 0
                raise ValueError(f"Width must be a multiple of UNITT_SIZE (40px). Using default: {PHOTO_WIDTH} and for height: {HEIGHT}")
            if height_value:
                HEIGHT = max(600, int(height_value))  # Ensure minimum height of 600
                PHOTO_WIDTH = max(600, int(width_value))  # Ensure minimum width of 600
        except ValueError as ve:
            print(ve)  # Print the specific ValueError message
            print(f"Invalid value for width. Using default: {PHOTO_WIDTH} and for height: {HEIGHT}")
    elif option == 'height':
        try:
            height_value = int(value)
            if not width_value % 40 and width_value > 1800:
                height_value = 0
                raise ValueError(f"Height must be a multiple of UNIT_SIZE (40px). Using default: {HEIGHT} and for wifth: {PHOTO_WIDTH}")
            if width_value:
                HEIGHT = max(600, int(height_value))  # Ensure minimum height of 600
                PHOTO_WIDTH = max(600, int(width_value))  # Ensure minimum width of 600
        except ValueError as ve:
            print(ve)  # Print the specific ValueError message
            print(f"Invalid value for height. Using default: {HEIGHT} and for width: {PHOTO_WIDTH}")
    elif option == 'min':
        try:
            min_value = max(1, int(value))
        except ValueError:
            print(f"Invalid value for min. Using default: {OBST_SIDE_MIN} and for max: {OBST_SIDE_MAX}")
    elif option == 'max':
        try:
            max_value = max(1, int(value))
        except ValueError:
            print(f"Invalid value for max. Using default: {OBST_SIDE_MAX} and for min: {OBST_SIDE_MIN}")
    elif option == 'speed':
        try:
            if int(value) > 10 or int(value) < 1:
                raise ValueError(f"Invalid value for speed. Using default: {PADDLE_SPEED}")
            BALL_SPEED = max(1, int(value))
            PADDLE_SPEED = max(1, int(value))
        except ValueError:
            print(f"Invalid value for speed. Using default: {PADDLE_SPEED}")
    elif option == 'p1col':
        try:
            rgb_values = [int(val) for val in value.split(',')]
            if len(rgb_values) == 3 and all(0 <= val <= 255 for val in rgb_values):
                player1_color = tuple(rgb_values)
        except (ValueError, TypeError):
            print(f"Invalid RGB value for p1col. Using default: {player1_color}")
    elif option == 'p2col':
        try:
            rgb_values = [int(val) for val in value.split(',')]
            if len(rgb_values) == 3 and all(0 <= val <= 255 for val in rgb_values):
                player2_color = tuple(rgb_values)
        except (ValueError, TypeError):
            print(f"Invalid RGB value for p1col. Using default: {player2_color}")
    elif option == 'm':
        try:
            if 1.0 >= float(value) >= 0.0:
                music_on = float(value)
        except ValueError:
            print(f"Invalid value for music volume. Using default: {music_on}")
    elif option == 'sfx':
        try:
            if 1.0 >= float(value) >= 0.0:
                sound_fx_on = float(value)
        except ValueError:
            print(f"Invalid value for sound FX volume. Using default: {sound_fx_on}")
    elif option == 'paddle':
        try:
            if 600 > int(value) > 50:
                PADDLE_HEIGHT = int(value)
        except ValueError:
            (f"Invalid value for paddle height. Using default: {PADDLE_HEIGHT}")
    elif option == 'max_p':
        try:
            if 60000 > int(value) > 1:
                point_to_win = int(value)
        except ValueError:
            (f"Invalid value for winning points. Using default: {point_to_win}")
    elif option == 'pl2':
        right_player_computer = False

WIDTH = PHOTO_WIDTH + 30
unit = UNIT_SIZE * UNIT_SIZE
total_units = int(PHOTO_WIDTH * HEIGHT / unit)
if min_value and max_value:
    try:
        if (has_combination_sum_recursive([elem + 1 for elem in range(min(min_value, max_value) - 1, max(min_value, max_value))], int(HEIGHT / UNIT_SIZE)) and
            has_combination_sum_recursive([elem + 1 for elem in range(min(min_value, max_value) - 1, max(min_value, max_value))], int(PHOTO_WIDTH / UNIT_SIZE))) == False:
                raise ValueError(f"There are no valid arrangements of rectangles that completely cover the game field for the specified size. Using default: {OBST_SIDE_MIN} and for min: {OBST_SIDE_MAX}")
        OBST_SIDE_MIN = min(min_value, max_value) # Ensure min is less than max
        OBST_SIDE_MAX = max(min_value, max_value) # Ensure max is not less than min
    except ValueError as ve:
        print(ve)  # Print the specific ValueError message
        print(f"Using default values, min: {OBST_SIDE_MIN} and max: {OBST_SIDE_MAX}")
row_length = int(PHOTO_WIDTH / UNIT_SIZE)
column_height = int(HEIGHT / UNIT_SIZE)
if user_img_input_path:    
    resize_and_crop(input_path = user_img_input_path, output_path = background_im_path, target_width = PHOTO_WIDTH, target_height = HEIGHT)
elif width_provided or height_provided:
    resize_and_crop(input_path = orig_bgnd_img_input_path, output_path = background_im_path, target_width = PHOTO_WIDTH, target_height = HEIGHT)

# %%
# Function to randomize shapes, generate random shapes (width, hegiht) based on the given min and max parameters.
# The w_fix and h_fix parameters allow the function to freeze the given side, meaning generate only one random side keeping the one freezed. 
def randomize_size(min_x = OBST_SIDE_MIN, min_y = OBST_SIDE_MIN, max_x = OBST_SIDE_MAX, max_y = OBST_SIDE_MAX, w_fix = 0, h_fix = 0):
    if w_fix:
        width = w_fix
    else:
        width = random.randint(int(min_x), int(max_x))  # Choose a random multiple between min_x and max_x
    if h_fix:
        height = h_fix
    else:        
        height = random.randint(int(min_y), int(max_y))  # Choose a random multiple between min_y and max_y

    return [int(width), int(height)]

# %%
# Fill a row with rectangles (rectangles are lists with width and height) and define the rectangle x, y coordinates too and add it to the rectanlge as the last two values of the rectangle (list).
# Elements are lists with the element width and height.
# Calling the mark_pixels function to fill out the screen_matrix_state matrix.
def row_maker(screen_state_matrix, row_length = row_length, row_x = 0, row_y = 0):
    global all_rectangles
    x = row_x
    y = row_y
    act_row_length = 0
    while True:
        rand_rect = randomize_size()
        max_side_x = row_length - act_row_length - rand_rect[0]
        max_side_y = column_height - y - rand_rect[1]
        if not (has_combination_sum_recursive([elem for elem in range(OBST_SIDE_MIN, OBST_SIDE_MAX + 1)], int(max_side_y)) and
            has_combination_sum_recursive([elem for elem in range(OBST_SIDE_MIN, OBST_SIDE_MAX + 1)], int(max_side_x))) :
            continue
        # Column height check
        # Case one the height of the rand_rect leaves lesser space above it then the UNIT_SIZE makes it impossible to generate the rectangle
        # would be needed to cover the complete column.
        # In this case we need to generate a rectangle until we either get the minimum space above the rand_rect enough to generate the next rectangle
        # or no space at all, meaning the created element the last element and covering exactly the available squares above it along its width.
        if 0 < max_side_y < OBST_SIDE_MIN:
            while True:
                rand_rect = randomize_size(w_fix = rand_rect[0])
                max_side_y = column_height - y - rand_rect[1]
                if max_side_y >= OBST_SIDE_MIN or max_side_y == 0:
                    break
        # Case two when the last rectangle extends over the top of the column. In this case we need to generate a rectangle until
        # the minimum space above the rand_rect enough to generate the next rectangle
        # or no space at all, meaning the created element the last element and covering exactly the available squares above it along its width.
        # The max height of this rectangle is the number of the available squares above the last generated one.
        if max_side_y < 0:
            while True:
                rand_rect = randomize_size(max_y = column_height - y, w_fix = rand_rect[0])
                max_side_y = column_height - y - rand_rect[1]
                if max_side_y >= OBST_SIDE_MIN or max_side_y == 0:
                    break
        # Case three when the rand_rect fits exactly to the top of the column, no free suqares left above it.
        # Go to check the width of the rand_rect and fix the height of the rand_rect since it is perfect.
        if max_side_y == 0:
            pass

        # Row length check
        # Case one when the defined rectangle placed to the end of the existing row of rectangles
        # leaves lesser space to the end of the row then the UNIT_SIZE makes it impossible to generate the rectangle
        # would be needed to cover the complete row.
        # In this case we need to generate a rectangle until we either get the minimum space at the end of the row enough to generate the next rectangle
        # or no space at all, meaning the created element the last element and covering exactly the available squares to the row end.  
        if 0 < max_side_x < OBST_SIDE_MIN:
            while True:
                rand_rect = randomize_size(h_fix = rand_rect[1])
                max_side_x = row_length - act_row_length - rand_rect[0]
                if max_side_x >= OBST_SIDE_MIN or max_side_x == 0:
                    break
        # Case two when the last rectangle extends over the row end. In this case we need to generate a rectangle until
        # we either get the minimum space at the end of the row enough to generate the next rectangle
        # or no space at all, meaning the created element the last element and covering exactly the available squares to the row end.
        # The max width of this rectangle is the number of the available squares in the row.
        if max_side_x < 0:
            while True:
                rand_rect = randomize_size(max_x = row_length - act_row_length, h_fix=rand_rect[1])
                max_side_x = row_length - act_row_length - rand_rect[0]
                if max_side_x >= OBST_SIDE_MIN or max_side_x == 0:
                    break
        # Case thre when we have a rectangle covering all the available squares exactely. We done with the row,
        # next up is the 'screen_state_matrix' markup function.
        if max_side_x == 0:
            all_rectangles.append(rand_rect + [x + act_row_length, y])
            mark_pixels(screen_state_matrix, all_rectangles[-1])
            return screen_state_matrix
        all_rectangles.append(rand_rect + [x + act_row_length, y])
        act_row_length += rand_rect[0]
        mark_pixels(screen_state_matrix, all_rectangles[-1])

# %%
# Updating the 'screen_state_matrix' with the 'rectangle'. Populating with 1 the values of the screen_state_matrix squares correspond to the 'rectangle'.
def mark_pixels(screen_state_matrix, rectangle):
    # Mark entire rectangular area in the matrix with 1s
    for i in range(rectangle[1]):
        for j in range(rectangle[0]):
            screen_state_matrix[rectangle[3] + i][rectangle[2] + j] = 1
    return screen_state_matrix

# %%
# Creates a screen_state_matrix to follow the state of the rectangle generation process.
# The 'screen_state_matrix' is a 'row_length' x 'column_height' matrix.
# 0 indicates where the screen is not yet populated with elements, 1 marks the occupied squares.
# 1 square size is defined by the 'UNIT_SIZE' variable (i.e. total unit in a row row length in pixels / UNIT_SIZE).
# This function scan all the squares in the 'screen_state_matrix' and if locate an empty square check how many consecutive empty squares
# are available in the given row_y. Invoke the row_maker function and pass the following details: row length (available consecutive free squares),
# the x, and y coordinates of the starting point of the row.
# The function finished when now availbla square left in the 'screen_state_matrix'.
def table_maker():
    screen_state_matrix = row_maker(screen_state_matrix = [[0 for _ in range(row_length)] for _ in range(column_height)], row_length = PHOTO_WIDTH / UNIT_SIZE, row_x = 0, row_y = 0)
    table_ready = False
    state = (0, 0) # Start the loop from the last checked element of the matrix.
    while not table_ready:
        for nr_y in range(state[1], len(screen_state_matrix)):
            start_coord = 0
            for nr_x, x in enumerate(screen_state_matrix[nr_y][state[0]:], start=state[0]):
                state = (0, 0)
                end_loop = 0
                if x == 0:
                    if not start_coord:
                        if nr_x == 0:
                            start_coord = 0.4 # We need some value when we check if wwe have start_coord, 0 would mean None
                        else:
                            start_coord = nr_x
                    if nr_x == row_length - 1:
                        row_maker(screen_state_matrix, row_length = row_length - int(start_coord), row_x = int(start_coord), row_y = nr_y)
                        state = (nr_x, nr_y)
                        end_loop = 1
                        break
                    else:
                        pass
                if x == 1:
                    if start_coord:
                        row_maker(screen_state_matrix, row_length = nr_x - int(start_coord), row_x = int(start_coord), row_y = nr_y)
                        state = (nr_x, nr_y)
                        end_loop = 1
                        break
                    if nr_x == row_length - 1 and nr_y == column_height - 1:
                        table_ready = True
                        end_loop = 1
                        break
            if end_loop:    
                break

# %%
# Random colors for rows from these option since taking rndom from the full color palette.
# color = random.choice([(r, g, b) for r in range(256) for g in range(256) for b in range(256) if (r, g, b) not in [black, white, gray]])
# is taking too much time.

color_dict = {
    'Red': {'normal': (255, 0, 0), 'light': (255, 102, 102), 'dark': (139, 0, 0)},
    'Blue': {'normal': (0, 0, 255), 'light': (173, 216, 230), 'dark': (0, 0, 139)},
    'Green': {'normal': (0, 255, 0), 'light': (144, 238, 144), 'dark': (0, 100, 0)},
    'Yellow': {'normal': (255, 255, 0), 'light': (255, 255, 153), 'dark': (204, 204, 0)},
    'Orange': {'normal': (255, 165, 0), 'light': (255, 204, 153), 'dark': (255, 140, 0)},
    'Cyan': {'normal': (0, 255, 255), 'light': (224, 255, 255), 'dark': (0, 139, 139)},
    'Brown': {'normal': (165, 42, 42), 'light': (210, 105, 30), 'dark': (139, 69, 19)},
    'Pink': {'normal': (255, 182, 193), 'light': (255, 182, 193), 'dark': (255, 20, 147)}
}

def get_random_color(history=None):
    if history is None:
        # Keeping track of the used colors.
        history = []

    if len(history) == len(color_dict) * 3:
        # If all variants have been used for all colors, reset the history.
        history = []

    available_choices = [(color, variant) for color in color_dict.keys() for variant in ['normal', 'light', 'dark'] if (color, variant) not in history]

    chosen_color, chosen_variant = random.choice(available_choices)
    history.append((chosen_color, chosen_variant))

    return color_dict[chosen_color][chosen_variant], history

# %%
# The pygame part of pongify

# Game classes
class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y, color = (255, 255, 255)):
        super().__init__()
        self.color = color
        self.image = pygame.Surface((PADDLE_WIDTH, PADDLE_HEIGHT))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, keys=None, ball=None, human = 0):
        if human == 1:
            if keys[pygame.K_UP] and self.rect.top > 0:
                self.rect.y -= PADDLE_SPEED
            if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
                self.rect.y += PADDLE_SPEED
        elif human == 2:
            if keys[pygame.K_s] and self.rect.top > 0:
                self.rect.y -= PADDLE_SPEED
            if keys[pygame.K_x] and self.rect.bottom < HEIGHT:
                self.rect.y += PADDLE_SPEED
        elif ball:
            # Player 2 (right paddle) follows the ball.
            if self.rect.centery < ball.rect.centery:
                self.rect.y += PADDLE_SPEED
            elif self.rect.centery > ball.rect.centery:
                self.rect.y -= PADDLE_SPEED


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE))
        self.update_img()
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.dx = random.choice([-1, 1]) * BALL_SPEED
        self.dy = random.choice([-1, 1]) * BALL_SPEED

    # Required to change the color of the ball when player paddle hits it.
    # Easiest way I find to update the color since self.image.fill is read only.
    def update_img(self, color = (255, 255, 255)):
        self.image.fill(color)

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Bounce off the top and bottom.
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, width = 0, height =0):
        super().__init__()
        self.width = width
        self.height = height
        self.rect = pygame.Rect(0, 0, 0, 0)  # Initialize the rect attribute.
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(GRAY)
        self.spawn_time = 0  # Timestamp when the obstacle is spawned.
        self.font = pygame.font.Font(None, 32)  # Font for displaying text.
    
    def draw_text(self, screen):
        text = f"{p.number_to_words(int(self.rect.width * self.rect.height / UNIT_SIZE ** 2))}"
        text_render = self.font.render(text, True, WHITE)
        text_rect = text_render.get_rect(center=(self.rect.centerx, self.rect.centery))
        if text_rect.width > self.width -10 and self.height > self.width:
            if text_rect.height > self.height - 10:
                # Change the font size to 24.
                self.font = pygame.font.Font(None, 24)
                text_render = self.font.render(text, True, WHITE)
                text_rect = text_render.get_rect(center=(self.rect.centerx, self.rect.centery))
            # Rotate the text_render surface.
            rotated_text_render = pygame.transform.rotate(text_render, 90)
            rotated_text_rect = rotated_text_render.get_rect(center=(self.rect.centerx, self.rect.centery))
            screen.blit(rotated_text_render, rotated_text_rect)
        elif text_rect.width > self.width - 10 and self.width == self.height:
            self.font = pygame.font.Font(None, 24)
            text_render = self.font.render(text, True, WHITE)
            text_rect = text_render.get_rect(center=(self.rect.centerx, self.rect.centery))
            screen.blit(text_render, text_rect)
        else:
            # Blit the non-rotated text onto the screen.
            screen.blit(text_render, text_rect)

    def draw_thicker_rectangle(self, screen):
        # Draw the obstacle with thicker lines.
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect.inflate(-10, -10))


# Game functions
def reset_game(ball):
    global player1_score, player2_score, player1_rects, player2_rects
    global game_state, all_rectangles, rectangle_to_hit, whose_turn

    all_rectangles = []

    table_maker()

    # Reset rectangles.
    all_rectangles = [[element * UNIT_SIZE + 15 if i == 2 else element * UNIT_SIZE for i, element in enumerate(sublist)] for sublist in all_rectangles]
    history = []
    for i in range(len(all_rectangles)):
        color, history = get_random_color(history=history)
        all_rectangles[i].append(color)

    # Reset scores.
    player1_score = 0
    player2_score = 0

    player1_rects = []
    player2_rects = []

    # Reset game state.
    game_state = 'start'

    rectangle_to_hit = []
    whose_turn = 0

    try:
        ball.rect.center = (WIDTH // 2, HEIGHT // 2)
        ball.update_img()
    except:
        pass


def show_scores(screen):
    font = pygame.font.Font(None, 50)
    player1_score_text = font.render(f"{player1_score}", True, WHITE)
    player2_score_text = font.render(f"{player2_score}", True, WHITE)

    screen.blit(player1_score_text, (30, 20))  # Top-left corner.
    screen.blit(player2_score_text, (WIDTH - player2_score_text.get_width() - 30, 20))  # Top-right corner.


def show_countdown(count, background_image, screen, all_sprites, obstacles, beep_sound):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))  # Adjust the last value (alpha) to control opacity.

    font = pygame.font.Font(None, 100)
    text = font.render(str(count), True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    background_rect = background_image.get_rect()
    screen.blit(background_image, ((WIDTH - background_rect.width) // 2, (HEIGHT - background_rect.height) // 2))  # Draw the background.
    
    # Draw the colored rectangles.
    for size in all_rectangles:
        rect = pygame.Rect(size[2], size[3], size[0], size[1])
        pygame.draw.rect(screen, size[4], rect)
    all_sprites.draw(screen)  # Draw sprites.
    for obstacle in obstacles:
        pygame.draw.rect(screen, WHITE, obstacle.rect)
        obstacle.draw_text(screen)

    screen.blit(overlay, (0, 0))  # Apply the overlay.
    screen.blit(text, text_rect)
    pygame.display.flip()
    beep_sound.play()
    pygame.time.wait(1000)  # Wait for 1 second.


def game_over(screen, background_image, all_sprites, obstacles, clock):
    waiting_for_input = True
    draw_background = False
    # While loop to wait for user.
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    waiting_for_input = False
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_p:
                    draw_background = not draw_background  # Toggle between showing background and final scoreboard.

        if draw_background:
            screen.fill(BLACK)
            background_rect = background_image.get_rect()
            screen.blit(background_image, ((WIDTH - background_rect.width) // 2, (HEIGHT - background_rect.height) // 2))
        else:
            background_rect = background_image.get_rect()
            screen.blit(background_image, ((WIDTH - background_rect.width) // 2, (HEIGHT - background_rect.height) // 2))
            for size in all_rectangles:
                rect = pygame.Rect(size[2], size[3], size[0], size[1])
                pygame.draw.rect(screen, size[4], rect)
            all_sprites.draw(screen)
            for obstacle in obstacles:
                obstacle.draw_thicker_rectangle(screen)
                obstacle.draw_text(screen)

            # Draw colored rectangles
            for rect in player1_rects:
                pygame.draw.rect(screen, player1_color, (rect[2], rect[3], rect[0], rect[1]), 3)  # Player1 color border.
            for rect in player2_rects:
                pygame.draw.rect(screen, player2_color, (rect[2], rect[3], rect[0], rect[1]), 3)  # Player2 color border.

            # Draw transparent gray layer
            transparent_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            transparent_surface.fill((0, 0, 0, 165))  # Adjust opacity as needed.
            screen.blit(transparent_surface, (0, 0))

            # Display instructions
            font = pygame.font.Font(None, 32)
            start_text = font.render("Press 'n' to start a new game or 'q' to quit", True, WHITE)
            start_text_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT - (HEIGHT // 6)))
            screen.blit(start_text, start_text_rect)
            photo_text = font.render("Press 'p' to toggle between background and final game state.", True, WHITE)
            photo_text_rect = photo_text.get_rect(center=(WIDTH // 2, HEIGHT - (HEIGHT // 6) + 40))
            screen.blit(photo_text, photo_text_rect)

            # Display final scores
            font = pygame.font.Font(None, 48)
            final_score_text = font.render(f"Final Scores", True, WHITE)
            final_score_text_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 6))
            screen.blit(final_score_text, final_score_text_rect)
            player1_score_text = font.render(f"Player 1: {player1_score}, rectangle hit: {len(player1_rects)} / {len(all_rectangles)}", True, player1_color)
            player1_score_text_rect = player1_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 6 + 100))
            screen.blit(player1_score_text, player1_score_text_rect)
            player2_score_text = font.render(f"Player 2: {player2_score}, rectangle hit: {len(player2_rects)} / {len(all_rectangles)}", True, player2_color)
            player2_score_text_rect = player2_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 6 + 180))
            screen.blit(player2_score_text, player2_score_text_rect)

        pygame.display.flip()
        clock.tick(FPS)


def spawn_obstacle(all_sprites, obstacles, obstacle_timer, obstacle_timeout):

    current_time = pygame.time.get_ticks()

    if random.randint(0, 100) < 50 and current_time - obstacle_timer > obstacle_timeout:  # Adjust probability and timeout as needed.
        # Choose a random element from the table.
        element = random.choice(all_rectangles)
        rectangle_to_hit = element
        
        # Create a new Obstacle instance.
        obstacle = Obstacle(width=element[0], height=element[1])
        obstacle.spawn_time = current_time

        obstacle.rect = pygame.Rect(element[2], element[3], element[0], element[1])

        obstacles.add(obstacle)
        all_sprites.add(obstacle)
        obstacle_timer = current_time

        return obstacle, rectangle_to_hit


def main():
    global player1_score, player2_score, game_state, whose_turn

    # Initialize Pygame
    # The sound initialization might seems messy, these are to try to avoid sound delay... not perfect though.
    pygame.mixer.pre_init(22050, -16, 2, 64)
    pygame.init()
    pygame.mixer.quit()
    pygame.mixer.init(22050, -16, 2, 64)

    # Loads game music and sets the volume to 50%
    pygame.mixer.music.load('sound/x2mate.com - Timothy Seals - Chasing Voids (Unreal Tournament 4 CTF-BigRock) (128 kbps).mp3')
    pygame.mixer.music.set_volume(music_on)

    # Sound effects and voices
    beep_sound = pygame.mixer.Sound('sound/beep-07a.wav')
    ball_left_sound = pygame.mixer.Sound('sound/analog-warm-pluck-132826.mp3')
    paddle_hit_sound = pygame.mixer.Sound('sound/sonarping-38269.mp3')
    obs_hit_sound = pygame.mixer.Sound('sound/hit-sound-effect-12445.mp3')
    yes_sound = pygame.mixer.Sound('sound/Rose (Urgent)-yes.wav')
    yeah_sound = pygame.mixer.Sound('sound/Rose (Urgent)-yeah.wav')
    oh_yeah_sound = pygame.mixer.Sound('sound/Rose (Urgent)-oh_yeah.wav')
    come_on_sound = pygame.mixer.Sound('sound/Rose (Urgent)-come_on.wav')
    start_sound = pygame.mixer.Sound('sound/Rose (Urgent)-start.wav')
    go_sound = pygame.mixer.Sound('sound/Rose (Urgent)-yes.wav')
    general_sfx = [sfx.set_volume(sound_fx_on) for sfx in [beep_sound, ball_left_sound, paddle_hit_sound, obs_hit_sound]]
    come_on_list = [yes_sound, yeah_sound, oh_yeah_sound, come_on_sound]
    [sfx.set_volume(sound_fx_on) for sfx in [yes_sound, yeah_sound, oh_yeah_sound, come_on_sound]]
    start_list = [start_sound, go_sound]
    [sfx.set_volume(sound_fx_on) for sfx in [start_sound, go_sound]]

    # Initialize screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pongify")
    clock = pygame.time.Clock()

    background_image = pygame.image.load(background_im_path)

    # Creates sprites: paddles and ball
    player1_paddle = Paddle(0, (HEIGHT - PADDLE_HEIGHT) // 2, player1_color)
    player2_paddle = Paddle(WIDTH - PADDLE_WIDTH, (HEIGHT - PADDLE_HEIGHT) // 2, player2_color)
    ball = Ball()

    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    paddles = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    # Add paddles, ball, and obstacle to sprite groups
    all_sprites.add(player1_paddle, player2_paddle, ball)
    paddles.add(player1_paddle, player2_paddle)
    balls.add(ball)

    # Function to spawn obstacle at random times
    obstacle_timeout = 2000  # in milliseconds.
    obstacle_timer = 0
    obstacle_active = False

    # Initialize the game
    reset_game(ball)

    # Main game loop
    game_on = True
    while game_on:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_time = pygame.time.get_ticks()

        keys = pygame.key.get_pressed()

        # Update paddles, ball, and obstacle
        if right_player_computer:
            player1_paddle.update(keys=keys, human = 1) # human = 1: up and down arrows.
            player2_paddle.update(ball=ball) # ball means computer controlled.
        else:
            player1_paddle.update(keys=keys, human = 2) # human = 2 's' up, 'x' down.
            player2_paddle.update(keys=keys, human = 1) # human = 1: up and down arrows.

        balls.update()

        # Spawn obstacle if there is no active obstacle.
        if not obstacle_active:
            try:
                obstacle, rectangle_to_hit = spawn_obstacle(all_sprites, obstacles, obstacle_timer, obstacle_timeout)
                if obstacle:
                    obstacle_active = True
            except:
                pass

        # Remove the obstacle after 5 seconds if not hit
        if obstacle_active and current_time - obstacle.spawn_time > 5000:
            obstacles.remove(obstacle)
            all_sprites.remove(obstacle)
            obstacle_active = False

        # Check for collisions with paddles
        if ball.rect.colliderect(player1_paddle.rect):
            ball.dx *= -1
            ball.rect.left = player1_paddle.rect.right
            whose_turn = 1
            paddle_hit_sound.play()
            ball.update_img(player1_color)

        if ball.rect.colliderect(player2_paddle.rect):
            ball.dx *= -1
            ball.rect.right = player2_paddle.rect.left
            whose_turn = 2
            paddle_hit_sound.play()
            ball.update_img(player2_color)


        # Check for collisions with the obstacle using colliderect
        if obstacle_active and ball.rect.colliderect(obstacle.rect):

            obs_hit_sound.play()
            if abs(ball.rect.top - obstacle.rect.bottom) < collision_tolerance:
                ball.dy *= -1
                ball.rect.top = obstacle.rect.bottom + 1  # Move the ball just outside the obstacle.
            if abs(ball.rect.bottom - obstacle.rect.top) < collision_tolerance:
                ball.dy *= -1
                ball.rect.bottom = obstacle.rect.top - 1  # Move the ball just outside the obstacle.
            if abs(ball.rect.left - obstacle.rect.right) < collision_tolerance:
                ball.dx *= -1
                ball.rect.left = obstacle.rect.right + 1  # Move the ball just outside the obstacle.
            if abs(ball.rect.right - obstacle.rect.left) < collision_tolerance:
                ball.dx *= -1
                ball.rect.right = obstacle.rect.left - 1  # Move the ball just outside the obstacle.

            # Plays sound if big hit.
            if obstacle.rect.width * obstacle.rect.height // UNIT_SIZE ** 2 > 12:
                random.choice(come_on_list).play()

            if whose_turn == 1:
                player1_rects.append(rectangle_to_hit)
                player1_score += obstacle.rect.width * obstacle.rect.height // UNIT_SIZE ** 2
                all_rectangles.remove(rectangle_to_hit)
                obstacles.remove(obstacle)
                all_sprites.remove(obstacle)
                obstacle_active = False
            elif whose_turn == 2:
                player2_rects.append(rectangle_to_hit)
                player2_score += obstacle.rect.width * obstacle.rect.height // UNIT_SIZE ** 2
                all_rectangles.remove(rectangle_to_hit)
                obstacles.remove(obstacle)
                all_sprites.remove(obstacle)
                obstacle_active = False
            else:
                obstacles.remove(obstacle)
                all_sprites.remove(obstacle)
                obstacle_active = False


        # Check for ball leaving
        if ball.rect.left <= 0 or ball.rect.right >= WIDTH:
            if ball.rect.left <= 0:
                player2_score += 50
                whose_turn = 1
                ball.update_img(player1_color)
            else:
                player1_score += 50
                whose_turn = 2
                ball.update_img(player2_color)
            ball_left_sound.play()
            ball.rect.center = (WIDTH // 2, HEIGHT // 2)
            ball.dx *= random.choice([-1, 1])

        # Check for game over
        if len(all_rectangles) == 0 or point_to_win and (player1_score > point_to_win or player2_score > point_to_win):
            if game_state != 'over':
                game_state = 'over'

        # Draw background
        screen.fill(BLACK)
        background_rect = background_image.get_rect()
        screen.blit(background_image, ((WIDTH - background_rect.width) // 2, (HEIGHT - background_rect.height) // 2))

        # Draw rectangles
        # font = pygame.font.Font(None, 28)
        for size in all_rectangles:
            rect = pygame.Rect(size[2], size[3], size[0], size[1])
            pygame.draw.rect(screen, size[4], rect)
            # # Get text surface and rectangle to center the text
            # text = f"{size[0]} x {size[1]}"
            # text_surface = font.render(text, True, BLACK)
            # text_rect = text_surface.get_rect(center=(rect.centerx, rect.centery))

            # # Draw the text on the screen
            # screen.blit(text_surface, text_rect)

        # Draw sprites
        all_sprites.draw(screen)

        for obstacle in obstacles:
            obstacle.draw_thicker_rectangle(screen)
            obstacle.draw_text(screen)

        show_scores(screen)

        # Countdown at the start
        if game_state == 'start':
            pygame.mixer.music.stop()
            for count in range(3, 0, -1):
                show_countdown(count, background_image, screen, all_sprites, obstacles, beep_sound)
            random.choice(start_list).play()
            game_state = 'play'
            pygame.mixer.music.play(loops=-1)

        # Draw scoreboard
        if game_state == 'over':
            game_over(screen, background_image, all_sprites, obstacles, clock)
            reset_game(ball)
        
        # Update display
        pygame.display.flip()
            
        # Cap the frame rate
        clock.tick(FPS)

if __name__ == "__main__":
    main()
