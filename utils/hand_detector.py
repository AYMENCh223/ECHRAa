import cv2
import mediapipe as mp
import numpy as np

class HandDetector:
    def __init__(self, static_image_mode=False, max_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initialize the HandDetector
        
        Args:
            static_image_mode: Whether to treat input images as static images
            max_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
        """
        self.static_image_mode = static_image_mode
        self.max_hands = max_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.static_image_mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Store the results for further processing
        self.results = None
        
    def find_hands(self, img, draw=True):
        """
        Find hands in the image and optionally draw landmarks
        
        Args:
            img: Input image (BGR format)
            draw: Whether to draw hand landmarks
            
        Returns:
            Image with hand landmarks drawn (if draw=True)
        """
        # Convert BGR to RGB for MediaPipe
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process the image
        self.results = self.hands.process(img_rgb)
        
        # Draw landmarks if hands are detected and draw is True
        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
                
        return img
    
    def find_position(self, img, hand_no=0, draw=True):
        """
        Find the position of hand landmarks
        
        Args:
            img: Input image
            hand_no: Which hand to get landmarks for (0 for first hand)
            draw: Whether to draw landmark points
            
        Returns:
            List of landmark positions [(id, x, y), ...]
        """
        x_list = []
        y_list = []
        bbox = []
        landmark_list = []
        
        if self.results.multi_hand_landmarks:
            if hand_no < len(self.results.multi_hand_landmarks):
                my_hand = self.results.multi_hand_landmarks[hand_no]
                
                for id, lm in enumerate(my_hand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    x_list.append(cx)
                    y_list.append(cy)
                    landmark_list.append([id, cx, cy])
                    
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
                
                # Calculate bounding box
                if x_list and y_list:
                    x_min, x_max = min(x_list), max(x_list)
                    y_min, y_max = min(y_list), max(y_list)
                    bbox = [x_min, y_min, x_max, y_max]
                    
                    if draw:
                        cv2.rectangle(img, (x_min - 20, y_min - 20), 
                                    (x_max + 20, y_max + 20), (0, 255, 0), 2)
                        
        return landmark_list
    
    def fingers_up(self, landmark_list):
        """
        Determine which fingers are up
        
        Args:
            landmark_list: List of hand landmarks
            
        Returns:
            List of 1s and 0s indicating which fingers are up [thumb, index, middle, ring, pinky]
        """
        if len(landmark_list) != 21:
            return [0, 0, 0, 0, 0]
            
        fingers = []
        tip_ids = [4, 8, 12, 16, 20]  # Fingertip landmark IDs
        
        # Thumb (different logic due to orientation)
        if landmark_list[tip_ids[0]][1] > landmark_list[tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
            
        # Other fingers
        for id in range(1, 5):
            if landmark_list[tip_ids[id]][2] < landmark_list[tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
                
        return fingers
    
    def find_distance(self, p1, p2, img=None, draw=True):
        """
        Find distance between two landmarks
        
        Args:
            p1: First point ID
            p2: Second point ID
            img: Image to draw on
            draw: Whether to draw the line
            
        Returns:
            Distance, image with line drawn, center point
        """
        if self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) > 0:
                hand = self.results.multi_hand_landmarks[0]
                
                h, w, c = img.shape if img is not None else (1, 1, 1)
                
                x1, y1 = int(hand.landmark[p1].x * w), int(hand.landmark[p1].y * h)
                x2, y2 = int(hand.landmark[p2].x * w), int(hand.landmark[p2].y * h)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                
                if img is not None and draw:
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                    cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                
                length = np.hypot(x2 - x1, y2 - y1)
                return length, img, [x1, y1, x2, y2, cx, cy]
        
        return 0, img, []
    
    def get_hand_type(self, hand_no=0):
        """
        Get the type of hand (Left or Right)
        
        Args:
            hand_no: Which hand to check
            
        Returns:
            String: "Left" or "Right" or None
        """
        if self.results.multi_handedness:
            if hand_no < len(self.results.multi_handedness):
                return self.results.multi_handedness[hand_no].classification[0].label
        return None
