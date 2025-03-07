from psychopy import visual, core, event
import pandas as pd
import random
import os

# Load Stimuli
stimuli_file = "stimuli_finalized.xlsx"
df = pd.read_excel(stimuli_file)
df = df.dropna(how="all").reset_index(drop=True)

# Practice Stimuli
practice_stimuli = pd.DataFrame({
    "context": ["The river sparkled in the sunlight, its surface dotted with tiny bubbles. The light shimmered on the water, making it look bright and lively.", 
                "The lamp stood quietly in the corner, giving off a dim yellow glow. It flickered slightly as the evening grew darker.", 
                "The device rested on the desk, its buttons arranged in neat rows. The case felt cool to the touch.", 
                "The package looked perfectly wrapped and clean from the outside. Inside, the contents were broken and missing pieces.", 
                "The pool stretched out in the backyard, its water a deep blue. Leaves floated slowly along the edges of the surface.", 
                "His fingers glided across the paper, leaving smooth strokes behind. Every movement traced soft lines in perfect shapes.", 
                "After rereading the letter, the meaning suddenly became clear. Everything else fell into place like pieces of a puzzle."],
    
    "stimulus": ["this river is champagne", 
                 "that lamp is a floor", 
                 "this device is a laptop", 
                 "appearance is a deceiver", 
                 "this pool is a mirror", 
                 "his hand is brush", 
                 "understanding is a key"],
    
    "stimulus_type": ["novel_metaphor", 
                      "anomalous", 
                      "conventional_metaphor", 
                      "novel_metaphor", 
                      "conventional_metaphor", 
                      "novel_metaphor", 
                      "conventional_metaphor"],
    
    "condition": ["meaningful", 
                  "meaningless", 
                  "meaningful", 
                  "meaningful", 
                  "meaningful", 
                  "meaningful", 
                  "meaningful"]
})

# Remove practice items from main list
df = df[~df["stimulus"].isin(practice_stimuli["stimulus"])].reset_index(drop=True)

# Window Setup
win = visual.Window(fullscr=True, color="white", units="pix")
text_stim = visual.TextStim(win, text="", color="black", height=40, wrapWidth=1000)
fixation = visual.TextStim(win, text="+", color="black", height=60)
progress_bar = visual.Rect(win, width=500, height=20, fillColor="black", pos=(0, -300))

# CSV Setup
data_file = "experiment_data.csv"
if not os.path.exists(data_file):
    with open(data_file, "w") as f:
        f.write("participant,language_group,context,stimulus,stimulus_type,condition,response,accuracy,response_time,key_mapping\n")

try:
    with open(data_file, "r") as f:
        last_line = f.readlines()[-1]
        participant_number = int(last_line.split(",")[0]) + 1
except:
    participant_number = 1

# Language Group Selection
text_stim.text = "Do you speak English as your FIRST language (L1) or SECOND language (L2)?\nPress '1' for L1\nPress '2' for L2"
text_stim.draw()
win.flip()
lang_key = event.waitKeys(keyList=["1", "2"])[0]
language_group = "L1" if lang_key == "1" else "L2"

# Welcome & Instructions
intro_text = (
    "Welcome to the experiment!\n\n"
    "In this study, you will read short descriptions followed by phrases. Your task is to decide whether each phrase is meaningful or meaningless in the given context.\n\n"
    "It is important to respond as quickly and accurately as possible.\n\n"
    "There will be self-paced breaks every 10 trials throughout the experiment, so please use as much time as you need to rest so that you can maintain focus.\n\n"

    "Press SPACE to continue."
)
text_stim.text = intro_text
text_stim.draw()
win.flip()
event.waitKeys(keyList=["space"])

#More instructions
text_stim.text = (
    "Here’s how the experiment will proceed:\n\n"
	"1.	You will first read a short context sentence or two sentences on the screen. Then, press SPACE to proceed.\n\n"
	"2.	A fixation cross (+) will appear to help you focus on the screen.\n\n"
	"3.	Next, the target phrase will be shown word by word.\n\n"
	"4.	Once the entire phrase is presented, you will have up to 2 seconds to decide whether the phrase is meaningful or meaningless to you.\n\n"

    "Press SPACE to continue."
)
text_stim.draw()
win.flip()
event.waitKeys(keyList=["space"])

# Risks and Discomforts
text_stim.text = (
    "Some phrases may seem unusual or difficult to understand.\n\n"
    "If you feel uncomfortable or tired, you may withdraw at any time.\n\n"
    "Press SPACE to continue."
)
text_stim.draw()
win.flip()
event.waitKeys(keyList=["space"])


# Key Assignment
key_mapping = random.choice([{"d": "meaningful", "k": "meaningless"}, {"k": "meaningful", "d": "meaningless"}])
text_stim.text = (
    f"Key Assignment:\n\n'D' = {key_mapping['d'].upper()}\n'K' = {key_mapping['k'].upper()}\n\n"
    "Press SPACE to continue."
)
text_stim.draw()
win.flip()
event.waitKeys(keyList=["space"])


# Countdown
def countdown():
    for count in [3, 2, 1]:
        text_stim.text = str(count)
        text_stim.draw()
        win.flip()
        core.wait(1)

# Trial Function
def run_trial(row, trial_num, total_trials, record_data=True):
    # Present context sentence
    text_stim.text = row["context"]
    text_stim.draw()
    win.flip()
    event.waitKeys(keyList=["space"])  # Wait for participant to proceed
    
    # Fixation cross with jittered duration
    fixation.draw()
    win.flip()
    core.wait(random.uniform(1.0, 2.0))
    
    # Present each word for 500 ms
    words = row["stimulus"].split()
    for word in words:
        text_stim.text = word
        text_stim.draw()
        win.flip()
        core.wait(0.5)
    
    # Response window
    win.color = "white"
    win.flip()
    response = None
    rt = None
    response_clock = core.Clock()
    
    while response_clock.getTime() < 2.0:
        keys = event.getKeys(keyList=["d", "k", "escape"], timeStamped=response_clock)
        if keys:
            response, rt = keys[0]
            win.color = "gray"
            win.flip()
            core.wait(random.uniform(1.0, 2.0))
            break

    # If no response is made within the 2s window
    if response is None:
        text_stim.text = "Please respond faster next time."
        text_stim.draw()
        win.color = "gray"
        win.flip()
        core.wait(3)
        accuracy = 0
    else:
        stimulus_type = row["stimulus_type"]
        correct_answer = "d" if key_mapping["d"] == "meaningful" and stimulus_type in ["novel metaphor", "conventional metaphor", "literal sentence"] else "k"
        accuracy = int(response == correct_answer)
    
    # Data Cleaning for CSV
    context_clean = row["context"].replace(",", ";")
    stimulus_clean = row["stimulus"].replace(",", ";")
    key_map_str = f"D = {key_mapping['d']}, K = {key_mapping['k']}"
    response = response if response else "NA"
    rt = rt if rt else "NA"
    accuracy = accuracy if response != "NA" else "NA"
    
    # Data Writing
    if record_data:
        with open(data_file, "a") as f:
            f.write(f"{participant_number},{language_group},{context_clean},{stimulus_clean},{row['stimulus_type']},{row['condition']},{response},{accuracy},{rt},{key_map_str}\n")


# Breaks
def self_paced_break(trial_num, total_trials):
    if trial_num % 10 == 0 and trial_num != total_trials:
        progress = (trial_num / total_trials) * 100
        text_stim.text = f"Take a short break!\n\nYou have completed {int(progress)}%.\nPress SPACE to continue."
        progress_bar.width = 500 * (trial_num / total_trials)
        progress_bar.draw()
        text_stim.draw()
        win.flip()
        event.waitKeys(keyList=["space"])

# Randomization Function
def create_randomized_trials(df):
    buffer_min = 20
    pairs = {}
    fillers = []

    # Group Pairs
    for _, row in df.iterrows():
        if "single" in row["stimulus_type"] or "extended" in row["stimulus_type"]:
            target = row["stimulus"].split()[0]
            pairs.setdefault(target, []).append(row)
        else:
            fillers.append(row)

    # Randomize Fillers
    random.shuffle(fillers)
    final_trials = []
    used_stimuli = set()

    # Place Pairs with Buffer
    while pairs:
        target, pair = pairs.popitem()
        random.shuffle(pair)
        final_trials.append(pair[0])
        used_stimuli.add(pair[0]["stimulus"])

        # Buffer Enforcement
        buffer_trials = fillers[:buffer_min]
        final_trials.extend(buffer_trials)
        fillers = fillers[buffer_min:]

        # Place Second Item
        if len(pair) > 1:
            final_trials.append(pair[1])
            used_stimuli.add(pair[1]["stimulus"])

    # Add Remaining Fillers
    final_trials.extend(fillers)
    return pd.DataFrame(final_trials)

# Practice Trials
text_stim.text = "Let's begin with practice trials.\nPress SPACE to continue."
text_stim.draw()
win.flip()
event.waitKeys(keyList=["space"])
countdown()
for trial_num, (_, row) in enumerate(practice_stimuli.iterrows(), start=1):
    run_trial(row, trial_num, len(practice_stimuli), record_data=False)

# Main Trials
text_stim.text = "Practice complete.\nPress SPACE to start the main experiment."
text_stim.draw()
win.flip()
event.waitKeys(keyList=["space"])

df_randomized = create_randomized_trials(df)

countdown()
total_trials = len(df_randomized)
for trial_num, (_, row) in enumerate(df_randomized.iterrows(), start=1):
    run_trial(row, trial_num, total_trials)
    self_paced_break(trial_num, total_trials)

# Goodbye
text_stim.text = "Thank you for your participation! Please, notify the researcher about the completion of the experiment.\nPress ESC to exit."
text_stim.draw()
win.flip()
event.waitKeys(keyList=["escape"])
win.close()
core.quit()