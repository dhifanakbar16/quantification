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
import time
from PIL import Image
from email.mime.base import MIMEBase
from email import encoders

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
        
        # Create email body with all responses
        body = "New survey response received:\n\n"
        for question, answer in responses.items():
            body += f"{question}: {answer}\n"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach CSV
        df = pd.DataFrame([responses])
        csv_data = df.to_csv(index=False)
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(csv_data.encode())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=f"survey_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        msg.attach(part)
        
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

def create_closure_visualization():
    """Create interactive visualization for Law of Closure"""
    st.subheader("1. Law of Closure")
    st.markdown("""
    **Instructions:**
    - Slide left to create a smaller arc.
    - Slide right to create a more closed shape.
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
    - At 1: Circles are randomly placed.
    - At 100: Perfectly continuous.
    """)
    
    # Constants
    DPI = 100 
    FIG_WIDTH_INCHES = 8
    FIG_HEIGHT_INCHES = 5
    MAX_PIXEL_OFFSET = 200
    
    # Slider configuration
    continuity_value = st.slider(
        "Adjust until circles appear continuous:",
        min_value=1,
        max_value=100,
        value=50,
        key="gestalt_continuity_slider",
        help=f"Slide to adjust alignment. Stop when you perceive the circles as continuous."
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
    - At minimum setting the circles are clearly separated.
    - At maximum setting the circles are clearly grouped.
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
    - Slide left to increase noise level.
    - Slide right to decrease noise level.
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
    st.write(f"Current noise level: {noise_level:.1f}")
    
    # Store responses
    st.session_state.responses["gestalt_experience_value"] = experience_value
    st.session_state.responses["gestalt_experience_noise"] = f"{noise_level:.1f}%"
    
    st.pyplot(fig, clear_figure=True)

    st.write("Credit: https://docs.flybywiresim.com/pilots-corner/a32nx/a32nx-briefing/pfd")

def create_pragnanz_visualization():
    """Interactive visualization for Law of Prägnanz (simplicity)"""
    st.subheader("5. Law of Prägnanz (Simplicity)")
    st.markdown(f"""
    **Instructions:**
    - 1: Simple circle.
    - 2: Inner circle added.
    - 3-6: Cardinal direction blades.
    - 7-10: Diagonal blades and details.
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
    - At 1: All shapes have random colors.
    - At 100: All shapes share the same color.
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
    - At 1: Random petal arrangement.
    - At 100: Perfect radial symmetry.
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

def create_common_fate_questions():
    st.subheader("8. Law of Common Fate")
    st.markdown(""" 
    **Instructions:** 
    - Select all expected behaviors for each aviation display element.
    - You may choose more than one option where fits.
    """)

    common_fate_responses = {}
    motion_options = [
        "⬆️ Up", "⬇️ Down", "➡️ Right", "⬅️ Left",
        "↻ Clockwise", "↺ Counter-clockwise",
        "💨 Expand outward", "🌀 Spiral inward",
        "🔴 Color change (e.g., red)", "🟢 Color change (e.g., green)",
        "🔢 Numerical update", "📈 Fill animation",
        "🚨 Blinking alert", "📉 Tape scrolls down", 
        "🛑 Solid red + audible alarm"
    ]

    # Question template
    def ask_motion_direction(question, element_name):
        st.write(f"**{question}**")
        selected = st.multiselect(
            f"Expected behaviors for {element_name}:",
            options=motion_options,
            default=None,
            key=f"common_fate_{element_name}",
            help="Select the option(s) which you deem fit for the display element in question."
        )
        common_fate_responses[element_name] = {"behaviors": selected}

    # Engine Display Instruments
    ask_motion_direction(
        "A. When engine RPM increases, how should the indicator respond?",
        "Engine RPM"
    )
    ask_motion_direction(
        "B. When temperature exceeds limit on the exhaust gas, how should the indicator be presented?",
        "Exhaust Gas Temperature"
    )
    ask_motion_direction(
        "C. When the fuel consumption decreases, how should the indicator change?",
        "Fuel Flow"
    )
    ask_motion_direction(
        "D. When the thrust setting changes, how should the information be displayed?",
        "Thrust Setting"
    )
    ask_motion_direction(
        "E. When the fuel on board decreases, how should the indicator change?",
        "Fuel on Board"
    )
    ask_motion_direction(
        "F. When the flap extends, how should the information be displayed?",
        "Flap Setting"
    )

    # Primary Flight Display
    ask_motion_direction(
        "G. When the airspeed increases, how should the indicator change?",
        "Airspeed"
    )
    ask_motion_direction(
        "H. When the climb rate decreases, how should the vertical speed indicator change?",
        "Climb Rate"
    )
    ask_motion_direction(
        "I. When turning right, how should the heading indicator change?",
        "Heading Indicator"
    )
    ask_motion_direction(
        "J. When the plane descends, how should the altimeter change?",
        "Altimeter"
    )

    # Other Critical Displays
    ask_motion_direction(
        "K. When hydraulic pressure drops critically, how should the warning appear?",
        "Hydraulic Warning"
    )
    ask_motion_direction(
        "L. When gear deploys, how should the landing gear indicator be displayed?",
        "Landing Gear"
    )
    ask_motion_direction(
        "M. When autopilot is turned off, how should the autopilot status be updated?",
        "Autopilot Status"
    )

    # Comment box at the end
    st.markdown("---")
    general_notes = st.text_area(
        "Additional context or special cases (optional):",
        key="common_fate_notes",
        help="Describe any unique expectations not captured above."
    )
    
    # Store all responses with notes
    st.session_state.responses["common_fate"] = {
        "elements": common_fate_responses,
        "general_notes": general_notes
    }

def create_legibility_questions():
    st.subheader("9. Display Legibility")
    st.markdown(""" 
    **Instructions:** 
    - Please answer the questions below to establish a minimum legibility thresholds.
    - Please remember to adjust your eyes to be at least 30 cm away from the screen and sit upright.
    """)

    # 1. Font Size Threshold Test
    st.markdown("**A. Minimum Legible Font Size**")
    font_sample = st.slider(
        "Adjust until text below becomes illegible:",
        min_value=1, max_value=30, value=15, step=1,
        key="legibility_font_size",
        help="Slide to change the font size. Stop when the text becomes too small to read comfortably."
    )

    st.write(f"Current font size: {font_sample}")
    st.markdown(f'<p style="font-size:{font_sample}pt">ALT 3200ft <span style="color:red">HDG 178°</span> IAS 210kt</p>', 
                unsafe_allow_html=True)
    st.session_state.responses["legibility_min_font_pt"] = font_sample

    # Add space between sections
    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Contrast Sensitivity Test
    st.markdown("**B. Contrast Threshold**")
    contrast = st.slider(
        "Adjust contrast until text becomes unreadable:",
        min_value=1, max_value=100, value=50,
        key="legibility_contrast",
        help="Slide to change the background color. Stop when the text becomes hard to read."
    )

    bg_color = 255 - int(255 * (contrast/100))

    st.write(f"Current background color value: {bg_color}")
    st.markdown(
        f'<div style="background-color:rgb({bg_color},{bg_color},{bg_color});'
        f'padding:10px;border-radius:5px">'
        f'<p style="color:black;font-size:14pt">ENG1 OIL 120°C</p></div>',
        unsafe_allow_html=True
    )

    st.session_state.responses["legibility_contrast_threshold"] = f"{100-contrast}%"

    # Add space between sections
    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Color Differentiation Test
    st.markdown("**C. Color Differentiation**")
    color_pairs = [
        ("red", "green", "WARNING vs NORMAL"),
        ("blue", "purple", "ACTIVE vs STANDBY"),
        ("orange", "yellow", "CAUTION vs ADVISORY")
    ]
    for color1, color2, label in color_pairs:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<p style="color:{color1};font-size:12pt">■ {label} {color1}</p>', 
                       unsafe_allow_html=True)
        with col2:
            st.markdown(f'<p style="color:{color2};font-size:12pt">■ {label} {color2}</p>', 
                       unsafe_allow_html=True)
        score = st.slider(
            f"How distinct are these colors for {label}? (1 = identical, 10 = very distinct)",
            min_value=1, max_value=10, value=5,
            key=f"legibility_color_{color1}_{color2}",
            help="Slide to adjust your answer. The slider does not change any appearances."
        )
        st.session_state.responses[f"legibility_color_{color1.replace('#','')}_{color2.replace('#','')}"] = score

    # Add space between sections
    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Glare Simulation Test
    st.markdown("**D. Glare Resistance**")
    glare_intensity = st.slider(
        "Adjust the glare effect until text become unreadable:",
        min_value=1, max_value=100, value=50,
        key="legibility_glare",
        help="Slide to change the glare opacity. Stop when you face difficulty in reading the text."
    )
    glare_opacity = glare_intensity / 50

    st.write(f"Current glare opacity: {glare_opacity}")

    st.markdown(
        f'<div style="position:relative;background-color:#003366;padding:15px;border-radius:5px">'
        f'<p style="color:white;font-size:14pt">FLAPS 15°</p>'
        f'<div style="position:absolute;top:0;left:0;width:100%;height:100%;'
        f'background:linear-gradient(135deg, rgba(255,255,255,{glare_opacity}) 0%, '
        f'rgba(255,255,255,{glare_opacity*0.5}) 50%);"></div></div>',
        unsafe_allow_html=True
    )
    st.session_state.responses["legibility_glare_tolerance"] = f"{glare_intensity}%"

    # Add space between sections
    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Dynamic Text Legibility
    st.markdown("**E. Moving Text Legibility**")
    motion_speed = st.slider(
        "Adjust until the text movement speed (0.1 = slow, 10.0 = fast) becomes too fast:",
        min_value=0.1, max_value=10.0, value=5.0, step=0.1,
        key="legibility_motion",
        help="Slide to change the text movement speed. Stop when the text becomes disorienting to read."
    )
    
    # Convert speed to animation duration (faster speed = shorter duration)
    animation_duration = max(0.1, 2.0 - (motion_speed * 0.19))  # Maps 0.1→~2s, 10→~0.1s
    
    st.write(f"Current speed: {motion_speed} (animation duration: {animation_duration:.1f}s)")

    st.markdown(
        f'<style>'
        f'.motion-test {{animation: moveText {animation_duration}s linear infinite;}}'
        f'@keyframes moveText {{0% {{transform: translateX(0px);}} 50% {{transform: translateX(20px);}} 100% {{transform: translateX(0px);}}}}'
        f'</style>'
        f'<p class="motion-test" style="font-size:14pt">VSI +1200 ft/min</p>',
        unsafe_allow_html=True
    )
    st.session_state.responses["legibility_motion_threshold"] = motion_speed

def create_absolute_judgement_questions():
    st.subheader("10. Avoid Absolute Judgement Limits")
    st.markdown("""
    **Instructions:**
    - Please evaluate whether the display requires you to make precise judgements (e.g., exact values, small differences).
    - Please rate how easily you can interpret the information without needing perfect precision.
    """)

    # 1. Numeric Readability (Exact vs. Approximate)
    st.markdown("**A. Numeric Readability**")
    st.markdown("Compare these two displays and rate each display on how easy it is to understand the information.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Display 1 (Precise):**  
        `Fuel: 4237 lbs`  
        `Oil Temp: 187°C`  
        `Altitude: 12453 ft`
        """)
        precise_score = st.slider(
            "Rate Display 1 (1 = hard, 5 = easy)",
            1, 5, 3,
            key="absjudge_numeric_precise",
            help="Slide to adjust your answer."
        )
    
    with col2:
        st.markdown("""
        **Display 2 (Approximate):**  
        `Fuel: ~4200 lbs`  
        `Oil Temp: ~190°C`  
        `Altitude: ~12500 ft`
        """)
        approx_score = st.slider(
            "Rate Display 2 (1 = hard, 5 = easy)",
            1, 5, 3,
            key="absjudge_numeric_approx",
            help="Slide to adjust your answer."
        )
    
    st.session_state.responses["absjudge_numeric_diff"] = approx_score - precise_score

    # 2. Color Gradients (Subtle Differences)
    st.markdown("**B. Color Gradient Interpretation**")
    st.markdown("Can you distinguish these color-coded status levels without exact hues?")
    
    gradient_colors = ["#FF0000", "#FF4500", "#FFA500", "#FFD700", "#FFFF00"]
    gradient_labels = ["Critical", "High", "Medium", "Low", "Caution"]
    
    cols = st.columns(len(gradient_colors))
    for i, (color, label) in enumerate(zip(gradient_colors, gradient_labels)):
        with cols[i]:
            st.markdown(f'<div style="height:50px;background:{color};border-radius:5px"></div>', unsafe_allow_html=True)
            st.markdown(f"**{label}**")
    
    gradient_score = st.slider(
        "Rate how easily you can distinguish levels (1 = indistinguishable, 5 = very clear)",
        1, 5, 3,
        key="absjudge_color_gradient",
        help="Slide to adjust your answer."
    )
    st.session_state.responses["absjudge_color_diff"] = gradient_score

    # 3. Relative vs Absolute Judgement
    st.markdown("**C. Relative vs Absolute Judgement**")
    st.markdown("Which of these altitude displays is easier to interpret quickly?")
    
    alt_option = st.radio(
        "Options:",
        ["Absolute: `ALT 12453 ft`", "Relative: `+500 ft` (from target)", "Both are equal"],
        key="absjudge_altitude",
        help="Select the option you think suits the question best."
    )
    st.session_state.responses["absjudge_alt_preference"] = alt_option

def create_topdown_processing_questions():
    st.subheader("11. Top-Down Processing")
    st.markdown("""
    **Instructions:**  
    - Assume all elements are placed in one square display.
    - For each horizontal region (Top/Middle/Bottom), select the cockpit elements you'd expect to see there.
    - Elements can now appear in multiple regions (duplicates allowed).
    - Number of elements per region can vary.
    """)

    # Define elements and grid
    elements = [
        "Engine RPM", "Exhaust Gas Temperature", "Fuel Flow", 
        "Thrust Setting", "Fuel on Board", "Flap Setting",
        "Additional Text Information"
    ]
    grid_labels = [
        "Top-Left", "Top-Middle", "Top-Right",
        "Middle-Left", "Center", "Middle-Right",
        "Bottom-Left", "Bottom-Middle", "Bottom-Right"
    ]

    # Initialize session state
    if "topdown_grid" not in st.session_state:
        st.session_state.topdown_grid = {label: [] for label in grid_labels}

    # TOP ROW (Horizontal)
    top_cols = st.columns(3)
    for i, label in enumerate(["Top-Left", "Top-Middle", "Top-Right"]):
        with top_cols[i]:
            st.markdown(f"**{label}**")
            current_selection = st.session_state.topdown_grid.get(label, [])
            
            new_selection = st.multiselect(
                f"Select for {label}:",
                elements,
                default=current_selection,
                key=f"top_select_{label}"
            )
            st.session_state.topdown_grid[label] = new_selection
            
            if new_selection:
                st.markdown(f"*Selected:* {', '.join(new_selection)}")

    # MIDDLE ROW (Horizontal)
    middle_cols = st.columns(3)
    for i, label in enumerate(["Middle-Left", "Center", "Middle-Right"]):
        with middle_cols[i]:
            st.markdown(f"**{label}**")
            current_selection = st.session_state.topdown_grid.get(label, [])
            
            new_selection = st.multiselect(
                f"Select for {label}:",
                elements,
                default=current_selection,
                key=f"middle_select_{label}"
            )
            st.session_state.topdown_grid[label] = new_selection
            
            if new_selection:
                st.markdown(f"*Selected:* {', '.join(new_selection)}")

    # BOTTOM ROW (Horizontal)
    bottom_cols = st.columns(3)
    for i, label in enumerate(["Bottom-Left", "Bottom-Middle", "Bottom-Right"]):
        with bottom_cols[i]:
            st.markdown(f"**{label}**")
            current_selection = st.session_state.topdown_grid.get(label, [])
            
            new_selection = st.multiselect(
                f"Select for {label}:",
                elements,
                default=current_selection,
                key=f"bottom_select_{label}"
            )
            st.session_state.topdown_grid[label] = new_selection
            
            if new_selection:
                st.markdown(f"*Selected:* {', '.join(new_selection)}")

    # Count how many times each element appears
    element_counts = {}
    for items in st.session_state.topdown_grid.values():
        for item in items:
            element_counts[item] = element_counts.get(item, 0) + 1

    # Save results
    st.session_state.responses["topdown_processing"] = {
        "grid_assignments": st.session_state.topdown_grid,
        "element_counts": element_counts
    }

def create_redundancy_gain_questions():
    st.subheader("12. Redundancy Gain")
    st.markdown("""
    **Instructions:**  
    - Compare the 4 versions of the engine failure alert below.  
    - Select which design is clearest and most intuitive.  
    """)

    alert = "ENGINE FAILURE"
    icons = {"ENGINE FAILURE": "🔥"}
    shapes = {"triangle": "⚠️"}
    
    # Initialize responses
    if "redundancy_responses" not in st.session_state:
        st.session_state.redundancy_responses = {}
    
    # Version 1: Text-Only
    st.markdown("**Version 1: Text-Only**")
    st.markdown(
        f'<div style="font-size:16pt; padding:10px; border:1px solid #ccc; border-radius:5px; margin-bottom:20px;">'
        f'{alert}</div>',
        unsafe_allow_html=True
    )
    
    # Version 2: Text + Icon
    st.markdown("**Version 2: Text + Icon**")
    st.markdown(
        f'<div style="font-size:16pt; padding:10px; border:1px solid #ccc; border-radius:5px; margin-bottom:20px;">'
        f'{icons[alert]} {alert} {icons[alert]}</div>',
        unsafe_allow_html=True
    )
    
    # Version 3: Text + Color + Shape
    st.markdown("**Version 3: Text + Icon + Color**")
    st.markdown(
        f'<div style="font-size:16pt; color:red; padding:10px; border:1px solid #ccc; '
        f'border-radius:5px; margin-bottom:20px;">'
        f'{shapes["triangle"]} <strong>{alert}</strong> {shapes["triangle"]}</div>',
        unsafe_allow_html=True
    )
    
    # Version 4: Spatial Grouping
    st.markdown("**Version 4: Spatial Grouping**")
    st.markdown(
        f'<div style="font-size:16pt; padding-left:10px; border-left:4px solid red; '
        f'border-radius:2px; margin-bottom:20px;">'
        f'{icons[alert]} <strong>{alert}</strong></div>',
        unsafe_allow_html=True
    )

    # --- Preference Question ---
    preference = st.radio(
        "Which version is clearest for recognizing an engine failure?",
        options=[
            "Version 1 (Text-Only)",
            "Version 2 (Text + Icon)",
            "Version 3 (Text + Icon + Color)",
            "Version 4 (Spatial Grouping)"
        ],
        index=None,  # Force user to select
        key="redundancy_preference"
    )
    
    # Save response
    if preference:
        st.session_state.responses["redundancy_gain"] = {
            "preferred_version": preference,
            "alert_type": alert
        }

    # Optional justification
    st.text_input("Briefly explain your choice (optional):", key="redundancy_reason")

import streamlit as st

def create_discriminability_questions():
    st.subheader("13. Discriminability")
    st.markdown("""
    **Instructions:**
    - A reference text is shown at font size 12.
    - Adjust the slider to find the smallest font size that looks visibly different from the reference.
    """)

    # Reference text (fixed at 12px)
    st.markdown("**Reference Text**")
    st.markdown('<p style="font-size:12px; margin:0">ALT 5000ft</p>', unsafe_allow_html=True)

    # Dynamic comparison text
    st.markdown("")
    font_size = st.slider(
        "Adjust font size until the text below looks clearly different from the reference text above (12px):",
        min_value=12.0,
        max_value=24.0,
        value=18.0,
        step=0.5,
        key="font_size_diff",
        help="Slide to change the font size. Stop at the smallest font size where you feel the text is in different grouping than the reference text."
    )
    
    difference = round(font_size - 12, 1)
    st.session_state.responses["min_discriminable_size_diff"] = f"{difference}px"
    st.write(f"Your current minimum noticeable difference: {difference}")

    # Display the comparison
    st.markdown(f'<p style="font-size:{font_size}px; margin:0">ALT 5000ft</p>', unsafe_allow_html=True)

def create_pictorial_realism_questions():
    st.subheader("14. Pictorial Realism")
    st.markdown("""
    **Instructions:** 
    - Evaluate how intuitively users interpret orderly vs realistic layouts.
    - Assume left/right wing tanks feed engines 1/2 respectively.
    """)

    # Generate simple diagrams
    left_tank = "⬤"  # Unicode circle
    right_tank = "⬤"
    engine1 = "✈️"
    engine2 = "✈️"

    # Orderly vs. realistic layouts
    orderly_layout = f"""
    ```
    [Tank A] ---> [Engine 1]
    [Tank B] ---> [Engine 2]
    """
    
    realistic_layout = """
    LEFT ENGINE       RIGHT ENGINE
      |                                                |
     ( )-----------------------------( )
       \\                                              /
        \\                                           /
         (lEFT TANK)       (RIGHT TANK)
    """

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Orderly Layout**")
        st.code(orderly_layout, language="text")
    
    with col2:
        st.markdown("**Realistic Layout**")
        st.text(realistic_layout)

    # Horizontal rating questions
    st.markdown("Rate each layout:")
    rating_col1, rating_col2 = st.columns(2)
    
    with rating_col1:
        orderly_pref = st.radio(
            "Orderly Layout (1 = unintuitive, 5 = intuitive)",
            [1, 2, 3, 4, 5],
            horizontal=True,
            key="orderly_layout",
            help="Please choose one of the option. Orderly layout follows modern design to classify and organize information in an oderly and minimalistic way."
        )
        st.session_state.responses["orderly_layout_rating"] = orderly_pref
    
    with rating_col2:
        realistic_pref = st.radio(
            "Realistic Layout (1 = unintuitive, 5 = intuitive)",
            [1, 2, 3, 4, 5],
            horizontal=True,
            key="realistic_layout",
            help="Please choose one of the option. Realistic layout follows the simplified and scaled down of the realistic placement of the elements presented."
        )
        st.session_state.responses["realistic_layout_rating"] = realistic_pref

def create_moving_parts_visualization():
    st.subheader("15. Moving Parts")
    st.markdown("""
    **Instructions:**
    - Play the animation as more circles start moving.
    - Select the point where you think that there are too many moving elements.
    """)

    # User selects when tracking becomes difficult
    difficulty_threshold = st.slider(
        "Adjust until the number of moving circles becomes overwhelming to see:",
        min_value=1, 
        max_value=10, 
        value=5,
        key="moving_parts_threshold",
        help="Adjust your answer on the slider. Stop when you feel the animation becomes hard to follow"
    )

    # Animation setup
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(0, 11)
    ax.set_ylim(-0.5, 1.5)
    ax.axis('off')
    
    n_circles = 10
    circles = []
    for i in range(n_circles):
        circle = plt.Circle((i+1, 0.5), 0.4, color='blue', alpha=0.7)
        ax.add_patch(circle)
        circles.append(circle)
        ax.text(i+1, 0.5, str(i+1), ha='center', va='center', color='white')

    # Animation update function
    def update(frame):
        current_moving = (frame // 20) % 10 + 1  # Cycles 1-10 every 2 sec (20 frames * 0.1s)
        
        for i, circle in enumerate(circles):
            if i < current_moving:
                # Animate moving up and down
                y_pos = 0.5 + 0.3 * np.sin(frame * 0.2 + i * 0.5)
                circle.set_center((i+1, y_pos))
                circle.set_alpha(0.7)
            else:
                circle.set_center((i+1, 0.5))
                circle.set_alpha(0.2)
        
        ax.set_title(f"{current_moving} Moving Circles", fontsize=12)
        return circles

    st.write(f"Current moving parts threshold: {difficulty_threshold} moving circles")

    # Create animation (simulated for Streamlit)
    # Note: Streamlit doesn't support FuncAnimation natively, so we simulate frames
    if st.button("Play Animation"):
        placeholder = st.empty()
        for frame in range(200):  # 200 frames (~20 sec loop)
            current_moving = (frame // 20) % 10 + 1
            update(frame)
            placeholder.pyplot(fig, clear_figure=False)
            time.sleep(0.1)

    # Store metrics
    st.session_state.responses.update({
        "moving_parts_threshold": difficulty_threshold,
        "moving_parts_assessment": "Optimal" if difficulty_threshold <= 3 else "High Load"
    })

def create_access_cost_visualization():
    st.subheader("16. Minimize Information Access Cost")
    st.markdown("""
    **Instructions:**  
    - Select each cockpit element into one of the Access Cost Zones below.  
    - **Zone 0**: Directly visible (optimal for critical elements).  
    - **Zone 3**: Buried in menus/subpages (high cost).  
    """)

    # Define elements
    elements = [
        "Engine RPM", "Exhaust Gas Temperature", "Fuel Flow", 
        "Thrust Setting", "Fuel on Board", "Flap Setting", 
        "Airspeed", "Climb Rate", "Heading Indicator", 
        "Altimeter", "Hydraulic Warning", "Landing Gear", 
        "Autopilot Status"
    ]

    # Define zones (0=lowest cost, 3=highest cost)
    zones = {
        "Zone 0: Directly Visible (Primary Display)": [],
        "Zone 1: 1-Step Access (Secondary Display)": [],
        "Zone 2: 2-Step Access (Submenu/Popup)": [],
        "Zone 3: 3+ Steps (Nested Menus)": []
    }

    # Initialize session state
    if "access_cost_zones" not in st.session_state:
        st.session_state.access_cost_zones = {zone: [] for zone in zones.keys()}
        st.session_state.unassigned_elements = elements.copy()

    # Reset tracking
    st.session_state.unassigned_elements = [
        e for e in elements 
        if not any(e in zone_list for zone_list in st.session_state.access_cost_zones.values())
    ]

    # --- ZONE LAYOUT (4 columns) ---
    cols = st.columns(4)
    for i, (zone_name, _) in enumerate(zones.items()):
        with cols[i]:
            st.markdown(f"**{zone_name}**")
            
            # Multiselect for each zone (acts as drag-and-drop proxy)
            zone_selection = st.multiselect(
                f"Assign to {zone_name.split(':')[0]}",
                st.session_state.unassigned_elements + st.session_state.access_cost_zones[zone_name],
                default=st.session_state.access_cost_zones.get(zone_name, []),
                key=f"zone_{i}"
            )
            st.session_state.access_cost_zones[zone_name] = zone_selection

            # Display current assignments
            if zone_selection:
                st.markdown(f"*Assigned:* {', '.join(zone_selection)}")

    # --- VALIDATION ---
    all_assigned = []
    for zone, items in st.session_state.access_cost_zones.items():
        all_assigned.extend(items)

    # Check for duplicates/missing elements
    duplicates = set([x for x in all_assigned if all_assigned.count(x) > 1])
    if duplicates:
        st.error(f"Error: Duplicate assignments: {duplicates}. Remove extras.")
    elif len(all_assigned) != len(elements):
        st.warning(f"Not all elements placed ({len(all_assigned)}/{len(elements)})")

    # Store results
    st.session_state.responses.update({
        "access_cost_zones": st.session_state.access_cost_zones
    })

def create_proximity_compatibility_questions():
    st.subheader("17. Proximity Compatibility")
    st.markdown("""
    **Instructions:**  
    - For each element pair, rate how closely they should be grouped (1 = Unrelated, 5 = Must be adjacent).
    - To be grouped is to put the elements close to each other.
    """)

    # Define element pairs
    element_pairs = [
        ("Engine RPM", "Exhaust Gas Temperature"),
        ("Airspeed", "Altimeter"),
        ("Fuel Flow", "Fuel on Board"),
        ("Heading Indicator", "Climb Rate"),
        ("Hydraulic Warning", "Landing Gear"),
        ("Autopilot Status", "Thrust Setting")
    ]

    ratings = {}
    for pair in element_pairs:
        key = f"{pair[0]} ↔ {pair[1]}"
        rating = st.slider(
            f"How closely should **{pair[0]}** and **{pair[1]}** be grouped?",
            1, 5, 3,
            key=f"prox_{pair[0]}_{pair[1]}",
            help="1 = Unrelated, 3 = Moderate, 5 = Critical to group"
        )
        ratings[key] = rating

    # Store results
    st.session_state.responses.update({
        "proximity_ratings": ratings,
    })

def create_multiple_resources_questions():
    st.subheader("18. Multiple Resources")
    st.markdown("""
    **Instructions:**  
    - For each task, select which resource channels are used.  
    - Leave unselected if a channel isn't used.  
    """)

    # Define tasks
    tasks = {
        "Monitor Engine RPM": "Visual gauge + Audio alert if exceeding threshold",
        "Adjust Thrust Setting": "Manual lever control + Voice command confirmation",
        "Respond to ATC Instructions": "Auditory message + Vocal response + Visual checklist",
        "Navigate with Map": "Visual map + Haptic feedback when off-course",
        "Handle Hydraulic Failure": "Visual warning + Audio alarm + Manual switch override"
    }

    # Resource channel options
    channels = {
        "Perceptual": ["Visual", "Auditory", "Haptic"],
        "Cognitive": ["Perception", "Working Memory", "Decision Making"],
        "Response": ["Manual", "Vocal", "None"]
    }

    # --- Task Evaluation ---
    allocations = {}
    for task, description in tasks.items():
        st.markdown(f"**Task:** {task}  \n*{description}*")

        cols = st.columns(3)
        selected_channels = []
        
        # Perceptual Channel
        with cols[0]:
            perceptual = st.multiselect(
                "Perceptual:",
                channels["Perceptual"],
                default=[],
                key=f"perceptual_{task}"
            )
            selected_channels.extend(perceptual)
        
        # Cognitive Channel
        with cols[1]:
            cognitive = st.multiselect(
                "Cognitive:",
                channels["Cognitive"],
                default=[], 
                key=f"cognitive_{task}"
            )
            selected_channels.extend(cognitive)
        
        # Response Channel
        with cols[2]:
            response = st.multiselect(
                "Response:",
                channels["Response"],
                default=[],
                key=f"response_{task}"
            )
            selected_channels.extend(response)
        
        allocations[task] = selected_channels

    # Store results
    st.session_state.responses.update({
        "resource_allocations": allocations,
    })

def create_predictive_aiding_questions():
    st.subheader("19. Predictive Aiding")
    st.markdown("""
    **Instructions:**  
    - Adjust each slider to set your preferred warning threshold.  
    - Warnings should trigger when the value crosses your selected threshold.  
    - Danger zones are fixed at max values (10, 100, 1000).  
    """)

    # --- Slider 1 (1-10 scale) ---
    st.write("**Case 1: Low-Range Metric (Danger = 10)**")
    threshold_1 = st.slider(
        "Adjust until it has reached an appropriate value to trigger a warning:",
        min_value=1,
        max_value=10,
        value=5,
        key="predictive_1",
        help="Slide to adjust your answer. Stop when you feel like it's the right value to issue a warning."
    )

    # --- Slider 2 (1-100 scale) ---
    st.write("**Case 2: Mid-Range Metric (Danger = 100)**")
    threshold_2 = st.slider(
        "Adjust until it has reached an appropriate value to trigger a warning:",
        min_value=1,
        max_value=100,
        value=50,
        key="predictive_2",
        help="Slide to adjust your answer. Stop when you feel like it's the right value to issue a warning."
    )

    # --- Slider 3 (1-1000 scale) ---
    st.write("**Case 3: High-Range Metric (Danger = 1000)**")
    threshold_3 = st.slider(
        "Adjust until it has reached an appropriate value to trigger a warning:",
        min_value=1,
        max_value=1000,
        value=500,
        key="predictive_3",
        help="Slide to adjust your answer. Stop when you feel like it's the right value to issue a warning."
    )
    
def create_memory_replacement_visualization():
    st.subheader("20. Replace Memory with Visual Information")
    st.markdown("""
    **Instructions:**  
    1. Click **Show Engine Display** to view an engine schematic for 7 seconds.  
    2. After it disappears, recall and enter as many details as possible.  
    """)

    # Load engine display image
    engine_img = Image.open("ecam.png")

    # Initialize session state
    if "memory_test_started" not in st.session_state:
        st.session_state.memory_test_started = False
        st.session_state.memory_test_end_time = 0
        st.session_state.recalled_items = []

    # --- Image Display Phase ---
    if not st.session_state.memory_test_started:
        if st.button("Show Engine Display"):
            st.session_state.memory_test_started = True
            st.session_state.memory_test_end_time = time.time() + 7 
            st.rerun()

    else:
        # Show image for 7 seconds
        if time.time() < st.session_state.memory_test_end_time:
            st.image(engine_img, caption="Engine Display (Memorize this!)", use_container_width=True)
            st.write(f"Time left: {int(st.session_state.memory_test_end_time - time.time())}s")
            st.rerun() 
        else:
            st.session_state.memory_test_started = False
            st.success("Time's up! Enter what you remember below.")

    st.write("Credit: Anja Faulhaber, 2021")

    # --- Recall Phase ---
    if "memory_test_end_time" in st.session_state and time.time() > st.session_state.memory_test_end_time:
        recalled = st.text_area(
            "List all details you remember (example: engine rpm, fuel flow, and so on):",
            height=200,
            key="memory_recall"
        )
        st.session_state.recalled_items = [item.strip() for item in recalled.split(",") if item.strip()]

    # Store results
    st.session_state.responses.update({
        "memory_recall_attempt": st.session_state.recalled_items
    })

def create_consistency_questions():
    st.subheader("21. Consistency")
    st.markdown("""
    **Instructions:**  
    1. Compare pairs of elements below.  
    2. Rate their consistency on a 1-5 scale (1 = Inconsistent, 5 = Identical) based on how they should be designed against each other.  
    """)

    # Define element pairs to compare
    consistency_pairs = [
        ("Engine RPM Gauge", "Exhaust Temp Gauge"),
        ("Primary Flight Display Colors", "Navigation Display Colors"),
        ("Warning Alert Sound", "System Notification Sound"),
        ("Button 'AUTO THRUST' Style", "Button 'FLAP EXTEND' Style"),
        ("Menu Navigation Pattern", "Submenu Navigation Pattern")
    ]

    # --- Pair Comparison ---
    ratings = {}
    for pair in consistency_pairs:
        key = f"{pair[0]} ↔ {pair[1]}"
        rating = st.slider(
            f"How consistent are **{pair[0]}** and **{pair[1]}**?",
            1, 5, 3,
            key=f"consistency_{pair[0]}_{pair[1]}",
            help="Slide to adjust your answer,"
        )
        ratings[key] = rating

    # Store results
    st.session_state.responses.update({
        "consistency_ratings": ratings,
    })

def create_frequency_of_use_questions():
    st.subheader("22. Frequency of Use")
    st.markdown("""
    **Instructions:**  
    - Assign each cockpit element to its usage frequency category.  
    """)

    # Define elements and frequency options
    elements = [
        "Engine RPM", "Exhaust Gas Temperature", "Fuel Flow", 
        "Thrust Setting", "Fuel on Board", "Flap Setting", 
        "Airspeed", "Climb Rate", "Heading Indicator", 
        "Altimeter", "Hydraulic Warning", "Landing Gear", 
        "Autopilot Status"
    ]
    
    frequency_options = [
        "Frequent", 
        "Occasional", 
        "Rare"
    ]

    # Initialize session state
    if "frequency_assignments" not in st.session_state:
        st.session_state.frequency_assignments = {opt: [] for opt in frequency_options}

    # Frequency Assignment
    cols = st.columns(3)
    
    # Create a dropdown for each frequency category
    for i, freq in enumerate(frequency_options):
        with cols[i]:
            assigned = st.multiselect(
                f"{freq}:",
                elements,
                default=st.session_state.frequency_assignments.get(freq, []),
                key=f"freq_{i}"
            )
            st.session_state.frequency_assignments[freq] = assigned

    # Validation (no duplicates)
    all_assigned = []
    for items in st.session_state.frequency_assignments.values():
        all_assigned.extend(items)
    
    duplicates = set([x for x in all_assigned if all_assigned.count(x) > 1])
    if duplicates:
        st.error(f"Error: Duplicate assignments for {duplicates}. Remove extras.")
    elif len(all_assigned) != len(elements):
        st.warning(f"Not all elements assigned ({len(all_assigned)}/{len(elements)})")

    # Store results
    st.session_state.responses.update({
        "frequency_assignments": st.session_state.frequency_assignments,
    })

def create_sequence_of_use_questions():
    st.subheader("23. Sequence of Use")
    st.markdown("""
    **Instructions:**  
    1. Click "Show Cockpit Display" to reveal the image.  
    2. Note the order in which your eyes are drawn to elements.  
    3. Answer the dropdown questions about your viewing sequence.  
    """)

    # Load image
    cockpit_img = Image.open("ecam_1.png")
    elements = [
        "EPR", "EGT", "N1", 
        "N2", "FF", "TOGA", "FOB", "Flaps Setting",
        "Text Information Left", "Text Information Right"
    ]

    # Initialize session state
    if "sequence_test_started" not in st.session_state:
        st.session_state.sequence_test_started = False
        st.session_state.sequence_answers = {}

    # --- Image Display ---
    if not st.session_state.sequence_test_started:
        if st.button("Show Cockpit Display"):
            st.session_state.sequence_test_started = True
            st.rerun()
    else:
        st.image(cockpit_img, caption="Cockpit Display - Observe Your Natural Viewing Sequence", use_container_width=True)
        st.success("Image locked. Answer the questions below.")

    st.write("Credit: https://en.wikipedia.org/wiki/Electronic_centralised_aircraft_monitor")

    # Sequence Questions    
    # Question 1
    first_noticed = st.selectbox(
        "What did you notice FIRST?",
        ["Select..."] + elements,
        key="sequence_first"
    )
    
    # Question 2 (dynamic options)
    second_options = ["Select..."] + [e for e in elements if e != first_noticed] if first_noticed != "Select..." else elements
    second_noticed = st.selectbox(
        "What did you notice SECOND?",
        second_options,
        key="sequence_second",
        disabled=(first_noticed == "Select...")
    )
    
    # Question 3 (dynamic options)
    if first_noticed != "Select..." and second_noticed != "Select...":
        third_options = ["Select..."] + [e for e in elements if e not in [first_noticed, second_noticed]]
    else:
        third_options = ["Select..."] + elements
        
    third_noticed = st.selectbox(
        "What did you notice THIRD?",
        third_options,
        key="sequence_third",
        disabled=(second_noticed == "Select...")
    )

    # Store results when all questions are answered
    if (first_noticed != "Select..." and 
        second_noticed != "Select..." and 
        third_noticed != "Select..."):
        
        st.session_state.sequence_answers = {
            "first": first_noticed,
            "second": second_noticed,
            "third": third_noticed
        }
        
        st.session_state.responses.update({
            "viewing_sequence": st.session_state.sequence_answers,
            "sequence_test_completed": True
        })

def create_importance_allocation_questions():
    st.subheader("24. Importance")
    st.markdown("""
    **Instructions:**  
    - Allocate percentage values to determine the ideal size for each element.  
    - Total must sum to 100%.
    """)

    # Define elements (customize as needed)
    elements = [
        "EPR (Engine Pressure Ratio)",
        "EGT (Exhaust Gas Temperature)",
        "N1 (Fan Speed)",
        "N2 (Core Speed)",
        "FF (Fuel Flow)",
        "Thrust Mode",
        "FOB (Fuel On Board)",
        "Flaps Setting",
        "Text Information"
    ]

    # Initialize session state
    if "importance_allocations" not in st.session_state:
        st.session_state.importance_allocations = {elem: 0 for elem in elements}

    # Allocation Interface
    total = 0
    allocations = {}
    
    for elem in elements:
        allocations[elem] = st.slider(
            f"{elem}:",
            min_value=0,
            max_value=100,
            value=st.session_state.importance_allocations.get(elem, 10),  # Default 10%
            key=f"alloc_{elem}",
            help="Slide to adjust your answer. Stop when you feel the size allocation for the current element is just about right."
        )
        total += allocations[elem]

    # --- Validation & Auto-Adjustment ---
    st.write(f"Total Allocated: {total}%")
    if total != 100:
        if total > 100:
            st.error("Over-allocated! Reduce some values.")
        else:
            st.warning("Under-allocated! Add remaining percentage.")
    else:
        st.success("Perfect allocation! (100%)")

    # Store results
    st.session_state.importance_allocations = allocations
    st.session_state.responses.update({
        "importance_allocations": allocations,
        "total_allocation": total
    })

def create_visibility_questions():
    st.subheader("25. Visibility")
    st.markdown("""
    **Instructions:**  
    - Rate the visibility of each element under different conditions (1 = Invisible, 5 = Perfectly Visible).  
    """)

    # Define elements to evaluate
    elements = [
        "EPR Gauge", 
        "EGT Indicator", 
        "N1 Fan Speed",
        "Fuel Flow Readout",
        "Flaps Setting"
    ]

    # Load base image
    base_img = Image.open("ecam.png")

    # Condition 1: Daylight
    st.write("**A. Ideal Lighting (Daylight)**")
    col1_day, col2_day = st.columns(2)
    with col1_day:
        st.image(base_img, use_container_width=True, caption="Daylight Simulation")
    with col2_day:
        daylight_ratings = {}
        for elem in elements:
            daylight_ratings[elem] = st.slider(
                f"{elem} visibility in daylight:",
                1, 5, 3,
                key=f"day_{elem}",
                help="Slide to adjust your answer."
            )

    # Condition 2: Low Light
    st.write("**B. Low Light (Night Operations)**")
    lowlight_img = base_img.point(lambda p: p * 0.4)  # Darken
    col1_night, col2_night = st.columns(2)
    with col1_night:
        st.image(lowlight_img, use_container_width=True, caption="Night Simulation")
    with col2_night:
        night_ratings = {}
        for elem in elements:
            night_ratings[elem] = st.slider(
                f"{elem} visibility at night:",
                1, 5, 3,
                key=f"night_{elem}",
                help="Slide to adjust your answer."
            )

    # Condition 3: Emergency Lighting
    st.write("**C. Emergency Lighting (Red Ambient)**")
    red_img = base_img.convert("RGB")
    r, g, b = red_img.split()
    red_img = Image.merge("RGB", (r, g.point(lambda p: p * 0.3), b.point(lambda p: p * 0.3)))
    col1_red, col2_red = st.columns(2)
    with col1_red:
        st.image(red_img, use_container_width=True, caption="Emergency Lighting")
    with col2_red:
        red_ratings = {}
        for elem in elements:
            red_ratings[elem] = st.slider(
                f"{elem} visibility in red light:",
                1, 5, 3,
                key=f"red_{elem}",
                help="Slide to adjust your answer."
            )

    st.write("Image Credit: Anja Faulhaber, 2021")

    # Store all results
    st.session_state.visibility_ratings = {
        "Daylight": daylight_ratings,
        "Night": night_ratings,
        "Emergency": red_ratings
    }
    st.session_state.responses.update({
        "visibility_assessment": st.session_state.visibility_ratings
    })

def create_reachability_questions():
    st.subheader("26. Reachability")
    st.markdown("""
    **Instructions:**  
    - Please make sure that your current seating position is comfortable.  
    - Please approximate how easily you can reach your current device.  
    """)

    # Device Reachability
    col1, col2 = st.columns(2)
    with col1:
        seat_height = st.slider(
            "Seat Height (cm from floor):",
            1, 150, 75,
            help="Slide to adjust your answer. Stop when you think the value is an approximation of your seat height."
        )
        arm_length = st.slider(
            "Arm Length (cm):",
            50, 100, 75,
            help="Slide to adjust your answer. Stop when you think the value is an approximation of your arm length."
        )
    with col2:
        viewing_angle = st.slider(
            "Viewing Angle (eye to screen angle in degrees):",
            0, 90, 45,
            help="Slide to adjust your answer. Stop when you think the value is an approximation of your viewing angle (neglect negative angle definition)."
        )
        keyboard_reach = st.slider(
            "Keyboard Reach (body to keyboard distance in cm):",
            35, 60, 45,
            help="Slide to adjust your answer. Stop when you think the value is an approximation of your keyboard reach."
        )

    # Store posture profile
    device_reachability = {
        "seat_height": seat_height,
        "arm_length": arm_length,
        "viewing_angle": viewing_angle,
        "keyboard_reach": keyboard_reach
    }

def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten nested dictionaries for CSV storage
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to strings for CSV
            items.append((new_key, str(v)))
        else:
            items.append((new_key, v))
    return dict(items)

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
    - 🙏 I ask for your patience when filling out the form, sometimes the website needs to update twice to record your answer.

    These conditions help minimize distractions, perception errors, or visibility-related inconsistencies.

    Thank you for your careful participation.
    """)

    if not st.session_state.submitted:
        # Add profession question before Gestalt Principles
        st.session_state.responses["profession"] = st.selectbox(
            "**What is your current profession or field of work?**",
            ["Pilot", "Operators", "Aerospace Engineer", "UI/UX Designer", "Human Factors Engineers", 
             "Researcher", "Student", "Other (please specify)"],
            key="profession"
        )
        if st.session_state.responses["profession"] == "Other (please specify)":
            st.session_state.responses["profession_other"] = st.text_input("Please specify your profession")
    
    if not st.session_state.submitted:
        # Gestalt Principles Section
        st.header("Gestalt Design Laws")
        st.markdown("""
        Gestalt Design Laws describe how humans perceive visual elements as unified wholes.
        """)
        
        create_closure_visualization()
        create_continuity_visualization()
        create_proximity_visualization()
        create_experience_visualization()
        create_pragnanz_visualization()
        create_similarity_visualization()
        create_symmetry_visualization()
        create_common_fate_questions()

        # Wickens' Principles Section
        st.header("Wickens' Principles")
        st.markdown("""
        Wickens' Principles focus on human information processing and cognitive ergonomics.
        """)

        create_legibility_questions()
        create_absolute_judgement_questions()
        create_topdown_processing_questions()
        create_redundancy_gain_questions()
        create_discriminability_questions()
        create_pictorial_realism_questions()
        create_moving_parts_visualization()
        create_access_cost_visualization()
        create_proximity_compatibility_questions()
        create_multiple_resources_questions()
        create_predictive_aiding_questions()
        create_memory_replacement_visualization()
        create_consistency_questions()

        # Ergonomic Considerations Section
        st.header("Ergonomic Considerations")
        st.markdown("""
        Ergonomic Considerations address physical and cognitive fit between users and designs.
        """)

        create_frequency_of_use_questions()
        create_sequence_of_use_questions()
        create_importance_allocation_questions()
        create_visibility_questions()
        create_reachability_questions()

        # Additional Comments
        st.session_state.responses["comments"] = st.text_area(
            "Additional comments or observations:",
            key="comments"
        )
        
        # Submit button (now outside any form)
        submitted = st.button("Submit Survey")
            
        if submitted:
            # Validate all responses are complete (optional)
            if not st.session_state.responses.get("profession"):
                st.error("Please complete all required questions")
            else:
                st.session_state.submitted = True
                
                # Save responses to CSV (ensure all nested dictionaries are flattened)
                flat_responses = flatten_dict(st.session_state.responses)
                csv_filename = save_responses_to_csv(flat_responses)
                
                # Send email
                email_sent = send_email_with_results(flat_responses)
                
                if email_sent:
                    st.success("Survey submitted successfully! Results have been saved and emailed.")
                else:
                    st.success("Survey submitted successfully! (Email notification failed)")
                
                st.download_button(
                    label="Download Your Responses",
                    data=pd.DataFrame([flat_responses]).to_csv(index=False),
                    file_name=csv_filename,
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
