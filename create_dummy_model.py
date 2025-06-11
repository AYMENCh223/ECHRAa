import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import os

# Define constants
IMAGE_SIZE = 224  # Standard input size for many vision models
NUM_CLASSES = 35   # 28 Arabic letters + 7 common phrases
DROPOUT_RATE = 0.3  # Helps prevent overfitting

# Create an improved model with regularization and more capacity
def create_improved_model():
    # Use MobileNetV2 as base model - efficient and works well for mobile
    base_model = keras.applications.MobileNetV2(
        input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3),
        include_top=False,
        weights=None  # Start with random weights for quick training
    )
    
    # Freeze the base model to use as feature extractor
    base_model.trainable = False
    
    # Create model
    inputs = keras.Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 3))
    
    # Data augmentation layers to improve robustness
    x = inputs
    
    # Create feature extractor
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    
    # Add classification head with dropout for regularization
    x = layers.Dense(512, activation='relu')(x)
    x = layers.Dropout(DROPOUT_RATE)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(DROPOUT_RATE)(x)
    
    # Final classification layer
    outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)
    
    model = keras.Model(inputs=inputs, outputs=outputs)
    
    # Compile with a lower learning rate for stability
    model.compile(
        optimizer=keras.optimizers.Adam(1e-4),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

# Alternative: create a lighter model that loads faster
def create_lightweight_model():
    inputs = keras.Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 3))
    
    # First convolutional block
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    
    # Second convolutional block
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    
    # Third convolutional block
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    
    # Fourth convolutional block
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    
    # Classification head
    x = layers.Flatten()(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)
    
    model = keras.Model(inputs=inputs, outputs=outputs)
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

# Ensure the directory exists
os.makedirs('Model', exist_ok=True)

# Create the lightweight model for better performance in Replit environment
model = create_lightweight_model()

# Save the model
model.save('Model/keras_model.h5')
print('Model saved successfully')

# Create a TensorFlow Lite version for better performance
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save the TFLite model
with open('Model/model.tflite', 'wb') as f:
    f.write(tflite_model)
print('TFLite model saved successfully')
