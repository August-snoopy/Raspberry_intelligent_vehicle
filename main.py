import turtle

colors = ["red", "orange", "yellow", "green", "blue", "purple"]

turtle.speed(0)
turtle.bgcolor("black")

for x in range(360):
    turtle.pencolor(colors[x % len(colors)])
    turtle.width(x / 100 + 1)
    turtle.forward(x)
    turtle.left(59)