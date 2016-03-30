Y_SIZE = 480.
X_SIZE = 640.

import Sph as SPH
import random

import sfml as sf

window = sf.RenderWindow(sf.VideoMode(X_SIZE, Y_SIZE), "Water under gravity")


def water_fall(particleCount):
    _particles = []
    for i in range(0, particleCount):
        particle = SPH.Particle()
        width = X_SIZE / 4
        x = (X_SIZE - width) + (random.randint(0, width)) % width
        y = (random.randint(0, 30) * i) % Y_SIZE
        particle.set_params(x, y, 0., 0., 1., 1., 1.)
        particle.radius = 10
        particle.outline_thickness = 0
        particle.position = X_SIZE - particle.x, Y_SIZE - particle.y
        _particles.append(particle)
    return _particles


def random_rain(particleCount):
    _particles = []
    for i in range(0, particleCount):
        particle = SPH.Particle()
        x = (random.randint(0, 50) * i) % X_SIZE
        y = (random.randint(0, 30) * i) % Y_SIZE
        particle.set_params(x, y, 0., 0., 1., 1., 1.)
        particle.radius = 10
        particle.outline_thickness = 0
        particle.position = X_SIZE - particle.x, Y_SIZE - particle.y
        _particles.append(particle)
    return _particles


particles = water_fall(400)
while window.is_open:
    for event in window.events:
        if type(event) is sf.CloseEvent:
            window.close()

    window.clear()
    for p in particles:
        p.radius = 10
        p.outline_thickness = 0
        p.position = X_SIZE - p.x, Y_SIZE - p.y
        window.draw(p)
    window.display()
    particles = SPH.compute_next_state(particles)

