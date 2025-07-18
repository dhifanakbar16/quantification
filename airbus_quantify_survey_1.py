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

st.set_page_config(page_title="Quantification Survey", layout="centered")

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

    # Visual feedback
    st.write(f"Current distance: {current_px_dist}")
    
    # Store responses
    st.session_state.responses["gestalt_proximity_value"] = proximity_value
    st.session_state.responses["gestalt_proximity_px"] = current_px_dist
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_aspect('equal')
    
    st.pyplot(fig, clear_figure=True)

def create_experience_visualization():
    """Interactive visualization for Law of Experience"""
    st.subheader("4. Law of Experience")
    st.markdown(f"""
    **Instructions:**
    - Slide left to increase noise level
    - Slide right to decrease noise level
    """)
    
    # Configuration
    IMAGE_PATH = "pfd.png" 
    MAX_NOISE = 1000  # Maximum noise at slider=1 (completely hidden)
    MIN_NOISE = 0     # Minimum noise at slider=100 (fully clear)
    
    experience_value = st.slider(
        "Adjust the slider until you recognize the image:",
        min_value=1,
        max_value=100,
        value=50,
        key="gestalt_experience_slider",
        help="Slide right to reduce noise. Stop when you recognize what it depicts."
    )
    
    # Load and process image
    img = plt.imread(IMAGE_PATH)
    noise_level = MAX_NOISE * (1 - experience_value/100)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(5, 5))
    
    # Apply noise proportional to slider
    if noise_level > 0:
        noise = np.random.normal(0, noise_level/255, img.shape)
        noisy_img = np.clip(img + noise, 0, 1)
        ax.imshow(noisy_img)
    else:
        ax.imshow(img)
    
    ax.axis('off')

    # Visual feedback
    st.write(f"Current noise level: {noise_level:.2f}")
    
    # Store responses
    st.session_state.responses["gestalt_experience_value"] = experience_value
    st.session_state.responses["gestalt_experience_noise"] = f"{noise_level:.1f}%"
    
    st.pyplot(fig, clear_figure=True)

def create_pragnanz_visualization():
    """Interactive visualization for Law of Prägnanz (simplicity)"""
    st.subheader("5. Law of Prägnanz (Simplicity)")
    st.markdown(f"""
    **Instructions:**
    - 1: Simple circle
    - 2: Inner circle added
    - 3-6: Cardinal direction blades
    - 7-10: Diagonal blades and details
    """)
    
    pragnanz_value = st.slider(
        "Adjust the slider until the shape reaches the simplest form that clearly represents an engine:",
        min_value=1,
        max_value=10,
        value=5,
        key="gestalt_pragnanz_slider",
        help="Slide to make the shape more detailed. Stop when the shape reaches the simplest form that clearly represents an engine."
    )
    
    # Create figure
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Base circle (always present)
    outer_circle = plt.Circle((0.5, 0.5), 0.4, fill=False, linewidth=2)
    ax.add_patch(outer_circle)
    
    # Progressive elements
    if pragnanz_value >= 2:
        # Inner circle
        inner_circle = plt.Circle((0.5, 0.5), 0.1, fill=False, linewidth=2)
        ax.add_patch(inner_circle)
    
    if pragnanz_value >= 3:
        # First blade at 0°
        ax.plot([0.5, 0.5 + 0.35], [0.5, 0.5], 'k-', linewidth=2)
    
    if pragnanz_value >= 4:
        # Second blade at 90°
        ax.plot([0.5, 0.5], [0.5, 0.5 + 0.35], 'k-', linewidth=2)
    
    if pragnanz_value >= 5:
        # Third blade at 180°
        ax.plot([0.5, 0.5 - 0.35], [0.5, 0.5], 'k-', linewidth=2)
    
    if pragnanz_value >= 6:
        # Fourth blade at 270°
        ax.plot([0.5, 0.5], [0.5, 0.5 - 0.35], 'k-', linewidth=2)
    
    if pragnanz_value >= 7:
        # Fifth blade at 45°
        x = 0.5 + 0.35 * np.cos(np.radians(45))
        y = 0.5 + 0.35 * np.sin(np.radians(45))
        ax.plot([0.5, x], [0.5, y], 'k-', linewidth=2)
    
    if pragnanz_value >= 8:
        # Sixth blade at 135°
        x = 0.5 + 0.35 * np.cos(np.radians(135))
        y = 0.5 + 0.35 * np.sin(np.radians(135))
        ax.plot([0.5, x], [0.5, y], 'k-', linewidth=2)
    
    if pragnanz_value >= 9:
        # Seventh blade at 225°
        x = 0.5 + 0.35 * np.cos(np.radians(225))
        y = 0.5 + 0.35 * np.sin(np.radians(225))
        ax.plot([0.5, x], [0.5, y], 'k-', linewidth=2)
    
    if pragnanz_value >= 10:
        # Eighth blade at 315°
        x = 0.5 + 0.35 * np.cos(np.radians(315))
        y = 0.5 + 0.35 * np.sin(np.radians(315))
        ax.plot([0.5, x], [0.5, y], 'k-', linewidth=2)
        
        # Swirl in inner circle (3 arcs)
        for i in range(3):
            ax.add_patch(Arc((0.5, 0.5), 0.15, 0.15, 
                        theta1=i*120, theta2=i*120+90, 
                        linewidth=1, color='k'))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_aspect('equal')
    
    st.pyplot(fig, clear_figure=True)
    
    # Store responses
    st.session_state.responses["gestalt_pragnanz_value"] = pragnanz_value
    st.session_state.responses["gestalt_pragnanz_complexity"] = f"Level {pragnanz_value}/10"

def create_similarity_visualization():
    """Interactive visualization for Law of Similarity"""
    st.subheader("6. Law of Similarity")
    st.markdown(f"""
    **Instructions:**
    - At 1: All shapes have random colors
    - At 100: All shapes share the same color
    """)
    
    similarity_color_value = st.slider(
        "Adjust until the shapes appear to belong together:",
        min_value=1,
        max_value=100,
        value=50,
        key="gestalt_similarity_color_slider",
        help="Slide to change the colors in the shapes. Stop when the shape appears to be similar."
    )
    
    # Create figure
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Base positions for 9 shapes (3x3 grid)
    positions = [(x, y) for x in np.linspace(0.2, 0.8, 3) 
                     for y in np.linspace(0.2, 0.8, 3)]
    
    # Base color (will be mixed with random colors based on slider)
    base_color = np.array([0.2, 0.4, 0.8])  # Blueish
    
    for i, (x, y) in enumerate(positions):
        # Calculate color similarity
        if similarity_color_value == 100:
            color = base_color
        else:
            random_component = np.random.rand(3)
            mix_ratio = 1 - (similarity_color_value/100)
            color = base_color * (1-mix_ratio) + random_component * mix_ratio
        
        # Alternate between circle and square for some variety
        if i % 2 == 0:
            shape = plt.Circle((x, y), 0.08, color=color)
        else:
            shape = plt.Rectangle((x-0.08, y-0.08), 0.16, 0.16, color=color)
        
        ax.add_patch(shape)
    
    # Calculate and store similarity metric
    color_variance = 100 - similarity_color_value
    st.session_state.responses["gestalt_similarity_color_value"] = similarity_color_value
    st.session_state.responses["gestalt_similarity_variance"] = f"{color_variance}%"

    # Visual feedback
    st.write(f"Current color variance: {color_variance}")
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    st.pyplot(fig, clear_figure=True)

def create_symmetry_visualization():
    st.subheader("7. Law of Symmetry")
    st.markdown("""
    **Instructions:**
    - At 1: Random petal arrangement
    - At 100: Perfect radial symmetry
    """)

    symmetry_value = st.slider(
        "Adjust until petals appear symmetrical:",
        min_value=1, 
        max_value=100, 
        value=50,
        key="gestalt_symmetry_slider",
        help="Slide to change the position of the petals. Stop when the petals appears to be symmetrical."
    )

    fig, ax = plt.subplots(figsize=(6, 6))
    center = (0.5, 0.5)
    ax.plot(center[0], center[1], 'ko', markersize=5)

    n_petals = 10  # Must be even
    angles = np.linspace(0, 2*np.pi, n_petals, endpoint=False)
    asymmetry = 1 - (symmetry_value / 100)
    petal_positions = []

    # Generate petals with controlled distortion
    for i, angle in enumerate(angles):
        ideal_x = center[0] + 0.4 * np.cos(angle)
        ideal_y = center[1] + 0.4 * np.sin(angle)
        
        if symmetry_value < 100:
            np.random.seed(i)
            x = ideal_x + asymmetry * np.random.normal(0, 0.05)
            y = ideal_y + asymmetry * np.random.normal(0, 0.05)
        else:
            x, y = ideal_x, ideal_y
        
        petal_positions.append((x, y))
        ax.plot([center[0], x], [center[1], y], 'k-', linewidth=2)
        ax.plot(x, y, 'ko', markersize=8)

    # Calculate radial symmetry offsets
    x_offsets = []
    y_offsets = []
    
    for i in range(n_petals // 2):
        x1, y1 = petal_positions[i]
        x2, y2 = petal_positions[i + n_petals//2]  # 180° counterpart
        
        # For perfect radial symmetry:
        # x1 + x2 should equal 2*center_x (1.0), and y1 + y2 should equal 2*center_y (1.0)
        x_offsets.append(abs((x1 + x2) - 1.0))  # X symmetry error
        y_offsets.append(abs((y1 + y2) - 1.0))  # Y symmetry error

    avg_x_offset = np.mean(x_offsets) * 100  # As % of figure width
    avg_y_offset = np.mean(y_offsets) * 100  # As % of figure height

    # Store corrected metrics
    st.session_state.responses.update({
        "gestalt_symmetry_value": symmetry_value,
        "gestalt_symmetry_avg_x_offset": f"{avg_x_offset:.2f}%",
        "gestalt_symmetry_avg_y_offset": f"{avg_y_offset:.2f}%",
        "gestalt_symmetry_avg_radial_error": f"{np.mean([avg_x_offset, avg_y_offset]):.2f}%"
    })

    st.write(f"Current avg X-offset from centerline: {avg_x_offset:.2f}%")
    st.write(f"Current avg Y-offset from centerline: {avg_y_offset:.2f}%")
    
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
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
        create_experience_visualization()
        create_pragnanz_visualization()
        create_similarity_visualization()
        create_symmetry_visualization()
        
        # Start the form for all other questions
        with st.form("design_survey"):
            # Wickens' Principles Section
            st.header("Wickens' Principles")
            st.markdown("""
            **Wickens' Principles** focus on human information processing and cognitive ergonomics.
            """)
            
            create_standard_question(
                "The design minimizes perceptual confusion",
                "wickens", "perceptual"
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
