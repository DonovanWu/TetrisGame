import sys, termios, select
import time, argparse


# This just serves as an interface
class Game:
    framecount = 0
    gamestate = None

    # called when game is initialized
    def start(self):
        pass

    # called every frame
    def update(self):
        pass

    # called when game exits
    def end(self):
        pass

    # how to present your game state to player
    def draw(self):
        pass

    # get player input
    def get_input(self):
        pass

    def is_closed(self):
        return False

    def is_gameover(self):
        return False


# Some basic setups for you to work with
class TerminalWASDInputGame(Game):
    virtual_gamepad = {
        'w': 'up',
        'a': 'left',
        's': 'down',
        'd': 'right',
        '[A': 'up',     # arrow keys remap
        '[B': 'down',   # arrow keys remap
        '[C': 'right',  # arrow keys remap
        '[D': 'left',   # arrow keys remap
        'z': 'A',
        'x': 'B',
        'j': 'A',
        'k': 'B',
        'q': 'quit'
    }

    def start(self):
        self.framecount = 0
        self.button_pressed = None

        # non echo terminal mode
        fd = sys.stdin.fileno()
        self.old_attr = termios.tcgetattr(fd)
        self.new_attr = termios.tcgetattr(fd)
        self.new_attr[3] &= ~(termios.ICANON | termios.ECHO)  # lflags
        termios.tcsetattr(fd, termios.TCSANOW, self.new_attr)

    def update(self):
        self.button_pressed = self.get_input()
        self.framecount += 1

    def end(self):
        # restore previous terminal settings
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, self.old_attr)

    def draw(self):
        if self.button_pressed is not None:
            print('You pressed: %s' % self.button_pressed)

    def get_input(self):
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            user_input = sys.stdin.read(1).lower()
            if user_input == '\x1b':
                # arrow keys
                user_input = sys.stdin.read(2)
            if user_input in self.virtual_gamepad:
                return self.virtual_gamepad[user_input]
            else:
                return None
        else:
            return None

    def is_closed(self):
        return self.button_pressed == 'quit'


if __name__ == '__main__':
    from tetris import Tetris
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--fps', action='store', default=30, required=False,
                        help='Frames per second: number or string literal "inf"')
    args = parser.parse_args()

    if args.fps == 'inf':
        frame_length = 0
    else:
        frame_length = 1 / float(args.fps)

    game = Tetris()

    game.start()
    while not game.is_closed():
        frame_start = time.time()
        game.update()
        game.draw()
        frame_duration_sec = time.time() - frame_start
        sleep_duration_sec = max(0.0, frame_length - frame_duration_sec)
        time.sleep(sleep_duration_sec)
    game.end()
