import functools
import sfml as sf
from math import pi, sqrt, exp
from time import time

BOUND_X = 130.
BOUND_Y = 20.
Y_SIZE = 480. - BOUND_Y
X_SIZE = 640. - BOUND_X
dt = 0.1
h = 100.
rest_dist = 1.5
rest_press = 10.
gas_const = 8.344 * 300 * 10**8
mu_visc = .05
gravity = 10.

max_rho = 10 ** -5


class Particle(sf.CircleShape):
    m = 1.
    x = 0.
    y = 0.
    vx = 0.
    vy = 0.
    rho = 0.
    dpx = 0.
    dpy = 0.

    def set_params(self, x, y, vx, vy, rho):
        global max_rho
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.rho = rho
        if rho - 1 > max_rho:
            max_rho = rho - 1
        self.fill_color = sf.Color(100, 70, 30 + round((rho - 1) / max_rho * 225))

    def set_pressure(self, dp_x, dp_y):
        self.dpx = -dp_x
        self.dpy = -dp_y


class GaussKernels:
    @staticmethod
    def _ker(subj, n):
        dist_q = _distance_q(subj, n)
        if dist_q >= h ** 2:
            return 0.
        return 1. / (pi**1.5 * h**3) * exp(-dist_q / h**2)

    @staticmethod
    def _dker(subj, n):
        dist_q = _distance_q(subj, n)
        if dist_q >= h ** 2:
            return 0.
        mul = -2. / (pi ** 1.5 * h ** 5) * exp(-dist_q / h ** 2)
        return mul * (subj.x - n.x), mul * (subj.y - n.y)

    @staticmethod
    def w_rho(subj, neighbour):
        return GaussKernels._ker(subj, neighbour)

    @staticmethod
    def w_pressure(subj, neighbour):
        return GaussKernels._ker(subj, neighbour)

    @staticmethod
    def dw_pressure(subj, neighbour):
        return GaussKernels._dker(subj, neighbour)

    @staticmethod
    def ddw_visc(subj, neighbour):
        return GaussKernels._ker(subj, neighbour)


class KernelsSecond:
    @staticmethod
    def w_rho(subj, neighbour):
        dist_q = _distance_q(subj, neighbour)
        if dist_q >= h ** 2:
            return 0.
        return 315. / (64 * pi * h**2) * (h**2 - dist_q)**3

    @staticmethod
    def w_pressure(subj, neighbour):
        dist_q = _distance_q(subj, neighbour)
        if dist_q >= h ** 2:
            return 0.
        res = (45. * sqrt(dist_q) * (4. * h**3 - 6. * h**2 * sqrt(dist_q) + 4. * h * dist_q - dist_q**(3./2.))) / (4. * pi * h**6)
        return res

    @staticmethod
    def dw_pressure(subj, neighbour):
        dist_q = _distance_q(subj, neighbour)
        if dist_q >= h ** 2:
            return 0.
        mul = 45. / (pi * h ** 6) * (h - sqrt(dist_q)) ** 3
        return mul * (subj.x - neighbour.x) / dist_q, mul * (subj.y - neighbour.y) / dist_q

    @staticmethod
    def ddw_visc(subj, neighbour):
        dist_q = _distance_q(subj, neighbour)
        if dist_q >= h ** 2:
            return 0.
        return 45. / (pi * h**6) * (h - sqrt(dist_q))


class KernelsFirst:
    @staticmethod
    def w_rho(subj, neighbour):
        dist = _distance_q(subj, neighbour)
        if dist >= h ** 2:
            return 0.
        return 315. / (64. * pi * (h ** 9)) * (h ** 2 - dist) ** 3

    @staticmethod
    def w_pressure(subj, neighbour):
        dist = _distance_q(subj, neighbour)
        if dist >= h ** 2 or dist == 0:
            return 0., 0.
        mul = 15. / (pi * h ** 6) * (h - sqrt(dist)) ** 3
        return mul

    @staticmethod
    def dw_pressure(subj, neighbour):
        dist = _distance_q(subj, neighbour)
        if dist >= h ** 2 or dist == 0:
            return 0., 0.
        mul = -15. * 3. / (pi * h ** 6) * (h - sqrt(dist)) ** 2 / sqrt(dist)
        return mul * (subj.x - neighbour.x), mul * (subj.y - neighbour.y)

    @staticmethod
    def ddw_visc(subj, neighbour):
        dist = _distance_q(subj, neighbour)
        if dist >= h ** 2:
            return 0.
        return 45. / (pi * h ** 6) * (h - sqrt(dist))


def _distance_q(lhs, rhs):
    return (lhs.x - rhs.x) ** 2 + (lhs.y - rhs.y) ** 2

timeout = 10000
draw_low_prt = True

def enable_wall(func):
    timestamp = time()

    @functools.wraps(func)
    def inner(subj):
        X1_WALL = BOUND_X + 25
        X2_WALL = BOUND_X + 55
        Y_WALL = 20
        if X1_WALL - X2_WALL < X1_WALL - subj.x < rest_dist and (subj.y > BOUND_Y + Y_WALL or draw_low_prt):
            return -subj.m * (rest_dist - (X1_WALL - subj.x)) / dt ** 2
        if 0 < subj.x - X2_WALL < rest_dist and (subj.y > BOUND_Y + Y_WALL or draw_low_prt):
            return subj.m * (rest_dist - (subj.x - X2_WALL)) / dt ** 2
        return func(subj)
    return inner


def enable_wall_from_floor(func):
    @functools.wraps(func)
    def inner(subj):
        X1_WALL = BOUND_X + 25
        X2_WALL = BOUND_X + 55
        Y_WALL = 35
        if X1_WALL - X2_WALL < X1_WALL - subj.x < rest_dist and subj.y < BOUND_Y + Y_WALL:
            return -subj.m * (rest_dist - (X1_WALL - subj.x)) / dt ** 2
        if 0 < subj.x - X2_WALL < rest_dist and subj.y < BOUND_Y + Y_WALL:
            return subj.m * (rest_dist - (subj.x - X2_WALL)) / dt ** 2
        return func(subj)
    return inner


def enable_y_wall(func):
    @functools.wraps(func)
    def inner(subj):
        X1_WALL = BOUND_X + 25
        X2_WALL = BOUND_X + 55
        Y_WALL = 20
        if BOUND_Y + Y_WALL - subj.y < rest_dist and X2_WALL < subj.x < X1_WALL:
            return -subj.m * (rest_dist - (BOUND_Y + Y_WALL - subj.y)) / dt ** 2
        return func(subj)
    return inner


def enable_y_wall_from_floor(func):
    @functools.wraps(func)
    def inner(subj):
        X1_WALL = BOUND_X + 25
        X2_WALL = BOUND_X + 55
        Y_WALL = 35
        if subj.y - (BOUND_Y + Y_WALL) < rest_dist and X2_WALL < subj.x < X1_WALL:
            return subj.m * (rest_dist - (subj.y - BOUND_Y - Y_WALL)) / dt ** 2
        return func(subj)
    return inner


@enable_wall
def xwall_pressure(subj):
    if subj.x - BOUND_X < rest_dist:
        return subj.m * (rest_dist - (subj.x - BOUND_X)) / dt ** 2
    if X_SIZE - BOUND_X - subj.x < rest_dist:
        return - subj.m * (rest_dist - (X_SIZE - BOUND_X - subj.x)) / dt ** 2
    return 0.


@enable_y_wall
def ywall_pressure(subj):
    if subj.y - BOUND_Y < rest_dist:
        return subj.m * (rest_dist - (subj.y - BOUND_Y)) / dt ** 2
    if Y_SIZE - BOUND_Y - subj.y < rest_dist:
        return - subj.m * (rest_dist - (Y_SIZE - BOUND_Y - subj.y)) / dt ** 2
    return 0.


def compute_next_state(particles):
    result = []
    for subj in particles:
        rho = rest_rho
        dp_x = 0.
        dp_y = 0.
        visc_x = 0.
        visc_y = 0.
        ext_forces_x = xwall_pressure(subj)
        ext_forces_y = -gravity + ywall_pressure(subj)
        for n in particles:
            if _distance_q(subj, n) < h and n != subj:
                rho += n.m * KernelsFirst.w_rho(subj, n)

                subj_press = rest_press + gas_const * (subj.rho - rest_rho)
                n_press = rest_press + gas_const * (n.rho - rest_rho)
                common_pressure = n.m * (subj_press + n_press) / (2. * subj.rho)
                dpress_ker_x, dpress_ker_y = KernelsFirst.dw_pressure(subj, n)
                dp_x += dpress_ker_x * common_pressure
                dp_y += dpress_ker_y * common_pressure

                dd_visc_ker = KernelsFirst.ddw_visc(subj, n)
                visc_x += n.m * (n.vx - subj.vx) / n.rho * dd_visc_ker
                visc_y += n.m * (n.vy - subj.vy) / n.rho * dd_visc_ker
        visc_x *= mu_visc
        visc_y *= mu_visc

        acceleration_x = (-dp_x + visc_x + ext_forces_x) / rho
        acceleration_y = (-dp_y + visc_y + ext_forces_y) / rho
        nvx = subj.vx + acceleration_x * dt
        nvy = subj.vy + acceleration_y * dt
        nx = subj.x + dt * (nvx + dt / 2. * acceleration_x)
        ny = subj.y + dt * (nvy + dt / 2. * acceleration_y)

        new = Particle()
        new.set_params(nx, ny, nvx, nvy, rho)
        new.set_pressure(dp_x, dp_y)
        result.append(new)
    return result


def set_rest_rho(rho):
    global rest_rho
    rest_rho = rho


def add_low_wall(func):
    timestamp = time()

    @functools.wraps(func)
    def inner(window):
        import sfml as sf
        X1_WALL = BOUND_X + 25
        X2_WALL = BOUND_X + 55
        Y_WALL = 20
        if timeout + timestamp > time():
            rectangle = sf.RectangleShape((X2_WALL - X1_WALL, Y_WALL + 4))
            rectangle.position = (X_SIZE - X2_WALL, Y_SIZE - BOUND_Y - Y_WALL - 2)
            rectangle.fill_color = sf.Color.GREEN
            window.draw(rectangle)
        func(window)
    return inner


# @add_low_wall
def wall(window, draw_low_part):
    global draw_low_prt
    draw_low_prt = draw_low_part
    X1_WALL = BOUND_X + 25
    X2_WALL = BOUND_X + 55
    Y_WALL = 20
    rectangle = sf.RectangleShape((X2_WALL - X1_WALL, Y_SIZE - 2 * BOUND_Y - Y_WALL + 2))
    rectangle.position = (X_SIZE - X2_WALL, BOUND_Y - 2)
    rectangle.fill_color = sf.Color.GREEN
    window.draw(rectangle)
    if draw_low_part:
        rectangle = sf.RectangleShape((X2_WALL - X1_WALL, Y_WALL + 4))
        rectangle.position = (X_SIZE - X2_WALL, Y_SIZE - BOUND_Y - Y_WALL - 2)
        rectangle.fill_color = sf.Color.GREEN
        window.draw(rectangle)
