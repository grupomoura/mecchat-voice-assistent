import openai  # pip install openai
import speech_recognition as sr  # pip install SpeechRecognition
import pyttsx4  # pip install pyttsx4
import configparser
import os
import json
import webbrowser
import threading
import pytz
from datetime import datetime
import platform
from colorama import Fore, Back, Style, init
import keyboard  
from time import sleep
from pydub import AudioSegment
from pydub.playback import play

# Inicializa o colorama (deve ser chamado antes de usá-lo)
init()

def print_color(color="white", text=""):
    if color.lower() == "green":
        color_code = Fore.GREEN
    elif color.lower() == "red":
        color_code = Fore.RED
    elif color.lower() == "blue":
        color_code = Fore.BLUE
    elif color.lower() == "yellow":
        color_code = Fore.YELLOW
    else:
        color_code = Fore.WHITE  # Cor padrão (sem cor)
    
    print(color_code + text + Style.RESET_ALL)

# Obtém o nome do sistema operacional
sistema_operacional = platform.system()

interrupt_speech = False
chat_press = False
LISTENING_SOUND = AudioSegment.from_wav("voice/bip.wav")
LISTENING_SOUND = AudioSegment.from_mp3("voice/message_start.mp3")
LOADING_SOUND = AudioSegment.from_mp3("voice/loading.mp3")
ERROR_SOUND = AudioSegment.from_mp3("voice/error.mp3")

config = configparser.ConfigParser()
config.read('config.ini')

# Key da openai para utilizar o chatgpt
openai.api_key = config.get('openai', 'api_key')
prompt_default = config.get('prompts', 'default')
username = config.get('user', 'username')
mic_sensibility = int(config.get('configs', 'mic_sensibility'))
speed_voice = int(config.get('configs', 'speed_voice'))
if sistema_operacional.lower() == 'windows':
    speed_voice = speed_voice*3
elif sistema_operacional.lower() == 'linux':
    speed_voice = speed_voice*3
ia_volume = float(config.get('configs', 'ia_volume'))

def clear_console():
    try:
        os.system("clear")
    except:
        pass
    try:
        os.system("cls")
    except:
        pass

def return_timer():
    # Define o fuso horário de Brasília
    brasilia_tz = pytz.timezone('America/Sao_Paulo')

    # Obtém a hora atual de Brasília
    brasilia_time = datetime.now(brasilia_tz)

    # Formata a hora de Brasília e imprime
    formatted_time = brasilia_time.strftime("%d-%m-%Y-%H_%M_%S")
    return("["+formatted_time+"]")

log_timer = return_timer()
    
def print_ts_log(text=""):
    # Define o fuso horário de Brasília
    brasilia_tz = pytz.timezone('America/Sao_Paulo')

    # Obtém a hora atual de Brasília
    brasilia_time = datetime.now(brasilia_tz)

    # Formata a hora de Brasília e imprime
    formatted_time = brasilia_time.strftime("%H:%M:%S")
    print_color("green","[" + formatted_time + "] " + text)

clear_console()
print_color("green",'_________________________________________\n')
print_ts_log('MecChat Voice Assistent 1.0')
# Imprime o nome do sistema operacional
print(f"Sistema Operacional: {sistema_operacional}")

print_color("Blue", """
Comandos de voz disponíveis:
- "Assistente, "Qualquer coisa que queira perguntar"
- "Assistente, desligar": Isso encerrará o Assistente MecChat.
- "Assistente, já entendi": Isso interrompe a resposta do Assistente MecChat.
- "Assistente, pode parar": Isso interrompe a resposta do Assistente MecChat.
- "Assistente, abrir área do aluno": Isso abrirá a área do aluno em um navegador.
- "Assistente, abrir plataforma": Isso abrirá a plataforma especialista em um navegador.            
""")
print_color("green",'_________________________________________')

while True:
    option = input("""\n\nSelecione uma opção:
    1. Conversar digitando
    2. Conversar falando (Microfone)
    3. Apertar (ctrl + alt + f) para falar
    Resposta: """)
    if option == "1":
        noKeyWord = True
        chat_input = True
        print()
        break
    elif option == "2":
        noKeyWord = False
        chat_input = False
        print()
        break
    elif option == "3":
        noKeyWord = False
        chat_input = False
        print()
        break
    else:
        print("\n\nOpção inválida!")

print_color("yellow","Inicializando.. ")
play(LOADING_SOUND)

def wait_for_ctrl_f():
    global chat_press
    while not keyboard.is_pressed('ctrl+alt+f'):
        pass
    chat_press = True

def start_wait_for_ctrl_f():
    # Inicie uma thread para aguardar a tecla Ctrl+F ser pressionada
    ctrl_f_thread = threading.Thread(target=wait_for_ctrl_f)
    ctrl_f_thread.start()

if option == "3":
    # Inicie uma thread para aguardar a tecla Ctrl+F ser pressionada
    start_wait_for_ctrl_f()

# user settings
context = prompt_default

if chat_input:
    noKeyWord = True

def generate_answer(prompt):  # cria a instância da api do chatgpt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Meu nome é {0} e {1}".format(
            username, context)}, {"role": "user", "content": "{0}".format(prompt)}],
        max_tokens=500,
        temperature=0.5,
    )
    return [response.choices[0].message.content]

# Função para verificar se a thread deve ser interrompida
def thread_stop():
    return interrupt_speech

def talk(texto, thread_stop):  # função para sintese de vo, thread_stopz
    global interrupt_speech
    
    # Verifica se a síntese de voz deve ser interrompida
    if interrupt_speech or thread_stop():
        if engine._inLoop:
            engine.endLoop()
        engine.stop()
        interrupt_speech = False
        return  # Encerra a função prematuramente se interrupt_speech for verdadeiro
    try:
        engine.say(texto)
        engine.runAndWait()
        engine.stop()
    except:
        if engine._inLoop:
            engine.endLoop()
            engine.stop()
            talk(texto, thread_stop)
    return

def wishme():    # função para reconhecer qual momendo do dia, manhã, tarde, noite.
    hour=int(datetime.now().hour)
    if hour>=0 and hour<12:
        talk('Bom dia! ', thread_stop)
    elif hour>=12 and hour<18:   
        talk('Boa tarde! ', thread_stop)
    else:
        talk('Boa noite! ', thread_stop)

def navegator(url):
    try:
        webbrowser.get(using='chrome').open(url)
    except:
        try:
            webbrowser.get(using='google-chrome').open(url)
        except:
            webbrowser.open(url)

# variaveis para controlar o reconhecimento de voz
r = sr.Recognizer()
mic = sr.Microphone()

# variaveis de controle de sintese de voz
try:
    engine = pyttsx4.init() #Padrão selecionado
except:
    engine = pyttsx4.init('dummy')

# ==================== LISTAGEM DE VOZES  ====================
voices = engine.getProperty('voices')

# ==================== CONFIGURAÇOES DE VOZ  ====================
engine.setProperty('rate', speed_voice)  # velocidade 120 = lento
engine.setProperty("volume", ia_volume) # Volume da voz 0-1

# ==================== SELEÇÃO DE VOZES  ====================
for i, voice in enumerate(voices):
    if "brazil" in voice.id.lower() or voice.languages == ['pt-BR'] or voice.name == 'Microsoft Maria Desktop - Portuguese(Brazil)':
        engine.setProperty('voice', voices[i].id)
        print()
        print_color("green", "MecChat > Olá! Sou seu assistente pessoal")
        talk("Olá", thread_stop)
        wishme()
        talk("Sou seu assistente pessoal", thread_stop)
        if option == "3":
            print_color("yellow","Pressione (ctrl + alt + f) para falar")
        break
    else:
        print_color("red",'Não foi possível selecionar uma voz\n\n')

def start_recognition():
    # start voice recognition
    with mic as source:
        try:
            r.adjust_for_ambient_noise(source, duration = 1)
            r.energy_threshold = mic_sensibility
            r.pause_threshold = 1
            print_color("yellow","Escutando..")
            if option == "3":
                play(LISTENING_SOUND)
            audio = r.listen(source=source, phrase_time_limit=6)
            question = r.recognize_google(audio, language="pt-BR")
        except sr.UnknownValueError: # error: recognizer does not understand
            print()
            return
        except sr.RequestError:
            print('Serviço offline') # error: recognizer is not connected
            return
        except Exception:
            print_ts_log('Verifique start_recognition')
            return
        return question

while True:
    question = ""

    if chat_input:
        print()
        question = input(Fore.BLUE + f"> {username}: " + Style.RESET_ALL)
    elif option == "3":
        if chat_press:
            question = start_recognition()
            sleep(0.05)
        else:
            continue
    else:
        try:
            question = start_recognition()
        except:
            continue

    if question != None and question.lower().startswith("assistente") or noKeyWord or question != None and chat_press:
        if ("desligar" in question.lower() or "encerrar" in question.lower()):
            print_ts_log("Desligando..")
            talk("Desligando.", thread_stop)
            exit(0)

        elif ("área do aluno" in question.lower()):
            print_color("green","Ok! Abrindo a área do aluno.")
            talk("Ok! Abrindo a área do aluno.", thread_stop)
            navegator("https://app.mecanicatotalacademy.com.br/lessons")
            continue

        elif ("abrir plataforma" in question.lower()):
            print_color("green","Ok! Abrindo a plataforma especialista.")
            talk("Ok! Abrindo a plataforma especialista.", thread_stop)
            navegator("https://app.mecanicatotalacademy.com.br")
            continue

        elif ("já entendi" in question.lower() or "pode parar" in question.lower()):
            interrupt_speech = True
            print_color("green", "MecChat > Ok!")
            talk("Ok!", thread_stop)
            continue
        
        if not chat_input:
            print_color("blue",f"{username}: {question}")

        answer = generate_answer(question)

        try:
            # Save the current interaction on memory database (json file)
            with open(f'logs/memory_data.json_{log_timer}', 'r') as f:
                interactions = json.load(f)
        except:
            interactions = []
            pass

        interactions.append({
                'timer': return_timer(),
                'usuario': question,
                'assistente': answer[0]
            })

        with open(f'logs/memory_data_{log_timer}.json', 'w') as f:
            json.dump(interactions, f)

        print_color("green", f"MecChat > {answer[0]}\n\n")

        # Salve a resposta atual na variável de controle para interromper
        current_response = answer[0]
        # Inicie uma nova thread para síntese de voz
        response_thread = threading.Thread(target=talk, args=(current_response, thread_stop))
        response_thread.start()
        
        if option == "3":
            chat_press = False
            print_color("yellow","Pressione (ctrl + alt + f) para falar")
            start_wait_for_ctrl_f()

        # Continue a execução do loop
        continue

    else:
        if question:
            print(question)
        if option == "3":
            chat_press = False
            if not question:
                play(ERROR_SOUND)
                talk("Não entendi, poderia repetir?", thread_stop)
                print_color("green", "MecChat > Não entendi, poderia repetir?")
                print_color("yellow","\n\nPressione (ctrl + alt + f) para falar")
            start_wait_for_ctrl_f()
        continue
