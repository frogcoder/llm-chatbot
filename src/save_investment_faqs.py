import os
import requests
from bs4 import BeautifulSoup
import re

def save_webpage_as_text(url, output_path):
    """Download a webpage and save its content as a text file"""
    try:
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the text content
        text_content = soup.get_text()
        
        # Clean up the text (remove excessive newlines, etc.)
        text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
        text_content = text_content.strip()
        
        # Add source information at the top
        text_content = f"Source: {url}\n\n" + text_content
        
        # Save to a text file
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(text_content)
        
        print(f"Webpage content saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error saving webpage {url}: {e}")
        return False

if __name__ == "__main__":
    # URL of the RBC Investment FAQs
    url = "https://www.rbcroyalbank.com/investments/investment-faqs.html"
    
    from chatbot.config import DOCS_DIRECTORY
    import os
    
    # Output file path
    output_path = os.path.join(DOCS_DIRECTORY, "rbc_investment_faqs.txt")
    
    # Download and save the webpage
    success = save_webpage_as_text(url, output_path)
    
    if success:
        print("RBC Investment FAQs have been successfully saved.")
    else:
        print("Failed to save RBC Investment FAQs.")
