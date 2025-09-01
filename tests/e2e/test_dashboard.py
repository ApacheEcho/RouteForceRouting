from playwright.sync_api import sync_playwright

def test_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('http://localhost:3000/dashboard')
        
        assert page.title() == 'Dashboard - My App'
        assert page.is_visible('text=Welcome to the Dashboard')
        
        page.click('text=View Reports')
        assert page.url == 'http://localhost:3000/dashboard/reports'
        
        browser.close()