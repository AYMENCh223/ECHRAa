import arabic_reshaper
from bidi.algorithm import get_display
import re

def reshape_arabic_text(text):
    """
    Reshape Arabic text for proper display
    
    Args:
        text: Arabic text string
        
    Returns:
        Properly shaped Arabic text
    """
    if not text:
        return text
        
    try:
        # Reshape Arabic text to handle character connections
        reshaped_text = arabic_reshaper.reshape(text)
        
        # Apply bidirectional algorithm for proper display
        display_text = get_display(reshaped_text)
        
        return display_text
    except Exception as e:
        print(f"Error reshaping Arabic text: {str(e)}")
        return text

def apply_arabic_grammar_rules(signs_list):
    """
    Apply basic Arabic grammar rules to a list of signs
    
    Args:
        signs_list: List of Arabic signs/letters
        
    Returns:
        Text with basic grammar rules applied
    """
    if not signs_list:
        return ""
    
    # Join signs into text
    text = " ".join(signs_list)
    
    # Apply basic grammar rules
    text = apply_basic_grammar(text)
    
    return text

def apply_basic_grammar(text):
    """
    Apply basic Arabic grammar transformations
    
    Args:
        text: Arabic text
        
    Returns:
        Text with basic grammar applied
    """
    if not text:
        return text
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Basic word corrections and combinations
    grammar_rules = {
        # Common letter combinations that form words
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
        'ن ع م': 'نعم',
        
        # Common prefixes
        'ال ': 'ال',  # Definite article
        'و ال': 'وال',  # And + definite article
        'ب ال': 'بال',  # With + definite article
        'ل ل': 'لل',    # For + definite article
        
        # Common suffixes
        ' ة': 'ة',     # Feminine marker
        ' ها': 'ها',   # Her/its
        ' هم': 'هم',   # Their (masculine)
        ' هن': 'هن',   # Their (feminine)
        ' ك': 'ك',     # Your
        ' ي': 'ي',     # My
    }
    
    # Apply grammar rules
    for pattern, replacement in grammar_rules.items():
        text = text.replace(pattern, replacement)
    
    return text

def detect_word_boundaries(signs_list):
    """
    Detect word boundaries in a sequence of signs
    
    Args:
        signs_list: List of signs/letters
        
    Returns:
        List of words formed from signs
    """
    if not signs_list:
        return []
    
    words = []
    current_word = []
    
    # Common word endings that indicate word completion
    word_endings = ['ة', 'ه', 'ك', 'ها', 'هم', 'هن', 'ي', 'نا']
    
    # Common standalone words
    standalone_words = ['أنا', 'أنت', 'هو', 'هي', 'نحن', 'أنتم', 'هم', 'هن', 
                       'لا', 'نعم', 'من', 'ما', 'أين', 'كيف', 'متى', 'لماذا']
    
    for sign in signs_list:
        current_word.append(sign)
        current_word_text = ''.join(current_word)
        
        # Check if current word is a standalone word
        if current_word_text in standalone_words:
            words.append(current_word_text)
            current_word = []
        # Check if current sign is a word ending
        elif sign in word_endings and len(current_word) > 1:
            words.append(current_word_text)
            current_word = []
        # Check if we've reached a reasonable word length
        elif len(current_word) >= 5:
            words.append(current_word_text)
            current_word = []
    
    # Add remaining letters as a word if any
    if current_word:
        words.append(''.join(current_word))
    
    return words

def suggest_word_completions(partial_word, word_list=None):
    """
    Suggest word completions for a partial Arabic word
    
    Args:
        partial_word: Partial word to complete
        word_list: List of words to search in (optional)
        
    Returns:
        List of suggested completions
    """
    if not partial_word:
        return []
    
    # Default Arabic words if none provided
    if word_list is None:
        word_list = [
            'أنا', 'أنت', 'أنتم', 'أنتن', 'هو', 'هي', 'نحن', 'هم', 'هن',
            'بيت', 'مدرسة', 'كتاب', 'قلم', 'طاولة', 'كرسي', 'باب', 'نافذة',
            'ماء', 'طعام', 'خبز', 'لحم', 'خضار', 'فاكهة', 'تفاح', 'برتقال',
            'أحمر', 'أزرق', 'أخضر', 'أصفر', 'أبيض', 'أسود', 'كبير', 'صغير',
            'سعيد', 'حزين', 'جميل', 'قبيح', 'سريع', 'بطيء', 'قوي', 'ضعيف',
            'أمس', 'اليوم', 'غداً', 'صباح', 'مساء', 'ليل', 'شهر', 'سنة'
        ]
    
    suggestions = []
    partial_lower = partial_word.lower()
    
    for word in word_list:
        if word.lower().startswith(partial_lower):
            suggestions.append(word)
    
    return suggestions[:10]  # Return top 10 suggestions

def is_arabic_text(text):
    """
    Check if text contains Arabic characters
    
    Args:
        text: Text to check
        
    Returns:
        Boolean indicating if text is Arabic
    """
    if not text:
        return False
    
    # Arabic Unicode range: 0600-06FF
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))

def clean_arabic_text(text):
    """
    Clean Arabic text by removing diacritics and extra characters
    
    Args:
        text: Arabic text to clean
        
    Returns:
        Cleaned Arabic text
    """
    if not text:
        return text
    
    # Remove Arabic diacritics (tashkeel)
    diacritics = re.compile(r'[\u064B-\u0652\u0670\u0640]')
    text = diacritics.sub('', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text

def get_text_direction(text):
    """
    Determine text direction (RTL for Arabic, LTR for others)
    
    Args:
        text: Text to analyze
        
    Returns:
        'rtl' for Arabic text, 'ltr' for others
    """
    if is_arabic_text(text):
        return 'rtl'
    return 'ltr'

def format_arabic_for_display(text):
    """
    Format Arabic text for proper web/UI display
    
    Args:
        text: Arabic text
        
    Returns:
        Formatted text ready for display
    """
    if not text:
        return text
    
    # Clean the text first
    text = clean_arabic_text(text)
    
    # Reshape for proper display
    text = reshape_arabic_text(text)
    
    return text
