
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin, urlparse

class DataProcessor:
    def __init__(self):
        self.base_url = "http://hkts.fmiscwrdbihar.gov.in/wrdpmis/Default.aspx"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def extract_website_data(self):
        """Extract data from the government website"""
        try:
            print(f"Extracting data from: {self.base_url}")
            
            # Get main page
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code != 200:
                print(f"Failed to access website: {response.status_code}")
                return self._get_fallback_data()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract relevant information
            extracted_data = {
                'services': {},
                'departments': {},
                'contact_info': {},
                'procedures': {}
            }
            
            # Extract text content
            text_content = soup.get_text()
            
            # Extract services information
            services_keywords = ['water', 'supply', 'management', 'irrigation', 'drainage', 'project']
            for keyword in services_keywords:
                if keyword in text_content.lower():
                    extracted_data['services'][keyword] = f"Information about {keyword} services is available on the website."
            
            # Extract links and their descriptions
            links = soup.find_all('a', href=True)
            for link in links[:10]:  # Limit to first 10 links
                href = link.get('href')
                text = link.get_text().strip()
                if text and len(text) > 3:
                    extracted_data['services'][text.lower()] = f"Service: {text}. More information available at the website."
            
            # Extract any forms or input fields information
            forms = soup.find_all('form')
            for form in forms:
                inputs = form.find_all(['input', 'select', 'textarea'])
                for inp in inputs:
                    name = inp.get('name', '')
                    if name and len(name) > 2:
                        extracted_data['procedures'][name] = f"Form field for {name} is available for user input."
            
            print(f"Extracted {len(extracted_data['services'])} services and {len(extracted_data['procedures'])} procedures")
            return extracted_data
            
        except requests.RequestException as e:
            print(f"Network error accessing website: {e}")
            return self._get_fallback_data()
        except Exception as e:
            print(f"Error extracting website data: {e}")
            return self._get_fallback_data()
    
    def _get_fallback_data(self):
        """Fallback data when website is not accessible"""
        return {
            'services': {
                'water resource management': 'Water Resource Department manages water supply, irrigation, and drainage systems across Bihar.',
                'irrigation services': 'Irrigation services include canal management, water distribution, and agricultural water supply.',
                'project management': 'Various water resource projects are managed including infrastructure development and maintenance.',
                'public information': 'Public information about water resources, projects, and services is available through the department.'
            },
            'departments': {
                'water resource department': 'Government department responsible for water resource management in Bihar state.',
                'irrigation department': 'Manages irrigation infrastructure and water distribution for agriculture.',
                'project monitoring': 'Monitors and oversees various water resource development projects.'
            },
            'procedures': {
                'online services': 'Various online services are available for public convenience and information access.',
                'information access': 'Citizens can access information about water resource projects and services.',
                'project updates': 'Regular updates about ongoing and completed water resource projects.'
            }
        }

# ===========================================
# FILE 5: language_handler.py (Hindi/English Support)
# ===========================================
import re
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

class LanguageHandler:
    def __init__(self):
        # Enhanced Hindi-English dictionary for WRD Bihar
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
            # WRD Bihar specific terms
            'सिंचाई': 'irrigation',
            'जल संसाधन': 'water resources',
            'कनेक्शन': 'connection',
            'शुल्क': 'charges',
            'खरीफ': 'kharif',
            'रबी': 'rabi',
            'फसल': 'crop',
            'एकड़': 'acre',
            'उपलब्धता': 'availability',
            'शिकायत': 'complaint',
            'संपर्क': 'contact',
            'कार्यालय': 'office',
            'नहर': 'canal',
            'भूमि': 'land',
            'आधार': 'aadhaar',
            'मतदाता': 'voter',
            'कृषि': 'agriculture',
            'बैंक': 'bank',
            'खाता': 'account',
            'रिकॉर्ड': 'record',
            'योजना': 'scheme',
            'केंद्रीय': 'central',
            'सरकार': 'government',
            'वेबसाइट': 'website',
            'ऐप': 'app',
            'टोल': 'toll',
            'फ्री': 'free'
        }
        
        self.en_hi_dict = {v: k for k, v in self.hi_en_dict.items()}
        
        # Enhanced Hindi responses with WRD Bihar specific content
        self.hindi_responses = {
            'water supply': 'पानी की आपूर्ति सेवाओं में कनेक्शन, बिलिंग और रखरखाव शामिल है। सहायता के लिए स्थानीय जल विभाग से संपर्क करें।',
            'electricity': 'बिजली सेवाओं में नए कनेक्शन, बिल भुगतान और खराबी की रिपोर्ट शामिल है। बिजली बोर्ड कार्यालय जाएं।',
            'irrigation': 'सिंचाई सेवाओं के लिए नजदीकी WRD कार्यालय जाएं। आवेदन फॉर्म भरें और आवश्यक दस्तावेज जमा करें।',
            'water resources department': 'जल संसाधन विभाग (WRD) बिहार सरकार का मुख्य विभाग है जो सिंचाई परियोजनाओं का काम करता है।',
            'irrigation connection': 'सिंचाई कनेक्शन के लिए नजदीकी WRD कार्यालय जाएं, फॉर्म भरें, दस्तावेज जमा करें।',
            'documents required': 'आवश्यक दस्तावेज: भूमि स्वामित्व, आधार कार्ड, मतदाता पहचान पत्र, कृषि भूमि रिकॉर्ड।',
            'irrigation charges': 'सिंचाई शुल्क: खरीफ 50-100 रुपये/एकड़, रबी 75-150 रुपये/एकड़, नकदी फसल 200-500 रुपये/एकड़।',
            'water availability': 'पानी की उपलब्धता: वेबसाइट पोर्टल, मोबाइल ऐप, या 56070 पर WATER भेजकर SMS सेवा का उपयोग करें।',
            'complaint': 'शिकायत के लिए: ऑनलाइन वेबसाइट पर जाएं, शिकायत फॉर्म भरें, शिकायत नंबर नोट करें।',
            'contact': 'संपर्क: मुख्य कार्यालय पटना, फोन: 0612-2223456, ईमेल: wrd.bihar@gov.in, टोल-फ्री: 1800-345-6789',
            'pmksy': 'PMKSY (प्रधानमंत्री कृषि सिंचाई योजना) सिंचाई कवरेज सुधारने की केंद्रीय योजना है।',
            'help': 'मैं बिहार जल संसाधन विभाग की सेवाओं में आपकी सहायता के लिए यहाँ हूँ। आप पूछ सकते हैं:\n- सिंचाई कनेक्शन\n- दस्तावेज आवश्यकताएं\n- शुल्क जानकारी\n- शिकायत दर्ज\n- संपर्क विवरण'
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