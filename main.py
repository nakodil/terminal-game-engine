import keyboard  # pip install keyboard
import time
import os
import config  # локальный
import assets  # локальный


class App:
    '''Программа'''
    def __init__(self) -> None:
        self.fps = config.FPS
        self.update_delay = 1 / self.fps
        self.last_update_time = 0
        keyboard.on_press(self.handle_keys)  # хук на все клавиши
        self.key_pressed = None
        self.screen = Screen(config.WIDTH, config.HEIGHT, config.CELL_SIZE)
        self.is_running = True
        self.run()

    def run(self) -> None:
        '''Главный цикл программы'''
        self.game = Game(self.screen)
        self.game.start()
        self.screen.clear()
        self.draw()  # при низких FPS видна задержка кадра, рисуем первый сразу
        while self.is_running:
            if time.time() - self.last_update_time < self.update_delay:
                continue
            self.update()
            self.last_update_time = time.time()
            self.draw()
        print('Конец программы')

    def update(self) -> None:
        if self.key_pressed:
            self.game.player.handle_keys(self.key_pressed)
        self.key_pressed = None  # отжимаем нажатую клавишу
        self.game.update()

    def draw(self) -> None:
        self.screen.draw()

    def handle_keys(self, event: keyboard.KeyboardEvent) -> None:
        '''Обработка нажатий клвиш, рабатывает по событию'''
        if event.event_type == 'down':
            self.key_pressed = event.name
            if self.key_pressed == config.KEY_QUIT:
                self.is_running = False


class Cell:
    '''
    Клетка экрана
    TODO: цвета
    '''
    def __init__(self, x: int, y: int, size: int, image: str) -> None:
        self.x = x
        self.y = y
        self.size = size
        self.image = image

    def __str__(self) -> str:
        return f'{self.x},{self.y}'


class Screen:
    '''
    Экран из клеток:
    отсчет клеток начинается с 1 по x и 1 по y,
    клетки хранятся в словаре self.cells как {(x, y): Cell()}
    '''
    def __init__(self, width: int, height: int, cell_size: int) -> None:
        # габариты
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2

        # клетки
        self.cell_size = cell_size
        self.cells = None
        self.buffered = None
        self.make_cells()

    def make_cells(self) -> None:
        '''Создает все клетки экрана'''
        self.cells = dict()
        for x in range(1, self.width + 1):
            for y in range(1, self.height + 1):
                self.cells[(x, y)] = Cell(x, y, self.cell_size, assets.EMPTY)

    def get_cell(self, x: int, y: int) -> Cell:
        '''Возвращает клетку в координатах x y'''
        return self.cells[(x, y)]

    def bufferise(self) -> None:
        '''
        Буферизирует изображения всех клеток экрана в строку
        Добавляет декоративную рамку вокруг экрана
        '''
        frame_top = '┌' + '─' * (self.width * self.cell_size) + '┐'
        frame_bottom = '└' + '─' * (self.width * self.cell_size) + '┘'

        buffer = ''
        buffer += frame_top + '\n'
        for y in range(1, self.height + 1):
            for i in range(self.cell_size):
                row = ''
                for x in range(1, self.width + 1):
                    cell = self.get_cell(x, y)
                    row += cell.image[i]
                buffer += '│' + row + '│' + '\n'
        buffer += frame_bottom
        self.buffered = buffer

    def move_cursor_to(self, x, y) -> None:
        '''Перемещает курсор в координаты'''
        print(f'\033[{x};{y}H', end='')

    def draw(self) -> None:
        '''
        Возвращает курсор в верхний левый угол консоли
        и оттуда выводит на экран буфферизированную строку
        из всех изображенйи клеток
        '''
        self.move_cursor_to(0, 0)
        print(self.buffered)
        self.bufferise()

    def clear(self) -> None:
        '''Очищает терминал в Windows'''
        os.system('cls')


class Player:
    '''
    Игрок
    TODO: цвета
    '''
    def __init__(
            self,
            screen: Screen = None,
            x: int = 1,
            y: int = 1,
            color: str = config.GREEN,
            image: list = assets.PLAYER,
            key_up: str = 'up',
            key_down: str = 'down',
            key_left: str = 'left',
            key_right: str = 'right'
    ) -> None:
        self.screen = screen
        self.x = x
        self.y = y
        self.image = image
        self.key_up = key_up
        self.key_down = key_down
        self.key_left = key_left
        self.key_right = key_right
        self.keys = (self.key_up, self.key_down, self.key_left, self.key_right)
        self.move(0, 0)  # игрок рисуется в первый раз без нажатия клавиш

    def handle_keys(self, key: str) -> None:
        '''Реакция игрока на клавиши управления'''
        if key not in self.keys:
            return
        if key == self.key_up:
            self.move(0, -1)
        if key == self.key_down:
            self.move(0, 1)
        if key == self.key_left:
            self.move(-1, 0)
        if key == self.key_right:
            self.move(1, 0)

    def move(self, dx: int, dy: int) -> None:
        '''Двигает игрока в границах экрана'''
        if self.x + dx > self.screen.width:
            return
        if self.x + dx < 1:
            return
        if self.y + dy > self.screen.height:
            return
        if self.y + dy < 1:
            return

        # TODO: в метод
        old_cell = self.screen.get_cell(self.x, self.y)
        new_cell = self.screen.get_cell(self.x + dx, self.y + dy)
        old_cell.image = assets.EMPTY
        new_cell.image = self.image
        self.x += dx
        self.y += dy


class Game:
    '''Игра'''
    def __init__(self, screen: Screen) -> None:
        self.screen = screen
        self.player = None

    def start(self) -> None:
        self.player = Player(
            screen=self.screen,
            x=self.screen.center_x,
            y=self.screen.center_y,
        )

    def update(self) -> None:
        '''Логика игры'''
        pass


if __name__ == '__main__':
    App()
