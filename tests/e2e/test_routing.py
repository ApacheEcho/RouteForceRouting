from playwright.sync_api import sync_playwright

def test_routing():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('http://localhost:3000')  # Adjust the URL as needed
        page.click('text=Dashboard')  # Adjust the selector as needed
        assert page.url == 'http://localhost:3000/dashboard'  # Adjust the expected URL as needed
        page.go_back()
        assert page.url == 'http://localhost:3000/'  # Adjust the expected URL as needed
        browser.close()