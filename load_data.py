import requests
import pandas as pd
from lxml import etree


UFC_URL = 'http://www.ufc.com'
UFC_FIGHTERS_URL = u'http://www.ufc.com/fighter/Weight_Class/filterFighters'
UFC_HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}
UFC_ROWS_PER_PAGE = 20
UFC_POST_DATA = {
    'fighterFilter': 'Current',
    'max': UFC_ROWS_PER_PAGE,
    'offset': 0,
    'order': 'asc',
    'sort': 'lastName'
}

SHERDOG_URL = 'http://www.sherdog.com'
SHERDOG_SEARCH_URL = 'http://www.sherdog.com/stats/fightfinder?SearchTxt='

DATA_SAVE_PATH = './data/train.pickle'


def load_fights_stats(fighters):
    """
    Load fights stats from sherdog.com

    :param fighters: dict_keys(str)
    :return: dict
    """
    fights_stats = dict()
    for fighter in fighters:
        r = requests.get(SHERDOG_SEARCH_URL + '+'.join(fighter.split(' ')))
        search_content = etree.HTML(r.text)
        try:
            fighter_url = search_content.xpath(
                '//table[@class="fightfinder_result"]//a[text()="{name}"]/@href'.format(
                    name=fighter
                )
            )[0]
        except Exception as exc:
            print("Sherdog: Fighter not found: " + fighter)
            continue
        fighter_r = requests.get(SHERDOG_URL + fighter_url)
        fighter_content = etree.HTML(fighter_r.text)
        fights = fighter_content.xpath(
            '//div[@class="module fight_history" and ' +
            './/div/h2/text()="Fight History - Pro"]' +
            '//tr[@class="odd" or @class="even"]'
        )

        for fight in fights:
            result = fight.xpath('./td[1]/span/text()')[0]
            rival = fight.xpath('./td[2]/a/text()')[0]
            if result in ('win', 'loss',) and rival in fighters:
                if (rival, fighter) in fights_stats:
                    continue
                if (fighter, rival) in fights_stats:
                    result = True if 'win' else False
                    if fights_stats[(fighter, rival)] == result:
                        continue
                    else:
                        del fights_stats[(fighter, rival)]
                fights_stats[(fighter, rival)] = True if result == 'win' else False

    return fights_stats


def load_ufc_fighter_characteristics():
    """
    Load fighters parameters(height, weight, etc) from ufc.com

    :return: dict
    """

    total_fighters_count = None
    fighters_urls = []
    fighters_stats = dict()
    # load first page and take total fighters count from there
    r = requests.post(
        UFC_FIGHTERS_URL, data=UFC_POST_DATA, headers=UFC_HEADERS
    )
    html_content = etree.HTML(r.text)
    total_fighters_count = int(html_content.xpath(
        '//div[@class="paginate-results"]/span[@class="row-count"][2]/text()'
    )[0])

    # collect fighters urls
    for fighter in html_content.xpath('//a[@class="fighter-name"]'):
        fighters_urls.append(fighter.values()[0])

    for offset in range(20, total_fighters_count, UFC_ROWS_PER_PAGE):
        UFC_POST_DATA['offset'] = offset
        r = requests.post(
            UFC_FIGHTERS_URL, data=UFC_POST_DATA, headers=UFC_HEADERS
        )
        # collect fighters urls
        html_content = etree.HTML(r.text)
        for fighter in html_content.xpath('//a[@class="fighter-name"]'):
            fighters_urls.append(fighter.values()[0])

    # collect fighters stats
    for url in fighters_urls:
        r = requests.get(UFC_URL + url)
        html_content = etree.HTML(r.text)
        name = html_content.xpath(
                '//div[@class="fighter-top"]/div[@class="top-links"]/' +
                'div[@class="ufc-breadcrumb-top floatl"]/' +
                'div[@id="fighter-breadcrumb"]/span/h1/text()'
        )[0]
        age = html_content.xpath(
            '//div[@class="fighter-info"]/table/tr/td[@id="fighter-age"]/text()'
        )
        height = html_content.xpath('//meta[@name="gssHeightCm"]/@content')
        weight = html_content.xpath('//meta[@name="gssWeight"]/@content')
        hand_reach = html_content.xpath(
            '//div[@class="fighter-info"]/table/tr/td[@id="fighter-reach"]/text()'
        )
        leg_reach = html_content.xpath(
            '//div[@class="fighter-info"]/table/tr/td[@id="fighter-leg-reach"]/text()'
        )
        try:
            wins, loses, draws = html_content.xpath(
                '//meta[@name="gssRecord"]/@content'
            )[0].split('-')
        except Exception:
            print("UFC: Fighter record is invalid: " + name)
            continue
        fighters_stats[name] = {
            'age': int(age[0]) if age else None,
            'height': int(height[0]) if height and height[0] else None,
            'weight': int(weight[0]) if weight and weight[0] else None,
            'hand_reach': int(hand_reach[0][:-1]) if hand_reach else None,
            'leg_reach': int(leg_reach[0][:-1]) if leg_reach else None,
            'wins': int(wins),
            'loses': int(loses),
            'draws': int(draws.split(',')[0])
        }

    return fighters_stats


def process_data(fights_stats, fighter_characteristics):
    """
    Merge loaded data to single DataFrame

    :param: dict((str, str) -> bool)
    :param: dict(str -> dict())
    :return: pandas.DataFrame
    """
    processed_data = pd.DataFrame()

    for fight in fights_stats.items():
        fighter = fight[0][0]
        rival = fight[0][1]
        result = fight[1]

        fighter_chars = fighter_characteristics[fighter]
        rival_chars = fighter_characteristics[rival]

        diff_dict = {'result': result}
        for char in fighter_chars.keys():
            if fighter_chars[char] and rival_chars[char]:
                diff_dict[char+'_diff'] = fighter_chars[char] - rival_chars[char]
            else:
                diff_dict[char+'_diff'] = 0
        processed_data = processed_data.append(diff_dict, ignore_index=True)

    return processed_data


def load_data():
    """
    Load fighter stats from different resources and merge it
    """
    fighter_characteristics = load_ufc_fighter_characteristics()
    fighters = fighter_characteristics.keys()
    fights_stats = load_fights_stats(fighters)

    # create DataFrame with stats and serialize result
    train_data = process_data(fights_stats, fighter_characteristics)
    train_data.to_pickle(DATA_SAVE_PATH)
