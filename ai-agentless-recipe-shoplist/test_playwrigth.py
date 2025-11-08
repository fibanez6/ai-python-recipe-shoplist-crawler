import asyncio
import rich
from playwright.async_api import async_playwright
import shutil
import os

STEALTH_JS = r"""
(() => {
  // 1) navigator.webdriver = false
  Object.defineProperty(navigator, 'webdriver', {
    get: () => false,
    configurable: true
  });

  // 2) navigator.languages
  Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
    configurable: true
  });

  // 3) navigator.plugins (fake a small list)
  Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5],
    configurable: true
  });

  // 4) window.chrome runtime stub
  if (!window.chrome) {
    window.chrome = { runtime: {} };
  }

  // 5) permissions query override (some bots check this)
  const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
  if (originalQuery) {
    window.navigator.permissions.query = (parameters) => {
      if (parameters && parameters.name === 'notifications') {
        return Promise.resolve({ state: Notification.permission });
      }
      return originalQuery(parameters);
    };
  }

  // 6) Mock webdriver-specific properties used by some checks
  try {
    // Fix for Headless detection via toString checks
    const newProto = navigator.__proto__;
    if (newProto && newProto.constructor) {
      newProto.constructor.prototype = newProto;
    }
  } catch (e) {}

  // 7) Provide a harmless WebGL vendor/renderer (used by some fingerprinting)
  try {
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
      // 37445 = UNMASKED_VENDOR_WEBGL, 37446 = UNMASKED_RENDERER_WEBGL
      if (parameter === 37445) return 'Intel Inc.';
      if (parameter === 37446) return 'Intel Iris OpenGL Engine';
      return getParameter.call(this, parameter);
    };
  } catch (e) {}
})();
"""

async def fetch_coles_products():
    # url = "https://www.coles.com.au/search/products?q=tomatoes&limit=12"
    url="https://www.coles.com.au/_next/data/20251029.1-5acc651e3b5f8a27a9fa067cf11fc08619865a7b/en/search/products.json?q=tomato"

    async with async_playwright() as p:
        # Use a persistent context and headed mode (helps bypass Incapsula)
        context = await p.chromium.launch_persistent_context(
            user_data_dir="/tmp/real_profile_playwright",
            headless=False,  # run headful at least first time
            viewport={"width": 1280, "height": 800},
        )

        page = await context.new_page()

        # Add stealth script to run on every new document
        await page.add_init_script(STEALTH_JS)

        # Set realistic headers / UA
        await page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
        })
        await page.evaluate("""() => { Object.defineProperty(navigator, 'userAgent', {get: () => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}); }""")

        # Navigate
        # await page.goto(url, wait_until="networkidle")
        await page.goto(url)

        html = await page.content()
        rich.print("------------------- PAGE HTML ------------------")
        rich.print(html)

        cleaned_file = "/tmp/coles_tomatoes_cleaned.html"
        with open(cleaned_file, 'w', encoding='utf-8') as f:
                f.write(html)

        await context.close()

        # Remove the persistent user data directory after closing the context
        # user_data_dir = "/tmp/real_profile_playwright"
        # if os.path.exists(user_data_dir):
        #     shutil.rmtree(user_data_dir)

if __name__ == "__main__":
    asyncio.run(fetch_coles_products())
