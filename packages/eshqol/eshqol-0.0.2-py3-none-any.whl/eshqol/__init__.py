def bigger_than_5(num: int):
    return num > 5


def bigger_than_10(num: int):
    return num > 10


def check_if_sort(lst: list):
    return sorted(lst) == lst


def get_folder_name(s: str):
    return s.split('/')[-2]


def encode_string(s: str):
    return s.encode()


def shuffle_the_name(s: str):
    name, last_name = s.split()
    return last_name + ' ' + name


def is_even(num: int):
    return not num % 2


def is_odd(num: int):
    return num % 2


def remove_none(lst: list):
    return [x for x in lst if x is not None]


def find_even_nums(n: int):
    return [x for x in range(2, n + 1) if not x % 2]


def only_positive(lst: list):
    return [x for x in lst if x > 0]


def squares_sum(n: int):
    return sum([x ** 2 for x in range(n + 1)])


def widen_the_string(s: str):
    return ' '.join(list(s))


def get_middle_digit(num: int):
    return num % 100 // 10


def is_int(st: str):
    return st.lstrip("-").isdigit()


def last_in_list(lst: list):
    return lst[-1]


def length_of_string(st: str):
    return len(st)


def check_duplicate(lst: list):
    return len(set(lst)) != len(lst)


def largest_element(lst: list):
    return max(lst)


def seven_in_list(lst: list):
    return 7 in lst


def sum_of_lst(lst: list):
    return sum(lst)


def one_to_thirty():
    return [x for x in range(1, 31)]


def num_average(n1: int, n2: int, n3: int):
    return (n1 + n2 + n3) / 3


def is_divisible(num1: int, num2: int):
    return not num1 % num2


def reverse_lst(lst: list):
    return lst[::-1]


def slice_in_half(lst: list):
    return lst[: len(lst) // 2]


def make_sentence(lst: list):
    return " ".join(lst)


def hours_to_minutes(hour: float):
    return hour * 60


def factorial(num: int):
    fact = 1
    for x in range(1, num + 1):
        fact *= x
    return fact


def count_in_list(lst: list):
    return lst.count('c')


def replace_list(lst: list):
    for index in range(len(lst)):
        if lst[index] == 0:
            lst[index] = 1
    return lst


def upper_cases(word: str):
    return word.upper()


def lower_cases(word: str):
    return word.lower()


def strip_word(word: str):
    return word.strip()


def is_uppercase(word: str):
    return word.isupper()


def join_list(lst: list):
    return ','.join(lst)


def who_is_bigger(a: int, b: int):
    return max(a, b)


def length_of_number(num: int):
    return len(str(num))


def dictionary_len(d: dict):
    return len(d)


def get_dictionary(d: dict):
    return d['1']


def add_dictionary(d: dict):
    d['number'] = 5
    return d


def square_root(num: int):
    return num ** 0.5


def power_by_number(num: int):
    return 3 ** num


def perfect_square(num: int):
    return num ** 0.5 == int(num ** 0.5)


def title_str(st: str):
    return st.title()


def is_binary(st: str):
    return set(st.replace('1', '0')) == {'0'}


def string_int(st: str):
    return int(st)


def subtraction_of_lists(lst1: list, lst2: list):
    return [lst1[x] - lst2[x] for x in range(len(lst1))]


def boolean_to_string(flag: bool):
    return str(flag)


def list_of_multiples(num: int, length: int):
    return [num * x for x in range(1, length + 1)]


def int_or_float(num):
    return type(num) == int


def one_three_nine(n: int):
    return n, n // 3, n // 9


def pythagoras(x1: float, x2: float):
    return (x1 ** 2 + x2 ** 2) ** 0.5


def count_spaces(words: str):
    return words.count(' ')


def longest_time(h: int, m: int, s: int):
    if h * 60 > m and h * 3600 > s:
        return h
    if m * 60 > s:
        return m
    return s


def less_than_100(num1: int, num2: int):
    return num1 + num2 < 100


def largest_even(lst: list):
    biggest = -1
    for n in lst:
        if n > biggest and not n % 2:
            biggest = n
    return biggest


def last_b(s: str):
    index = s.rfind('b')
    if index >= 0:
        return index


def is_repdigit(num: int):
    return len(set(str(num))) == 1


def add_indexes(lst: list):
    return [x + lst[x] for x in range(len(lst))]


def alphabet_soup(text: str):
    return ''.join(sorted(text))


def card_hide(card: str):
    k = len(card)
    return '*' * (k - 4) + card[k - 4:]


def index_of_caps(st: str):
    return [x for x in range(len(st)) if st[x].isupper()]


def absolute(number: int):
    return abs(number)


def amplify(n: int):
    return [x if x % 4 else x * 10 for x in range(1, n + 1)]


def unique_number(lst: list):
    for n in set(lst):
        if lst.count(n) == 1:
            return n


def equality_of_3(a, b, c):
    if a == b and b == c and a == c:
        return 3
    if a == b or b == c or a == c:
        return 2
    return 0


def folding_paper(n: int):
    return 0.5 * 2 ** n


def negative_number(n: int):
    return n < 0


def true_or_false(arg: any):
    return bool(arg)


def seperate_string(s: str):
    return ''.join([x for x in s if not x.isdigit()])


def remove_from_list(lst: list):
    return [x for x in lst if x > 50]


def all_truthy(lst: list):
    return all(lst)


def invert_list(lst: list):
    return [x * -1 for x in lst]


def is_empty(s: str):
    return s == ''


def evenly_divisible(a: int, b: int, c: int):
    return sum([x for x in range(a, b + 1) if not x % c])


def number_split(n: int):
    return [n // 2, n - n // 2]


def find_none(lst: list):
    if None in lst:
        return lst.index(None)
    return -1


def can_nest(lst1: list, lst2: list):
    return min(lst1) > min(lst2) and max(lst1) < max(lst2)


def rotate_by_one(lst: list):
    return lst[-1:] + lst[:-1]


def is_safe_bridge(s: str):
    return set(s) == {'#'}


def leap_year(year: int):
    if year % 4:
        return False
    if not year % 100:
        return not year % 400
    return True


def get_word(left: str, right: str):
    return (left + right).capitalize()


def add_nums(nums: str):
    lst = nums.split(', ')
    return sum([int(x) for x in lst])


def volume_of_box(sizes: dict):
    import math
    return math.prod(sizes.values())


def is_in_range(n: int, r: dict):
    return r['min'] <= n <= r['max']


def n_tables_plus_one(num: int):
    lst = [str(x * num + 1) for x in range(1, 11)]
    return ','.join(lst)


def add_ending(lst: list, ending: str):
    return [x + ending for x in lst]


def unlucky_13(nums: list):
    return [x for x in nums if x % 13]


def filter_digit_length(lst: list, num: int):
    return [x for x in lst if len(str(x)) == num]


def mirror(lst: list):
    k = lst[:-1]
    return lst + k[::-1]


def get_decimal_places(n: float):
    try:
        return len(str(n).split('.')[1])
    except IndexError:
        return 0


def double_letters(word: str):
    return any(letter * 2 in word for letter in word)


def not_not_not(n: int, b: bool):
    return n % 2 != b


def sub_reddit(link: str):
    return link.split('/')[-2]


def is_avg_whole(lst: list):
    average = sum(lst) / len(lst)
    return average == int(average)


def hello_world():
    return 'Hello World!'


def flip_boolean(var):
    if isinstance(var, bool):
        return not var
    return 'invalid'


def integer_boolean(n: str):
    return [True if x == '1' else False for x in n]


def decimal_to_binary(dec: int):
    return str(format(dec, '2b'))


def is_palindrome(word: str):
    return word == word[::-1]


def longest_word(sentence: str):
    lst = sentence.split()
    return sorted(lst, key=len)[-1]


def fibonacci_numbers(n: int):
    current = 0
    next = 1
    for i in range(n):
        current, next = next, current + next
    return current


def filter_odds(lst: list):
    return [x for x in lst if not x % 2]


def number_formatting(num: int):
    return format(num, ',d')


def sum_odd_and_even(lst: list):
    odd = sum([x for x in lst if x % 2])
    return [sum(lst) - odd, odd]


def count_solution(a: float, b: float, c: float):
    root = b ** 2 - 4 * a * c
    if root > 0:
        return 2
    if root < 0:
        return 0
    return 1


def get_indexes(lst: list, n: int):
    return [x for x in range(len(lst)) if lst[x] == n]


def sum_of_primes(n: int):
    sum = 0
    for i in range(2, n + 1):
        if isPrime(i):
            sum += i
    return sum


def see_the_sun(lst: list):
    sum = 1
    for i in range(1, len(lst)):
        if max(lst[:i]) < lst[i]:
            sum += 1
    return sum


def delete_java(lst: list):
    return [x for x in lst if x.split('.')[1] != 'java']


def almost_last(s: str):
    return s[:s.rfind('1')].rfind('1')


def power(x: float, n: int):
    return x ** n


def triplet_sum_array(lst: list, num: int):
    from itertools import combinations
    all_possibles = combinations(lst, 3)
    for possible in all_possibles:
        if sum(possible) == num:
            return True
    return False


def get_abs_sum(nums: list):
    return sum([abs(x) for x in nums])


def add_binary(bin1: str, bin2: str):
    return format(int(bin1, 2) + int(bin2, 2), '2b')


def string_product(s1: str, s2: str):
    return toInt(s1) * toInt(s2)


def toInt(string: str) -> int:
    value = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9}
    result = 0
    for digit in string:
        result = 10 * result + value[digit]
    return result


def sum_of_digits(num: int):
    if num < 10:
        return num
    return sum_of_digits(sum([int(x) for x in str(num)]))


def queen_attack(q: tuple, e: tuple):
    if q[0] == e[0] or q[1] == e[1]:
        return True
    if abs(q[0] - q[1]) == abs(e[0] - e[1]):
        return True
    return False


def string_and_integer(obj):
    if isinstance(obj, int):
        return str(obj)
    return int(obj)


def correct_signs(expression: str):
    return eval(expression)


def majority_vote(lst: list):
    for item in lst:
        if lst.count(item) > len(lst) / 2:
            return item


def validate_pin(pin: str):
    n = len(pin)
    return pin.isdigit() and n in [4, 6] and n == len(set(pin))


def sum_missing_numbers(lst: list):
    return sum(range(min(lst), max(lst) + 1)) - sum(lst)


def palindrome_number(num: int):
    lst = []
    while num > 0:
        lst.append(num % 10)
        num //= 10
    return lst == lst[::-1]


def merge_lists(lst1: list, lst2: list):
    return sorted(lst1 + lst2)


def binary_to_decimal(binary: str):
    return int(binary, 2)


def single_number(nums: list):
    return sorted(nums, key=lambda x:nums.count(x))[0]


def valid_anagram(s: str, t: str):
    return sorted(s) == sorted(t)


def perfect_number(n: int):
    return n == sum([x for x in range(1, n) if not n % x])


def face_interval(nums: list):
    if max(nums) - min(nums) in nums:
        return ":)"
    else:
        return ":("


def largest_gap(lst: list):
    lst.sort()
    return max(b - a for a, b in zip(lst, lst[1:]))


def match_last_item(lst):
    return ''.join(str(i) for i in lst[:-1]) == lst[-1]


def num_of_sublists(lst: list):
    count = 0
    for i in lst:
        if type(i) == list:
            count += 1
    return count


def is_pandigital(n: int):
    return len(set(str(n))) == 10


def common_divisor(a: int, b: int):
    for i in reversed(range(a + 1)):
        if not a % i and not b % i:
            return i


def payment_price(price: int):
    total = 0
    while price > 0:
        for item in [200, 50, 10, 1]:
            if price >= item:
                price -= item
                break
        total += 1
    return total


def cube_diagonal(vol: float):
    edge = vol ** (1 / 3)
    cube_root = 3 ** (1 / 2)
    return round(edge * cube_root, 2)


def sum_fractions(lst: list):
    s = [n / d for n, d in lst]
    return round(sum(s))


def stupid_addition(a, b):
    if type(a) == type(b):
        if type(a) == int:
            return str(a) + str(b)
        return int(a) + int(b)


def rearranged_difference(n: int):
    x = ''.join(sorted(str(n)))
    return int(x[::-1]) - int(x)


def sale_price(p: float, s: int):
    return p / (1 - s / 100)


def shared_letters(st1: str, st2: str):
    lst = [x for x in st1 if x in st2]
    return len(lst)


def dict_to_list(d: dict):
    return [[x, d[x]] for x in d]


def bank_security(s: str):
    s = s.replace('x', '')
    return not ("$T" in s or "T$" in s)


def duplicates(s: str):
    return len(s) - len(set(s))


def greater_than_sum(nums):
    return all(nums[i] > sum(nums[:i]) for i in range(1, len(nums)))


def is_automorphic(n: int):
    return str(n ** 2).endswith(str(n))


def sort_by_length(lst: list):
    return sorted(lst, key=len)


def num_args(*args):
    return len(args)


def is_harshad(n: int):
    s = sum([int(x) for x in str(n)])
    return not n % s


def square_patch(n: int):
    sub = [n for x in range(n)]
    return [sub for x in range(n)]


def one_char_diff(str1: str, str2: str):
    total = 0
    for s1, s2 in zip(str1, str2):
        if s1 != s2:
            total += 1
    return total == 1


def smiley_faces(s: str):
    happy = s.count(':)') + s.count('(:')
    sad = s.count(':(') + s.count('):')
    return happy, sad


def len(object: any):
    length = 0
    for item in object:
        length += 1
    return length


def fact_of_fact(n: int):
    m = 1
    for i in range(1, n + 1):
        m *= (n + 1 - i) ** i
    return m


def double_swap(txt, c1, c2):
    return "".join(c1 if i == c2 else c2 if i == c1 else i for i in txt)


def sum_is_equal(lst: list):
    return sum(int(x) for x in str(lst[0])) == sum(int(x) for x in str(lst[1]))


def cap_space(txt):
    return ''.join([ch if ch.islower() else ' ' + ch.lower() for ch in txt])


def valid_division(d: str):
    try:
        return eval(d) == int(eval(d))
    except:
        return "invalid"


def camel_case(s: str):
    st = ""
    words = s.split(" ")
    for i in range(len(words)):
        if i == 0:
            st += (words[0].lower())
        else:
            st += words[i].title()
    return st


def de_nest(lst: list):
    return eval("".join([x for x in str(lst) if x not in "[]"]))


def is_exactly_three(n: int):
    return len([x for x in range(1, n + 1) if n % x == 0]) == 3


def intersection(nums1: list, nums2: list):
    return list(sorted(set(x for x in nums1 if x in nums2)))


def remove_letters(letters: list, word: str):
    return [x for x in letters if x not in word]


def expensive_orders(d: dict, p: dict):
    return {k:v for k, v in d.items() if v > p}


def decimal_to_roman(number):
    num = [1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1000]
    sym = ["I", "IV", "V", "IX", "X", "XL", "L", "XC", "C", "CD", "D", "CM", "M"]
    i = 12
    roman = ""
    while number:
        div = number // num[i]
        number %= num[i]
        while div:
            roman += sym[i]
            div -= 1
        i -= 1
    return roman


def consecutive_combo(lst1, lst2):
    lst3 = lst1 + lst2
    return max(lst3) - min(lst3) == len(lst3) - 1


def mark_maths(lst: list):
    s = []
    for x in lst:
        x = x.replace('=', '==')
        s.append(eval(x))
    percentage = (s.count(True) / len(s)) * 100
    return str(round(percentage)) + '%'


def plus_sign(txt: str):
    s = ' ' + txt + ' '
    for i in range(len(s)):
        if s[i].isalpha():
            if s[i + 1] != '+' or s[i - 1] != '+':
                return False
    return True


def is_center(s: str):
    return s == s[::-1]


def invert_dict(d: dict):
    return {d[key]:key for key in d}


def bigger_number(a: int, b: int):
    sub = a - b
    if not sub:
        return None
    if not abs(sub) - sub:
        return a
    return b


def next_letter(word: str):
    from string import ascii_letters as s
    for i in reversed(range(26)):
        word = word.replace(s[i], s[i + 1])
    return word


def move_zeroes(lst: list):
    a = [x for x in lst if x != 0]
    b = [x for x in lst if x == 0]
    return a + b


def concat(*args):
    a = []
    for lst in args:
        a += lst
    return sorted(a)


def correct_expression(expression: str):
    return eval(expression)


def area_of_triangle(dot1: str, dot2: str, dot3: str):
    x1, y1 = dot1[1:-1].split(',')
    x2, y2 = dot2[1:-1].split(',')
    x3, y3 = dot3[1:-1].split(',')
    x1, x2, x3, y1, y2, y3 = float(x1), float(x2), float(x3), float(y1), float(y2), float(y3)
    return round(0.5 * abs(x1 * (y3 - y2) + x2 * (y1 - y3) + x3 * (y2 - y1)), 10)


def time_saved(lim, avg, d):
    return round((d / lim - d / avg) * 60, 1)


def digit_occurrences(start, end, digit):
    s = ''.join(str(i) for i in range(start, end + 1))
    return s.count(str(digit))


def free_throws(success: str, rows: int):
    return format((int(success[:-1]) / 100) ** rows, '.0%')


def median(nums):
    m = len(nums) // 2
    return (nums[-(m + 1)] + nums[m]) / 2


def median1(nums):
    from statistics import median
    return median(nums)


def balanced(lst):
    h1, h2 = sorted((lst[:len(lst) // 2], lst[len(lst) // 2:]), key=sum)
    return lst if sum(h1) == sum(h2) else h2 * 2


def match_by2char(a, b):
    return sum([1 for i in range(len(a) - 1) if a[i:i + 2] == b[i:i + 2]])


def minimize_the_sum(a: list, b: list):
    a = sorted(a)
    b = sorted(b, reverse=True)
    s = 0
    for i in range(len(a)):
        s += a[i] * b[i]
    return s


def form_divisible_by_3(lst: list):
    extra = 0
    for number in lst:
        extra += number % 3
    return not extra % 3


def word_builder(ltr: list, pos: list):
    return ''.join(ltr[i] for i in pos)


def extend_vowels(word: str, num: int):
    for x in 'aieouAIEOU':
        word = word.replace(x, x * (num + 1))
    return word


def get_type(value):
    return type(value).__name__


def smallest_n(n: int, value: int):
    base = 10 ** (n - 1)
    mode = base % value
    if mode == 0:
        return base
    return base + (value - mode)


def count_digits(n: int, k: int):
    lst = [str(x ** 2) for x in range(n + 1)]
    return ''.join(lst).count(str(k))


def nth_smallest(lst: list, n: int):
    try:
        return sorted(lst)[n - 1]
    except IndexError:
        pass


def abundant_number(num: int):
    return sum(x for x in range(1, num) if not num % x) > num


def partition(s: str, n: int):
    lst = []
    while s != '':
        lst.append(s[:n])
        s = s[n:]
    return lst


def to_ascii(c: str):
    try:
        return ord(c)
    except TypeError:
        return 'invalid'


def cap_last(txt: str):
    lst = txt.split()
    for i in range(len(lst)):
        lst[i] = lst[i][:-1] + lst[i][-1].upper()
    return ' '.join(lst)


def check_square_and_cube(lst: list):
    a, b = lst
    return round(a ** (1 / 2), 10) == round(b ** (1 / 3), 10)


def secret_function_1(text: str):
    a, n = text.split('*')
    return f"<{a}></{a}>" * int(n)


def secret_function_2(txt: str):
    lst = txt.split('.')
    a, b = lst[0], ' '.join(lst[1:])
    return f"<{a} class='{b}'></{a}>"


def revers_sentence(s: str):
    return '.'.join(s.split('.')[::-1])


def secret_function_3(n: int):
    """
	This function will return the sum of digit
	of a number in his binary form
	"""
    return str(bin(n)).count('1')


def secret_function_4(s: str):
    """
	This function will return the sum of
	ascii codes for each char in a string
	"""
    return sum(ord(x) for x in s)


def deepest_sublist(lst: list):
    if type(lst) != list: return 0
    return 1 + max(deepest_sublist(e) for e in lst)


def prime_factors(num: int):
    lst = []
    while num != 1:
        for i in range(2, num):
            while not num % i:
                lst.append(i)
                num = num / i
    return lst


def tic_tac_toe(text: str):
    c = [list(i) for i in zip(*text)]
    dlr = [[text[0][0], text[1][1], text[2][2]]]
    drl = [[text[2][0], text[1][1], text[0][2]]]
    for i in text + c + dlr + drl:
        if set(i) == {'X'}:
            return 'X'
        elif set(i) == {'O'}:
            return 'O'
    return "Draw"


def is_prime(num):
    if num < 2:
        return False
    return all(num % x for x in range(2, int(num ** 0.5 + 1)))


def bin_to_septenary(a: str):
    return toSeven(int(a, 2), [])


def toSeven(n, a):
    if n > 1:
        toSeven(n // 7, a)
    a.append(str(n % 7))
    return str(int(''.join(a)))


def valid_parentheses(s: str):
    brackets = ['()', '{}', '[]']
    while any(x in s for x in brackets):
        for b in brackets:
            s = s.replace(b, '')
    return not s


def nodes_network(nodes: list, current: str, target: str):
    for node in nodes:
        if node[0] == current:
            nodes.remove(node)
            if target in node[1:]:
                return True
            for t in node[1:]:
                if nodes_network(nodes, t, target):
                    return True
    return False


class equals:
    def __eq__(self, other):
        return True


def gimme_the_letters(s: str):
    s, f = s.split("-")
    if ord(s) <= ord(f):
        return "".join(chr(i) for i in range(ord(s), ord(f) + 1))
    start_to_end = "".join(chr(i) for i in range(ord(s), ord("z") + 1))
    end_to_start = "".join(chr(i) for i in range(ord("a"), ord(f) + 1))
    return start_to_end + end_to_start


def rotate_list(lst: list, k: int):
    for i in range(k):
        lst.insert(0, lst.pop())
    return lst


def nearest_multiple_of_10(n: str):
    a, b = int(n[:-1]), int(n[-1])
    if b > 5:
        return a * 10 + 10
    return a * 10


def bed_time(*times):
    res = []
    for wake, duration in times:
        h = int(wake[:2]) - int(duration[:2])
        s = int(wake[-2:]) - int(duration[-2:])
        res.append('{:02}:{:02}'.format((h - 1) % 24 if s < 0 else h % 24, s % 60))
    return res


def all_possibilities(lst: list, k: int):
    pos = set()
    n = len(lst)
    helper(lst, "", n, k, pos)
    return pos


def helper(st, prefix, n, k, pos):
    if k == 0:
        pos.add(prefix)
        return
    for i in range(n):
        newPrefix = prefix + st[i]
        helper(st, newPrefix, n, k - 1, pos)


def equation_solver(equation: str):
    s = equation.replace('x', 'j')
    s = s.replace('=', '-(') + ')'
    z = eval(s, {'j':1j})
    solution = z.real / -z.imag
    return int(str(solution).split('.')[0])


def only_5_and_3(n):
    if n in [3, 5]:
        return True
    if n < 3:
        return False
    return only_5_and_3(n - 5) or only_5_and_3(n / 3)


def divide_two_integers(dividend: int, divisor: int):
    x = abs(dividend)
    y = abs(divisor)
    quotient = 0
    while x >= y:
        x = x - y
        quotient = quotient + 1
    return quotient


def reorder(n: int):
    from itertools import permutations as p
    from math import log2
    for x in p(str(n)):
        x = ''.join(x)
        if log2(int(x)).is_integer():
            if x[0] != '0':
                return True
    return False


def complete_binary(s: str):
    return "0" * (8 - len(s) % 8) + s if len(s) % 8 else s


def ramp(lst: list):
    final = -1
    n = len(lst)
    for i in range(n):
        for j in range(i, n):
            if lst[i] <= lst[j]:
                final = max(j - i, final)
    return final


def substring_length(s: str):
    mx = 0
    for i in range(len(s) - 1):
        count = 1
        lst = [s[i]]
        x = i + 1

        while x < len(s) and s[x] not in lst:
            lst.append(s[x])
            count += 1
            x += 1
        mx = max(count, mx)

    return mx


def sorting(string: str):
    return ''.join(sorted(string, key=lambda x:helper1(x)))


def helper1(s: str):
    if s.isdigit():
        return int(s) + 200
    if s.islower():
        return ord(s)
    return ord(s) + 32.5


def maximum_subarray(a: list):
    final = a[0]
    temp = a[0]

    for i in range(1, len(a)):
        temp = max(a[i], temp + a[i])
        final = max(final, temp)

    return final


def word_pattern(pattern: str, s: str):
    words = s.split()
    if len(pattern) != len(words):
        return False
    forbidden = []
    for x in range(len(pattern)):
        key = pattern[x]
        if not key in forbidden:
            s = s.replace(words[x], key)
            forbidden.append(key)

    return pattern == s.replace(' ', '')


def decode_string(s: str):
    curr, num, ltr = [], [], []
    n = 0
    for c in s:
        if c.isdigit():
            n = n * 10 + ord(c) - ord('0')
        elif c == '[':
            num.append(n)
            n = 0
            ltr.append(curr)
            curr = []
        elif c == ']':
            ltr[-1].extend(curr * num.pop())
            curr = ltr.pop()
        else:
            curr.append(c)
    return "".join(ltr[-1]) if ltr else "".join(curr)


def sudoku(board: list):
    import numpy as np

    if any(f(board[r]) or f(np.rot90(board)[r]) for r in range(9)):
        return False

    for i in range(9):
        if f(board[i]):
            return False

    lst = [[x * 3, y * 3] for x in range(3) for y in range(3)]

    for x, y in lst:
        if f(sum([item[y:y + 3] for item in board[x: x + 3]], [])):
            return False
    return True


def f(lst: list):
    s = [x for x in lst if x != '.']
    return len(set(s)) != len(s)


def prime_at_prime(lst: list):
    return all(isPrime(lst[x]) for x in range(len(lst)) if isPrime(x))


def isPrime(n: int):
    if n < 2:
        return False
    return all(n % x for x in range(2, n))
