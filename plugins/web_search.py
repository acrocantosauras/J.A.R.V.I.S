"""
Web Search Plugin for JARVIS
Search the web and read results.
"""
import requests
from bs4 import BeautifulSoup


def register(jarvis):
    """Register web search commands."""

    def web_search_handler(query, speak, log, **kwargs):
        """Search the web for a query and read top results."""
        import re

        # Extract search query
        search_query = query
        for trigger in ['search', 'google', 'look up', 'find online', 'web search']:
            search_query = search_query.replace(trigger, '')
        search_query = search_query.strip()

        if not search_query:
            speak("What would you like me to search for?")
            return

        speak(f"Searching for {search_query}...")
        log(f"Web search: {search_query}")

        try:
            # Use DuckDuckGo HTML for scraping (no API key needed)
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(search_query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            results = []
            for result in soup.find_all('div', class_='result', limit=5):
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    link = title_elem.get('href', '')
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'link': link
                    })

            if results:
                speak(f"Found {len(results)} results for {search_query}.")
                for i, r in enumerate(results[:3], 1):
                    speak(f"Result {i}: {r['title']}")
                    if r['snippet']:
                        log(f"  {r['snippet'][:120]}")
                log(f"\nTop results for '{search_query}':")
                for i, r in enumerate(results, 1):
                    log(f"  {i}. {r['title']}")
                    log(f"     {r['link']}")
            else:
                speak(f"Sorry, I couldn't find results for {search_query}.")

        except requests.RequestException as e:
            log(f"Web search error: {e}")
            speak("Sorry, I couldn't complete the search. Check your internet connection.")
        except Exception as e:
            log(f"Web search error: {e}")
            speak("An error occurred during the search.")

    def open_url_handler(query, speak, log, **kwargs):
        """Open a URL in the browser."""
        import webbrowser
        import re

        url = query
        for trigger in ['open website', 'go to', 'visit', 'open url', 'open site']:
            url = url.replace(trigger, '')
        url = url.strip()

        if not url:
            speak("What website should I open?")
            return

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            webbrowser.open(url)
            speak(f"Opening {url}")
        except Exception as e:
            speak(f"Failed to open {url}")

    jarvis['add_command'](
        trigger_words=['search', 'google', 'look up', 'find online', 'web search'],
        handler=web_search_handler,
        description='Search the web for information.'
    )

    jarvis['add_command'](
        trigger_words=['open website', 'go to', 'visit', 'open url', 'open site'],
        handler=open_url_handler,
        description='Open a website in the browser.'
    )
