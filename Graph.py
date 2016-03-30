Y_SIZE = 480.
X_SIZE = 640.

import Sph as SPH
import random

import sfml as sf

window = sf.RenderWindow(sf.VideoMode(X_SIZE, Y_SIZE), "Water under gravity")

particles = []

for i in range(0, 250):
    particle = SPH.Particle()
    x = (random.randint(0, 50) * i) % X_SIZE
    y = (random.randint(0, 30) * i) % Y_SIZE
    particle.set_params(x, y, 0., 0., 1., 1., 1.)
    particle.radius = 10
    particle.outline_thickness = 0
    particle.position = X_SIZE - particle.x, Y_SIZE - particle.y
    particles.append(particle)


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

