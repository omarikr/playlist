import re

# Read config
with open('config.py', 'r') as f:
    config_content = f.read()
    match = re.search(r'color\s*=\s*["\']([^"\']+)["\']', config_content)
    if match:
        icon_color = match.group(1)
    else:
        icon_color = "#126317"  # Default dark green

# Read HTML
with open('index.html', 'r') as f:
    html_content = f.read()

# Replace icon colors in HTML
# Control buttons (prev, next, play/pause icons)
html_content = re.sub(
    r'<button id="prevBtn" class="control-btn [^"]*" style="color: [^"]+">',
    f'<button id="prevBtn" class="control-btn" style="color: {icon_color}">',
    html_content
)
html_content = re.sub(
    r'<button id="nextBtn" class="control-btn [^"]*" style="color: [^"]+">',
    f'<button id="nextBtn" class="control-btn" style="color: {icon_color}">',
    html_content
)
html_content = re.sub(
    r'<button id="playPauseBtn" class="play-btn [^"]*" style="color: [^"]+">',
    f'<button id="playPauseBtn" class="play-btn w-14 h-14 sm:w-16 sm:h-16 rounded-full flex items-center justify-center" style="color: {icon_color}">',
    html_content
)

# Volume icons
html_content = re.sub(
    r'<svg class="w-4 h-4 sm:w-5 sm:h-5" style="color: [^"]+"',
    f'<svg class="w-4 h-4 sm:w-5 sm:h-5" style="color: {icon_color}"',
    html_content
)

# Effects toggle button
html_content = re.sub(
    r'<button id="effectsToggle" class="toggle-btn [^"]*" style="color: [^"]+">',
    f'<button id="effectsToggle" class="toggle-btn fixed bottom-4 right-4 md:bottom-6 md:right-6 w-12 h-12 md:w-14 md:h-14 rounded-full bg-white/20 flex items-center justify-center backdrop-blur-md" style="color: {icon_color}">',
    html_content
)

# Album art background
html_content = re.sub(
    r'\.album-art \{[^}]*background: linear-gradient\([^)]+\)[^}]*\}',
    f'.album-art {{\n            background: linear-gradient(135deg, {icon_color}80 0%, {icon_color}60 50%, {icon_color}40 100%);\n            box-shadow: 0 8px 32px {icon_color}40;\n            backdrop-filter: blur(10px);\n        }}',
    html_content
)

# Progress fill
html_content = re.sub(
    r'\.progress-fill \{[^}]*background: linear-gradient\([^)]+\)[^}]*\}',
    f'.progress-fill {{\n            background: linear-gradient(90deg, {icon_color}90, {icon_color}b0);\n        }}',
    html_content
)

# Write updated HTML
with open('index.html', 'w') as f:
    f.write(html_content)

print(f"Updated icon colors to {icon_color}")
