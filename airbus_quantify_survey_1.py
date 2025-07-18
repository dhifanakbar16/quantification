import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc
from matplotlib.patches import Wedge

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USERNAME = 'itsffworldno5@gmail.com'
EMAIL_PASSWORD = 'vzcejhcgtwwcbhia'
RECIPIENT_EMAIL = 'dhifan.akbar@tum.de'

# Initialize session state for survey responses
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

def save_responses_to_csv(responses):
    """Save survey responses to a CSV file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"design_survey_responses_{timestamp}.csv"
    
    # Convert responses to DataFrame
    df = pd.DataFrame([responses])
    
    # Write to CSV (append if file exists)
    if not os.path.exists(filename):
        df.to_csv(filename, index=False)
    else:
        df.to_csv(filename, mode='a', header=False, index=False)
    
    return filename

def send_email_with_results(responses):
    """Send survey results via email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"New Design Survey Response - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Create email body
        body = "New survey response received:\n\n"
        for question, answer in responses.items():
            body += f"{question}: {answer}\n"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server and send
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

def create_standard_question(question_text, principle_category, key_suffix):
    """Helper function to create a standardized survey question"""
    key = f"{principle_category}_{key_suffix}"
    st.session_state.responses[key] = st.slider(
        question_text,
        min_value=1,
        max_value=5,
        value=3,
        key=key,
        help="1: Strongly Disagree, 3: Neutral, 5: Strongly Agree"
    )

def create_closure_visualization():
    """Create interactive visualization for Law of Closure"""
    st.subheader("1. Law of Closure")
    st.markdown("""
    **Instructions:**
    - Slide left to create a smaller arc
    - Slide right to create a more closed shape
    """)

    # Slider: Value maps to how 'closed' the circle appears
    closure_value = st.slider(
        "Adjust until you perceive this as a circle:",
        min_value=1,
        max_value=100,
        value=50,
        key="gestalt_closure_slider",
        help="Slide to change the arc length. Stop when you perceive it as a circle."
    )

    # Store the response
    st.session_state.responses["gestalt_closure"] = closure_value

    # Create visualization
    fig, ax = plt.subplots(figsize=(5, 5))

    # Convert slider value to arc span
    min_arc = 1
    max_arc = 360
    degrees = min_arc + (closure_value / 100) * (max_arc - min_arc)

    # Define arc as a wedge
    center = (0.5, 0.5)
    radius = 0.4
    theta1 = 270 - degrees / 2
    theta2 = 270 + degrees / 2

    wedge = plt.matplotlib.patches.Wedge(
        center=center,
        r=radius,
        theta1=theta1,
        theta2=theta2,
        width=0.05,
        color='black'
    )

    ax.add_patch(wedge)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_aspect('equal')

    # Plot the figure live
    st.pyplot(fig, clear_figure=True)

def create_continuity_visualization():
    """Create interactive visualization with pixel-offset quantification"""
    st.subheader("2. Law of Continuity")
    st.markdown(f"""
    **Instructions:**
    - At 1: Circles are randomly placed
    - At 100: Perfectly aligned
    """)
    
    # Constants
    DPI = 100 
    FIG_WIDTH_INCHES = 8
    FIG_HEIGHT_INCHES = 5
    MAX_PIXEL_OFFSET = 100
    
    # Slider configuration
    continuity_value = st.slider(
        "Adjust until circles appear aligned:",
        min_value=1,
        max_value=100,
        value=50,
        key="gestalt_continuity_slider",
        help=f"Slide to adjust alignment. Stop when you perceive the circles as aligned."
    )
    
    # Calculate current pixel offset
    current_px_offset = round(MAX_PIXEL_OFFSET * (1 - continuity_value/100))
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_INCHES, FIG_HEIGHT_INCHES), dpi=DPI)
    num_circles = 7
    circle_radius = 0.08
    
    # Base path (sine wave)
    x_base = np.linspace(0.1, 0.9, num_circles)
    y_base = 0.5 + 0.3 * np.sin(np.pi * (x_base - 0.5))
    
    # Convert pixel offset to figure coordinates
    max_deviation_x = (MAX_PIXEL_OFFSET / (FIG_WIDTH_INCHES * DPI))
    max_deviation_y = (MAX_PIXEL_OFFSET / (FIG_HEIGHT_INCHES * DPI))
    
    # Calculate current deviations
    np.random.seed(42)  # Consistent randomness
    x_dev = current_px_offset/MAX_PIXEL_OFFSET * max_deviation_x * (np.random.rand(num_circles) - 0.5)
    y_dev = current_px_offset/MAX_PIXEL_OFFSET * max_deviation_y * (np.random.rand(num_circles) - 0.5)
    
    # Calculate actual offsets
    actual_offsets = []
    for i in range(num_circles):
        x = x_base[i] + x_dev[i]
        y = y_base[i] + y_dev[i]
        actual_offsets.append(np.sqrt((x-x_base[i])**2 + (y-y_base[i])**2))
        
        circle = plt.Circle((x, y), circle_radius, color='black', fill=False, linewidth=2)
        ax.add_patch(circle)
    
    # Fixed this line
    avg_offset_px = round(np.mean(actual_offsets) * (FIG_WIDTH_INCHES * DPI))
    
    # Store both values
    st.session_state.responses["gestalt_continuity_value"] = continuity_value
    st.session_state.responses["gestalt_continuity_px"] = avg_offset_px
    
    # Visual feedback
    st.write(f"Current average offset: {avg_offset_px} pixels")
    
    # Visual reference at high alignment
    if continuity_value > 85:
        ax.plot(x_base, y_base, '--', color='gray', alpha=0.2, linewidth=1)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_aspect('equal')
    
    st.pyplot(fig, clear_figure=True)

def create_proximity_visualization():
    """Interactive visualization for Law of Proximity"""
    st.subheader("3. Law of Proximity")
    st.markdown(f"""
    **Instructions:**
    - At minimum setting the circles are clearly separated
    - At maximum setting the circles are clearly grouped
    """)
    
    # Constants
    DPI = 100
    FIG_SIZE = 5            # Square figure (inches)
    CIRCLE_RADIUS = 0.15    # Fixed size for all circles
    
    # Configuration
    MAX_PIXEL_DISTANCE = 350  # Maximum distance at slider=1 (spread apart)
    MIN_PIXEL_DISTANCE = 150  # Minimum distance at slider=100 (tightly grouped)
    
    proximity_value = st.slider(
        "Adjust the slider until the circles appear to form a cohesive group:",
        min_value=1,
        max_value=100,
        value=50,
        key="gestalt_proximity_slider",
        help=f"Slide to adjust the distance between the circles. Stop when you perceive it as grouped by proximity."
    )
    
    # Calculate current distance in pixels and figure coordinates
    current_px_dist = MIN_PIXEL_DISTANCE + (MAX_PIXEL_DISTANCE - MIN_PIXEL_DISTANCE) * (1 - proximity_value/100)
    fig_dist = current_px_dist / (FIG_SIZE * DPI)
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(FIG_SIZE, FIG_SIZE), dpi=DPI)
    
    # Position 4 circles in a square formation
    positions = [
        (0.5 - fig_dist/2, 0.5 - fig_dist/2),  # Bottom-left
        (0.5 + fig_dist/2, 0.5 - fig_dist/2),  # Bottom-right
        (0.5 - fig_dist/2, 0.5 + fig_dist/2),  # Top-left
        (0.5 + fig_dist/2, 0.5 + fig_dist/2)   # Top-right
    ]
    
    for (x, y) in positions:
        circle = plt.Circle(
            (x, y), 
            CIRCLE_RADIUS,
            color='black',
            fill=False,
            linewidth=2
        )
        ax.add_patch(circle)
    
    # Store responses
    st.session_state.responses["gestalt_proximity_value"] = proximity_value
    st.session_state.responses["gestalt_proximity_px"] = current_px_dist
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_aspect('equal')
    
    st.pyplot(fig, clear_figure=True)
    
def main():
    # Survey Header
    st.title("Expert Survey on Quantifying Design Principles")
    st.markdown("""
    Dear respondents,

    My name is Dhifan, and I am a Master's student at the Technical University of Munich (TUM), currently conducting my thesis at TADYX6 – Airbus Defence and Space.

    As part of this research, I aim to gather expert insights from professionals like you to transform qualitative design principles into quantifiable definitions. These principles—often text-based and generic—are widely used in the evaluation of graphical user interfaces (GUIs) in aviation and safety-critical systems.

    The numerical representation of these rules will serve as the foundation for building a rule-based algorithm that automatically assesses interface quality. By quantifying what is often considered subjective or implicit, we can improve design traceability, consistency, and validation in future display development tools.

    Your input is essential to this research, as it provides industry-grounded context that ensures the model reflects real-world expectations and expert judgment—especially in aviation-related displays.

    Thank you very much for your time and expertise.
    """)

    # Instructions Section
    st.subheader("Instructions for Taking the Survey")
    st.markdown("""
    To ensure the quality and consistency of your responses, please follow these setup guidelines:

    - 📏 Sit approximately 30 cm from your screen.
    - 🪑 Maintain an upright, comfortable posture.
    - ☀️ Make sure no direct sunlight or light is shining on your screen or face (other than the screen itself).
    - 🖥️ Set screen brightness to a comfortable, readable level.
    - 🌡️ You may take the survey in any quiet room or workspace — lighting and temperature may vary, as long as your view of the screen is clear.
    - ⏱️ Allocate enough uninterrupted time to thoughtfully consider each question.
    - 🔁 You may go back and adjust your answers before final submission.

    These conditions help minimize distractions, perception errors, or visibility-related inconsistencies.

    Thank you for your careful participation.
    """)
    
    if not st.session_state.submitted:
        # Gestalt Principles Section - moved outside the form for immediate updates
        st.header("Gestalt Design Laws")
        st.markdown("""
        Gestalt Design Laws describe how humans perceive visual elements as unified wholes.
        """)
        
        # Initialization of visualization
        create_closure_visualization()
        create_continuity_visualization()
        create_proximity_visualization()
        
        # Start the form for all other questions
        with st.form("design_survey"):
            # Other Gestalt Principles
            create_standard_question(
                "Elements that are close together are perceived as related (Proximity)",
                "gestalt", "proximity"
            )
            create_standard_question(
                "Similar elements are perceived as related (Similarity)",
                "gestalt", "similarity"
            )
            create_standard_question(
                "Elements arranged in a line or curve are perceived as related (Continuity)",
                "gestalt", "continuity"
            )
            create_standard_question(
                "The figure/ground relationship is clear in the design",
                "gestalt", "figure_ground"
            )
            
            # Wickens' Principles Section
            st.header("Wickens' Principles")
            st.markdown("""
            **Wickens' Principles** focus on human information processing and cognitive ergonomics.
            """)
            
            create_standard_question(
                "The design minimizes perceptual confusion",
                "wickens", "perceptual"
            )
            create_standard_question(
                "The design reduces mental workload",
                "wickens", "mental_workload"
            )
            create_standard_question(
                "The design minimizes memory requirements",
                "wickens", "memory"
            )
            create_standard_question(
                "The design guides attention effectively",
                "wickens", "attention"
            )
            
            # Ergonomic Considerations Section
            st.header("Ergonomic Considerations")
            st.markdown("""
            **Ergonomic Considerations** address physical and cognitive fit between users and designs.
            """)
            
            create_standard_question(
                "The design promotes user comfort",
                "ergonomic", "comfort"
            )
            create_standard_question(
                "The design is accessible to diverse users",
                "ergonomic", "accessibility"
            )
            create_standard_question(
                "The design considers safety aspects",
                "ergonomic", "safety"
            )
            create_standard_question(
                "The design promotes efficient task completion",
                "ergonomic", "efficiency"
            )
            
            # Additional Comments
            st.session_state.responses["comments"] = st.text_area(
                "Additional comments or observations:",
                key="comments"
            )
            
            # Submit button
            submitted = st.form_submit_button("Submit Survey")
            
            if submitted:
                st.session_state.submitted = True
                
                # Save responses to CSV
                csv_filename = save_responses_to_csv(st.session_state.responses)
                
                # Send email
                email_sent = send_email_with_results(st.session_state.responses)
                
                if email_sent:
                    st.success("Survey submitted successfully! Results have been saved and emailed.")
                else:
                    st.success("Survey submitted successfully! (Email notification failed)")
                
                st.download_button(
                    label="Download Your Responses",
                    data=pd.DataFrame([st.session_state.responses]).to_csv(index=False),
                    file_name=csv_filename,
                    mime="text/csv"
                )
    else:
        st.success("Thank you for completing the survey!")
        if st.button("Take survey again"):
            st.session_state.submitted = False
            st.session_state.responses = {}
            st.experimental_rerun()

if __name__ == "__main__":
    main()
