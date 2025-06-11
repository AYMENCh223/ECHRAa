/**
 * Arabic Sign Language Translator - Camera Management
 * Handles webcam access, video streaming, and camera controls
 */

class CameraManager {
    constructor() {
        this.stream = null;
        this.video = null;
        this.canvas = null;
        this.context = null;
        this.isStreaming = false;
        this.constraints = {
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                frameRate: { ideal: 30 }
            },
            audio: false
        };
        
        // Camera settings
        this.currentDeviceId = null;
        this.availableDevices = [];
        this.settings = {
            brightness: 0,
            contrast: 0,
            saturation: 0,
            flipHorizontal: true
        };
        
        // Event callbacks
        this.onStreamStart = null;
        this.onStreamStop = null;
        this.onError = null;
        this.onFrameCapture = null;
        
        this.initialize();
    }
    
    /**
     * Initialize camera manager
     */
    async initialize() {
        try {
            await this.enumerateDevices();
            this.setupEventListeners();
            console.log('Camera manager initialized successfully');
        } catch (error) {
            console.error('Failed to initialize camera manager:', error);
            this.handleError('فشل في تهيئة مدير الكاميرا', error);
        }
    }
    
    /**
     * Enumerate available camera devices
     */
    async enumerateDevices() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            this.availableDevices = devices.filter(device => device.kind === 'videoinput');
            
            console.log(`Found ${this.availableDevices.length} camera devices`);
            
            // Set default device
            if (this.availableDevices.length > 0) {
                this.currentDeviceId = this.availableDevices[0].deviceId;
            }
            
            // Update device selector if exists
            this.updateDeviceSelector();
            
        } catch (error) {
            console.error('Error enumerating devices:', error);
            throw new Error('لا يمكن الوصول لقائمة الكاميرات');
        }
    }
    
    /**
     * Update device selector dropdown
     */
    updateDeviceSelector() {
        const selector = document.getElementById('cameraSelector');
        if (!selector) return;
        
        selector.innerHTML = '';
        
        this.availableDevices.forEach((device, index) => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.textContent = device.label || `كاميرا ${index + 1}`;
            selector.appendChild(option);
        });
        
        if (this.currentDeviceId) {
            selector.value = this.currentDeviceId;
        }
    }
    
    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Device change listener
        const selector = document.getElementById('cameraSelector');
        if (selector) {
            selector.addEventListener('change', (e) => {
                this.switchCamera(e.target.value);
            });
        }
        
        // Settings controls
        this.setupSettingsControls();
        
        // Handle visibility change to pause/resume camera
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isStreaming) {
                this.pauseStream();
            } else if (!document.hidden && this.stream) {
                this.resumeStream();
            }
        });
    }
    
    /**
     * Set up camera settings controls
     */
    setupSettingsControls() {
        const controls = [
            { id: 'brightnessSlider', setting: 'brightness' },
            { id: 'contrastSlider', setting: 'contrast' },
            { id: 'saturationSlider', setting: 'saturation' }
        ];
        
        controls.forEach(({ id, setting }) => {
            const control = document.getElementById(id);
            if (control) {
                control.addEventListener('input', (e) => {
                    this.settings[setting] = parseFloat(e.target.value);
                    this.applyCameraSettings();
                });
            }
        });
        
        // Flip horizontal toggle
        const flipToggle = document.getElementById('flipHorizontalToggle');
        if (flipToggle) {
            flipToggle.addEventListener('change', (e) => {
                this.settings.flipHorizontal = e.target.checked;
                this.applyCameraSettings();
            });
        }
    }
    
    /**
     * Start camera stream
     */
    async startCamera(videoElement = null) {
        try {
            if (videoElement) {
                this.video = videoElement;
            } else {
                this.video = document.getElementById('videoFeed') || 
                           document.getElementById('collectionVideo') ||
                           document.querySelector('video');
            }
            
            if (!this.video) {
                throw new Error('لم يتم العثور على عنصر الفيديو');
            }
            
            // Update constraints with current device
            if (this.currentDeviceId) {
                this.constraints.video.deviceId = { exact: this.currentDeviceId };
            }
            
            // Request camera access
            this.stream = await navigator.mediaDevices.getUserMedia(this.constraints);
            
            // Set video source
            this.video.srcObject = this.stream;
            
            // Wait for video to be ready
            await new Promise((resolve, reject) => {
                this.video.onloadedmetadata = () => {
                    this.video.play()
                        .then(resolve)
                        .catch(reject);
                };
                
                this.video.onerror = () => {
                    reject(new Error('فشل في تشغيل الفيديو'));
                };
            });
            
            this.isStreaming = true;
            
            // Apply camera settings
            this.applyCameraSettings();
            
            // Set up canvas for frame capture
            this.setupCanvas();
            
            // Update UI
            this.updateCameraUI(true);
            
            // Call success callback
            if (this.onStreamStart) {
                this.onStreamStart();
            }
            
            console.log('Camera started successfully');
            
            return true;
            
        } catch (error) {
            console.error('Error starting camera:', error);
            this.handleError('فشل في تشغيل الكاميرا', error);
            return false;
        }
    }
    
    /**
     * Stop camera stream
     */
    stopCamera() {
        try {
            if (this.stream) {
                this.stream.getTracks().forEach(track => {
                    track.stop();
                });
                this.stream = null;
            }
            
            if (this.video) {
                this.video.srcObject = null;
            }
            
            this.isStreaming = false;
            
            // Update UI
            this.updateCameraUI(false);
            
            // Call stop callback
            if (this.onStreamStop) {
                this.onStreamStop();
            }
            
            console.log('Camera stopped successfully');
            
        } catch (error) {
            console.error('Error stopping camera:', error);
            this.handleError('فشل في إيقاف الكاميرا', error);
        }
    }
    
    /**
     * Switch to different camera device
     */
    async switchCamera(deviceId) {
        const wasStreaming = this.isStreaming;
        
        if (wasStreaming) {
            this.stopCamera();
        }
        
        this.currentDeviceId = deviceId;
        
        if (wasStreaming) {
            await this.startCamera();
        }
    }
    
    /**
     * Pause camera stream (keep connection but stop display)
     */
    pauseStream() {
        if (this.video && this.isStreaming) {
            this.video.pause();
        }
    }
    
    /**
     * Resume camera stream
     */
    resumeStream() {
        if (this.video && this.isStreaming) {
            this.video.play().catch(error => {
                console.error('Error resuming video:', error);
            });
        }
    }
    
    /**
     * Set up canvas for frame capture
     */
    setupCanvas() {
        if (!this.canvas) {
            this.canvas = document.createElement('canvas');
            this.context = this.canvas.getContext('2d');
        }
        
        if (this.video) {
            this.canvas.width = this.video.videoWidth || 640;
            this.canvas.height = this.video.videoHeight || 480;
        }
    }
    
    /**
     * Capture current frame as image data
     */
    captureFrame() {
        if (!this.video || !this.isStreaming) {
            return null;
        }
        
        this.setupCanvas();
        
        // Draw video frame to canvas
        if (this.settings.flipHorizontal) {
            this.context.save();
            this.context.scale(-1, 1);
            this.context.drawImage(this.video, -this.canvas.width, 0, this.canvas.width, this.canvas.height);
            this.context.restore();
        } else {
            this.context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        }
        
        // Apply camera settings
        this.applyCanvasFilters();
        
        // Get image data
        const imageData = this.context.getImageData(0, 0, this.canvas.width, this.canvas.height);
        
        // Call frame capture callback
        if (this.onFrameCapture) {
            this.onFrameCapture(imageData, this.canvas);
        }
        
        return imageData;
    }
    
    /**
     * Capture frame as base64 encoded image
     */
    captureFrameAsBase64(format = 'image/jpeg', quality = 0.8) {
        if (!this.video || !this.isStreaming) {
            return null;
        }
        
        this.setupCanvas();
        
        // Draw video frame
        if (this.settings.flipHorizontal) {
            this.context.save();
            this.context.scale(-1, 1);
            this.context.drawImage(this.video, -this.canvas.width, 0, this.canvas.width, this.canvas.height);
            this.context.restore();
        } else {
            this.context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        }
        
        // Apply filters
        this.applyCanvasFilters();
        
        return this.canvas.toDataURL(format, quality);
    }
    
    /**
     * Apply camera settings
     */
    applyCameraSettings() {
        if (!this.video || !this.isStreaming) return;
        
        try {
            const track = this.stream.getVideoTracks()[0];
            const capabilities = track.getCapabilities();
            const settings = {};
            
            // Apply supported settings
            if (capabilities.brightness && this.settings.brightness !== 0) {
                settings.brightness = Math.max(
                    capabilities.brightness.min,
                    Math.min(capabilities.brightness.max, this.settings.brightness)
                );
            }
            
            if (capabilities.contrast && this.settings.contrast !== 0) {
                settings.contrast = Math.max(
                    capabilities.contrast.min,
                    Math.min(capabilities.contrast.max, this.settings.contrast)
                );
            }
            
            if (capabilities.saturation && this.settings.saturation !== 0) {
                settings.saturation = Math.max(
                    capabilities.saturation.min,
                    Math.min(capabilities.saturation.max, this.settings.saturation)
                );
            }
            
            if (Object.keys(settings).length > 0) {
                track.applyConstraints({ advanced: [settings] });
            }
            
        } catch (error) {
            console.warn('Cannot apply camera settings:', error);
            // Fallback to CSS filters
            this.applyCSSFilters();
        }
    }
    
    /**
     * Apply CSS filters as fallback
     */
    applyCSSFilters() {
        if (!this.video) return;
        
        const filters = [];
        
        if (this.settings.brightness !== 0) {
            filters.push(`brightness(${1 + this.settings.brightness})`);
        }
        
        if (this.settings.contrast !== 0) {
            filters.push(`contrast(${1 + this.settings.contrast})`);
        }
        
        if (this.settings.saturation !== 0) {
            filters.push(`saturate(${1 + this.settings.saturation})`);
        }
        
        this.video.style.filter = filters.join(' ');
        
        if (this.settings.flipHorizontal) {
            this.video.style.transform = 'scaleX(-1)';
        } else {
            this.video.style.transform = 'none';
        }
    }
    
    /**
     * Apply filters to canvas context
     */
    applyCanvasFilters() {
        if (!this.context) return;
        
        const imageData = this.context.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const data = imageData.data;
        
        // Apply brightness, contrast, saturation adjustments
        for (let i = 0; i < data.length; i += 4) {
            // Apply brightness
            if (this.settings.brightness !== 0) {
                data[i] = Math.max(0, Math.min(255, data[i] + this.settings.brightness * 255));     // Red
                data[i + 1] = Math.max(0, Math.min(255, data[i + 1] + this.settings.brightness * 255)); // Green
                data[i + 2] = Math.max(0, Math.min(255, data[i + 2] + this.settings.brightness * 255)); // Blue
            }
            
            // Apply contrast
            if (this.settings.contrast !== 0) {
                const contrast = 1 + this.settings.contrast;
                data[i] = Math.max(0, Math.min(255, (data[i] - 128) * contrast + 128));
                data[i + 1] = Math.max(0, Math.min(255, (data[i + 1] - 128) * contrast + 128));
                data[i + 2] = Math.max(0, Math.min(255, (data[i + 2] - 128) * contrast + 128));
            }
        }
        
        this.context.putImageData(imageData, 0, 0);
    }
    
    /**
     * Update camera UI elements
     */
    updateCameraUI(isActive) {
        // Update video placeholder/display
        const videoPlaceholder = document.getElementById('videoPlaceholder') || 
                                document.getElementById('collectionVideoPlaceholder');
        const video = this.video;
        
        if (videoPlaceholder && video) {
            if (isActive) {
                videoPlaceholder.style.display = 'none';
                video.style.display = 'block';
            } else {
                videoPlaceholder.style.display = 'block';
                video.style.display = 'none';
            }
        }
        
        // Update control buttons
        const startBtn = document.getElementById('startCamera') || 
                        document.getElementById('enableCollectionCamera');
        const stopBtn = document.getElementById('stopCamera') || 
                       document.getElementById('disableCollectionCamera');
        
        if (startBtn && stopBtn) {
            if (isActive) {
                startBtn.style.display = 'none';
                startBtn.disabled = true;
                stopBtn.style.display = 'inline-block';
                stopBtn.disabled = false;
            } else {
                startBtn.style.display = 'inline-block';
                startBtn.disabled = false;
                stopBtn.style.display = 'none';
                stopBtn.disabled = true;
            }
        }
        
        // Update status indicators
        const statusIndicator = document.querySelector('.camera-status');
        if (statusIndicator) {
            statusIndicator.className = `camera-status ${isActive ? 'active' : 'inactive'}`;
            statusIndicator.textContent = isActive ? 'الكاميرا نشطة' : 'الكاميرا متوقفة';
        }
    }
    
    /**
     * Handle camera errors
     */
    handleError(message, error) {
        console.error('Camera error:', error);
        
        let userMessage = message;
        
        // Provide specific error messages
        if (error.name === 'NotAllowedError') {
            userMessage = 'يرجى السماح للموقع بالوصول للكاميرا';
        } else if (error.name === 'NotFoundError') {
            userMessage = 'لم يتم العثور على كاميرا متصلة بالجهاز';
        } else if (error.name === 'NotReadableError') {
            userMessage = 'الكاميرا مستخدمة بواسطة تطبيق آخر';
        } else if (error.name === 'OverconstrainedError') {
            userMessage = 'إعدادات الكاميرا غير مدعومة';
        } else if (error.name === 'SecurityError') {
            userMessage = 'يجب استخدام HTTPS للوصول للكاميرا';
        }
        
        // Show user notification
        if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
            window.ArabicSignLanguage.showNotification(userMessage, 'error');
        } else {
            alert(userMessage);
        }
        
        // Call error callback
        if (this.onError) {
            this.onError(error, userMessage);
        }
        
        // Update UI to reflect error state
        this.updateCameraUI(false);
    }
    
    /**
     * Get camera capabilities
     */
    getCapabilities() {
        if (!this.stream) return null;
        
        const track = this.stream.getVideoTracks()[0];
        return track ? track.getCapabilities() : null;
    }
    
    /**
     * Get current camera settings
     */
    getSettings() {
        if (!this.stream) return null;
        
        const track = this.stream.getVideoTracks()[0];
        return track ? track.getSettings() : null;
    }
    
    /**
     * Check if camera is supported
     */
    static isSupported() {
        return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    }
    
    /**
     * Request camera permissions
     */
    static async requestPermissions() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            stream.getTracks().forEach(track => track.stop());
            return true;
        } catch (error) {
            return false;
        }
    }
}

// Global camera manager instance
let cameraManager = null;

// Initialize camera functionality when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeCameraControls();
});

/**
 * Initialize camera controls
 */
function initializeCameraControls() {
    // Check camera support
    if (!CameraManager.isSupported()) {
        console.error('Camera not supported');
        showCameraUnsupportedMessage();
        return;
    }
    
    // Create camera manager instance
    cameraManager = new CameraManager();
    
    // Set up camera manager callbacks
    cameraManager.onStreamStart = onCameraStreamStart;
    cameraManager.onStreamStop = onCameraStreamStop;
    cameraManager.onError = onCameraError;
    cameraManager.onFrameCapture = onFrameCapture;
    
    // Set up camera control buttons
    setupCameraButtons();
    
    console.log('Camera controls initialized');
}

/**
 * Set up camera control buttons
 */
function setupCameraButtons() {
    // Start camera buttons
    const startButtons = document.querySelectorAll('#startCamera, #enableCollectionCamera, #enablePracticeCamera');
    startButtons.forEach(button => {
        button.addEventListener('click', startCameraHandler);
    });
    
    // Stop camera buttons
    const stopButtons = document.querySelectorAll('#stopCamera, #disableCollectionCamera, #disablePracticeCamera');
    stopButtons.forEach(button => {
        button.addEventListener('click', stopCameraHandler);
    });
    
    // Camera settings buttons
    const settingsButton = document.getElementById('cameraSettings');
    if (settingsButton) {
        settingsButton.addEventListener('click', showCameraSettings);
    }
    
    // Screenshot button
    const screenshotButton = document.getElementById('takeScreenshot');
    if (screenshotButton) {
        screenshotButton.addEventListener('click', takeScreenshot);
    }
}

/**
 * Start camera handler
 */
async function startCameraHandler(event) {
    event.preventDefault();
    
    if (!cameraManager) {
        console.error('Camera manager not initialized');
        return;
    }
    
    // Show loading state
    const button = event.target.closest('button');
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري التشغيل...';
    button.disabled = true;
    
    try {
        const success = await cameraManager.startCamera();
        
        if (success) {
            console.log('Camera started successfully');
        } else {
            throw new Error('Failed to start camera');
        }
        
    } catch (error) {
        console.error('Error starting camera:', error);
        
        // Restore button state
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

/**
 * Stop camera handler
 */
function stopCameraHandler(event) {
    event.preventDefault();
    
    if (!cameraManager) {
        console.error('Camera manager not initialized');
        return;
    }
    
    cameraManager.stopCamera();
}

/**
 * Show camera settings modal
 */
function showCameraSettings() {
    const modal = document.getElementById('cameraSettingsModal');
    if (modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Update settings values
        updateCameraSettingsUI();
    }
}

/**
 * Update camera settings UI
 */
function updateCameraSettingsUI() {
    if (!cameraManager) return;
    
    const settings = cameraManager.settings;
    const capabilities = cameraManager.getCapabilities();
    
    // Update sliders
    const brightnessSlider = document.getElementById('brightnessSlider');
    if (brightnessSlider) {
        brightnessSlider.value = settings.brightness;
    }
    
    const contrastSlider = document.getElementById('contrastSlider');
    if (contrastSlider) {
        contrastSlider.value = settings.contrast;
    }
    
    const saturationSlider = document.getElementById('saturationSlider');
    if (saturationSlider) {
        saturationSlider.value = settings.saturation;
    }
    
    const flipToggle = document.getElementById('flipHorizontalToggle');
    if (flipToggle) {
        flipToggle.checked = settings.flipHorizontal;
    }
    
    // Update device selector
    cameraManager.updateDeviceSelector();
}

/**
 * Take screenshot
 */
function takeScreenshot() {
    if (!cameraManager || !cameraManager.isStreaming) {
        if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
            window.ArabicSignLanguage.showNotification('يرجى تشغيل الكاميرا أولاً', 'warning');
        }
        return;
    }
    
    const base64Image = cameraManager.captureFrameAsBase64();
    if (base64Image) {
        downloadImage(base64Image, `screenshot-${Date.now()}.jpg`);
        
        if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
            window.ArabicSignLanguage.showNotification('تم حفظ لقطة الشاشة', 'success');
        }
    }
}

/**
 * Download image
 */
function downloadImage(base64Data, filename) {
    const link = document.createElement('a');
    link.href = base64Data;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Camera stream start callback
 */
function onCameraStreamStart() {
    console.log('Camera stream started');
    
    if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
        window.ArabicSignLanguage.showNotification('تم تشغيل الكاميرا بنجاح', 'success');
    }
    
    // Start gesture recognition if available
    if (window.gestureRecognition && typeof window.gestureRecognition.start === 'function') {
        window.gestureRecognition.start();
    }
}

/**
 * Camera stream stop callback
 */
function onCameraStreamStop() {
    console.log('Camera stream stopped');
    
    // Stop gesture recognition if running
    if (window.gestureRecognition && typeof window.gestureRecognition.stop === 'function') {
        window.gestureRecognition.stop();
    }
}

/**
 * Camera error callback
 */
function onCameraError(error, message) {
    console.error('Camera error callback:', error, message);
    
    // Additional error handling can be added here
}

/**
 * Frame capture callback
 */
function onFrameCapture(imageData, canvas) {
    // This callback is called whenever a frame is captured
    // It can be used by gesture recognition or other modules
    
    // Trigger custom event for other modules
    const event = new CustomEvent('frameCapture', {
        detail: { imageData, canvas }
    });
    document.dispatchEvent(event);
}

/**
 * Show camera unsupported message
 */
function showCameraUnsupportedMessage() {
    const message = 'الكاميرا غير مدعومة في هذا المتصفح. يرجى استخدام متصفح حديث.';
    
    if (window.ArabicSignLanguage && window.ArabicSignLanguage.showNotification) {
        window.ArabicSignLanguage.showNotification(message, 'error');
    } else {
        alert(message);
    }
    
    // Hide camera-related UI elements
    const cameraElements = document.querySelectorAll('.camera-controls, .video-container');
    cameraElements.forEach(element => {
        element.style.display = 'none';
    });
}

// Export for use in other modules
window.cameraManager = cameraManager;
window.CameraManager = CameraManager;

console.log('Camera.js loaded successfully');
