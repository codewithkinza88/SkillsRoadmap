# Skills Roadmap - Gradio app
# Converted from the original Google Colab notebook.

from dotenv import load_dotenv
import os
import json
import re
import gradio as gr
from openai import OpenAI

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set. Add it as an environment variable or hosting secret.")

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
MODEL_NAME = "openai/gpt-oss-20b"

# ============================================================
# STEP 5: CREATE ROADMAP AI SYSTEM PROMPT
# ============================================================
# This prompt tells the AI exactly how our application should
# create personalized learning roadmaps.
#
# The AI will consider:
# - Student level
# - Learning goal
# - Available time
# - Daily study time
# - Existing skills
# - Learning style
# - Purpose
# - Interests

SYSTEM_PROMPT = """

You are RoadMap AI, an intelligent personalized learning
roadmap generator for students.

Your job is to create a realistic, structured and personalized
learning roadmap based on the student's information.

============================================================
STUDENT LEVELS
============================================================

BEGINNER:
- Assume little or no previous knowledge.
- Start from fundamentals.
- Explain concepts in a logical order.
- Include simple exercises.
- Include beginner-friendly projects.
- Do not overwhelm the student.

INTERMEDIATE:
- Assume the student already knows the fundamentals.
- Avoid unnecessary beginner material.
- Focus on skill improvement.
- Introduce intermediate and advanced concepts.
- Include practical projects.

EXPERT:
- Assume strong existing knowledge.
- Skip basic concepts.
- Focus on advanced and specialized topics.
- Include challenging real-world projects.
- Include production-level or research-oriented concepts
  when appropriate.

============================================================
TIME MANAGEMENT
============================================================

The roadmap MUST respect the student's available duration
and daily study time.

For short durations:
- Prioritize the most important concepts.
- Keep the roadmap focused.
- Avoid unrealistic amounts of content.

For longer durations:
- Include deeper learning.
- Include revision.
- Include multiple projects.
- Include specialization.

The roadmap must be achievable.

============================================================
PRACTICAL LEARNING
============================================================

Whenever appropriate, include:

- Concepts
- Practice
- Exercises
- Mini projects
- Larger projects
- Revision
- Final capstone project

============================================================
PERSONALIZATION
============================================================

Do NOT generate the same roadmap for every student.

The roadmap should change depending on:

- Level
- Goal
- Duration
- Daily time
- Existing skills
- Learning style
- Purpose
- Interests

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Do NOT use Markdown.

Use exactly this structure:

{
    "title": "",
    "summary": "",

    "student_profile": {
        "goal": "",
        "level": "",
        "duration": "",
        "daily_time": ""
    },

    "roadmap": [
        {
            "phase": "",
            "duration": "",
            "focus": "",
            "topics": [],
            "practice": [],
            "project": "",
            "outcome": ""
        }
    ],

    "final_project": {
        "title": "",
        "description": "",
        "skills_used": []
    },

    "completion_outcome": ""
}

Make the roadmap realistic, useful and personalized.

"""



# ============================================================
# STEP 7: FORMAT ROADMAP FOR DISPLAY
# ============================================================
# The AI gives us structured JSON.
# This function converts that JSON into beautiful Markdown
# that will later be displayed inside our Gradio app.

def roadmap_to_markdown(data):

    # --------------------------------------------------------
    # Get student profile
    # --------------------------------------------------------

    profile = data.get("student_profile", {})

    # --------------------------------------------------------
    # Create roadmap header
    # --------------------------------------------------------

    markdown = f"""
# 🗺️ {data.get("title", "Your Learning Roadmap")}

### ✨ Your Personalized AI Learning Journey

{data.get("summary", "")}

---

## 🎓 Student Profile

| Information | Details |
|---|---|
| 🎯 Goal | {profile.get("goal", "")} |
| 📊 Level | {profile.get("level", "")} |
| ⏳ Duration | {profile.get("duration", "")} |
| 🕐 Daily Time | {profile.get("daily_time", "")} |

---

# 📚 Your Roadmap
"""

    # --------------------------------------------------------
    # Add every roadmap phase
    # --------------------------------------------------------

    phases = data.get("roadmap", [])

    for number, phase in enumerate(phases, start=1):

        topics = phase.get("topics", [])

        practice = phase.get("practice", [])

        # Convert topics into bullet points
        topic_text = "\n".join(
            f"- {topic}"
            for topic in topics
        )

        # Convert practice into bullet points
        practice_text = "\n".join(
            f"- {item}"
            for item in practice
        )

        markdown += f"""

## {number}. {phase.get("phase", "Learning Phase")}

**⏱ Duration:** {phase.get("duration", "")}

### 🎯 Focus

{phase.get("focus", "")}

### 📖 Topics

{topic_text}

### 🧠 Practice

{practice_text}

### 🛠️ Project

**{phase.get("project", "Practice Project")}**

### ✅ Expected Outcome

{phase.get("outcome", "")}

---

"""

    # --------------------------------------------------------
    # Final capstone project
    # --------------------------------------------------------

    final_project = data.get("final_project", {})

    skills = final_project.get("skills_used", [])

    skills_text = ", ".join(skills)

    markdown += f"""

# 🏆 Final Capstone Project

## {final_project.get("title", "Final Project")}

{final_project.get("description", "")}

**🧰 Skills Used:** {skills_text}

---

# 🎉 Completion Outcome

{data.get("completion_outcome", "")}

---

<center>

### 💡 RoadMap AI

**Your path. Your pace. Your progress.**

</center>
"""

    return markdown




# ============================================================
# STEP 8: CUSTOM UI STYLING
# ============================================================
# This CSS makes our Gradio application look like a modern
# AI web application instead of a basic Python interface.

custom_css = """

/* General font for elegance and readability */
body {
    font-family: 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
}

/* Main application container */
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}

/* Hero section */
#hero {
    text-align: center;
    padding: 45px 25px;
    border-radius: 25px;
    margin-bottom: 30px;

    background: linear-gradient(
        135deg,
        #667eea,
        #764ba2
    );

    color: white;
}

/* Hero title */
#hero h1 {
    font-size: 48px; /* Slightly larger for impact */
    margin-bottom: 10px;
    font-weight: 700; /* Bolder */
}

/* Hero text */
#hero p {
    font-size: 20px; /* Slightly larger for elegance */
    line-height: 1.6; /* Better readability */
}

/* General heading adjustments for professionalism */
h1 {
    font-size: 3em; /* Larger headings */
    font-weight: 600;
}
h2 {
    font-size: 2em;
    font-weight: 500;
}
h3 {
    font-size: 1.5em;
    font-weight: 500;
}

/* Generate button */
.generate-btn {
    font-size: 18px !important;
    font-weight: bold !important;
    border-radius: 14px !important;
    min-height: 55px !important;
    /* Adding some subtle shadow for more modern look */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Output area */
.output-box {
    border-radius: 20px !important;
    padding: 20px; /* Add padding for better look */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); /* Subtle shadow */
}

/* Input labels and info text */
.gradio-app label {
    font-weight: 500; /* Make labels a bit bolder */
    font-size: 1.1em;
}

.gradio-app .gr-form-text { /* For info text */
    font-size: 0.9em;
    color: #555;
}

/* Remove default footer */
footer {
    display: none !important;
}

"""



# ============================================================
# STEP 9: MAIN APPLICATION FUNCTION
# ============================================================
# This function connects:
#
# Gradio inputs
#       ↓
# AI roadmap generator
#       ↓
# Markdown formatter
#       ↓
# Gradio output
#
# So when the user clicks the button, this function runs.

def create_roadmap(
    goal,
    level,
    duration,
    daily_time,
    current_skills,
    learning_style,
    purpose,
    interests
):

    # --------------------------------------------------------
    # Generate roadmap using our AI function
    # --------------------------------------------------------

    data, error = generate_roadmap(
        goal,
        level,
        duration,
        daily_time,
        current_skills,
        learning_style,
        purpose,
        interests
    )

    # --------------------------------------------------------
    # If something went wrong
    # --------------------------------------------------------

    if error:

        return f"""
## ❌ Unable to Generate Roadmap

{error}
"""

    # --------------------------------------------------------
    # Convert AI JSON into beautiful Markdown
    # --------------------------------------------------------

    return roadmap_to_markdown(data)

# ============================================================
# HELPER FUNCTION: GENERATE ROADMAP
# ============================================================
# This function sends the student's profile to Groq and
# returns the AI-generated roadmap. It also handles errors.

def generate_roadmap(
    goal,
    level,
    duration,
    daily_time,
    current_skills,
    learning_style,
    purpose,
    interests
):

    # --------------------------------------------------------
    # Create user prompt
    # --------------------------------------------------------

    user_prompt = f"""

    Create a personalized learning roadmap for this student.

    Learning Goal:
    {goal}

    Current Level:
    {level}

    Available Duration:
    {duration}

    Study Time Per Day:
    {daily_time}

    Current Knowledge:
    {current_skills}

    Learning Style:
    {learning_style}

    Purpose:
    {purpose}

    Specific Interests:
    {interests}

    Make the roadmap realistic and personalized.

    Return valid JSON only.

    """

    # --------------------------------------------------------
    # Send request to Groq
    # --------------------------------------------------------

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            # Lower temperature helps the AI follow our structure
            temperature=0.3
        )

        # Get AI response
        raw_output = response.choices[0].message.content.strip()

        # Remove accidental Markdown code fences
        raw_output = re.sub(
            r"^```json\s*|\s*```$",
            "",
            raw_output,
            flags=re.IGNORECASE
        ).strip()

        # Convert JSON text into Python dictionary
        roadmap_data = json.loads(raw_output)

        return roadmap_data, None

    except Exception as e:

        return None, f"Error generating roadmap: {e}"

# ============================================================
# STEP 10: BUILD ROADMAP AI INTERFACE
# ============================================================
# Gradio will create the complete web interface for us.

import gradio as gr


with gr.Blocks(
    theme=gr.themes.Soft(),
    css=custom_css,
    title="Skills Roadmap"
) as app:

    # ========================================================
    # HERO SECTION
    # ========================================================

    gr.HTML("""
    <div id="hero">

        <h1>🗺️ Skills Roadmap</h1>

        <p>
            Your personalized learning journey.
        </p>

        <p>
            Tell us where you are.
            We'll help you discover where to go. ✨
        </p>

    </div>
    """)

    # ========================================================
    # FORM HEADING
    # ========================================================

    gr.Markdown(
        """
# 🎓 Build Your Personalized Skills Roadmap

Tell us about yourself and we will create a
learning path designed specifically for you.
"""
    )

    # ========================================================
    # INPUT SECTION
    # ========================================================

    with gr.Row():

        # ----------------------------------------------------
        # LEFT COLUMN
        # ----------------------------------------------------

        with gr.Column():

            goal = gr.Textbox(
                label="🎯 What do you want to learn?",
                placeholder=(
                    "e.g. Data Science, Web Development, "
                    "Artificial Intelligence..."
                ),
                info="Enter your main learning goal."
            )

            level = gr.Dropdown(
                choices=[
                    "Beginner",
                    "Intermediate",
                    "Expert"
                ],
                label="📊 Current Skill Level",
                value="Beginner"
            )

            duration = gr.Dropdown(
                choices=[
                    "7 days",
                    "2 weeks",
                    "1 month",
                    "2 months",
                    "3 months",
                    "6 months",
                    "1 year"
                ],
                label="⏳ How much time do you have?",
                value="3 months"
            )

            daily_time = gr.Dropdown(
                choices=[
                    "30 minutes/day",
                    "1 hour/day",
                    "2 hours/day",
                    "3 hours/day",
                    "4+ hours/day"
                ],
                label="🕐 Study Time Per Day",
                value="2 hours/day"
            )

        # ----------------------------------------------------
        # RIGHT COLUMN
        # ----------------------------------------------------

        with gr.Column():

            current_skills = gr.Textbox(
                label="💻 What do you already know?",
                placeholder=(
                    "e.g. Basic Python, HTML/CSS, "
                    "Statistics..."
                ),
                lines=4
            )

            learning_style = gr.Radio(
                choices=[
                    "Theory + Practice",
                    "Mostly Projects",
                    "Mostly Theory",
                    "Mixed / Not Sure"
                ],
                label="📚 Preferred Learning Style",
                value="Theory + Practice"
            )

            purpose = gr.Dropdown(
                choices=[
                    "Career",
                    "University / Studies",
                    "Personal Learning",
                    "Build a Project",
                    "Freelancing",
                    "Other"
                ],
                label="🎓 Why do you want to learn this?",
                value="Career"
            )

            interests = gr.Textbox(
                label="⭐ Specific Interests (Optional)",
                placeholder=(
                    "e.g. Machine Learning, NLP, "
                    "Computer Vision..."
                ),
                lines=3
            )

    # ========================================================
    # GENERATE BUTTON
    # ========================================================

    generate_btn = gr.Button(
        "✨ Generate My Roadmap",
        variant="primary",
        elem_classes="generate-btn"
    )

    # ========================================================
    # DIVIDER
    # ========================================================

    gr.Markdown("---")

    # ========================================================
    # OUTPUT SECTION
    # ========================================================

    gr.Markdown(
        """
# 🗺️ Your Personalized Roadmap

Your personalized learning journey will appear below.
"""
    )

    output = gr.Markdown(
        """
### 👋 Welcome to Skills Roadmap!

Fill in your learning profile above and click:

### ✨ Generate My Roadmap

Your personalized roadmap will appear here.
""",
        elem_classes="output-box"
    )

    # ========================================================
    # BUTTON EVENT
    # ========================================================
    # When the button is clicked:
    #
    # User inputs
    #      ↓
    # create_roadmap()
    #      ↓
    # Groq AI
    #      ↓
    # formatted roadmap
    #      ↓
    # output
    #
    # The inputs list MUST match the order of the function
    # parameters.

    generate_btn.click(

        fn=create_roadmap,

        inputs=[
            goal,
            level,
            duration,
            daily_time,
            current_skills,
            learning_style,
            purpose,
            interests
        ],

        outputs=output
    )

    # ========================================================
    # FOOTER
    # ========================================================

    gr.Markdown(
        """
---
<center>

**🗺️ Skills Roadmap**

*Your path. Your pace. Your progress.*

</center>
"""
    )



if __name__ == "__main__":
    app.launch(
        server_name="127.0.0.1",
        server_port=7862,
        share=False,
        show_error=True,
        quiet=False
    )
