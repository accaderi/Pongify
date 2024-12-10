# Pongify App

Youtube link: <a href="[https://www.youtube.com/watch?v=fk2l6p7Q744](https://youtu.be/skKTsMTlP0c)">[https://www.youtube.com/watch?v=fk2l6p7Q744](https://youtu.be/skKTsMTlP0c)</a>

The Pongify app is a Python application that leverages the Pygame library to create an interactive game. The following is an in-depth overview of its key components and functionalities:

## 1. Imports and Setup
- The app imports necessary libraries such as `pillow`, `pygame`, `sys`, `random`, and `inflect`.
- It defines constants and variables for the game, including screen dimensions, unit size, paddle dimensions, ball size, colors, frame rate, and more.
- The game can be started with the following optional arguments:
    - img: the path of the desired background image in jpg format (if it is in the game main dir just the name of the file i.e.: myimage.jpg)
    - width: width of the playing field (in pixels), has to be a multiple of the UNIT_SIZE defined 40px, min value is 600px max value is 1800px.
    - height: height of the playing field (in pixels), has to be a multiple of the UNIT_SIZE defined 40px, min value is 600px max value is 1800px.
    - min: the minimum length of the random generated rectangles (whole numbers from 1 to 12, min. 1 = 40px)
    - max: the maximum length of the random generated rectangles (whole numbers from 1 to 12, 1 = 40px)
    - speed: the speed of the paddles and the ball (whole numbers, between 1 and 10)
    - p1col: color for player 1 (r, g, b) each being a whole number between 0 and 255
    - p2col: color for player 2 (r, g, b) each being a whole number between 0 and 255
    - paddle: length of the paddles in pixel. (min. 50px, max. 600px)
    - max_p: required points to win the game (between 1 and 60000)
    - pl2: 'h', human player 2, controls for pl1: 's' - up, 'x' - down, pl2 up and down arrow
    - m: volume of the music between 0 - 1 (0 is off 1 is 100%)
    - sfx: volume of the sound FX between 0 - 1 (0 is off 1 is 100%)


## 2. Background Image Processing
- The Pillow library (`PIL`) is employed to process a background image (`background_im.jpg`) and resize/crop it to fit the game screen dimensions.

## 3. Randomization Functions
- The app includes functions like `randomize_size` to generate random width and height for game elements.
- `get_random_color` is used to get a random color from a predefined dictionary.

## 4. Row and Matrix Handling
- The app utilizes a the `screen_state_matrix' to follow the covered screen area during the random rectangles generation process.

### 4.1 `table_maker`
The `table_maker` is the 'manager' function. 

Scans all the squares in the 'screen_state_matrix' and if locate an empty square check how many consecutive empty squares are available in the given row_y.

Invoke the row_maker function and passes the following details:
- row length (available consecutive free squares),
- the x, and y coordinates of the starting point of the row.

The function finished when no availbla square left in the 'screen_state_matrix'.

```python
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
```

### 4.3 `screen_state_matrix`
The screen_state_matrix is a 2D matrix that represents the current state of the rectangle generation. Each element in the matrix corresponds to a UNIT_SIZE corresponds 40px x 40px on the screen.

```python
print(screen_state_matrix)
[[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
 [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
 [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
 [0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
 [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
 [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
```

## 6. Pygame Initialization
- Pygame is initialized, and the app loads music, sounds, and sets up the game window.

## 7. Game Classes
- Classes like `Paddle`, `Ball`, and `Obstacle` are defined to represent game entities with their properties and behaviors.

## 8. Game Functions
- Functions like `reset_game`, `show_scores`, `show_countdown`, `game_over`, and `spawn_obstacle` are implemented to manage various aspects of the game.

## 9. Game Initialization and Sprite Handling
- The app initializes game entities (paddles, ball) and sprite groups.

## 10. Main Game Loop
- The main loop handles user input, updates game entities, checks for collisions, and manages the game state.

## 11. Obstacle Handling
- Logic for spawning and handling obstacles, including collisions with the ball and players.

## 12. Point System and Game End Conditions
- A scoring system is implemented based on the area of rectangles hit, along with conditions for ending the game. If a player let the ball leave the screen the opponent receives 50 points.

## 13. Drawing Elements
- The app draws the background, rectangles, and other game elements on the screen.

## 14. Audio Handling
- It loads and plays various sounds during different game events.

## 15. User Input Handling
- The app processes user input to control the paddles and interact with the game.

## 16. Overall Game Flow
- The game progresses through different states (`start`, `play`, `over`) based on certain conditions.

## 17. Exception Handling
- The app includes mechanisms to handle potential errors when processing background images and command line arguments.
- The app accepts several keyword arguments. Those are validated.

The most important ones:

Checking for valid screen width and height
```python
 if not width_value % 40 and width_value > 1800:
                width_value = 0
                raise ValueError(f"Width must be a multiple of UNITT_SIZE (40px). Using default: {PHOTO_WIDTH} and for height: {HEIGHT}")
```

Checking and correcting the provided min and max valuees for random rectangle generation:

```python
if (has_combination_sum_recursive([elem + 1 for elem in range(min(min_value, max_value) - 1, max(min_value, max_value))], column_height) and
has_combination_sum_recursive([elem + 1 for elem in range(min(min_value, max_value) - 1, max(min_value, max_value))], row_length)) == False:
    raise ValueError(f"There are no valid arrangements of rectangles that completely cover the game field for the specified size. Using default: {OBST_SIDE_MIN} and for min: {OBST_SIDE_MAX}")
OBST_SIDE_MIN = min(min_value, max_value) # Ensure min is less than max
OBST_SIDE_MAX = max(min_value, max_value) # Ensure max is not less than min
```
The `has_combination_sum_recursive` function:

```python
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
```

## 18. Directory structure

```pongify/
    background_im.jpg - 121155 bytes
    bgnd_img_orig_pexels-nate-hovee-4659963.jpg - 3778924 bytes
    pongify.py - 37626 bytes
    requirements.txt - 1964 bytes
    sound/
        analog-warm-pluck-132826.mp3 - 384768 bytes
        beep-07a.wav - 9702 bytes
        hit-sound-effect-12445.mp3 - 145920 bytes
        Rose (Urgent)-come_on.wav - 21548 bytes
        Rose (Urgent)-go.wav - 14892 bytes
        Rose (Urgent)-oh_yeah.wav - 24108 bytes
        Rose (Urgent)-start.wav - 29228 bytes
        Rose (Urgent)-yeah.wav - 13868 bytes
        Rose (Urgent)-yes.wav - 21548 bytes
        sonarping-38269.mp3 - 96966 bytes
        x2mate.com - Timothy Seals - Chasing Voids (Unreal Tournament 4 CTF-BigRock) (128 kbps).mp3 - 4714415 bytes
```

