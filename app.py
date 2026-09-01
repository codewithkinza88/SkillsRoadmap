# Skills Roadmap - Streamlit app
# Converted from the original Gradio version.

from dotenv import load_dotenv
import os
import json
import re
import streamlit as st
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
# STEP 8: HELPER FUNCTION: GENERATE ROADMAP
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
# STEP 9: MAIN APPLICATION FUNCTION
# ============================================================
# This function connects:
#
# Streamlit inputs
#       ↓
# AI roadmap generator
#       ↓
# Markdown formatter
#       ↓
# Streamlit output
#
# User ke inputs ko AI ko bhejte hain, aur output display karte hain.

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
# STEP 10: PAGE CONFIGURATION & STREAMLIT INTERFACE
# ============================================================
# Streamlit page configuration sets up the app's appearance.

st.set_page_config(
    page_title="Skills Roadmap",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():

    # ========================================================
    # HERO SECTION
    # ========================================================
    
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px; 
                background: linear-gradient(135deg, #667eea, #764ba2); 
                border-radius: 15px; color: white; margin-bottom: 30px;">
        <h1 style="font-size: 48px; margin-bottom: 10px;">🗺️ Skills Roadmap</h1>
        <p style="font-size: 20px; line-height: 1.6;">Your personalized learning journey.</p>
        <p style="font-size: 18px;">Tell us where you are. We'll help you discover where to go. ✨</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ========================================================
    # FORM HEADING
    # ========================================================
    
    st.markdown("""
    # 🎓 Build Your Personalized Skills Roadmap
    
    Tell us about yourself and we will create a
    learning path designed specifically for you.
    """)
    
    # ========================================================
    # INPUT SECTION - TWO COLUMNS
    # ========================================================
    
    col1, col2 = st.columns(2)
    
    # -------- LEFT COLUMN --------
    with col1:
        st.subheader("📋 Learning Profile")
        
        goal = st.text_input(
            label="🎯 What do you want to learn?",
            placeholder="e.g. Data Science, Web Development, Artificial Intelligence...",
            help="Enter your main learning goal."
        )
        
        level = st.selectbox(
            label="📊 Current Skill Level",
            options=["Beginner", "Intermediate", "Expert"],
            index=0
        )
        
        duration = st.selectbox(
            label="⏳ How much time do you have?",
            options=["7 days", "2 weeks", "1 month", "2 months", "3 months", "6 months", "1 year"],
            index=4  # Default to 3 months
        )
        
        daily_time = st.selectbox(
            label="🕐 Study Time Per Day",
            options=["30 minutes/day", "1 hour/day", "2 hours/day", "3 hours/day", "4+ hours/day"],
            index=2  # Default to 2 hours/day
        )
    
    # -------- RIGHT COLUMN --------
    with col2:
        st.subheader("🎯 Your Preferences")
        
        current_skills = st.text_area(
            label="💻 What do you already know?",
            placeholder="e.g. Basic Python, HTML/CSS, Statistics...",
            height=100
        )
        
        learning_style = st.radio(
            label="📚 Preferred Learning Style",
            options=["Theory + Practice", "Mostly Projects", "Mostly Theory", "Mixed / Not Sure"],
            index=0
        )
        
        purpose = st.selectbox(
            label="🎓 Why do you want to learn this?",
            options=["Career", "University / Studies", "Personal Learning", "Build a Project", "Freelancing", "Other"],
            index=0
        )
        
        interests = st.text_area(
            label="⭐ Specific Interests (Optional)",
            placeholder="e.g. Machine Learning, NLP, Computer Vision...",
            height=80
        )
    
    # ========================================================
    # GENERATE BUTTON
    # ========================================================
    
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        if st.button(
            "✨ Generate My Roadmap",
            use_container_width=True,
            type="primary"
        ):
            # ========================================================
            # GENERATE ROADMAP
            # ========================================================
            
            with st.spinner("🚀 Generating your personalized roadmap..."):
                
                roadmap_markdown = create_roadmap(
                    goal,
                    level,
                    duration,
                    daily_time,
                    current_skills,
                    learning_style,
                    purpose,
                    interests
                )
                
                # Store in session state taaki scroll na ho jaye
                st.session_state.roadmap_output = roadmap_markdown
    
    # ========================================================
    # OUTPUT SECTION
    # ========================================================
    
    st.markdown("---")
    
    st.markdown("""
    # 🗺️ Your Personalized Roadmap
    
    Your personalized learning journey will appear below.
    """)
    
    # Display roadmap agar generate ho gaya ho
    if "roadmap_output" in st.session_state:
        st.markdown(st.session_state.roadmap_output)
    else:
        st.info("""
        ### 👋 Welcome to Skills Roadmap!
        
        Fill in your learning profile above and click:
        
        ### ✨ Generate My Roadmap
        
        Your personalized roadmap will appear here.
        """)
    
    # ========================================================
    # FOOTER
    # ========================================================
    
    st.markdown("---")
    st.markdown("""
    <center>
    
    **🗺️ Skills Roadmap**
    
    *Your path. Your pace. Your progress.*
    
    </center>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()