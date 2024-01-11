import cv2
import numpy as np

def get_dominant_color(bgr_pixel):
    b, g, r = bgr_pixel
    if r >= g and r >= b and r >= 128:  # Check for sufficiently bright red
        return "red"
    elif g > r and g > b and g >= 128:  # Check for sufficiently bright green
        return "green"
    elif b >= r and b >= g and b >= 128:  # Check for sufficiently bright blue
        return "blue"
    elif r >= g > b and r >= 128:  # Check for purple (red > green > blue)
        return "purple"  # Added condition for purple
    elif r >= b and b >= g:
        return "orange"
    elif g >= r and r >= b:
        return "yellow"
    # Add condition for brown
    elif b >= r and b >= g and b >= 128:  # Check for sufficiently bright blue with some red/green
        return "brown"
    else:
        return "black"  # Set black as the dominant color for other pixels
    
def calculate_adaptive_resize_factor(frame):
    # Combine multiple techniques for a robust calculation
    resize_factor1 = analyze_frequency_content(frame)  # Adjusts for areas with high-frequency details
    resize_factor2 = analyze_edge_density(frame)  # Differentiates near and far objects based on edge presence
    # Blend factors using weights based on your priorities
    resize_factor = 0.7 * resize_factor1 + 0.3 * resize_factor2
    return resize_factor

def analyze_frequency_content(frame):
    # Calculate the frame's Fourier transform
    fft = cv2.dft(frame, dft_flags=cv2.DFT_COMPLEX_OUTPUT)
    # Analyze magnitude spectrum to identify high-frequency areas
    mag_spectrum = np.abs(fft)
    high_freq_mask = cv2.threshold(mag_spectrum, 20, 255, cv2.THRESH_BINARY)[1]  # Adjust threshold levels
    # Calculate a resize factor based on the mask density
    resize_factor = 1 + (np.count_nonzero(high_freq_mask) / np.prod(high_freq_mask.shape)) * 0.5
    return resize_factor

def analyze_edge_density(frame):
    # Apply Canny edge detection
    edges = cv2.Canny(frame, 50, 150)
    # Calculate edge density in different regions (e.g., foreground, background)
    foreground_mask = ...  # Define your foreground mask (e.g., based on object detection or segmentation)
    foreground_edge_density = np.count_nonzero(edges & foreground_mask) / np.count_nonzero(foreground_mask)
    background_edge_density = np.count_nonzero(edges) / np.prod(edges.shape)
    # Determine resize factor based on edge density difference
    if foreground_edge_density > background_edge_density:
        resize_factor = 1 - (foreground_edge_density - background_edge_density) * 0.5
    else:
        resize_factor = 1 + (background_edge_density - foreground_edge_density) * 0.3
    return resize_factor

def create_ascii_frame(frame, gray_chars, bg_colors, resize_factor=0.1):
    """Converts a video frame into an ASCII art representation."""
    resized = cv2.resize(frame, (int(frame.shape[1] * resize_factor), int(frame.shape[0] * resize_factor)))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    ascii_frame = ''
    for i in range(0, resized.shape[0], 2):
        for j in range(0, resized.shape[1], 1):
            color = get_dominant_color(resized[i, j])
            bg_color_code = bg_colors.get(color, '')  # Use escape sequence for detected color
            cell_avg = np.mean(gray[i:i+2, j:j+1])
            index = min(int(cell_avg / 255 * len(gray_chars)), len(gray_chars) - 1)
            ascii_frame += bg_color_code + gray_chars[index] + '\033[0m'
        ascii_frame += '\n'
    return ascii_frame

def create_color_map(frame, color_map_size):
    """Creates a color map overlaying the ASCII art."""
    resized = cv2.resize(frame, (color_map_size, color_map_size))
    color_map = np.zeros((color_map_size, color_map_size, 3), dtype=np.uint8)
    for i in range(color_map_size):
        for j in range(color_map_size):
            color_map[i, j] = resized[i, j]
    return cv2.cvtColor(color_map, cv2.COLOR_BGR2RGB)  # Convert to RGB for display

def create_combined_frame(ascii_frame, color_map):
    """Combines ASCII art and color map into a single frame."""
    # Example combination: Display ASCII art above color map
    combined_frame = np.concatenate((color_map, np.full((color_map.shape[0], color_map.shape[1], 3), 255)), axis=1)
    for i in range(len(ascii_frame)):
        for j in range(len(ascii_frame[0])):
            combined_frame[i, j * 2, :] = 0  # Set background for ASCII characters
            combined_frame[i, j * 2 + 1, :] = 255
            combined_frame[i, j * 2 + 1, 0] = 0  # Set red channel to 0 for better visibility
            combined_frame[i, j * 2 + 1, 1] = 0  # Set green channel to 0 for better visibility
            combined_frame[i, j * 2 + 1, 2] = ord(ascii_frame[i][j]) * 4  # Adjust character brightness
    return combined_frame

def display_ascii_art(ascii_frame):
    """Clears the console and prints the ASCII art frame."""
    print("\033[H\033[J", end="")  # Clear console
    print(ascii_frame)

def main():
    """Main function to capture video and display ASCII art."""
    askVideoPath = str(input("Enter absolute path to video file without quotation marks at the start and end: "))
    cap = cv2.VideoCapture(f"{askVideoPath}")

    red_chars = ".,-~:;=!*#$@"
    green_chars = "+oO08@"
    blue_chars = ">]`^v"
    gray_chars = " ░▒▓█"
    bg_colors = {
    "red": '\033[41m',
    "green": '\033[42m',
    "blue": '\033[44m',
    "yellow": '\033[43m',
    "purple": '\033[45m',  # Added for purple
    "orange": '\033[33m',
    "cyan": '\033[36m',
    "brown": '\033[46m',  # Adjusted for brown
}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read frame from video.")
            break

        ascii_frame = create_ascii_frame(frame, gray_chars, bg_colors)
        display_ascii_art(ascii_frame)

        if cv2.waitKey(0) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()