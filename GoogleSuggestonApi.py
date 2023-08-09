import aiohttp
import asyncio
import json
from billiard import Pool
import argparse


def criteria_for_miss_spells(keyword, suggestions):
    if not suggestions == []:
        shortest_suggestion = min([word for word in suggestions if word], key=len)
        keyword_data = keyword.split()
        suggestions_data = shortest_suggestion.split()
        is_misspelled = True
        order_present = True

        if keyword in suggestions:
            is_misspelled = False
        
        if len(keyword) <= 2:
            is_misspelled = False

        for i , word in enumerate(keyword_data):
            if word not in suggestions_data[i]:
                order_present = False
                break

        if (len(keyword_data) < len(suggestions_data)
            and order_present):
            is_misspelled = False

        correct_keyword = shortest_suggestion if is_misspelled else None

        keyword_dict = {
            'keyword': keyword,
            'suggestions': suggestions,  
            'is_misspelled': is_misspelled,
            'correct_keyword': correct_keyword,
        }
        return keyword_dict

    else:
        keyword_dict = {
            'keyword': keyword,
            'data_found': False,
            'is_misspelled': "",
            'correct_keyword': "",
        }
        return keyword_dict


async def fetch_suggestions(session, keyword):
    url = (
        f'http://suggestqueries.google.com/complete/search?client=firefox&q={keyword}'
    )
    async with session.get(url) as response:
        try:
            response.raise_for_status()
            data = json.loads(await response.text())  
            return keyword, data[1]
        except aiohttp.ClientError:
            return keyword, None


async def main(keywords):
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
