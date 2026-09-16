#!/usr/bin/env python3
"""Build a compact, frequency-sorted answer index from the 17 enriched exams."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ENRICHED_DIR = ROOT / "data" / "enriched_exams"
DATA_OUTPUT = ROOT / "data" / "quick_reference.json"
WEB_OUTPUT = ROOT / "web" / "public" / "data" / "quick-reference.json"

SUPERSECTIONS = {
    "geography": ("Geography", "地理"),
    "history": ("History", "历史"),
    "government": ("Politics", "政治"),
    "law-life": ("Law & everyday life", "法律与生活"),
    "religion-holidays": ("Religion & holidays", "宗教与节日"),
    "culture-inventions": ("Culture & inventions", "文化与发明"),
    "sport-leisure": ("Sport & leisure", "体育与休闲"),
    "civic-responsibility": ("Civic responsibility", "公民责任"),
}

CATEGORY_SUPERSECTIONS = {
    "1.1 Becoming a permanent resident": "civic-responsibility",
    "1.2 The values and principles of the UK": "civic-responsibility",
    "2.1 What is the UK?": "geography",
    "3.1 Early Britain": "history",
    "3.2 The Middle Ages": "history",
    "3.3 The Tudors and Stuarts": "history",
    "3.4 A global power": "history",
    "3.5 The 20th century": "history",
    "3.6 Britain since 1945": "history",
    "4.1 The UK today": "geography",
    "4.2 Religion": "religion-holidays",
    "4.3 Customs and traditions": "religion-holidays",
    "4.4 Sport": "sport-leisure",
    "4.5 Arts and culture": "culture-inventions",
    "4.6 Leisure": "sport-leisure",
    "4.7 Places of interest": "geography",
    "5.1 The development of British democracy": "government",
    "5.2 The British constitution": "government",
    "5.3 The government": "government",
    "5.4 The UK and international institutions": "government",
    "5.5 Respecting the law": "law-life",
    "5.6 Fundamental principles": "law-life",
    "5.7 Your role in the community": "civic-responsibility",
}

# Topic-level placement takes precedence over the source chapter when a topic
# is more useful under another short, learner-facing heading.
TOPIC_SUPERSECTION_OVERRIDES = {
    # Place topics by what the question actually tests rather than by the
    # handbook chapter in which the source happened to introduce them.
    "mary-peters": "sport-leisure",
    "shakespeare": "culture-inventions",
    "canterbury-tales": "culture-inventions",
    "rutherford-atom": "culture-inventions",
    "modern-british-inventions": "culture-inventions",
    "swinging-sixties": "culture-inventions",
    "british-film": "culture-inventions",
    "wallace-gromit": "culture-inventions",
    "charlie-chaplin": "culture-inventions",
    "traditional-food": "culture-inventions",
    "margaret-thatcher": "government",
    "robert-walpole": "government",
    "coalition-2010": "government",
    "bbc-independence": "government",
    "union-jack": "geography",
    "national-flowers": "geography",
    "crathes-castle": "geography",
    "women-workforce": "law-life",
    "leisure-age-limits": "law-life",
    "shopping-hours": "law-life",
    "house-lords": "government",
    "jury": "law-life",
    "dog-collar": "law-life",
    "caxton-printing": "culture-inventions",
    "baird-television": "culture-inventions",
    "newton-gravity": "culture-inventions",
    "whittle-jet": "culture-inventions",
    "concorde": "culture-inventions",
    "francis-crick-dna": "culture-inventions",
}

# The culture section is easier to scan when individual people and works sit
# under a small set of subject headings. Visual art remains separate because
# those questions do not truthfully fit any of the requested media categories.
CULTURE_TOPIC_GROUPS = {
    "british-film": (0, "film", "Film", "电影"),
    "wallace-gromit": (0, "film", "Film", "电影"),
    "charlie-chaplin": (0, "film", "Film", "电影"),
    "visual-art": (1, "visual-art", "Visual art", "美术"),
    "classical-music": (2, "classical-music", "Classical music", "古典音乐"),
    "swinging-sixties": (3, "rock-music", "Rock & pop music", "摇滚音乐"),
    "wordsworth-daffodils": (4, "poetry", "Poetry", "诗歌"),
    "british-literature": (5, "literature", "Literature", "文学"),
    "canterbury-tales": (5, "literature", "Literature", "文学"),
    "modern-british-inventions": (6, "inventions", "Inventions", "发明"),
    "caxton-printing": (6, "inventions", "Inventions", "发明"),
    "baird-television": (6, "inventions", "Inventions", "发明"),
    "whittle-jet": (6, "inventions", "Inventions", "发明"),
    "concorde": (6, "inventions", "Inventions", "发明"),
    "cenotaph": (7, "architecture", "Architecture", "建筑"),
    "francis-crick-dna": (8, "science", "Science", "科学"),
    "newton-gravity": (8, "science", "Science", "科学"),
    "rutherford-atom": (8, "science", "Science", "科学"),
    "shakespeare": (9, "theatre", "Theatre", "戏剧"),
    "london-theatreland": (9, "theatre", "Theatre", "戏剧"),
    "traditional-food": (10, "food", "Food", "食物"),
    "edinburgh-fringe": (11, "cultural-festivals", "Cultural festivals", "文化节"),
}

GOVERNMENT_TOPIC_GROUPS = {
    "unwritten-constitution": (0, "constitution-monarch", "Constitution & monarch", "宪法与君主"),
    "constitutional-institutions": (0, "constitution-monarch", "Constitution & monarch", "宪法与君主"),
    "parliamentary-democracy": (0, "constitution-monarch", "Constitution & monarch", "宪法与君主"),
    "monarch-duties": (0, "constitution-monarch", "Constitution & monarch", "宪法与君主"),
    "house-commons": (1, "parliament-mps", "Parliament & MPs", "议会与议员"),
    "house-lords": (1, "parliament-mps", "Parliament & MPs", "议会与议员"),
    "mp-elections-duties": (1, "parliament-mps", "Parliament & MPs", "议会与议员"),
    "hansard": (1, "parliament-mps", "Parliament & MPs", "议会与议员"),
    "shadow-cabinet": (1, "parliament-mps", "Parliament & MPs", "议会与议员"),
    "home-secretary": (2, "government-pm", "Government & Prime Minister", "政府与首相"),
    "civil-servants": (2, "government-pm", "Government & Prime Minister", "政府与首相"),
    "prime-minister-residence": (2, "government-pm", "Government & Prime Minister", "政府与首相"),
    "robert-walpole": (2, "government-pm", "Government & Prime Minister", "政府与首相"),
    "margaret-thatcher": (2, "government-pm", "Government & Prime Minister", "政府与首相"),
    "coalition-2010": (2, "government-pm", "Government & Prime Minister", "政府与首相"),
    "election-ages": (3, "elections-media", "Elections & media", "选举与媒体"),
    "individual-electoral-registration": (3, "elections-media", "Elections & media", "选举与媒体"),
    "by-elections": (3, "elections-media", "Elections & media", "选举与媒体"),
    "poll-card": (3, "elections-media", "Elections & media", "选举与媒体"),
    "balanced-election-media": (3, "elections-media", "Elections & media", "选举与媒体"),
    "broadcast-impartiality": (3, "elections-media", "Elections & media", "选举与媒体"),
    "bbc-independence": (3, "elections-media", "Elections & media", "选举与媒体"),
    "devolved-government": (4, "central-local-government", "Central & local government", "中央与地方"),
    "welsh-government": (4, "central-local-government", "Central & local government", "中央与地方"),
    "northern-ireland-elections": (4, "central-local-government", "Central & local government", "中央与地方"),
    "local-government": (4, "central-local-government", "Central & local government", "中央与地方"),
    "commonwealth": (5, "international-organisations", "International organisations", "国际组织"),
}

GEOGRAPHY_TOPIC_GROUPS = {
    "great-britain": (0, "uk-overview", "UK overview", "英国概况"),
    "uk-location": (0, "uk-overview", "UK overview", "英国概况"),
    "uk-population": (0, "uk-overview", "UK overview", "英国概况"),
    "uk-capitals": (0, "uk-overview", "UK overview", "英国概况"),
    "overseas-territories": (1, "territories-dependencies", "Territories & dependencies", "领土与属地"),
    "crown-dependencies": (1, "territories-dependencies", "Territories & dependencies", "领土与属地"),
    "national-parks": (2, "landscapes-parks", "Landscapes & parks", "自然与公园"),
    "lake-district": (2, "landscapes-parks", "Landscapes & parks", "自然与公园"),
    "giants-causeway": (2, "landscapes-parks", "Landscapes & parks", "自然与公园"),
    "wales-places": (3, "places-landmarks", "Places & landmarks", "地点与名胜"),
    "tower-crown-jewels": (3, "places-landmarks", "Places & landmarks", "地点与名胜"),
    "big-ben": (3, "places-landmarks", "Places & landmarks", "地点与名胜"),
    "crathes-castle": (3, "places-landmarks", "Places & landmarks", "地点与名胜"),
    "eden-project": (3, "places-landmarks", "Places & landmarks", "地点与名胜"),
    "national-trust": (3, "places-landmarks", "Places & landmarks", "地点与名胜"),
    "national-flowers": (4, "symbols-currency", "Symbols & currency", "象征与货币"),
    "union-jack": (4, "symbols-currency", "Symbols & currency", "象征与货币"),
    "uk-currency-banknotes": (4, "symbols-currency", "Symbols & currency", "象征与货币"),
    "uk-coins": (4, "symbols-currency", "Symbols & currency", "象征与货币"),
}

RELIGION_HOLIDAY_TOPIC_GROUPS = {
    "st-patrick": (0, "patron-saints", "Patron saints", "守护神"),
    "st-andrew": (0, "patron-saints", "Patron saints", "守护神"),
    "st-david": (0, "patron-saints", "Patron saints", "守护神"),
    "st-george": (0, "patron-saints", "Patron saints", "守护神"),
    "established-churches": (1, "churches", "Churches", "教会"),
    "church-of-scotland": (1, "churches", "Churches", "教会"),
    "christmas-boxing-day": (2, "christian-festivals", "Christian festivals", "基督教节日"),
    "easter-good-friday": (2, "christian-festivals", "Christian festivals", "基督教节日"),
    "diwali": (3, "other-religious-festivals", "Other religious festivals", "其他宗教节日"),
    "eid-al-fitr": (3, "other-religious-festivals", "Other religious festivals", "其他宗教节日"),
    "hogmanay-auld-lang-syne": (4, "traditional-festivals", "Traditional festivals", "传统节日"),
    "april-fools-day": (4, "traditional-festivals", "Traditional festivals", "传统节日"),
    "halloween": (4, "traditional-festivals", "Traditional festivals", "传统节日"),
    "bank-holidays": (5, "public-holidays", "Public holidays", "公共假日"),
}

LAW_LIFE_TOPIC_GROUPS = {
    "jury": (0, "courts-juries", "Courts & juries", "法院与陪审团"),
    "magistrates": (0, "courts-juries", "Courts & juries", "法院与陪审团"),
    "scottish-criminal-courts": (0, "courts-juries", "Courts & juries", "法院与陪审团"),
    "small-claims": (0, "courts-juries", "Courts & juries", "法院与陪审团"),
    "solicitor-fees": (0, "courts-juries", "Courts & juries", "法院与陪审团"),
    "criminal-civil-law": (1, "crime-protection", "Crime & protection", "犯罪与保护"),
    "protecting-against-abuse": (1, "crime-protection", "Crime & protection", "犯罪与保护"),
    "reporting-terrorism": (1, "crime-protection", "Crime & protection", "犯罪与保护"),
    "young-offenders-privacy": (1, "crime-protection", "Crime & protection", "犯罪与保护"),
    "police-complaints": (2, "police-complaints", "Police complaints", "警察投诉"),
    "motorcycle-moped-age": (3, "driving-rules", "Driving rules", "驾驶规则"),
    "driving-licence": (3, "driving-rules", "Driving rules", "驾驶规则"),
    "dog-collar": (4, "everyday-rules", "Everyday rules", "日常规定"),
    "leisure-age-limits": (4, "everyday-rules", "Everyday rules", "日常规定"),
    "shopping-hours": (4, "everyday-rules", "Everyday rules", "日常规定"),
    "national-insurance-number": (5, "work-documents", "Work & documents", "工作与证件"),
    "women-workforce": (5, "work-documents", "Work & documents", "工作与证件"),
}

SPORT_TOPIC_GROUPS = {
    "paralympians": (0, "olympics-athletics", "Olympics & athletics", "奥运与田径"),
    "olympic-games": (0, "olympics-athletics", "Olympics & athletics", "奥运与田径"),
    "roger-bannister": (0, "olympics-athletics", "Olympics & athletics", "奥运与田径"),
    "mary-peters": (0, "olympics-athletics", "Olympics & athletics", "奥运与田径"),
    "bobby-moore": (1, "ball-sports", "Ball sports", "球类运动"),
    "six-nations": (1, "ball-sports", "Ball sports", "球类运动"),
    "the-ashes": (1, "ball-sports", "Ball sports", "球类运动"),
    "wimbledon": (1, "ball-sports", "Ball sports", "球类运动"),
    "golf": (1, "ball-sports", "Ball sports", "球类运动"),
    "horse-racing": (2, "horse-racing", "Horse racing", "赛马"),
    "boat-race": (3, "rowing", "Rowing", "划船"),
}

CIVIC_TOPIC_GROUPS = {
    "british-values-responsibilities": (0, "values-responsibilities", "Values & responsibilities", "公民价值与责任"),
    "national-citizen-service": (1, "community-participation", "Community participation", "社区参与"),
    "canvassing": (1, "community-participation", "Community participation", "社区参与"),
    "school-governors": (1, "community-participation", "Community participation", "社区参与"),
    "friends-earth": (2, "charity-environment", "Charity & environment", "慈善与环保"),
}

HISTORY_TOPIC_GROUPS = {
    "prehistoric-britain": (0, "prehistoric-era", "Prehistoric Britain", "史前英国"),
    "first-farmers": (0, "prehistoric-era", "Prehistoric Britain", "史前英国"),
    "iron-age-coins": (0, "prehistoric-era", "Prehistoric Britain", "史前英国"),
    "roman-britain": (1, "roman-era", "Roman invasion & rule", "罗马入侵与统治"),
    "anglo-saxon-britain": (2, "early-medieval-era", "Anglo-Saxons & Vikings", "盎格鲁-撒克逊与维京"),
    "norman-conquest": (3, "medieval-era", "The Middle Ages", "中世纪"),
    "english-language-origins": (3, "medieval-era", "The Middle Ages", "中世纪"),
    "domesday-book": (3, "medieval-era", "The Middle Ages", "中世纪"),
    "medieval-society": (3, "medieval-era", "The Middle Ages", "中世纪"),
    "magna-carta": (3, "medieval-era", "The Middle Ages", "中世纪"),
    "bannockburn-robert-bruce": (3, "medieval-era", "The Middle Ages", "中世纪"),
    "hundred-years-war": (3, "medieval-era", "The Middle Ages", "中世纪"),
    "black-death": (3, "medieval-era", "The Middle Ages", "中世纪"),
    "wars-roses": (3, "medieval-era", "The Middle Ages", "中世纪"),
    "henry-viii-reformation": (4, "tudor-era", "The Tudors", "都铎时期"),
    "mary-queen-scots": (4, "tudor-era", "The Tudors", "都铎时期"),
    "protestant-britain": (4, "tudor-era", "The Tudors", "都铎时期"),
    "spanish-armada-elizabeth": (4, "tudor-era", "The Tudors", "都铎时期"),
    "james-i": (5, "stuart-era", "Stuarts & Civil War", "斯图亚特与内战"),
    "civil-war-cromwell": (5, "stuart-era", "Stuarts & Civil War", "斯图亚特与内战"),
    "charles-ii": (5, "stuart-era", "Stuarts & Civil War", "斯图亚特与内战"),
    "great-fire-london": (5, "stuart-era", "Stuarts & Civil War", "斯图亚特与内战"),
    "habeas-corpus": (5, "stuart-era", "Stuarts & Civil War", "斯图亚特与内战"),
    "huguenots": (5, "stuart-era", "Stuarts & Civil War", "斯图亚特与内战"),
    "glorious-revolution": (5, "stuart-era", "Stuarts & Civil War", "斯图亚特与内战"),
    "glencoe-massacre": (5, "stuart-era", "Stuarts & Civil War", "斯图亚特与内战"),
    "enlightenment": (6, "hanoverian-era", "Hanoverian Britain", "汉诺威时期"),
    "britain-france-trade": (6, "hanoverian-era", "Hanoverian Britain", "汉诺威时期"),
    "bonnie-prince-charlie": (6, "hanoverian-era", "Hanoverian Britain", "汉诺威时期"),
    "highland-clearances": (6, "hanoverian-era", "Hanoverian Britain", "汉诺威时期"),
    "industrial-revolution": (6, "hanoverian-era", "Hanoverian Britain", "汉诺威时期"),
    "james-cook": (6, "hanoverian-era", "Hanoverian Britain", "汉诺威时期"),
    "american-independence": (6, "hanoverian-era", "Hanoverian Britain", "汉诺威时期"),
    "admiral-nelson-trafalgar": (6, "hanoverian-era", "Hanoverian Britain", "汉诺威时期"),
    "slavery-abolition": (6, "hanoverian-era", "Hanoverian Britain", "汉诺威时期"),
    "battle-waterloo": (6, "hanoverian-era", "Hanoverian Britain", "汉诺威时期"),
    "victorian-britain": (7, "victorian-empire-era", "Victorian Britain & Empire", "维多利亚与帝国"),
    "irish-nationalism-famine": (7, "victorian-empire-era", "Victorian Britain & Empire", "维多利亚与帝国"),
    "crimean-war": (7, "victorian-empire-era", "Victorian Britain & Empire", "维多利亚与帝国"),
    "boer-war": (7, "victorian-empire-era", "Victorian Britain & Empire", "维多利亚与帝国"),
    "women-suffrage": (8, "democracy-ww1-era", "Democratic reform & WWI", "民主改革与一战"),
    "first-world-war": (8, "democracy-ww1-era", "Democratic reform & WWI", "民主改革与一战"),
    "first-world-war-end": (8, "democracy-ww1-era", "Democratic reform & WWI", "民主改革与一战"),
    "great-depression": (9, "ww2-era", "Second World War era", "二战前后"),
    "germany-poland-1939": (9, "ww2-era", "Second World War era", "二战前后"),
    "second-world-war-churchill": (9, "ww2-era", "Second World War era", "二战前后"),
    "battle-britain": (9, "ww2-era", "Second World War era", "二战前后"),
    "butler-act": (9, "ww2-era", "Second World War era", "二战前后"),
    "clement-attlee": (9, "ww2-era", "Second World War era", "二战前后"),
    "ireland-republic": (9, "ww2-era", "Second World War era", "二战前后"),
}

# The four busiest history periods retain their chronological title-two era,
# then split into concise title-three study clusters. These labels describe
# existing source topics only; they do not change or merge exam questions.
HISTORY_DETAIL_GROUPS = {
    # The Middle Ages
    "norman-conquest": (0, "norman-conquest-english", "Norman Conquest & English", "诺曼征服与英语"),
    "english-language-origins": (0, "norman-conquest-english", "Norman Conquest & English", "诺曼征服与英语"),
    "domesday-book": (1, "domesday-book-detail", "Domesday Book", "Domesday Book"),
    "medieval-society": (2, "medieval-society-magna-carta", "Society & Magna Carta", "社会与Magna Carta"),
    "magna-carta": (2, "medieval-society-magna-carta", "Society & Magna Carta", "社会与Magna Carta"),
    "bannockburn-robert-bruce": (3, "medieval-wars", "Medieval wars", "中世纪战争"),
    "hundred-years-war": (3, "medieval-wars", "Medieval wars", "中世纪战争"),
    "wars-roses": (3, "medieval-wars", "Medieval wars", "中世纪战争"),
    "black-death": (4, "black-death-detail", "Black Death", "黑死病"),
    # The Tudors
    "henry-viii-reformation": (0, "henry-viii-reformation-detail", "Henry VIII & Reformation", "Henry VIII与宗教改革"),
    "mary-queen-scots": (1, "mary-queen-scots-detail", "Mary, Queen of Scots", "苏格兰女王Mary"),
    "protestant-britain": (2, "protestant-britain-detail", "Protestant Britain", "新教英国"),
    "spanish-armada-elizabeth": (3, "elizabeth-spanish-armada", "Elizabeth I & Spanish Armada", "Elizabeth I与西班牙无敌舰队"),
    # The Stuarts and Civil War
    "james-i": (0, "james-i-detail", "James I", "James I"),
    "civil-war-cromwell": (1, "civil-war-cromwell-detail", "Civil War & Cromwell", "内战与Cromwell"),
    "charles-ii": (2, "restoration-great-fire", "Restoration & Great Fire", "王政复辟与伦敦大火"),
    "great-fire-london": (2, "restoration-great-fire", "Restoration & Great Fire", "王政复辟与伦敦大火"),
    "habeas-corpus": (3, "rights-glorious-revolution", "Rights & Glorious Revolution", "权利与光荣革命"),
    "glorious-revolution": (3, "rights-glorious-revolution", "Rights & Glorious Revolution", "权利与光荣革命"),
    "glencoe-massacre": (3, "rights-glorious-revolution", "Rights & Glorious Revolution", "权利与光荣革命"),
    "huguenots": (4, "huguenots-detail", "Huguenots", "Huguenots"),
    # Hanoverian Britain
    "enlightenment": (0, "enlightenment-detail", "Enlightenment", "启蒙运动"),
    "bonnie-prince-charlie": (1, "jacobites-highlands", "Jacobites & Highlands", "Jacobites与苏格兰高地"),
    "highland-clearances": (1, "jacobites-highlands", "Jacobites & Highlands", "Jacobites与苏格兰高地"),
    "industrial-revolution": (2, "industrial-revolution-detail", "Industrial Revolution", "工业革命"),
    "britain-france-trade": (3, "exploration-global-rivalry", "Exploration & global rivalry", "探索与全球竞争"),
    "james-cook": (3, "exploration-global-rivalry", "Exploration & global rivalry", "探索与全球竞争"),
    "american-independence": (3, "exploration-global-rivalry", "Exploration & global rivalry", "探索与全球竞争"),
    "admiral-nelson-trafalgar": (4, "trafalgar-waterloo", "Trafalgar & Waterloo", "Trafalgar与Waterloo"),
    "battle-waterloo": (4, "trafalgar-waterloo", "Trafalgar & Waterloo", "Trafalgar与Waterloo"),
    "slavery-abolition": (5, "slavery-abolition-detail", "Abolition of slavery", "废除奴隶制"),
}

TOPIC_GROUPS_BY_SECTION = {
    "history": HISTORY_TOPIC_GROUPS,
    "culture-inventions": CULTURE_TOPIC_GROUPS,
    "government": GOVERNMENT_TOPIC_GROUPS,
    "geography": GEOGRAPHY_TOPIC_GROUPS,
    "religion-holidays": RELIGION_HOLIDAY_TOPIC_GROUPS,
    "law-life": LAW_LIFE_TOPIC_GROUPS,
    "sport-leisure": SPORT_TOPIC_GROUPS,
    "civic-responsibility": CIVIC_TOPIC_GROUPS,
}

BOOLEAN_ANSWERS = {"true", "false", "yes", "no"}

# Questions about the same person, event or institution often test different
# facts, so an answer-only key splits the very material this page should join.
# Keep these rules deliberately specific and ordered: the first matching topic
# wins, which prevents (for example) Mary, Queen of Scots questions from being
# absorbed into the broader Elizabeth I topic.
TOPIC_RULES = (
    ("admiral-nelson-trafalgar", "Admiral Nelson & the Battle of Trafalgar", "纳尔逊海军上将与特拉法加海战", (r"\badmiral nelson\b", r"\bbattle of trafalgar\b")),
    ("women-suffrage", "Women's suffrage & Emmeline Pankhurst", "妇女选举权与Emmeline Pankhurst", (r"\bemmeline pankhurst\b", r"\bsuffragettes?\b", r"\bwomen(?:'s)? (?:rights?|right) to vote\b", r"\bwomen.*\bright to vote\b")),
    ("mary-queen-scots", "Mary, Queen of Scots", "苏格兰女王Mary", (r"\bmary,? queen of scots\b", r"\bmary stuart\b")),
    ("spanish-armada-elizabeth", "Elizabeth I & the Spanish Armada", "Elizabeth I与西班牙无敌舰队", (r"\bspanish armada\b", r"\belizabeth i\b")),
    ("henry-viii-reformation", "Henry VIII & the Reformation", "Henry VIII与宗教改革", (r"\bhenry viii\b", r"\bthe reformation\b", r"\bauthority of the pope\b")),
    ("civil-war-cromwell", "The Civil War, Charles I & Oliver Cromwell", "内战、Charles I与Oliver Cromwell", (r"\boliver cromwell\b", r"\blord protector\b", r"\bcharles i\b", r"\benglish civil war\b")),
    ("glorious-revolution", "The Glorious Revolution & the Bill of Rights", "光荣革命与《权利法案》", (r"\bglorious revolution\b", r"\bbill of rights\b", r"\bwilliam of orange\b", r"\bjames ii\b")),
    ("battle-waterloo", "The Battle of Waterloo", "滑铁卢战役", (r"\bbattle of waterloo\b", r"\bduke of wellington\b")),
    ("slavery-abolition", "The abolition of slavery", "废除奴隶制", (r"\bemancipation act\b", r"\bwilliam wilberforce\b", r"\babolish(?:ed)? slavery\b")),
    ("enlightenment", "The Enlightenment", "启蒙运动", (r"\bthe enlightenment\b", r"\badam smith\b", r"\bdavid hume\b")),
    ("boer-war", "The Boer War", "Boer War", (r"\bboer war\b", r"\bboers\b")),
    ("american-independence", "American independence & taxation", "美国独立与税收争议", (r"\bno taxation without representation\b", r"\bamerican colon(?:y|ies)\b")),
    ("industrial-revolution", "The Industrial Revolution", "工业革命", (r"\bindustrial revolution\b", r"\bsteam power\b", r"\bgreat western railway\b", r"\bisambard kingdom brunel\b")),
    ("crimean-war", "The Crimean War", "克里米亚战争", (r"\bcrimean war\b",)),
    ("bonnie-prince-charlie", "Bonnie Prince Charlie & the Highlands", "Bonnie Prince Charlie与苏格兰高地", (r"\bbonnie prince charlie\b",)),
    ("domesday-book", "The Domesday Book", "Domesday Book", (r"\bdomesday book\b",)),
    ("tower-crown-jewels", "The Tower of London & the Crown Jewels", "伦敦塔与Crown Jewels", (r"\bcrown jewels\b", r"\bwhite tower\b", r"\btower of london\b")),
    ("norman-conquest", "The Norman Conquest", "诺曼征服", (r"\bnorman conquest\b", r"\bwilliam the conqueror\b", r"\bbattle of hastings\b")),
    ("wars-roses", "The Wars of the Roses", "玫瑰战争", (r"\bwars? of the roses\b", r"\btudor rose\b", r"\bhouse of lancaster\b", r"\bhouse of york\b")),
    ("magna-carta", "Magna Carta", "Magna Carta", (r"\bmagna carta\b",)),
    ("black-death", "The Black Death", "黑死病", (r"\bblack death\b",)),
    ("great-fire-london", "The Great Fire of London", "伦敦大火", (r"\bgreat fire\b", r"\brebuilt saint paul(?:'s|’s) cathedral\b")),
    ("roman-britain", "Roman Britain", "罗马时期", (r"\bhadrian(?:'s|’s) wall\b", r"\bhousesteads\b", r"\bvindolanda\b", r"\bboudicca\b")),
    ("first-farmers", "Britain's first farmers", "英国最早的农民", (r"\bfirst farmers\b",)),
    ("iron-age-coins", "Britain's first coins", "英国最早的硬币", (r"\bfirst coins\b", r"\bcoins? (?:to be )?minted in britain\b")),
    ("anglo-saxon-britain", "Anglo-Saxons & Vikings", "盎格鲁-撒克逊与维京", (r"\balfred the great\b", r"\bking alfred\b")),
    ("first-world-war", "The First World War", "第一次世界大战", (r"\bfirst world war\b", r"\bworld war (?:one|i)\b", r"\b11 november 1918\b")),
    ("second-world-war-churchill", "The Second World War & Winston Churchill", "第二次世界大战与Winston Churchill", (r"\bwinston churchill\b", r"\bsecond world war\b", r"\bworld war (?:two|ii)\b")),
    ("st-george", "St George, patron saint of England", "英格兰守护神St George", (r"\bst george(?:'s|’s)?\b",)),
    ("st-andrew", "St Andrew, patron saint of Scotland", "苏格兰守护神St Andrew", (r"\bst andrew(?:'s|’s)?\b",)),
    ("st-patrick", "St Patrick, patron saint of Northern Ireland", "北爱尔兰守护神St Patrick", (r"\bst patrick(?:'s|’s)?\b", r"\bshamrock\b")),
    ("st-david", "St David, patron saint of Wales", "威尔士守护神St David", (r"\bst david(?:'s|’s)?\b",)),
    ("house-commons", "The House of Commons, the Speaker & PMQs", "下议院、Speaker与PMQs", (r"\bhouse of commons\b", r"\bprime minister's questions\b", r"\bprime minister’s questions\b", r"\bthe speaker\b")),
    ("house-lords", "The House of Lords", "上议院", (r"\bhouse of lords\b", r"\blife peers?\b")),
    ("shadow-cabinet", "The opposition & the Shadow Cabinet", "反对党与Shadow Cabinet", (r"\bshadow cabinet\b", r"\bshadow ministers?\b", r"\bleader of the opposition\b")),
    ("devolved-government", "Devolution in Scotland, Wales & Northern Ireland", "苏格兰、威尔士与北爱尔兰的权力下放", (r"\bscottish parliament\b", r"\bwelsh parliament\b", r"\bsenedd\b", r"\bnorthern ireland assembly\b", r"\bdevolved\b")),
    ("home-secretary", "The Home Secretary", "Home Secretary的职责", (r"\bhome secretary\b",)),
    ("balanced-election-media", "Balanced election coverage", "选举期间的平衡媒体报道", (r"\bbalanced coverage\b", r"\bcoverage of (?:all )?political parties must be balanced\b")),
    ("individual-electoral-registration", "Individual electoral registration", "个人选民登记", (r"\bindividual registration\b",)),
    ("civil-servants", "Civil servants", "Civil servants", (r"\bcivil servants?\b",)),
    ("jury", "Juries & jury service", "陪审团与陪审义务", (r"\bjury\b",)),
    ("magistrates", "Magistrates & District Judges", "Magistrates与District Judges", (r"\bmagistrates?\b", r"\bdistrict judge\b")),
    ("small-claims", "The small claims procedure", "小额索赔程序", (r"\bsmall claims procedure\b",)),
    ("police-complaints", "Complaints about the police", "投诉警察的方式", (r"\bcomplaints? (?:against|about) the police\b", r"\bcomplaint about the police\b", r"\bchief constable\b")),
    ("reporting-terrorism", "Reporting terrorism", "举报恐怖主义活动", (r"\bterrorist activity\b", r"\bextremist or terrorist\b")),
    ("motorcycle-moped-age", "Minimum driving ages: motorcycles & mopeds", "摩托车与轻便摩托车的最低驾驶年龄", (r"\bdrive a motorcycle\b", r"\bdrive a moped\b")),
    ("crown-dependencies", "The Crown Dependencies", "皇家属地", (r"\bcrown dependenc(?:y|ies)\b", r"\bchannel islands\b", r"\bisle of man\b")),
    ("overseas-territories", "The British Overseas Territories", "英国海外领土", (r"\bbritish overseas territor(?:y|ies)\b", r"\bst helena\b", r"\bfalkland islands\b")),
    ("hogmanay-auld-lang-syne", "Hogmanay & Auld Lang Syne", "Hogmanay与Auld Lang Syne", (r"\bhogmanay\b", r"\bauld lang syne\b")),
    ("bank-holidays", "Bank holidays", "Bank Holidays", (r"\bbank holidays?\b", r"\bpublic holidays? called\b")),
    ("christmas-boxing-day", "Christmas Day & Boxing Day", "Christmas Day与Boxing Day", (r"\bchristmas day\b", r"\bboxing day\b", r"\bbirth of jesus christ\b")),
    ("april-fools-day", "April Fool's Day", "April Fool's Day", (r"\bapril fool(?:'s|’s|‘s) day\b", r"\bstories that are jokes until midday\b")),
    ("easter-good-friday", "Easter, Lent & Good Friday", "Easter、Lent与Good Friday", (r"\bgood friday\b", r"\beaster\b", r"\blent\b")),
    ("diwali", "Diwali / Deepavali", "排灯节Diwali", (r"\bdiwali\b", r"\bdeepavali\b")),
    ("shakespeare", "William Shakespeare", "William Shakespeare", (r"\bwilliam shakespeare\b", r"\bshakespeare\b", r"\ba midsummer night(?:'s|’s) dream\b")),
    ("wordsworth-daffodils", "William Wordsworth & Daffodils", "Wordsworth与Daffodils", (r"\bwilliam wordsworth\b", r"\bdaffodils\b")),
    ("caxton-printing", "William Caxton & printing", "William Caxton与印刷术", (r"\bwilliam caxton\b",)),
    ("baird-television", "John Logie Baird & television", "John Logie Baird与电视", (r"\bjohn logie baird\b",)),
    ("newton-gravity", "Isaac Newton & gravity", "Isaac Newton与重力", (r"\bisaac newton\b", r"\bgravity\b")),
    ("whittle-jet", "Frank Whittle & the jet engine", "Frank Whittle与喷气发动机", (r"\bfrank whittle\b", r"\bjet engine\b")),
    ("wallace-gromit", "Nick Park & Wallace and Gromit", "Nick Park与Wallace and Gromit", (r"\bnick park\b", r"\bwallace and gromit\b")),
    ("margaret-thatcher", "Margaret Thatcher", "Margaret Thatcher", (r"\bmargaret thatcher\b",)),
    ("swinging-sixties", "The Swinging Sixties", "Swinging Sixties", (r"\bswinging sixties\b", r"\bbeatles\b", r"\b1960s.*(?:fashion|pop music)\b")),
    ("concorde", "Concorde", "Concorde超音速客机", (r"\bconcorde\b",)),
    ("francis-crick-dna", "Francis Crick & DNA", "Francis Crick与DNA", (r"\bfrancis crick\b", r"\bstructure of the dna molecule\b")),
    ("battle-britain", "The Battle of Britain", "Battle of Britain", (r"\bbattle of britain\b",)),
    ("germany-poland-1939", "Germany's invasion of Poland", "德国入侵波兰", (r"\bgermany invade(?:d)? poland\b", r"\bcountry was invaded by germany in 1939\b")),
    ("charlie-chaplin", "Charlie Chaplin & the Tramp", "Charlie Chaplin与流浪汉形象", (r"\bcharlie chaplin\b", r"\btramp character\b")),
    ("dog-collar", "Dog collars & identification", "狗项圈与身份信息", (r"\bdog(?:'s|’s)? collar\b", r"\bdog wears a collar\b")),
    ("golf", "Golf in Scotland", "苏格兰高尔夫", (r"\bgolf\b",)),
    ("bobby-moore", "Bobby Moore & the 1966 World Cup", "Bobby Moore与1966年世界杯", (r"\bbobby moore\b", r"\b1966 world cup\b")),
    ("roger-bannister", "Roger Bannister's four-minute mile", "Roger Bannister与四分钟一英里", (r"\broger bannister\b", r"\bmile in under four minutes\b", r"\b1 mile in under 4 minutes\b")),
    ("paralympians", "British Paralympians", "英国残奥运动员", (r"\bparalympians?\b", r"\bellie simmonds\b")),
    ("horse-racing", "British horse racing", "英国赛马", (r"\bhorse[- ]racing\b", r"\bgrand national\b", r"\broyal ascot\b", r"\bnational horseracing museum\b")),
    ("giants-causeway", "The Giant's Causeway", "巨人堤道", (r"\bgiant(?:'s|’s) causeway\b",)),
    ("cenotaph", "The Cenotaph", "The Cenotaph", (r"\bthe cenotaph\b",)),
    ("canterbury-tales", "Chaucer & The Canterbury Tales", "Chaucer与The Canterbury Tales", (r"\bcanterbury tales\b", r"\bgeoffrey chaucer\b")),
    ("bannockburn-robert-bruce", "Robert the Bruce & Bannockburn", "Robert the Bruce与Bannockburn", (r"\brobert the bruce\b", r"\bbattle of bannockburn\b")),
    ("london-theatreland", "London's Theatreland", "伦敦Theatreland", (r"\btheatreland\b", r"\bfamous theatres are located\b")),
    ("lake-district", "The Lake District", "Lake District", (r"\blake district\b",)),
    ("national-parks", "National parks in Britain", "英国国家公园", (r"\bnational parks?\b",)),
    ("uk-currency-banknotes", "UK currency & banknotes", "英国货币与纸币", (r"\buk currency\b", r"\bpound sterling\b", r"\bbanknotes?\b", r"\bhighest value note\b", r"\bbritish banknote\b")),
    ("great-britain", "Great Britain & Northern Ireland", "Great Britain与Northern Ireland", (r"\bgreat britain\b",)),
    ("mp-elections-duties", "MPs: elections & responsibilities", "MP的选举与职责", (r"\bmember of (?:the )?parliament \(mp\)\b", r"\bresponsibilit(?:y|ies) of the mps\b", r"\bmps? can only be contacted\b", r"\bconstituency\b", r"\bgeneral elections held\b")),
    ("national-insurance-number", "National Insurance numbers", "National Insurance Number", (r"\bnational insurance number\b",)),
    ("protecting-against-abuse", "Protection from abuse & forced marriage", "防止虐待与强迫婚姻", (r"\bforces his wife to have sex\b", r"\bfemale genital mutilation\b", r"\bviolent towards their partner\b", r"\bforced into a marriage\b")),
    ("national-citizen-service", "National Citizen Service", "National Citizen Service", (r"\bnational citizen service\b",)),
    ("friends-earth", "Friends of the Earth", "Friends of the Earth", (r"\bfriends of the earth\b",)),
    ("british-values-responsibilities", "British values & civic responsibilities", "英国价值观与公民责任", (r"\bfundamental principles? of british life\b", r"\bas a british citizen\b", r"\bresponsibilit(?:y|ies).*british citizen\b", r"\bpermanent resident or citizen of the uk\b")),
    ("established-churches", "Established churches in the UK", "英国的国教制度", (r"\bestablished church\b", r"\bhead of the church of england\b", r"\bspiritual leader of the church of england\b")),
)

# Title-two headings are navigation labels, not summaries. Keep them short and
# let the question rows carry the fuller person, event and institution names.
TOPIC_TITLE_OVERRIDES = {
    "anglo-saxon-britain": ("Anglo-Saxons & Vikings", "盎格鲁-撒克逊与维京"),
    "bannockburn-robert-bruce": ("Bannockburn", "Bannockburn"),
    "canterbury-tales": ("Canterbury Tales", "Canterbury"),
    "henry-viii-reformation": ("The Reformation", "宗教改革"),
    "shakespeare": ("Shakespeare", "Shakespeare"),
    "spanish-armada-elizabeth": ("Spanish Armada", "西班牙无敌舰队"),
    "civil-war-cromwell": ("Civil War & Cromwell", "内战与Cromwell"),
    "glorious-revolution": ("Glorious Revolution", "光荣革命"),
    "american-independence": ("American independence", "美国独立"),
    "bonnie-prince-charlie": ("Bonnie Prince Charlie", "Bonnie Prince"),
    "admiral-nelson-trafalgar": ("Trafalgar", "特拉法加海战"),
    "women-suffrage": ("Women's suffrage", "妇女选举权"),
    "second-world-war-churchill": ("Second World War", "第二次世界大战"),
    "battle-britain": ("Battle of Britain", "不列颠之战"),
    "swinging-sixties": ("Swinging Sixties", "摇摆六十年代"),
    "margaret-thatcher": ("Margaret Thatcher", "撒切尔"),
    "devolved-government": ("Devolution", "权力下放"),
    "house-commons": ("House of Commons", "下议院"),
    "mp-elections-duties": ("MPs", "MP"),
    "home-secretary": ("Home Secretary", "Home Secretary"),
    "individual-electoral-registration": ("Electoral registration", "选民登记"),
    "shadow-cabinet": ("Shadow Cabinet", "影子内阁"),
    "tower-crown-jewels": ("Tower of London", "伦敦塔"),
    "great-britain": ("Great Britain", "Great Britain"),
    "overseas-territories": ("Overseas Territories", "海外领土"),
    "established-churches": ("Established churches", "国教"),
    "easter-good-friday": ("Easter", "Easter"),
    "hogmanay-auld-lang-syne": ("Hogmanay", "Hogmanay"),
    "st-patrick": ("St Patrick", "St Patrick"),
    "christmas-boxing-day": ("Christmas & Boxing Day", "Christmas"),
    "april-fools-day": ("April Fool's Day", "April Fool"),
    "st-andrew": ("St Andrew", "St Andrew"),
    "st-david": ("St David", "St David"),
    "st-george": ("St George", "St George"),
    "magistrates": ("Magistrates", "Magistrates"),
    "protecting-against-abuse": ("Abuse & forced marriage", "虐待与强迫婚姻"),
    "motorcycle-moped-age": ("Driving ages", "驾驶年龄"),
    "national-insurance-number": ("NI numbers", "NI Number"),
    "wallace-gromit": ("Wallace & Gromit", "超级无敌掌门狗"),
    "charlie-chaplin": ("Charlie Chaplin", "卓别林"),
    "roger-bannister": ("Roger Bannister", "Bannister"),
    "bobby-moore": ("Bobby Moore", "Bobby Moore"),
    "wordsworth-daffodils": ("Daffodils", "Daffodils"),
    "francis-crick-dna": ("DNA", "DNA"),
    "newton-gravity": ("Newton", "Newton"),
    "caxton-printing": ("Caxton", "Caxton"),
    "whittle-jet": ("Whittle", "Whittle"),
    "baird-television": ("Baird", "Baird"),
    "british-values-responsibilities": ("British values", "英国价值观"),
    "friends-earth": ("Friends of the Earth", "地球之友"),
    "national-citizen-service": ("National Citizen Service", "NCS"),
}

# Some differently worded questions test one reversible fact. On the quick
# reference page they should occupy one row, while their original records and
# stable IDs remain untouched in the source and enriched exam data.
FACT_RULES = (
    (
        "admiral-nelson-trafalgar",
        "nelson-died-at-trafalgar",
        (
            r"^in which battle did admiral nelson die\?",
            r"^who died at the battle of trafalgar\?",
        ),
    ),
    (
        "admiral-nelson-trafalgar",
        "nelson-commanded-british-fleet",
        (
            r"^who was admiral nelson\?",
            r"^who was in charge of the british fleet at the battle of trafalgar\?",
        ),
    ),
    (
        "women-suffrage",
        "equal-voting-age-in-1928",
        (
            r"^when were men and women given the right to vote at the age of 21\?",
            r"^when did women get the right to vote at the same age as men\?",
            r"^why is 1928 an important year in women(?:'|’)s voting history\?",
        ),
    ),
    (
        "iron-age-coins",
        "britains-first-coins-made-in-iron-age",
        (
            r"^who made the first coins to be minted in britain\?",
            r"^when were the first coins in britain made\?",
        ),
    ),
    (
        "roman-britain",
        "boudicca-fought-the-romans",
        (
            r"^who was the tribal leader who fought against the romans\?",
            r"^boudicca, was a tribal leader who fought against which foreign invaders\?",
        ),
    ),
    (
        "anglo-saxon-britain",
        "alfred-defeated-the-vikings",
        (
            r"^under which king did the anglo-saxon kingdoms in england unite to defeat the vikings\?",
            r"^who defeated the vikings\?",
        ),
    ),
    (
        "mary-queen-scots",
        "mary-queen-scots-executed-after-imprisonment",
        (
            r"^what happened to [‘']mary, queen of scots[’'] after she spent 20 years in prison\?",
            r"^what happened to mary, queen of scots, after being sent to prison for 20 years by her cousin queen elizabeth i\?",
        ),
    ),
    (
        "shakespeare",
        "shakespeare-born-in-stratford-upon-avon",
        (
            r"^where was william shakespeare born\?",
            r"^who was born in stratford-upon-avon\?",
        ),
    ),
    (
        "enlightenment",
        "enlightenment-new-ideas-period",
        (
            r"^what is the name of the period when new ideas about politics, philosophy and science were developed\?",
            r"^what is the enlightenment\?",
        ),
    ),
    (
        "bonnie-prince-charlie",
        "bonnie-prince-charlie-supported-by-highlanders-in-1745",
        (
            r"^who was supported by clansmen from the scottish highlands and raised and army in 1745\?",
            r"^during the rebellion of the clans in scotland, bonnie prince charlie was supported by clansmen from which scottish region\?",
        ),
    ),
    (
        "industrial-revolution",
        "steam-power-drove-industrial-development",
        (
            r"^which invention led to the development of britain during the industrial revolution\?",
            r"^which invention lead to the rapid development of the industry in britain during the 18th and 19th centuries\?",
        ),
    ),
    (
        "american-independence",
        "north-american-colonies-taxation-without-representation",
        (
            r"^what led the american colonies to want their independence from britain\?",
            r"^in 1776, which british colonies declared their independence because they demanded that there should be [‘']no taxation without representation[‘']\.",
        ),
    ),
    (
        "slavery-abolition",
        "emancipation-act-abolished-slavery-in-1833",
        (
            r"^when did the emancipation act abolish slavery throughout the british empire\?",
            r"^in 1833 the emancipation act abolished slavery throughout the british empire\.$",
        ),
    ),
    (
        "overseas-territories",
        "st-helena-and-falklands-not-part-of-uk",
        (
            r"^is st helena part of the uk\?",
            r"^st helena is a british overseas territory and it is part of the united kingdom\.$",
            r"^st helena and the falkland islands are part of great britain\.$",
            r"^the falkland islands are a british overseas territory and are part of the united kingdom\.$",
        ),
    ),
)

FACT_CANONICAL_DISPLAY = {
    "alfred-defeated-the-vikings": {
        "prompts": ["Under which king did the Anglo-Saxon kingdoms in England unite to defeat the Vikings?"],
        "answers": ["King Alfred the Great"],
    },
    "boudicca-fought-the-romans": {
        "prompts": ["Who was the tribal leader who fought against the Romans?"],
        "answers": ["Boudicca"],
    },
    "britains-first-coins-made-in-iron-age": {
        "prompts": ["Who made the first coins to be minted in Britain?"],
        "answers": ["The people of the Iron Age"],
    },
    "mary-queen-scots-executed-after-imprisonment": {
        "prompts": ["What happened to Mary, Queen of Scots, after 20 years in prison?"],
        "answers": ["She was executed"],
    },
    "shakespeare-born-in-stratford-upon-avon": {
        "prompts": ["Where was William Shakespeare born?"],
        "answers": ["Stratford-upon-Avon"],
    },
    "enlightenment-new-ideas-period": {
        "prompts": ["What is the Enlightenment?"],
        "answers": ["A period when new ideas about politics, philosophy and science were developed"],
    },
    "bonnie-prince-charlie-supported-by-highlanders-in-1745": {
        "prompts": ["Who raised an army with support from clansmen of the Scottish Highlands in 1745?"],
        "answers": ["Bonnie Prince Charlie"],
    },
    "steam-power-drove-industrial-development": {
        "prompts": ["Which invention drove Britain's industrial development during the Industrial Revolution?"],
        "answers": ["Steam power"],
    },
    "north-american-colonies-taxation-without-representation": {
        "prompts": ["Which colonies declared independence in 1776 after opposing British taxation without representation?"],
        "answers": ["The North American colonies"],
    },
    "emancipation-act-abolished-slavery-in-1833": {
        "prompts": ["When did the Emancipation Act abolish slavery throughout the British Empire?"],
        "answers": ["1833"],
    },
    "st-helena-and-falklands-not-part-of-uk": {
        "prompts": ["St Helena and the Falkland Islands are part of Great Britain."],
        "answers": ["False"],
    },
}

# Stable-ID groups for reviewed duplicates and reversible questions. These
# rules affect only the generated quick reference; every source exam question
# remains unchanged and traceable through question_ids.
FACT_ID_GROUPS = {
    "black-death-killed-one-third": {
        "question_ids": ("exam-06-q18", "exam-17-q08"),
        "prompts": ["Which disease killed about one third of England's population in 1348?"],
        "answers": ["The Black Death"],
    },
    "reformation-challenged-pope": {
        "question_ids": ("exam-07-q19", "exam-09-q19", "exam-16-q22"),
        "prompts": ["What movement challenged the authority of the Pope during Henry VIII's reign?"],
        "answers": ["The Reformation"],
    },
    "english-defeated-armada-in-1588": {
        "question_ids": ("exam-01-q12", "exam-08-q18"),
        "prompts": ["Who did the English defeat in 1588?"],
        "answers": ["The Spanish Armada"],
    },
    "spanish-armada-came-from-spain": {
        "question_ids": ("exam-10-q16", "exam-11-q11", "exam-13-q21"),
        "prompts": ["Which country sent the Spanish Armada to England in 1588?"],
        "answers": ["Spain"],
    },
    "waterloo-last-britain-france-battle": {
        "question_ids": ("exam-04-q01", "exam-09-q02"),
        "prompts": ["What was the last battle between Britain and France?"],
        "answers": ["The Battle of Waterloo"],
    },
    "boer-war-south-africa-1899-1902": {
        "question_ids": ("exam-05-q21", "exam-09-q10"),
        "prompts": ["Which war took place in South Africa from 1899 to 1902?"],
        "answers": ["The Boer War"],
    },
    "pankhurst-led-suffragettes": {
        "question_ids": ("exam-03-q20", "exam-11-q22"),
        "prompts": ["Who led the suffragettes campaigning for women's voting rights?"],
        "answers": ["Emmeline Pankhurst"],
    },
    "germany-invaded-poland-1939": {
        "question_ids": ("exam-03-q13", "exam-05-q24", "exam-08-q01"),
        "prompts": ["Which country did Germany invade in 1939, starting the Second World War?"],
        "answers": ["Poland"],
    },
    "battle-of-britain-aerial-battle": {
        "question_ids": ("exam-06-q14", "exam-11-q07"),
        "prompts": ["Which crucial aerial battle was fought between Germany and Britain during the Second World War?"],
        "answers": ["The Battle of Britain"],
    },
    "devolved-reserved-policies": {
        "question_ids": ("exam-09-q12", "exam-11-q16"),
        "prompts": ["Which two policies are not controlled by the devolved administrations?"],
        "answers": ["Defence", "Immigration"],
    },
    "home-secretary-responsibilities": {
        "question_ids": ("exam-02-q01", "exam-08-q04", "exam-15-q22"),
        "prompts": ["Who is responsible for crime, policing and immigration?"],
        "answers": ["The Home Secretary"],
    },
    "shadow-cabinet-opposition-group": {
        "question_ids": ("exam-17-q03", "exam-17-q23"),
        "prompts": ["What is the group of senior opposition MPs who challenge the government called?"],
        "answers": ["The Shadow Cabinet"],
    },
    "scotland-northern-ireland-banknotes": {
        "question_ids": ("exam-02-q13", "exam-04-q05", "exam-08-q08"),
        "prompts": ["Scotland and Northern Ireland have their own banknotes, valid everywhere in the UK."],
        "answers": ["True"],
    },
    "beefeaters-tower-guides": {
        "question_ids": ("exam-03-q09", "exam-13-q09"),
        "prompts": ["What are the Tower of London tour guides called?"],
        "answers": ["Beefeaters"],
    },
    "lake-district-largest-english-national-park": {
        "question_ids": ("exam-03-q15", "exam-13-q02"),
        "prompts": ["Which is the largest national park in England?"],
        "answers": ["The Lake District"],
    },
    "lent-forty-days-before-easter": {
        "question_ids": ("exam-01-q24", "exam-07-q23"),
        "prompts": ["What are the 40 days before Easter called?"],
        "answers": ["Lent"],
    },
    "wales-northern-ireland-no-established-church": {
        "question_ids": ("exam-03-q02", "exam-06-q05", "exam-10-q03"),
        "prompts": ["Wales and Northern Ireland have their own established churches."],
        "answers": ["False"],
    },
    "public-holidays-bank-holidays": {
        "question_ids": ("exam-10-q06", "exam-13-q05"),
        "prompts": ["What are public holidays called in the UK?"],
        "answers": ["Bank Holidays"],
    },
    "april-fools-media-jokes": {
        "question_ids": ("exam-05-q09", "exam-12-q13"),
        "prompts": ["On which day do television and newspapers publish jokes until midday?"],
        "answers": ["April Fool's Day"],
    },
    "report-terrorism-to-local-police": {
        "question_ids": ("exam-03-q07", "exam-16-q17"),
        "prompts": ["Who should you contact about extremist or terrorist activity?"],
        "answers": ["Your local police force"],
    },
    "chaplin-tramp-character": {
        "question_ids": ("exam-04-q20", "exam-13-q12"),
        "prompts": ["Who became famous for playing a tramp in silent movies?"],
        "answers": ["Charlie Chaplin"],
    },
    "golf-originated-scotland": {
        "question_ids": ("exam-02-q21", "exam-05-q08"),
        "prompts": ["Which sport can be traced to 15th-century Scotland?"],
        "answers": ["Golf"],
    },
    "caxton-first-english-printer": {
        "question_ids": ("exam-02-q22", "exam-13-q08"),
        "prompts": ["Who was the first person in England to print books using a printing press?"],
        "answers": ["William Caxton"],
    },
    "crick-co-discovered-dna-structure": {
        "question_ids": ("exam-08-q07", "exam-16-q10"),
        "prompts": ["Who was the British scientist who co-discovered the structure of DNA in the 1950s?"],
        "answers": ["Francis Crick"],
    },
    "british-citizen-responsibilities": {
        "question_ids": ("exam-09-q05", "exam-12-q19"),
        "prompts": ["Which two responsibilities will you have as a British citizen or permanent resident?"],
        "answers": ["Look after yourself and your family", "Respect the rights of others, including their right to their own opinions"],
    },
    "core-british-citizen-responsibilities": {
        "question_ids": ("exam-01-q01", "exam-06-q01", "exam-07-q01"),
        "prompts": ["What responsibilities will you have as a British citizen or permanent resident?"],
        "answers": [
            "Respect and obey the law",
            "Look after yourself and your family",
            "Look after the area in which you live and the environment",
        ],
    },
    "wordsworth-wrote-daffodils": {
        "question_ids": ("exam-01-q22", "exam-11-q18"),
        "prompts": ["Who wrote a famous poem about daffodils?"],
        "answers": ["William Wordsworth"],
    },
    "friends-of-the-earth-environmental-charity": {
        "question_ids": ("exam-05-q19", "exam-11-q06"),
        "prompts": ["Which environmental charity is called 'Friends of the Earth'?"],
        "answers": ["Friends of the Earth"],
    },
}

FACT_ID_LOOKUP = {
    question_id: fact_id
    for fact_id, definition in FACT_ID_GROUPS.items()
    for question_id in definition["question_ids"]
}
FACT_CANONICAL_DISPLAY.update(
    {
        fact_id: {
            "prompts": definition["prompts"],
            "answers": definition["answers"],
        }
        for fact_id, definition in FACT_ID_GROUPS.items()
    }
)

# Every remaining question belongs to a concise, learner-facing title-two
# topic. Stable IDs keep this curation independent from source punctuation.
FALLBACK_TOPIC_DEFINITIONS = (
    # History
    ("norman-conquest", "Norman Conquest", "诺曼征服", ("exam-07-q24",)),
    ("english-language-origins", "English language origins", "英语来源", ("exam-11-q09", "exam-15-q01")),
    ("roman-britain", "Roman Britain", "罗马时期", ("exam-10-q22", "exam-02-q10")),
    ("prehistoric-britain", "Prehistoric Britain", "史前英国", ("exam-07-q18", "exam-17-q14", "exam-14-q13")),
    ("anglo-saxon-britain", "Anglo-Saxon Britain", "盎格鲁-撒克逊", ("exam-14-q14", "exam-16-q04")),
    ("medieval-society", "Medieval society", "中世纪社会", ("exam-09-q16",)),
    ("hundred-years-war", "Hundred Years' War", "百年战争", ("exam-03-q05",)),
    ("protestant-britain", "Protestant Britain", "新教改革", ("exam-11-q14", "exam-12-q08", "exam-15-q16")),
    ("james-i", "James I", "James I", ("exam-13-q19",)),
    ("charles-ii", "Charles II", "Charles II", ("exam-16-q07", "exam-13-q06")),
    ("great-fire-london", "Great Fire of London", "伦敦大火", ("exam-04-q03",)),
    ("civil-war-cromwell", "Civil War & Cromwell", "内战与Cromwell", ("exam-07-q15",)),
    ("habeas-corpus", "Habeas Corpus", "Habeas Corpus", ("exam-10-q17",)),
    ("glencoe-massacre", "Glencoe", "Glencoe", ("exam-07-q08",)),
    ("huguenots", "Huguenots", "Huguenots", ("exam-12-q10",)),
    ("britain-france-trade", "Britain & France", "英法竞争", ("exam-17-q12",)),
    ("robert-walpole", "Robert Walpole", "Walpole", ("exam-14-q03",)),
    ("highland-clearances", "Highland Clearances", "高地清洗", ("exam-07-q13",)),
    ("james-cook", "James Cook", "James Cook", ("exam-14-q11",)),
    ("victorian-britain", "Victorian Britain", "维多利亚时代", ("exam-09-q24", "exam-09-q14", "exam-17-q22", "exam-07-q05", "exam-09-q23")),
    ("irish-nationalism-famine", "Ireland in the 19th century", "19世纪爱尔兰", ("exam-15-q17", "exam-17-q02")),
    ("union-jack", "Union Jack", "英国国旗", ("exam-12-q22",)),
    ("rutherford-atom", "Rutherford & the atom", "Rutherford与原子", ("exam-15-q12",)),
    ("first-world-war-end", "End of the First World War", "一战结束", ("exam-10-q21",)),
    ("great-depression", "Great Depression", "经济大萧条", ("exam-03-q22",)),
    ("butler-act", "Butler Act", "Butler Act", ("exam-09-q21",)),
    ("clement-attlee", "Clement Attlee", "Clement Attlee", ("exam-14-q18",)),
    ("modern-british-inventions", "Modern inventions", "现代发明", ("exam-04-q22", "exam-12-q15", "exam-15-q10")),
    ("ireland-republic", "Ireland becomes a republic", "爱尔兰共和国", ("exam-02-q06",)),
    ("mary-peters", "Mary Peters", "Mary Peters", ("exam-15-q08",)),
    ("coalition-2010", "2010 coalition", "2010联合政府", ("exam-06-q16",)),
    # Politics
    ("prime-minister-residence", "Prime Minister's residence", "首相官邸", ("exam-04-q23",)),
    ("election-ages", "Voting & candidacy ages", "选举年龄", ("exam-09-q13", "exam-04-q21", "exam-13-q14")),
    ("welsh-government", "Welsh government", "威尔士政府", ("exam-10-q10", "exam-08-q20")),
    ("poll-card", "Poll card", "投票卡", ("exam-01-q17",)),
    ("northern-ireland-elections", "Northern Ireland elections", "北爱选举", ("exam-14-q02",)),
    ("by-elections", "By-elections", "补选", ("exam-08-q23",)),
    ("local-government", "Local government", "地方政府", ("exam-12-q06",)),
    ("hansard", "Hansard", "Hansard", ("exam-14-q08",)),
    ("broadcast-impartiality", "Broadcast impartiality", "广播公正", ("exam-11-q10",)),
    ("commonwealth", "Commonwealth", "英联邦", ("exam-16-q21",)),
    ("unwritten-constitution", "Unwritten constitution", "不成文宪法", ("exam-10-q24",)),
    ("constitutional-institutions", "Constitutional institutions", "宪法机构", ("exam-17-q01",)),
    ("monarch-duties", "Monarch's duties", "君主职责", ("exam-17-q10",)),
    ("parliamentary-democracy", "Parliamentary democracy", "议会民主", ("exam-14-q16",)),
    # Geography
    ("wales-places", "Places in Wales", "威尔士地点", ("exam-03-q11", "exam-03-q21", "exam-06-q15")),
    ("uk-capitals", "UK capital cities", "英国首都", ("exam-09-q09", "exam-07-q11")),
    ("uk-location", "UK location", "英国位置", ("exam-01-q04",)),
    ("uk-coins", "UK coins", "英国硬币", ("exam-05-q02",)),
    ("uk-population", "UK population", "英国人口", ("exam-16-q11",)),
    ("women-workforce", "Women in the workforce", "女性劳动力", ("exam-12-q24",)),
    ("eden-project", "Eden Project", "Eden Project", ("exam-05-q03",)),
    ("big-ben", "Big Ben", "Big Ben", ("exam-01-q02",)),
    ("national-trust", "National Trust", "National Trust", ("exam-04-q06",)),
    # Religion and holidays
    ("halloween", "Halloween", "Halloween", ("exam-07-q02",)),
    ("eid-al-fitr", "Eid al-Fitr", "Eid al-Fitr", ("exam-03-q24",)),
    ("church-of-scotland", "Church of Scotland", "苏格兰教会", ("exam-05-q07",)),
    # Law and everyday life
    ("driving-licence", "Driving licence", "驾驶执照", ("exam-10-q08",)),
    ("criminal-civil-law", "Criminal & civil law", "刑事与民事法律", ("exam-04-q19", "exam-05-q16", "exam-07-q07")),
    ("young-offenders-privacy", "Young offenders' privacy", "未成年人隐私", ("exam-10-q11",)),
    ("solicitor-fees", "Solicitor fees", "律师收费", ("exam-01-q18",)),
    ("scottish-criminal-courts", "Scottish criminal courts", "苏格兰刑事法院", ("exam-06-q20",)),
    # Sport and leisure
    ("leisure-age-limits", "Leisure age limits", "年龄限制", ("exam-11-q24", "exam-14-q15")),
    ("olympic-games", "Olympic Games", "奥运会", ("exam-14-q19", "exam-12-q20")),
    ("crathes-castle", "Crathes Castle", "Crathes Castle", ("exam-13-q23",)),
    ("national-flowers", "National flowers", "国花", ("exam-04-q02", "exam-16-q19", "exam-08-q02")),
    ("british-film", "British film", "英国电影", ("exam-14-q04", "exam-15-q04", "exam-16-q05")),
    ("shopping-hours", "Shopping hours", "商店营业", ("exam-13-q20",)),
    ("bbc-independence", "BBC independence", "BBC独立性", ("exam-12-q02",)),
    ("traditional-food", "Traditional food", "传统食物", ("exam-06-q19", "exam-14-q17")),
    ("the-ashes", "The Ashes", "The Ashes", ("exam-07-q04",)),
    ("six-nations", "Six Nations", "Six Nations", ("exam-14-q09",)),
    ("boat-race", "The Boat Race", "牛津剑桥划船赛", ("exam-10-q23",)),
    ("wimbledon", "Wimbledon", "Wimbledon", ("exam-12-q11",)),
    # Culture and inventions
    ("visual-art", "Visual art", "视觉艺术", ("exam-08-q24", "exam-13-q24", "exam-02-q08", "exam-12-q07")),
    ("classical-music", "Classical music", "古典音乐", ("exam-10-q19", "exam-10-q12")),
    ("cenotaph", "The Cenotaph", "The Cenotaph", ("exam-11-q12",)),
    ("edinburgh-fringe", "Edinburgh Fringe", "Fringe", ("exam-10-q09",)),
    ("british-literature", "British literature", "英国文学", ("exam-08-q22", "exam-03-q12", "exam-05-q23")),
    # Civic responsibility
    ("school-governors", "School governors", "学校管理委员会", ("exam-03-q17",)),
    ("canvassing", "Canvassing", "拉票", ("exam-05-q22",)),
)

FALLBACK_TOPIC_LOOKUP = {
    question_id: (topic_id, title_en, title_zh)
    for topic_id, title_en, title_zh, question_ids in FALLBACK_TOPIC_DEFINITIONS
    for question_id in question_ids
}

# History title-two headings use one concise period label and are ordered by
# the start of that period. Dates are learning labels, not changes to the
# authorized question text.
HISTORY_TOPIC_PERIODS = {
    "prehistoric-era": (-10000, "before AD 43", "公元43年以前"),
    "roman-era": (-55, "55 BC-AD 410", "公元前55年-公元410年"),
    "early-medieval-era": (410, "AD 410-1066", "410-1066年"),
    "medieval-era": (1066, "1066-1485", "1066-1485年"),
    "tudor-era": (1485, "1485-1603", "1485-1603年"),
    "stuart-era": (1603, "1603-1714", "1603-1714年"),
    "hanoverian-era": (1714, "1714-1837", "1714-1837年"),
    "victorian-empire-era": (1837, "1837-1902", "1837-1902年"),
    "democracy-ww1-era": (1903, "1903-1928", "1903-1928年"),
    "ww2-era": (1930, "1930-1949", "1930-1949年"),
    "prehistoric-britain": (-10000, "Prehistory", "史前时期"),
    "first-farmers": (-4000, "c. 4000 BC", "约公元前4000年"),
    "iron-age-coins": (-100, "c. 100 BC", "约公元前100年"),
    "roman-britain": (-55, "55 BC-AD 410", "公元前55年-公元410年"),
    "anglo-saxon-britain": (410, "AD 410-1066", "410-1066年"),
    "norman-conquest": (1066, "1066", "1066年"),
    "english-language-origins": (1066.1, "after 1066", "1066年以后"),
    "domesday-book": (1086, "1086", "1086年"),
    "medieval-society": (1100, "Middle Ages", "中世纪"),
    "magna-carta": (1215, "1215", "1215年"),
    "bannockburn-robert-bruce": (1314, "1314", "1314年"),
    "hundred-years-war": (1337, "1337-1453", "1337-1453年"),
    "black-death": (1348, "1348-1350", "1348-1350年"),
    "canterbury-tales": (1387, "late 14th century", "14世纪后期"),
    "wars-roses": (1455, "1455-1485", "1455-1485年"),
    "henry-viii-reformation": (1534, "1530s", "16世纪30年代"),
    "protestant-britain": (1560, "from 1560", "1560年起"),
    "james-i": (1603, "1603-1625", "1603-1625年"),
    "mary-queen-scots": (1542, "1542-1587", "1542-1587年"),
    "shakespeare": (1564, "1564-1616", "1564-1616年"),
    "spanish-armada-elizabeth": (1588, "1588", "1588年"),
    "civil-war-cromwell": (1642, "1642-1660", "1642-1660年"),
    "charles-ii": (1660, "1660-1685", "1660-1685年"),
    "great-fire-london": (1666, "1666", "1666年"),
    "habeas-corpus": (1679, "1679", "1679年"),
    "huguenots": (1680, "1680-1720", "1680-1720年"),
    "glorious-revolution": (1688, "1688-1689", "1688-1689年"),
    "glencoe-massacre": (1692, "1692", "1692年"),
    "enlightenment": (1700, "18th century", "18世纪"),
    "britain-france-trade": (1700.1, "18th century", "18世纪"),
    "robert-walpole": (1721, "from 1721", "1721年起"),
    "bonnie-prince-charlie": (1745, "1745-1746", "1745-1746年"),
    "highland-clearances": (1750, "18th-19th centuries", "18-19世纪"),
    "industrial-revolution": (1760, "c. 1760-1840", "约1760-1840年"),
    "james-cook": (1770, "18th century", "18世纪"),
    "american-independence": (1776, "1776", "1776年"),
    "admiral-nelson-trafalgar": (1805, "1805", "1805年"),
    "slavery-abolition": (1807, "1807-1833", "1807-1833年"),
    "union-jack": (1807.1, "from 1801", "1801年起"),
    "battle-waterloo": (1815, "1815", "1815年"),
    "victorian-britain": (1837, "1837-1901", "1837-1901年"),
    "irish-nationalism-famine": (1845, "19th century", "19世纪"),
    "crimean-war": (1853, "1853-1856", "1853-1856年"),
    "boer-war": (1899, "1899-1902", "1899-1902年"),
    "women-suffrage": (1903, "1903-1928", "1903-1928年"),
    "first-world-war": (1914, "1914-1918", "1914-1918年"),
    "first-world-war-end": (1918, "1918", "1918年"),
    "rutherford-atom": (1919, "early 20th century", "20世纪初"),
    "great-depression": (1930, "1930s", "20世纪30年代"),
    "modern-british-inventions": (1930.1, "20th century", "20世纪"),
    "germany-poland-1939": (1939, "1939", "1939年"),
    "second-world-war-churchill": (1939.1, "1939-1945", "1939-1945年"),
    "battle-britain": (1940, "1940", "1940年"),
    "butler-act": (1944, "1944", "1944年"),
    "clement-attlee": (1945, "1945", "1945年"),
    "ireland-republic": (1949, "1949", "1949年"),
    "swinging-sixties": (1960, "1960s", "20世纪60年代"),
    "margaret-thatcher": (1979, "1979-1990", "1979-1990年"),
    "mary-peters": (1972, "1972", "1972年"),
    "coalition-2010": (2010, "2010", "2010年"),
}


def normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def english_display_text(value: str) -> str:
    """Use ASCII punctuation in generated study text without altering source data."""
    return value.translate(
        str.maketrans(
            {
                "‘": "'",
                "’": "'",
                "“": '"',
                "”": '"',
                "–": "-",
                "—": "-",
            }
        )
    )


def topic_for(item: dict) -> tuple[str, str, str] | None:
    if fallback_topic := FALLBACK_TOPIC_LOOKUP.get(item["id"]):
        return fallback_topic
    learning = item.get("learning", {})
    searchable = " ".join(
        [item["question"], *item["correct_answers"], *learning.get("keywords", [])]
    )
    for topic_id, title_en, title_zh, patterns in TOPIC_RULES:
        if any(re.search(pattern, searchable, re.IGNORECASE) for pattern in patterns):
            title_en, title_zh = TOPIC_TITLE_OVERRIDES.get(
                topic_id, (title_en, title_zh)
            )
            return topic_id, title_en, title_zh
    return None


def fact_key(item: dict) -> tuple:
    if fact_id := FACT_ID_LOOKUP.get(item["id"]):
        return ("semantic-fact", fact_id)
    topic = topic_for(item)
    if topic:
        for topic_id, fact_id, question_patterns in FACT_RULES:
            if topic[0] == topic_id and any(
                re.search(pattern, item["question"], re.IGNORECASE)
                for pattern in question_patterns
            ):
                return ("semantic-fact", fact_id)
    return (
        "exact-question",
        normalise(item["question"]),
        tuple(normalise(answer) for answer in item["correct_answers"]),
    )


def supersection_for(item: dict) -> str:
    topic = topic_for(item)
    if topic and topic[0] in TOPIC_SUPERSECTION_OVERRIDES:
        return TOPIC_SUPERSECTION_OVERRIDES[topic[0]]
    return CATEGORY_SUPERSECTIONS[item["category_name"]]


def display_topic_for(
    topic: tuple[str, str, str], section_id: str
) -> tuple[str, str, str]:
    topic_groups = TOPIC_GROUPS_BY_SECTION.get(section_id, {})
    if topic[0] in topic_groups:
        _, topic_id, title_en, title_zh = topic_groups[topic[0]]
        return topic_id, title_en, title_zh
    return topic


def source_topic_order(section_id: str, topic_id: str | None) -> int:
    if not topic_id:
        return 10_000
    topic_groups = TOPIC_GROUPS_BY_SECTION.get(section_id, {})
    try:
        return list(topic_groups).index(topic_id)
    except ValueError:
        return 10_000


def question_relevance_key(item: dict) -> tuple[int, str]:
    """Order related rows from the core fact towards supporting detail."""
    question = normalise(item["question"])
    if re.match(r"^(what (?:is|are)|who (?:is|was)|which .+ (?:is|are|was|were))\b", question):
        priority = 0
    elif re.match(r"^(what (?:did|does|do|happened)|why|how)\b", question):
        priority = 1
    elif question.startswith("when "):
        priority = 2
    elif question.startswith("where "):
        priority = 3
    elif len(item["correct_answers"]) == 1 and normalise(item["correct_answers"][0]) in BOOLEAN_ANSWERS:
        priority = 4
    else:
        priority = 1
    return priority, question


def main() -> None:
    questions = []
    for exam_number in range(1, 18):
        exam_path = ENRICHED_DIR / f"exam-{exam_number:02d}.json"
        questions.extend(json.loads(exam_path.read_text())["questions"])

    # Keep every named title-two topic together even when its source questions
    # came from different handbook chapters. Explicit learner-facing overrides
    # win; otherwise the topic uses the broad section of its first occurrence.
    topic_home_supersections: dict[str, str] = {}
    for question in questions:
        topic = topic_for(question)
        if topic:
            topic_home_supersections.setdefault(topic[0], supersection_for(question))

    category_questions: dict[str, list[dict]] = defaultdict(list)
    for question in questions:
        topic = topic_for(question)
        section_id = (
            topic_home_supersections[topic[0]] if topic else supersection_for(question)
        )
        category_questions[section_id].append(question)

    sections = []
    grouped_total = 0
    for section_id, items in category_questions.items():
        groups: dict[tuple, list[dict]] = defaultdict(list)
        for item in items:
            answers = tuple(normalise(answer) for answer in item["correct_answers"])
            topic = topic_for(item)
            if fact_id := FACT_ID_LOOKUP.get(item["id"]):
                key = ("fact", fact_id)
            elif topic:
                key = ("topic", topic[0])
            elif len(answers) == 1 and answers[0] in BOOLEAN_ANSWERS:
                key = ("statement", normalise(item["question"]), answers)
            else:
                key = ("answer", answers)
            groups[key].append(item)

        grouped_rows = []
        for key, grouped_items in groups.items():
            topic_metadata = None
            source_topic_id = None
            if key[0] in {"topic", "fact"}:
                topic = next(
                    (candidate for item in grouped_items if (candidate := topic_for(item))),
                    None,
                )
                if topic:
                    source_topic_id = topic[0]
                    topic = display_topic_for(topic, section_id)
                    topic_metadata = {
                        "topic_id": topic[0],
                        "topic_en": topic[1],
                        "topic_zh": topic[2],
                    }
            sort_label = (
                topic_metadata["topic_en"]
                if topic_metadata
                else " / ".join(grouped_items[0]["correct_answers"])
            )
            grouped_rows.append(
                (
                    len(grouped_items),
                    normalise(sort_label),
                    grouped_items,
                    topic_metadata,
                    source_topic_id,
                )
            )

        rows = []
        def group_sort_key(group: tuple) -> tuple:
            frequency, label, _, topic_metadata, source_topic_id = group
            if section_id in TOPIC_GROUPS_BY_SECTION and topic_metadata:
                source_definition = TOPIC_GROUPS_BY_SECTION[section_id].get(source_topic_id)
                topic_order = source_definition[0] if source_definition else float("inf")
                detail_definition = (
                    HISTORY_DETAIL_GROUPS.get(source_topic_id)
                    if section_id == "history"
                    else None
                )
                detail_order = (
                    detail_definition[0]
                    if detail_definition
                    else source_topic_order(section_id, source_topic_id)
                )
                return (
                    topic_order,
                    detail_order,
                    source_topic_order(section_id, source_topic_id),
                    label,
                )
            if section_id == "history" and topic_metadata:
                period = HISTORY_TOPIC_PERIODS.get(topic_metadata["topic_id"])
                return (period[0] if period else float("inf"), label)
            return (-frequency, label, source_topic_order(section_id, source_topic_id))

        for frequency, _, grouped_items, topic_metadata, source_topic_id in sorted(
            grouped_rows, key=group_sort_key
        ):
            display_groups: dict[tuple, list[dict]] = {}
            for item in sorted(
                grouped_items,
                key=lambda question: (question["exam_number"], question["number"]),
            ):
                display_groups.setdefault(fact_key(item), []).append(item)

            for display_key, equivalent_items in sorted(
                display_groups.items(),
                key=lambda display_group: question_relevance_key(display_group[1][0]),
            ):
                item = equivalent_items[0]
                canonical = (
                    FACT_CANONICAL_DISPLAY.get(display_key[1])
                    if display_key[0] == "semantic-fact"
                    else None
                )
                row = {
                    "prompts": [
                        english_display_text(value)
                        for value in (
                            canonical["prompts"] if canonical else [item["question"]]
                        )
                    ],
                    "answers": [
                        english_display_text(value)
                        for value in (
                            canonical["answers"]
                            if canonical
                            else item["correct_answers"]
                        )
                    ],
                    "frequency": frequency,
                    "question_ids": [question["id"] for question in equivalent_items],
                }
                if topic_metadata:
                    row.update(topic_metadata)
                    if section_id == "history":
                        detail_topic = HISTORY_DETAIL_GROUPS.get(source_topic_id)
                        if detail_topic:
                            row.update(
                                {
                                    "detail_topic_sort": detail_topic[0],
                                    "detail_topic_id": detail_topic[1],
                                    "detail_topic_en": detail_topic[2],
                                    "detail_topic_zh": detail_topic[3],
                                }
                            )
                        period = HISTORY_TOPIC_PERIODS.get(topic_metadata["topic_id"])
                        if period:
                            row.update(
                                {
                                    "topic_period_sort": period[0],
                                    "topic_period_en": period[1],
                                    "topic_period_zh": period[2],
                                }
                            )
                rows.append(row)

        grouped_total += len(rows)
        sections.append(
            {
                "id": section_id,
                "title_en": SUPERSECTIONS[section_id][0],
                "title_zh": SUPERSECTIONS[section_id][1],
                "question_count": len(items),
                "rows": rows,
            }
        )

    sections.sort(key=lambda section: (-section["question_count"], section["title_en"]))
    payload = {
        "dataset": "life-in-the-uk-quick-reference",
        "source_question_count": len(questions),
        "group_count": grouped_total,
        "sections": sections,
    }
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    DATA_OUTPUT.write_text(encoded)
    WEB_OUTPUT.write_text(encoded)
    print(json.dumps({"questions": len(questions), "groups": grouped_total, "sections": len(sections)}))


if __name__ == "__main__":
    main()
