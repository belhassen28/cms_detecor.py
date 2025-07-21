import subprocess
import re
from typing import Dict, Optional

def clean_whatweb_output(output: str) -> str:
    """Remove ANSI escape sequences from whatweb output."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', output)

def extract_cms_info(cleaned_output: str) -> Dict[str, str]:
    """
    Extract CMS information from whatweb output.
    Returns a dictionary with 'name' and optionally 'version'.
    """
    # Ordered by popularity to match most common CMS first
    cms_patterns = [
        ('WordPress', r'WordPress\[(.*?)\]'),
        ('Drupal', r'Drupal\[(.*?)\]'),
        ('Joomla', r'Joomla\[(.*?)\]'),
        ('Magento', r'Magento\[(.*?)\]'),
        ('Shopify', r'Shopify'),
        ('Squarespace', r'Squarespace'),
        ('Wix', r'Wix'),
    ]

    for name, pattern in cms_patterns:
        match = re.search(pattern, cleaned_output)
        if match:
            version = match.group(1) if match.groups() else None
            return {
                "name": name,
                "version": version if version else "unknown version",
                "full_name": f"{name} {version}" if version else name
            }

    # Check for CMS mentions without version info
    for name, _ in cms_patterns:
        if name in cleaned_output:
            return {
                "name": name,
                "version": "unknown version",
                "full_name": f"{name} (unknown version)"
            }

    # If no known CMS found
    if cleaned_output.strip():
        return {"name": "Other CMS", "full_name": "Other CMS"}
    return {"name": "Unknown", "full_name": "Unknown"}

def detect_cms(url: str, timeout: int = 30) -> Dict[str, str]:
    """
    Detect the CMS used by a website using whatweb.
    
    Args:
        url: The URL to check
        timeout: Timeout in seconds for the whatweb command
        
    Returns:
        Dictionary with CMS information or error details
    """
    try:
        result = subprocess.run(
            ["whatweb", "--color=never", "--user-agent", "Mozilla/5.0", url],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            return {
                "name": "Error",
                "detail": f"whatweb returned {result.returncode}",
                "stderr": result.stderr.strip()
            }
            
        cleaned_output = clean_whatweb_output(result.stdout)
        return extract_cms_info(cleaned_output)
        
    except subprocess.TimeoutExpired:
        return {"name": "Error", "detail": "Timeout from whatweb"}
    except FileNotFoundError:
        return {"name": "Error", "detail": "whatweb command not found"}
    except Exception as e:
        return {"name": "Error", "detail": str(e)}

if __name__ == "__main__":
    # Example usage
    test_url = "https://wordpress.org"
    result = detect_cms(test_url)
    print(f"CMS Detection Result: {result}")
