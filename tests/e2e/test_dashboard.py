from playwright.sync_api import sync_playwright


def test_dashboard():
    p = sync_playwright().start()
    try:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:3000/dashboard')

        assert page.title() == 'RouteForce Dashboard'

        # current placeholder shows a simple welcome message
        assert page.is_visible('text=Welcome to the dashboard placeholder')

        # click the Home link (placeholder) and assert navigation
        page.click('text=Home')
        assert page.url.startswith('http://localhost:3000')

        browser.close()
    finally:
        p.stop()