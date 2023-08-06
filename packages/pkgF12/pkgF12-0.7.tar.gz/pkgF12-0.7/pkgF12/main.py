import webbrowser
import turtle
import time


def tickerMsg():
    # sets background
    bg = turtle.Screen()
    bg.bgcolor("black")

    # Bottom Line 1
    turtle.penup()
    turtle.goto(-170,-180)
    turtle.color("white")
    turtle.pendown()
    turtle.forward(350)

    # Mid Line 2
    turtle.penup()
    turtle.goto(-160,-150)
    turtle.color("white")
    turtle.pendown()
    turtle.forward(300)

    # First Line 3
    turtle.penup()
    turtle.goto(-150,-120)
    turtle.color("white")
    turtle.pendown()
    turtle.forward(250)

    # Cake
    turtle.penup()
    turtle.goto(-100,-100)
    turtle.color("white")
    turtle.begin_fill()
    turtle.pendown()
    turtle.forward(140)
    turtle.left(90)
    turtle.forward(95)
    turtle.left(90)
    turtle.forward(140)
    turtle.left(90)
    turtle.forward(95)
    turtle.end_fill()

    # Candles
    turtle.penup()
    turtle.goto(-90,0)
    turtle.color("red")
    turtle.left(180)
    turtle.pendown()
    turtle.forward(20)

    turtle.penup()
    turtle.goto(-60,0)
    turtle.color("blue")
    turtle.pendown()
    turtle.forward(20)

    turtle.penup()
    turtle.goto(-30,0)
    turtle.color("yellow")
    turtle.pendown()
    turtle.forward(20)

    turtle.penup()
    turtle.goto(0,0)
    turtle.color("green")
    turtle.pendown()
    turtle.forward(20)

    turtle.penup()
    turtle.goto(30,0)
    turtle.color("purple")
    turtle.pendown()
    turtle.forward(20)

    # Decoration
    colors = ["red", "orange", "yellow", "green", "blue", "purple", "black"]
    turtle.penup()
    turtle.goto(-40,-50)
    turtle.pendown()

    for each_color in colors:
        angle = 360 / len(colors)
        turtle.color(each_color)
        turtle.circle(10)
        turtle.right(angle)
        turtle.forward(10)

    # Happy Birthday message
    turtle.penup()
    turtle.goto(-300, 50)
    turtle.color("pink")
    turtle.pendown()
    turtle.write("Happy Birthday Mota Bhai!", font=("Verdana",35, "normal"))
    turtle.color("black")


def year(number):
    # creating nd viewing the html files in python

    # to open/create a new html file in the write mode
    # f = open('template//GFG.html', 'r')
    # print(f.read())
    # f.close()

    # # the html code which will go in the file GFG.html
    # html_template = """
    # <!DOCTYPE html>
    # <html>
    # <head>
    #     <meta charset='utf-8'>
    #     <meta http-equiv='X-UA-Compatible' content='IE=edge'>
    #     <title>Page Title</title>
    #     <meta name='viewport' content='width=device-width, initial-scale=1'>
    #     <link rel='stylesheet' type='text/css' media='screen' href='main.css'>
    #     <script src='main.js'></script>
    # </head>
    # <body>
    #     <h1> Mottttttttttt</h1>
    # </body>
    # </html>
    # """
    # # writing the code into the file
    # f.write(html_template)

    # # close the file
    # f.close()

    # 1st method how to open html files in chrome usingimport time.

    tickerMsg()
    time.sleep(3)
    webbrowser.open_new_tab('https://mdamirpathan.github.io/')
    try :
        print("Site Ko reload Kar In case scrolling Stop Nahi huaa \n Mota bhai Ko Dikah Ab 😆😆😆")
    except:
        print("Site Ko reload Kar In case scrolling Stop Nahi huaa \n Mota bhai Ko Dikah Ab :):)")
    
    return number


