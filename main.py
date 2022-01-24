import PySimpleGUI as sg

layout = [[sg.Text("What's your name?")],
          [sg.Button('Ok')]]


window = sg.Window('说唱脚本', layout)

layout = [[sg.Text("What's your name?")],
          [sg.Button('Ok')],
          [sg.Button('Ok')]]



event, values = window.read()


print('Hello', values[0], "! Thanks for trying PySimpleGUI")

window.close()
