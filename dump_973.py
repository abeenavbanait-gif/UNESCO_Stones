import asyncio
from playwright.async_api import async_playwright
from unesco_fetcher import create_stealth_browser, wait_for_cloudflare

async def main():
    async with async_playwright() as p:
        browser, context, page = await create_stealth_browser(p)
        await page.goto("https://whc.unesco.org/en/list/973", wait_until="domcontentloaded", timeout=120000)
        await wait_for_cloudflare(page, context=context, timeout_ms=20000)
        html = await page.content()
        with open("973.html", "w") as f:
            f.write(html)
        await browser.close()
        print("Successfully dumped 973.html")

if __name__ == "__main__":
    asyncio.run(main())
