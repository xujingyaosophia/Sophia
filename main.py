import re
import tkinter as tk
from tkinter import scrolledtext, ttk
import random
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(SCRIPT_DIR, "score_history.json")

TASK_1_PROMPTS = [
    {
        "text": "The chart below shows the number of men and women in further education in Britain in three periods and whether they were studying full-time or part-time. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "type": "bar_chart",
        "data": {
            "title": "Further Education in Britain (in thousands)",
            "x_labels": ["1970/71", "1980/81", "1990/91"],
            "series": [
                {"name": "Men (Part-time)", "values": [1000, 850, 900], "color": "#4e79a7"},
                {"name": "Women (Part-time)", "values": [800, 950, 1100], "color": "#f28e2b"},
                {"name": "Men (Full-time)", "values": [180, 250, 200], "color": "#e15759"},
                {"name": "Women (Full-time)", "values": [150, 220, 250], "color": "#76b7b2"}
            ]
        }
    },
    {
        "text": "The graph below shows radio and television audiences throughout the day in 1992. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "type": "line_graph",
        "data": {
            "title": "UK Audiences, Oct-Dec 1992 (% over age 4)",
            "x_labels": ["6am", "8am", "10am", "12pm", "2pm", "4pm", "6pm", "8pm", "10pm", "12am", "2am", "4am"],
            "series": [
                {"name": "Radio", "values": [8, 28, 18, 15, 12, 13, 8, 5, 4, 2, 1, 1], "color": "#59a14f"},
                {"name": "Television", "values": [1, 5, 5, 3, 15, 25, 38, 45, 38, 10, 3, 2], "color": "#edc948"}
            ]
        }
    },
    {
        "text": "The diagram below shows the process by which bricks are manufactured for the building industry. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
        "type": "diagram",
        "data": {
            "title": "Brick Manufacturing Process",
            "steps": [
                {"label": "1. Dig Clay", "arrow_to": 1},
                {"label": "2. Metal Grid\n+ Roller", "arrow_to": 2},
                {"label": "3. Add Sand\n& Water", "arrow_to": 3},
                {"label": "4. Wire Cutter\nor Mould", "arrow_to": 4},
                {"label": "5. Drying Oven\n(24-48 hrs)", "arrow_to": 5},
                {"label": "6. Kiln (High Temp)", "arrow_to": 6},
                {"label": "7. Cooling Chamber\n(48-72 hrs)", "arrow_to": 7},
                {"label": "8. Packaging\n& Delivery", "arrow_to": None}
            ]
        }
    }
]

TASK_2_PROMPTS = [
    "Children who are brought up in families that do not have large amounts of money are better prepared to deal with the problems of adult life than children brought up by wealthy parents. To what extent do you agree or disagree with this opinion?",
    "International tourism has brought enormous benefit to many places. At the same time, there is concern about its impact on local inhabitants and the environment. Do the disadvantages of international tourism outweigh the advantages?",
    "A growing number of people feel that animals should not be exploited by people and that they should have the same rights as humans, while others argue that humans must employ animals to satisfy their various needs. Discuss both views and give your opinion.",
    "Government investment in the arts, such as music and theatre, is a waste of money. Governments must invest this money in public services instead. To what extent do you agree with this statement?",
    "In the last 20 years there have been significant developments in the field of information technology (IT). However, future developments in IT are likely to have more negative effects than positive. To what extent do you agree with this view?"
]

def load_score_history():
    """Loads score history from a JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_score_history(history_data):
    """Saves score history to a JSON file."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history_data, f, indent=4)

# This application is now fully self-contained and requires no external packages.

def assess_grammatical_range_and_accuracy(essay_text):
    """
    Assesses the grammatical range and accuracy of the essay with a simple regex-based checker.
    """
    errors = []
    a_an_errors = re.findall(r'\b(a\s+[aeiou]|an\s+[^aeiou\s])', essay_text, re.IGNORECASE)
    if a_an_errors:
        errors.append(f"Found {len(a_an_errors)} potential 'a/an' misuse(s) (e.g., '{a_an_errors[0]}').")

    sv_errors = re.findall(r'\b(he|she|it)\s+(are|have|go|do|run|write|read)\b', essay_text, re.IGNORECASE)
    if sv_errors:
        errors.append(f"Found {len(sv_errors)} potential subject-verb agreement issue(s) (e.g., '{sv_errors[0][0]} {sv_errors[0][1]}').")

    if "futhermore" in essay_text.lower():
        errors.append("Potential typo found: 'futhermore' should be 'furthermore'.")

    num_errors = len(errors)
    
    if num_errors == 0: score = 9.0
    elif num_errors == 1: score = 7.5
    elif num_errors <= 3: score = 6.0
    else: score = 5.0

    reason = f"Found {num_errors} potential grammatical issues."
    if num_errors == 0: reason = "No obvious grammatical errors found."
    if errors: reason += " Details: " + " ".join(errors)
    return score, reason

def assess_lexical_resource(essay_text):
    """
    Assesses the lexical resource of the essay using average word length.
    """
    words = re.findall(r'\b\w+\b', essay_text.lower())
    if not words: return 4.0, "The essay appears to be empty."
    avg_word_length = sum(len(word) for word in words) / len(words)
    
    if avg_word_length > 5.2: score = 9.0
    elif avg_word_length > 4.8: score = 8.0
    elif avg_word_length > 4.5: score = 7.0
    elif avg_word_length > 4.2: score = 6.0
    elif avg_word_length > 3.8: score = 5.0
    else: score = 4.0
        
    reason = f"The average word length is {avg_word_length:.2f}, which indicates vocabulary complexity."
    return score, reason

def assess_task_1_response(essay_text):
    """Assesses the task response for Task 1 (word count)."""
    word_count = len(re.findall(r'\b\w+\b', essay_text))
    if word_count < 120: return 4.0, f"Essay is too short ({word_count} words). Min 150 required."
    if word_count < 150: return 5.0, f"Essay is slightly short ({word_count} words). Aim for 150."
    if word_count <= 250: return 8.0, f"The essay has a suitable length of {word_count} words."
    return 7.0, f"The essay has a good length ({word_count} words), but ensure it remains concise."

def assess_task_2_response(essay_text):
    """Assesses the task response for Task 2 (word count)."""
    word_count = len(re.findall(r'\b\w+\b', essay_text))
    if word_count < 200: return 4.0, f"Essay is too short ({word_count} words). Min 250 required."
    if word_count < 250: return 5.0, f"Essay is slightly short ({word_count} words). Aim for 250."
    if word_count <= 350: return 8.0, f"The essay has a suitable length of {word_count} words."
    return 7.0, f"The essay has a good length ({word_count} words), but ensure it remains concise."

def assess_coherence_and_cohesion(essay_text):
    """Assesses the coherence and cohesion of the essay."""
    connectors = ['for example', 'in addition', 'moreover', 'however', 'on the other hand', 'therefore', 'as a result', 'in conclusion', 'firstly', 'secondly']
    lower_text = essay_text.lower()
    connector_count = sum(lower_text.count(c) for c in connectors)
    num_paragraphs = len(re.split(r'\n\s*\n', essay_text.strip()))
    
    points = 0
    if connector_count >= 5: points += 2
    elif connector_count >= 3: points += 1
    if 3 <= num_paragraphs <= 5: points += 2
    elif num_paragraphs > 1: points += 1

    scores = {4: 8.5, 3: 7.5, 2: 6.5, 1: 5.5}
    score = scores.get(points, 4.5)
    return score, f"Found {connector_count} connectors and {num_paragraphs} paragraphs."

def round_to_half(score):
    return round(score * 2) / 2

def score_essay(essay_text, task_type):
    """Scores an English essay based on IELTS criteria."""
    tr_func = assess_task_1_response if task_type == 1 else assess_task_2_response
    scores = [
        assess_grammatical_range_and_accuracy(essay_text),
        assess_lexical_resource(essay_text),
        tr_func(essay_text),
        assess_coherence_and_cohesion(essay_text)
    ]
    
    final_score = round_to_half(sum(s[0] for s in scores) / 4)
    reasons = {
        "grammatical_range_and_accuracy": scores[0][1],
        "lexical_resource": scores[1][1],
        "task_response": scores[2][1],
        "coherence_and_cohesion": scores[3][1]
    }
    return {"score": final_score, "reasons": reasons}

def update_total_score(scores_dict, total_score_label, status_label):
    """Updates the total score label based on the current scores in scores_dict."""
    task1_score = scores_dict.get('task1', 0)
    task2_score = scores_dict.get('task2', 0)

    if task1_score > 0 and task2_score > 0:
        weighted_score = (task1_score * 0.4) + (task2_score * 0.6)
        final_score = round_to_half(weighted_score)
        total_score_label.config(text=f"Overall IELTS Score: {final_score:.1f} / 9.0")
        status_label.config(text="👆 Preview score. Click 'Submit' below to record this attempt.", foreground="#007bff")
    else:
        total_score_label.config(text="Overall IELTS Score: N/A (Score both tasks to see total)")
        status_label.config(text="")

def display_results(result, result_widget):
    """Updates the result widget with the scoring results."""
    result_widget.config(state=tk.NORMAL)
    result_widget.delete('1.0', tk.END)
    result_widget.insert(tk.END, f"Overall Score: {result['score']:.1f}/9.0\n\n", "bold")
    result_widget.insert(tk.END, "Reasons:\n", "bold")
    for criterion, reason in result['reasons'].items():
        result_widget.insert(tk.END, f"• {criterion.replace('_', ' ').title()}: {reason}\n")
    result_widget.config(state=tk.DISABLED)

def on_submit_final_score_click(scores_dict, total_score_label, score_history_tree, score_history_data, attempt_counter, status_label):
    """Handles the 'Submit Final Score' button click."""
    task1_score = scores_dict.get('task1', 0)
    task2_score = scores_dict.get('task2', 0)
    
    if task1_score > 0 and task2_score > 0:
        weighted_score = (task1_score * 0.4) + (task2_score * 0.6)
        final_score = round_to_half(weighted_score)
        
        attempt_id = f"Attempt {attempt_counter[0]}"
        new_record = (attempt_id, f"{task1_score:.1f}", f"{task2_score:.1f}", f"{final_score:.1f}")
        
        score_history_data.append(new_record)
        score_history_tree.insert("", tk.END, values=new_record)
        score_history_tree.yview_moveto(1)
        
        save_score_history(score_history_data)
        
        attempt_counter[0] += 1
        
        scores_dict['task1'], scores_dict['task2'] = 0, 0
        
        update_total_score(scores_dict, total_score_label, status_label)
        status_label.config(text="✅ Score recorded! Ready for next attempt.", foreground="green")
        status_label.after(3000, lambda: status_label.config(text=""))
    else:
        status_label.config(text="⚠️ Please score both Task 1 and Task 2 first.", foreground="red")
        status_label.after(3000, lambda: status_label.config(text=""))

def on_score_button_click(essay_widget, result_widget, task_type, scores_dict, total_score_label, status_label):
    """Handles the score button click event."""
    essay = essay_widget.get('1.0', tk.END)
    result = score_essay(essay, task_type) if len(essay.strip()) >= 10 else {"score": 0.0, "reasons": {"Info": "Please enter an essay."}}
    display_results(result, result_widget)

    if result['score'] > 0:
        scores_dict[f'task{task_type}'] = result['score']
        update_total_score(scores_dict, total_score_label, status_label)

def draw_bar_chart(canvas, data):
    canvas.delete("all")
    width, height = 480, 220
    canvas.create_text(width/2, 10, text=data['title'], font=("Helvetica", 10, "bold"))
    
    max_val = max(max(s['values']) for s in data['series'])
    y_axis_height = height - 50
    x_axis_width = width - 60
    
    # Y-axis
    canvas.create_line(50, 20, 50, y_axis_height)
    for i in range(5):
        val = max_val * (1 - i/4)
        y = 20 + (i * (y_axis_height - 20) / 4)
        canvas.create_line(45, y, 50, y)
        canvas.create_text(35, y, text=f"{val:.0f}", anchor=tk.E)
        
    # X-axis
    canvas.create_line(50, y_axis_height, width-10, y_axis_height)
    
    num_groups = len(data['x_labels'])
    num_series = len(data['series'])
    group_width = x_axis_width / num_groups
    bar_width = (group_width * 0.8) / num_series
    
    for i, label in enumerate(data['x_labels']):
        group_x = 50 + (i * group_width)
        canvas.create_text(group_x + group_width/2, y_axis_height + 10, text=label)
        for j, series in enumerate(data['series']):
            bar_x1 = group_x + (group_width * 0.1) + (j * bar_width)
            bar_y1 = y_axis_height - (series['values'][i] / max_val * (y_axis_height - 20))
            bar_x2 = bar_x1 + bar_width
            bar_y2 = y_axis_height
            canvas.create_rectangle(bar_x1, bar_y1, bar_x2, bar_y2, fill=series['color'])

def draw_line_graph(canvas, data):
    canvas.delete("all")
    width, height = 480, 220
    canvas.create_text(width/2, 10, text=data['title'], font=("Helvetica", 10, "bold"))

    max_val = max(max(s['values']) for s in data['series'])
    y_axis_height = height - 50
    x_axis_width = width - 60
    
    # Y-axis
    canvas.create_line(50, 20, 50, y_axis_height)
    for i in range(6):
        val = max_val * (1 - i/5)
        y = 20 + (i * (y_axis_height - 20) / 5)
        canvas.create_line(45, y, 50, y)
        canvas.create_text(40, y, text=f"{val:.0f}%", anchor=tk.E)

    # X-axis
    canvas.create_line(50, y_axis_height, width-10, y_axis_height)

    num_points = len(data['x_labels'])
    for series in data['series']:
        points = []
        for i, val in enumerate(series['values']):
            x = 50 + (i * x_axis_width / (num_points-1))
            y = y_axis_height - (val / max_val * (y_axis_height - 20))
            points.extend([x,y])
            if i % 2 == 0: canvas.create_text(x, y_axis_height + 10, text=data['x_labels'][i])
        canvas.create_line(points, fill=series['color'], width=2)
        canvas.create_text(x + 5, y, text=series['name'], fill=series['color'], anchor=tk.W)

def draw_diagram(canvas, data):
    canvas.delete("all")
    width, height = 480, 220
    canvas.create_text(width/2, 10, text=data['title'], font=("Helvetica", 10, "bold"))
    
    num_steps = len(data['steps'])
    box_w, box_h = 100, 50
    x_spacing, y_spacing = 20, 30
    
    positions = []
    for i, step in enumerate(data['steps']):
        row = i // 4
        col = i % 4
        x = col * (box_w + x_spacing) + 30
        y = row * (box_h + y_spacing) + 40
        positions.append((x + box_w/2, y + box_h/2))
        
        canvas.create_rectangle(x, y, x + box_w, y + box_h, fill="#e0e0e0", outline="black")
        canvas.create_text(x + box_w/2, y + box_h/2, text=step['label'], justify=tk.CENTER)
        
        if step['arrow_to'] is not None:
            from_pos = positions[i]
            to_pos = positions[step['arrow_to']]
            
            if to_pos[0] > from_pos[0]: # Arrow right
                start_x, start_y = from_pos[0] + box_w/2, from_pos[1]
                end_x, end_y = to_pos[0] - box_w/2, to_pos[1]
                canvas.create_line(start_x, start_y, end_x, end_y, arrow=tk.LAST, width=1.5)
            else: # Arrow wraps around to the next line
                start_x, start_y = from_pos[0], from_pos[1] + box_h/2
                mid_y = start_y + y_spacing/2
                end_x, end_y = to_pos[0], to_pos[1] - box_h/2
                canvas.create_line(start_x, start_y, start_x, mid_y, end_x, mid_y, end_x, end_y, arrow=tk.LAST, width=1.5)

def populate_task_tab(parent_tab, task_number, prompts, scores_dict, total_score_label, status_label):
    """Populates a tab with the widgets for a single essay task."""
    parent_tab.columnconfigure(0, weight=1)
    parent_tab.rowconfigure(4, weight=2)
    parent_tab.rowconfigure(6, weight=1)

    # --- Prompt Section ---
    prompt_frame = ttk.Frame(parent_tab)
    prompt_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    prompt_frame.columnconfigure(0, weight=1)
    
    prompt_title = ttk.Label(prompt_frame, text=f"IELTS Writing Task {task_number}", style="Title.TLabel")
    prompt_title.grid(row=0, column=0, sticky="w")
    
    prompt_text_label = ttk.Label(prompt_frame, text="Click 'New Prompt' to begin.", wraplength=480, justify=tk.CENTER, font=("Helvetica", 10))

    canvas = tk.Canvas(prompt_frame, width=480, height=220, bg="#ffffff", relief=tk.SUNKEN, borderwidth=1)
    if task_number == 1:
        canvas.grid(row=1, column=0, pady=(5, 0), columnspan=2)
        prompt_text_label.grid(row=2, column=0, pady=(5, 0), columnspan=2)
    else:  # Task 2 has no canvas
        prompt_text_label.grid(row=1, column=0, sticky="ew", pady=(5, 0), columnspan=2)

    def get_new_prompt():
        prompt_data = random.choice(prompts)
        if task_number == 1:
            prompt_text_label.config(text=prompt_data["text"])
            draw_func = {"bar_chart": draw_bar_chart, "line_graph": draw_line_graph, "diagram": draw_diagram}.get(prompt_data["type"])
            if draw_func:
                draw_func(canvas, prompt_data["data"])
        else: # Task 2 prompts are simple strings
            prompt_text_label.config(text=prompt_data)
        
    new_prompt_button = ttk.Button(prompt_frame, text="New Prompt", command=get_new_prompt)
    new_prompt_button.grid(row=0, column=1, sticky="e", padx=(10, 0))

    # --- Input & Result Sections ---
    essay_text = scrolledtext.ScrolledText(parent_tab, wrap=tk.WORD, height=10, font=("Helvetica", 11), relief=tk.SOLID, borderwidth=1)
    essay_text.grid(row=4, column=0, sticky="nsew", pady=(10,0))
    
    score_button = ttk.Button(parent_tab, text=f"Score Task {task_number} Essay", style="Accent.TButton", command=lambda: on_score_button_click(essay_text, result_text, task_number, scores_dict, total_score_label, status_label))
    score_button.grid(row=5, column=0, pady=15)
    
    result_text = scrolledtext.ScrolledText(parent_tab, wrap=tk.WORD, height=8, font=("Helvetica", 11), relief=tk.SOLID, borderwidth=1, state=tk.DISABLED, bg="#ffffff")
    result_text.grid(row=6, column=0, sticky="nsew")
    result_text.tag_configure("bold", font=("Helvetica", 11, "bold"))

def create_gui():
    """Creates and runs the main GUI for the application."""
    window = tk.Tk()
    window.title("IELTS Essay Scorer")
    try:
        window.state('zoomed')
    except tk.TclError:
        # Fallback for some systems that don't support 'zoomed'
        window.attributes('-zoomed', True)
    window.minsize(1024, 700)
    
    style = ttk.Style(window)
    style.theme_use('clam')
    
    BG_COLOR, TEXT_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR = "#f0f2f5", "#333333", "#007bff", "#0056b3"
    
    window.configure(bg=BG_COLOR)
    
    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Helvetica", 11))
    style.configure("Title.TLabel", font=("Helvetica", 14, "bold"))
    style.configure("TotalScore.TLabel", font=("Helvetica", 16, "bold"), padding=(0, 10, 0, 10))
    style.configure("Accent.TButton", font=("Helvetica", 12, "bold"), padding=(10, 5))
    style.map("Accent.TButton", background=[('active', BUTTON_HOVER_COLOR), ('!disabled', BUTTON_COLOR)], foreground=[('!disabled', 'white')])
    style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"))
    style.configure("Status.TLabel", font=("Helvetica", 10, "italic"), anchor=tk.CENTER)
    style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"), padding=[10, 5])

    # --- Score History Data ---
    score_history_data = load_score_history()
    attempt_counter = [len(score_history_data) + 1] # Use a list to make it mutable inside functions

    # --- Main layout frames ---
    top_frame = ttk.Frame(window)
    top_frame.pack(fill=tk.X)

    main_app_frame = ttk.Frame(window)
    main_app_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    history_frame = ttk.Frame(window, width=350)
    history_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=(10,10), pady=(10,10))
    history_frame.pack_propagate(False) # Prevent resizing

    # --- Toggle History Button ---
    history_visible = tk.BooleanVar(value=True)
    def toggle_history():
        if history_visible.get():
            history_frame.pack_forget()
            history_visible.set(False)
        else:
            history_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=(10,10), pady=(10,10))
            history_visible.set(True)

    # --- Total Score Display ---
    scores_dict = {'task1': 0, 'task2': 0}
    total_score_frame = ttk.Frame(top_frame)
    total_score_frame.pack(fill=tk.X, pady=(5,0), expand=True)
    total_score_label = ttk.Label(total_score_frame, text="Overall IELTS Score: N/A (Score both tasks to see total)", style="TotalScore.TLabel", anchor=tk.CENTER)
    total_score_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(120,0)) # Pad to center roughly
    
    toggle_button = ttk.Button(total_score_frame, text="Toggle History", command=toggle_history)
    toggle_button.pack(side=tk.RIGHT, padx=20)

    status_label = ttk.Label(top_frame, text="", style="Status.TLabel")
    status_label.pack(fill=tk.X, expand=True)

    # --- Score History Panel ---
    history_label = ttk.Label(history_frame, text="Score History", style="Title.TLabel")
    history_label.pack(pady=5)

    tree_frame = ttk.Frame(history_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5,0))

    columns = ("attempt", "task1", "task2", "overall")
    score_history_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=score_history_tree.yview)
    score_history_tree.configure(yscrollcommand=scrollbar.set)

    score_history_tree.heading("attempt", text="Attempt")
    score_history_tree.heading("task1", text="Task 1")
    score_history_tree.heading("task2", text="Task 2")
    score_history_tree.heading("overall", text="Overall")
    score_history_tree.column("attempt", width=90, anchor=tk.CENTER, stretch=tk.YES)
    score_history_tree.column("task1", width=75, anchor=tk.CENTER)
    score_history_tree.column("task2", width=75, anchor=tk.CENTER)
    score_history_tree.column("overall", width=90, anchor=tk.CENTER)
    
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    score_history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for record in score_history_data:
        score_history_tree.insert("", tk.END, values=record)

    # --- Main Task Panes ---
    # Create a Notebook (tabbed view)
    notebook = ttk.Notebook(main_app_frame)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    task1_tab = ttk.Frame(notebook, padding=10)
    task2_tab = ttk.Frame(notebook, padding=10)

    notebook.add(task1_tab, text="IELTS Writing Task 1")
    notebook.add(task2_tab, text="IELTS Writing Task 2")

    populate_task_tab(task1_tab, 1, TASK_1_PROMPTS, scores_dict, total_score_label, status_label)
    populate_task_tab(task2_tab, 2, TASK_2_PROMPTS, scores_dict, total_score_label, status_label)

    # --- Submit Button ---
    submit_frame = ttk.Frame(main_app_frame)
    submit_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
    submit_button = ttk.Button(submit_frame, text="Submit for Final Score & Record", style="Accent.TButton", command=lambda: on_submit_final_score_click(scores_dict, total_score_label, score_history_tree, score_history_data, attempt_counter, status_label))
    submit_button.pack()

    window.mainloop()

if __name__ == "__main__":
    create_gui() 