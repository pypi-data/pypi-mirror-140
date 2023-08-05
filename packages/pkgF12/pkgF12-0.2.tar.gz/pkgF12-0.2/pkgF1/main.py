import webbrowser
import os
import pkgF1


def f1func(number):
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

    # 1st method how to open html files in chrome using
    filename = 'template\\GFG.html'
    webbrowser.open_new_tab(filename)
    path = os.path.dirname(pkgF1.__file__)
    print("path", path,"This Is a F1Func updated", filename)
    return number


