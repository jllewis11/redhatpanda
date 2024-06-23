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
    "pip install boto3",
    "playwright install-deps chromium",
    "playwright install chromium",
)


@app.function(image=playwright_image)
async def get_links(url: str) -> set[str]:
    from playwright.async_api import async_playwright
    from playwright._impl._errors import TargetClosedError
    import requests

    try:
        if url == "https://jllewis11--example-mockdata-details.modal.run/":
            data = requests.get(url).json()
            return [(url, data)]

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            links = await page.eval_on_selector_all(
                "a[href]", "elements => elements.map(element => element.href)"
            )
            await browser.close()

        base_url = links[0]

        # Filter out links that do not match the base url
        filtered_links = [link for link in links if base_url in link]

        # Redo as a list of tuples(base_url, filtered_links)
        final_links = []
        for link in filtered_links:
            final_links.append((base_url, link))

        return final_links
    except Exception as e:
        return


@app.function(image=playwright_image, secrets=[modal.Secret.from_name("upstash-redis")])
async def print_network_info(base_url: str, link: str) -> None:
    import asyncio
    from playwright.async_api import async_playwright
    from playwright._impl._errors import TargetClosedError
    from upstash_redis import Redis
    import requests

    redis = Redis(
        url="https://good-hen-52234.upstash.io", token=os.environ["UPSTASH_REDIS"]
    )

    if redis.sismember(base_url, link):
        return
    else:
        redis.sadd(base_url, link)
    try:
        responses = []

        if base_url == "https://jllewis11--example-mockdata-details.modal.run/":
            data = requests.get(base_url).json()
            responses.append(data)
            return responses

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()

            # Add an event listener to print the response JSON of fetch/XHR requests
            async def print_response(response):
                try:
                    if (
                        response.request.resource_type == "fetch"
                        or response.request.resource_type == "xhr"
                    ):
                        res = await response.json()
                        if res is not None:
                            responses.append(res)
                except Exception as e:
                    return

            context.on("response", print_response)

            page = await context.new_page()
            await page.goto(link)
            await asyncio.sleep(5)
            await browser.close()

        return responses

    except Exception as e:
        return


@app.function(image=playwright_image, secrets=[modal.Secret.from_name("my-aws-secret")])
async def summarize(res: list[dict]):
    import boto3
    import json

    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    # Define the prompt for the model.
    prompt = f"Determine whether the response data poses one or more of the following security risk which are PII leaked, API keys exposed, or any other data that aren't suppose to be seen by the public. {res}. Do not say the word clear if there is a security issue. Only say clear if there is no security issue."

    # Set the model ID, e.g., Claude 3 Haiku.
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    # Format the request payload using the model's native structure.
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)
    response_text = ""
    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)
        # Decode the response body.
        model_response = json.loads(response["body"].read())

        # Extract and print the response text.
        response_text = model_response["content"][0]["text"]

    except Exception as e:
        response_text = "Error invoking model: " + str(e)

    print("Response", response_text)
    return response_text


@app.function(image=playwright_image, secrets=[modal.Secret.from_name("upstash-redis")])
def scrape(base_url: str):
    from upstash_redis import Redis
    import json

    redis = Redis(
        url="https://good-hen-52234.upstash.io", token=os.environ["UPSTASH_REDIS"]
    )

    links = get_links.remote(base_url)

    results = []

    for result in print_network_info.starmap(links):
        results.append(result)
    redis.flushall()

    website = {}

    summarized_results = []

    for r in summarize.map(results):
        summarized_results.append(r)
        print(r)
        print("\n\n")

    print(len(links))
    print(len(summarized_results))
    for x in range(len(summarized_results)):
        website[links[x][1]] = summarized_results[x]

    # Turn the dictionary into a json
    json_website = json.dumps(website)
    return json_website


@app.function()
@modal.web_endpoint()
def check(baseUrl: str):
    response = scrape.remote(baseUrl)
    return response


@app.local_entrypoint()
def run():
    scrape.remote()
