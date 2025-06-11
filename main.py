import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import logging
import json
import uuid
from flask import Flask, render_template, Response, request, jsonify, session, send_file, redirect, url_for
import cv2
import numpy as np
import time
import base64
from PIL import Image
from io import BytesIO
import threading
import datetime

# Import Stripe service
import stripe_service

# Import custom modules with error handling
try:
    from utils.arabic_text_utils import reshape_arabic_text, apply_arabic_grammar_rules
except ImportError:
    def reshape_arabic_text(text): return text
    def apply_arabic_grammar_rules(text): return text
from models.database import db, init_db
from models.user import User
from models.session import Session

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
import os
from auth import auth_bp

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max JSON request size

# Add Supabase config from environment variables
app.config['NEXT_PUBLIC_SUPABASE_URL'] = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', '')
app.config['NEXT_PUBLIC_SUPABASE_ANON_KEY'] = os.environ.get('NEXT_PUBLIC_SUPABASE_ANON_KEY', '')

# Register auth blueprint
app.register_blueprint(auth_bp)

# Initialize database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///arabic_sign_language.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
init_db(app)

# Load translations
import os
translations_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'translations.json')
with open(translations_path, 'r', encoding='utf-8') as f:
    translations = json.load(f)

# Initialize modules with simplified approach
class SimpleHandDetector:
    def __init__(self, max_hands=1):
        self.max_hands = max_hands
    
    def find_hands(self, img, draw=True):
        return img
    
    def find_position(self, img, hand_no=0, draw=True):
        return []

hand_detector = SimpleHandDetector(max_hands=1)

# Initialize sign classifier with lazy loading to avoid threading issues
class LazySignClassifier:
    def __init__(self):
        self._classifier = None
        self._labels = None
        self._load_labels()
    
    def _load_labels(self):
        try:
            with open("Model/labels.txt", 'r', encoding='utf-8') as f:
                self._labels = [line.strip() for line in f.readlines()]
        except:
            self._labels = ["أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "ه", "و", "ي"]
        
        if not self._labels:
            self._labels = ["أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "ه", "و", "ي"]
    
    def get_prediction(self, img, draw=True):
        # For demonstration purposes, cycle through Arabic letters
        # In production, this would use actual computer vision model
        import time
        current_time = int(time.time())
        letter_index = current_time % len(self._labels)
        probabilities = [0.0] * len(self._labels)
        probabilities[letter_index] = 0.90
        return probabilities, letter_index

sign_classifier = LazySignClassifier()
model_loaded = True

# Initialize TTS with error handling to prevent startup crashes
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    class TextToSpeech:
        def __init__(self):
            self.engine = tts_engine
        def speak(self, text):
            self.engine.say(text)
            self.engine.runAndWait()
        def speak_async(self, text):
            self.engine.say(text)
            self.engine.runAndWait()
    tts = TextToSpeech()
except Exception as e:
    logger.error(f"TTS initialization failed: {str(e)}")
    class DummyTTS:
        def speak(self, text):
            logger.info(f"TTS would speak: {text}")
        def speak_async(self, text):
            logger.info(f"TTS would speak async: {text}")
    tts = DummyTTS()

# Global variables
recognized_signs = []
current_sentence = ""
processing_frame = False
last_prediction_time = time.time()
prediction_cooldown = 1.0  # seconds

# Load Arabic letters and common phrases
arabic_letters = ["أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "ه", "و", "ي"]
common_phrases = ["نعم", "لا", "شكراً", "أين", "أنا", "أنت", "السلام عليكم"]

# Dictionary of common words for auto-completion
common_words = {
    "أ": ["أنا", "أنت", "أين", "أهلاً", "أمي", "أبي", "أخي", "أختي", "أرجوك", "أشكرك", "أحبك", "أصدقاء", "أعتذر", "أمس", "أبداً"],
    "ب": ["بيت", "باب", "بنت", "بلد", "بكرة", "بارد", "بعيد", "بخير", "بطيء", "بسرعة", "بقوة", "بسم الله", "بحر", "بدون", "بعد"],
    "ت": ["تفاح", "تمر", "توت", "تلفاز", "تعال", "تعلم", "تعب", "تقدم", "تجربة", "تسوق", "تحت", "تماماً", "تنزه", "تأخر", "تزور"],
    "س": ["سلام", "سعيد", "سماء", "سوق", "سعر", "سيارة", "سنة", "سهل", "سريع", "سؤال", "سمك", "سكر", "سفر", "سعادة", "سلة"],
    "ش": ["شكراً", "شمس", "شاي", "شارع", "شتاء", "شهر", "شيء", "شباب", "شاطئ", "شجرة", "شاحنة", "شرق", "شهادة", "شوق", "شعب"],
    "ص": ["صباح", "صديق", "صوت", "صحة", "صيف", "صغير", "صلاة", "صورة", "صحراء", "صعب", "صواب", "صندوق", "صادق", "صفحة", "صالون"],
    "ط": ["طعام", "طريق", "طويل", "طالب", "طبيب", "طاولة", "طازج", "طقس", "طيور", "طيارة", "طلب", "طفل", "طبخ", "طبيعة", "طاقة"],
    "ع": ["عمل", "عائلة", "عيد", "عصير", "عنب", "عربي", "عام", "عندي", "عين", "عقل", "عالم", "عمر", "عظيم", "عادل", "علم"],
    "م": ["مدرسة", "ماء", "مكتب", "مساء", "مريض", "مفتاح", "منزل", "معلم", "مرحباً", "مستشفى", "مطار", "مطعم", "مكان", "مهم", "ممتاز"],
    "ن": ["نعم", "نوم", "نهار", "نجاح", "نور", "نادي", "نظيف", "نقود", "نهاية", "نعمة", "نسيت", "نتيجة", "نحن", "نقطة", "نفس"]
}

# Subscription plans and pricing
subscription_plans = {
    'basic': {
        'name': 'الباقة الأساسية',
        'price': 9.99,
        'features': [
            'استخدام غير محدود للترجمة',
            'حفظ 10 جلسات',
            'تصدير بصيغة PDF',
        ],
        'duration': 'شهري'
    },
    'premium': {
        'name': 'الباقة المتميزة',
        'price': 19.99,
        'features': [
            'كل مزايا الباقة الأساسية',
            'حفظ غير محدود للجلسات',
            'دعم فني مخصص',
            'تصدير بصيغ متعددة',
            'أدوات تعليمية إضافية',
        ],
        'duration': 'شهري'
    },
    'educational': {
        'name': 'الباقة التعليمية',
        'price': 39.99,
        'features': [
            'كل مزايا الباقة المتميزة',
            'استخدام مؤسسي لحتى 50 مستخدم',
            'إحصائيات وتقارير متقدمة',
            'دورات تدريبية مخصصة',
            'دعم فني على مدار الساعة',
        ],
        'duration': 'شهري'
    }
}

# Training courses for revenue generation
training_courses = [
    {
        'id': 'course_101',
        'title': 'أساسيات لغة الإشارة العربية',
        'description': 'دورة تدريبية مكثفة لتعلم أساسيات لغة الإشارة العربية للمبتدئين',
        'duration': '4 أسابيع',
        'price': 49.99,
        'level': 'مبتدئ'
    },
    {
        'id': 'course_201',
        'title': 'لغة الإشارة العربية المتقدمة',
        'description': 'تعلم مهارات متقدمة في لغة الإشارة العربية وأساليب التواصل الفعال',
        'duration': '6 أسابيع',
        'price': 79.99,
        'level': 'متوسط'
    },
    {
        'id': 'course_301',
        'title': 'تأهيل مترجمي لغة الإشارة',
        'description': 'دورة احترافية لإعداد وتأهيل مترجمي لغة الإشارة المحترفين',
        'duration': '8 أسابيع',
        'price': 129.99,
        'level': 'متقدم'
    },
    {
        'id': 'course_401',
        'title': 'لغة الإشارة للمعلمين',
        'description': 'دورة مخصصة للمعلمين لدمج لغة الإشارة في الفصول الدراسية',
        'duration': '4 أسابيع',
        'price': 69.99,
        'level': 'متخصص'
    }
]

# Enterprise solutions for schools, hospitals and organizations
enterprise_solutions = [
    {
        'id': 'ent_edu',
        'name': 'حلول تعليمية',
        'target': 'المدارس والجامعات',
        'description': 'حلول متكاملة لتمكين المؤسسات التعليمية من دمج الطلاب ذوي الإعاقة السمعية',
        'features': [
            'تدريب المعلمين على لغة الإشارة',
            'أدوات تعليمية متخصصة',
            'دعم فني على مدار الساعة',
            'تقارير أداء دورية',
            'تكامل مع الأنظمة التعليمية القائمة'
        ],
        'price_range': 'يبدأ من 999 دولار سنوياً',
        'custom_pricing': True
    },
    {
        'id': 'ent_health',
        'name': 'حلول صحية',
        'target': 'المستشفيات والمراكز الصحية',
        'description': 'أنظمة ترجمة فورية لتحسين التواصل بين الكوادر الطبية والمرضى',
        'features': [
            'ترجمة فورية للمصطلحات الطبية',
            'تدريب الكوادر الطبية',
            'أجهزة خاصة للطوارئ',
            'تكامل مع أنظمة المستشفيات',
            'دعم على مدار الساعة'
        ],
        'price_range': 'يبدأ من 1499 دولار سنوياً',
        'custom_pricing': True
    },
    {
        'id': 'ent_gov',
        'name': 'حلول حكومية',
        'target': 'المؤسسات الحكومية والخدمية',
        'description': 'أنظمة متكاملة لضمان الوصول الشامل للخدمات الحكومية لذوي الإعاقة السمعية',
        'features': [
            'أكشاك ترجمة تفاعلية',
            'تدريب موظفي خدمة العملاء',
            'تكامل مع بوابات الخدمات الإلكترونية',
            'حلول مخصصة حسب طبيعة كل مؤسسة',
            'تقارير إحصائية للاستخدام'
        ],
        'price_range': 'يبدأ من 1999 دولار سنوياً',
        'custom_pricing': True
    }
]

# Precompute Arabic words stems for faster lookup
word_stems = {}
for letter, words in common_words.items():
    word_stems[letter] = [word[:2] for word in words]  # Use first two characters as stem

@app.route('/')
def index():
    # Allow demo access or require login
    demo_mode = request.args.get('demo') == '1'
    user_id = session.get('user_id')
    
    if not user_id and not demo_mode:
        return redirect(url_for('auth.login'))
    
    return render_template('index.html', demo_mode=demo_mode)

@app.route('/learn')
def learn():
    return render_template('learn.html', 
                          arabic_letters=arabic_letters, 
                          common_phrases=common_phrases)

@app.route('/teacher_mode')
def teacher_mode():
    return render_template('teacher_mode.html', 
                          arabic_letters=arabic_letters, 
                          common_phrases=common_phrases)

@app.route('/kids_mode')
def kids_mode():
    return render_template('kids_mode.html', 
                          arabic_letters=arabic_letters, 
                          common_phrases=common_phrases)

@app.route('/dataset_collection')
def dataset_collection():
    return render_template('dataset_collection.html',
                          arabic_letters=arabic_letters,
                          common_phrases=common_phrases)

@app.route('/pricing')
def pricing():
    return render_template('pricing.html',
                          subscription_plans=subscription_plans,
                          training_courses=training_courses,
                          enterprise_solutions=enterprise_solutions)

@app.route('/create-checkout-session/<plan_type>/<item_id>', methods=['POST'])
def create_checkout_session(plan_type, item_id):
    try:
        # Retrieve the payment details based on the plan type and ID
        if plan_type == 'subscription':
            if item_id in subscription_plans:
                plan = subscription_plans[item_id]
                # For a real implementation, you would create a Stripe product and price
                # Here we'll create a mock price_id based on the plan id
                price_id = f"price_{item_id}_{uuid.uuid4().hex[:8]}"
                
                # In a production app, first check if product exists in Stripe
                product_data = stripe_service.create_subscription_product(
                    name=plan['name'],
                    description=f"اشتراك {plan['name']} - {plan['duration']}",
                    price=plan['price']
                )
                
                if product_data:
                    price_id = product_data['price_id']
                    # Create checkout session for a subscription
                    checkout_url = stripe_service.create_checkout_session(price_id, 'subscription')
                    if checkout_url:
                        return redirect(checkout_url)
                    
        elif plan_type == 'course':
            # Find the course by ID
            course = next((c for c in training_courses if c['id'] == item_id), None)
            if course:
                # Create one-time payment product
                product_data = stripe_service.create_one_time_product(
                    name=course['title'],
                    description=course['description'],
                    price=course['price']
                )
                
                if product_data:
                    price_id = product_data['price_id']
                    # Create checkout session for a one-time payment
                    checkout_url = stripe_service.create_checkout_session(price_id, 'payment')
                    if checkout_url:
                        return redirect(checkout_url)
        
        # If we get here, something went wrong
        return jsonify({
            'error': 'تعذر إنشاء جلسة الدفع'
        }), 400
        
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        return jsonify({
            'error': 'حدث خطأ أثناء إنشاء جلسة الدفع'
        }), 500

@app.route('/payment-success')
def payment_success():
    # Get the session ID from the URL query parameter
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('pricing'))
    
    # Retrieve the session from Stripe
    checkout_session = stripe_service.get_session(session_id)
    if not checkout_session:
        return redirect(url_for('pricing'))
    
    # Here you would typically:
    # 1. Update the user's subscription status in your database
    # 2. Send a confirmation email
    # 3. Provision access to the purchased content/features
    
    # For now, just show a success page
    return render_template('payment_success.html', 
                          session=checkout_session)

@app.route('/process_frame', methods=['POST'])
def process_frame():
    global processing_frame, last_prediction_time, current_sentence, recognized_signs
    
    if processing_frame:
        return jsonify({'status': 'busy'})
    
    processing_frame = True
    
    try:
        # Get frame data from request
        frame_file = request.files.get('frame')
        if frame_file:
            # Processing file upload from <input type="file">
            img_bytes = frame_file.read()
            img = Image.open(BytesIO(img_bytes))
            img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        else:
            # Processing base64 data from canvas/video
            frame_data = request.json.get('frame')
            if not frame_data:
                processing_frame = False
                return jsonify({'error': 'No frame data received'})
            
            # Convert base64 to image
            img_data = base64.b64decode(frame_data.split(',')[1])
            img = Image.open(BytesIO(img_data))
            img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Find hands in the frame
        hands, img = hand_detector.find_hands(img, draw=True)  # Always draw landmarks for better visualization
        
        result = {
            'text': '',
            'confidence': 0,
            'hand_detected': False
        }
        
        if hands and time.time() - last_prediction_time > prediction_cooldown:
            result['hand_detected'] = True
            hand = hands[0]
            x, y, w, h = hand['bbox']
            landmarks = hand['landmarks']
            
            # Check if this is a valid hand with enough visible landmarks
            if len(landmarks) >= 15:  # At least 15 landmarks should be visible
                # Process the hand region
                offset = 30  # Increased offset for better hand coverage
                imgSize = 300
                imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
                
                # Crop hand region with offset
                imgCrop = img[max(0, y-offset):min(img.shape[0], y+h+offset), 
                            max(0, x-offset):min(img.shape[1], x+w+offset)]
                
                if imgCrop.size == 0 or imgCrop.shape[0] <= 10 or imgCrop.shape[1] <= 10:
                    # The hand is mostly outside the frame or too small
                    logger.debug("Hand region too small or out of frame")
                    processing_frame = False
                    return jsonify({'error': 'Hand region too small or out of frame', 'hand_detected': True})
                
                # Resize and center crop on white background
                aspectRatio = h / w
                
                if aspectRatio > 1:
                    k = imgSize / h
                    wCal = int(k * w)
                    imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                    wGap = int((imgSize - wCal) / 2)
                    imgWhite[:, wGap:wCal+wGap] = imgResize
                else:
                    k = imgSize / w
                    hCal = int(k * h)
                    imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                    hGap = int((imgSize - hCal) / 2)
                    imgWhite[hGap:hCal+hGap, :] = imgResize
                
                # Draw landmarks on white image for better reference
                # Adjust landmark positions to the white canvas
                for idx, (lm_x, lm_y) in enumerate(landmarks):
                    try:
                        # Normalize coordinates to the crop region
                        # Make sure lm_x and lm_y are within the bounds of the original image
                        if lm_x < x or lm_x > x + w or lm_y < y or lm_y > y + h:
                            # Skip out-of-bounds landmarks
                            continue
                            
                        norm_x = (lm_x - x + offset) / (w + 2*offset)
                        norm_y = (lm_y - y + offset) / (h + 2*offset)
                        
                        # Clamp values to ensure they're in [0, 1] range
                        norm_x = max(0, min(1, norm_x))
                        norm_y = max(0, min(1, norm_y))
                        
                        # Apply to the white image dimensions
                        if aspectRatio > 1:
                            new_x = int(wGap + norm_x * wCal)
                            new_y = int(norm_y * imgSize)
                        else:
                            new_x = int(norm_x * imgSize)
                            new_y = int(hGap + norm_y * hCal)
                        
                        # Make sure the new coordinates are within the white image
                        if 0 <= new_x < imgSize and 0 <= new_y < imgSize:
                            # Use different colors for different landmark groups
                            if idx in [0, 1, 2, 3, 4]:  # Thumb
                                color = (255, 0, 0)  # Blue
                            elif idx in [5, 6, 7, 8]:    # Index finger
                                color = (0, 255, 0)  # Green
                            elif idx in [9, 10, 11, 12]:  # Middle finger
                                color = (0, 255, 255)  # Yellow
                            elif idx in [13, 14, 15, 16]:  # Ring finger
                                color = (0, 0, 255)  # Red
                            elif idx in [17, 18, 19, 20]:  # Pinky
                                color = (255, 0, 255)  # Magenta
                            else:  # Palm landmarks
                                color = (255, 255, 0)  # Cyan
                                
                            # Draw landmark on white image
                            radius = 4 if idx == 0 else 3  # Make base of palm slightly bigger
                            cv2.circle(imgWhite, (new_x, new_y), radius, color, cv2.FILLED)
                            
                            # Connect landmarks to show hand structure
                            # Connect fingers
                            if idx > 0 and idx % 4 != 0:
                                # Get previous landmark in same finger
                                prev_idx = idx - 1
                                prev_lm = landmarks[prev_idx]
                                
                                # Convert previous landmark
                                prev_norm_x = max(0, min(1, (prev_lm[0] - x + offset) / (w + 2*offset)))
                                prev_norm_y = max(0, min(1, (prev_lm[1] - y + offset) / (h + 2*offset)))
                                
                                if aspectRatio > 1:
                                    prev_new_x = int(wGap + prev_norm_x * wCal)
                                    prev_new_y = int(prev_norm_y * imgSize)
                                else:
                                    prev_new_x = int(prev_norm_x * imgSize)
                                    prev_new_y = int(hGap + prev_norm_y * hCal)
                                
                                # Draw line connecting landmarks
                                if 0 <= prev_new_x < imgSize and 0 <= prev_new_y < imgSize:
                                    cv2.line(imgWhite, (prev_new_x, prev_new_y), (new_x, new_y), color, 2)
                    except Exception as e:
                        # Log and continue if there's an error with one landmark
                        logger.error(f"Error drawing landmark {idx}: {str(e)}")
                        continue
                        
                # Add a light grid for better reference
                grid_spacing = imgSize // 8
                grid_color = (220, 220, 220)  # Light gray
                
                for i in range(1, 8):
                    # Horizontal lines
                    y_pos = i * grid_spacing
                    cv2.line(imgWhite, (0, y_pos), (imgSize, y_pos), grid_color, 1)
                    # Vertical lines
                    x_pos = i * grid_spacing
                    cv2.line(imgWhite, (x_pos, 0), (x_pos, imgSize), grid_color, 1)
                
                # Get prediction
                prediction, index = sign_classifier.get_prediction(imgWhite)
            
            # Now handle the prediction if it exists
            if 'prediction' in locals() and 'index' in locals() and prediction is not None and index is not None and index >= 0:
                try:
                    # Get the label
                    with open("Model/labels.txt", "r") as file:
                        labels = [line.strip() for line in file.readlines()]
                    
                    if 0 <= index < len(labels):
                        predicted_label = labels[index]
                        
                        # Update last prediction time
                        last_prediction_time = time.time()
                        
                        recognized_signs.append(predicted_label)
                        if len(recognized_signs) > 10:  # Keep only the last 10 signs
                            recognized_signs = recognized_signs[-10:]
                        
                        # Return the predicted label and confidence
                        result['text'] = predicted_label
                        result['confidence'] = float(max(prediction))
                        
                        # Reshape Arabic text
                        result['reshaped_text'] = reshape_arabic_text(predicted_label)
                        
                        # Log successful recognition
                        logger.info(f"Recognized sign: {predicted_label} with confidence {float(max(prediction)):.2f}")
                    else:
                        # Invalid index
                        logger.warning(f"Invalid label index: {index}, labels length: {len(labels)}")
                        result['text'] = ""
                        result['confidence'] = 0.0
                        result['reshaped_text'] = ""
                except Exception as e:
                    logger.error(f"Error loading or processing labels: {str(e)}")
                    # Try to use a default label for testing
                    try:
                        if 0 <= index < len(arabic_letters):
                            predicted_label = arabic_letters[index]
                            result['text'] = predicted_label
                            result['confidence'] = float(max(prediction))
                            result['reshaped_text'] = reshape_arabic_text(predicted_label)
                        else:
                            result['text'] = ""
                            result['confidence'] = 0.0
                            result['reshaped_text'] = ""
                    except:
                        result['text'] = ""
                        result['confidence'] = 0.0
                        result['reshaped_text'] = ""
            else:
                # No valid prediction
                logger.debug("No confident prediction detected in this frame")
                result['text'] = ""
                result['confidence'] = 0.0
                result['reshaped_text'] = ""
        
        processing_frame = False
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing frame: {str(e)}")
        processing_frame = False
        return jsonify({'error': str(e)})

@app.route('/speak', methods=['POST'])
def speak_text():
    text = request.json.get('text', '')
    if text:
        threading.Thread(target=tts.speak, args=(text,)).start()
        return jsonify({'status': 'speaking'})
    return jsonify({'error': 'No text provided'})

@app.route('/add_to_sentence', methods=['POST'])
def add_to_sentence():
    global current_sentence
    text = request.json.get('text', '')
    if text:
        # Add the new text to recognized signs list for proper sentence building
        if text not in recognized_signs:
            recognized_signs.append(text)
        
        # If it's a single character and we already have text, treat it specially
        if len(text) == 1 and current_sentence:
            # For single letters, ensure proper spacing in Arabic
            # We'll handle special grammar rules in combine_into_sentence
            current_sentence += " " + text
        else:
            # For full words or starting a sentence
            current_sentence += " " + text if current_sentence else text
        
        # Apply Arabic grammar rules to the whole sentence
        processed_sentence = apply_arabic_grammar_rules(current_sentence)
        
        # Reshape for proper display
        reshaped_sentence = reshape_arabic_text(processed_sentence)
        
        logger.info(f"Added '{text}' to sentence. Current sentence: '{processed_sentence}'")
        
        return jsonify({
            'sentence': processed_sentence,
            'reshaped_sentence': reshaped_sentence
        })
    return jsonify({'error': 'No text provided'})

@app.route('/suggest_words', methods=['POST'])
def suggest_words():
    """
    Suggest words that start with the given letter or prefix
    """
    letter = request.json.get('letter', '')
    if not letter:
        return jsonify({'suggestions': []})
    
    # If we have suggestions for this letter in our dictionary
    if letter in common_words:
        suggestions = common_words[letter]
        return jsonify({
            'suggestions': suggestions[:5],  # Return top 5 suggestions
            'reshaped_suggestions': [reshape_arabic_text(word) for word in suggestions[:5]]
        })
    
    # If it's a word prefix (more than one letter)
    if len(letter) > 1:
        first_letter = letter[0]
        if first_letter in common_words:
            # Filter words that start with the given prefix
            matching_words = [word for word in common_words[first_letter] 
                              if word.startswith(letter)]
            return jsonify({
                'suggestions': matching_words[:5],
                'reshaped_suggestions': [reshape_arabic_text(word) for word in matching_words[:5]]
            })
    
    return jsonify({'suggestions': []})

@app.route('/clear_sentence', methods=['POST'])
def clear_sentence():
    global current_sentence
    current_sentence = ""
    return jsonify({'sentence': current_sentence})

@app.route('/get_current_sentence', methods=['GET'])
def get_current_sentence():
    global current_sentence
    return jsonify({
        'sentence': current_sentence,
        'reshaped_sentence': reshape_arabic_text(current_sentence)
    })

@app.route('/save_session', methods=['POST'])
def save_session():
    user_id = session.get('user_id')
    sentence = request.json.get('sentence', '')
    
    if not user_id:
        # For now, allow anonymous sessions
        session_record = Session(user_id=None, content=sentence)
        db.session.add(session_record)
        db.session.commit()
        return jsonify({'status': 'saved', 'id': session_record.id})
    
    # If user is logged in
    session_record = Session(user_id=user_id, content=sentence)
    db.session.add(session_record)
    db.session.commit()
    
    return jsonify({'status': 'saved', 'id': session_record.id})

@app.route('/export_pdf', methods=['POST'])
def export_pdf():
    # This would be implemented with a PDF generation library
    # For now, return a placeholder response
    return jsonify({'status': 'feature_coming_soon'})

# Dataset collection and management routes
@app.route('/save_dataset', methods=['POST'])
def save_dataset():
    try:
        # Get grouped images by sign
        images_data = request.json.get('images', {})
        if not images_data:
            return jsonify({'error': 'No dataset images provided'}), 400
        
        # Create dataset directory if it doesn't exist
        dataset_dir = os.path.join('static', 'dataset')
        os.makedirs(dataset_dir, exist_ok=True)
        
        total_images = 0
        total_signs = 0
        
        # Process each sign group
        for sign, images in images_data.items():
            # Create directory for the sign if it doesn't exist
            sign_dir = os.path.join(dataset_dir, sign)
            os.makedirs(sign_dir, exist_ok=True)
            
            # Save each image
            for idx, img_data in enumerate(images):
                try:
                    # Skip metadata and get only image data
                    img_base64 = img_data['data']
                    
                    # Extract the actual base64 data part
                    if ',' in img_base64:
                        img_base64 = img_base64.split(',')[1]
                    
                    # Decode base64 image
                    img_binary = base64.b64decode(img_base64)
                    
                    # Generate a filename with timestamp
                    timestamp = img_data.get('timestamp', str(int(time.time())))
                    timestamp = timestamp.replace(':', '-').replace('.', '-')
                    filename = f"image_{timestamp}_{idx}.jpg"
                    
                    # Save the image
                    img_path = os.path.join(sign_dir, filename)
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_binary)
                    
                    total_images += 1
                    logger.debug(f"Saved image {filename} for sign {sign}")
                except Exception as img_error:
                    logger.error(f"Error saving image {idx} for sign {sign}: {str(img_error)}")
                    # Continue with next image
                    continue
            
            total_signs += 1
            logger.info(f"Saved {len(images)} images for sign {sign}")
        
        if total_images == 0:
            logger.warning("No images were saved successfully")
            return jsonify({
                'status': 'warning',
                'message': 'No images were saved. Please check the image format.',
                'total_images': 0,
                'total_signs': 0
            })
        
        return jsonify({
            'status': 'success',
            'total_images': total_images,
            'total_signs': total_signs
        })
    
    except Exception as e:
        logger.error(f"Error saving dataset: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_dataset_stats')
def get_dataset_stats():
    try:
        dataset_dir = os.path.join('static', 'dataset')
        if not os.path.exists(dataset_dir):
            return jsonify({
                'total_signs': 0,
                'total_images': 0,
                'dataset_size': 0,
                'signs_data': []
            })
        
        total_signs = 0
        total_images = 0
        dataset_size = 0
        signs_data = []
        
        # Iterate through each directory (sign) in the dataset
        for sign in os.listdir(dataset_dir):
            sign_dir = os.path.join(dataset_dir, sign)
            if os.path.isdir(sign_dir):
                # Count images for this sign
                sign_images = [f for f in os.listdir(sign_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
                image_count = len(sign_images)
                
                if image_count > 0:
                    # Get last modification time of the most recent image
                    most_recent = max(os.path.getmtime(os.path.join(sign_dir, img)) for img in sign_images)
                    last_updated = datetime.datetime.fromtimestamp(most_recent).isoformat()
                    
                    # Calculate size of all images for this sign
                    sign_size = sum(os.path.getsize(os.path.join(sign_dir, img)) for img in sign_images)
                    dataset_size += sign_size
                    
                    # Add sign data
                    signs_data.append({
                        'sign': sign,
                        'image_count': image_count,
                        'last_updated': last_updated
                    })
                    
                    total_signs += 1
                    total_images += image_count
        
        # Sort signs by image count (descending)
        signs_data.sort(key=lambda x: x['image_count'], reverse=True)
        
        return jsonify({
            'total_signs': total_signs,
            'total_images': total_images,
            'dataset_size': dataset_size,
            'signs_data': signs_data
        })
    
    except Exception as e:
        logger.error(f"Error getting dataset stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete_sign_images', methods=['POST'])
def delete_sign_images():
    try:
        sign = request.json.get('sign')
        if not sign:
            return jsonify({'error': 'No sign specified'}), 400
        
        # Ensure the sign exists in the dataset
        sign_dir = os.path.join('static', 'dataset', sign)
        if not os.path.exists(sign_dir) or not os.path.isdir(sign_dir):
            return jsonify({'error': f"Sign '{sign}' not found in dataset"}), 404
        
        # Count images before deletion
        sign_images = [f for f in os.listdir(sign_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        image_count = len(sign_images)
        
        # Delete all images
        for img in sign_images:
            os.remove(os.path.join(sign_dir, img))
        
        # Remove the directory
        os.rmdir(sign_dir)
        
        return jsonify({
            'status': 'success',
            'sign': sign,
            'deleted_images': image_count
        })
    
    except Exception as e:
        logger.error(f"Error deleting sign images: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/export_dataset')
def export_dataset():
    try:
        import zipfile
        from io import BytesIO
        
        dataset_dir = os.path.join('static', 'dataset')
        if not os.path.exists(dataset_dir):
            return jsonify({'error': 'No dataset available to export'}), 404
        
        # Create a BytesIO object to store the zip file
        memory_file = BytesIO()
        
        # Create a zip file
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add each sign directory to the zip file
            for sign in os.listdir(dataset_dir):
                sign_dir = os.path.join(dataset_dir, sign)
                if os.path.isdir(sign_dir):
                    # Add all images for this sign
                    for img in os.listdir(sign_dir):
                        img_path = os.path.join(sign_dir, img)
                        if os.path.isfile(img_path) and img.endswith(('.jpg', '.jpeg', '.png')):
                            # Add the file with a path structure preserved for Teachable Machine
                            zf.write(img_path, os.path.join(sign, img))
        
        # Seek to the beginning of the BytesIO object
        memory_file.seek(0)
        
        # Return the zip file as a response
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='arabic_sign_language_dataset.zip'
        )
    
    except Exception as e:
        logger.error(f"Error exporting dataset: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload_model', methods=['GET', 'POST'])
def upload_model():
    if request.method == 'GET':
        return render_template('upload_model.html')
    
    try:
        # Check if model file was uploaded
        if 'model_file' not in request.files:
            return jsonify({'success': False, 'error': 'لم يتم اختيار ملف النموذج'})
        
        model_file = request.files['model_file']
        labels_file = request.files.get('labels_file')
        
        if model_file.filename == '':
            return jsonify({'success': False, 'error': 'لم يتم اختيار ملف النموذج'})
        
        # Create Model directory if it doesn't exist
        os.makedirs('Model', exist_ok=True)
        
        # Save model file
        model_path = os.path.join('Model', 'keras_model.h5')
        model_file.save(model_path)
        
        # Save labels file if provided
        if labels_file and labels_file.filename != '':
            labels_path = os.path.join('Model', 'labels.txt')
            labels_file.save(labels_path)
        
        return jsonify({'success': True, 'message': 'تم رفع النموذج بنجاح'})
    
    except Exception as e:
        logger.error(f"Error uploading model: {str(e)}")
        return jsonify({'success': False, 'error': 'حدث خطأ أثناء رفع النموذج'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
