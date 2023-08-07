import aiohttp
import asyncio
import sys
import json
from billiard import Pool
import argparse


def criteria_for_miss_spells(keyword, suggestions):
    if not suggestions == []:
        shortest_keyword_suggestion = min([word for word in suggestions if word], key=len)
        splitted_keyword = keyword.split()
        splitted_shortest_suggestions = shortest_keyword_suggestion.split()
        is_misspelled = True
        order_present = False

        if keyword in suggestions:
            is_misspelled = False
        
        if len(keyword) <= 2:
            is_misspelled = False

        for word in splitted_shortest_suggestions:
            if word in keyword:   
                order_present = True
                break
            
        if (len(splitted_keyword) < len(splitted_shortest_suggestions)
            and order_present):
            is_misspelled = False

        correct_keyword = shortest_keyword_suggestion if is_misspelled else None

        if is_misspelled is not None:
            keyword_dict = {
                'keyword': keyword,
                'suggestions': suggestions,  
                'is_misspelled': is_misspelled,
                'correct_keyword': correct_keyword,
            }

        else:
            keyword_dict = {
                'keyword': keyword,
                'data_found': True,
                'is_misspelled': False,
                'correct_keyword': ""
            }

        return keyword_dict


async def fetch_suggestions(session, keyword):
    url = (
        f'http://suggestqueries.google.com/complete/search?client=firefox&q={keyword}'
    )
    async with session.get(url) as response:
        try:
            response.raise_for_status()
            response_text = await response.text()
            data = json.loads(response_text)  
            return keyword, data[1]
        except aiohttp.ClientError:
            return keyword, None


async def main(keywords):
    processed_results_list = []

    connector = aiohttp.TCPConnector(ssl=False, limit=20)
    timeout = aiohttp.ClientTimeout(
        total=None,
        sock_connect=100,
        sock_read=100
    )
    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector
    ) as session:
        tasks = [fetch_suggestions(session, keyword) for keyword in keywords]
        results = await asyncio.gather(*tasks)

    with Pool() as pool:
        processed_results_list = pool.starmap(criteria_for_miss_spells, results)

    return processed_results_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('keywords', type=str, nargs='+')

    args = parser.parse_args()
    keywords = args.keywords

    final_results = asyncio.run(main(keywords))
    print(json.dumps(final_results, indent=4))
