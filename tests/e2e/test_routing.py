from playwright.sync_api import sync_playwright

def test_routing():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('http://localhost:3000')  # Adjust the URL as needed
        page.click('text=Dashboard')  # Adjust the selector as needed
        # Accept trailing slash variations from static server
        assert page.url.rstrip('/') == 'http://localhost:3000/dashboard'
        # Close browser inside the context to avoid event-loop issues
        browser.close()