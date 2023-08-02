import aiohttp
import asyncio
import sys
import json
from billiard import Pool


def criteria_for_miss_spells(keyword, suggestions):
    if suggestions != []:
        shortest_keyword = min([word for word in suggestions if word], key=len)
        is_misspelled = (
            keyword not in suggestions or
            len(keyword) <= 2 or
            (len(keyword.split()) > len(shortest_keyword.split())
             and keyword in shortest_keyword)
        )
        correct_keyword = shortest_keyword if is_misspelled else None
        return is_misspelled, correct_keyword


def show_result(keywords, results, processed_results):
    result_dict = []
    for keyword, suggestions, processed_result in zip(keywords, results, processed_results):
        if processed_result is not None:
            is_misspelled, correct_keyword = processed_result
            keyword_dict = {
                'keyword': keyword,
                'suggestions': suggestions[1],  
                'is_misspelled': is_misspelled,
                'correct_keyword': correct_keyword,
            }
            result_dict.append(keyword_dict)
        else:
            keyword_dict = {
                'keyword': keyword,
                'Data Not Found in Api': True,
                'is_misspelled': False,
                'correct_keyword': ""
            }
            result_dict.append(keyword_dict)

    return json.dumps(result_dict, indent=4)


async def fetch_suggestions(session, keyword, fetched_keywords, unfetched_keywords):
    url = (
        f'http://suggestqueries.google.com/complete/search?client=firefox&q={keyword}'
    )
    async with session.get(url) as response:
        if response.status == 200:
            response_text = await response.text()
            print(f'i am response {response_text}')
            if response_text.startswith('['):
                data = json.loads(response_text)
                fetched_keywords.append(keyword)
                return keyword, data[1]
            else:
                unfetched_keywords.append(keyword)
                return keyword, None
        else:
            unfetched_keywords.append(keyword)
            return keyword, None


def generate_report(fetched_keywords, unfetched_keywords):
    with open('keywords_report.txt', 'w') as report_file:
        report_file.write("Fetched Keywords: ")
        report_file.write(", ".join(fetched_keywords))
        report_file.write("\nUnfetched Keywords: ")
        report_file.write(", ".join(unfetched_keywords))


async def main(keywords):
    fetched_keywords = []
    unfetched_keywords = []
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
        tasks = [fetch_suggestions(session, keyword, fetched_keywords, unfetched_keywords) for keyword in keywords]
        results = await asyncio.gather(*tasks)

    with Pool(processes=len(keywords)) as pool:
        processed_results_list = pool.starmap(criteria_for_miss_spells, results)

    generate_report(fetched_keywords, unfetched_keywords)
    return results, processed_results_list


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please Enter Atleast 2 keywords")
        sys.exit(1)

    keywords = sys.argv[1:]
    results, processed_results_list = asyncio.run(main(keywords))
    print(show_result(keywords, results, processed_results_list))
