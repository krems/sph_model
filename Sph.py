__author__ = 'krm'
import sfml as sf
from math import pi, sqrt

dt = 0.1
h = 10.
k_press = .5
mu_visc = 0.05

class Particle(sf.CircleShape):
    m = 1.
    x = 0.
    y = 0.
    vx = 0.
    vy = 0.
    rho = 1.

    def set_params(self, x, y, vx, vy, rho):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.rho = rho


def _distance(lhs, rhs):
    return (lhs.x - rhs.x) ** 2 + (lhs.y - rhs.y) ** 2


def _w_rho(subj, neighbour):
    dist = _distance(subj, neighbour)
    if dist >= h ** 2:
        return 0.
    return 315. / (64. * pi * (h ** 9)) * (h ** 2 - dist) ** 3


def _dw_dpressure(subj, neighbour):
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


def _calc_rho(subj, neighbours):
    rho = 0.
    for n in neighbours:
        if _distance(subj, n) >= h or n == subj:
            continue
        rho += n.m * _w_rho(subj, n)
    if rho == 0:
        return subj.rho
    return rho


def _calc_dpressure(subj, neighbours, subj_rho):
    dp_x = 0.
    dp_y = 0.
    for n in neighbours:
        if _distance(subj, n) >= h or n == subj:
            continue
        ker_x, ker_y = _dw_dpressure(subj, n)
        mul = n.m * k_press * (subj_rho + n.rho) / (2. * n.rho)
        dp_x += mul * ker_x
        dp_y += mul * ker_y
    return dp_x, dp_y


def _calc_viscosity(subj, neighbours):
    visc_x = 0.
    visc_y = 0.
    for n in neighbours:
        if _distance(subj, n) >= h or n == subj:
            continue
        visc_x += n.m * (n.vx - subj.vx) / n.rho * _ddw_visc(subj, n)
        visc_y += n.m * (n.vy - subj.vy) / n.rho * _ddw_visc(subj, n)
    return mu_visc * visc_x, mu_visc * visc_y


def _calc_ext_forces(subj, neighbours):
    return 0., -1.


def compute_next_state(particles):
    result = []
    for p in particles:
        rho = _calc_rho(p, particles)
        dpressure_x, dpressure_y = _calc_dpressure(p, particles, rho)
        visc_x, visc_y = _calc_viscosity(p, particles)
        ext_forces_x, ext_forces_y = _calc_ext_forces(p, particles)
        acceleration_x = (-dpressure_x + visc_x + ext_forces_x) / rho
        acceleration_y = (-dpressure_y + visc_y + ext_forces_y) / rho
        nvx = p.vx + acceleration_x * dt
        nvy = p.vy + acceleration_y * dt
        nx = p.x + dt * (nvx + dt / 2. * acceleration_x)
        if nx < 0:
            nx = -nx
            nvx = -nvx
        ny = p.y + dt * (nvy + dt / 2. * acceleration_y)
        if ny < 0:
            ny = -ny
            nvy = -nvy
        new = Particle()
        new.set_params(nx, ny, nvx, nvy, rho)
        result.append(new)
    return result
