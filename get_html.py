import asyncio
from playwright.async_api import async_playwright
from unesco_fetcher import create_stealth_browser, wait_for_cloudflare, UNESCO_LIST_URL

async def main():
    async with async_playwright() as p:
        browser, context, page = await create_stealth_browser(p)
        print("Warming up...")
        await page.goto(UNESCO_LIST_URL, wait_until="domcontentloaded")
        await wait_for_cloudflare(page, context=context, timeout_ms=20000)
        print("Fetching site 703...")
        await page.goto("https://whc.unesco.org/en/list/703", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        html = await page.content()
        with open('site_703.html', 'w') as f:
            f.write(html)
        print("Saved.")
        await browser.close()

asyncio.run(main())
