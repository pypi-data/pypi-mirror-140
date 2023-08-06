def translit(obj, translit_str_fun):
    if isinstance(obj, str):
        return translit_str_fun(obj)
    if isinstance(obj, dict):
        result = dict()
        for key, value in obj.items():
            result[translit(key, translit_str_fun)] = translit(value, translit_str_fun)
        return result
    if isinstance(obj, list):
        return map(lambda x: translit(x, translit_str_fun), obj)
    return obj
    
def translit_str(str, translit_letter_fun):
    return "".join(map(translit_letter_fun, str))

def cyr_to_lat(obj):
    def cyr_to_lat_letter(letter):
        f = {"а":"a", "б":"b",  "в":"v", "г":"g",  "д":"d",
             "ђ":"đ", "е":"e",  "ж":"ž", "з":"z",  "и":"i",
             "ј":"j", "к":"k",  "л":"l", "љ":"lj", "м":"m",
             "н":"n", "њ":"nj", "о":"o", "п":"p",  "р":"r",
             "с":"s", "т":"t",  "ћ":"ć", "у":"u",  "ф":"f",
             "х":"h", "ц":"c",  "ч":"č", "џ":"dž", "ш":"š",
             "А":"A", "Б":"B",  "В":"V", "Г":"G",  "Д":"D",
             "Ђ":"Đ", "Е":"E",  "Ж":"Ž", "З":"Z",  "И":"I",
             "Ј":"J", "К":"K",  "Л":"L", "Љ":"Lj", "М":"M",
             "Н":"N", "Њ":"Nj", "О":"O", "П":"P",  "Р":"R",
             "С":"S", "Т":"T",  "Ћ":"Ć", "У":"U",  "Ф":"F",
             "Х":"H", "Ц":"C",  "Ч":"Č", "Џ":"Dž", "Ш":"Š"}
        return f[letter] if letter in f else letter
    cyr_to_lat_str = lambda str: translit_str(str, cyr_to_lat_letter)
    return translit(obj, cyr_to_lat_str)

def lat_to_cyr(obj):
    f = {"a":"а", "b":"б",  "v":"в", "g":"г",  "d":"д",
         "đ":"ђ", "e":"е",  "ž":"ж", "z":"з",  "i":"и",
         "j":"ј", "k":"к",  "l":"л", "lj":"љ", "m":"м",
         "n":"н", "nj":"њ", "o":"о", "p":"п",  "r":"р",
         "s":"с", "t":"т",  "ć":"ћ", "u":"у",  "f":"ф",
         "h":"х", "c":"ц",  "č":"ч", "dž":"џ", "š":"ш",
         "A":"А", "B":"Б",  "V":"В", "G":"Г",  "D":"Д",
         "Đ":"Ђ", "E":"Е",  "Ž":"Ж", "Z":"З",  "I":"И",
         "J":"Ј", "K":"К",  "L":"Л", "Lj":"Љ", "M":"М",
         "N":"Н", "Nj":"Њ", "O":"О", "P":"П",  "R":"Р",
         "S":"С", "T":"Т",  "Ć":"Ћ", "U":"У",  "F":"Ф",
         "H":"Х", "C":"Ц",  "Č":"Ч", "Dž":"Џ", "Š":"Ш"}
    
    def lat_to_cyr_letter(letter):
        return f[letter] if letter in f else letter

    def lat_to_cyr_str(str):
        letters = []
        i = 0
        while i < len(str):
            letter = str[i]
            i += 1
            if i < len(str) and (letter + str[i]) in f:
                letter += str[i]
                i += 1
            letters.append(letter)
        return "".join(map(lat_to_cyr_letter, letters))

    return translit(obj, lat_to_cyr_str)

if __name__ == '__main__':
    print(cyr_to_lat("Здраво, zdravo!"))
    print(lat_to_cyr("Injekcija! Nadživeti."))
