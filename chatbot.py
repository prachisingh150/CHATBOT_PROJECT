import re
import json
import pickle
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
from data_processor import DataProcessor
from language_handler import LanguageHandler
import numpy as np

class GovernmentChatbot:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.language_handler = LanguageHandler()
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.classifier = MultinomialNB()
        
        # Knowledge base
        self.knowledge_base = {}
        self.responses = {}
        self.trained = False
        
        # Load existing data if available
        self.load_existing_model()
        
        # If no existing model, train with default data
        if not self.trained:
            self.load_and_process_data()
    
    def load_existing_model(self):
        """Load pre-trained model if exists"""
        try:
            if os.path.exists('chatbot_model.pkl'):
                with open('chatbot_model.pkl', 'rb') as f:
                    model_data = pickle.load(f)
                    self.vectorizer = model_data['vectorizer']
                    self.classifier = model_data['classifier']
                    self.knowledge_base = model_data['knowledge_base']
                    self.responses = model_data['responses']
                    self.trained = True
                    print("Loaded existing chatbot model")
        except Exception as e:
            print(f"Could not load existing model: {e}")
    
    def save_model(self):
        """Save trained model"""
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'knowledge_base': self.knowledge_base,
            'responses': self.responses
        }
        with open('chatbot_model.pkl', 'wb') as f:
            pickle.dump(model_data, f)
        print("Model saved successfully")
    
    def load_and_process_data(self):
        """Load and process website data"""
        print("Processing website data...")
        
        # Get processed data from website
        website_data = self.data_processor.extract_website_data()
        
        # Comprehensive WRD Bihar Knowledge Base - English
        wrd_knowledge_english = [
            {
                'question': 'What is Water Resources Department Bihar?',
                'answer': 'Water Resources Department (WRD) is a key establishment of Government of Bihar, formerly known as Irrigation Department. It handles major and medium irrigation projects, inter-state river water sharing, and irrigation potential creation.',
                'category': 'about',
                'language': 'en',
                'keywords': 'water resources department, WRD, irrigation, bihar government, about'
            },
            {
                'question': 'What are the main functions of WRD Bihar?',
                'answer': 'Main functions include: 1) Construction and maintenance of major irrigation projects, 2) Inter-state river water sharing, 3) Flood control and drainage, 4) Irrigation potential creation and utilization, 5) Water resource management and planning.',
                'category': 'functions',
                'language': 'en',
                'keywords': 'functions, irrigation projects, flood control, water management, inter-state rivers'
            },
            {
                'question': 'How to apply for irrigation connection?',
                'answer': 'To apply for irrigation connection: 1) Visit your nearest WRD office, 2) Fill application form with required documents, 3) Submit fees as per government rates, 4) Application will be processed within 30 days, 5) You will receive connection details via SMS/email.',
                'category': 'services',
                'language': 'en',
                'keywords': 'irrigation connection, application, apply, documents, fees, process'
            },
            {
                'question': 'What documents are required for irrigation connection?',
                'answer': 'Required documents: 1) Land ownership documents, 2) Aadhaar card, 3) Voter ID, 4) Agriculture land records, 5) Bank account details, 6) Passport size photographs, 7) Caste certificate (if applicable).',
                'category': 'documents',
                'language': 'en',
                'keywords': 'documents required, land records, aadhaar, voter id, agriculture, bank account'
            },
            {
                'question': 'What are the irrigation charges?',
                'answer': 'Irrigation charges vary by crop type and season: Kharif crops: Rs. 50-100 per acre, Rabi crops: Rs. 75-150 per acre, Cash crops: Rs. 200-500 per acre. Additional charges may apply for maintenance and development.',
                'category': 'charges',
                'language': 'en',
                'keywords': 'irrigation charges, fees, kharif, rabi, cash crops, rates, per acre'
            },
            {
                'question': 'How to check irrigation water availability?',
                'answer': 'Check water availability through: 1) Official website portal, 2) Mobile app, 3) SMS service by sending WATER to 56070, 4) Contact local irrigation office, 5) Visit nearest canal division office.',
                'category': 'services',
                'language': 'en',
                'keywords': 'water availability, check, portal, mobile app, SMS, canal division'
            },
            {
                'question': 'What to do in case of drainage problems?',
                'answer': 'For drainage problems: 1) Register complaint online or at office, 2) Provide location details and problem description, 3) Complaint will be assigned to field engineer, 4) Resolution within 7-15 days, 5) Follow up through complaint number.',
                'category': 'complaints',
                'language': 'en',
                'keywords': 'drainage problems, complaint, register, field engineer, resolution, follow up'
            },
            {
                'question': 'Contact information for WRD Bihar?',
                'answer': 'Contact Details: Main Office: Patna, Phone: 0612-2223456, Email: wrd.bihar@gov.in, Website: fmiscwrdbihar.gov.in, Toll-free: 1800-345-6789, Office Hours: 10 AM to 5 PM (Mon-Fri)',
                'category': 'contact',
                'language': 'en',
                'keywords': 'contact information, phone, email, website, office hours, toll-free'
            },
            {
                'question': 'How to register complaint online?',
                'answer': 'To register complaint online: 1) Visit official website, 2) Go to complaint section, 3) Fill complaint form with details, 4) Upload supporting documents if any, 5) Submit and note complaint number, 6) Track status using complaint number.',
                'category': 'complaints',
                'language': 'en',
                'keywords': 'online complaint, register, website, complaint number, track status'
            },
            {
                'question': 'What is PMKSY scheme?',
                'answer': 'PMKSY (Pradhan Mantri Krishi Sinchayee Yojana) is a Central Government scheme for improving irrigation coverage. It focuses on micro-irrigation, watershed development, and per drop more crop strategy. Apply through designated officers.',
                'category': 'schemes',
                'language': 'en',
                'keywords': 'PMKSY, Pradhan Mantri Krishi Sinchayee Yojana, micro irrigation, watershed, central scheme'
            }
        ]
        
        # Comprehensive WRD Bihar Knowledge Base - Hindi
        wrd_knowledge_hindi = [
            {
                'question': 'बिहार जल संसाधन विभाग क्या है?',
                'answer': 'जल संसाधन विभाग (WRD) बिहार सरकार का एक मुख्य विभाग है, जो पहले सिंचाई विभाग के नाम से जाना जाता था। यह प्रमुख और मध्यम सिंचाई परियोजनाओं, अंतर्राज्यीय नदी जल साझाकरण और सिंचाई क्षमता निर्माण का काम करता है।',
                'category': 'about',
                'language': 'hi',
                'keywords': 'जल संसाधन विभाग, सिंचाई, बिहार सरकार, के बारे में'
            },
            {
                'question': 'सिंचाई कनेक्शन के लिए कैसे आवेदन करें?',
                'answer': 'सिंचाई कनेक्शन के लिए आवेदन: 1) नजदीकी WRD कार्यालय जाएं, 2) आवश्यक दस्तावेजों के साथ आवेदन फॉर्म भरें, 3) सरकारी दरों के अनुसार फीस जमा करें, 4) 30 दिनों में आवेदन प्रक्रिया होगी, 5) SMS/ईमेल के माध्यम से कनेक्शन विवरण मिलेगा।',
                'category': 'services',
                'language': 'hi',
                'keywords': 'सिंचाई कनेक्शन, आवेदन, दस्तावेज, फीस, प्रक्रिया'
            },
            {
                'question': 'सिंचाई कनेक्शन के लिए कौन से दस्तावेज चाहिए?',
                'answer': 'आवश्यक दस्तावेज: 1) भूमि स्वामित्व दस्तावेज, 2) आधार कार्ड, 3) मतदाता पहचान पत्र, 4) कृषि भूमि रिकॉर्ड, 5) बैंक खाता विवरण, 6) पासपोर्ट साइज फोटो, 7) जाति प्रमाण पत्र (यदि लागू हो)।',
                'category': 'documents',
                'language': 'hi',
                'keywords': 'दस्तावेज, भूमि रिकॉर्ड, आधार, मतदाता पहचान पत्र, कृषि, बैंक खाता'
            },
            {
                'question': 'सिंचाई शुल्क क्या है?',
                'answer': 'सिंचाई शुल्क फसल के प्रकार और मौसम के अनुसार: खरीफ फसल: 50-100 रुपये प्रति एकड़, रबी फसल: 75-150 रुपये प्रति एकड़, नकदी फसल: 200-500 रुपये प्रति एकड़। रखरखाव और विकास के लिए अतिरिक्त शुल्क हो सकता है।',
                'category': 'charges',
                'language': 'hi',
                'keywords': 'सिंचाई शुल्क, फीस, खरीफ, रबी, नकदी फसल, दरें, प्रति एकड़'
            },
            {
                'question': 'सिंचाई पानी की उपलब्धता कैसे चेक करें?',
                'answer': 'पानी की उपलब्धता चेक करने के तरीके: 1) आधिकारिक वेबसाइट पोर्टल, 2) मोबाइल ऐप, 3) 56070 पर WATER भेजकर SMS सेवा, 4) स्थानीय सिंचाई कार्यालय से संपर्क, 5) नजदीकी नहर डिवीजन कार्यालय जाएं।',
                'category': 'services',
                'language': 'hi',
                'keywords': 'पानी उपलब्धता, चेक, पोर्टल, मोबाइल ऐप, SMS, नहर डिवीजन'
            },
            {
                'question': 'ऑनलाइन शिकायत कैसे दर्ज करें?',
                'answer': 'ऑनलाइन शिकायत दर्ज करने के लिए: 1) आधिकारिक वेबसाइट पर जाएं, 2) शिकायत सेक्शन में जाएं, 3) विवरण के साथ शिकायत फॉर्म भरें, 4) यदि कोई सहायक दस्तावेज हो तो अपलोड करें, 5) सबमिट करें और शिकायत नंबर नोट करें, 6) शिकायत नंबर से स्थिति ट्रैक करें।',
                'category': 'complaints',
                'language': 'hi',
                'keywords': 'ऑनलाइन शिकायत, दर्ज, वेबसाइट, शिकायत नंबर, ट्रैक स्थिति'
            },
            {
                'question': 'संपर्क जानकारी WRD बिहार?',
                'answer': 'संपर्क विवरण: मुख्य कार्यालय: पटना, फोन: 0612-2223456, ईमेल: wrd.bihar@gov.in, वेबसाइट: fmiscwrdbihar.gov.in, टोल-फ्री: 1800-345-6789, कार्यालय समय: 10 AM से 5 PM (सोम-शुक्र)',
                'category': 'contact',
                'language': 'hi',
                'keywords': 'संपर्क जानकारी, फोन, ईमेल, वेबसाइट, कार्यालय समय, टोल-फ्री'
            },
            {
                'question': 'PMKSY योजना क्या है?',
                'answer': 'PMKSY (प्रधानमंत्री कृषि सिंचाई योजना) सिंचाई कवरेज सुधारने के लिए केंद्र सरकार की योजना है। यह सूक्ष्म सिंचाई, वाटरशेड विकास, और प्रति बूंद अधिक फसल रणनीति पर केंद्रित है। नामित अधिकारियों के माध्यम से आवेदन करें।',
                'category': 'schemes',
                'language': 'hi',
                'keywords': 'PMKSY, प्रधानमंत्री कृषि सिंचाई योजना, सूक्ष्म सिंचाई, वाटरशेड, केंद्रीय योजना'
            }
        ]
        
        # Combine all knowledge data
        all_knowledge = wrd_knowledge_english + wrd_knowledge_hindi
        
        # Organize knowledge base by categories
        self.knowledge_base = {
            'about': {},
            'services': {},
            'functions': {},
            'documents': {},
            'charges': {},
            'complaints': {},
            'contact': {},
            'schemes': {}
        }
        
        # Process all knowledge entries
        questions = []
        answers = []
        categories = []
        
        for entry in all_knowledge:
            # Add original question and answer
            questions.append(entry['question'])
            answers.append(entry['answer'])
            categories.append(entry['category'])
            
            # Store in knowledge base by category
            if entry['category'] not in self.knowledge_base:
                self.knowledge_base[entry['category']] = {}
            
            # Create key from question
            key = entry['question'].lower().replace('?', '').strip()
            self.knowledge_base[entry['category']][key] = entry['answer']
            
            # Generate keyword-based variations
            if entry['keywords']:
                keywords = entry['keywords'].split(',')
                for keyword in keywords:
                    keyword = keyword.strip()
                    if keyword and len(keyword) > 2:
                        # Generate question variations
                        variations = self._generate_question_variations(keyword, entry['category'])
                        for variation in variations:
                            questions.append(variation)
                            answers.append(entry['answer'])
                            categories.append(entry['category'])
        
        # Merge website data if available
        if website_data:
            self.knowledge_base.update(website_data)
        
        if questions:
            # Train the model
            X = self.vectorizer.fit_transform(questions)
            self.classifier.fit(X, categories)
            
            # Store responses
            for i, answer in enumerate(answers):
                self.responses[questions[i]] = answer
            
            self.trained = True
            self.save_model()
            print(f"Chatbot trained with {len(questions)} question-answer pairs")
        else:
            print("No training data available")
    
    def _generate_question_variations(self, keyword, category):
        """Generate question variations for better matching"""
        variations = [
            keyword,
            f"what is {keyword}",
            f"how to get {keyword}",
            f"information about {keyword}",
            f"tell me about {keyword}",
            f"help with {keyword}",
            f"{keyword} procedure",
            f"{keyword} process",
            f"apply for {keyword}",
            f"{keyword} application"
        ]
        
        if category == "services":
            variations.extend([
                f"how to apply for {keyword}",
                f"{keyword} online",
                f"{keyword} documents required",
                f"{keyword} fees"
            ])
        
        return variations
    
    def get_response(self, message, language='english'):
        """Get chatbot response"""
        try:
            # Preprocess message
            processed_message = self._preprocess_message(message, language)
            
            if not self.trained or not processed_message:
                return self._get_default_response(language)
            
            # Find best matching response
            response = self._find_best_response(processed_message)
            
            # Handle language conversion
            if language == 'hindi':
                response = self.language_handler.translate_to_hindi(response)
            
            return response
            
        except Exception as e:
            print(f"Error getting response: {e}")
            return self._get_error_response(language)
    
    def _preprocess_message(self, message, language):
        """Preprocess user message"""
        if language == 'hindi':
            message = self.language_handler.translate_to_english(message)
        
        # Clean and normalize
        message = message.lower().strip()
        message = re.sub(r'[^\w\s]', ' ', message)
        message = re.sub(r'\s+', ' ', message)
        
        return message
    
    def _find_best_response(self, message):
        """Find best matching response"""
        try:
            # Vectorize the message
            message_vector = self.vectorizer.transform([message])
            
            # Predict category
            predicted_category = self.classifier.predict(message_vector)[0]
            
            # Find most similar question in the category
            max_similarity = 0
            best_response = ""
            
            for question, answer in self.responses.items():
                question_vector = self.vectorizer.transform([question])
                similarity = cosine_similarity(message_vector, question_vector)[0][0]
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_response = answer
            
            # If similarity is too low, provide category-based response
            if max_similarity < 0.1:
                return self._get_category_response(predicted_category)
            
            return best_response
            
        except Exception as e:
            print(f"Error finding response: {e}")
            return self._get_general_help_response()
    
    def _get_category_response(self, category):
        """Get general response based on category"""
        category_responses = {
            "about": "I can provide information about the Water Resources Department (WRD) Bihar, its history, and organizational structure. What specific information would you like to know?",
            "services": "I can help you with WRD Bihar services including irrigation connections, water availability checks, and online applications. Please specify which service you need help with.",
            "functions": "The main functions of WRD Bihar include irrigation project management, flood control, drainage, and water resource planning. What specific function would you like to know about?",
            "documents": "I can guide you about required documents for various WRD services including land records, Aadhaar card, voter ID, and agriculture documents. Which service documents do you need information about?",
            "charges": "I can provide information about irrigation charges for different crops (Kharif, Rabi, Cash crops) and seasons. What specific charge information do you need?",
            "complaints": "I can help you with the complaint process including online registration, tracking, and resolution. What type of complaint assistance do you need?",
            "contact": "I can provide contact information for WRD Bihar offices including phone numbers, email, and office hours. What contact information do you need?",
            "schemes": "I can provide information about government schemes like PMKSY and other water resource related schemes. Which scheme would you like to know about?"
        }
        return category_responses.get(category, self._get_general_help_response()).get(category, self._get_general_help_response())
    
    def _get_general_help_response(self):
        return "I'm here to help you with Bihar Water Resources Department (WRD) services and information. You can ask me about:\n- Irrigation connections and applications\n- Required documents and procedures\n- Irrigation charges and fees\n- Water availability status\n- Online complaint registration\n- Contact information\n- Government schemes like PMKSY\n\nPlease let me know what specific information you need."
    
    def _get_default_response(self, language):
        if language == 'hindi':
            return "नमस्ते! मैं बिहार जल संसाधन विभाग (WRD) की सहायता के लिए यहाँ हूँ। मैं सिंचाई सेवाओं, दस्तावेज आवश्यकताओं, शुल्क जानकारी, और शिकायत प्रक्रिया में आपकी सहायता कर सकता हूँ। कृपया बताएं कि आपको किस जानकारी की आवश्यकता है?"
        return "Hello! I'm here to help you with Bihar Water Resources Department (WRD) services. I can assist you with irrigation connections, document requirements, charges information, and complaint procedures. How can I help you today?"
    
    def _get_error_response(self, language):
        if language == 'hindi':
            return "क्षमा करें, मुझे आपके प्रश्न को समझने में कुछ कठिनाई हो रही है। कृपया दूसरे तरीके से पूछें।"
        return "I'm sorry, I'm having trouble understanding your question. Please try asking in a different way."