"""
File Search Plugin for JARVIS
Search for files by name across the system.
"""
import os
import re


def register(jarvis):
    """Register the file search plugin with JARVIS."""
    
    def file_search_handler(query, speak, log, **kwargs):
        """Handle file search commands."""
        # Extract filename from query
        pattern = re.search(r'(?:find|search|file named|file called)\s+(\S+)', query)
        if not pattern:
            speak("Please specify the file name to search for.")
            return
        
        filename = pattern.group(1)
        
        # Search from user's home directory
        base_dir = os.path.expanduser('~')
        speak(f"Searching for {filename}, please wait...")
        
        matches = []
        try:
            for root, dirs, files in os.walk(base_dir):
                # Skip hidden directories and common system dirs
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                          ['AppData', 'node_modules', '__pycache__', '.git']]
                
                for f in files:
                    if filename.lower() in f.lower():
                        matches.append(os.path.join(root, f))
                        if len(matches) >= 10:  # Limit results
                            break
                
                if len(matches) >= 10:
                    break
        except PermissionError:
            pass
        except Exception as e:
            log(f"Search error: {e}")
            speak("An error occurred while searching.")
            return
        
        if matches:
            speak(f"Found {len(matches)} file(s).")
            log("File matches:\n" + "\n".join(matches[:10]))
        else:
            speak(f"No files matching '{filename}' found.")
    
    jarvis['add_command'](
        trigger_words=['find file', 'search file', 'file named', 'file called', 'search for'],
        handler=file_search_handler,
        description='Search for files by name on your system.'
    )
