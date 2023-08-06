import random
import json
import os
import re

# In[223]:

abb_data = None
oov_dict = None
domain_extension_dict = None
domain_name_dict = None
general_en_word = None


class NumToVnStr:
    def __init__(self, mươi='mươi', nghìn='nghìn', tư='tư', lăm='lăm', bảy='bẩy', linh='linh', tỷ='tỷ',
                 đọc_số_rỗng=True):
        self.chữ_số = (
            'không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', random.choice(['bảy', 'bẩy']), 'tám', 'chín', 'mười')
        self.mươi = mươi
        self.trăm = 'trăm'
        self.nghìn = nghìn
        self.triệu = 'triệu'
        self.tỷ = tỷ
        self.mốt = 'mốt'
        self.tư = tư
        self.bảy = bảy
        self.lăm = lăm
        self.linh = linh
        self.đọc_số_rỗng = đọc_số_rỗng

    def remove_zero(self, text):
        # remove 0 trăm
        text = text.replace(' không trăm ', ' ')
        # remove 0 nghìn
        text = text.replace(' không nghìn ', ' ').replace(' không ngàn ', ' ')
        # remove
        words = set(text.split())
        if len(words.intersection({'nghìn', 'ngàn'})) > 0:
            text = text.replace(' triệu lẻ ', ' triệu ').replace(' triệu linh ', ' triệu ')
            if text.endswith('trăm'):
                text = text[:-5]
        if len(words.intersection({'triệu'})) > 0:
            text = text.replace(' tỷ lẻ ', ' tỷ ').replace(' tỷ linh ', ' tỷ ')
            if text.endswith('trăm nghìn'):
                text = text[:-11]
            elif text.endswith('trăm ngàn'):
                text = text[:-10]
        # if text.endswith('trăm')

        return text

    def to_vn_str(self, s):
        plain = self._arbitrary(s.lstrip('0'))
        lint = self.remove_zero(plain)
        return plain, lint
        # return random.choice([plain, lint])
        # return self._arbitrary(s.lstrip('0'))

    def _int(self, c):
        return ord(c) - ord('0') if c else 0

    def _LT1e2(self, s):
        if len(s) <= 1: return self.chữ_số[self._int(s)]
        if s[0] == '1':
            ret = self.chữ_số[10]
        else:
            ret = self.chữ_số[self._int(s[0])]
            if self.mươi:
                ret += ' ' + self.mươi
            elif s[1] == '0':
                ret += ' mươi'
        if s[1] != '0':
            ret += ' '
            if s[1] == '1' and s[0] != '1':
                ret += self.mốt
            elif s[1] == '4' and s[0] != '1':
                ret += self.tư
            elif s[1] == '7' and s[0] != '1':
                ret += self.bảy
            elif s[1] == '5':
                ret += self.lăm
            else:
                ret += self.chữ_số[self._int(s[1])]
        return ret

    def _LT1e3(self, s):
        if len(s) <= 2: return self._LT1e2(s)
        if s == '000': return ''
        ret = self.chữ_số[self._int(s[0])] + ' ' + self.trăm
        if s[1] != '0':
            ret += ' ' + self._LT1e2(s[1:])
        elif s[2] != '0':
            ret += ' ' + self.linh + ' ' + self.chữ_số[self._int(s[2])]
        return ret

    def _LT1e9(self, s):
        if len(s) <= 3: return self._LT1e3(s)
        if s == '000000' or s == '000000000': return ''
        mid = len(s) % 3 if len(s) % 3 else 3
        left, right = self._LT1e3(s[:mid]), self._LT1e9(s[mid:])
        hang = self.nghìn if len(s) <= 6 else self.triệu
        if not left:
            if not self.đọc_số_rỗng:
                return right
            else:
                return self.chữ_số[0] + ' ' + hang + ' ' + right
        if not right: return left + ' ' + hang
        return left + ' ' + hang + ' ' + right

    def _arbitrary(self, s):
        if len(s) <= 9: return self._LT1e9(s)
        mid = len(s) % 9 if len(s) % 9 else 9
        left, right = self._LT1e9(s[:mid]), self._arbitrary(s[mid:])
        hang = ' '.join([self.tỷ] * ((len(s) - mid) // 9))
        if not left:
            if not self.đọc_số_rỗng:
                return right
            elif right:
                return self.chữ_số[0] + ' ' + hang + ' ' + right
            else:
                return right
        if not right: return left + ' ' + hang
        return left + ' ' + hang + ' ' + right


def strip_text(text):
    words = text.split()
    words = [i for i in words if len(i) > 0]
    return ' '.join(words)


def get_re_idx(re_str, src_txt):
    src_txt = src_txt.lower()
    p_list = [
        (re.compile("^(" + re_str + ")\s"), 1),
        (re.compile("\s(" + re_str + ")$"), 1),
        (re.compile("(?=(\s(" + re_str + ")\s))"), 2),
        (re.compile("^(" + re_str + ")$"), 1),
    ]
    dict_result = dict({})
    for (p, idx) in p_list:
        # print(p, idx)
        # print(p, list(p.finditer(src_txt)))
        for m in p.finditer(src_txt):
            dict_result["{}-{}".format(m.start(idx), len(m.group(idx)))] = m.group(idx)
    return dict_result


def replace_oov_char(word, index_dict):
    dict_read = {
        'x': ['sờ', 'xờ', ''],
        'v': ['vờ', ''],
        'b': ['bờ'],
        'đ': ['đờ', ''],
        'm': ['mờ', ''],
        'z': ['dờ', ''],
        'g': ['gờ'],
        'd': ['dờ', ''],
        's': ['sờ', 'xờ', ''],
        't': ['tờ', ''],
        'p': ['pờ', ''],
        'j': ['giờ'],
        'k': ['cờ', ''],
        'y': ['i', ''],
        'r': ['rờ'],
        'ph': ['phờ'],
        'ch': ['chờ'],
        'c': ['cờ'],
        'f': ['phờ', '']
    }

    for key in index_dict.values():
        if dict_read.get(key, None) is not None:
            replace_value = random.choice(dict_read[key])
            if word.startswith('{} '.format(key)):
                word = replace_value + " " + word[len(key):]
                # print(word)
            if word.endswith(' {}'.format(key)):
                word = word[:-len(key)] + " " + replace_value
            if ' {} '.format(key) in word:
                word = word.replace(' {} '.format(key), ' {} '.format(replace_value))
    words = word.split()
    words = [i for i in words if len(i) > 0]
    return ' '.join(words)


def get_random_oov(value=None):
    global oov_dict
    if oov_dict is None:
        # oov_dict = dict({})
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'en_dict.json'), 'r',
                  encoding='utf-8') as file:
            oov_dict = json.load(file)
            # for line in file:
            #     data_line = json.loads(line)
            #     oov_dict[data_line['src']] = data_line['tgt']
    if value is None:
        src = random.choice(list(oov_dict.keys()))
        tgt = random.choice(oov_dict[src])
    else:
        if oov_dict.get(value, None) is None:
            return None
        else:
            src = value
            tgt = random.choice(oov_dict[src])

    # tgt = random.choice(candidate['tgt'])
    replace_dict = get_re_idx('(.|ph|ch)', tgt)
    tgt = replace_oov_char(tgt, replace_dict)
    return src, strip_text(tgt)


def get_general_en_word():
    global general_en_word
    if general_en_word is None:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'general_word_en.txt'), 'r',
                  encoding='utf-8') as file:
            general_en_word = list(set(file.read().strip().split('\n')))
    return general_en_word


def get_random_abb(val):
    global abb_data
    if abb_data is None:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'abb_dict.json'), 'r',
                  encoding='utf-8') as file:
            abb_data = json.load(file)

    if val is None or abb_data.get(val, None) is None:
        val = random.choice(list(abb_data.keys()))
    return abb_data[val], strip_text(abb_data[val])


# # Number

def get_random_decimal(min_num, max_num, read_single=False):
    convert = NumToVnStr(đọc_số_rỗng=True,
                         linh=random.choice(['lẻ', 'linh']),
                         tư=random.choice(['bốn', 'tư']),
                         nghìn=random.choice(['ngàn', 'nghìn']),
                         mươi=random.choice([False, "mươi"]),
                         tỷ=random.choice(['tỷ']),
                         lăm=random.choice(['lăm', 'nhăm', 'năm']),
                         bảy=random.choice(['bảy', 'bẩy']))
    number = random.randint(min_num, max_num)
    is_negative = number < 0

    # if not read_single:
    #     if number == 10:
    #         return "10", 'mười'
    #     if number == -10:
    #         return random.choice([("-10", 'âm mười'), ("-10", 'trừ mười')])

    if is_negative:
        if read_single:
            return str(number), "{} {}".format(random.choice(['trừ']),
                                               ' '.join([convert.to_vn_str(i) for i in list(str(number * -1))]))

        num_out = str(number)
        if len(num_out) >= 6:
            num_out = "{:,}".format(number).replace(',', '.')
        return num_out, "{} {}".format(random.choice(['âm']), convert.to_vn_str((str(number * -1))))

    if read_single:
        return str(number), "{}".format(' '.join([convert.to_vn_str(i) for i in list(str(number))]))

    if len(str(number)) >= 5:
        # print(number)
        return "{:,}".format(number).replace(',', '.'), strip_text("{}".format(convert.to_vn_str(str(number))))

    return str(number), strip_text("{}".format(convert.to_vn_str(str(number))))


def get_random_float(max_int, max_real, is_positive=False):
    min_num_int, max_num_int = -(10 ** max_int - 1) if not is_positive else 0, 10 ** max_int - 1
    min_num_real, max_num_real = 0, 10 ** max_real - 1
    real_with_zero = None
    read_real_sigle = random.choice([False, True])
    if random.random() < 0.3:
        real_with_zero = random.choice([("0", "không"), ("00", "không không")])
    int_number = get_random_decimal(min_num_int, max_num_int)
    real_number = get_random_decimal(min_num_real, max_num_real, read_single=read_real_sigle)
    if real_with_zero is not None:
        real_number = real_with_zero[0] + real_number[0], "{} {}".format(real_with_zero[1], real_number[1])
    if '.' not in int_number[0]:
        sep = random.choice([('.', 'chấm'), (',', 'phẩy')])
    else:
        sep = (',', 'phẩy')
    return "{}{}{}".format(int_number[0], sep[0], real_number[0]), strip_text("{} {} {}".format(int_number[1], sep[1],
                                                                                                real_number[1]))


# # Date time

def get_random_date():
    day = get_random_decimal(1, 31)
    day_2 = get_random_decimal(1, 31)
    day_3 = get_random_decimal(1, 31)
    month = get_random_decimal(1, 12)
    year = get_random_decimal(100, 3000, read_single=random.choice([False, True]))

    year_single = get_random_decimal(100, 3000, read_single=True)
    month_single = get_random_decimal(1, 12, read_single=True)
    if len(month_single[0]) < 2:
        month_single = ("0" + month_single[0], 'không {}'.format(month_single[1]))
    day_single = get_random_decimal(1, 31, read_single=True)
    if len(day_single[0]) < 2:
        day_single = ("0" + day_single[0], 'không {}'.format(day_single[1]))
    sep = '/'

    word_sep_1 = random.choice(
        ['ngày'] + ([random.choice(['mồng', 'mùng', 'ngày mồng', 'ngày mùng'])] if len(day[0]) < 2 else []))
    word_sep_2 = random.choice(
        ['ngày'] + ([random.choice(['mồng', 'mùng', 'ngày mồng', 'ngày mùng'])] if len(day_2[0]) < 2 else []))

    and_sep = random.choice(['và', ''])
    to_sep = random.choice(['tới', 'đến'])

    candidates = [
        ("{} {} {} {} {} tháng {}".format(word_sep_1, day[0], to_sep, word_sep_2, day_2[0], month[0]),
         "{} {} {} {} {} tháng {}".format(
             word_sep_1,
             day[1],
             to_sep,
             word_sep_2,
             day_2[1],
             month[1])),
        ("{} {} {} {} {} tháng {}".format(word_sep_1, day[0], and_sep, word_sep_2, day_2[0], month[0]),
         "{} {} {} {} {} tháng {}".format(
             word_sep_1,
             day[1],
             and_sep,
             word_sep_2,
             day_2[1],
             month[1])),

        ("{} {} và {} {}".format(word_sep_1, day[0], word_sep_2, day_2[0]), "{} {} và {} {}".format(
            word_sep_1,
            day[1],
            word_sep_2,
            day_2[1])),

        ("{}".format(day[0]), "{} {}".format(
            word_sep_1,
            day[1])),

        ("{}{}{}".format(day[0], sep, month[0]), "{} {} tháng {}".format(
            random.choice(list(set(
                ['ngày', random.choice(['mồng', 'mùng', 'ngày mồng', 'ngày mùng']) if len(day[0]) < 2 else '', '']))),
            day[1],
            month[1])),
        ("{}{}{}".format(month[0], sep, year[0]),
         "tháng {} {} {}".format(month[1], random.choice(['năm', '']), year[1])),
        ("{}{}{}{}{}".format(day[0], sep, month[0], sep, year[0]), "{} {} tháng {} {} {}".format(
            random.choice(list(set(
                ['ngày', random.choice(['mồng', 'mùng', 'ngày mồng', 'ngày mùng']) if len(day[0]) < 2 else '', '']))),
            day[1],
            month[1], random.choice(['năm', '']), year[1])),
    ]

    day_only = []
    if len(day[0]) > 1:
        day_only += [("ngày {}".format(day[0]), "ngày {}".format(day[1]))]
        if len(day_2[0]) > 1:
            day_only += [("ngày {}, {}".format(day[0], day_2[0]), "ngày {} {}".format(day[1], day_2[1]))]
            if len(day_3[0]) > 1:
                day_only += [("ngày {}, {}, {}".format(day[0], day_2[0], day_3[0]),
                              "ngày {} {} {}".format(day[1], day_2[1], day_3[1]))]

    month_only = [("tháng {}".format(month[0]), "tháng {}".format(month[1]))]
    q_only = [("quí {}".format(month[0]), "quí {}".format(month[1]))]
    year_only = [("năm {}".format(year[0]), "năm {}".format(year[1]))]

    candidates_single = [
        (
            "ngày {}{}{}".format(day_single[0], sep, month_single[0]),
            "ngày {} {}".format(day_single[1], month_single[1])),
        ("tháng {}{}{}".format(month_single[0], sep, year_single[0]),
         "tháng {} {}".format(month_single[1], year_single[1])),
        ("quí {}{}{}".format(month_single[0], sep, year_single[0]),
         "quí {} {}".format(month_single[1], year_single[1])),
        ("ngày {}{}{}{}{}".format(day_single[0], sep, month_single[0], sep, year_single[0]),
         "ngày {} {} {}".format(day_single[1], month_single[1], year_single[1])),
        ("{}{}{}{}{}".format(day_single[0], sep, month_single[0], sep, year_single[0]),
         "{} tháng {} {}".format(day_single[1], month_single[1], year_single[1])),
    ]

    result = random.choice(candidates + candidates_single + day_only + month_only + q_only + year_only)
    # result = random.choice(candidates)

    date_out = result[0]
    date_in = strip_text(result[1])

    if date_in.startswith('ngày mồng') and not date_out.startswith('ngày mồng'):
        date_out = "{} {}".format('ngày mồng', date_out)
    if date_in.startswith('ngày mùng') and not date_out.startswith('ngày mùng'):
        date_out = "{} {}".format('ngày mùng', date_out)
    if date_in.startswith('ngày') and not date_out.startswith('ngày'):
        date_out = "{} {}".format('ngày', date_out)
    if date_in.startswith('mồng') and not date_out.startswith('mồng'):
        date_out = "{} {}".format('mồng', date_out)
    if date_in.startswith('mùng') and not date_out.startswith('mùng'):
        date_out = "{} {}".format('mùng', date_out)
    if date_in.startswith('tháng') and not date_out.startswith('tháng'):
        date_out = "{} {}".format('tháng', date_out)

    return date_out, date_in


def get_random_time():
    hour = get_random_decimal(0, 23)
    minute = get_random_decimal(0, 60)
    sec = get_random_decimal(0, 60)

    candidates = [
        ("{}h".format(hour[0]), "{} giờ".format(hour[1])),
        ("{}h{}".format(hour[0], minute[0]), "{} giờ {} {}".format(hour[1], minute[1], random.choice(['phút', '']))),
        ("{}:{}:{}".format(hour[0], minute[0], sec[0]), "{} giờ {} phút {} giây".format(hour[1], minute[1], sec[1])),
    ]

    if minute[0] == '30':
        candidates += [
            ("{}h30".format(hour[0]), "{} {}".format(hour[1], random.choice(['giờ rưỡi', 'rưỡi']))),
        ]

    result = random.choice(candidates)
    return result[0], strip_text(result[1])


# # read id


def get_random_char_id(num_chars):
    char_read = {
        "f": "ép",
        "j": random.choice(["giây", "gi"]),
        "z": "dét",
        "b": random.choice(["bê", "bờ"]),
        "c": random.choice(["xê", "cờ"]),
        "d": random.choice(["dê", "đê"]),
        "đ": random.choice(["đê", "đờ"]),
        "g": "gờ",
        "h": random.choice(["hát", "hờ", "hắt"]),
        "k": "ca",
        "l": "lờ",
        "m": "mờ",
        "n": "nờ",
        "p": random.choice(["pê", "pờ"]),
        "q": random.choice(["quy", "quờ"]),
        "r": "rờ",
        "s": random.choice(["ét", "sờ"]),
        "t": random.choice(["tê", "tờ"]),
        "v": random.choice(["vê", "vờ"]),
        "x": random.choice(["ích", "xờ"]),
        "y": "i",
        "w": random.choice(["vê kép", "đắp liu"])
    }
    # print(char_read)
    letters = list('abcdefghijklmnopqrstuvwxyzđ') * num_chars
    char_id = random.choices(letters, k=num_chars)
    read_chars = [i if (char_read.get(i, None) is None) else char_read[i] for i in char_id]
    return ''.join(char_id), ' '.join(read_chars)


def get_random_sep(val=None):
    sep_read = {
        "!": "chấm than",
        "@": "a còng",
        "#": "thăng",
        "$": "đô la",
        "%": "phần trăm",
        "^": "mũ",
        "&": "và",
        "*": "sao",
        "_": "gạch dưới",
        "-": random.choice(["gạch ngang", "ngang", "trừ"]),
        "+": "cộng",
        "=": "bằng",
        "\\": random.choice(["gạch chéo", "chéo", "xuộc", "xoẹt"]),
        "/": random.choice(["gạch chéo", "chéo", "xuộc", "xoẹt"]),
        ":": "hai chấm",
        ";": "chấm phẩy",
        "<": "nhỏ hơn",
        ",": "phẩy",
        ">": "lớn hơn",
        ".": "chấm",
        "?": "hỏi chấm",
        "~": "ngã",
        "": ""
    }
    if val is None or sep_read.get(val, None) is None:
        val = random.choice(list(sep_read.keys()) + [''])
        if len(val) == 0:
            return "", ""
    return val, sep_read[val]


def get_random_id():
    num_1 = get_random_decimal(0, 100, read_single=True)
    num_2 = get_random_decimal(0, 1000, read_single=True)
    char_1 = get_random_char_id(random.randint(1, 5))
    char_2 = get_random_char_id(random.randint(1, 5))
    sep_1 = get_random_sep(val=random.choice(list('/-') + ['']))
    sep_2 = get_random_sep(val=random.choice(list('/-') + ['']))
    sep_3 = get_random_sep(val=random.choice(list('/-') + ['']))

    candidates = [
        ("{}{}{}".format(num_1[0], sep_1[0], char_1[0]), "{} {} {}".format(num_1[1], sep_1[1], char_1[1])),
        ("{}{}{}".format(char_1[0], sep_1[0], num_1[0]), "{} {} {}".format(char_1[1], sep_1[1], num_1[1])),
        ("{}{}{}{}{}".format(num_1[0], sep_1[0], num_2[0], sep_2[0], char_1[0]),
         "{} {} {} {} {}".format(num_1[1], sep_1[1], num_2[1], sep_2[1], char_1[1])),
        ("{}{}{}{}{}".format(char_1[0], sep_1[0], num_2[0], sep_2[0], num_1[0]),
         "{} {} {} {} {}".format(char_1[1], sep_1[1], num_2[1], sep_2[1], num_1[1])),
        ("{}{}{}{}{}".format(char_1[0], sep_2[0], char_2[0], sep_1[0], num_1[0]),
         "{} {} {} {} {}".format(char_1[1], sep_2[1], char_2[1], sep_1[1], num_1[1])),
        ("{}{}{}{}{}".format(num_1[0], sep_1[0], char_1[0], sep_2[0], char_2[0]),
         "{} {} {} {} {}".format(num_1[1], sep_1[1], char_1[1], sep_2[1], char_2[1])),
        ("{}{}{}{}{}{}{}".format(num_1[0], sep_1[0], num_2[0], sep_2[0], char_1[0], sep_3[0], char_2[0]),
         "{} {} {} {} {} {} {}".format(num_1[1], sep_1[1], num_2[1], sep_2[1], char_1[1], sep_3[1], char_2[1])),
    ]

    result = random.choice(candidates)
    return result[0], strip_text(result[1])


def get_random_phone():
    num_1 = get_random_decimal(1000000000, 100000000000, read_single=True)

    candidates = [
        ("{}".format(num_1[0]), "{}".format(num_1[1])),
        ("0{}".format(num_1[0]), "không {}".format(num_1[1])),
        ("+{}".format(num_1[0]), "cộng {}".format(num_1[1])),
    ]

    result = random.choice(candidates)
    return result[0], strip_text(result[1])


def get_random_domain():
    global domain_extension_dict
    global domain_name_dict
    if domain_extension_dict is None:
        domain_extension_dict = []
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'domain_extension.json'), 'r',
                  encoding='utf-8') as file:
            for line in file:
                domain_extension_dict.append(json.loads(line))

    if domain_name_dict is None:
        domain_name_dict = []
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'domain_names.json'), 'r',
                  encoding='utf-8') as file:
            for line in file:
                domain_name_dict.append(json.loads(line))

    len_extension = random.choice([1, 1, 1, 1, 2, 2, 3])
    list_extensions = random.choices(domain_extension_dict, k=len_extension)
    list_extensions = [(item['src'], random.choice(item['tgt'])) for item in list_extensions]

    # domain_name = get_random_oov()
    candidate = random.choice(domain_name_dict)
    tgt = random.choice(candidate['tgt'])
    domain_name = (candidate['src'], tgt)

    middle_domain = random.choice([
        ('www', 'vê kép vê kép vê kép'),
        ('www', 'đáp liu đáp liu đáp liu'),
        ('', ''),
        ('', ''),
        ('', '')
    ])

    if len(middle_domain[0]) > 0:

        tgt_extension = '.'.join([middle_domain[0], domain_name[0]] + [item[0] for item in list_extensions])
        src_extension = ' chấm '.join([middle_domain[1], domain_name[1]] + [item[1] for item in list_extensions])
    else:
        tgt_extension = '.'.join([domain_name[0]] + [item[0] for item in list_extensions])
        src_extension = ' chấm '.join([domain_name[1]] + [item[1] for item in list_extensions])

    begin_domain = random.choice([
        ('http://',
         '{} hai chấm {}'.format(random.choice(['hát tê tê pê',
                                                'hắt tê tê pê',
                                                'hắt ti ti pi',
                                                'hờ tê tê pê']),
                                 random.choice(['gạch chéo gạch chéo',
                                                'chéo chéo'
                                                ])
                                 )
         ),
        ('https://',
         '{} hai chấm {}'.format(random.choice(['hát tê tê pê ét',
                                                'hắt tê tê pê ét',
                                                'hắt ti ti pi ét',
                                                'hờ tê tê pê ét']),
                                 random.choice(['gạch chéo gạch chéo',
                                                'chéo chéo'
                                                ])
                                 )
         ),
        ('', ''),
        ('', ''),
        ('', ''),
    ])

    return begin_domain[0] + tgt_extension, (begin_domain[1] + ' ' + src_extension).strip()


def get_random_email():
    global domain_extension_dict
    if domain_extension_dict is None:
        domain_extension_dict = []
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'domain_extension.json'), 'r',
                  encoding='utf-8') as file:
            for line in file:
                domain_extension_dict.append(json.loads(line))

    len_extension = random.choice([1, 2, 2, 2])
    list_extensions = random.choices(domain_extension_dict, k=len_extension)
    list_extensions = [(item['src'], random.choice(item['tgt'])) for item in list_extensions]

    domain_extension = ('.'.join([item[0] for item in list_extensions]),
                        ' chấm '.join([item[1] for item in list_extensions]))

    domain_extension = random.choice([
        domain_extension,
        ('gmail.com', 'gờ meo chấm com'),
        ('yahoo.com', 'i a hu chấm com'),
        ('outlook.com', 'ao lúc chấm com'),
        ('inbox.com', 'in bóc chấm com'),
        ('icloud.com', random.choice(['ai cơ lao chấm com', 'i cờ lao chấm com'])),
        ('mail.com', 'meo chấm com'),
        ('zoho.com', 'dô hô chấm com')
    ])

    domain_name = get_random_oov()

    tgt_extension = "{}@{}".format(domain_name[0], domain_extension[0])
    src_extension = '{} a còng {}'.format(domain_name[1], domain_extension[1])

    return tgt_extension, src_extension.strip()


def get_random_fraction_form():
    num_1 = get_random_decimal(0, 30, read_single=False)
    num_2 = get_random_decimal(0, 30, read_single=False)
    frac_1 = random.choice(['tỉ số', 'hiệu số', 'vòng', 'giai đoạn'])
    frac_2 = random.choice(['chia', 'trên'])

    float_1 = get_random_float(2, 1, is_positive=True)
    float_2 = get_random_float(2, 1, is_positive=True)

    to_1 = random.choice(['đến', 'tới'])

    candidates = [
        ("{} {} - {}".format(frac_1, num_1[0], num_2[0]), "{} {} {}".format(frac_1, num_1[1], num_2[1])),
        ("{} - {}".format(num_1[0], num_2[0]), "{} {} {}".format(num_1[1], to_1, num_2[1])),
        ("{} / {}".format(num_1[0], num_2[0]), "{} {} {}".format(num_1[1], frac_2, num_2[1])),
        ("{} - {}".format(float_1[0], float_2[0]), "{} {} {}".format(float_1[1], to_1, float_2[1])),
    ]

    result = random.choice(candidates)
    return result[0], strip_text(result[1])


# # Num scale

def get_random_scale(val=None):
    scale_dict = {"%": "phần trăm", "$": "đô la", "euro": random.choice(["êu rô", "ê rô"]),
                  "ngày": "ngày", "m": "mét", "nm": "na nô mét", "g": "gam",
                  "ampe": "am be", "mol": "mon", "cd": "can đê la", "n": "niu tơn", "pa": "bát can",
                  "atm": "át mót phe", "đ": "đồng", "ha": "héc ta", "h": "giờ", "giờ": "giờ", "tháng": "tháng",
                  "năm": "năm", "s": "giây", "giây": "giây", "đồng": "đồng", "ml": "mi li lít",
                  "l": "lít", "lít": "lít", "gb": random.choice(["ghi ga bít", "ghi ga bai"]),
                  "mb": random.choice(["mê ga bít", "mê ga bai"]),
                  "kb": random.choice(["ki lô bít", "ki lô bai"]), "kg": "ki lô gam",
                  "mg": "mi li gam", "m3": "mét khối", "km3": "ki lô mét khối", "dm3": "đề xi mét khối",
                  "cc": "xen ti mét khối", "cm3": "xen ti mét khối", "m2": "mét vuông", "km2": "ki lô mét vuông",
                  "dm2": "đề xi mét vuông", "cm2": "xen ti mét vuông", "mm2": "mi li mét vuông", "km": "ki lô mét",
                  "dm": "đề xi mét", "cm": "xen ti mét", "mm": "mi li mét", "mph": "dặm một giờ",
                  "ft": random.choice(["phuốt", "phít"]),
                  # "kn": "hải lí một giờ",
                  # "nm": "niu tơn mét",
                  "gn": "gi ga niu tơn",
                  # "mn": "mê ga niu tơn",
                  "kn": "ki lô niu tơn",
                  "mn": "mi li niu tơn", "j": "giun", "kj": "ki lô giun", "mj": "mê ga giun",
                  "gj": "gi ga giun", "mw": "mê ga oát", "kw": "ki lo oát", "w": "oát", "wh": "oát giời",
                  "mwh": "mê ga oát giờ", "kwh": "ki lo oát giờ", "mev": "mê ga e lét tron vôn",
                  "ev": "e lét tron vôn", "cal": "ca lo", "kcal": "ki lô ca lo", "oc": "độ xê",
                  "of": "độ ép", "ok": "độ ca", "dp": "đi ốp", "độ": "độ", "wb": "ve bê", "điôp": "đi ốp",
                  "bq": "bét cơ ren", "db": "đề xi ben", "min": "phút", "sec": "giây", "mmhg": "mi li mét thủy ngân",
                  "ma": "mi li âm be", "rad": "ra đi an", "radian": "ra đi an", "hz": "héc", "tấn": "tấn", "lb": "bao",
                  "oz": "ao", "ounce": "ao", "pound": "bao", "carat": "ca ra", "gallon": "ga lon",
                  "gal": "ga lon", "inch": "in", "vnđ": "việt nam đồng", "vnd": "việt nam đồng", "rm": "ring git",
                  "rub": "rúp", "chỉ": "chỉ", "lượng": "lượng", "sào": "sào", "công": "công", "mẫu": "mẫu",
                  "yến": "yến",
                  "tạ": "tạ", "vg": "vòng", "vòng": "vòng", "ph": "phút", "s2": "giây bình phương"}
    if val is None or scale_dict.get(val, None) is None:
        val = random.choice(list(scale_dict.keys()))
    return val, scale_dict[val]


def get_random_num_scale():
    num_int = get_random_decimal(-100, 1000)
    num_float = get_random_float(4, 3)
    scale_1 = get_random_scale()
    scale_2 = get_random_scale()
    candidates = [
                     ("{} {}".format(num_int[0], scale_1[0]), "{} {}".format(num_int[1], scale_1[1])),
                     ("{} {}".format(num_float[0], scale_1[0]), "{} {}".format(num_float[1], scale_1[1])),
                 ] * 2
    candidates_2_scale = [
        ("{} {}/{}".format(num_int[0], scale_1[0], scale_2[0]),
         "{} {} trên {}".format(num_int[1], scale_1[1], scale_2[1])),
        ("{} {}/{}".format(num_float[0], scale_1[0], scale_2[0]),
         "{} {} trên {}".format(num_float[1], scale_1[1], scale_2[1])),
    ]

    result = random.choice(candidates + candidates_2_scale)
    return result[0], strip_text(result[1])


def get_random_span(span_type=None, val=None):
    if span_type is None:
        span_type = random.choice(['oov', 'number', 'date', 'numscale'] * 2 + ['id'])
    if span_type == 'id':
        return get_random_id()
    if span_type == 'email':
        return get_random_email()
    if span_type == 'url':
        return get_random_domain()
    if span_type == 'oov':
        ran_oov = get_random_oov(val)
        if val is not None and ran_oov is not None:
            return ran_oov
        ran = random.random()
        ran_oov = get_random_oov()

        if ran < 0.3:
            candidates = [get_random_domain(), get_random_email(), (ran_oov[0], ran_oov[0])]
            return random.choice(candidates)
        if 0.3 <= ran < 0.6:
            word_in = []
            words = ran_oov[1].split()
            if len(words) > 2:
                for w in words:
                    if random.random() < 0.2:
                        continue
                    else:
                        word_in.append(w)
            else:
                word_in = words
            return ran_oov[0], ' '.join(word_in)
        return ran_oov
    if span_type == 'number':
        ran = random.random()
        if ran < 0.1:
            return get_random_float(5, 4)
        elif 0.1 <= ran <= 0.15:
            return get_random_decimal(min_num=-1000000, max_num=1000000)
        elif 0.15 < ran <= 0.3:
            return get_random_decimal(min_num=0, max_num=100)
        elif 0.3 < ran <= 0.4:
            return get_random_phone()
        elif 0.4 < ran <= 0.5:
            return get_random_fraction_form()
        elif 0.5 < ran <= 0.7:
            return get_random_decimal(min_num=0, max_num=9999999)
        elif 0.7 < ran <= 0.8:
            return get_random_float(2, 2)
        else:
            return get_random_decimal(min_num=-1000, max_num=1000)
    if span_type == 'date':
        if random.random() < 0.3:
            return get_random_time()
        else:
            return get_random_date()
    if span_type == 'numscale':
        return get_random_num_scale()
    if span_type == 'abbrev':
        return get_random_abb(val)


if __name__ == "__main__":
    # print(get_random_decimal(-10000, 10000))
    # print(get_random_float(5, 3))
    # print(get_random_num_scale())
    # for i in range(1000):
    #     print(get_random_decimal(0, 10000))
    # print(get_random_date())
    # print(get_random_time())
    # print(get_random_id())
    # print(get_random_phone())
    # print(get_random_fraction_form())
    # print(get_random_abb("tc"))
    # print(get_general_en_word())
    # print(get_random_oov('pnj'))
    # print(get_random_domain())
    # print(get_random_email())
    # print(get_random_span('oov', 'park'))

    # for i in range(1000):
    #     print(get_random_span("oov"))

    # oov_en = oov_dict
    # for item in oov_dict:
    #     oov_en[item['src']] = item['tgt']

    # oov_general = dict({})
    # list_words = []
    # with open('general_word_en.txt', 'r', encoding='utf-8') as file:
    #     for line in file:
    #         data = json.loads(line)
    #         key = list(data.keys())[0]
    #         oov_en[key] = data[key]
    #
    # with open('en_dict.json', 'w', encoding='utf-8') as file:
    #     json.dump(oov_en, file, ensure_ascii=False, indent=4)

    convert = NumToVnStr(đọc_số_rỗng=True,
                         linh=random.choice(['lẻ', 'linh']),
                         tư=random.choice(['bốn', 'tư']),
                         nghìn=random.choice(['ngàn', 'nghìn']),
                         mươi=random.choice([False, "mươi"]),
                         tỷ=random.choice(['tỷ']),
                         lăm=random.choice(['lăm', 'nhăm', 'năm']))

    print(convert.to_vn_str('2100'))
    print(convert.to_vn_str('2010'))
    print(convert.to_vn_str('2001'))
    print(convert.to_vn_str('8001108'))
    print(convert.to_vn_str('8007001'))
    print(convert.to_vn_str('8001011'))
    print(convert.to_vn_str('2000001'))
    print(convert.to_vn_str('12002000001'))
    print(convert.to_vn_str('12200000000'))
    print(convert.to_vn_str('700000231'))
    print(convert.to_vn_str('1200'))
    print(convert.to_vn_str('5900000'))
    print(convert.to_vn_str('900370200'))
    print(convert.to_vn_str('32000000'))
    print(convert.to_vn_str('400070192'))
    print(convert.to_vn_str('32516000'))
