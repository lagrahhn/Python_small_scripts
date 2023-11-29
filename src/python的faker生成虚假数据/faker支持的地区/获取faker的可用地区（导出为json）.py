import json

ff = open('lists1.json', 'w', encoding='utf-8')
fff = open('lists2.json', 'w', encoding="utf-8")
with open('faker支持的地区.txt', 'r', encoding='utf-8') as f:
    content = f.readlines()
    str_ = "["
    for i in content:
        lists = i.split("-")
        lists = [j.strip() for j in lists]
        dicts = {
            "缩写": lists[0],
            "英文名称": lists[1],
            "中文名称": lists[2]
        }
        str_ += str(dicts).replace("'", '"') + ","
        ff.write(json.dumps(dicts))
        ff.write("\n")
    str_ = str_[:-1]
    str_ += "]"
    fff.write(str_)