import re
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

class LanguageHandler:
    def __init__(self):
        # Basic Hindi-English word mappings for government terms
        self.hi_en_dict = {
            'पानी': 'water',
            'बिजली': 'electricity', 
            'सेवा': 'service',
            'विभाग': 'department',
            'आवेदन': 'application',
            'प्रमाण पत्र': 'certificate',
            'जन्म प्रमाण पत्र': 'birth certificate',
            'मृत्यु प्रमाण पत्र': 'death certificate',
            'राशन कार्ड': 'ration card',
            'ड्राइविंग लाइसेंस': 'driving license',
            'पासपोर्ट': 'passport',
            'संपत्ति कर': 'property tax',
            'नगर निगम': 'municipal corporation',
            'स्वास्थ्य विभाग': 'health department',
            'शिक्षा विभाग': 'education department',
            'परिवहन विभाग': 'transport department',
            'ऑनलाइन': 'online',
            'फीस': 'fees',
            'दस्तावेज': 'documents',
            'आवश्यक': 'required',
            'सहायता': 'help',
            'जानकारी': 'information',
            'प्रक्रिया': 'procedure',
            'नमस्ते': 'hello',
            'स्वागत':'welcome',
            'पता':'adress',
            'ईमेल':'email',
            'फोन':'phone',
            'सरकार':'government',
            'संसाधन':'recources',
            'योजना':'scheme',
            'विभाग':'department'
        }
        
        self.en_hi_dict = {v: k for k, v in self.hi_en_dict.items()}
        
        # Common Hindi responses
        self.hindi_responses = {
            'water supply': 'पानी की आपूर्ति सेवाओं में कनेक्शन, बिलिंग और रखरखाव शामिल है। सहायता के लिए स्थानीय जल विभाग से संपर्क करें।',
            'electricity': 'बिजली सेवाओं में नए कनेक्शन, बिल भुगतान और खराबी की रिपोर्ट शामिल है। बिजली बोर्ड कार्यालय जाएं।',
            'birth certificate': 'जन्म प्रमाण पत्र रजिस्ट्रार कार्यालय से प्राप्त किया जा सकता है। आवश्यक दस्तावेजों में अस्पताल के रिकॉर्ड शामिल हैं।',
            'help': 'मैं सरकारी सेवाओं और जानकारी के साथ आपकी सहायता के लिए यहाँ हूँ। आप मुझसे पूछ सकते हैं:\n- सरकारी सेवाएं (पानी, बिजली, प्रमाण पत्र, आदि)\n- विभाग की जानकारी\n- आवेदन प्रक्रियाएं\n- दस्तावेज आवश्यकताएं'
        }
    
    def translate_to_english(self, hindi_text):
        """Basic Hindi to English translation"""
        if not hindi_text:
            return ""
        
        # Simple word-by-word replacement
        words = hindi_text.split()
        translated_words = []
        
        for word in words:
            # Remove punctuation for matching
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word in self.hi_en_dict:
                translated_words.append(self.hi_en_dict[clean_word])
            else:
                # Try transliteration as fallback
                try:
                    transliterated = transliterate(clean_word, sanscript.DEVANAGARI, sanscript.IAST)
                    translated_words.append(transliterated)
                except:
                    translated_words.append(word)
        
        return ' '.join(translated_words)
    
    def translate_to_hindi(self, english_text):
        """Basic English to Hindi translation"""
        if not english_text:
            return ""
        
        # Check for direct matches in responses
        english_lower = english_text.lower()
        for key, hindi_response in self.hindi_responses.items():
            if key in english_lower:
                return hindi_response
        
        # Simple word-by-word replacement
        words = english_text.split()
        translated_words = []
        
        for word in words:
            clean_word = word.lower().strip('.,!?;:')
            if clean_word in self.en_hi_dict:
                translated_words.append(self.en_hi_dict[clean_word])
            else:
                translated_words.append(word)
        
        result = ' '.join(translated_words)
        
        # If no translation found, provide a generic Hindi response
        if result == english_text:
            return f"जानकारी: {english_text}"
        
        return result
    
    def detect_language(self, text):
        """Detect if text is Hindi or English"""
        if not text:
            return 'english'
        
        # Count Devanagari characters
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        total_chars = len(re.findall(r'\S', text))
        
        if total_chars == 0:
            return 'english'
        
        hindi_ratio = hindi_chars / total_chars
        return 'hindi' if hindi_ratio > 0.3 else 'english'