import os
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RBCExplorer:
    def __init__(self, output_folder="./rbc_documents", delay=2):
        self.output_folder = output_folder
        self.delay = delay  # Seconds between requests
        self.visited_urls = set()
        self.document_urls = set()
        self.queue = []
        self.domains = ["rbc.com", "rbcroyalbank.com", "rbcfinancialplanning.com"]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Create output folder
        os.makedirs(output_folder, exist_ok=True)
    
    def is_valid_url(self, url):
        """Check if URL is valid and belongs to RBC domain"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and any(domain in parsed.netloc for domain in self.domains)
        except:
            return False
    
    def is_relevant_page(self, url, soup):
        """Check if a page is likely to contain relevant information"""
        # Keywords that suggest the page might contain useful documents
        relevant_keywords = [
            'pdf', 'document', 'download', 'form', 'application', 
            'terms', 'conditions', 'policy', 'agreement', 'disclosure',
            'mortgage', 'loan', 'credit', 'card', 'banking', 'investment',
            'report', 'statement', 'brochure', 'guide', 'product'
        ]
        
        # Check URL for relevance
        url_lower = url.lower()
        if any(keyword in url_lower for keyword in relevant_keywords):
            return True
        
        # Check page title
        title = soup.title.string.lower() if soup.title else ""
        if any(keyword in title for keyword in relevant_keywords):
            return True
        
        # Check for download links or sections
        download_indicators = soup.find_all(['a', 'button', 'div'], 
                                          string=re.compile(r'download|pdf|document', re.I))
        if download_indicators:
            return True
        
        return False
    
    def download_document(self, url):
        """Download a document file (PDF, DOCX, etc.)"""
        if url in self.document_urls:
            return
        
        try:
            # Create a filename from the URL
            filename = url.split('/')[-1]
            
            # Check file extension
            valid_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.txt']
            has_valid_ext = any(filename.lower().endswith(ext) for ext in valid_extensions)
            
            if not has_valid_ext:
                # If no valid extension, try to determine from content type
                response_head = requests.head(url, headers=self.headers)
                content_type = response_head.headers.get('Content-Type', '')
                
                if 'application/pdf' in content_type:
                    filename = f"{filename.replace('.', '_')}.pdf"
                elif 'application/msword' in content_type or 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
                    filename = f"{filename.replace('.', '_')}.docx"
                elif 'application/vnd.ms-excel' in content_type or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type:
                    filename = f"{filename.replace('.', '_')}.xlsx"
                else:
                    # Skip if we can't determine the file type
                    print(f"Skipping unknown file type: {url}")
                    return
            
            filepath = os.path.join(self.output_folder, filename)
            
            # Download the file
            response = requests.get(url, headers=self.headers, stream=True, timeout=10)
            response.raise_for_status()
            
            # Save the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.document_urls.add(url)
            print(f"Downloaded document: {filename}")
            
        except Exception as e:
            print(f"Error downloading {url}: {e}")
    
    def explore_page(self, url):
        """Explore a page for links and documents"""
        if url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        print(f"Exploring: {url}")
        
        try:
            # Respect the website by waiting between requests
            time.sleep(self.delay)
            
            # Get the page content
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if page is relevant
            is_relevant = self.is_relevant_page(url, soup)
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                full_url = urljoin(url, href)
                
                # Check if it's a document
                if any(href.lower().endswith(ext) for ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt']):
                    self.download_document(full_url)
                
                # Check if it's a valid RBC URL to explore
                elif self.is_valid_url(full_url) and full_url not in self.visited_urls:
                    # Only add to queue if the current page is relevant or we're still at a shallow depth
                    if is_relevant or len(self.visited_urls) < 15:  # Explore broadly at first
                        self.queue.append(full_url)
        
        except Exception as e:
            print(f"Error exploring {url}: {e}")
    
    def run(self, starting_urls, max_pages=100):
        """Run the explorer starting from given URLs"""
        # Initialize queue with starting URLs
        self.queue = starting_urls.copy()
        
        # Process queue until empty or max_pages reached
        page_count = 0
        while self.queue and page_count < max_pages:
            current_url = self.queue.pop(0)
            self.explore_page(current_url)
            page_count += 1
            
            print(f"Progress: {page_count}/{max_pages} pages explored, {len(self.document_urls)} documents found")
        
        print(f"Exploration complete. Downloaded {len(self.document_urls)} documents.")
        return len(self.document_urls)

def main():
    # Starting points - these are general entry points to RBC's website
    starting_urls = [
        "https://www.rbc.com/",
        "https://www.rbcroyalbank.com/personal.html",
        "https://www.rbc.com/investor-relations/",
        "https://www.rbcroyalbank.com/business/index.html",
        "https://www.rbc.com/about-rbc.html",
        "https://www.rbcroyalbank.com/mortgages/",
        "https://www.rbcroyalbank.com/credit-cards/",
        "https://www.rbcroyalbank.com/investments/",
        "https://www.rbcroyalbank.com/banking-services/"
    ]
    
    # Create and run the explorer
    explorer = RBCExplorer()
    num_docs = explorer.run(starting_urls, max_pages=50)  # Limit to 50 pages for initial run
    
    if num_docs > 0:
        print(f"\nSuccess! {num_docs} documents have been downloaded to the 'rbc_documents' folder.")
        print("You can now run your RAG chatbot with these documents.")
    else:
        print("\nNo documents were found. You might need to adjust the starting URLs or increase the max_pages limit.")

if __name__ == "__main__":
    main()
