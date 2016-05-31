import Sph as SPH
from Sph import BOUND_X
from Sph import BOUND_Y
from Sph import X_SIZE
from Sph import Y_SIZE
import random
import sfml as sf

PARTICLE_RADIUS = 2
DRAW_VELOCITIES = False
DRAW_PRESSURE = False


def water_behind_the_wall(particleCount):
    X1_WALL = BOUND_X + 25
    _particles = []
    x = BOUND_X + 2
    y = BOUND_Y + 2
    for i in range(0, particleCount):
        particle = SPH.Particle()
        if x >= X1_WALL - 2:
            x = BOUND_X + 1
            y += 1
        particle.set_params(x, y, 0., 0., 1.)
        particle.radius = PARTICLE_RADIUS
        particle.outline_thickness = 0
        particle.position = X_SIZE - particle.x, Y_SIZE - particle.y
        _particles.append(particle)
        x += 2
    return _particles


def water_thin_dike_center(particleCount):
    _particles = []
    width = X_SIZE / 5
    x = 2 * width + 1
    y = BOUND_Y + 1
    for i in range(0, particleCount):
        particle = SPH.Particle()
        if x >= 3 * width or x <= 2 * width:
            x = 2 * width + 1
            y += 2
        particle.set_params(x, y, 0., 0., 1.)
        particle.radius = PARTICLE_RADIUS
        particle.outline_thickness = 0
        particle.position = X_SIZE - particle.x, Y_SIZE - particle.y
        _particles.append(particle)
        x += 3
    return _particles


def water_dike_center(particleCount):
    _particles = []
    width = X_SIZE / 3
    x = width + 1
    y = 2 * BOUND_Y
    for i in range(0, particleCount):
        particle = SPH.Particle()
        if x >= 2 * width or x <= width:
            x = width + 1
            y += 10
        particle.set_params(x, y, 0., 0., 1.)
        particle.radius = PARTICLE_RADIUS
        particle.outline_thickness = 0
        particle.position = X_SIZE - particle.x, Y_SIZE - particle.y
        _particles.append(particle)
        x += 3
    return _particles


def water_dike(particleCount):
    _particles = []
    width = (X_SIZE - 2 * BOUND_X) / 4
    x = 2 * BOUND_X
    y = 2 * BOUND_Y
    for i in range(0, particleCount):
        particle = SPH.Particle()
        if x >= width:
            x = 2 * BOUND_X
            y += 4
        particle.set_params(x, y, 0., 0., 1.)
        particle.radius = PARTICLE_RADIUS
        particle.outline_thickness = 0
        particle.position = X_SIZE - particle.x, Y_SIZE - particle.y
        _particles.append(particle)
        x += 4
    return _particles


def water_fall(particleCount):
    _particles = []
    for i in range(0, particleCount):
        particle = SPH.Particle()
        width = (X_SIZE - 2 * BOUND_X) / 4
        x = (X_SIZE - BOUND_X - width) + (random.randint(BOUND_X, width)) % width
        y = (random.randint(BOUND_Y, Y_SIZE - BOUND_Y))
        particle.set_params(x, y, 0., 0., 1.)
        particle.radius = PARTICLE_RADIUS
        particle.outline_thickness = 0
        particle.position = X_SIZE - particle.x, Y_SIZE - particle.y
        _particles.append(particle)
    return _particles


def random_rain(particleCount):
    _particles = []
    for i in range(0, particleCount):
        particle = SPH.Particle()
        x = (random.randint(BOUND_X, X_SIZE - BOUND_X))
        y = (random.randint(BOUND_Y, Y_SIZE - BOUND_Y))
        particle.set_params(x, y, 0., 0., 1.)
        particle.radius = PARTICLE_RADIUS
        particle.outline_thickness = 0
        particle.position = X_SIZE - particle.x, Y_SIZE - particle.y
        _particles.append(particle)
    return _particles


def draw_velocities(window, p):
    lines = sf.VertexArray(sf.PrimitiveType.LINES_STRIP, 2)
    lines[0].position = (X_SIZE - p.x, Y_SIZE - p.y)
    lines[1].position = (X_SIZE - p.x - p.vx, Y_SIZE - p.y - p.vy)
    window.draw(lines)


def draw_pressure(window, p):
    lines = sf.VertexArray(sf.PrimitiveType.LINES_STRIP, 2)
    lines[0].position = (X_SIZE - p.x, Y_SIZE - p.y)
    lines[1].position = (X_SIZE - p.x - p.dpx, Y_SIZE - p.y - p.dpy)
    window.draw(lines)


def set_rest_rho(particles):
    SPH.set_rest_rho(1.)
    particles = SPH.compute_next_state(particles)
    sum = 0.
    for p in particles:
        sum += p.rho
    SPH.set_rest_rho(sum / len(particles))
    return particles


def draw_borders(window):
    rectangle = sf.RectangleShape((BOUND_X - 2, Y_SIZE))
    rectangle.position = (0, 0)
    rectangle.fill_color = sf.Color.CYAN
    window.draw(rectangle)

    rectangle1 = sf.RectangleShape((X_SIZE, BOUND_Y - 2))
    rectangle1.position = (0, 0)
    rectangle1.fill_color = sf.Color.CYAN
    window.draw(rectangle1)

    rectangle2 = sf.RectangleShape((X_SIZE, BOUND_Y))
    rectangle2.position = (0, Y_SIZE - BOUND_Y + 2)
    rectangle2.fill_color = sf.Color.CYAN
    window.draw(rectangle2)

    rectangle3 = sf.RectangleShape((X_SIZE, Y_SIZE))
    rectangle3.position = (X_SIZE - BOUND_X + 2, BOUND_Y - 2)
    rectangle3.fill_color = sf.Color.CYAN
    window.draw(rectangle3)


def main():
    draw_low_part = True
    window = sf.RenderWindow(sf.VideoMode(X_SIZE, Y_SIZE), "Water under gravity")
    particles = water_behind_the_wall(500)
    # set_rest_rho(particles)
    SPH.set_rest_rho(1.)
    while window.is_open:
        for event in window.events:
            if type(event) is sf.CloseEvent:
                window.close()
            if type(event) is sf.MouseButtonEvent:
                draw_low_part = False
        window.clear()
        for p in particles:
            p.radius = 4
            p.outline_thickness = 0
            p.position = X_SIZE - p.x, Y_SIZE - p.y
            window.draw(p)
            if DRAW_VELOCITIES:
                draw_velocities(window, p)
            if DRAW_PRESSURE:
                draw_pressure(window, p)
        draw_borders(window)
        SPH.wall(window, draw_low_part)
        window.display()
        particles = SPH.compute_next_state(particles)


main()
