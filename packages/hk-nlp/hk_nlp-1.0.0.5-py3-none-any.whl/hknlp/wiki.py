import re


def numbering(text):
    i, j = 1, 1
    while True:
        v = re.search("==.+==", text)
        if not v:
            break
        s, e = v.span()
        tar = v.group(0)
        if tar.startswith("==="):
            text = text[:s] + str(j) + ") " + re.sub("=", "", tar).strip() + text[e:]
            j += 1
        elif tar.startswith("=="):
            text = text[:s] + str(i) + ". " + re.sub("=", "", tar).strip() + text[e:]
            i += 1
            j = 1
    return text


def remove_tags(text):
    text = re.sub("<ref.+</ref>", "", text)
    text = re.sub("<[^가-힣][^>]+>", '', text)
    return text


def normalize_numbers(text):
    text = re.sub("'''\{\{NUMBEROFACTIVEUSERS\}\}'''", "N", text)
    text = re.sub("\{\{NUMBER[^\}]+\}\}", "N", text)
    return text


def remain_mathmatics(text):
    while True:
        matched = re.search("(?<=\{\{).?(?=\}\})", text)
        if not matched:
            break
        text = text[:matched.start() - 2] + matched.group(0) + text[matched.end() + 2:]

    while True:
        matched = re.search("(?<=\{\{) ?수학[^\{\}]+(?=\}\})", text)
        if not matched:
            break
        target = re.sub(".+\|", "", matched.group(0))
        text = text[:matched.start() - 2] + target + text[matched.end() + 2:]

    return text


def remove_blanks(text):
    text = re.sub(", +(,|\))", "", text)
    text = re.sub("\(,", "(", text)
    text = re.sub(" , ", '', text)
    text = re.sub("\n{2,}", "\n\n", text)
    text = re.sub("\n[^\w]+\n", "", text)
    text = re.sub(" {2,}", " ", text)
    return text


def remove_brace(text):
    while re.findall("\{\{[^\{\}]+\}\}", text):
        text = re.sub("\{\{[^\{\}]+\}\}", "", text)
    text = re.sub("\{\|.+\|\}", "", text, flags=re.DOTALL)
    return text


def release_square_bracket(text):
    text = re.sub("\[\[파일:[^\[\]]+\]\]", "", text)
    while True:
        matched = re.search("(?<=\[\[)[^\[\]]+(?=\]\])", text)
        if not matched:
            break
        target = re.sub(".+\|", "", matched.group(0))
        target = re.sub("link=", "", target)
        text = text[:matched.start() - 2] + target + text[matched.end() + 2:]
    return text


def useless_text(text):
    text = re.sub('분류:.+', '', text)
    text = re.sub("===? ?같이 보기 ?===?.+\n\n", "", text, flags=re.DOTALL)
    text = re.sub("===? ?참고 문헌 ?===?.+\n\n", "", text, flags=re.DOTALL)
    text = re.sub("===? ?관련[ \w]+===?.+\n\n", "", text, flags=re.DOTALL)
    text = re.sub("===? ?외부 링크 ?===?.+\n\n", "", text, flags=re.DOTALL)
    text = re.sub("===? ?각주 ===?.+\n\n", "", text, flags=re.DOTALL)
    text = re.sub("===? ?같이 보기 ?===?.+\n\n", "", text, flags=re.DOTALL)
    text = re.sub("===? ?출처 ?===?.+\n\n", "", text, flags=re.DOTALL)
    text = re.sub("===? ?사진 ?===?\n?.+\n\n", "", text, flags=re.DOTALL)
    return text


def wiki_text_processing(text):
    if not isinstance(text, str):
        return ""
    text = remove_tags(text)
    text = release_square_bracket(text)
    text = normalize_numbers(text)
    text = remain_mathmatics(text)
    text = remove_brace(text)
    text = re.sub("'''?", "", text)
    text = re.sub("\[http.+\]", "", text)
    text = re.sub("(?<=\n):", "", text)
    text = re.sub("\( ?\)", "", text)
    text = re.sub("‘", "'", text)
    text = re.sub("\t", "", text)
    text = re.sub("\* ?(?=\n)", "", text)
    text = useless_text(text)
    text = numbering(text)
    return text
