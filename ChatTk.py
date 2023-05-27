import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import filedialog
import openai
import os
import threading
import datetime
import json

openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"

try:
    openai.api_key = os.environ['OPENAI_API_KEY']
except KeyError:
    openai.api_key = ""

try:
    openai.api_base = os.environ['OPENAI_API_BASE']
except Exception:
    openai.api_base = ""

model_deployment_name = "gpt-4" # customize this for your own model deployment within the Azure OpenAI Service (e.g. "gpt-4", "gpt-4-32k", "gpt-35-turbo")

chatbot_name = "ChatTk"
system_message = "Your name is " + chatbot_name + ". You are a large language model. You are using the " + model_deployment_name + " AI model via the Azure OpenAI Service. Answer as concisely as possible. Knowledge cutoff: September 2021. Current date: "+str(datetime.date.today())

chathistory = [{"role":"system","content":system_message}]

icon_path = "icon16ChatTk.ico"

font_text = "Consolas 11"

# Set variables - https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference

var_temperature = 0.7 # between 0 and 1
var_top_p=0.95 # between 0 and 1
var_max_tokens = 800 # between 1 and 32,768
var_frequency_penalty = 0 # between -2.0 and 2.0
var_presence_penalty = 0 # between -2.0 and 2.0

# Function to get the response from the OpenAI API after the 'Send' button is clicked
def send():
    
    ask_button.config(state="disabled")
    clear_button.config(state="disabled")
    # Get the user's prompt from the input box
    input_text = input_box.get("1.0", "end")

    output_box.configure(state="normal")
    output_box.insert("end", "User: " + " "*(len(chatbot_name)-4) + input_text+"\n")
    output_box.configure(state="disabled")
    output_box.see("end") # Scroll to the bottom of the output box

    # Insert the user's prompt into the chat history
    inputdict = {"role":"assistant","content":input_text}
    chathistory.append(inputdict)

    # Clear the input box
    input_box.delete("1.0", "end")

    # Create a new thread for the API call
    api_thread = threading.Thread(target=call_api, args=(input_text,))
    api_thread.start()

# Function to call the OpenAI API in a separate thread to prevent locking-up the application while waiting for the API response
def call_api(input_text):

    def generate_text():
        
        try:      
            reply = ""
            chatbot_name_displayed=False
            for chunk in openai.ChatCompletion.create(
                
                engine=model_deployment_name,
                messages=chathistory,
                temperature=var_temperature,
                max_tokens=var_max_tokens,
                top_p=var_top_p,
                frequency_penalty=var_frequency_penalty,
                presence_penalty=var_presence_penalty,
                stop=None,
                stream=True,
            ):
                content = chunk["choices"][0].get("delta", {}).get("content")
                if content is not None:
                    if chatbot_name_displayed == False:
                        output_box.configure(state="normal")
                        output_box.insert("end", chatbot_name +": ")
                        output_box.configure(state="disabled")
                        chatbot_name_displayed=True
                    output_box.configure(state="normal")
                    output_box.insert("end", content)
                    output_box.configure(state="disabled")
                    output_box.see("end")
                    reply = reply+content
            
            output_box.configure(state="normal")
            #Insert two new lines after the response
            output_box.insert("end", "\n\n")
            output_box.configure(state="disabled")
            output_box.see("end")
            
            # Insert the chatbot's response into the chat history
            contentdict = {"role":"assistant","content":reply}
            chathistory.append(contentdict)

        except openai.error.OpenAIError as e:
            messagebox.showerror("Error", f"Azure OpenAI API Error: {e}")

        ask_button.config(state="normal")
        clear_button.config(state="normal")

    # Create a new thread to run the generate_text function
    thread = threading.Thread(target=generate_text)
    thread.start()


# Function to clear the chat boxes, and reset the chat history
def clear_chat():
    input_box.delete("1.0", "end")
    output_box.configure(state="normal")
    output_box.delete("1.0", "end")
    output_box.configure(state="disabled")
    global chathistory
    chathistory = [{"role":"system","content":system_message}]

# Function to handle the "Return" key event
def handle_return(event):
    send()
    return "break"  # Prevents the default behavior of the "Return" key adding a stray carriage return after the input box has been cleared

def open_about_window():

    # Create a new window
    about_window = tk.Toplevel(root)
    about_window.title("About " + chatbot_name)

    # Set the icon if the file exists, otherwise use the default icon
    if os.path.exists(icon_path):
        try:
            about_window.iconbitmap(icon_path)
        except tk.TclError:
            pass

    # Set the size of the window to be 250x150
    about_window.geometry("250x150")

    # Create a Label to display the About message

    about_message = "Created by Guy Gregory\nguy.gregory@microsoft.com\nhttps://aka.ms/ChatToolkit"
    about_label = tk.Label(about_window, text=about_message, font=font_text)
    about_label.pack(side="top", fill="both", expand=True)

    # Create a button to cancel and close the window
    def cancel_and_close():
        # Close the window without saving
        about_window.destroy()

    cancel_button = tk.Button(about_window, text="Close", command=cancel_and_close)
    cancel_button.pack(side="bottom", anchor="center", pady=5)

def open_chatbot_name_window():

    # Create a new window
    chatbot_name_window = tk.Toplevel(root)
    chatbot_name_window.title("Edit chat bot name")
    chatbot_name_window.geometry("250x100")
    chatbot_name_window.minsize(300, 120)  # Set the minimum width to 250 pixels

    # Set the icon if the file exists, otherwise use the default icon
    if os.path.exists(icon_path):
        try:
            chatbot_name_window.iconbitmap(icon_path)
        except tk.TclError:
            pass

    # Create a frame to hold the message box
    message_box_frame = tk.Frame(chatbot_name_window)
    message_box_frame.pack(side="top", fill="both", expand=True)

    # configure the grid
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=3)

    # Chat bot name
    global chatbot_name
    chatbot_name_label = tk.Label(message_box_frame, text="Chat bot name:", font=font_text)
    chatbot_name_label.grid(column=0, row=0, sticky=tk.E, padx=5, pady=5)

    chatbot_name_entry = tk.Entry(message_box_frame, font=font_text, width=14)
    chatbot_name_entry.grid(column=1, row=0, sticky=tk.W, padx=5, pady=5)
    chatbot_name_entry.insert(0, chatbot_name)

    # Create a button to save and close the window
    def save_and_close():

        # Save the system message and close the window
        global chatbot_name
        global system_message
        
        system_message = system_message.replace(chatbot_name, chatbot_name_entry.get(), 1)

        chatbot_name = chatbot_name_entry.get()
        root.title(chatbot_name)

        chatbot_name_window.destroy()
        clear_chat()

    save_button = tk.Button(chatbot_name_window, text="Save and close", command=save_and_close)
    save_button.pack(side="left", padx=6, pady=5)

    # Create a button to cancel and close the window
    def cancel_and_close():
        # Close the window without saving
        chatbot_name_window.destroy()

    cancel_button = tk.Button(chatbot_name_window, text="Cancel", command=cancel_and_close)
    cancel_button.pack(side="right", padx=16, pady=5)

def open_system_message_window():

    # Create a new window
    system_message_window = tk.Toplevel(root)
    system_message_window.title("Edit system message")

    # Set the icon if the file exists, otherwise use the default icon
    if os.path.exists(icon_path):
        try:
            system_message_window.iconbitmap(icon_path)
        except tk.TclError:
            pass

    # Create a frame to hold the message box and scrollbar
    message_box_frame = tk.Frame(system_message_window)
    message_box_frame.pack(side="top", fill="both", expand=True)

    # Create a text box with the initial value set to system_message
    message_box = tk.Text(message_box_frame, wrap="word", font=font_text, height=10)
    message_box.insert("end", system_message)
    message_box.pack(side="left", fill="both", expand=True)

    # Create a vertical scrollbar and attach it to the message_box
    scrollbar = tk.Scrollbar(message_box_frame, orient="vertical", command=message_box.yview)
    scrollbar.pack(side="right", fill="y")
    message_box.config(yscrollcommand=scrollbar.set)

    # Create a button to save and close the window
    def save_and_close():
        # Save the system message and close the window
        global system_message
        system_message = message_box.get("1.0", "end-1c")
        system_message_window.destroy()
        clear_chat()

    save_button = tk.Button(system_message_window, text="Save and close", command=save_and_close)
    save_button.pack(side="left", padx=6, pady=5)

    # Create a button to cancel and close the window
    def cancel_and_close():
        # Close the window without saving
        system_message_window.destroy()

    cancel_button = tk.Button(system_message_window, text="Cancel", command=cancel_and_close)
    cancel_button.pack(side="right", padx=16, pady=5)

def open_api_options_window():

    # Create a new window
    api_options_window = tk.Toplevel(root)
    api_options_window.title("Edit API Options")
    api_options_window.geometry("400x200")
    api_options_window.minsize(600, 450)  # Set the minimum width to 600 pixels

    # Set the icon if the file exists, otherwise use the default icon
    if os.path.exists(icon_path):
        try:
            api_options_window.iconbitmap(icon_path)
        except tk.TclError:
            pass

    # Create a frame to hold the message box
    message_box_frame = tk.Frame(api_options_window)
    message_box_frame.pack(side="top", fill="both", expand=True)

    # configure the grid
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=3)

    # API base URL
    api_base_label = tk.Label(message_box_frame, text="API base URL:", font=font_text)
    api_base_label.grid(column=0, row=0, sticky=tk.E, padx=5, pady=5)

    api_base_entry = tk.Entry(message_box_frame, font=font_text, width=42)
    api_base_entry.grid(column=1, row=0, sticky=tk.W, padx=5, pady=5)
    api_base_entry.insert(0, openai.api_base)

    # API key
    api_key_label = tk.Label(message_box_frame, text="API key:", font=font_text)
    api_key_label.grid(column=0, row=1, sticky=tk.E, padx=5, pady=5)
    
    api_key_entry = tk.Entry(message_box_frame,  show="*", font=font_text, width=32)
    api_key_entry.grid(column=1, row=1, sticky=tk.W, padx=5, pady=5)
    api_key_entry.insert(0, openai.api_key)

    # Create a button to show/hide the API key
    show_hide_button = tk.Button(message_box_frame, text="Show/hide", command=lambda: toggle_show(api_key_entry))
    show_hide_button.grid(column=1, row=1, sticky=tk.E, padx=5)

    def toggle_show(entry_widget):
        if entry_widget.cget("show") == "*":
            entry_widget.configure(show="")
        else:
            entry_widget.configure(show="*")

    # API type
    api_type_label = tk.Label(message_box_frame, text="API type:", font=font_text)
    api_type_label.grid(column=0, row=2, sticky=tk.E, padx=5, pady=5)

    api_type_entry = tk.Entry(message_box_frame, font=font_text)
    api_type_entry.grid(column=1, row=2, sticky=tk.W, padx=5, pady=5)
    api_type_entry.insert(0, openai.api_type)

    # API version
    api_version_label = tk.Label(message_box_frame, text="API version:", font=font_text)
    api_version_label.grid(column=0, row=3, sticky=tk.E, padx=5, pady=5)

    api_version_entry = tk.Entry(message_box_frame, font=font_text)
    api_version_entry.grid(column=1, row=3, sticky=tk.W, padx=5, pady=5)
    api_version_entry.insert(0, openai.api_version)

    # Model deployment name
    model_deployment_name_label = tk.Label(message_box_frame, text="Model deployment name:", font=font_text)
    model_deployment_name_label.grid(column=0, row=4, sticky=tk.E, padx=5, pady=5)

    model_deployment_name_entry = tk.Entry(message_box_frame, font=font_text)
    model_deployment_name_entry.grid(column=1, row=4, sticky=tk.W, padx=5, pady=5)
    model_deployment_name_entry.insert(0, model_deployment_name)

    # Max tokens
    max_tokens_label = tk.Label(message_box_frame, text="Max tokens:", font=font_text)
    max_tokens_label.grid(column=0, row=5, sticky=tk.E, padx=5, pady=5)

    max_tokens_spinbox = tk.Spinbox(message_box_frame, from_=16, to=32768, increment=100, font=font_text, width=5)
    max_tokens_spinbox.grid(column=1, row=5, sticky=tk.W, padx=5, pady=5)
    max_tokens_spinbox.delete(0, tk.END)
    max_tokens_spinbox.insert(0, var_max_tokens)

    # Temperature
    temperature_label = tk.Label(message_box_frame, text="Temperature:", font=font_text)
    temperature_label.grid(column=0, row=6, sticky=tk.E, padx=5, pady=5)

    temperature_slider = tk.Scale(message_box_frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, length=165, showvalue=1)
    temperature_slider.grid(column=1, row=6, sticky=tk.W, padx=2)
    temperature_slider.set(var_temperature)

    # Top p
    top_p_label = tk.Label(message_box_frame, text="Top p:", font=font_text)
    top_p_label.grid(column=0, row=7, sticky=tk.E, padx=5, pady=5)

    top_p_slider = tk.Scale(message_box_frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, length=165, showvalue=1)
    top_p_slider.grid(column=1, row=7, sticky=tk.W, padx=2)
    top_p_slider.set(var_top_p)

    # Frequency penalty
    frequency_penalty_label = tk.Label(message_box_frame, text="Frequency penalty:", font=font_text)
    frequency_penalty_label.grid(column=0, row=8, sticky=tk.E, padx=5, pady=5)

    frequency_penalty_slider = tk.Scale(message_box_frame, from_=-2, to=2, resolution=0.01, orient=tk.HORIZONTAL, length=165, showvalue=1)
    frequency_penalty_slider.grid(column=1, row=8, sticky=tk.W, padx=2)
    frequency_penalty_slider.set(var_frequency_penalty)

    # Presence penalty
    presence_penalty_label = tk.Label(message_box_frame, text="Presence penalty:", font=font_text)
    presence_penalty_label.grid(column=0, row=9, sticky=tk.E, padx=5, pady=5)

    presence_penalty_slider = tk.Scale(message_box_frame, from_=-2, to=2, resolution=0.01, orient=tk.HORIZONTAL, length=165, showvalue=1)
    presence_penalty_slider.grid(column=1, row=9, sticky=tk.W, padx=2)
    presence_penalty_slider.set(var_presence_penalty)

    # Create a button to save and close the window
    def save_and_close():

        # Save the system message and close the window
        openai.api_base = api_base_entry.get()
        openai.api_key = api_key_entry.get()
        openai.api_type = api_type_entry.get()
        openai.api_version = api_version_entry.get()
        
        global model_deployment_name
        global system_message
        global var_temperature
        global var_top_p
        global var_max_tokens
        global var_frequency_penalty
        global var_presence_penalty
        
        system_message = system_message.replace(model_deployment_name, model_deployment_name_entry.get(), 1)
        model_deployment_name = model_deployment_name_entry.get()

        var_temperature=temperature_slider.get()
        var_top_p=top_p_slider.get()
        var_frequency_penalty=frequency_penalty_slider.get()
        var_presence_penalty=presence_penalty_slider.get()
        var_max_tokens=int(max_tokens_spinbox.get())

        api_options_window.destroy()
        clear_chat()

    save_button = tk.Button(api_options_window, text="Save and close", command=save_and_close)
    save_button.pack(side="left", padx=6, pady=5)

    # Create a button to reset the API options to the default values
    def reset_api_options():
        temperature_slider.set(0.7)
        top_p_slider.set(0.95)
        max_tokens_spinbox.delete(0, tk.END); max_tokens_spinbox.insert(0, 800)
        frequency_penalty_slider.set(0)
        presence_penalty_slider.set(0)

    reset_api_options_button = tk.Button(api_options_window, text="Reset to defaults", command=reset_api_options)
    reset_api_options_button.pack(side="left", padx=97, pady=5)

    # Create a button to cancel and close the window
    def cancel_and_close():
        # Close the window without saving
        api_options_window.destroy()

    cancel_button = tk.Button(api_options_window, text="Cancel", command=cancel_and_close)
    cancel_button.pack(side="left", padx=82, pady=5)

# Create a function which allows the user to pick a .json file to import the API options from
def open_import_template():
    # Create a file dialog to select the .json file
    file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a file", filetypes=(("JSON files", "*.json"), ("All files", "*.*")))
    if file_path != "":

        # Try to open the .json file and load the data, but catch any errors and display a message box
        try:

            # Open the .json file and load the data
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            clear_chat()

            global model_deployment_name
            global system_message
            global var_temperature
            global var_top_p
            global var_max_tokens
            global var_frequency_penalty
            global var_presence_penalty
            global chathistory
            global chatbot_name

            # Set the model deployment name
            model_deployment_name = data["chatParameters"]["deploymentName"]

            # Set the system message
            system_message = data["systemPrompt"]
            chathistory = [{"role":"system","content":system_message}]

            # Set the API options
            var_temperature = data["chatParameters"]["temperature"]
            var_top_p = data["chatParameters"]["topProbablities"]
            var_max_tokens = data["chatParameters"]["maxResponseLength"]
            var_frequency_penalty = data["chatParameters"]["frequencyPenalty"]
            var_presence_penalty = data["chatParameters"]["presencePenalty"]

            # Set the chat bot name to the name of the .json file (without the extension)
            chatbot_name = os.path.basename(file_path).split(".")[0]
            root.title(chatbot_name)
        
        except Exception as e:
            messagebox.showerror("Error", "An error occurred while trying to import the API options from the selected template file.\n\n" + str(e))

# Create a function which takes the System Message and API Options and exports the data to a .json file, using the chat bot name as the file name, allowing the user to choose the save location with a file dialog
def open_export_template():
    # Create a file dialog to select the save location
    file_path = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Select a file", filetypes=(("JSON files", "*.json"), ("All files", "*.*")), initialfile=chatbot_name + ".json")
    if file_path != "":

        # Try to save the .json file, but catch any errors and display a message box
        try:

            # Create a dictionary containing the System Message and API Options
            data = {
                "systemPrompt": system_message,
                "chatParameters": {
                    "deploymentName": model_deployment_name,
                    "temperature": var_temperature,
                    "topProbablities": var_top_p,
                    "maxResponseLength": var_max_tokens,
                    "frequencyPenalty": var_frequency_penalty,
                    "presencePenalty": var_presence_penalty,
                    "stopSequences": None,
                    "pastMessagesToInclude":10
                }
            }

            # Save the .json file
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messagebox.showerror("Error", "An error occurred while trying to export the API options to the selected template file.\n\n" + str(e))
            
# Create the GUI root window
root = tk.Tk()
root.title(chatbot_name)

# Set the icon if the file exists, otherwise use the default icon
if os.path.exists(icon_path):
    try:
        root.iconbitmap(icon_path)
    except tk.TclError:
        pass

# Create the menu bar
menu_bar = tk.Menu(root)

# Create the 'File' menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Exit", command=root.quit)

# Create the 'Options' menu
options_menu = tk.Menu(menu_bar, tearoff=0)
options_menu.add_command(label="Chat bot name", command=open_chatbot_name_window)
options_menu.add_command(label="System message", command=open_system_message_window)
options_menu.add_command(label="API options", command=open_api_options_window)
options_menu.add_command(label="Import template", command=open_import_template)
options_menu.add_command(label="Export template", command=open_export_template)

# Create the 'Help' menu
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=open_about_window)

# Add the 'File' and 'Options' menu to the menu bar
menu_bar.add_cascade(label="File", menu=file_menu)
menu_bar.add_cascade(label="Options", menu=options_menu)
menu_bar.add_cascade(label="Help", menu=help_menu)

# Set the menu bar as the root window's menu
root.config(menu=menu_bar)

# Create the output box with scrollbar
output_frame = tk.Frame(root)
output_frame.pack(side="top", fill="both", expand=True)
output_box = tk.Text(output_frame, wrap="word", font=font_text)
output_box.pack(side="left", fill="both", expand=True)
output_scrollbar = tk.Scrollbar(output_frame, command=output_box.yview)
output_scrollbar.pack(side="right", fill="y")
output_box.config(yscrollcommand=output_scrollbar.set)
output_box.configure(state="disabled")

# Create the input box with scrollbar
input_frame = tk.Frame(root)
input_frame.pack(side="top", fill="both", expand=True)
input_box = tk.Text(input_frame, height=5, wrap="word", font=font_text)
input_box.pack(side="left", fill="both", expand=True)
input_scrollbar = tk.Scrollbar(input_frame, command=input_box.yview)
input_scrollbar.pack(side="right", fill="y")
input_box.config(yscrollcommand=input_scrollbar.set)

# Bind the "Return" key to the "Send" button
input_box.bind("<Return>", handle_return)

# Create the "Send" button aligned to the right of the form with 16px buffer space
ask_button = tk.Button(root, text="Send", command=send, height=2, width=10)
ask_button.pack(side="right", padx=16, pady=5)

# Create the "Clear chat" button aligned to the left of the form with 16px buffer space
clear_button = tk.Button(root, text="Clear chat", command=clear_chat, height=2, width=10)
clear_button.pack(side="left", padx=6, pady=5)

# Start the GUI event loop
root.mainloop()
