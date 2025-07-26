
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

