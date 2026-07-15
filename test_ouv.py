import asyncio
from playwright.async_api import async_playwright
from unesco_fetcher import create_stealth_browser, wait_for_cloudflare

async def main():
    async with async_playwright() as p:
        browser, context, page = await create_stealth_browser(p)
        await page.goto("https://whc.unesco.org/en/list/703", wait_until="domcontentloaded")
        await wait_for_cloudflare(page, context=context)
        
        # Check if there is a div with id='ouv'
        has_ouv_div = await page.evaluate("() => !!document.querySelector('#ouv')")
        print("Has #ouv div:", has_ouv_div)
        
        if has_ouv_div:
            ouv_text = await page.evaluate("() => document.querySelector('#ouv').innerText")
            print("Length of #ouv text:", len(ouv_text))
            print(ouv_text[:500])
        else:
            # Maybe it's a different id or just headings
            print("No #ouv div found. Let's get the headings.")
            html = await page.content()
            print("Content length:", len(html))
        
        await browser.close()

asyncio.run(main())
