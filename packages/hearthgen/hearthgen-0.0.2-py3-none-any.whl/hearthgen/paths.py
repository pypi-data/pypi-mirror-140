# XPATHS

NAME_FIELD = '//*[@id="panel_left_cardname_race"]/div/input[1]'
SUBMIT_BTN = '//*[@id="next"]'
TEXT_FIELD = '//*[@id="input-area"]'
MANA_FIELD = '//*[@id="panel_left_mana"]/div/input[1]'
ATTACK_FIELD = '//*[@id="panel_left_mana"]/div/input[2]'
HEALTH_FIELD = '//*[@id="panel_left_mana"]/div/input[3]'
ART_UPLOAD = '//*[@id="file"]'
HD_USE = '//*[@id="background-choser"]/div/div[1]/p[1]/input'
READY_CARD = '//*[@id="card"]'
TYPE = '//*[@id="panel_left_cardname_race"]/div/input[2]'

# CSS SELECTORS

HD = '#addbgCheckbox'
GOLDEN = '#goldenCheckbox'

# RARITY CSS

RARITY_BUTTONS = {
    'legendary': '#panel_left_rarity > div > label:nth-child(10) > i',
    'leg': '#panel_left_rarity > div > label:nth-child(10) > i',
    'epic': '#panel_left_rarity > div > label:nth-child(8) > i',
    'rare': '#panel_left_rarity > div > label:nth-child(6) > i',
    'common': '#panel_left_rarity > div > label:nth-child(6) > i',
    'basic': ''
}

# TYPE CSS

TYPE_BUTTONS = {
    'spell': '#type_menu > div:nth-child(3)',
    'weapon': '#type_menu > div:nth-child(4)',
    'power': '#type_menu > div:nth-child(5)',
    'portrait': '#type_menu > div:nth-child(6)',
    'hero': '#type_menu > div:nth-child(7)'
}
