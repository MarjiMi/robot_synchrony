from itertools import cycle
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pandas as pd
import os

# Global variables
participant_number = ""
obstacles = ['EASY', 'MEDIUM', 'HARD'] * 10  # Initialize with 30 obstacles
obstacle_type = ""
result = []  # Store participant choices
global obstacle_count
obstacle_count = 0  # Keep track of the obstacle count

def update_instructions(obstacle_type):
    instructions_text.config(state=tk.NORMAL)  # Enable editing temporarily
    instructions_text.delete("1.0", tk.END)
    instructions_text.insert("1.0", "\n\n\n\n\nHow much do you trust the robotic arm to successfully complete a ")
    if obstacle_type == "EASY":
        instructions_text.insert(tk.END, obstacle_type, "green")
        instructions_text.tag_configure("green", foreground="green", font=("Helvetica", 22))
    elif obstacle_type == "MEDIUM":
        instructions_text.insert(tk.END, obstacle_type, "orange")
        instructions_text.tag_configure("orange", foreground="orange", font=("Helvetica", 22))
    else:
        instructions_text.insert(tk.END, obstacle_type, "red")
        instructions_text.tag_configure("red", foreground="red", font=("Helvetica", 22))
    instructions_text.insert(tk.END, " obstacle course?")
    instructions_text.tag_add("center", "1.0", "end")
    instructions_text.config(state=tk.DISABLED)  # Disable editing

def submit_participant_number():
    global participant_number
    participant_number = participant_number_entry.get()
    participant_number_label.pack_forget()
    participant_number_entry.pack_forget()
    submit_button.pack_forget()

    for button in [option1_button, option2_button, option3_button, option4_button, option5_button, option6_button]:
        button.config(font=("Helvetica", 22), width=8, height=2)
        button.pack(side=tk.LEFT, padx=6, pady=6)
        #button.pack(side=tk.LEFT, padx=5)

    next_obstacle()

def update_image(label, frames, frame_index=0):
    try:
        frame = next(frames)  # Get the next frame of the gif
        label.configure(image=frame)  # Update the label with the next frame
        root.after(50, update_image, label, frames)  # Continue looping every 50 ms
    except StopIteration:
        pass  # Handle the end of the gif frames gracefully

def start_animation(gif_path, label):
    frames = []
    frame_count = 0
    while True:
        try:
            photo = tk.PhotoImage(file=gif_path, format=f"gif -index {frame_count}")
            frames.append(photo)
            frame_count += 1
        except tk.TclError:
            break
    cycle_frames = cycle(frames)
    update_image(label, cycle_frames)

def configure_buttons(buttons, states):
    for button, state in zip(buttons, states):
        button.config(state=state)

def next_obstacle():
    global obstacle_type
    reset_button_styles()
    if obstacles:
        obstacle_type = obstacles.pop(0)
        #Update the instructions and obstacle type
        update_instructions(obstacle_type)
        option1_button.config(state=tk.NORMAL, text="0% Trust", font=("Helvetica", 20))
        option2_button.config(state=tk.NORMAL, text="20%", font=("Helvetica", 20))
        option3_button.config(state=tk.NORMAL, text="40%", font=("Helvetica", 20))
        option4_button.config(state=tk.NORMAL, text="60%", font=("Helvetica", 20))
        option5_button.config(state=tk.NORMAL, text="80%", font=("Helvetica", 20))
        option6_button.config(state=tk.NORMAL, text="100% Trust", font=("Helvetica", 20))
        obstacles_left_progress_bar["value"] = total_obstacles - len(obstacles)
    else:
        finish_game()

def choose_option(option):
    global obstacle_count  # Make sure to use global variables
    reset_button_styles()
    buttons = [option1_button, option2_button, option3_button, option4_button, option5_button, option6_button]
    selected_button = buttons[option]
    selected_button.config(bg='blue', fg='white')
    # Disable all option buttons
    for btn in buttons:
        btn.config(state=tk.DISABLED)
    result.append(option) # Store the participant's choice
    
    process_label.config(text="Checking results...", fg="blue", font=("Helvetica", 24))
    process_label.pack()
    gif_label.pack()
    progress_bar["value"] = 0
    progress_bar.pack()
    update_progress_bar(obstacle_type)
    wait_times = {"EASY": 3000, "MEDIUM": 4000, "HARD": 5000}
    wait_time = wait_times.get(obstacle_type, 5000)
    
    # Debug prints
    print(f"Obstacle count before increment: {obstacle_count}")
    
    # Check if it's the 9th, 18th, or 30th trial
    if obstacle_count == 8:
        print("9th obstacle reached")
        root.after(5000, lambda: show_result_label("The robotic arm SUCCEEDED!", "green"))
    elif obstacle_count == 17:
        print("18th obstacle reached")
        root.after(5000, lambda: show_result_label("The robotic arm FAILED", "red"))
    elif obstacle_count == 29:
        print("30th obstacle reached")
        root.after(5000, show_thank_you_message)
    else:
        root.after(wait_time, lambda: show_result_label("Done!", "Dark Blue"))

    obstacle_count += 1  # Increment the obstacle count only once
    print(f"Obstacle count after increment: {obstacle_count}")


def update_progress_bar(obstacle_type):
    progress_increments = {"EASY": 10, "MEDIUM": 8, "HARD": 6}
    progress_bar["value"] += progress_increments.get(obstacle_type, 6)
    if progress_bar["value"] < progress_bar["maximum"]:
        root.after(300, update_progress_bar, obstacle_type)
    else:
        progress_bar.pack_forget()
        gif_label.pack_forget()

def hide_process_label():
    process_label.pack_forget()
    progress_bar.pack_forget()
    next_obstacle()

def hide_result_label():
    result_label.pack_forget()
    next_obstacle()

def show_result_label(text, color):
    progress_bar.pack_forget()
    process_label.pack_forget()
    result_label.config(text=text, fg=color, font=("Helvetica", 40))
    result_label.pack()
    result_label.pack(side=tk.TOP, pady=22)  # Ensure the result label appears above the trust buttons
    root.after(3000 if text == "Done!" else 5000, hide_result_label)

def show_thank_you_message():
    process_label.pack_forget()
    messagebox.showinfo("Thank you!", "You have completed this task. Please let the researcher know you are ready for next steps.")
    root.after(5000, finish_game)

def finish_game():
    print("Finishing game and saving data...")
    save_data()
    print("Data saved successfully.")
    root.quit()  # This ensures the Tkinter main loop is exited

def save_data():
    data = {"participant_number": participant_number}
    for i, choice in enumerate(result):
        data[f"obstacle {i + 1}"] = choice
    df = pd.DataFrame(data, index=[0])

    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')

    data_csv = os.path.join(desktop_path, 'data.csv')

    file_exists = os.path.isfile(data_csv)
    df.to_csv(data_csv, mode='a', header=not file_exists, index=False)

    # Debug print
    print("DataFrame to be saved:")
    print(df)
    print(f"Data saved to {data_csv}")


def reset_button_styles():
    for btn in [option1_button, option2_button, option3_button, option4_button, option5_button, option6_button]:
        btn.config(bg='gray85', fg='black')

# GUI setup
root = tk.Tk()
root.title("Obstacle Course Task")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - 1000) // 4
y = (screen_height - 600) // 4
root.geometry("1000x600")
root.geometry("+{}+{}".format(x, y))

instructions_text = tk.Text(root, font=("Helvetica", 24), wrap=tk.WORD, borderwidth=1, relief="solid", width=5, height=5)
instructions_text.tag_configure("center", justify='center', font=("Helvetica", 22))
instructions = """Now, you will play a game with the robotic arm you just worked with. 
Pay attention carefully, because your decisions will affect how much money you will win. 
The robotic arm moved through several obstacle courses earlier today.
The robotic arm moved toy balls to the other side of the table, but this time with obstacles in the way.
Each obstacle course had a difficulty of easy, medium, or hard. 
For easy obstacle courses, the robotic arm moved around one obstacle, for medium, 2 obstacles, and for hard, 3 obstacles. 
In this game, you will rate your level of trust that the robotic arm completed the course without hitting any obstacles from 0% trust to 100% trust.
If you are correct, easy obstacles will win you up to $0.25, medium obstacles will win you up to $0.50, and hard obstacles $1.00.
The level of trust you have in the robotic arm will relate directly to your reward.
That means, if you have high trust in the robotic arm and it succeeds, you will win more money.
If you have low trust in the robotic arm and it fails, you will win more money.
However, if you have low trust in the robotic arm and it succeeds, you will win less money, and vice versa.
You will get feedback about whether the robotic arm succeeded for two random hard obstacles."""
instructions_text.insert("1.0", instructions, "center")
instructions_text.config(state=tk.DISABLED)
scrollbar = tk.Scrollbar(root, command=instructions_text.yview)
instructions_text['yscrollcommand'] = scrollbar.set
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
instructions_text.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

participant_number_label = tk.Label(root, text="Enter Participant Number:", font=("Helvetica", 20))
participant_number_label.pack(padx=5, pady=5)
participant_number_entry = tk.Entry(root)
participant_number_entry.pack(padx=5, pady=5)
submit_button = tk.Button(root, text="Submit", command=submit_participant_number)
submit_button.pack(pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=20)
option1_button = tk.Button(button_frame, text="0%", state=tk.DISABLED, command=lambda: choose_option(0))
option2_button = tk.Button(button_frame, text="20%", state=tk.DISABLED, command=lambda: choose_option(1))
option3_button = tk.Button(button_frame, text="40%", state=tk.DISABLED, command=lambda: choose_option(2))
option4_button = tk.Button(button_frame, text="60%", state=tk.DISABLED, command=lambda: choose_option(3))
option5_button = tk.Button(button_frame, text="80%", state=tk.DISABLED, command=lambda: choose_option(4))
option6_button = tk.Button(button_frame, text="100%", state=tk.DISABLED, command=lambda: choose_option(5))

process_label = tk.Label(root, text="", font=("Helvetica"))
result_label = tk.Label(root, text="", font=("Helvetica"))
thank_you_label = tk.Label(root, text="", font=("Helvetica"))

style = ttk.Style(root)
style.theme_use('default')
total_obstacles = len(obstacles)
style.configure("Orange.Horizontal.TProgressbar", troughcolor='white', background='#F6B979', thickness=12)
obstacles_left_progress_bar = ttk.Progressbar(root, style="Orange.Horizontal.TProgressbar", orient="horizontal", length=300, mode="determinate", maximum=total_obstacles)
obstacles_left_progress_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
style.configure("Blue.Horizontal.TProgressbar", troughcolor='white', background='#6FA8DC', thickness=5)
progress_bar = ttk.Progressbar(root, style="Blue.Horizontal.TProgressbar", orient="horizontal", length=300, mode="determinate", maximum=100)
robotic_arm_gif_path = "robotic_arm.gif"
gif_label = tk.Label(root)
start_animation(robotic_arm_gif_path, gif_label)

root.mainloop()
