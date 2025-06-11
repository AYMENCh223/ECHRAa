import pyttsx3
import threading
import time
from gtts import gTTS
import pygame
import io
import os
import tempfile

class TextToSpeech:
    def __init__(self):
        """
        Initialize Text-to-Speech engine
        """
        self.engine = None
        self.setup_engine()
        
        # Initialize pygame mixer for playing audio
        try:
            pygame.mixer.init()
            self.pygame_available = True
        except:
            self.pygame_available = False
            print("pygame not available, using pyttsx3 only")
        
        self.is_speaking = False
        
    def setup_engine(self):
        """Setup pyttsx3 engine with Arabic support"""
        try:
            self.engine = pyttsx3.init()
            
            # Try to find Arabic voice
            voices = self.engine.getProperty('voices')
            arabic_voice = None
            
            for voice in voices:
                # Look for Arabic voices (common identifiers)
                if any(keyword in voice.id.lower() for keyword in ['arabic', 'ar', 'عربي']):
                    arabic_voice = voice
                    break
            
            if arabic_voice:
                self.engine.setProperty('voice', arabic_voice.id)
                print(f"Using Arabic voice: {arabic_voice.name}")
            else:
                print("No Arabic voice found, using default voice")
            
            # Set speech rate and volume
            self.engine.setProperty('rate', 150)  # Slower rate for Arabic
            self.engine.setProperty('volume', 0.9)
            
        except Exception as e:
            print(f"Error initializing TTS engine: {str(e)}")
            self.engine = None
    
    def speak_with_pyttsx3(self, text):
        """
        Speak text using pyttsx3 (offline)
        
        Args:
            text: Arabic text to speak
        """
        if not self.engine:
            print("TTS engine not available")
            return
            
        try:
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.is_speaking = False
        except Exception as e:
            print(f"Error in pyttsx3 speech: {str(e)}")
            self.is_speaking = False
    
    def speak_with_gtts(self, text):
        """
        Speak text using Google Text-to-Speech (online)
        
        Args:
            text: Arabic text to speak
        """
        if not self.pygame_available:
            print("pygame not available for gTTS playback")
            return
            
        try:
            self.is_speaking = True
            
            # Create gTTS object
            tts = gTTS(text=text, lang='ar', slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Play audio using pygame
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Clean up temporary file
                os.unlink(tmp_file.name)
            
            self.is_speaking = False
            
        except Exception as e:
            print(f"Error in gTTS speech: {str(e)}")
            self.is_speaking = False
    
    def speak(self, text, method='auto'):
        """
        Speak Arabic text using available TTS method
        
        Args:
            text: Arabic text to speak
            method: 'pyttsx3', 'gtts', or 'auto' (try gtts first, fallback to pyttsx3)
        """
        if not text or not text.strip():
            return
            
        # Clean text (remove extra spaces, etc.)
        text = text.strip()
        
        def speak_async():
            if method == 'gtts':
                self.speak_with_gtts(text)
            elif method == 'pyttsx3':
                self.speak_with_pyttsx3(text)
            else:  # auto
                try:
                    # Try gTTS first (better Arabic pronunciation)
                    self.speak_with_gtts(text)
                except:
                    # Fallback to pyttsx3
                    print("gTTS failed, falling back to pyttsx3")
                    self.speak_with_pyttsx3(text)
        
        # Run TTS in a separate thread to avoid blocking
        if not self.is_speaking:
            thread = threading.Thread(target=speak_async)
            thread.daemon = True
            thread.start()
        else:
            print("Already speaking, please wait...")
    
    def stop(self):
        """Stop current speech"""
        try:
            if self.engine:
                self.engine.stop()
            
            if self.pygame_available:
                pygame.mixer.music.stop()
            
            self.is_speaking = False
        except Exception as e:
            print(f"Error stopping speech: {str(e)}")
    
    def is_busy(self):
        """Check if TTS is currently speaking"""
        return self.is_speaking
    
    def set_rate(self, rate):
        """
        Set speech rate
        
        Args:
            rate: Speech rate (words per minute)
        """
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
            except Exception as e:
                print(f"Error setting speech rate: {str(e)}")
    
    def set_volume(self, volume):
        """
        Set speech volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.engine:
            try:
                self.engine.setProperty('volume', min(1.0, max(0.0, volume)))
            except Exception as e:
                print(f"Error setting volume: {str(e)}")
    
    def get_available_voices(self):
        """
        Get list of available voices
        
        Returns:
            List of voice information
        """
        if not self.engine:
            return []
            
        try:
            voices = self.engine.getProperty('voices')
            voice_info = []
            
            for voice in voices:
                info = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown'),
                    'age': getattr(voice, 'age', 'unknown')
                }
                voice_info.append(info)
            
            return voice_info
        except Exception as e:
            print(f"Error getting voices: {str(e)}")
            return []
    
    def set_voice(self, voice_id):
        """
        Set specific voice by ID
        
        Args:
            voice_id: Voice identifier
        """
        if self.engine:
            try:
                self.engine.setProperty('voice', voice_id)
                print(f"Voice set to: {voice_id}")
            except Exception as e:
                print(f"Error setting voice: {str(e)}")
