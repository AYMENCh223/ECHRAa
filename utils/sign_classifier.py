import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
import os

class SignClassifier:
    def __init__(self, model_path="Model/keras_model.h5", labels_path="data/labels.txt"):
        """
        Initialize the Sign Language Classifier
        
        Args:
            model_path: Path to the trained Keras model
            labels_path: Path to the labels file
        """
        self.model_path = model_path
        self.labels_path = labels_path
        self.model = None
        self.labels = []
        self.img_size = 224  # Standard input size
        
        # Load model and labels
        self.load_model()
        self.load_labels()
        
    def load_model(self):
        """Load the trained Keras model"""
        try:
            if os.path.exists(self.model_path):
                self.model = keras.models.load_model(self.model_path)
                print(f"Model loaded successfully from {self.model_path}")
            else:
                print(f"Model file not found at {self.model_path}")
                # Create a simple dummy model for testing
                self.create_dummy_model()
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.create_dummy_model()
            
    def create_dummy_model(self):
        """Create a dummy model for testing purposes"""
        print("Creating dummy model for testing...")
        inputs = keras.Input(shape=(self.img_size, self.img_size, 3))
        x = keras.layers.GlobalAveragePooling2D()(inputs)
        x = keras.layers.Dense(64, activation='relu')(x)
        outputs = keras.layers.Dense(35, activation='softmax')(x)  # 35 classes
        
        self.model = keras.Model(inputs=inputs, outputs=outputs)
        
        # Initialize with random weights
        dummy_input = np.random.random((1, self.img_size, self.img_size, 3))
        _ = self.model(dummy_input)
        
    def load_labels(self):
        """Load class labels from file"""
        try:
            if os.path.exists(self.labels_path):
                with open(self.labels_path, 'r', encoding='utf-8') as f:
                    self.labels = [line.strip() for line in f.readlines()]
                print(f"Loaded {len(self.labels)} labels")
            else:
                print(f"Labels file not found at {self.labels_path}")
                # Create default labels
                self.create_default_labels()
        except Exception as e:
            print(f"Error loading labels: {str(e)}")
            self.create_default_labels()
            
    def create_default_labels(self):
        """Create default Arabic labels"""
        arabic_letters = ["أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "ه", "و", "ي"]
        common_phrases = ["نعم", "لا", "شكراً", "أين", "أنا", "أنت", "السلام عليكم"]
        self.labels = arabic_letters + common_phrases
        
        # Save labels to file
        os.makedirs(os.path.dirname(self.labels_path), exist_ok=True)
        with open(self.labels_path, 'w', encoding='utf-8') as f:
            for label in self.labels:
                f.write(label + '\n')
        print(f"Created default labels file with {len(self.labels)} labels")
        
    def preprocess_image(self, img):
        """
        Preprocess image for model prediction
        
        Args:
            img: Input image (BGR format from OpenCV)
            
        Returns:
            Preprocessed image array
        """
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize image to model input size
        img_resized = cv2.resize(img_rgb, (self.img_size, self.img_size))
        
        # Normalize pixel values to [0, 1]
        img_normalized = img_resized.astype(np.float32) / 255.0
        
        # Add batch dimension
        img_batch = np.expand_dims(img_normalized, axis=0)
        
        return img_batch
        
    def get_prediction(self, img, draw=True):
        """
        Get prediction for the input image
        
        Args:
            img: Input image (BGR format)
            draw: Whether to draw prediction on image
            
        Returns:
            Tuple: (prediction_probabilities, predicted_class_index)
        """
        if self.model is None:
            return np.zeros(len(self.labels)), 0
            
        try:
            # Preprocess image
            processed_img = self.preprocess_image(img)
            
            # Get prediction
            predictions = self.model.predict(processed_img, verbose=0)
            prediction_probs = predictions[0]  # Remove batch dimension
            
            # Get the class with highest probability
            predicted_class = np.argmax(prediction_probs)
            
            # Draw prediction on image if requested
            if draw and predicted_class < len(self.labels):
                label = self.labels[predicted_class]
                confidence = prediction_probs[predicted_class]
                
                # Draw prediction text
                text = f"{label}: {confidence:.2f}"
                cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, (0, 255, 0), 2, cv2.LINE_AA)
                
                # Draw confidence bar
                bar_width = int(confidence * 200)
                cv2.rectangle(img, (10, 50), (10 + bar_width, 70), (0, 255, 0), -1)
                cv2.rectangle(img, (10, 50), (210, 70), (255, 255, 255), 2)
            
            return prediction_probs, predicted_class
            
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return np.zeros(len(self.labels)), 0
    
    def get_top_predictions(self, img, top_k=3):
        """
        Get top-k predictions for the input image
        
        Args:
            img: Input image (BGR format)
            top_k: Number of top predictions to return
            
        Returns:
            List of tuples: [(label, confidence), ...]
        """
        prediction_probs, _ = self.get_prediction(img, draw=False)
        
        # Get top-k indices
        top_indices = np.argsort(prediction_probs)[-top_k:][::-1]
        
        # Create list of (label, confidence) pairs
        top_predictions = []
        for idx in top_indices:
            if idx < len(self.labels):
                label = self.labels[idx]
                confidence = prediction_probs[idx]
                top_predictions.append((label, confidence))
        
        return top_predictions
    
    def is_confident(self, img, threshold=0.7):
        """
        Check if the model is confident about its prediction
        
        Args:
            img: Input image
            threshold: Confidence threshold
            
        Returns:
            Boolean: True if confident, False otherwise
        """
        prediction_probs, predicted_class = self.get_prediction(img, draw=False)
        return prediction_probs[predicted_class] >= threshold
