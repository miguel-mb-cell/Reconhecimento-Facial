import cv2
import face_recognition
import numpy as np
import os
import customtkinter as ctk
import threading
from PIL import Image

BACKGROUND_COLOR = "#2E2E2E"
unlock = False

# Define a video capture object
vid = cv2.VideoCapture(0)

# Declare the width and height in variables
width, height = 800, 600

# Set the width and height
vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# Create a GUI app
app = ctk.CTk()
app.geometry("800x600")
app.title("Face Recognition")
app.configure(fg_color=BACKGROUND_COLOR)

# Function to maximize window after opening
def maximize_window():
    app.state('zoomed')

# Schedule the maximize function to run shortly after the app starts
app.after(100, maximize_window)

# Bind the app with Escape keyboard to quit app whenever pressed
app.bind('<Escape>', lambda e: app.quit())

# Load encodings and class names
def load_encodings(encodings_path):
    encodings = []
    class_names = []
    for file in os.listdir(encodings_path):
        if file.endswith(".npy"):
            class_name = file.split('.')[0]
            encoding = np.load(os.path.join(encodings_path, file))
            encodings.append(encoding)
            class_names.append(class_name)
    return encodings, class_names

# Path for saved encodings
encodings_path = 'faces'
known_encodings, class_names = load_encodings(encodings_path)
print(f"Loaded classes: {class_names}")

# Global flags
recognize_mode = False
matches = []

# Function to capture and use the encoding
def capture_image():
    if name_input.get() == "":
        show_temporary_message_capture("Digite um nome", False)
        return

    success, frame = vid.read()
    if not success:
        print("Failed to capture frame")
        return

    # Convert the frame to RGB and find encodings
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(img_rgb)

    if encodings:
        # Save the face encoding as a numpy array
        np.save(f'faces/{name_input.get()}.npy', encodings[0])
        add_encoding(name_input.get())
        show_temporary_message_capture(f"Encoding salvo para\n{name_input.get()}", True)
    else:
        show_temporary_message_capture("Nenhum rosto detectado\nTente novamente.", False)

# Variável para armazenar o frame temporário atual
current_temp_frame = None

def show_temporary_message_unlock(message, success):
    global current_temp_frame

    # Se já houver um frame temporário, remova-o antes de criar outro
    if current_temp_frame is not None:
        current_temp_frame.destroy()
        current_temp_frame = None

    # Criar um frame temporário para exibir o ícone e o texto
    temp_frame = ctk.CTkFrame(desbloquear_frame)
    temp_frame.place(relx=0.5, rely=0.6, anchor="center")  # Posição relativa fixa
    current_temp_frame = temp_frame  # Atualizar a referência ao frame atual

    # Configurar o ícone
    if success:
        icon_path = "imgs/check_icon.png"
        text_color = "green"
    else:
        icon_path = "imgs/x_icon.png"
        text_color = "red"

    icon = Image.open(icon_path)
    icon = icon.resize((50, 50), Image.LANCZOS)
    icon = ctk.CTkImage(dark_image=icon, size=(50, 50))

    icon_label = ctk.CTkLabel(temp_frame, image=icon, text="")
    icon_label.pack(pady=(0, 10))  # Espaçamento entre o ícone e o texto
    icon_label.image = icon  # Evitar coleta de lixo

    # Configurar o texto
    text_label = ctk.CTkLabel(temp_frame, text=message, text_color=text_color, font=("Arial", 14))
    text_label.pack()

    # Remover o frame após 2 segundos
    app.after(3000, lambda: remove_temp_frame(temp_frame))

def show_temporary_message_capture(message, success):
    global current_temp_frame

    # Se já houver um frame temporário, remova-o antes de criar outro
    if current_temp_frame is not None:
        current_temp_frame.destroy()
        current_temp_frame = None

    # Criar um frame temporário para exibir o ícone e o texto
    temp_frame = ctk.CTkFrame(app, fg_color=BACKGROUND_COLOR)
    temp_frame.place(relx=0.11, rely=0.2, anchor="center")  # Posição relativa fixa
    current_temp_frame = temp_frame  # Atualizar a referência ao frame atual

    # Configurar o ícone
    if success:
        text_color = "green"
    else:
        text_color = "red"

    # Configurar o texto
    text_label = ctk.CTkLabel(temp_frame, text=message, text_color=text_color, font=("Arial", 14))
    text_label.pack()

    # Remover o frame após 2 segundos
    app.after(3000, lambda: remove_temp_frame(temp_frame))

def remove_temp_frame(temp_frame):
    global current_temp_frame
    if temp_frame == current_temp_frame:
        temp_frame.destroy()
        current_temp_frame = None

# Function to toggle the recognition mode
def toggle_recognition():
    global recognize_mode
    recognize_mode = not recognize_mode

    if recognize_mode:
        mode_switch.configure(text="Desbloquear")
        unlock_button.configure(state="normal")
        capture_button.configure(state="disabled")
        name_input.configure(state="disabled")
    else:
        mode_switch.configure(text="Capturar Imagem")
        unlock_button.configure(state="disabled")
        capture_button.configure(state="normal")
        name_input.configure(state="normal")

def unlock_access():
    global unlock
    unlock = True    
    app.after(500, lock_access)

def lock_access():
    global unlock
    unlock = False

# Function to properly close the application
def on_closing():
    global camera_running
    camera_running = False  # Stop the camera thread
    vid.release()
    cv2.destroyAllWindows()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_closing)

# Configure grid layout
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.grid_columnconfigure(2, weight=1)
app.grid_rowconfigure(0, weight=1)

# Create widgets for the first column (Captura de Imagem)
captura_frame = ctk.CTkFrame(master=app, fg_color=BACKGROUND_COLOR)
captura_frame.grid(row=0, column=0)
captura_frame.grid_rowconfigure(0, weight=1)

name_label = ctk.CTkLabel(master=captura_frame, text="Digite o nome:")
name_label.grid(row=0, column=0, pady=10, columnspan=2)

name_input = ctk.CTkEntry(master=captura_frame)
name_input.grid(row=1, column=0, pady=10, columnspan=2)

capture_button = ctk.CTkButton(master=captura_frame, text="Capturar Imagem", command=capture_image)
capture_button.grid(row=2, column=0, pady=10, columnspan=2)

# Display the encodings in a CTkScrollableFrame
def display_encodings():
    known_encodings, class_names = load_encodings(encodings_path)
    
    # Limpar os widgets existentes no frame
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    # Carregar a imagem da lixeira
    trash_icon = Image.open("imgs/trash_icon.png")
    trash_icon = trash_icon.resize((20, 20), Image.LANCZOS)
    trash_ctk_image = ctk.CTkImage(dark_image=trash_icon, size=(20, 20))
    
    # Adicionar os nomes das classes e o botão de lixeira no frame
    for name in class_names:
        # Frame interno para agrupar o label e o botão
        item_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        item_frame.pack(fill="x", padx=5, pady=2)

        # Label para o nome da classe
        label = ctk.CTkLabel(item_frame, text=name, anchor="w")
        label.pack(side="left", padx=(5, 10))

        # Botão de lixeira
        trash_button = ctk.CTkButton(
            item_frame,
            image=trash_ctk_image,
            text="",
            width=20,
            height=20,
            fg_color="transparent",
            hover_color="#ffcccc",
            cursor="hand1",
            command=lambda n=name, f=item_frame: handle_trash_button(n, f)
        )
        trash_button.pack(side="right", padx=5)

# Função para remover o arquivo e o frame
def handle_trash_button(name, frame):
    remove_encoding(name)  # Remove o arquivo
    frame.destroy()   

# Função para remover o encoding associado
def remove_encoding(name):
    # Construir o caminho do arquivo com base no nome
    file_name = f"{name}.npy"
    file_path = os.path.join("faces", file_name)
    
    try:
        # Verificar se o arquivo existe e removê-lo
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Arquivo '{file_name}' removido com sucesso.")
        else:
            print(f"Arquivo '{file_name}' não encontrado.")
    except Exception as e:
        print(f"Erro ao tentar remover o arquivo '{file_name}': {e}")

# Função para remover o arquivo e o frame
def add_encoding(name):
    trash_icon = Image.open("imgs/trash_icon.png")
    trash_icon = trash_icon.resize((20, 20), Image.LANCZOS)
    trash_ctk_image = ctk.CTkImage(dark_image=trash_icon, size=(20, 20))

    item_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    item_frame.pack(fill="x", padx=5, pady=2)

    # Label para o nome da classe
    label = ctk.CTkLabel(item_frame, text=name, anchor="w")
    label.pack(side="left", padx=(5, 10))

    # Botão de lixeira
    trash_button = ctk.CTkButton(
        item_frame,
        image=trash_ctk_image,
        text="",
        width=20,
        height=20,
        fg_color="transparent",
        hover_color="#ffcccc",
        cursor="hand1",
        command=lambda n=name, f=item_frame: handle_trash_button(n, f)
    )
    trash_button.pack(side="right", padx=5)

# Label
label = ctk.CTkLabel(captura_frame, text="Loaded Classes:")
label.grid(row=3, column=0, pady=10, columnspan=2)

scrollable_frame = ctk.CTkScrollableFrame(captura_frame, width=220, height=250, fg_color=BACKGROUND_COLOR, 
                                          border_color="#1F6AA5", border_width=2, corner_radius=10,
                                          scrollbar_button_color="#1F6AA5")
scrollable_frame.grid(row=4, column=0, pady=10, padx=10, columnspan=2)

# Load and display encodings initially
display_encodings()

# Create widgets for the second column (Reconhecimento Facial)
camera_frame = ctk.CTkFrame(master=app, fg_color=BACKGROUND_COLOR)
camera_frame.grid(row=0, column=1)
camera_frame.grid_rowconfigure(0, weight=1)

title_label = ctk.CTkLabel(master=camera_frame, text="Reconhecimento Facial", font=("Arial", 30))
title_label.grid(row=0, column=1, pady=10, padx=10)

mode_switch = ctk.CTkSwitch(master=camera_frame, text="Capturar Imagem", command=toggle_recognition)
mode_switch.grid(row=1, column=1, pady=10, padx=10)

label_widget = ctk.CTkLabel(master=camera_frame, text="")
label_widget.grid(row=2, column=1, pady=10, padx=10)

# Create widgets for the third column (Desbloquear)
desbloquear_frame = ctk.CTkFrame(master=app, fg_color=BACKGROUND_COLOR)
desbloquear_frame.grid(row=0, column=2, sticky="ns")
desbloquear_frame.grid_rowconfigure(0, weight=1)

unlock_button = ctk.CTkButton(master=desbloquear_frame, text="Desbloquear", command=unlock_access)
unlock_button.grid(row=0, column=2, pady=10, padx=10)
unlock_button.configure(state="disabled")

message_label = ctk.CTkLabel(master=desbloquear_frame, text="")
message_label.place_forget()

# Create a directory to store training images if it doesn't exist
os.makedirs('faces', exist_ok=True)

# Global flag to control the camera thread
camera_running = True

# Function to handle the camera feed and recognition in a separate thread
def camera_thread():
    global matches, camera_running, unlock

    while camera_running:
        known_encodings, class_names = load_encodings(encodings_path)
        success, frame = vid.read()
        if not success:
            print("Failed to capture frame")
            continue

        if recognize_mode:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            if face_locations == [] and unlock:
                show_temporary_message_unlock("Nenhum rosto detectado\nTente novamente", False)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
                name = "Desconhecido"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = class_names[first_match_index].upper()
                    if unlock:
                        show_temporary_message_unlock("Desbloqueado", True)
                if True not in matches and unlock:
                    show_temporary_message_unlock("Acesso Negado", False)

                y1, x2, y2, x1 = face_location
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 2)

        # Convert the frame to a format suitable for Tkinter
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        captured_image = Image.fromarray(opencv_image)
        photo_image = ctk.CTkImage(dark_image=captured_image, size=(width, height))

        # Update the image on the label in the main thread
        label_widget.after(0, lambda: label_widget.configure(image=photo_image))
        label_widget.photo_image = photo_image

# Function to start the camera thread
def start_camera_thread():
    camera_thread_obj = threading.Thread(target=camera_thread, daemon=True)
    camera_thread_obj.start()

app.protocol("WM_DELETE_WINDOW", on_closing)

# Start the camera processing in a separate thread
start_camera_thread()

# Create an infinite loop for displaying app on screen
app.mainloop()
