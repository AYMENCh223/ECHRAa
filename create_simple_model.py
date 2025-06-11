"""
Create Simple TensorFlow Model for Arabic Sign Language Recognition
This script creates a lightweight model for development and testing purposes.
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

# Model configuration
CONFIG = {
    'IMAGE_SIZE': 224,  # Standard input size for vision models
    'NUM_CLASSES': 35,  # 28 Arabic letters + 7 common phrases
    'BATCH_SIZE': 32,
    'LEARNING_RATE': 0.001,
    'DROPOUT_RATE': 0.3,
    'MODEL_DIR': 'Model',
    'MODEL_NAME': 'keras_model.h5',
    'TFLITE_NAME': 'model.tflite',
    'LABELS_FILE': 'data/labels.txt'
}

# Arabic letters and common phrases
ARABIC_LETTERS = [
    "أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", 
    "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "ه", "و", "ي"
]

COMMON_PHRASES = [
    "نعم", "لا", "شكراً", "أين", "أنا", "أنت", "السلام عليكم"
]

def ensure_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs(CONFIG['MODEL_DIR'], exist_ok=True)
    os.makedirs(os.path.dirname(CONFIG['LABELS_FILE']), exist_ok=True)
    logger.info("Directories created/verified")

def create_labels_file():
    """Create labels file with Arabic letters and common phrases."""
    all_labels = ARABIC_LETTERS + COMMON_PHRASES
    
    with open(CONFIG['LABELS_FILE'], 'w', encoding='utf-8') as f:
        for label in all_labels:
            f.write(label + '\n')
    
    logger.info(f"Labels file created with {len(all_labels)} labels at {CONFIG['LABELS_FILE']}")
    return all_labels

def create_simple_cnn_model():
    """
    Create a simple CNN model for sign language recognition.
    This model is designed to be lightweight and fast for development/testing.
    """
    model = keras.Sequential([
        # Input layer
        layers.Input(shape=(CONFIG['IMAGE_SIZE'], CONFIG['IMAGE_SIZE'], 3)),
        
        # Data preprocessing
        layers.Rescaling(1./255),
        
        # First convolutional block
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.1),
        
        # Second convolutional block
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.1),
        
        # Third convolutional block
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.2),
        
        # Fourth convolutional block
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.2),
        
        # Global average pooling instead of flatten to reduce parameters
        layers.GlobalAveragePooling2D(),
        
        # Dense layers for classification
        layers.Dense(256, activation='relu'),
        layers.Dropout(CONFIG['DROPOUT_RATE']),
        layers.Dense(128, activation='relu'),
        layers.Dropout(CONFIG['DROPOUT_RATE']),
        
        # Output layer
        layers.Dense(CONFIG['NUM_CLASSES'], activation='softmax', name='predictions')
    ])
    
    logger.info("Simple CNN model architecture created")
    return model

def create_mobilenet_model():
    """
    Create a model based on MobileNetV2 for better accuracy.
    This uses transfer learning with a pre-trained backbone.
    """
    # Create base model from MobileNetV2
    base_model = keras.applications.MobileNetV2(
        input_shape=(CONFIG['IMAGE_SIZE'], CONFIG['IMAGE_SIZE'], 3),
        include_top=False,
        weights=None  # No pre-trained weights for faster initialization
    )
    
    # Freeze the base model initially
    base_model.trainable = False
    
    # Add custom head
    model = keras.Sequential([
        # Input preprocessing
        layers.Input(shape=(CONFIG['IMAGE_SIZE'], CONFIG['IMAGE_SIZE'], 3)),
        layers.Rescaling(1./255),
        
        # Base model
        base_model,
        
        # Custom classification head
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.2),
        layers.Dense(512, activation='relu'),
        layers.Dropout(CONFIG['DROPOUT_RATE']),
        layers.Dense(256, activation='relu'),
        layers.Dropout(CONFIG['DROPOUT_RATE']),
        layers.Dense(CONFIG['NUM_CLASSES'], activation='softmax', name='predictions')
    ])
    
    logger.info("MobileNetV2-based model architecture created")
    return model

def create_very_simple_model():
    """
    Create a very simple model for the fastest possible loading and inference.
    """
    model = keras.Sequential([
        # Input layer
        layers.Input(shape=(CONFIG['IMAGE_SIZE'], CONFIG['IMAGE_SIZE'], 3)),
        
        # Rescale images
        layers.Rescaling(1./255),
        
        # Very simple architecture
        layers.Conv2D(16, (5, 5), activation='relu', strides=2),
        layers.MaxPooling2D((4, 4)),
        
        layers.Conv2D(32, (5, 5), activation='relu', strides=2),
        layers.MaxPooling2D((4, 4)),
        
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.GlobalAveragePooling2D(),
        
        # Classification layers
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(CONFIG['NUM_CLASSES'], activation='softmax')
    ])
    
    logger.info("Very simple model architecture created")
    return model

def compile_model(model, learning_rate=None):
    """Compile the model with appropriate optimizer and loss function."""
    if learning_rate is None:
        learning_rate = CONFIG['LEARNING_RATE']
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy', 'top_3_accuracy']
    )
    
    logger.info(f"Model compiled with learning rate: {learning_rate}")
    return model

def initialize_model_weights(model):
    """Initialize model weights with a dummy forward pass."""
    # Create dummy input to initialize weights
    dummy_input = tf.random.normal((1, CONFIG['IMAGE_SIZE'], CONFIG['IMAGE_SIZE'], 3))
    
    # Forward pass to initialize weights
    _ = model(dummy_input)
    
    logger.info("Model weights initialized")

def save_model(model, model_path):
    """Save the model in Keras format."""
    try:
        model.save(model_path, save_format='h5')
        logger.info(f"Model saved successfully to {model_path}")
        
        # Print model summary
        logger.info("Model summary:")
        model.summary(print_fn=logger.info)
        
        return True
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        return False

def create_tflite_model(model, tflite_path):
    """Convert model to TensorFlow Lite format for better performance."""
    try:
        # Convert the model to TensorFlow Lite
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        # Apply optimizations
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        # Additional optimizations for smaller size
        converter.target_spec.supported_types = [tf.float16]
        
        # Convert
        tflite_model = converter.convert()
        
        # Save the TensorFlow Lite model
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        
        # Get file sizes for comparison
        keras_size = os.path.getsize(os.path.join(CONFIG['MODEL_DIR'], CONFIG['MODEL_NAME']))
        tflite_size = os.path.getsize(tflite_path)
        
        logger.info(f"TensorFlow Lite model saved to {tflite_path}")
        logger.info(f"Model size comparison: Keras={keras_size/1024/1024:.2f}MB, TFLite={tflite_size/1024/1024:.2f}MB")
        logger.info(f"Size reduction: {((keras_size - tflite_size) / keras_size * 100):.1f}%")
        
        return True
    except Exception as e:
        logger.error(f"Error creating TensorFlow Lite model: {str(e)}")
        return False

def verify_model(model_path):
    """Verify that the saved model can be loaded and used for prediction."""
    try:
        # Load the model
        loaded_model = keras.models.load_model(model_path)
        
        # Create test input
        test_input = np.random.random((1, CONFIG['IMAGE_SIZE'], CONFIG['IMAGE_SIZE'], 3))
        
        # Make prediction
        prediction = loaded_model.predict(test_input, verbose=0)
        
        # Verify output shape
        expected_shape = (1, CONFIG['NUM_CLASSES'])
        if prediction.shape == expected_shape:
            logger.info(f"Model verification successful. Output shape: {prediction.shape}")
            logger.info(f"Prediction sum: {np.sum(prediction):.6f} (should be close to 1.0)")
            return True
        else:
            logger.error(f"Model verification failed. Expected shape: {expected_shape}, got: {prediction.shape}")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying model: {str(e)}")
        return False

def create_model_info_file():
    """Create a model information file with metadata."""
    model_info = {
        'model_type': 'Simple CNN',
        'input_shape': [CONFIG['IMAGE_SIZE'], CONFIG['IMAGE_SIZE'], 3],
        'output_classes': CONFIG['NUM_CLASSES'],
        'labels': ARABIC_LETTERS + COMMON_PHRASES,
        'preprocessing': {
            'rescaling': '1/255',
            'resize_method': 'bilinear'
        },
        'performance': {
            'designed_for': 'development_and_testing',
            'expected_accuracy': 'varies_with_training_data'
        },
        'usage': {
            'load_with': 'tf.keras.models.load_model',
            'input_format': 'RGB_image_array',
            'output_format': 'softmax_probabilities'
        }
    }
    
    info_path = os.path.join(CONFIG['MODEL_DIR'], 'model_info.json')
    with open(info_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(model_info, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Model info file created at {info_path}")

def main():
    """Main function to create and save the model."""
    logger.info("Starting Arabic Sign Language model creation...")
    
    # Ensure directories exist
    ensure_directories()
    
    # Create labels file
    create_labels_file()
    
    # Choose model architecture based on requirements
    # For development, use the simple model for faster loading
    logger.info("Creating simple CNN model...")
    model = create_very_simple_model()
    
    # Compile the model
    compile_model(model)
    
    # Initialize weights
    initialize_model_weights(model)
    
    # Save paths
    model_path = os.path.join(CONFIG['MODEL_DIR'], CONFIG['MODEL_NAME'])
    tflite_path = os.path.join(CONFIG['MODEL_DIR'], CONFIG['TFLITE_NAME'])
    
    # Save the model
    if save_model(model, model_path):
        logger.info("Keras model saved successfully")
        
        # Verify the model
        if verify_model(model_path):
            logger.info("Model verification passed")
        else:
            logger.warning("Model verification failed")
        
        # Create TensorFlow Lite version
        if create_tflite_model(model, tflite_path):
            logger.info("TensorFlow Lite model created successfully")
        else:
            logger.warning("Failed to create TensorFlow Lite model")
        
        # Create model info file
        create_model_info_file()
        
        logger.info("Model creation completed successfully!")
        logger.info(f"Files created:")
        logger.info(f"  - Keras model: {model_path}")
        logger.info(f"  - TensorFlow Lite model: {tflite_path}")
        logger.info(f"  - Labels file: {CONFIG['LABELS_FILE']}")
        logger.info(f"  - Model info: {os.path.join(CONFIG['MODEL_DIR'], 'model_info.json')}")
        
    else:
        logger.error("Failed to save model")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Model creation interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        exit(1)
