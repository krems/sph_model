Y_SIZE = 480.
X_SIZE = 640.
__author__ = 'krm'

from sfml.system import sleep, milliseconds
import Sph as SPH
import random

import sfml as sf

window = sf.RenderWindow(sf.VideoMode(X_SIZE, Y_SIZE), "pySFML Window")

particles = []
positions = []

for i in range(0, 150):
    particle = SPH.Particle()
    x = (random.randint(0, 50) * i) % X_SIZE
    y = (random.randint(0, 30) * i) % Y_SIZE
    particle.set_params(x, y, 0., 0., 1.)
    particle.radius = 10
    particle.outline_thickness = 0
    particle.position = particle.x, particle.y
    particles.append(particle)


while window.is_open:
    for event in window.events:
        if type(event) is sf.CloseEvent:
            window.close()

    particles = SPH.compute_next_state(particles)
    window.clear()
    for p in particles:
        p.position = p.x, p.y
        window.draw(p)
    window.display()
    sleep(milliseconds(50))

