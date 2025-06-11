"""
Create Lightweight Model for Arabic Sign Language Recognition
This script creates a very simple model that loads quickly without threading issues.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple configuration
CONFIG = {
    'IMAGE_SIZE': 64,  # Smaller size for faster processing
    'NUM_CLASSES': 28,  # Arabic letters only
    'MODEL_DIR': 'Model',
    'MODEL_NAME': 'keras_model.h5',
    'LABELS_FILE': 'data/labels.txt'
}

# Arabic letters only (simpler)
ARABIC_LETTERS = [
    "أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", 
    "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "ه", "و", "ي"
]

def ensure_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs(CONFIG['MODEL_DIR'], exist_ok=True)
    os.makedirs(os.path.dirname(CONFIG['LABELS_FILE']), exist_ok=True)

def create_labels_file():
    """Create labels file with Arabic letters."""
    with open(CONFIG['LABELS_FILE'], 'w', encoding='utf-8') as f:
        for label in ARABIC_LETTERS:
            f.write(label + '\n')
    logger.info(f"Labels file created with {len(ARABIC_LETTERS)} labels")

def create_minimal_model():
    """Create the smallest possible functional model."""
    model = keras.Sequential([
        layers.Input(shape=(CONFIG['IMAGE_SIZE'], CONFIG['IMAGE_SIZE'], 3)),
        layers.Rescaling(1./255),
        layers.Conv2D(8, 8, strides=4, activation='relu'),
        layers.Conv2D(16, 4, strides=2, activation='relu'),
        layers.GlobalAveragePooling2D(),
        layers.Dense(32, activation='relu'),
        layers.Dense(CONFIG['NUM_CLASSES'], activation='softmax')
    ])
    
    # Compile immediately
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Initialize with dummy data
    dummy_input = tf.random.normal((1, CONFIG['IMAGE_SIZE'], CONFIG['IMAGE_SIZE'], 3))
    _ = model(dummy_input)
    
    return model

def main():
    """Create and save the lightweight model."""
    logger.info("Creating lightweight Arabic Sign Language model...")
    
    # Ensure directories exist
    ensure_directories()
    
    # Create labels file
    create_labels_file()
    
    # Create minimal model
    model = create_minimal_model()
    
    # Save the model
    model_path = os.path.join(CONFIG['MODEL_DIR'], CONFIG['MODEL_NAME'])
    model.save(model_path, save_format='h5')
    
    logger.info(f"Model saved to {model_path}")
    print(f"Model summary:")
    model.summary()
    
    # Verify the model works
    test_input = np.random.random((1, CONFIG['IMAGE_SIZE'], CONFIG['IMAGE_SIZE'], 3))
    prediction = model.predict(test_input, verbose=0)
    logger.info(f"Test prediction shape: {prediction.shape}")
    logger.info("Model creation completed successfully!")

if __name__ == "__main__":
    main()