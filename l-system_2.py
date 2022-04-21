import turtle
import random
from mpmath import mp, mpf

mp.dps = 10

turtle.bgcolor(255 / 255, 240 / 255, 244 / 255)
turtle.color('black')
turtle.speed("fastest")
turtle.tracer(0)
turtle.penup()
turtle.setposition(0, -500)
turtle.pendown()

axiom = "X"
line = ""

tr = {"X": "F[@[-X]+X]", "F": "F", "@": "@", "+": "+", "-": "-", "[": "[", "]": "]"}

i = 14
s = mpf(100)
w = mpf(36)
turtle.pensize(w)
a = lambda: random.uniform(0, 50)
c = 2.5

p = [0, 0]
b = 45

stack = []

turtle.left(90)
turtle.forward(220)

while i != 0:
    for ch in axiom:
        line += tr[ch]
    axiom = line
    line = ''
    i -= 1

i = 1
for ch in axiom:
    if ch == "X" or ch == "F":
        turtle.forward(s + random.uniform(0, 5))
    if ch == "@":
        s /= 1.2
        s = max(1, s)
        s += random.uniform(-1 / i, 1 / i)
        w /= 1.18
        w += random.uniform(-5 / i, 5 / i)
        w = max(0.4, w)
        c += 4
        c = min(220, c)
        turtle.color((c - 2.5) / 255, (c + 5) / 255, (c - 2.5) / 255)
        turtle.pensize(int(w))
    elif ch == "+":
        turtle.right(a())
    elif ch == "-":
        turtle.left(a())
    elif ch == "[":
        b = turtle.heading()
        p = turtle.pos()

        stack.append((b, p, w, s, c))
    elif ch == "]":
        angle, pos, thickness, step, color = stack.pop()
        turtle.setposition(pos)
        turtle.setheading(angle)
        turtle.pensize(thickness)
        turtle.color((color - 2.5) / 255, (color + 5) / 255, (color - 2.5) / 255)
        w = thickness
        s = step
        c = color
    i += 1

turtle.update()
turtle.mainloop()

input("prompt: ")