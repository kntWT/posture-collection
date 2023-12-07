import math as m
import mediapipe as mp
import cv2

# Calculate distance
def findDistance(x1, y1, x2, y2):
    dist = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist


# Calculate angle.
def findAngle(x1, y1, x2, y2):
    theta = m.acos((y2 - y1) * (-y1) / (m.sqrt(
        (x2 - x1) ** 2 + (y2 - y1) ** 2) * y1))
    degree = 180 / m.pi * theta
    return degree


"""
Function to send alert. Use this function to send alert when bad posture detected.
Feel free to get creative and customize as per your convenience.
"""

def sendWarning(x):
    pass


# =============================CONSTANTS and INITIALIZATIONS=====================================#
# Initilize frame counters.
good_frames = 0
bad_frames = 0

# Font type.
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 5
font_thickness = 10

# Colors.
blue = (255, 127, 0)
red = (50, 50, 255)
green = (127, 255, 0)
black = (0, 0, 0)
dark_blue = (127, 20, 0)
light_green = (127, 233, 100)
yellow = (0, 255, 255)
pink = (255, 0, 255)

expand_offset = 400

# Initialize mediapipe pose class.
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
# ===============================================================================================#

# Calculate posture. returns None if not detected.
# image: np.ndarray
# return: image, neck_angle, torso_angle | None
def calculate_posture(image, neck_angle_offset: float = 0.0):
    # Convert the BGR image to RGB.
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    keypoints = pose.process(image)
    h, w = image.shape[:2]
    # Convert the image back to BGR.
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Use lm and lmPose as representative of the following methods.
    lm = keypoints.pose_landmarks
    lmPose = mp_pose.PoseLandmark
    if lm is None or lmPose is None:
        return None

    # Acquire the landmark coordinates.
    # Once aligned properly, left or right should not be a concern.      
    # Left shoulder.
    l_shldr_x = int(lm.landmark[lmPose.LEFT_SHOULDER].x * w)
    l_shldr_y = int(lm.landmark[lmPose.LEFT_SHOULDER].y * h)
    # Right shoulder
    r_shldr_x = int(lm.landmark[lmPose.RIGHT_SHOULDER].x * w)
    r_shldr_y = int(lm.landmark[lmPose.RIGHT_SHOULDER].y * h)
    # Left ear.
    l_ear_x = int(lm.landmark[lmPose.LEFT_EAR].x * w)
    l_ear_y = int(lm.landmark[lmPose.LEFT_EAR].y * h)
    # Left hip.
    l_hip_x = int(lm.landmark[lmPose.LEFT_HIP].x * w)
    l_hip_y = int(lm.landmark[lmPose.LEFT_HIP].y * h)

    # Calculate distance between left shoulder and right shoulder points.
    offset = findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)

    # Assist to align the camera to point at the side view of the person.
    # Offset threshold 30 is based on results obtained from analysis over 100 samples.
    if offset < 100:
        cv2.putText(image, str(int(offset)) + ' Aligned', (w - 150, 30), font, font_scale, black, font_thickness)
    else:
        cv2.putText(image, str(int(offset)) + ' Not Aligned', (w - 150, 30), font, font_scale, red, font_thickness)

    # Calculate angles.
    neck_inclination = findAngle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
    torso_inclination = findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)
    neck_angle: float = neck_inclination - neck_angle_offset

    # Draw landmarks.
    cv2.circle(image, (l_shldr_x, l_shldr_y), 7, yellow, -1)
    cv2.circle(image, (l_ear_x, l_ear_y), 7, yellow, -1)

    # Let's take y - coordinate of P3 100px above x1,  for display elegance.
    # Although we are taking y = 0 while calculating angle between P1,P2,P3.
    cv2.circle(image, (l_shldr_x, l_shldr_y - expand_offset), 7, yellow, -1)
    cv2.circle(image, (r_shldr_x, r_shldr_y), 7, pink, -1)
    cv2.circle(image, (l_hip_x, l_hip_y), 7, yellow, -1)

    # Similarly, here we are taking y - coordinate 100px above x1. Note that
    # you can take any value for y, not necessarily 100 or 200 pixels.
    cv2.circle(image, (l_hip_x, l_hip_y - expand_offset), 7, yellow, -1)

    # Put text, Posture and angle inclination.
    # Text string for display.
    angle_text_string = 'Neck : ' + str(int(neck_angle)) + '  Torso : ' + str(int(torso_inclination))

    # Determine whether good posture or bad posture.
    # The threshold angles have been set based on intuition.
    cv2.putText(image, angle_text_string, (10, 100), font, font_scale, red, font_thickness)
    cv2.putText(image, str(int(neck_angle)), (l_shldr_x + 10, l_shldr_y), font, font_scale, red, font_thickness)
    cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, font_scale, red, font_thickness)

    # Join landmarks.
    cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), red, 4)
    cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - expand_offset), red, 4)
    cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), red, 4)
    cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - expand_offset), red, 4)

    return image, neck_angle, torso_inclination