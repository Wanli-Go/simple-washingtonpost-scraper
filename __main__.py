import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pyperclip

# Modify Proxy as needed
proxy_url = 'http://127.0.0.1:33210'

def convert_to_markdown(header, img, metered_content):
    """Convert HTML elements to Markdown format"""
    markdown = []

    for elem in header.find_all(True):
        if elem.name == 'h1':
            markdown.append(f"# {elem.get_text().strip()}")
        elif elem.name == 'p':
            markdown.append(f"#### **{elem.get_text().strip()}**")
    
    for elem in img:
        markdown.append(f"![{elem.get('alt', '')}]({elem.get('srcset', '').split(',')[-1].split(' ')[0]})") # Get the highest resolution
    
    for elem in metered_content.find_all(True):
        # Skip unnecessary elements
        if 'ad-slot-component' in elem.get('class', []):
            continue
            
        # Handle paragraphs
        if elem.name == 'p':
            text = elem.get_text().strip()
            if text:
                # Handle links within paragraphs
                links = elem.find_all('a')
                for link in links:
                    link_text = link.get_text()
                    link_url = urljoin(base_url, link.get('href', ''))
                    text = text.replace(link_text, f"[{link_text}]({link_url})")
                
                is_enclosing = False;
                added_count = 0;
                for idx, char in enumerate(text[:]):
                    if char == '“' or char == "”" or char == '"':
                        if not is_enclosing:
                            text = text[:idx+added_count] + '"*' + text[idx+added_count+1:]
                        else:
                            text = text[:idx+added_count] + '*"' + text[idx+added_count+1:]
                        added_count += 1
                        is_enclosing = not is_enclosing
                        
                markdown.append(f"\n{text}\n")
        
        # Handle headings
        elif elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(elem.name[1])
            markdown.append(f"\n{'#' * level} {elem.get_text().strip()}\n")
        
        # Handle images
        elif elem.name == 'img':
            src = elem.get('src', '')
            alt = elem.get('alt', '')
            if src:
                markdown.append(f"\n![{alt}]({src})\n")
                
    return '\n'.join(markdown)

def get_article_content(url):
    global base_url
    base_url = url

    mock_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "referer": "https://www.google.com/",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
    }
    
    try:
        print('before request')
        response = requests.get(url, headers=mock_headers, proxies={'http': proxy_url, 'https': proxy_url})
        print('after request')
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}"

    soup = BeautifulSoup(response.content, 'html.parser')
    header = soup.find('header')
    header = header or soup.find('div', class_='grid-full-bleed')
    img = soup.find_all('img', {'fetchpriority': 'high'})
    metered_content = soup.find('div', class_='meteredContent')
    
    
    if not metered_content:
        return "No metered content found on the page"
    
    return convert_to_markdown(header, img, metered_content)

if __name__ == "__main__":
    url = input("Enter news article URL: ")
    markdown_content = get_article_content(url)
    print("\n" + "="*50 + " ARTICLE CONTENT " + "="*50)
    print(markdown_content)
    pyperclip.copy(markdown_content)
    print("="*120)
    print("The markdown content has been copied to clipboard. If not, mannually copy the content above to a markdown file to see the content.")