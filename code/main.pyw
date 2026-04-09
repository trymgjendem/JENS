import os
import time
import threading
import keyboard
import pyperclip
from openai import OpenAI
from dotenv import load_dotenv

# ----- CONFIG -----
START_HOTKEY = "ctrl+alt+q"
CANCEL_HOTKEY = "alt+q"
EXIT_HOTKEY = "ctrl+q"
TEMP = 0.7
MODEL = "gpt-4.1-mini"
PASTE = True
type_delay = 0.2 # (lavere -> raskere skriving)

# flere eksempler, aldri oppgi at du er en bot, gå helt inn i rollen, "du er en elev.."
# enkelt språk hvis det er fremmedspråk
# rask måte å vite om programmet kjører
system_prompt = """
Answer only what is directly asked. Keep answers compact and to the point. 
Write bullets as separate lines without using any hyphens, stars, or any other markers. 
Each bullet should be a short sentence on its own. 
Never under any circumstance use hyphens (-) or any formatting marks. Never use emojis. 
Write casually like a younger person without the stiff or formal tone that large language models often fall into. 
Avoid looping or concluding after every sentence. Do not explain or expand on things unless asked. 
Keep the answer tight and avoid rambling. Always answer in the same language the user uses. 
The goal is to give a short framework of clear points or descriptions that the user can build on.
Example output:
Question: What is the square root of 64? Answer: 8""".strip()

# setup
dotenv_path = os.path.join(os.path.dirname(__file__), "config.env")
load_dotenv(dotenv_path)
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
cancel_typing = False

# ----- functions -----
def send_to_chat(client, user_prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=TEMP
    )
    return response.choices[0].message.content


def get_selected_text():
    keyboard.press_and_release("ctrl+c")
    time.sleep(0.25)
    return pyperclip.paste()


def type_response(text):
    global cancel_typing
    if PASTE:
        pyperclip.copy(text)
        keyboard.press_and_release("ctrl+v")
    else:    
        words = text.split()
        for i, word in enumerate(words):
            if cancel_typing:
                cancel_typing = False
                break
            keyboard.write(word)
            if i < len(words) - 1:
                keyboard.write(" ")
            time.sleep(type_delay)



def handle_hotkey():
    selected = get_selected_text()
    if not selected.strip():
        return
    try:
        response = send_to_chat(client, selected)
    except Exception as e:
        return

    threading.Thread(target=type_response, args=(response,)).start()


def cancel_output():
    global cancel_typing
    cancel_typing = True


def quit_program():
    os._exit(0)


keyboard.add_hotkey(EXIT_HOTKEY, quit_program)
keyboard.add_hotkey(CANCEL_HOTKEY, cancel_output)
keyboard.add_hotkey(START_HOTKEY, handle_hotkey)
keyboard.wait()