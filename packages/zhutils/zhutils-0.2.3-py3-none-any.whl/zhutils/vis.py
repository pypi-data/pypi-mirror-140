from .lib import *


def log_init(filename="example.log", show=True, file=True, level=logging.INFO):
    assert show or file, "must choose at least one"
    handlers = []
    if show:
        handlers.append(logging.StreamHandler())
    if file:
        handlers.append(logging.FileHandler(filename))
    logging.basicConfig(format='[%(asctime)s] (%(levelname)s) %(message)s',
                        level=level,
                        handlers=handlers)


def get_new_name(x, y="crop"):
    _, ext = os.path.splitext(x)
    return x.replace(ext, "_" + y + ext)


def get_new_extension(x, y=".png"):
    x, _ = os.path.splitext(x)
    return x + y


class AdaptiveAxes:
    def __init__(self,
                 n_figure: int,
                 n_col: int = 4,
                 fig_size: tuple = (7, 5)) -> None:
        self.n = n_figure
        self.n_col = min(n_figure, n_col)
        self.n_row = (n_figure + n_col - 1) // n_col
        self.fig_size = (fig_size[0] * self.n_col, fig_size[1] * self.n_row)
        self.fig, self.axes = plt.subplots(self.n_row,
                                           self.n_col,
                                           squeeze=False,
                                           figsize=self.fig_size)

    def __iter__(self):
        for i in range(self.n):
            j = i // self.n_col
            k = i % self.n_col
            yield self.axes[j][k]
