def get_correct_number(number, range=True):
    for el in number:
            if el in "1234567890":
                continue
            elif range and el == ":":
                 continue
            else:
                number = number.replace(el, "")
    
    return number

def is_range(number):
    err = -1
    for el in number:
        if el == ":":
            err += 1
        elif number[0] == ":" or number[-1] == ":":
            err += 1

    return err == 0

def breaking_range(item, chapters):
    chapters_range = item.split(':')
    min, max = chapters_range
    min, max = int(min), int(max)
    if min > max:
        min, max = max, min
    for i in range(min, max+1):
        chapters.append(i)

def get_correct_sorted_chapters(user_string, chapters):
    splited_string = user_string.split(',')
    for num, number in enumerate(splited_string):
        number = get_correct_number(number, is_range(number))
        splited_string[num] = number
        if number == "":
            splited_string.remove("")
        elif number == " ":
            splited_string.remove(" ")
     
    for item in splited_string:
        if ":" in item:
            breaking_range(item, chapters)
        else: 
            item = int(item)
            chapters.append(item)

    sorted_chapters = sorted(list(set(chapters)))
    if sorted_chapters[0] == 0:
        sorted_chapters.remove(0)

    return sorted_chapters

def main():
    user_string = "1daf.f2,23:2,24ss:, ,0"
    # user_string = input("Введите значения: ")
    chapters = []
    sorted_chapters = get_correct_sorted_chapters(user_string, chapters)
    print(sorted_chapters)

if __name__ == "__main__":
    main()
