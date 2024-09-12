import json
import crud_sql as crud
import schemas as s

FILES = {
    'pics': 'backup/hanna_images.json',
    'text': 'backup/hanna_textblock.json',
    'markt': 'backup/hanna_market.json',
    'user': 'backup/hanna_profile.json'
}

SCHEMAS = {
    'pics': s.ImageForDB,
    'text': s.Textblock,
    'markt': s.Market_lim,
    'user': s.ProfileCreate
}


def load_all(db):
    for typ, file in FILES.items():
        print(typ)
        with open(file) as f:
            print(file)
            d = json.load(f)
            print('loaded json file')
            for item in d:
                print(item)
                item_s = SCHEMAS[typ].parse_obj(item)
                print(item_s)
                crud.new(db, typ, item_s)

    return True
