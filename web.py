import os

import modal

app = modal.App("example-linkscraper")


playwright_image = modal.Image.debian_slim(
    python_version="3.10"
).run_commands(  # Doesn't work with 3.11 yet
    "apt-get update",
    "apt-get install -y software-properties-common",
    "apt-add-repository non-free",
    "apt-add-repository contrib",
    "pip install playwright",
    "pip install upstash-redis",
    "playwright install-deps chromium",
    "playwright install chromium",
)


@app.function(image=playwright_image)
async def get_links(url: str) -> set[str]:
    from playwright.async_api import async_playwright
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            links = await page.eval_on_selector_all(
                "a[href]", "elements => elements.map(element => element.href)"
            )
            print(links)
            await browser.close()

        base_url = links[0]

        # Filter out links that do not match the base url
        filtered_links = [link for link in links if base_url in link]
        print(filtered_links)
        
        #Redo as a list of tuples(base_url, filtered_links)
        final_links = []
        for link in filtered_links:
            final_links.append((base_url, link))

        return final_links
    except Exception as e:
        return

@app.function(image=playwright_image,secrets=[modal.Secret.from_name("upstash-redis")])
def print_network_info(base_url: str, link: str) -> None:

    from playwright.sync_api import sync_playwright
    from upstash_redis import Redis

    redis = Redis(url="https://good-hen-52234.upstash.io", token=os.environ["UPSTASH_REDIS"])

    if redis.sismember(base_url, link):
        return
    else:
        redis.sadd(base_url, link)
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
                context = browser.new_context()

                # Add an event listener to print the response JSON of fetch/XHR requests
                context.on('response', lambda response: (
                    print(response.json()) if response.request.resource_type == 'fetch' else None
                ))

                page = context.new_page()
                page.goto(link)
                browser.close()
            except Exception as e:
                return
    except Exception as e:
        return

@app.function()
def scrape():
    base_url = "http://modal.com"

    links = get_links.remote(base_url)
    for results in print_network_info.starmap(links,return_exceptions=False):
        print(results)

@app.local_entrypoint()
def run():
    scrape.remote()