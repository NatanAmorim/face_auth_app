import PySimpleGUI as sg
import cv2
import numpy as np
import face_recognition
import os

sg.theme('SandyBeach')

nomes = None
cadastro = False
cadastrado = False
autenticado = False
sair = False

try:
    with open("nomes.txt", "r") as file:
        nomes = file.read().split(",")
        nomes = map(str.upper, nomes)
except:
    print('Arquivo de Nomes não encontrado!')

if nomes is not None:
    layout = [[sg.Text("Digite o seu ID")],
          [sg.Input(key='-INPUT-')],
          [sg.Text(size=(40,1), key='-OUTPUT-')],
          [sg.Button('Entrar'), sg.Button('Cadastrar'), sg.Button('Sair')]]
else:
    layout = [[sg.Text("Nenhum ID cadastrado")],
              [sg.Text(size=(40, 1), key='-OUTPUT-')],
              [sg.Button('Cadastrar'), sg.Button('Sair')]]

window = sg.Window('Face Auth App', layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Sair':
        sair = True
        break
    if event == 'Cadastrar':
        cadastro = True
        break
    if values['-INPUT-'].upper() in nomes and not event == 'Cadastrar':
        window['-OUTPUT-'].update('Olá ' + values['-INPUT-'] + "! seja bem-vindo.")
        sg.Popup('Olá ' + values['-INPUT-'] + "! seja bem-vindo.", keep_on_top=True, no_titlebar=True, auto_close_duration=1, auto_close=False)
        id = values['-INPUT-']
        break
    else:
        window['-OUTPUT-'].update("ID não encontrado!")

window.close()

if not (event == 'Sair'):
    layout_webcam = [[sg.Text("Qual o Tipo de WebCam?")],
                     [sg.Input(key='-INPUT-')],
                     [sg.Text(size=(40,1), key='-OUTPUT-')],
                     [sg.Button('Normal'), sg.Button('IP'), sg.Button('Sair')]]

    window = sg.Window('Webcam', layout_webcam)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Sair':
            sair = True
            break
        if event == 'IP':
            if values['-INPUT-'] != "" and values['-INPUT-'][0:4] == 'http':
                cap = cv2.VideoCapture(values['-INPUT-'])
                break
            else:
                window['-OUTPUT-'].update("IP está incorreto!")
        else:
            cap = cv2.VideoCapture(0)
            break

    window.close()

if cadastro:
    layout_cadastro = [[sg.Text("Qual o seu ID?")],
                       [sg.Input(key='-INPUT-')],
                       [sg.Text(size=(40, 1), key='-OUTPUT-')],
                       [sg.Button('OK'), sg.Button('Sair')]]

    window = sg.Window('Cadastro', layout_cadastro)

    while not cadastrado:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Sair':
            sair = True
            break
        if values['-INPUT-'].upper() in nomes:
            window['-OUTPUT-'].update('ID ' + values['-INPUT-'] + " já está sendo ultilizado!")
            sg.Popup('ID ' + values['-INPUT-'] + " já está sendo ultilizado!", keep_on_top=True, no_titlebar=True,
                     auto_close_duration=1, auto_close=False)
        else:
            if not values['-INPUT-'] == "":
                layout = [[sg.Text('WebCam', size=(40, 1), justification='center', font='Helvetica 20')],
                          [sg.Image(filename='', key='image')],
                          [sg.Button('Iniciar', size=(10, 1), font='Helvetica 14'),
                           sg.Button('Foto', size=(10, 1), font='Helvetica 14'),
                           sg.Button('Sair', size=(10, 1), font='Helvetica 14'), ]]

                window = sg.Window('WebCam',
                                   layout, location=(800, 400))

                cap.set(3, 640)  # width=640
                cap.set(4, 480)  # height=480
                recording = False

                id = values['-INPUT-']

                while not cadastrado:
                    event, values = window.read(timeout=20)
                    if event == 'Sair' or event == sg.WIN_CLOSED:
                        sair = True
                        break

                    elif event == 'Iniciar':
                        recording = True

                    if recording:
                        ret, frame = cap.read()
                        imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
                        window['image'].update(data=imgbytes)
                        if event == 'Foto':
                            _, frame = cap.read()
                            if _ and frame is not None:
                                cv2.imwrite(f"fotos/{id}.jpg", frame)
                                with open("nomes.txt", "a") as myfile:
                                    myfile.write("," + id.upper())
                            cadastrado = True
window.close()

if True:
    autenticado = False
    imagens = list()
    nomes = list()
    my_list = os.listdir('fotos')

    for file in my_list:
        current_image = cv2.imread(f'fotos/{file}')
        imagens.append(current_image)
        nomes.append(os.path.splitext(file)[0])

    print(nomes)

    def find_encodings(images):
        encode_list = list()
        for img in images:
           img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
           encode = face_recognition.face_encodings(img)[0]
           encode_list.append(encode)
        return encode_list

    encode_list_known = find_encodings(imagens)

    print('Finished running encoding.')

    while not autenticado:
        sucess, img = cap.read()
        img = cv2.resize(img, (360, 240))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        faces_in_frame = face_recognition.face_locations(img)
        encodes_of_frame = face_recognition.face_encodings(img)

        for encoded_face, face_location in zip(encodes_of_frame, faces_in_frame):
            matches = face_recognition.compare_faces(encode_list_known, encoded_face)
            face_distance = face_recognition.face_distance(encode_list_known,
                                                           encoded_face)  # Menor distancia é a mais precisa

            print(face_distance)

            match_index = np.argmin(face_distance)

            print(match_index)

            if matches[match_index]:
                name = nomes[match_index].upper()
                print(name)
                if name == id.upper():
                    autenticado = True
                    print('_' * 60)
                    print('Autenticado com sucesso!')
                    print('_' * 60)
                y1, x2, y2, x1 = face_location
                cv2.rectangle(img, (x1, y1), (x2, y2), (180, 20, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (180, 20, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imshow('WebCam', img)
        cv2.waitKey(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


cap.release()
cv2.destroyAllWindows()

if autenticado:
    import PySimpleGUI as sg

    theme_dict = {'BACKGROUND': '#2B475D',
                  'TEXT': '#EEEEEE',
                  'INPUT': '#F2EFE8',
                  'TEXT_INPUT': '#000000',
                  'SCROLL': '#F2EFE8',
                  'BUTTON': ('#000000', '#C2D4D8'),
                  'PROGRESS': ('#EEEEEE', '#C7D5E0'),
                  'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}

    # sg.theme_add_new('Dashboard', theme_dict)     # if using 4.20.0.1+
    sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
    sg.theme('SandyBeach')

    BORDER_COLOR = '#C7D5E0'
    DARK_HEADER_COLOR = '#EEEEEE'
    BPAD_TOP = ((20, 20), (20, 10))
    BPAD_LEFT = ((20, 10), (0, 10))
    BPAD_LEFT_INSIDE = (0, 10)
    BPAD_RIGHT = ((10, 20), (10, 20))

    top_banner = [[sg.Text('Dashboard' + ' ' * 64, font='Any 20', background_color=DARK_HEADER_COLOR),
                   sg.Text('Segunda-feira 26 Outubro', font='Any 20', background_color=DARK_HEADER_COLOR)]]

    top = [[sg.Text(f'Sejá bem vindo {id}!', size=(50, 1), justification='c', pad=BPAD_TOP, font='Any 20')],
           [sg.T(f'{i * 25}-{i * 34}') for i in range(7)], ]

    block_3 = [[sg.Text('Titulo 3', font='Any 20')],
               [sg.Input(), sg.Text('lorem ipsum')],
               [sg.Button('Go'), sg.Button('Sair')]]

    block_2 = [[sg.Text('Titulo 2', font='Any 20')],
               [sg.T('lorem ipsum dolor sit amet')],
               [sg.Image(data=sg.DEFAULT_BASE64_ICON)]]

    block_4 = [[sg.Text('Titulo 4', font='Any 20')],
               [sg.T('lorem ipsum dolor sit amet')],
               [sg.T('lorem ipsum dolor sit amet')],
               [sg.T('lorem ipsum dolor sit amet')],
               [sg.T('lorem ipsum dolor sit amet')]]

    layout = [[sg.Column(top_banner, size=(960, 60), pad=(0, 0), background_color=DARK_HEADER_COLOR)],
              [sg.Column(top, size=(920, 90), pad=BPAD_TOP)],
              [sg.Column([[sg.Column(block_2, size=(450, 150), pad=BPAD_LEFT_INSIDE)],
                          [sg.Column(block_3, size=(450, 150), pad=BPAD_LEFT_INSIDE)]], pad=BPAD_LEFT,
                         background_color=BORDER_COLOR),
               sg.Column(block_4, size=(450, 320), pad=BPAD_RIGHT)]]

    window = sg.Window('Dashboard - Autenticado com sucesso', layout, margins=(0, 0), background_color=BORDER_COLOR,
                       no_titlebar=True, grab_anywhere=True)

    sg.Popup(f"Olá {name} login autorizado por reconhecimento facial!", keep_on_top=True, no_titlebar=True,
             auto_close_duration=1, auto_close=False)

    while True:  # Event Loop
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Sair':
            break
    window.close()

print('Finalizado com sucesso.')
