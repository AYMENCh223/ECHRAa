/**
 * Arabic Sign Language Translator - Gesture Recognition
 * Handles real-time gesture recognition and prediction processing
 */

class GestureRecognition {
    constructor() {
        this.isRunning = false;
        this.isProcessing = false;
        this.lastPredictionTime = 0;
        this.predictionInterval = 1000; // milliseconds between predictions
        this.confidenceThreshold = 0.7;
        
        // Prediction results
        this.currentPrediction = null;
        this.predictionHistory = [];
        this.recognizedSigns = [];
        this.currentSentence = '';
        
        // Processing settings
        this.smoothingWindow = 3; // Number of predictions to smooth over
        this.maxHistoryLength = 10;
        
        // Event callbacks
        this.onPrediction = null;
        this.onSignRecognized = null;
        this.onSentenceUpdate = null;
        this.onError = null;
        
        // API endpoints
        this.endpoints = {
            predict: '/api/predict',
            processImage: '/process_image'
        };
        
        // Performance monitoring
        this.stats = {
            totalPredictions: 0,
            successfulPredictions: 0,
            averageProcessingTime: 0,
            lastProcessingTime: 0
        };
        
        this.initialize();
    }
    
    /**
     * Initialize gesture recognition system
     */
    initialize() {
        this.setupEventListeners();
        this.loadConfiguration();
        console.log('Gesture recognition system initialized');
    }
    
    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Listen for frame capture events from camera
        document.addEventListener('frameCapture', (event) => {
            if (this.isRunning && !this.isProcessing) {
                this.processFrame(event.detail.imageData, event.detail.canvas);
            }
        });
        
        // Listen for manual image processing
        document.addEventListener('processImage', (event) => {
            this.processImageData(event.detail.imageData);
        });
        
        // Set up UI event listeners
        this.setupUIEventListeners();
    }
    
    /**
     * Set up UI event listeners
     */
    setupUIEventListeners() {
        // Clear translation button
        const clearBtn = document.getElementById('clearTranslation');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearRecognition();
            });
        }
        
        // Speak translation button
        const speakBtn = document.getElementById('speakTranslation');
        if (speakBtn) {
            speakBtn.addEventListener('click', () => {
                this.speakCurrentSentence();
            });
        }
        
        // Save session button
        const saveBtn = document.getElementById('saveSession');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveCurrentSession();
            });
        }
        
        // Settings controls
        this.setupSettingsControls();
    }
    
    /**
     * Set up settings controls
     */
    setupSettingsControls() {
        // Confidence threshold slider
        const confidenceSlider = document.getElementById('confidenceThreshold');
        if (confidenceSlider) {
            confidenceSlider.addEventListener('input', (e) => {
                this.confidenceThreshold = parseFloat(e.target.value);
                this.updateSettingsDisplay();
            });
        }
        
        // Prediction interval slider
        const intervalSlider = document.getElementById('predictionInterval');
        if (intervalSlider) {
            intervalSlider.addEventListener('input', (e) => {
                this.predictionInterval = parseInt(e.target.value);
                this.updateSettingsDisplay();
            });
        }
        
        // Smoothing window slider
        const smoothingSlider = document.getElementById('smoothingWindow');
        if (smoothingSlider) {
            smoothingSlider.addEventListener('input', (e) => {
                this.smoothingWindow = parseInt(e.target.value);
                this.updateSettingsDisplay();
            });
        }
    }
    
    /**
     * Load configuration from localStorage or defaults
     */
    loadConfiguration() {
        const savedConfig = localStorage.getItem('gestureRecognitionConfig');
        if (savedConfig) {
            try {
                const config = JSON.parse(savedConfig);
                this.confidenceThreshold = config.confidenceThreshold || 0.7;
                this.predictionInterval = config.predictionInterval || 1000;
                this.smoothingWindow = config.smoothingWindow || 3;
            } catch (error) {
                console.warn('Failed to load saved configuration:', error);
            }
        }
        
        this.updateSettingsDisplay();
    }
    
    /**
     * Save configuration to localStorage
     */
    saveConfiguration() {
        const config = {
            confidenceThreshold: this.confidenceThreshold,
            predictionInterval: this.predictionInterval,
            smoothingWindow: this.smoothingWindow
        };
        
        localStorage.setItem('gestureRecognitionConfig', JSON.stringify(config));
    }
    
    /**
     * Update settings display
     */
    updateSettingsDisplay() {
        // Update confidence threshold display
        const confidenceDisplay = document.getElementById('confidenceDisplay');
        if (confidenceDisplay) {
            confidenceDisplay.textContent = `${Math.round(this.confidenceThreshold * 100)}%`;
        }
        
        // Update interval display
        const intervalDisplay = document.getElementById('intervalDisplay');
        if (intervalDisplay) {
            intervalDisplay.textContent = `${this.predictionInterval}ms`;
        }
        
        // Update smoothing display
        const smoothingDisplay = document.getElementById('smoothingDisplay');
        if (smoothingDisplay) {
            smoothingDisplay.textContent = this.smoothingWindow;
        }
        
        // Update slider values
        const confidenceSlider = document.getElementById('confidenceThreshold');
        if (confidenceSlider) {
            confidenceSlider.value = this.confidenceThreshold;
        }
        
        const intervalSlider = document.getElementById('predictionInterval');
        if (intervalSlider) {
            intervalSlider.value = this.predictionInterval;
        }
        
        const smoothingSlider = document.getElementById('smoothingWindow');
        if (smoothingSlider) {
            smoothingSlider.value = this.smoothingWindow;
        }
    }
    
    /**
     * Start gesture recognition
     */
    start() {
        if (this.isRunning) {
            console.log('Gesture recognition already running');
            return;
        }
        
        this.isRunning = true;
        this.lastPredictionTime = 0;
        
        console.log('Gesture recognition started');
        
        // Update UI
        this.updateRecognitionStatus(true);
        
        // Save configuration
        this.saveConfiguration();
    }
    
    /**
     * Stop gesture recognition
     */
    stop() {
        this.isRunning = false;
        this.isProcessing = false;
        
        console.log('Gesture recognition stopped');
        
        // Update UI
        this.updateRecognitionStatus(false);
    }
    
    /**
     * Process video frame for gesture recognition
     */
    async processFrame(imageData, canvas) {
        if (!this.isRunning || this.isProcessing) {
            return;
        }
        
        // Check if enough time has passed since last prediction
        const currentTime = Date.now();
        if (currentTime - this.lastPredictionTime < this.predictionInterval) {
            return;
        }
        
        this.isProcessing = true;
        this.lastPredictionTime = currentTime;
        
        try {
            // Convert canvas to base64 image
            const base64Image = canvas.toDataURL('image/jpeg', 0.8);
            
            // Process the image
            await this.processImageData(base64Image);
            
        } catch (error) {
            console.error('Error processing frame:', error);
            this.handleError('خطأ في معالجة الإطار', error);
        } finally {
            this.isProcessing = false;
        }
    }
    
    /**
     * Process image data for prediction
     */
    async processImageData(imageData) {
        const startTime = performance.now();
        
        try {
            // Prepare request data
            const requestData = {
                image: imageData
            };
            
            // Send request to backend
            const response = await fetch(this.endpoints.processImage, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            // Calculate processing time
            const processingTime = performance.now() - startTime;
            this.updateStats(processingTime, result.success);
            
            if (result.success) {
                await this.handlePredictionResult(result);
            } else {
                this.handleError('فشل في التنبؤ', new Error(result.error || 'Unknown error'));
            }
            
        } catch (error) {
            console.error('Error in image processing:', error);
            this.handleError('خطأ في معالجة الصورة', error);
            
            // Update stats for failed prediction
            const processingTime = performance.now() - startTime;
            this.updateStats(processingTime, false);
        }
    }
    
    /**
     * Handle prediction result
     */
    async handlePredictionResult(result) {
        const prediction = result.prediction;
        const confidence = result.confidence;
        
        // Create prediction object
        const predictionObj = {
            sign: prediction,
            confidence: confidence,
            timestamp: Date.now()
        };
        
        // Add to prediction history
        this.predictionHistory.push(predictionObj);
        
        // Keep history within limits
        if (this.predictionHistory.length > this.maxHistoryLength) {
            this.predictionHistory.shift();
        }
        
        // Apply smoothing if enabled
        const smoothedPrediction = this.applySmoothingToPrediction();
        
        // Update current prediction
        this.currentPrediction = smoothedPrediction;
        
        // Check if prediction meets confidence threshold
        if (smoothedPrediction.confidence >= this.confidenceThreshold) {
            await this.recognizeSign(smoothedPrediction.sign, smoothedPrediction.confidence);
        }
        
        // Update UI with current prediction
        this.updatePredictionDisplay(smoothedPrediction);
        
        // Call prediction callback
        if (this.onPrediction) {
            this.onPrediction(smoothedPrediction);
        }
    }
    
    /**
     * Apply smoothing to predictions using sliding window
     */
    applySmoothingToPrediction() {
        if (this.predictionHistory.length < this.smoothingWindow) {
            return this.predictionHistory[this.predictionHistory.length - 1];
        }
        
        // Get recent predictions within smoothing window
        const recentPredictions = this.predictionHistory.slice(-this.smoothingWindow);
        
        // Group predictions by sign
        const signGroups = {};
        recentPredictions.forEach(pred => {
            if (!signGroups[pred.sign]) {
                signGroups[pred.sign] = [];
            }
            signGroups[pred.sign].push(pred);
        });
        
        // Find most frequent sign with highest average confidence
        let bestSign = null;
        let bestScore = 0;
        
        Object.keys(signGroups).forEach(sign => {
            const predictions = signGroups[sign];
            const frequency = predictions.length / this.smoothingWindow;
            const avgConfidence = predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length;
            const score = frequency * avgConfidence;
            
            if (score > bestScore) {
                bestScore = score;
                bestSign = sign;
            }
        });
        
        if (bestSign) {
            const bestPredictions = signGroups[bestSign];
            const avgConfidence = bestPredictions.reduce((sum, p) => sum + p.confidence, 0) / bestPredictions.length;
            
            return {
                sign: bestSign,
                confidence: avgConfidence,
                timestamp: Date.now()
            };
        }
        
        // Fallback to latest prediction
        return this.predictionHistory[this.predictionHistory.length - 1];
    }
    
    /**
     * Recognize a sign and add it to the sentence
     */
    async recognizeSign(sign, confidence) {
        // Avoid duplicate consecutive signs
        if (this.recognizedSigns.length > 0 && 
            this.recognizedSigns[this.recognizedSigns.length - 1] === sign) {
            return;
        }
        
        // Add sign to recognized signs
        this.recognizedSigns.push(sign);
        
        // Update current sentence
        this.updateCurrentSentence();
        
        // Update UI
        this.updateRecognizedSignsDisplay();
        this.updateCurrentSentenceDisplay();
        
        // Enable action buttons
        this.enableActionButtons();
        
        // Call sign recognized callback
        if (this.onSignRecognized) {
            this.onSignRecognized(sign, confidence);
        }
        
        // Call sentence update callback
        if (this.onSentenceUpdate) {
            this.onSentenceUpdate(this.currentSentence);
        }
        
        console.log(`Sign recognized: ${sign} (confidence: ${Math.round(confidence * 100)}%)`);
    }
    
    /**
     * Update current sentence from recognized signs
     */
    updateCurrentSentence() {
        // Apply Arabic text processing
        this.currentSentence = this.processArabicText(this.recognizedSigns);
    }
    
    /**
     * Process Arabic text with proper formatting and grammar
     */
    processArabicText(signs) {
        if (signs.length === 0) {
            return '';
        }
        
        // Basic concatenation with spaces
        let text = signs.join(' ');
        
        // Apply basic Arabic text processing
        text = this.applyArabicGrammarRules(text);
        
        return text;
    }
    
    /**
     * Apply basic Arabic grammar rules
     */
    applyArabicGrammarRules(text) {
        // Remove extra spaces
        text = text.replace(/\s+/g, ' ').trim();
        
        // Apply common letter combinations
        const grammarRules = {
            'أ ن ا': 'أنا',
            'أ ن ت': 'أنت',
            'ه ذ ا': 'هذا',
            'ه ذ ه': 'هذه',
            'م ن': 'من',
            'إ ل ى': 'إلى',
            'ع ل ى': 'على',
            'ف ي': 'في',
            'م ع': 'مع',
            'ل ا': 'لا',
            'ن ع م': 'نعم'
        };
        
        Object.keys(grammarRules).forEach(pattern => {
            const replacement = grammarRules[pattern];
            text = text.replace(new RegExp(pattern, 'g'), replacement);
        });
        
        return text;
    }
    
    /**
     * Clear all recognition data
     */
    clearRecognition() {
        this.recognizedSigns = [];
        this.currentSentence = '';
        this.predictionHistory = [];
        this.currentPrediction = null;
        
        // Update UI
        this.updateRecognizedSignsDisplay();
        this.updateCurrentSentenceDisplay();
        this.updatePredictionDisplay(null);
        this.disableActionButtons();
        
        console.log('Recognition data cleared');
        
        // Show notification
        if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
            window.ArabicSignLanguage.showNotification('تم مسح الترجمة', 'info');
        }
    }
    
    /**
     * Speak current sentence using text-to-speech
     */
    async speakCurrentSentence() {
        if (!this.currentSentence) {
            if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
                window.ArabicSignLanguage.showNotification('لا يوجد نص للنطق', 'warning');
            }
            return;
        }
        
        try {
            const response = await fetch('/speak_translation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: this.currentSentence
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
                    window.ArabicSignLanguage.showNotification('يتم تشغيل الصوت...', 'info');
                }
            } else {
                throw new Error(result.error || 'Failed to speak text');
            }
            
        } catch (error) {
            console.error('Error speaking text:', error);
            if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
                window.ArabicSignLanguage.showNotification('خطأ في تشغيل الصوت', 'error');
            }
        }
    }
    
    /**
     * Save current session
     */
    async saveCurrentSession() {
        if (!this.currentSentence && this.recognizedSigns.length === 0) {
            if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
                window.ArabicSignLanguage.showNotification('لا يوجد محتوى للحفظ', 'warning');
            }
            return;
        }
        
        // Show session save modal if it exists
        const modal = document.getElementById('saveSessionModal');
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            return;
        }
        
        // Otherwise save with default name
        const sessionName = `جلسة ${new Date().toLocaleDateString('ar-SA')} ${new Date().toLocaleTimeString('ar-SA')}`;
        await this.saveSessionWithName(sessionName);
    }
    
    /**
     * Save session with specific name
     */
    async saveSessionWithName(sessionName) {
        try {
            const sessionData = {
                name: sessionName,
                translation: this.currentSentence,
                signs: this.recognizedSigns,
                timestamp: new Date().toISOString(),
                stats: this.stats
            };
            
            const response = await fetch('/save_session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(sessionData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
                    window.ArabicSignLanguage.showNotification('تم حفظ الجلسة بنجاح', 'success');
                }
            } else {
                throw new Error(result.error || 'Failed to save session');
            }
            
        } catch (error) {
            console.error('Error saving session:', error);
            if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
                window.ArabicSignLanguage.showNotification('خطأ في حفظ الجلسة', 'error');
            }
        }
    }
    
    /**
     * Update prediction display
     */
    updatePredictionDisplay(prediction) {
        const predictionElement = document.getElementById('currentPrediction');
        const confidenceElement = document.getElementById('confidenceLevel');
        const predictionDisplay = document.getElementById('predictionDisplay');
        
        if (prediction) {
            if (predictionElement) {
                predictionElement.textContent = prediction.sign;
            }
            
            if (confidenceElement) {
                const confidencePercent = Math.round(prediction.confidence * 100);
                confidenceElement.textContent = `${confidencePercent}%`;
                
                // Update confidence color
                confidenceElement.className = '';
                if (prediction.confidence >= 0.8) {
                    confidenceElement.className = 'text-success';
                } else if (prediction.confidence >= 0.6) {
                    confidenceElement.className = 'text-warning';
                } else {
                    confidenceElement.className = 'text-danger';
                }
            }
            
            if (predictionDisplay) {
                predictionDisplay.style.display = 'block';
            }
        } else {
            if (predictionElement) {
                predictionElement.textContent = '-';
            }
            
            if (confidenceElement) {
                confidenceElement.textContent = '-';
                confidenceElement.className = '';
            }
            
            if (predictionDisplay) {
                predictionDisplay.style.display = 'none';
            }
        }
    }
    
    /**
     * Update recognized signs display
     */
    updateRecognizedSignsDisplay() {
        const signsContainer = document.getElementById('signsContainer');
        if (!signsContainer) return;
        
        signsContainer.innerHTML = '';
        
        this.recognizedSigns.forEach((sign, index) => {
            const signElement = document.createElement('span');
            signElement.className = 'sign-badge';
            signElement.textContent = sign;
            signElement.setAttribute('data-index', index);
            
            // Add click to remove functionality
            signElement.addEventListener('click', () => {
                this.removeSignAtIndex(index);
            });
            
            signsContainer.appendChild(signElement);
        });
    }
    
    /**
     * Update current sentence display
     */
    updateCurrentSentenceDisplay() {
        const sentenceElement = document.getElementById('currentSentence');
        if (sentenceElement) {
            sentenceElement.textContent = this.currentSentence || '';
        }
    }
    
    /**
     * Update recognition status
     */
    updateRecognitionStatus(isActive) {
        const statusElements = document.querySelectorAll('.recognition-status');
        statusElements.forEach(element => {
            element.className = `recognition-status ${isActive ? 'active' : 'inactive'}`;
            element.textContent = isActive ? 'التعرف نشط' : 'التعرف متوقف';
        });
    }
    
    /**
     * Enable action buttons
     */
    enableActionButtons() {
        const buttons = document.querySelectorAll('#speakTranslation, #saveSession');
        buttons.forEach(button => {
            button.disabled = false;
        });
    }
    
    /**
     * Disable action buttons
     */
    disableActionButtons() {
        const buttons = document.querySelectorAll('#speakTranslation, #saveSession');
        buttons.forEach(button => {
            button.disabled = true;
        });
    }
    
    /**
     * Remove sign at specific index
     */
    removeSignAtIndex(index) {
        if (index >= 0 && index < this.recognizedSigns.length) {
            this.recognizedSigns.splice(index, 1);
            this.updateCurrentSentence();
            this.updateRecognizedSignsDisplay();
            this.updateCurrentSentenceDisplay();
            
            if (this.recognizedSigns.length === 0) {
                this.disableActionButtons();
            }
        }
    }
    
    /**
     * Update performance statistics
     */
    updateStats(processingTime, success) {
        this.stats.totalPredictions++;
        this.stats.lastProcessingTime = processingTime;
        
        if (success) {
            this.stats.successfulPredictions++;
        }
        
        // Update average processing time
        this.stats.averageProcessingTime = 
            (this.stats.averageProcessingTime * (this.stats.totalPredictions - 1) + processingTime) 
            / this.stats.totalPredictions;
        
        // Update stats display
        this.updateStatsDisplay();
    }
    
    /**
     * Update statistics display
     */
    updateStatsDisplay() {
        const elements = {
            totalPredictions: document.getElementById('totalPredictions'),
            successRate: document.getElementById('successRate'),
            avgProcessingTime: document.getElementById('avgProcessingTime'),
            lastProcessingTime: document.getElementById('lastProcessingTime')
        };
        
        if (elements.totalPredictions) {
            elements.totalPredictions.textContent = this.stats.totalPredictions;
        }
        
        if (elements.successRate && this.stats.totalPredictions > 0) {
            const rate = (this.stats.successfulPredictions / this.stats.totalPredictions * 100).toFixed(1);
            elements.successRate.textContent = `${rate}%`;
        }
        
        if (elements.avgProcessingTime) {
            elements.avgProcessingTime.textContent = `${Math.round(this.stats.averageProcessingTime)}ms`;
        }
        
        if (elements.lastProcessingTime) {
            elements.lastProcessingTime.textContent = `${Math.round(this.stats.lastProcessingTime)}ms`;
        }
    }
    
    /**
     * Handle errors
     */
    handleError(message, error) {
        console.error('Gesture recognition error:', error);
        
        // Call error callback
        if (this.onError) {
            this.onError(error, message);
        }
        
        // Show user notification
        if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
            window.ArabicSignLanguage.showNotification(message, 'error');
        }
    }
    
    /**
     * Get current recognition state
     */
    getState() {
        return {
            isRunning: this.isRunning,
            isProcessing: this.isProcessing,
            currentPrediction: this.currentPrediction,
            recognizedSigns: [...this.recognizedSigns],
            currentSentence: this.currentSentence,
            stats: { ...this.stats }
        };
    }
    
    /**
     * Export recognition data
     */
    exportData() {
        return {
            session: {
                signs: this.recognizedSigns,
                sentence: this.currentSentence,
                timestamp: new Date().toISOString()
            },
            history: this.predictionHistory,
            stats: this.stats,
            settings: {
                confidenceThreshold: this.confidenceThreshold,
                predictionInterval: this.predictionInterval,
                smoothingWindow: this.smoothingWindow
            }
        };
    }
}

// Global gesture recognition instance
let gestureRecognition = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeGestureRecognition();
});

/**
 * Initialize gesture recognition system
 */
function initializeGestureRecognition() {
    gestureRecognition = new GestureRecognition();
    
    // Set up callbacks
    gestureRecognition.onPrediction = onPredictionReceived;
    gestureRecognition.onSignRecognized = onSignRecognized;
    gestureRecognition.onSentenceUpdate = onSentenceUpdated;
    gestureRecognition.onError = onGestureRecognitionError;
    
    // Set up additional UI handlers
    setupGestureRecognitionUI();
    
    console.log('Gesture recognition initialized');
}

/**
 * Set up gesture recognition UI handlers
 */
function setupGestureRecognitionUI() {
    // Save session modal confirm button
    const confirmSaveBtn = document.getElementById('confirmSaveSession');
    if (confirmSaveBtn) {
        confirmSaveBtn.addEventListener('click', () => {
            const sessionName = document.getElementById('sessionName').value.trim();
            if (sessionName) {
                gestureRecognition.saveSessionWithName(sessionName);
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('saveSessionModal'));
                if (modal) {
                    modal.hide();
                }
                
                // Clear input
                document.getElementById('sessionName').value = '';
            } else {
                if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
                    window.ArabicSignLanguage.showNotification('يرجى إدخال اسم الجلسة', 'warning');
                }
            }
        });
    }
    
    // Export data button
    const exportBtn = document.getElementById('exportData');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            exportRecognitionData();
        });
    }
    
    // Settings modal save button
    const saveSettingsBtn = document.getElementById('saveRecognitionSettings');
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', () => {
            gestureRecognition.saveConfiguration();
            if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
                window.ArabicSignLanguage.showNotification('تم حفظ الإعدادات', 'success');
            }
        });
    }
}

/**
 * Callback for prediction received
 */
function onPredictionReceived(prediction) {
    // Additional handling for prediction if needed
    console.log('Prediction received:', prediction);
}

/**
 * Callback for sign recognized
 */
function onSignRecognized(sign, confidence) {
    // Additional handling for recognized sign
    console.log(`Sign recognized: ${sign} (${Math.round(confidence * 100)}%)`);
    
    // Haptic feedback if available
    if (navigator.vibrate) {
        navigator.vibrate(100);
    }
}

/**
 * Callback for sentence updated
 */
function onSentenceUpdated(sentence) {
    // Additional handling for sentence update
    console.log('Sentence updated:', sentence);
    
    // Announce to screen readers
    if (window.ArabicSignLanguage && window.ArabicSignLanguage.announceToScreenReader) {
        window.ArabicSignLanguage.announceToScreenReader(`تم تحديث الجملة: ${sentence}`);
    }
}

/**
 * Callback for gesture recognition errors
 */
function onGestureRecognitionError(error, message) {
    console.error('Gesture recognition error callback:', error, message);
    
    // Additional error handling can be added here
}

/**
 * Export recognition data as JSON file
 */
function exportRecognitionData() {
    if (!gestureRecognition) {
        return;
    }
    
    const data = gestureRecognition.exportData();
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `gesture-recognition-data-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    
    if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
        window.ArabicSignLanguage.showNotification('تم تصدير البيانات بنجاح', 'success');
    }
}

/**
 * Start gesture recognition (called from camera events)
 */
function startGestureRecognition() {
    if (gestureRecognition) {
        gestureRecognition.start();
    }
}

/**
 * Stop gesture recognition (called from camera events)
 */
function stopGestureRecognition() {
    if (gestureRecognition) {
        gestureRecognition.stop();
    }
}

// Export for use in other modules
window.gestureRecognition = gestureRecognition;
window.GestureRecognition = GestureRecognition;
window.startGestureRecognition = startGestureRecognition;
window.stopGestureRecognition = stopGestureRecognition;

console.log('Gesture recognition module loaded successfully');
