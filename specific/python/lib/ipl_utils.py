import os
import sys
import re
import cid_trans


def is_skipped_line(line):
    # ページ番号表記
    if re.match(r"^\d+ 特$", line) or re.match(r"^\d+ 特 許$", line) or line=="許" or line=="法":
        return True
    if re.match(r"^特 許 法 \d+", line):
        return True
    # 内部間利用?フッター
    if re.match(r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}  v\d.\d{2}", line):
        return True
    if re.match(r"^\d{2}-\d{2}-\d{3}　.*?  Page ([0-9]+)$", line):
        return True
    # 空行
    if len(line) == 0:
        return True
    else:
        return False

def make_trans():
    return str.maketrans({
        '︑':'、',
        '︒':'。',
        '︵':'（',
        '︶':'）',
        '︹':'［',
        '︺':'］',
        '︿':'＜',
        '﹀':'＞'
    })

def replace_line(line, trans, opt=None):
    line = line.translate(trans)
    line = cid_trans.cid_trans(line)
    return line

def conversion_text(pages):
    result = []
    trans = make_trans()
    for page in pages:
        out_obj = {
            "page_number": page["page_number"],
            "lines": []
        }
        for in_line in page["lines"]:
            if is_skipped_line(in_line):
                continue
            out_line = replace_line(in_line, trans)
            if 0 < len(out_line):
                out_obj["lines"].append(out_line)
        if 0 < len(out_obj["lines"]):
            result.append(out_obj)
    return result


def make_number_trans():
    return str.maketrans({
        '一':'1',
        '二':'2',
        '三':'3',
        '四':'4',
        '五':'5',
        '六':'6',
        '七':'7',
        '八':'8',
        '九':'9',
        '〇':'0'
    })

def extract_kamji_number_title(line, type, additional_re=" "):
    return re.match(f"^第([一二三四五六七八九〇]+)({type})(の[一二三四五六七八九〇]+)?{additional_re}", line)

def extract_kamji_number_title1(line, type, additional_re=" "):
    return re.match(f"^第([一二三四五六七八九〇]+)({type}){additional_re}", line)

def extract_kamji_number_title2(line, type, additional_re=" "):
    return re.match(f"^第([一二三四五六七八九〇]+)({type})(の[一二三四五六七八九〇]+){additional_re}", line)

def extract_kamji_number_title3(line, type, additional_re=" "):
    return re.match(f"^第([一二三四五六七八九〇]+)({type})(の[一二三四五六七八九〇]+)(の[一二三四五六七八九〇]+){additional_re}", line)

def extract_attribute(line, prev_line, current_article, next_article, page_index, line_index, trans, current_id_str_obj):
    done = False
#    print(f">> {line} <<")
    m_chapter = extract_kamji_number_title(line, "章")
    m_section = extract_kamji_number_title(line, "節")
    m_article1 = extract_kamji_number_title1(line, "条")
    m_article2 = extract_kamji_number_title2(line, "条")
    m_article3 = extract_kamji_number_title3(line, "条")
    m_caption = re.match(r"（(.*?)）(（.*)?([実意商]*)(.*)", line)

    if m_chapter:
#        print(m_chapter.groups())
        chapter_number = m_chapter.groups()[0].translate(trans)
        if 2 < len(m_chapter.groups()) and m_chapter.groups()[2] is not None:
            print(m_chapter.groups())
            chapter_sub_number = m_chapter.groups()[2].replace("の","").translate(trans)
            current_id_str_obj.update({"id":f"Mp-Ch_{chapter_number}_{chapter_sub_number}"})
        else:
            current_id_str_obj.update({"id":f"Mp-Ch_{chapter_number}"})
        print(json.dumps(line, ensure_ascii=False))
    elif m_section:
#        print(f' {m_section.group()}')
        base_str = current_id_str_obj["id"]
        if "-Se" in current_id_str_obj["id"]:
            base_str = current_id_str_obj["id"].split("-Se")[0]
        section_number = m_section.groups()[0].translate(trans)
        base_str += f"-Se_{section_number}"
        current_id_str_obj.update({"id":base_str})
        print(json.dumps(line, ensure_ascii=False))
        print(current_id_str_obj["id"])
    elif m_caption:
        pass
    elif m_article1 or m_article2 or m_article3:
        if m_article1:
            m_article = m_article1
        elif m_article2:
            m_article = m_article2
        else:
            m_article = m_article3

        m_caption = re.match(r"（(.*?)）(（.*)?([実意商]*)(.*)", prev_line)
        if m_caption:
            rev_hist = ""
            if m_caption.groups()[1] is not None:
                rev_hist = m_caption.groups()[1]
            if 0 < len(m_caption.groups()[3]):
                rev_hist = m_caption.groups()[3]

            done = True
            id_str = str(current_id_str_obj["id"])
            article_number = int(m_article.groups()[0].translate(trans), 10)
            id_str += f"-At_{article_number}"
            article_sub_number = 0
            if 2 < len(m_article.groups()):
                article_sub_number_str = m_article.groups()[2].replace("の","").translate(trans) if m_article.groups()[2] else "1"
                article_sub_number = int(article_sub_number_str, 10)
                id_str += f"_{article_sub_number}"
            article_sub_sub_number = 0
            if 3 < len(m_article.groups()):
                article_sub_sub_number_str = m_article.groups()[3].replace("の","").translate(trans) if m_article.groups()[3] else "1"
                article_sub_sub_number = int(article_sub_sub_number_str, 10)
                id_str += f"_{article_sub_sub_number}"
            next_article.update({
                "Caption":{
                    "ArticleCaption":m_caption.groups()[0],
                    "MutatisMutandis":m_caption.groups()[2],
                    "RevisionHistory":rev_hist,
                    "Line":prev_line,
                },
                "Article":{
                    "Id":id_str,
                    "ArticleTitle":m_article.group().strip(),
                    "ArticleNumber":article_number,
                    "ArticleSubNumber":article_sub_number,
                    "ArticleSubSubNumber":article_sub_sub_number,
                    "ArticleLine":line,
                    "Texts":[line.replace(m_article.group(),"").strip()]
                },
                "Explanations":[],
            })
            next_article.update({
                "_AddTextTarget":next_article['Article']["Texts"]
            })
        else:
            m_deleted_article = extract_kamji_number_title(line, "条", ".*?削除")
            if m_deleted_article:
                done = True
                id_str = str(current_id_str_obj["id"])
                article_number = int(m_article.groups()[0].translate(trans), 10)
                id_str += f"-At_{article_number}"
                article_sub_number = 0
                if 2 < len(m_article.groups()):
                    article_sub_number_str = m_article.groups()[2].replace("の","").translate(trans) if m_article.groups()[2] else "1"
                    article_sub_number = int(article_sub_number_str, 10)
                    id_str += f"_{article_sub_number}"
                next_article.update({
                    "Article":{
                        "Id":id_str,
                        "ArticleTitle":f"第{m_deleted_article.groups()[0].strip()}条",
                        "ArticleLine":line,
                        "ArticleNumber":article_number,
                        "ArticleSubNumber":article_sub_number,
                        "Texts":[line.replace(m_article.group(),"").strip()]
                    },
                    "Explanations":[]
                })
                next_article.update({
                    "_AddTextTarget":next_article['Article']["Texts"]
                })
            else:
                print(f'!! {m_article.group()}')
    elif line.startswith("［旧法との関係］"):
        current_article.update({
            "OldLawRelation":{
                "Line":line,
                "Texts":[line.replace("［旧法との関係］","").strip()]
            }
        })
        current_article.update({
            "_AddTextTarget":current_article["OldLawRelation"]["Texts"]
        })
    elif line == "［趣 旨］":
        current_article.update({
            "Purpose":{
                "Texts":[]
            }
        })
        current_article.update({
            "_AddTextTarget":current_article["Purpose"]["Texts"]
        })
    elif line == "［字句の解釈］":
        current_article.update({
            "Interpretation":{
                "Texts":[]
            }
        })
        current_article.update({
            "_AddTextTarget":current_article["Interpretation"]["Texts"]
        })
    elif line == "［参 考］":
        current_article.update({
            "Reference":{
                "Texts":[]
            }
        })
        current_article.update({
            "_AddTextTarget":current_article["Reference"]["Texts"]
        })
    else:
        if '_AddTextTarget' in current_article:
            current_article['_AddTextTarget'].append(line)
        
    return done

def to_structured_data(pages_obj):
    trans = make_number_trans()
    article_objs = []
    current_article = {}
    current_id_str_obj = {"id":""}
    next_article = {}
    prev_line = ""
    for page_obj in pages_obj:
        page_lines = page_obj['lines']
        page_idx = page_obj['page_number']
        for line_idx, line in enumerate(page_lines):
            if extract_attribute(line, prev_line, current_article, next_article, page_idx, line_idx, trans,current_id_str_obj):
                if "_AddTextTarget" in current_article:
                    current_article.pop("_AddTextTarget")
                if current_article != {}:
                    article_objs.append(current_article)
                current_article = next_article.copy()
                next_article = {}
            prev_line = line
    if "_AddTextTarget" in current_article:
        current_article.pop("_AddTextTarget")
    article_objs.append(current_article)
    return article_objs

def texts_to_sentences(list_to_append, texts):
    line = ""
    for text in texts:
        line += text
        if re.search("。[ 　]*$", text) or re.search("。（.*?）$", text):
            list_to_append.append(line)
            line = ""
    if 0 < len(line):
        list_to_append.append(line)


def make_article_md(article):
    md_article_texts = []
    if "Article" in article and "ArticleTitle" in article["Article"]:
        title = article["Article"]["ArticleTitle"]
    else:
        title = None
    if "Caption" in article and "ArticleCaption" in article["Caption"]:
        caption = article["Caption"]["ArticleCaption"]
    else:
        caption = None
    
    if caption is None:
        md_article_texts.append(f"## {title}")
    else:
        md_article_texts.append(f"## {title} ({caption})")
    
    if "Article" in article and "Texts" in article["Article"]:
        texts_to_sentences(md_article_texts, article["Article"]["Texts"])
        md_article_texts.append("")

    if "OldLawRelation" in article and "Texts" in article["OldLawRelation"]:
        md_article_texts.append("### 旧法との関係")
#        md_article_texts.append("```")
        md_article_texts.extend(article["OldLawRelation"]["Texts"])
#        md_article_texts.append("```")
        md_article_texts.append("")

    if "Purpose" in article and "Texts" in article["Purpose"]:
        md_article_texts.append("### 趣旨")
        texts_to_sentences(md_article_texts, article["Purpose"]["Texts"])
        md_article_texts.append("")

    if "Interpretation" in article and "Texts" in article["Interpretation"]:
        md_article_texts.append("### 字句解説")
        texts_to_sentences(md_article_texts, article["Interpretation"]["Texts"])
        md_article_texts.append("")

    if "Reference" in article and "Texts" in article["Reference"]:
        md_article_texts.append("### 参考")
        texts_to_sentences(md_article_texts, article["Reference"]["Texts"])
        md_article_texts.append("")

    return {
        "title":f'{article["Article"]["Id"]}',
        "texts":md_article_texts
    }


if __name__ == "__main__":
    import json
    from pathlib import Path    


#    in_file_name = "tokkyo_chikujo_text.json"
    in_file_name = "tokkyo_text_modified.json"
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    in_file_base = os.path.join(base_path, "extracted_text_from_pdf")
    in_file_path = os.path.join(in_file_base, in_file_name)
    out_file_base = os.path.abspath(os.path.join(base_path, "..","markdowns","特許法"))
    os.makedirs(out_file_base, exist_ok=True)

    with open(in_file_path, encoding='utf-8') as f:
        in_obj = json.load(f)

#    pages = in_obj["pages"]
    pages = in_obj
    conversioned_obj = conversion_text(pages)
    articles = to_structured_data(conversioned_obj)
    
    article_mds = [make_article_md(article) for article in articles]

    for idx, article_md in enumerate(article_mds):
        md_file_path = os.path.join(out_file_base, f"{idx:03d}_{article_md['title']}.md")

        prev_next_strs = []
        if 0 < idx:
            prev_json_file_path = os.path.join(out_file_base, f"{idx-1:03d}_{article_mds[idx-1]['title']}.md")
            prev_file_path_rel = Path(prev_json_file_path).relative_to(Path.cwd())
            prev_str = f"[prev](/{prev_file_path_rel})"
            prev_next_strs.append(prev_str)
        if idx < len(articles) - 1:
            next_json_file_path = os.path.join(out_file_base, f"{idx+1:03d}_{article_mds[idx+1]['title']}.md")
            next_file_path_rel = Path(next_json_file_path).relative_to(Path.cwd())
            next_str = f"[next](/{next_file_path_rel})"
            prev_next_strs.append(next_str)
        
        all_lines = prev_next_strs + article_md["texts"] + prev_next_strs


        with open(md_file_path, "w", encoding='utf-8') as f:
            f.write("\n".join(all_lines))