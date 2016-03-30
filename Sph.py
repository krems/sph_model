Y_SIZE = 480.
X_SIZE = 640.
import sfml as sf
from math import pi, sqrt


dt = 0.1
h = 50.
rest_dist = 1.5
mu_visc = 0.05
gravity = 5.


class Particle(sf.CircleShape):
    m = 1.
    x = 0.
    y = 0.
    vx = 0.
    vy = 0.
    rho = 1.
    press_x = 0.
    press_y = 0.
    force = 0.

    def set_params(self, x, y, vx, vy, press_x, press_y, rho):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.press_x = press_x
        self.press_y = press_y
        self.rho = rho


def _distance(lhs, rhs):
    return (lhs.x - rhs.x) ** 2 + (lhs.y - rhs.y) ** 2


def _w_rho(subj, neighbour):
    dist = _distance(subj, neighbour)
    if dist >= h ** 2:
        return 0.
    return 315. / (64. * pi * (h ** 9)) * (h ** 2 - dist) ** 3


def _w_pressure(subj, neighbour):
    dist = _distance(subj, neighbour)
    if dist >= h ** 2 or dist == 0:
        return 0., 0.
    mul = 15. / (pi * h ** 6) * (h - sqrt(dist)) ** 3
    return mul * (subj.x - neighbour.x), mul * (subj.y - neighbour.y)


def _dw_pressure(subj, neighbour):
    dist = _distance(subj, neighbour)
    if dist >= h ** 2 or dist == 0:
        return 0., 0.
    mul = -15. * 3. / (pi * h ** 6) * (h - sqrt(dist)) ** 2 / sqrt(dist)
    return mul * (subj.x - neighbour.x), mul * (subj.y - neighbour.y)


def _ddw_visc(subj, neighbour):
    dist = _distance(subj, neighbour)
    if dist >= h ** 2:
        return 0.
    return 45. / (pi * h ** 6) * (h - sqrt(dist))


def xwall_pressure(subj):
    if subj.x < rest_dist:
        return subj.m * (rest_dist - subj.x) / dt ** 2
    if X_SIZE - subj.x < rest_dist:
        return - subj.m * (rest_dist - (X_SIZE - subj.x)) / dt ** 2
    return 0.

def ywall_pressure(subj):
    if subj.y < rest_dist:
        return subj.m * (rest_dist - subj.y) / dt ** 2
    if Y_SIZE - subj.y < rest_dist:
        return - subj.m * (rest_dist - (Y_SIZE - subj.y)) / dt ** 2
    return 0.


def compute_next_state(particles):
    result = []
    for subj in particles:
        rho = subj.rho
        dp_x = 0.
        dp_y = 0.
        visc_x = 0.
        visc_y = 0.
        ext_forces_x = 0. + xwall_pressure(subj)
        ext_forces_y = - gravity + ywall_pressure(subj)
        pressure_x = 0.
        pressure_y = 0.
        for n in particles:
            if _distance(subj, n) < h and n != subj:
                rho += n.m * _w_rho(subj, n)

                dpress_ker_x, dpress_ker_y = _dw_pressure(subj, n)
                dp_x += dpress_ker_x * n.m * (subj.press_x + n.press_x) / (2. * n.rho)
                dp_y += dpress_ker_y * n.m * (subj.press_y + n.press_y) / (2. * n.rho)

                dd_visc_ker = _ddw_visc(subj, n)
                visc_x += n.m * (n.vx - subj.vx) / n.rho * dd_visc_ker
                visc_y += n.m * (n.vy - subj.vy) / n.rho * dd_visc_ker

                ker_x, ker_y = _w_pressure(subj, n)
                pressure_x += ker_x * n.m * (subj.press_x + n.press_x) / (2. * n.rho)
                pressure_y += ker_y * n.m * (subj.press_y + n.press_y) / (2. * n.rho)
        visc_x *= mu_visc
        visc_y *= mu_visc

        acceleration_x = (-dp_x + visc_x + ext_forces_x) / rho
        acceleration_y = (-dp_y + visc_y + ext_forces_y) / rho
        nvx = subj.vx + acceleration_x * dt
        nvy = subj.vy + acceleration_y * dt
        nx = subj.x + dt * (nvx + dt / 2. * acceleration_x)
        ny = subj.y + dt * (nvy + dt / 2. * acceleration_y)

        new = Particle()
        new.set_params(nx, ny, nvx, nvy, pressure_x, pressure_y, rho)
        result.append(new)
    return result
