import pygame
import random
import os
import sys

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

CELL_SIZE = 20

GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

FPS = 60

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption("Snake")

clock = pygame.time.Clock()

BACKGROUND = (14, 17, 19)
GRID_COLOR = (27, 31, 34)

WHITE = (245, 245, 245)
GRAY = (150, 155, 160)

GREEN_HEAD = (75, 230, 105)
GREEN_BODY = (45, 190, 78)
GREEN_TAIL = (30, 145, 58)

APPLE_RED = (235, 55, 55)
APPLE_LIGHT = (255, 130, 130)
APPLE_DARK = (180, 35, 35)

OBSTACLE = (85, 92, 102)
OBSTACLE_BORDER = (145, 150, 160)

YELLOW = (255, 215, 70)
RED = (240, 65, 65)

MENU_GREEN = (80, 230, 110)

PANEL = (28, 32, 36)
PANEL_BORDER = (75, 80, 85)

TITLE_FONT = pygame.font.Font(None, 90)
BIG_FONT = pygame.font.Font(None, 64)
FONT = pygame.font.Font(None, 34)
SMALL_FONT = pygame.font.Font(None, 24)

MENU = "menu"
DIFFICULTY_MENU = "difficulty"
MAP_MENU = "map"
HIGH_SCORE_MENU = "high_score"
PLAYING = "playing"

game_state = MENU

DIFFICULTIES = {
    "EASY": 7,
    "NORMAL": 10,
    "HARD": 15
}

DIFFICULTY_NAMES = [
    "EASY",
    "NORMAL",
    "HARD"
]

MAP_NAMES = [
    "CLASSIC",
    "BLOCKS",
    "ISLANDS"
]

selected_difficulty = 1
selected_map = 0

menu_selection = 0

HIGH_SCORE_FILE = "highscore.txt"


def load_high_score():
    """Load high score safely."""

    if not os.path.exists(HIGH_SCORE_FILE):
        return 0

    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            value = int(file.read().strip())

        return max(0, value)

    except (ValueError, OSError):
        return 0


def save_high_score(value):
    """Save high score safely."""

    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(value))

    except OSError:
        pass


high_score = load_high_score()

snake = []
direction = (1, 0)

apple = None

score = 0

game_over = False
paused = False

confirm_quit = False

confirm_menu = False

shake_timer = 0

new_high_score = False

MOVE_EVENT = pygame.USEREVENT + 1



def get_base_speed():
    """Return starting speed for selected difficulty."""

    difficulty = DIFFICULTY_NAMES[selected_difficulty]

    return DIFFICULTIES[difficulty]


def get_current_speed():
    """
    Increase speed every 5 points.
    Maximum speed is 25 moves per second.
    """

    base_speed = get_base_speed()

    speed_bonus = score // 5

    return min(
        base_speed + speed_bonus,
        25
    )


def update_move_timer():
    """Update snake movement timer."""

    speed = get_current_speed()

    interval = int(
        1000 / speed
    )

    interval = max(
        interval,
        20
    )

    pygame.time.set_timer(
        MOVE_EVENT,
        interval
    )


def stop_move_timer():
    """Stop snake movement."""

    pygame.time.set_timer(
        MOVE_EVENT,
        0
    )


def create_map(map_name):
    """Create obstacles for the selected map."""

    result = set()

    if map_name == "CLASSIC":

        return result


    if map_name == "BLOCKS":

        for x in range(5, 10):
            for y in range(5, 7):
                result.add((x, y))

        for x in range(20, 25):
            for y in range(5, 7):
                result.add((x, y))

        for x in range(5, 10):
            for y in range(23, 25):
                result.add((x, y))

        for x in range(20, 25):
            for y in range(23, 25):
                result.add((x, y))

        return result

    if map_name == "ISLANDS":

        for x in range(5, 10):

            for y in range(5, 9):

                result.add((x, y))

        result.discard((7, 8))
        

        for x in range(20, 25):

            for y in range(5, 9):

                result.add((x, y))

        result.discard((22, 8))


        for x in range(5, 10):

            for y in range(21, 25):

                result.add((x, y))

        result.discard((7, 21))


        for x in range(20, 25):

            for y in range(21, 25):

                result.add((x, y))

        result.discard((22, 21))


        for x in range(14, 17):

            for y in range(13, 16):

                result.add((x, y))

        result.discard((15, 13))
        result.discard((13, 14))
        result.discard((16, 14))
        result.discard((15, 16))

        return result

    return result



def spawn_apple():
    """
    Spawn apple on a free cell.

    Apple will never spawn:
    - inside the snake
    - inside an obstacle
    """

    free_positions = []

    for x in range(GRID_WIDTH):

        for y in range(GRID_HEIGHT):

            position = (x, y)

            if position in snake:
                continue

            if position in obstacles:
                continue

            free_positions.append(position)

    if not free_positions:

        return None

    return random.choice(
        free_positions
    )


def reset_game():
    """Reset the game and select a safe spawn."""

    global snake
    global direction
    global apple
    global score
    global game_over
    global paused
    global obstacles
    global confirm_quit
    global confirm_menu
    global shake_timer
    global new_high_score

    score = 0

    game_over = False
    paused = False

    confirm_quit = False
    confirm_menu = False

    shake_timer = 0
    new_high_score = False

    obstacles = create_map(
        MAP_NAMES[selected_map]
    )

    if MAP_NAMES[selected_map] == "ISLANDS":

        snake = [
            (10, 18),
            (9, 18),
            (8, 18),
            (7, 18)
        ]

        direction = (1, 0)

    elif MAP_NAMES[selected_map] == "BLOCKS":

        snake = [
            (15, 15),
            (14, 15),
            (13, 15),
            (12, 15)
        ]

        direction = (1, 0)

    else:

        snake = [
            (15, 15),
            (14, 15),
            (13, 15),
            (12, 15)
        ]

        direction = (1, 0)


    if any(
        position in obstacles
        for position in snake
    ):

        found_spawn = False

        for y in range(GRID_HEIGHT):

            for x in range(GRID_WIDTH):

                candidate = [
                    (
                        x % GRID_WIDTH,
                        y % GRID_HEIGHT
                    ),

                    (
                        (x - 1) % GRID_WIDTH,
                        y % GRID_HEIGHT
                    ),

                    (
                        (x - 2) % GRID_WIDTH,
                        y % GRID_HEIGHT
                    ),

                    (
                        (x - 3) % GRID_WIDTH,
                        y % GRID_HEIGHT
                    )
                ]

                if all(
                    position not in obstacles
                    for position in candidate
                ):

                    snake = candidate

                    direction = (1, 0)

                    found_spawn = True

                    break

            if found_spawn:
                break


    apple = spawn_apple()


    update_move_timer()



def is_opposite_direction(current, new):
    """Return True if new direction is backwards."""

    return (
        current[0] == -new[0]
        and
        current[1] == -new[1]
    )


def change_direction(new_direction):
    """Change direction unless it is a 180-degree turn."""

    global direction

    if is_opposite_direction(
        direction,
        new_direction
    ):
        return

    direction = new_direction



def trigger_game_over():
    """Trigger game over and screen shake."""

    global game_over
    global shake_timer

    game_over = True

    stop_move_timer()

    shake_timer = 22

def update_game():
    """Update snake movement and collisions."""

    global snake
    global apple
    global score
    global high_score
    global new_high_score

    if game_over:
        return

    if paused:
        return


    head_x, head_y = snake[0]

    dx, dy = direction

    new_x = head_x + dx
    new_y = head_y + dy


    new_x %= GRID_WIDTH
    new_y %= GRID_HEIGHT

    new_head = (
        new_x,
        new_y
    )

    if new_head in obstacles:

        trigger_game_over()

        return


    eating_apple = (
        new_head == apple
    )

    if eating_apple:

        collision_body = snake

    else:

        collision_body = snake[:-1]

    if new_head in collision_body:

        trigger_game_over()

        return

    snake.insert(
        0,
        new_head
    )


    if eating_apple:

        score += 1

        if score > high_score:

            high_score = score

            new_high_score = True

            save_high_score(
                high_score
            )

        apple = spawn_apple()

        update_move_timer()

    else:

        snake.pop()


def get_shake_offset():
    """Return screen shake offset."""

    if shake_timer <= 0:

        return 0, 0

    strength = 6

    return (
        random.randint(
            -strength,
            strength
        ),

        random.randint(
            -strength,
            strength
        )
    )



def draw_grid(
    offset_x=0,
    offset_y=0
):
    """Draw background grid."""

    for x in range(
        0,
        SCREEN_WIDTH + CELL_SIZE,
        CELL_SIZE
    ):

        pygame.draw.line(
            screen,
            GRID_COLOR,
            (
                x + offset_x,
                offset_y
            ),
            (
                x + offset_x,
                SCREEN_HEIGHT + offset_y
            )
        )

    for y in range(
        0,
        SCREEN_HEIGHT + CELL_SIZE,
        CELL_SIZE
    ):

        pygame.draw.line(
            screen,
            GRID_COLOR,
            (
                offset_x,
                y + offset_y
            ),
            (
                SCREEN_WIDTH + offset_x,
                y + offset_y
            )
        )


def draw_obstacles(
    offset_x=0,
    offset_y=0
):
    """Draw map obstacles."""

    for x, y in obstacles:

        rect = pygame.Rect(
            x * CELL_SIZE
            + 1
            + offset_x,

            y * CELL_SIZE
            + 1
            + offset_y,

            CELL_SIZE - 2,
            CELL_SIZE - 2
        )

        pygame.draw.rect(
            screen,
            OBSTACLE,
            rect,
            border_radius=5
        )

        pygame.draw.rect(
            screen,
            OBSTACLE_BORDER,
            rect,
            1,
            border_radius=5
        )



def draw_apple(
    offset_x=0,
    offset_y=0
):
    """Draw apple."""

    if apple is None:

        return

    x, y = apple

    center_x = (
        x * CELL_SIZE
        + CELL_SIZE // 2
        + offset_x
    )

    center_y = (
        y * CELL_SIZE
        + CELL_SIZE // 2
        + offset_y
    )

    pygame.draw.circle(
        screen,
        APPLE_RED,
        (
            center_x,
            center_y + 2
        ),
        7
    )

    pygame.draw.arc(
        screen,
        APPLE_DARK,
        (
            center_x - 7,
            center_y - 5,
            14,
            15
        ),
        0,
        3.14,
        2
    )

    pygame.draw.circle(
        screen,
        APPLE_LIGHT,
        (
            center_x - 3,
            center_y - 1
        ),
        2
    )

    pygame.draw.line(
        screen,
        (100, 60, 30),
        (
            center_x,
            center_y - 5
        ),
        (
            center_x + 2,
            center_y - 10
        ),
        2
    )

    pygame.draw.ellipse(
        screen,
        (50, 175, 70),
        (
            center_x + 1,
            center_y - 12,
            7,
            4
        )
    )



def draw_snake(
    offset_x=0,
    offset_y=0
):
    """Draw improved snake."""

    if not snake:

        return


    for index, (x, y) in enumerate(
        snake
    ):

        rect = pygame.Rect(
            x * CELL_SIZE
            + 2
            + offset_x,

            y * CELL_SIZE
            + 2
            + offset_y,

            CELL_SIZE - 4,
            CELL_SIZE - 4
        )

        if index == 0:

            color = GREEN_HEAD

        elif index >= len(snake) - 2:

            color = GREEN_TAIL

        else:

            color = GREEN_BODY

        pygame.draw.rect(
            screen,
            color,
            rect,
            border_radius=6
        )

    head_x, head_y = snake[0]

    base_x = (
        head_x * CELL_SIZE
        + offset_x
    )

    base_y = (
        head_y * CELL_SIZE
        + offset_y
    )

    if direction == (1, 0):

        eyes = [
            (base_x + 14, base_y + 6),
            (base_x + 14, base_y + 14)
        ]

    elif direction == (-1, 0):

        eyes = [
            (base_x + 6, base_y + 6),
            (base_x + 6, base_y + 14)
        ]

    elif direction == (0, -1):

        eyes = [
            (base_x + 6, base_y + 6),
            (base_x + 14, base_y + 6)
        ]

    else:

        eyes = [
            (base_x + 6, base_y + 14),
            (base_x + 14, base_y + 14)
        ]

    for eye_x, eye_y in eyes:

        pygame.draw.circle(
            screen,
            WHITE,
            (
                eye_x,
                eye_y
            ),
            3
        )

        pygame.draw.circle(
            screen,
            (15, 15, 15),
            (
                eye_x,
                eye_y
            ),
            1
        )


def draw_score():
    """Draw score and game information."""

    score_text = FONT.render(
        f"Score: {score}",
        True,
        WHITE
    )

    best_text = SMALL_FONT.render(
        f"Best: {high_score}",
        True,
        GRAY
    )

    difficulty_text = SMALL_FONT.render(
        DIFFICULTY_NAMES[selected_difficulty],
        True,
        GRAY
    )

    map_text = SMALL_FONT.render(
        f"Map: {MAP_NAMES[selected_map]}",
        True,
        GRAY
    )

    screen.blit(
        score_text,
        (10, 7)
    )

    screen.blit(
        best_text,
        (10, 37)
    )

    screen.blit(
        difficulty_text,
        (
            SCREEN_WIDTH
            - difficulty_text.get_width()
            - 10,
            8
        )
    )

    screen.blit(
        map_text,
        (
            SCREEN_WIDTH
            - map_text.get_width()
            - 10,
            32
        )
    )



def draw_pause():
    """Draw pause overlay."""

    overlay = pygame.Surface(
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 175)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title = BIG_FONT.render(
        "PAUSED",
        True,
        WHITE
    )

    rect = title.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 25
        )
    )

    screen.blit(
        title,
        rect
    )

    text = SMALL_FONT.render(
        "P = Resume     M = Main Menu     ESC = Quit",
        True,
        GRAY
    )

    rect = text.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 30
        )
    )

    screen.blit(
        text,
        rect
    )

def draw_game_over():
    """Draw Game Over screen."""

    overlay = pygame.Surface(
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 190)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title = BIG_FONT.render(
        "GAME OVER",
        True,
        RED
    )

    rect = title.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 85
        )
    )

    screen.blit(
        title,
        rect
    )

    score_text = FONT.render(
        f"Score: {score}",
        True,
        WHITE
    )

    rect = score_text.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 25
        )
    )

    screen.blit(
        score_text,
        rect
    )

    if new_high_score:

        best_text = SMALL_FONT.render(
            "NEW HIGH SCORE!",
            True,
            YELLOW
        )

        rect = best_text.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 10
            )
        )

        screen.blit(
            best_text,
            rect
        )

        instruction_y = (
            SCREEN_HEIGHT // 2 + 65
        )

    else:

        instruction_y = (
            SCREEN_HEIGHT // 2 + 30
        )

    instruction = SMALL_FONT.render(
        "R = Restart    M = Menu    ESC = Quit",
        True,
        GRAY
    )

    rect = instruction.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            instruction_y
        )
    )

    screen.blit(
        instruction,
        rect
    )


def draw_quit_confirmation():
    """Draw quit confirmation."""

    overlay = pygame.Surface(
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 195)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    width = 450
    height = 180

    dialog = pygame.Rect(
        (
            (SCREEN_WIDTH - width) // 2,
            (SCREEN_HEIGHT - height) // 2,
            width,
            height
        )
    )

    pygame.draw.rect(
        screen,
        PANEL,
        dialog,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        PANEL_BORDER,
        dialog,
        2,
        border_radius=12
    )

    title = FONT.render(
        "Are you sure you want to quit?",
        True,
        WHITE
    )

    rect = title.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 25
        )
    )

    screen.blit(
        title,
        rect
    )

    instruction = SMALL_FONT.render(
        "Y / ENTER = Yes     N / ESC = No",
        True,
        GRAY
    )

    rect = instruction.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 25
        )
    )

    screen.blit(
        instruction,
        rect
    )


def draw_menu_confirmation():
    """Draw main menu confirmation."""

    overlay = pygame.Surface(
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 195)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    width = 450
    height = 180

    dialog = pygame.Rect(
        (
            (SCREEN_WIDTH - width) // 2,
            (SCREEN_HEIGHT - height) // 2,
            width,
            height
        )
    )

    pygame.draw.rect(
        screen,
        PANEL,
        dialog,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        PANEL_BORDER,
        dialog,
        2,
        border_radius=12
    )

    title = FONT.render(
        "Return to Main Menu?",
        True,
        WHITE
    )

    rect = title.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 25
        )
    )

    screen.blit(
        title,
        rect
    )

    instruction = SMALL_FONT.render(
        "Y / ENTER = Yes     N / ESC = No",
        True,
        GRAY
    )

    rect = instruction.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 25
        )
    )

    screen.blit(
        instruction,
        rect
    )


def draw_menu_title(text):
    """Draw menu title."""

    title = BIG_FONT.render(
        text,
        True,
        GREEN_HEAD
    )

    rect = title.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            120
        )
    )

    screen.blit(
        title,
        rect
    )


def draw_menu_option(
    text,
    y,
    selected
):
    """Draw menu item."""

    if selected:

        color = MENU_GREEN

        prefix = "▶ "

    else:

        color = WHITE

        prefix = "  "

    rendered = FONT.render(
        prefix + text,
        True,
        color
    )

    rect = rendered.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            y
        )
    )

    screen.blit(
        rendered,
        rect
    )


def draw_main_menu():
    """Draw main menu."""

    screen.fill(
        BACKGROUND
    )

    pygame.draw.circle(
        screen,
        GREEN_HEAD,
        (
            SCREEN_WIDTH // 2,
            55
        ),
        21
    )

    pygame.draw.circle(
        screen,
        GREEN_BODY,
        (
            SCREEN_WIDTH // 2 - 33,
            55
        ),
        18
    )

    pygame.draw.circle(
        screen,
        GREEN_BODY,
        (
            SCREEN_WIDTH // 2 - 63,
            55
        ),
        15
    )

    title = TITLE_FONT.render(
        "SNAKE",
        True,
        GREEN_HEAD
    )

    rect = title.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            150
        )
    )

    screen.blit(
        title,
        rect
    )

    items = [
        "PLAY",
        "DIFFICULTY",
        "MAP",
        "HIGH SCORE",
        "QUIT"
    ]

    for index, item in enumerate(
        items
    ):

        draw_menu_option(
            item,
            255 + index * 48,
            index == menu_selection
        )

    instruction = SMALL_FONT.render(
        "↑ ↓ Select     ENTER Confirm     ESC Quit",
        True,
        GRAY
    )

    rect = instruction.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            545
        )
    )

    screen.blit(
        instruction,
        rect
    )


def draw_difficulty_menu():
    """Draw difficulty selection."""

    screen.fill(
        BACKGROUND
    )

    draw_menu_title(
        "DIFFICULTY"
    )

    descriptions = [
        "Relaxed speed",
        "Balanced challenge",
        "Fast and difficult"
    ]

    for index, name in enumerate(
        DIFFICULTY_NAMES
    ):

        y = 230 + index * 80

        draw_menu_option(
            name,
            y,
            index == selected_difficulty
        )

        description = SMALL_FONT.render(
            f"{descriptions[index]} | "
            f"{DIFFICULTIES[name]} moves/sec",
            True,
            GRAY
        )

        rect = description.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                y + 28
            )
        )

        screen.blit(
            description,
            rect
        )

    instruction = SMALL_FONT.render(
        "↑ ↓ Select     ENTER Confirm     ESC Back",
        True,
        GRAY
    )

    rect = instruction.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            540
        )
    )

    screen.blit(
        instruction,
        rect
    )


def draw_map_menu():
    """Draw map selection."""

    screen.fill(
        BACKGROUND
    )

    draw_menu_title(
        "SELECT MAP"
    )

    descriptions = [
        "No obstacles",
        "Four obstacle blocks",
        "Four islands with a center obstacle"
    ]

    for index, name in enumerate(
        MAP_NAMES
    ):

        y = 220 + index * 90

        draw_menu_option(
            name,
            y,
            index == selected_map
        )

        description = SMALL_FONT.render(
            descriptions[index],
            True,
            GRAY
        )

        rect = description.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                y + 30
            )
        )

        screen.blit(
            description,
            rect
        )

    instruction = SMALL_FONT.render(
        "↑ ↓ Select     ENTER Confirm     ESC Back",
        True,
        GRAY
    )

    rect = instruction.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            540
        )
    )

    screen.blit(
        instruction,
        rect
    )


def draw_high_score_menu():
    """Draw high score screen."""

    screen.fill(
        BACKGROUND
    )

    title = BIG_FONT.render(
        "HIGH SCORE",
        True,
        YELLOW
    )

    rect = title.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            150
        )
    )

    screen.blit(
        title,
        rect
    )

    score_text = TITLE_FONT.render(
        str(high_score),
        True,
        WHITE
    )

    rect = score_text.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            280
        )
    )

    screen.blit(
        score_text,
        rect
    )

    instruction = SMALL_FONT.render(
        "Press ESC to return",
        True,
        GRAY
    )

    rect = instruction.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            510
        )
    )

    screen.blit(
        instruction,
        rect
    )


def handle_menu_event(event):
    """Handle main menu."""

    global menu_selection
    global game_state

    if event.key == pygame.K_UP:

        menu_selection = (
            menu_selection - 1
        ) % 5

    elif event.key == pygame.K_DOWN:

        menu_selection = (
            menu_selection + 1
        ) % 5

    elif event.key == pygame.K_RETURN:

        if menu_selection == 0:

            reset_game()

            game_state = PLAYING

        elif menu_selection == 1:

            game_state = DIFFICULTY_MENU

        elif menu_selection == 2:

            game_state = MAP_MENU

        elif menu_selection == 3:

            game_state = HIGH_SCORE_MENU

        elif menu_selection == 4:

            pygame.quit()
            sys.exit()

    elif event.key == pygame.K_ESCAPE:

        pygame.quit()
        sys.exit()


def handle_difficulty_event(event):
    """Handle difficulty selection."""

    global selected_difficulty
    global game_state

    if event.key == pygame.K_UP:

        selected_difficulty = (
            selected_difficulty - 1
        ) % len(DIFFICULTY_NAMES)

    elif event.key == pygame.K_DOWN:

        selected_difficulty = (
            selected_difficulty + 1
        ) % len(DIFFICULTY_NAMES)

    elif event.key == pygame.K_RETURN:

        game_state = MENU

    elif event.key == pygame.K_ESCAPE:

        game_state = MENU


def handle_map_event(event):
    """Handle map selection."""

    global selected_map
    global game_state

    if event.key == pygame.K_UP:

        selected_map = (
            selected_map - 1
        ) % len(MAP_NAMES)

    elif event.key == pygame.K_DOWN:

        selected_map = (
            selected_map + 1
        ) % len(MAP_NAMES)

    elif event.key == pygame.K_RETURN:

        game_state = MENU

    elif event.key == pygame.K_ESCAPE:

        game_state = MENU

def handle_high_score_event(event):
    """Handle high score screen."""

    global game_state

    if event.key == pygame.K_ESCAPE:

        game_state = MENU


def handle_game_event(event):
    """Handle gameplay input."""

    global paused
    global confirm_quit
    global confirm_menu
    global game_state

    if game_over:

        if event.key == pygame.K_r:

            reset_game()
        elif event.key == pygame.K_m:

            stop_move_timer()

            confirm_quit = False
            confirm_menu = False

            game_state = MENU

        elif event.key == pygame.K_ESCAPE:

            pygame.quit()
            sys.exit()

        return

    if confirm_quit:

        if event.key in (
            pygame.K_y,
            pygame.K_RETURN
        ):

            pygame.quit()
            sys.exit()

        elif event.key in (
            pygame.K_n,
            pygame.K_ESCAPE
        ):

            confirm_quit = False

        return

    if confirm_menu:

        if event.key in (
            pygame.K_y,
            pygame.K_RETURN
        ):

            stop_move_timer()

            confirm_menu = False
            confirm_quit = False

            game_state = MENU

        elif event.key in (
            pygame.K_n,
            pygame.K_ESCAPE
        ):

            confirm_menu = False

        return

    if event.key == pygame.K_ESCAPE:

        confirm_quit = True

        return

    if event.key == pygame.K_m:

        confirm_menu = True

        return

    if event.key == pygame.K_p:

        paused = not paused

        if paused:

            stop_move_timer()

        else:

            update_move_timer()

        return

    if paused:

        return

    if event.key in (
        pygame.K_UP,
        pygame.K_w
    ):

        change_direction(
            (0, -1)
        )

    elif event.key in (
        pygame.K_DOWN,
        pygame.K_s
    ):

        change_direction(
            (0, 1)
        )

    elif event.key in (
        pygame.K_LEFT,
        pygame.K_a
    ):

        change_direction(
            (-1, 0)
        )

    elif event.key in (
        pygame.K_RIGHT,
        pygame.K_d
    ):

        change_direction(
            (1, 0)
        )

def draw_game():
    """Draw the complete game."""

    offset_x, offset_y = get_shake_offset()

    screen.fill(
        BACKGROUND
    )

    draw_grid(
        offset_x,
        offset_y
    )

    draw_obstacles(
        offset_x,
        offset_y
    )

    draw_apple(
        offset_x,
        offset_y
    )

    draw_snake(
        offset_x,
        offset_y
    )

    draw_score()

    if paused and not game_over:

        draw_pause()
    if game_over:

        draw_game_over()
    if confirm_quit:

        draw_quit_confirmation()

    if confirm_menu:

        draw_menu_confirmation()

reset_game()
stop_move_timer()


running = True

while running:

    if shake_timer > 0:

        shake_timer -= 1

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False
        elif event.type == pygame.KEYDOWN:

            if game_state == MENU:

                handle_menu_event(
                    event
                )

            elif game_state == DIFFICULTY_MENU:

                handle_difficulty_event(
                    event
                )

            elif game_state == MAP_MENU:

                handle_map_event(
                    event
                )

            elif game_state == HIGH_SCORE_MENU:

                handle_high_score_event(
                    event
                )

            elif game_state == PLAYING:

                handle_game_event(
                    event
                )

        elif (
            event.type == MOVE_EVENT
            and game_state == PLAYING
            and not game_over
            and not paused
            and not confirm_quit
            and not confirm_menu
        ):

            update_game()

    if game_state == MENU:

        draw_main_menu()

    elif game_state == DIFFICULTY_MENU:

        draw_difficulty_menu()

    elif game_state == MAP_MENU:

        draw_map_menu()

    elif game_state == HIGH_SCORE_MENU:

        draw_high_score_menu()

    elif game_state == PLAYING:

        draw_game()

    pygame.display.flip()

    clock.tick(FPS)

stop_move_timer()

pygame.quit()

sys.exit()

