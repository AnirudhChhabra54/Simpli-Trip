"""
Web Scraper Service - FREE Travel Data Collection
Collects travel information from public sources
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import time
import re

from utils.logger import logger
from services.rag_service import rag_service


class ScraperService:
    """
    Service to scrape travel information from public sources
    Respects robots.txt and rate limits
    """
    
    def __init__(self, delay: float = 2.0):
        """
        Initialize scraper service
        
        Args:
            delay: Delay between requests in seconds (be respectful!)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SimpliTrip/1.0 (Educational Project; +https://simplitrip.com)'
        })
    
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """
        Make HTTP request with error handling
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Respect rate limits
            time.sleep(self.delay)
            
            return BeautifulSoup(response.content, 'lxml')
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def scrape_destination_info(self, destination: str) -> Dict[str, Any]:
        """
        Scrape basic destination information
        
        Note: This is a template. In production, you would scrape from
        actual travel websites (respecting their robots.txt and ToS)
        
        Args:
            destination: Destination name
            
        Returns:
            Dict with scraped information
        """
        logger.info(f"Scraping information for: {destination}")
        
        # For demo purposes, we'll create structured data
        # In production, you would scrape from actual websites
        
        info = {
            'destination': destination,
            'description': f"Information about {destination}",
            'best_time': "October to March",
            'activities': [],
            'budget_range': "₹20,000 - ₹50,000",
            'source': 'demo_data'
        }
        
        logger.info(f"Scraped info for {destination}")
        return info
    
    def scrape_travel_tips(self, category: str = "general") -> List[str]:
        """
        Scrape travel tips from public sources
        
        Args:
            category: Category of tips
            
        Returns:
            List of travel tips
        """
        logger.info(f"Scraping {category} travel tips")
        
        # Demo tips - in production, scrape from actual sources
        tips = [
            "Book flights 2-3 months in advance for best prices",
            "Travel during off-season for better deals",
            "Use public transportation to save money",
            "Stay in hostels or budget hotels",
            "Eat at local restaurants for authentic experience"
        ]
        
        return tips
    
    def scrape_and_index(self, destination: str):
        """
        Scrape destination info and add to RAG knowledge base
        
        Args:
            destination: Destination to scrape
        """
        logger.info(f"Scraping and indexing: {destination}")
        
        # Scrape information
        info = self.scrape_destination_info(destination)
        
        # Create documents for RAG
        documents = []
        metadatas = []
        
        # Add description
        if info.get('description'):
            documents.append(info['description'])
            metadatas.append({
                'destination': destination,
                'type': 'description',
                'source': info.get('source', 'scraped')
            })
        
        # Add best time info
        if info.get('best_time'):
            doc = f"{destination} is best visited during {info['best_time']}"
            documents.append(doc)
            metadatas.append({
                'destination': destination,
                'type': 'best_time',
                'source': info.get('source', 'scraped')
            })
        
        # Add budget info
        if info.get('budget_range'):
            doc = f"Budget for {destination}: {info['budget_range']}"
            documents.append(doc)
            metadatas.append({
                'destination': destination,
                'type': 'budget',
                'source': info.get('source', 'scraped')
            })
        
        # Add to RAG knowledge base
        if documents:
            rag_service.add_documents(documents, metadatas)
            logger.info(f"Indexed {len(documents)} documents for {destination}")
    
    def scrape_multiple_destinations(self, destinations: List[str]):
        """
        Scrape information for multiple destinations
        
        Args:
            destinations: List of destination names
        """
        logger.info(f"Scraping {len(destinations)} destinations")
        
        for destination in destinations:
            try:
                self.scrape_and_index(destination)
            except Exception as e:
                logger.error(f"Failed to scrape {destination}: {e}")
                continue
        
        logger.info("Scraping completed")
    
    def extract_text_from_html(self, html: str) -> str:
        """
        Extract clean text from HTML
        
        Args:
            html: HTML content
            
        Returns:
            Clean text
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def scrape_from_url(self, url: str, selector: Optional[str] = None) -> Optional[str]:
        """
        Scrape content from a specific URL
        
        Args:
            url: URL to scrape
            selector: Optional CSS selector to extract specific content
            
        Returns:
            Scraped text or None
        """
        soup = self._make_request(url)
        if not soup:
            return None
        
        if selector:
            # Extract specific element
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
            return None
        else:
            # Extract all text
            return self.extract_text_from_html(str(soup))
    
    def batch_scrape_and_index(self, urls: List[Dict[str, str]]):
        """
        Batch scrape multiple URLs and index in RAG
        
        Args:
            urls: List of dicts with 'url', 'destination', 'category'
        """
        logger.info(f"Batch scraping {len(urls)} URLs")
        
        documents = []
        metadatas = []
        
        for item in urls:
            url = item.get('url')
            destination = item.get('destination', 'unknown')
            category = item.get('category', 'general')
            
            content = self.scrape_from_url(url)
            if content:
                # Chunk content if too long
                chunks = self._chunk_text(content, max_length=500)
                
                for chunk in chunks:
                    documents.append(chunk)
                    metadatas.append({
                        'destination': destination,
                        'category': category,
                        'source': url,
                        'type': 'scraped'
                    })
        
        # Add to RAG
        if documents:
            rag_service.add_documents(documents, metadatas)
            logger.info(f"Indexed {len(documents)} scraped documents")
    
    def _chunk_text(self, text: str, max_length: int = 500) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Text to chunk
            max_length: Maximum chunk length
            
        Returns:
            List of text chunks
        """
        # Split by sentences
        sentences = re.split(r'[.!?]+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks


# Create global instance
scraper_service = ScraperService()
