import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import os
import re


def get_zed_toc_items():
    """
    Get the list of TOC items from Zed documentation.
    Returns items from "Getting Started" until before "Developing Zed".
    Excludes section titles.
    """
    url = "https://zed.dev/docs"

    # Fetch the page
    response = requests.get(url)
    response.raise_for_status()

    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the navigation/TOC menu using #sidebar
    nav = soup.find(id='sidebar')

    if not nav:
        raise ValueError("Could not find navigation menu")

    # Extract all links from the navigation
    # Only get items with <a> tags under .chapter-item elements within .chapter
    toc_items = []
    seen_urls = set()

    # Find all chapter items
    chapter_items = nav.find_all(class_='chapter-item')

    for item in chapter_items:
        # Only process items that have an <a> tag
        link = item.find('a')
        if not link:
            continue

        text = link.get_text(strip=True)
        href = link.get('href', '')

        # Skip if already seen
        if not text or not href or href in seen_urls:
            continue

        # Construct full URL from relative href
        full_url = f"{url}/{href}"

        seen_urls.add(href)
        toc_items.append({
            'title': text,
            'url': full_url
        })

    return toc_items


def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)


def download_page_as_pdf(url, output_path, custom_css):
    """Download a web page as PDF with custom CSS."""
    if os.path.exists(output_path):
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Navigate to the page
        page.goto(url, wait_until='load')

        # Inject custom CSS
        page.add_style_tag(content=custom_css)

        # Generate PDF
        page.pdf(
            path=output_path,
            format='Letter',
            margin={"top": "0.45in", "right": "0.45in", "bottom": "0.45in", "left": "0.45in"},
            print_background=False,
        )

        browser.close()
        return True


def main():
    # Custom CSS for PDF generation
    custom_css = """
    @media print {
        #sidebar, .header-bar, .toc-container, .footer-buttons {
            display: none;
        }
    }

    body, #body-container {
        height: auto;
        overflow: auto;
    }

    #content {
        font-weight: 500;
        font-family: "SF Pro Text";
    }

    #content, blockquote > p, table {
        font-size: 0.8em;
    }
    """

    # Create output directory
    output_dir = "zed-docs-pdf"
    os.makedirs(output_dir, exist_ok=True)

    print("Fetching Zed documentation TOC items...\n")

    try:
        items = get_zed_toc_items()
        print(f"Found {len(items)} TOC items\n")

        # Download each page as PDF
        for i, item in enumerate(items, 1):
            title = sanitize_filename(item['title'])
            filename = f"{i:03d}. {title}.pdf"
            output_path = os.path.join(output_dir, filename)

            print(f"[{i}/{len(items)}] Downloading: {item['title']}")
            print(f"    URL: {item['url']}")
            print(f"    Saving to: {filename}")

            try:
                downloaded = download_page_as_pdf(item['url'], output_path, custom_css)
                if downloaded:
                    print("    ✓ Success\n")
                else:
                    print("    ↷ Skipped (already exists)\n")
            except Exception as e:
                print(f"    ✗ Error: {e}\n")

        print(f"\nAll PDFs saved to: {output_dir}/")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
