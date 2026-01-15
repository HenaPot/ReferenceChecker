# File: backend/app/services/scraper_service.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import Optional, Dict


class WebScraperService:
    """Service for scraping metadata from web pages using Playwright."""
    
    def __init__(self):
        self.timeout = 10000  # 10 seconds
    
    def scrape_metadata(self, url: str) -> Dict[str, Optional[str]]:
        """
        Scrape title, author, and publication date from a URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with title, author, publication_date
        """
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Navigate to URL
                page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')
                
                # Get page content
                content = page.content()
                browser.close()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract metadata
                metadata = {
                    'title': self._extract_title(soup, url),
                    'author': self._extract_author(soup, url),
                    'publication_date': self._extract_date(soup)
                }
                
                return metadata
                
        except PlaywrightTimeout:
            print(f"Timeout scraping {url}")
            return self._fallback_metadata(url)
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._fallback_metadata(url)
    
    def _extract_title(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extract title from page."""
        # Try ScienceDirect specific selector FIRST
        if 'sciencedirect.com' in url:
            title_span = soup.find('span', class_='title-text')
            if title_span:
                return title_span.get_text().strip()
        
        # Try Open Graph tag
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try Twitter card
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return twitter_title['content'].strip()
        
        # Try standard title tag
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string.strip()
            # Clean up common suffixes
            title = re.sub(r'\s*[\|\-]\s*(Nature|arXiv|Science|PLOS|ScienceDirect|.*)\s*$', '', title)
            return title
        
        # Try h1 as fallback
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extract author from page."""
        # Try ScienceDirect specific selector FIRST
        if 'sciencedirect.com' in url:
            authors = []
            
            # Find the AuthorGroups div
            author_groups = soup.find('div', class_='AuthorGroups')
            if author_groups:
                # Find all author buttons
                author_buttons = author_groups.find_all('button', class_='button-link')
                
                for button in author_buttons:
                    # Extract given name and surname
                    given_name = button.find('span', class_='given-name')
                    surname = button.find('span', class_='surname')
                    
                    if given_name and surname:
                        full_name = f"{given_name.get_text().strip()} {surname.get_text().strip()}"
                        authors.append(full_name)
                
                # Return comma-separated list of authors
                if authors:
                    # Return first 3 authors + "et al." if more than 3
                    if len(authors) > 3:
                        return ', '.join(authors[:3]) + ' et al.'
                    else:
                        return ', '.join(authors)
        
        # Try meta author tag
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author and meta_author.get('content'):
            return meta_author['content'].strip()
        
        # Try DC.creator (Dublin Core)
        dc_creator = soup.find('meta', attrs={'name': 'DC.creator'})
        if dc_creator and dc_creator.get('content'):
            return dc_creator['content'].strip()
        
        # Try citation_author (common in academic papers)
        citation_author = soup.find('meta', attrs={'name': 'citation_author'})
        if citation_author and citation_author.get('content'):
            return citation_author['content'].strip()
        
        # Try data-test attribute (Nature, Science journals)
        author_data_test = soup.find('a', attrs={'data-test': 'author-name'})
        if author_data_test:
            return author_data_test.get_text().strip()
        
        # Try common class names
        author_classes = ['author', 'byline', 'article-author', 'post-author', 'author-name']
        for class_name in author_classes:
            author_elem = soup.find(class_=class_name)
            if author_elem:
                author_text = author_elem.get_text().strip()
                # Clean common prefixes
                author_text = re.sub(r'^(By|Written by|Author:)\s*', '', author_text, flags=re.IGNORECASE)
                if author_text and len(author_text) < 100:  # Sanity check
                    return author_text
        
        return None
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date from page."""
        # Try meta tags first
        date_meta_names = [
            'article:published_time',
            'citation_publication_date',
            'DC.date',
            'date',
            'publish_date',
            'publication_date'
        ]
        
        for meta_name in date_meta_names:
            # Try property attribute
            date_tag = soup.find('meta', property=meta_name)
            if date_tag and date_tag.get('content'):
                date_str = date_tag['content']
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    return parsed_date
            
            # Try name attribute
            date_tag = soup.find('meta', attrs={'name': meta_name})
            if date_tag and date_tag.get('content'):
                date_str = date_tag['content']
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    return parsed_date
        
        # Try time tag
        time_tag = soup.find('time')
        if time_tag:
            # Try datetime attribute
            if time_tag.get('datetime'):
                parsed_date = self._parse_date(time_tag['datetime'])
                if parsed_date:
                    return parsed_date
            # Try text content
            if time_tag.string:
                parsed_date = self._parse_date(time_tag.string)
                if parsed_date:
                    return parsed_date
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse date string into YYYY-MM-DD format.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Date in YYYY-MM-DD format or None
        """
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # List of date formats to try
        formats = [
            '%Y-%m-%d',           # 2024-01-15
            '%Y-%m-%dT%H:%M:%S',  # 2024-01-15T10:30:00
            '%Y-%m-%dT%H:%M:%SZ', # 2024-01-15T10:30:00Z
            '%Y/%m/%d',           # 2024/01/15
            '%d %B %Y',           # 15 January 2024
            '%B %d, %Y',          # January 15, 2024
            '%d %b %Y',           # 15 Jan 2024
            '%b %d, %Y',          # Jan 15, 2024
            '%Y',                 # 2024 (year only)
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Try ISO format parsing
        try:
            # Handle ISO format with timezone
            if 'T' in date_str:
                date_part = date_str.split('T')[0]
                datetime.strptime(date_part, '%Y-%m-%d')
                return date_part
        except ValueError:
            pass
        
        return None
    
    def _fallback_metadata(self, url: str) -> Dict[str, Optional[str]]:
        """Return empty metadata when scraping fails."""
        return {
            'title': None,
            'author': None,
            'publication_date': None
        }