import requests
from bota.web_scrap import scrap_constant
from bota import constant
from datetime import datetime
from bota.utility.discord_display import cvt_dict_to_discord_pretty_text


class DotaProTracker():
    def __init__(self):
        self.update_threshold_time = constant.D2PT_HERO_UPDATE_THRESHOLD
        self.hero_info = {}

    def get_hero_details_from_d2pt(self, hero_name, top=5):
        current_time = datetime.now()
        flag = 1 if hero_name in self.hero_info else 0
        if flag:
            if (current_time - self.hero_info[hero_name]['fetch_time']).total_seconds() < constant.D2PT_HERO_UPDATE_THRESHOLD:
                hero_info = self.hero_info[hero_name]['value']
                return hero_info

        value = get_d2pt_hero(hero_name, top)
        fetch_time = datetime.now()
        self.hero_info[hero_name] = {'fetch_time': fetch_time, 'value': value}
        return value


def get_d2pt_hero_json(heroname):
    d2pt_hero_name = scrap_constant.d2pt_hero_names[heroname]
    url = constant.D2PT_HERO_BASE_URL + d2pt_hero_name
    json_data = requests.get(url, headers=scrap_constant.browser_headers)
    json_data = json_data.json()
    return json_data


def clean_list_dict(matches, wanted_keys):
    final_matches = []
    for match in matches:
        temp = {}
        for wanted_key in wanted_keys:
            temp[wanted_key] = match[wanted_key]
        final_matches.append(temp)
    return final_matches


def get_d2pt_hero(hero_name, top=5):
    json_data = get_d2pt_hero_json(hero_name)
    meta_data = json_data[constant.D2PT_KEYWORD_META]
    good_against_data = json_data[constant.D2PT_KEYWORD_CROSS_META][constant.D2PT_KEYWORD_GOOD_AGAINST][:top]
    bad_against_data = json_data[constant.D2PT_KEYWORD_CROSS_META][constant.D2PT_KEYWORD_BAD_AGAINST][:top]
    recent_matches = json_data[constant.D2PT_KEYWORD_RECENT_MATCH][:top]

    total_picked = meta_data['picked']
    total_won = meta_data['won']
    total_winrate = int((total_won/total_picked) * 100)
    notable_players = meta_data['pros']
    notable_players_string = ""
    for player in notable_players:
        name = player['ident']
        win_loss = str(player['won']) + "-" + str(player['picked'] - player['won'])
        notable_players_string += f"  |  **{name}**   `W/L:` **{win_loss}**"

    header = f"**{hero_name.upper()}**      `Total Pick`: **{total_picked}**      `Won`: **{total_won}**      `Win Rate`: **{total_winrate}%**"
    post_header = f"Mostly Played by: {notable_players_string}"

    recent_matches = clean_list_dict(recent_matches,constant.WANTED_KEYS_RECENT_MATCHES)
    recent_matches_string = cvt_dict_to_discord_pretty_text(recent_matches, rename_keys=constant.RECENT_MATCHES_KEY_RENAME)

    good_against_data_updated = []
    for data in good_against_data:
        temp = {}
        temp['hero 1'] = hero_name
        temp['score'] = str(data['won_against']) + '    -    ' + str(data['lost_against'])
        temp['hero 2'] = data['name']
        good_against_data_updated.append(temp)
    good_against_string = cvt_dict_to_discord_pretty_text(good_against_data_updated)

    bad_against_data_updated = []
    for data in bad_against_data:
        temp = {}
        temp['hero 1'] = hero_name
        temp['score'] = str(data['won_against']) + '    -    ' + str(data['lost_against'])
        temp['hero 2'] = data['name']
        bad_against_data_updated.append(temp)
    bad_against_string = cvt_dict_to_discord_pretty_text(bad_against_data_updated)

    body_1 = f"**Recent Matches**```glsl\n{recent_matches_string}```"
    body_2 = f"**Good Against**```glsl\n{good_against_string}```"
    body_3 = f"**Bad Against**```glsl\n{bad_against_string}```"

    final_string = header + '\n' + post_header + '\n' + body_1 + body_2 + body_3
    return final_string


if __name__ == "__main__":
    d2pt = DotaProTracker()
    for i in range(5):
        start = datetime.now()
        r = d2pt.get_hero_details_from_d2pt('axe')
        print((datetime.now() - start).total_seconds())
        print(r)

    # start= datetime.now()
    # r = get_d2pt_hero("axe")
    # print((datetime.now() - start).total_seconds())
    # print(r)