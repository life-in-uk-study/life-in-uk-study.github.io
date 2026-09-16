#!/usr/bin/env python3
"""Add explanations, authority references, and answer-aligned learning visuals."""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
IMAGE_DIR = ROOT / "public" / "images" / "questions"
AI_IMAGE_DIR = ROOT / "public" / "images" / "ai"
TRANSLATION_DIR = DATA / "explanations_zh"
LEARNING_OVERRIDE_DIR = DATA / "learning_overrides"
ENRICHED_EXAM_DIR = DATA / "enriched_exams"
WEB_EXAM_DIR = ROOT / "web" / "public" / "data" / "exams"


PALETTES = {
    "history": ("#261F18", "#E8C978", "#FFF7E4"),
    "geography": ("#123C4A", "#75C9C8", "#E8FAF7"),
    "society": ("#37224F", "#CF9FE8", "#FAF1FF"),
    "government": ("#152B45", "#E4B64E", "#F7F2E8"),
    "values": ("#173A32", "#75C49A", "#F0FBF5"),
}


LEARNING_OVERRIDES = {
    "exam-02-q01": {
        "why_correct_en": (
            "Policing is the correct answer. The Home Secretary leads the Home Office, "
            "whose responsibilities include policing, crime, counter-terrorism, borders, "
            "immigration and passports."
        ),
        "source_ids": [
            "official-handbook",
            "govuk-home-office-about",
        ],
    },
    "exam-02-q02": {
        "why_correct_en": (
            "False. St Helena forms part of the British Overseas Territory of Saint Helena, "
            "Ascension and Tristan da Cunha. British Overseas Territories are constitutionally "
            "separate from the United Kingdom and are not independent sovereign states. The UK "
            "is responsible for their defence and external affairs, while each has its own written "
            "constitution and local government. Eligible people connected with St Helena may hold "
            "British Overseas Territories citizenship and, under the 2002 legislation, many also "
            "hold British citizenship. Birth there alone does not always confer citizenship; the "
            "date of birth and the parents' status matter."
        ),
        "source_ids": [
            "official-handbook",
            "ons-uk-geographies",
            "govuk-overseas-territories-constitutional-status",
            "st-helena-constitution-2009",
            "govuk-british-overseas-territories-citizenship",
        ],
    },
    "exam-02-q04": {
        "why_correct_en": (
            "Dogs on a highway or in a public place in England, Wales and Scotland must wear "
            "a collar bearing the owner's name and address, either on the collar itself or on "
            "an attached tag. A microchip does not replace this requirement. Failure to comply "
            "is an offence: a local authority officer may seize the dog and treat it as a stray, "
            "and the owner may be prosecuted. The offence carries a level 5 fine; this is unlimited "
            "in England and Wales and normally capped at £5,000 in Scotland, with the actual amount "
            "set by the court. In a 2025 Plymouth case, the collar-and-tag offence resulted in a "
            "£220 fine plus costs and a surcharge. Northern Ireland has a separate dog-control regime."
        ),
        "source_ids": [
            "official-handbook",
            "control-of-dogs-order-1992",
            "govuk-dog-ownership-enforcement-manual",
            "plymouth-collar-tag-case-2025",
            "nidirect-controlling-dog-public",
        ],
    },
    "exam-02-q05": {
        "why_correct_en": (
            "The First World War is the correct answer. Women made munitions, explosives "
            "and aircraft parts; served as nurses and VAD volunteers; worked in agriculture "
            "through the Women's Land Army; took jobs in transport, policing, postal services "
            "and government offices; and joined women's services such as the Wrens, performing "
            "communications, electrical and shore-based duties that released more men for the "
            "front. This work made women's labour and social value more visible. However, the "
            "limited female franchise introduced in 1918 also resulted from the long suffrage "
            "campaign and wider electoral reform, so it should not be described simply as a "
            "reward for wartime service."
        ),
        "source_ids": [
            "official-handbook",
            "national-archives-women-first-world-war",
            "parliament-suffrage-wartime",
            "parliament-did-war-make-a-difference",
        ],
    },
    "exam-01-q02": {
        "why_correct_en": (
            "Big Ben is the nickname of the Great Bell in the Elizabeth Tower at "
            "the Houses of Parliament in London. UK Parliament says the name was "
            "probably a playful reference to Sir Benjamin Hall MP, the tall First "
            "Commissioner of Works who oversaw the later stages of the tower; the "
            "exact origin is not certain."
        ),
        "source_ids": ["official-handbook", "parliament-big-ben-construction"],
    },
    "exam-01-q05": {
        "why_correct_en": (
            "The patron Saint of Scotland is St Andrew. Several legends connect him "
            "with Scotland; the best known says that St Rule brought some of his relics "
            "to the place now called St Andrews. He had been honoured in Scotland for "
            "more than a thousand years, and the 1320 Declaration of Arbroath invoked "
            "him as Scotland's protector, strengthening his status as the national "
            "patron saint. The X-shaped cross in Rubens's painting is the symbol of his "
            "martyrdom and became the Saltire on Scotland's flag."
        ),
        "source_ids": [
            "official-handbook",
            "scotland-st-andrew",
            "prado-rubens-saint-andrew",
            "rubens-saint-andrew-image",
        ],
    },
    "exam-01-q06": {
        "why_correct_en": (
            "The correct answers are the House of York and the House of Lancaster, "
            "rival branches of the Plantagenet royal family whose supporters fought "
            "for the English Crown.\n\n"
            "It is called the Wars of the Roses because rose badges became linked "
            "with the rival causes: York's white rose and Lancaster's red rose. "
            "These were heraldic badges used to show allegiance, not the families' "
            "complete coats of arms.\n\n"
            "Roses were already common in medieval heraldry. The white rose came "
            "from Edmund of Langley, first Duke of York; Lancaster adopted the red "
            "rose. After 1485, Henry VII combined them as the Tudor Rose to present "
            "the two houses as reconciled."
        ),
        "source_ids": [
            "official-handbook",
            "national-archives-wars-of-roses",
            "english-heritage-rose-symbols",
            "royal-collection-medieval-palace",
        ],
    },
    "exam-01-q07": {
        "why_correct_en": (
            "The statement is false. The Bill of Rights did not give every adult "
            "man the vote; it defined limits on the Crown and protected the rights "
            "of Parliament and subjects.\n\n"
            "The Crown could not suspend or dispense with laws, levy taxes, or keep "
            "a standing army in peacetime without Parliament's consent. Subjects "
            "also had the right to petition the monarch.\n\n"
            "Parliamentary elections were to be free, parliamentary speech protected, "
            "and Parliaments held frequently. Excessive bail and fines and cruel or "
            "unusual punishments were barred. These controls limited royal power; "
            "they did not create universal suffrage."
        ),
        "source_ids": [
            "official-handbook",
            "parliament-bill-of-rights-1689",
            "national-archives-declaration-of-rights",
        ],
    },
    "exam-01-q08": {
        "why_correct_en": (
            "The correct answer is a war memorial. A cenotaph is not one unique "
            "monument: it is a type of memorial for people whose remains are buried "
            "elsewhere. The word comes from Greek and means 'empty tomb'.\n\n"
            "In this question, the capital letter and 'the' point to the Cenotaph on "
            "Whitehall in Westminster, central London, close to Parliament Square and "
            "the Houses of Parliament. Its address is Whitehall, London SW1A 2ET.\n\n"
            "Edwin Lutyens first designed it as a temporary memorial in 1919; the "
            "permanent stone version was unveiled in 1920. No body is buried inside it. "
            "The Unknown Warrior's tomb is nearby in Westminster Abbey.\n\n"
            "It does not commemorate one named person and carries no individual names. "
            "Its inscription, 'THE GLORIOUS DEAD', collectively honours the dead of the "
            "two World Wars and later conflicts; national remembrance also includes "
            "British and Commonwealth military and civilian service."
        ),
        "source_ids": [
            "official-handbook",
            "english-heritage-cenotaph",
            "english-heritage-cenotaph-history",
            "iwm-cenotaph-register",
        ],
    },
    "exam-01-q09": {
        "why_correct_en": (
            "Margaret Thatcher became Prime Minister on 4 May 1979, making her the "
            "UK's first woman Prime Minister. She served until November 1990 and won "
            "three consecutive general elections.\n\n"
            "The nickname has a precise origin. On 19 January 1976, while Leader of the "
            "Opposition, Thatcher's 'Britain Awake' speech warned about Soviet military "
            "expansion and called for stronger Western defence.\n\n"
            "On 24 January, the Soviet Army newspaper Red Star called her the 'Iron "
            "Lady'. It was intended as a hostile Cold War caricature: uncompromising, "
            "anti-Soviet and militaristic.\n\n"
            "She turned the attack into a brand. On 31 January she jokingly presented "
            "herself as the 'Iron Lady of the Western world' and said the label suited "
            "her defence of Western values and freedoms."
        ),
        "source_ids": [
            "official-handbook",
            "govuk-margaret-thatcher",
            "parliament-thatcher-tributes",
            "thatcher-foundation-britain-awake",
            "thatcher-foundation-iron-lady-response",
            "parliament-thatcher-booklet",
        ],
    },
    "exam-01-q10": {
        "why_correct_en": (
            "The Speaker chairs debates in the House of Commons, keeps order, applies "
            "the House's rules and decides which MPs may speak.\n\n"
            "The Speaker is not appointed by the Prime Minister. The office is held by "
            "an MP elected by the other MPs; after election, the Speaker must act "
            "politically impartially. As of August 2026, the Speaker is Sir Lindsay "
            "Hoyle, MP for Chorley, who has held the office since 4 November 2019.\n\n"
            "During debates, the Speaker sits on the raised Speaker's Chair at the north "
            "end of the Commons Chamber, at the end of the Table of the House, facing "
            "the opposing rows of green benches. From the Speaker's point of view, the "
            "Government sits on the right and the Opposition on the left."
        ),
        "source_ids": [
            "official-handbook",
            "parliament-commons-speaker",
            "parliament-commons-chamber-guide",
        ],
    },
    "exam-01-q11": {
        "why_correct_en": (
            "Bobby Moore captained England when they won the 1966 FIFA World Cup. "
            "He played as a central defender, a position commonly called centre-half "
            "in his era.\n\n"
            "He first captained England at the age of 22. Across 108 international "
            "appearances, he wore the captain's armband 90 times and won 57 of those "
            "matches. He remains the only England captain to have lifted the men's "
            "World Cup."
        ),
        "source_ids": [
            "official-handbook",
            "fa-bobby-moore-captain",
        ],
    },
    "exam-01-q12": {
        "why_correct_en": (
            "The Spanish Armada was the large invasion fleet sent by King Philip II "
            "of Spain in 1588.\n\n"
            "Armada is a Spanish word for an armed fleet or navy. In Spain the force is "
            "usually called the Gran Armada; 'Invincible Armada' was not an official "
            "name chosen by Philip II. Spanish naval-history material says the label was "
            "coined and spread in England, becoming especially ironic after the fleet's "
            "defeat. The Chinese name '西班牙无敌舰队' follows that traditional label.\n\n"
            "This happened during the reign of Elizabeth I, Queen of England and Ireland "
            "from 1558 to 1603. Philip II's invasion was intended to overthrow her and "
            "restore a Catholic ruler in England."
        ),
        "source_ids": [
            "official-handbook",
            "national-archives-spanish-armada",
            "spanish-navy-gran-armada-name",
        ],
    },
    "exam-01-q13": {
        "why_correct_en": (
            "The statement is true: writing to the Chief Constable is a way to complain "
            "to the police force involved. A Chief Constable is the most senior officer "
            "who leads a local police force; this does not mean that they personally "
            "handle each complaint. Complaints are usually managed by the force's "
            "Professional Standards Department.\n\n"
            "In England and Wales, you can complain directly to the force online, by "
            "calling 101, at a police station or in writing. You can also use the IOPC "
            "form, which normally forwards the complaint to the relevant force. The "
            "force assesses and records it; the most serious matters must be referred "
            "to the IOPC. After the outcome, the notice explains whether and where you "
            "can request a review, normally within 28 days."
        ),
        "source_ids": [
            "official-handbook",
            "college-policing-chief-constable",
            "iopc-complaints-process",
        ],
    },
    "exam-01-q14": {
        "why_correct_en": (
            "The minimum age in the exam answer is 18. Jury service gives ordinary "
            "members of the public a direct role in the justice system. In an England "
            "and Wales Crown Court trial, 12 jurors listen to the evidence and decide "
            "whether the defendant is guilty.\n\n"
            "The judge and jury have different jobs: the judge explains the law and "
            "manages the trial, while the jury weighs the evidence, decides the facts "
            "and returns the verdict. If the verdict is guilty, the judge—not the "
            "jury—decides the sentence. Jury rules differ in Scotland and Northern "
            "Ireland."
        ),
        "source_ids": [
            "official-handbook",
            "govuk-jury-service",
            "judiciary-criminal-jurisdiction",
        ],
    },
    "exam-01-q15": {
        "why_correct_en": (
            "Jurors are selected at random from the electoral register. This is why "
            "being registered to vote can also lead to a jury summons.\n\n"
            "Jury service gives ordinary members of the public a direct role in the "
            "justice system. In an England and Wales Crown Court trial, 12 jurors listen "
            "to the evidence, decide what facts have been proved and return the verdict. "
            "The judge explains the law and, after a guilty verdict, decides the sentence. "
            "Jury rules differ in Scotland and Northern Ireland."
        ),
        "source_ids": [
            "official-handbook",
            "govuk-jury-service",
            "judiciary-criminal-jurisdiction",
        ],
    },
    "exam-01-q16": {
        "why_correct_en": (
            "Bank holidays are public holidays when banks and many other businesses "
            "close, although employees do not automatically have a legal right to paid "
            "leave on these dates.\n\n"
            "The name comes from the Bank Holidays Act 1871. It made specified days "
            "closing days for banks and allowed bills and promissory notes due on those "
            "days to be dealt with on the next working day. The Act was promoted by the "
            "banker, scientist and MP Sir John Lubbock. People were so pleased with the "
            "new holidays that they briefly nicknamed them 'St Lubbock's Days'. What "
            "began as bank closures gradually became holidays observed much more widely."
        ),
        "source_ids": [
            "official-handbook",
            "govuk-bank-holidays",
            "bank-holidays-act-1871",
            "parliament-bank-holidays-history",
        ],
    },
    "exam-01-q17": {
        "why_correct_en": (
            "Before an election, a registered voter is sent a poll card. It is an "
            "information notice, not the ballot paper, so you do not write your vote "
            "on it.\n\n"
            "A poll card normally shows your name and address, elector number, the "
            "election and polling date, polling hours, your assigned polling station "
            "and information about how you are registered to vote. It may also remind "
            "you about voter ID or important deadlines. For most voters it is helpful "
            "but not required at the polling station; an anonymous elector must take "
            "their poll card. The actual vote is marked later on a ballot paper."
        ),
        "source_ids": [
            "official-handbook",
            "govuk-voting-in-person",
            "legislation-sample-poll-card",
            "electoral-commission-anonymous-voting",
        ],
    },
    "exam-01-q18": {
        "why_correct_en": (
            "The statement is correct because solicitors and barristers may charge by "
            "the hour, although fixed fees and conditional arrangements are also used. "
            "There is no standard UK-wide market average: price varies by work, region, "
            "experience and complexity.\n\n"
            "For scale, the 2026 England and Wales court-cost guidelines range from "
            "£288–£579 an hour for lawyers with over eight years' experience, £247–£393 "
            "for over four years, £200–£305 for other qualified fee earners, and "
            "£142–£210 for trainees or paralegals. London commercial work is highest.\n\n"
            "These figures help courts assess recoverable costs; they are not compulsory "
            "retail prices. VAT and expenses may be extra. The SRA requires published "
            "prices for certain common solicitor services, while each barrister sets "
            "their own fees."
        ),
        "source_ids": [
            "official-handbook",
            "govuk-solicitor-guideline-hourly-rates",
            "sra-price-transparency",
            "bsb-barrister-fees",
        ],
    },
    "exam-01-q19": {
        "why_correct_en": (
            "The exam answer is Television and Radio because these broadcast services "
            "are subject to statutory impartiality rules. Sections 319 and 320 of the "
            "Communications Act 2003 require Ofcom to set standards for due impartiality; "
            "Ofcom applies them through Sections Five and Six of the Broadcasting Code.\n\n"
            "The wording 'equal time' in the question is an oversimplification. Ofcom "
            "expressly says that due impartiality does not require an equal division of "
            "airtime for every view. During an election, broadcasters must give parties "
            "and independent candidates due weight, considering evidence of past and "
            "current support, and must consider significant perspectives. The amount of "
            "coverage may therefore differ, but it must not unfairly favour one side. "
            "Newspapers and ordinary internet publishers are not governed by these same "
            "broadcast-impartiality provisions."
        ),
        "source_ids": [
            "official-handbook",
            "communications-act-2003-impartiality",
            "ofcom-due-impartiality",
            "ofcom-elections-referendums",
        ],
    },
    "exam-01-q20": {
        "why_correct_en": (
            "The Channel Islands lie in the English Channel off Normandy. They comprise "
            "two Crown Dependencies: Jersey and Guernsey, the latter including Alderney "
            "and Sark.\n\n"
            "They are neither part of the United Kingdom nor British Overseas Territories. "
            "They are self-governing possessions of the Crown with their own institutions "
            "and laws. The UK is responsible for defence and some international relations.\n\n"
            "There is no separate Channel Islands citizenship. British nationality law "
            "applies, but birth there after 1 January 1983 does not by itself confer British "
            "citizenship; a parent's citizenship or settled status will normally matter."
        ),
        "source_ids": [
            "official-handbook",
            "jersey-relationship-uk",
            "govuk-crown-dependencies-factsheet",
            "british-nationality-act-1981",
            "jersey-child-passport-nationality",
        ],
    },
    "exam-01-q21": {
        "why_correct_en": (
            "The jet engine is the correct answer. RAF officer and engineer Sir "
            "Frank Whittle developed Britain's first practical turbojet. An early "
            "Power Jets experimental engine ran successfully in 1937, and the "
            "Whittle W.1 then powered the Gloster E.28/39 on the first flight by a "
            "British jet aircraft in May 1941.\n\n"
            "Whittle's work helped open the jet age. Jet propulsion ultimately allowed "
            "aircraft to fly faster and higher than piston-engine, propeller-driven "
            "aircraft, transforming military aviation and later long-distance passenger "
            "travel. Whittle developed his turbojet independently in Britain while Hans "
            "von Ohain pursued a separate jet-engine design in Germany."
        ),
        "source_ids": [
            "official-handbook",
            "science-museum-whittle-jet-engine",
            "raf-museum-whittle-engine",
            "raf-museum-meteor-1944",
        ],
    },
    "exam-01-q22": {
        "why_correct_en": (
            "William Wordsworth wrote the poem commonly called 'Daffodils', whose "
            "title is 'I Wandered Lonely as a Cloud'. Some of its best-known lines are:\n\n"
            "'I wandered lonely as a cloud ...\n"
            "A host, of golden daffodils;\n"
            "And then my heart with pleasure fills,\n"
            "And dances with the daffodils.'"
        ),
        "source_ids": [
            "official-handbook",
            "wordsworth-grasmere-daffodils",
        ],
    },
    "exam-01-q23": {
        "why_correct_en": (
            "Oliver Cromwell is correct. After Charles I was executed in 1649, England "
            "became a Commonwealth. Failed republican experiments left government "
            "increasingly dependent on the army.\n\n"
            "The 1653 Instrument of Government created Lord Protector as head of state "
            "and named the army-backed Cromwell for life. It was a constitutional office, "
            "not a noble title granted by a king.\n\n"
            "There is no Lord Protector today. Cromwell's son Richard briefly succeeded "
            "him but resigned in 1659. Charles II restored the monarchy in 1660, ending "
            "the Protectorate."
        ),
        "source_ids": [
            "official-handbook",
            "parliament-protectorate-parliaments",
            "national-archives-cromwell-protector",
            "royal-family-interregnum",
        ],
    },
    "exam-01-q24": {
        "why_correct_en": (
            "Lent is the Christian season of reflection, penitence and preparation for "
            "Easter. It runs from Ash Wednesday to Easter Eve.\n\n"
            "Its forty days recall Jesus fasting and being tempted in the wilderness for "
            "forty days before beginning his public ministry. Western churches exclude "
            "Sundays from the count, so the calendar span is forty-six days.\n\n"
            "Traditional observance includes fasting, prayer, study and charity. The day "
            "before Lent is Shrove Tuesday; using up eggs, milk and fat before the fast "
            "helped create the British Pancake Day tradition."
        ),
        "source_ids": [
            "official-handbook",
            "church-england-lent-easter",
            "church-england-countdown-easter",
        ],
    },
    "exam-11-q18": {
        "why_correct_en": (
            "The flower is the daffodil. William Wordsworth's poem is commonly called "
            "'Daffodils', although its title is 'I Wandered Lonely as a Cloud'. Some of "
            "its best-known lines are:\n\n"
            "'I wandered lonely as a cloud ...\n"
            "A host, of golden daffodils;\n"
            "And then my heart with pleasure fills,\n"
            "And dances with the daffodils.'\n\n"
            "The remembered sight of the flowers transforms solitude into happiness."
        ),
        "source_ids": [
            "official-handbook",
            "wordsworth-grasmere-daffodils",
        ],
    },
    "exam-13-q15": {
        "why_correct_en": (
            "William Wordsworth was strongly inspired by nature. His poem commonly "
            "called 'Daffodils' is titled 'I Wandered Lonely as a Cloud'. Some of its "
            "best-known lines are:\n\n"
            "'I wandered lonely as a cloud ...\n"
            "A host, of golden daffodils;\n"
            "And then my heart with pleasure fills,\n"
            "And dances with the daffodils.'\n\n"
            "The remembered natural scene continues to give the poet joy even when "
            "he is alone indoors."
        ),
        "source_ids": [
            "official-handbook",
            "wordsworth-grasmere-daffodils",
        ],
    },
    "exam-04-q24": {
        "why_correct_en": (
            "The exam answer is Television and Radio because these broadcast services "
            "are subject to statutory impartiality rules. Sections 319 and 320 of the "
            "Communications Act 2003 require Ofcom to set standards for due impartiality; "
            "Ofcom applies them through Sections Five and Six of the Broadcasting Code.\n\n"
            "The wording 'equal time' in the question is an oversimplification. Ofcom "
            "expressly says that due impartiality does not require an equal division of "
            "airtime for every view. During an election, broadcasters must give parties "
            "and independent candidates due weight, considering evidence of past and "
            "current support, and must consider significant perspectives. The amount of "
            "coverage may therefore differ, but it must not unfairly favour one side. "
            "Newspapers and ordinary internet publishers are not governed by these same "
            "broadcast-impartiality provisions."
        ),
        "source_ids": [
            "official-handbook",
            "communications-act-2003-impartiality",
            "ofcom-due-impartiality",
            "ofcom-elections-referendums",
        ],
    },
    "exam-08-q03": {
        "why_correct_en": (
            "The statement is false because writing to the Chief Constable is not the "
            "only way to complain. A Chief Constable is the most senior officer who "
            "leads a local police force; complaints are normally handled by the force's "
            "Professional Standards Department rather than personally by that officer.\n\n"
            "In England and Wales, you can complain directly to the force online, by "
            "calling 101, at a police station or in writing. You can also use the IOPC "
            "form, which normally forwards the complaint to the relevant force. The "
            "force assesses and records it; the most serious matters must be referred "
            "to the IOPC. The outcome notice explains any right to request a review, "
            "normally within 28 days."
        ),
        "source_ids": [
            "official-handbook",
            "college-policing-chief-constable",
            "iopc-complaints-process",
        ],
    },
    "exam-11-q08": {
        "why_correct_en": (
            "Margaret Thatcher is famous for becoming the UK's first woman Prime "
            "Minister in 1979. She served until November 1990 and won three consecutive "
            "general elections.\n\n"
            "The nickname has a precise origin. On 19 January 1976, while Leader of the "
            "Opposition, Thatcher's 'Britain Awake' speech warned about Soviet military "
            "expansion and called for stronger Western defence.\n\n"
            "On 24 January, the Soviet Army newspaper Red Star called her the 'Iron "
            "Lady'. It was intended as a hostile Cold War caricature: uncompromising, "
            "anti-Soviet and militaristic.\n\n"
            "She turned the attack into a brand. On 31 January she jokingly presented "
            "herself as the 'Iron Lady of the Western world' and said the label suited "
            "her defence of Western values and freedoms."
        ),
        "source_ids": [
            "official-handbook",
            "govuk-margaret-thatcher",
            "parliament-thatcher-tributes",
            "thatcher-foundation-britain-awake",
            "thatcher-foundation-iron-lady-response",
            "parliament-thatcher-booklet",
        ],
    },
    "exam-11-q10": {
        "why_correct_en": (
            "The source set marks this statement true because television and radio are "
            "the media covered by statutory broadcast-impartiality rules. Sections 319 "
            "and 320 of the Communications Act 2003 require Ofcom to set standards for "
            "due impartiality, implemented through the Broadcasting Code.\n\n"
            "However, 'equal time' is not the exact current legal test. Ofcom says due "
            "impartiality does not require equal airtime for every view. During an "
            "election, parties and independent candidates receive due weight based on "
            "factors including past and current support, with significant perspectives "
            "also considered. Coverage can differ in length while still being duly "
            "impartial."
        ),
        "source_ids": [
            "official-handbook",
            "communications-act-2003-impartiality",
            "ofcom-due-impartiality",
            "ofcom-elections-referendums",
        ],
    },
    "exam-11-q17": {
        "why_correct_en": (
            "The two exam answers are to go directly to a police station or write to "
            "the Chief Constable of the force involved. A Chief Constable is the most "
            "senior officer who leads a local police force; complaints are normally "
            "handled by its Professional Standards Department, not personally by the "
            "Chief Constable.\n\n"
            "In England and Wales, complaints can now also be made to the force online "
            "or by calling 101, or through the IOPC form. An IOPC submission is normally "
            "forwarded to the relevant force for assessment and recording. The most "
            "serious matters must be referred to the IOPC. The outcome notice explains "
            "any right to request a review, normally within 28 days."
        ),
        "source_ids": [
            "official-handbook",
            "college-policing-chief-constable",
            "iopc-complaints-process",
        ],
    },
    "exam-17-q05": {
        "why_correct_en": (
            "Margaret Thatcher was the longest-serving UK Prime Minister of the 20th "
            "century. She served from May 1979 until November 1990 and won three "
            "consecutive general elections.\n\n"
            "The nickname has a precise origin. On 19 January 1976, while Leader of the "
            "Opposition, Thatcher's 'Britain Awake' speech warned about Soviet military "
            "expansion and called for stronger Western defence.\n\n"
            "On 24 January, the Soviet Army newspaper Red Star called her the 'Iron "
            "Lady'. It was intended as a hostile Cold War caricature: uncompromising, "
            "anti-Soviet and militaristic.\n\n"
            "She turned the attack into a brand. On 31 January she jokingly presented "
            "herself as the 'Iron Lady of the Western world' and said the label suited "
            "her defence of Western values and freedoms."
        ),
        "source_ids": [
            "official-handbook",
            "govuk-margaret-thatcher",
            "parliament-thatcher-tributes",
            "thatcher-foundation-britain-awake",
            "thatcher-foundation-iron-lady-response",
            "parliament-thatcher-booklet",
        ],
    },
}


LEARNING_OVERRIDES.update(
    {
        "exam-02-q03": {
            "why_correct_en": (
                "The answer is True. Twenty-six Church of England archbishops and "
                "bishops sit in the House of Lords as the Lords Spiritual. They may "
                "debate, scrutinise legislation and vote."
            ),
            "source_ids": ["official-handbook", "parliament-lords-spiritual"],
        },
        "exam-02-q13": {
            "why_correct_en": (
                "The answer is True. Authorised Northern Ireland banks issue notes "
                "denominated in pounds sterling, and the notes can be used across the UK.\n\n"
                "However, 'valid everywhere' does not mean every shop must accept them. "
                "Northern Irish and Scottish banknotes are not legal tender anywhere in "
                "the UK, and businesses may choose which payments to accept."
            ),
            "source_ids": ["official-handbook", "bank-england-legal-tender"],
        },
        "exam-02-q14": {
            "why_correct_en": (
                "A Midsummer Night's Dream is one of William Shakespeare's best-known "
                "comedies. Four young lovers enter a forest near Athens, where Puck's "
                "mistaken use of a love potion makes them fall in love with the wrong "
                "people. The fairy queen Titania is also enchanted and falls in love "
                "with Bottom, whose head has been transformed into that of a donkey. "
                "The spells are eventually corrected and the lovers are reunited at "
                "the wedding celebrations."
            ),
            "source_ids": ["official-handbook", "rsc-midsummer-plot"],
        },
        "exam-02-q15": {
            "why_correct_en": (
                "The correct answer is 12. Criminal juries in England, Wales and "
                "Northern Ireland normally have 12 members; Scotland traditionally "
                "uses 15. US federal criminal juries also usually have 12 members, "
                "although federal civil juries may have 6 to 12 and state rules vary."
            ),
            "source_ids": [
                "official-handbook",
                "us-courts-jury-types",
                "ny-courts-criminal-trial",
            ],
        },
        "exam-02-q16": {
            "why_correct_en": (
                "The correct answer is Hindus and Sikhs. Diwali, or Deepavali, is the "
                "Festival of Lights and usually falls between October and November. "
                "Lighting lamps symbolises light over darkness, good over evil and "
                "knowledge over ignorance. Hindu traditions commonly connect the festival "
                "with Rama and Sita's return to Ayodhya after defeating Ravana, and many "
                "families worship Lakshmi. Sikhs mark Bandi Chhor Divas at the same time, "
                "remembering the release of Guru Hargobind and, according to tradition, "
                "52 other imprisoned princes. Celebrations include diyas, rangoli, family "
                "meals, sweets, gifts, prayer and fireworks."
            ),
            "source_ids": [
                "official-handbook",
                "rcahmw-diwali-festival",
                "rcahmw-bandi-chhor-divas",
            ],
        },
        "exam-02-q17": {
            "why_correct_en": (
                "The correct answer is Good Friday. It commemorates the crucifixion and "
                "death of Jesus. The exact origin of the name is uncertain, but 'good' "
                "may preserve a Middle English sense meaning holy or sacred. In Christian "
                "belief, Jesus's suffering and death also opened the way to redemption "
                "and new life; the day is therefore solemn and sorrowful while still "
                "being called Good Friday."
            ),
            "source_ids": [
                "official-handbook",
                "church-england-lent-easter",
                "etymonline-good-friday",
            ],
        },
        "exam-02-q18": {
            "why_correct_en": (
                "The answer is True. Northern Ireland observes St Patrick's Day as a "
                "public holiday. St Patrick's Day is held on 17 March, traditionally "
                "regarded as the anniversary of Ireland's patron saint's death. Patrick "
                "was probably born in Roman Britain, was taken to Ireland as a slave, "
                "escaped and later returned as a Christian missionary. Originally a "
                "religious feast day, celebrations developed into large parades through "
                "the Irish diaspora and became an international celebration of Irish "
                "culture and identity."
            ),
            "source_ids": [
                "official-handbook",
                "ireland-st-patrick-activity-pack",
                "gov-ie-st-patrick-global",
            ],
        },
        "exam-02-q19": {
            "why_correct_en": (
                "The correct answer is the Norman Conquest of 1066. William, Duke of "
                "Normandy, defeated King Harold's army at the Battle of Hastings, where "
                "Harold died, and was crowned William I. The Normans descended from "
                "Scandinavian Vikings who had settled in northern France; by 1066 they "
                "were French-speaking Christians. William suppressed resistance, replaced "
                "most of the Anglo-Saxon elite with Norman lords, built castles, reorganised "
                "landholding and commissioned Domesday Book. Ordinary people continued to "
                "speak Old English while the court and ruling elite used Norman French, "
                "which contributed many words to modern English, including government, "
                "court, judge, beef and pork."
            ),
            "source_ids": [
                "official-handbook",
                "english-heritage-norman-conquest",
                "english-heritage-william-legacy",
                "national-archives-domesday",
            ],
        },
        "exam-02-q20": {
            "why_correct_en": (
                "The correct answer is the Tower of London. The Crown Jewels are not one "
                "crown but a collection of state regalia including crowns, sceptres, the "
                "Sovereign's Orb and the Coronation Spoon. Parliament ordered most of the "
                "medieval regalia destroyed in 1649; the core of today's collection was "
                "remade for Charles II's coronation in 1661 after the Restoration. St "
                "Edward's Crown is worn only at the moment a new monarch is crowned, while "
                "the Imperial State Crown is used for the coronation procession out of "
                "Westminster Abbey and state occasions such as the State Opening of "
                "Parliament. The monarch holds the collection in trust for the nation, "
                "and it is normally kept at the Tower of London."
            ),
            "source_ids": [
                "official-handbook",
                "hrp-crown-jewels",
                "royal-coronation-regalia",
            ],
        },
        "exam-02-q21": {
            "why_correct_en": (
                "The correct answer is 15th-century Scotland. Scotland's earliest known "
                "written reference to golf is a 1457 ban intended to stop the game from "
                "distracting men from compulsory archery practice. The ban was repeated, "
                "yet James IV, under whom it was prohibited again in 1491, later bought "
                "expensive clubs in Perth, Edinburgh and St Andrews. Early courses had "
                "different numbers of holes; Scotland's natural coastal links and the "
                "influence of St Andrews helped 18 holes become the modern standard. In "
                "1744, the Company of Gentlemen Golfers wrote 13 early rules. Its first "
                "champion, surgeon John Rattray, later escaped execution after the Jacobite "
                "rising with help from a fellow golfer."
            ),
            "source_ids": [
                "official-handbook",
                "nls-early-scottish-golf",
                "historic-scotland-st-andrews-links",
                "randa-why-18-holes",
            ],
        },
        "exam-02-q22": {
            "why_correct_en": (
                "The correct answer is William Caxton. He brought movable-type printing "
                "skills learned on the European continent to England and established "
                "England's first printing press at Westminster around 1476. Caxton began "
                "as a London cloth merchant and spent much of his commercial career in "
                "Bruges and other trading centres in the Low Countries. He learned about "
                "printing in Cologne and later helped produce books in Flanders. His "
                "merchant experience, Continental connections and links with wealthy "
                "English patrons helped him recognise and serve a market for printed "
                "books in English."
            ),
            "source_ids": [
                "official-handbook",
                "westminster-abbey-william-caxton",
                "merton-caxton-canterbury-tales",
            ],
        },
        "exam-02-q24": {
            "why_correct_en": (
                "The correct answer is John Logie Baird, the Scottish inventor who "
                "developed an early mechanical television system in the 1920s. His first "
                "test 'star' was the ventriloquist's dummy head Stookie Bill because the "
                "equipment required lighting too hot for prolonged human use. In 1925, "
                "Baird paid his assistant William Taynton two shillings and sixpence to "
                "endure the lights and become the first recognisable human face transmitted "
                "by Baird's system. On 26 January 1926, Baird demonstrated live, recognisable "
                "faces to Royal Institution members at 22 Frith Street, London. In 1928, he "
                "made the first transatlantic television transmission and demonstrated both "
                "colour and stereoscopic television."
            ),
            "source_ids": [
                "official-handbook",
                "science-museum-stookie-bill",
                "iet-100-years-television",
                "nms-first-colour-television",
            ],
        },
        "exam-03-q15": {
            "why_correct_en": (
                "The answer is True. The Lake District, in north-west England, is the "
                "largest national park in England by area. The question is specifically "
                "about England; the other UK nations have their own national parks."
            ),
            "source_ids": ["official-handbook"],
        },
        "exam-04-q05": {
            "why_correct_en": (
                "The answer is True. Authorised Scottish banks issue their own notes "
                "denominated in pounds sterling, and the notes can be used across the UK.\n\n"
                "They are not legal tender, so businesses do not have to accept them. In "
                "the exam wording, 'valid everywhere' means valid sterling notes, not a "
                "compulsory form of payment."
            ),
            "source_ids": ["official-handbook", "bank-england-legal-tender"],
        },
        "exam-04-q07": {
            "why_correct_en": (
                "The answer is True. Great Britain comprises England, Scotland and "
                "Wales; it does not include Northern Ireland. The United Kingdom is Great "
                "Britain together with Northern Ireland."
            ),
            "source_ids": ["official-handbook", "ons-uk-geographies"],
        },
        "exam-05-q20": {
            "why_correct_en": (
                "The answer is True. Marriage or cohabitation does not provide automatic "
                "consent to sex. A husband who forces his wife to have sex without her "
                "consent can be charged with rape."
            ),
            "source_ids": ["official-handbook"],
        },
        "exam-07-q06": {
            "why_correct_en": (
                "The answer is True. At the Battle of Bannockburn in 1314, the Scots led "
                "by Robert the Bruce defeated the English army of Edward II. The victory "
                "strengthened Scotland's continued position as an independent kingdom."
            ),
            "source_ids": ["official-handbook", "national-archives-education"],
        },
        "exam-07-q12": {
            "why_correct_en": (
                "The answer is True. Parliament passed the Slavery Abolition Act in 1833, "
                "ending slavery in most British colonies. Do not confuse it with the 1807 "
                "Act that prohibited British participation in the slave trade."
            ),
            "source_ids": ["official-handbook", "national-archives-education"],
        },
        "exam-08-q08": {
            "why_correct_en": (
                "The answer is True. Authorised banks in Scotland and Northern Ireland "
                "issue notes denominated in pounds sterling for use across the UK.\n\n"
                "The notes are not legal tender, so a business may refuse them. 'Valid "
                "everywhere' means valid sterling currency, not that every shop must "
                "accept it."
            ),
            "source_ids": ["official-handbook", "bank-england-legal-tender"],
        },
        "exam-08-q15": {
            "why_correct_en": (
                "The answer is True. Female genital mutilation is a criminal offence in "
                "the UK. Arranging or assisting FGM is also illegal, including taking a "
                "British national or permanent resident abroad for it."
            ),
            "source_ids": ["official-handbook", "govuk-fgm-help"],
        },
        "exam-09-q02": {
            "why_correct_en": (
                "The answer is True. The Battle of Waterloo in 1815 ended Napoleon's "
                "Hundred Days and the period of conflict described by the source. The "
                "allied army led by the Duke of Wellington and the Prussians defeated him."
            ),
            "source_ids": ["official-handbook", "national-archives-education"],
        },
        "exam-09-q11": {
            "why_correct_en": (
                "The answer is True: Northern Ireland uses Individual Electoral "
                "Registration, so each eligible voter registers separately.\n\n"
                "This is no longer unique to Northern Ireland. England and Wales moved to "
                "individual registration in June 2014 and Scotland in September 2014. The "
                "exam point is that each voter is responsible for their own registration."
            ),
            "source_ids": ["official-handbook", "govuk-individual-electoral-registration"],
        },
        "exam-14-q16": {
            "why_correct_en": (
                "The answer is True. In the UK's parliamentary democracy, voters elect "
                "MPs and the party or coalition able to command the confidence of the "
                "House of Commons forms the government. The government is accountable to "
                "Parliament."
            ),
            "source_ids": ["official-handbook", "parliament-how-it-works"],
        },
        "exam-17-q13": {
            "why_correct_en": (
                "The answer is True. The Speaker must first be an MP and continues to "
                "represent a constituency and handle constituents' concerns. Once elected "
                "Speaker, they must remain politically impartial in parliamentary work."
            ),
            "source_ids": ["official-handbook", "parliament-how-it-works"],
        },
        "exam-17-q18": {
            "why_correct_en": (
                "The answer is True. In Northern Ireland, a Youth Court case may be heard "
                "by a District Judge or by up to three specially trained lay magistrates. "
                "Youth Courts mainly deal with defendants under 18 and restrict public access."
            ),
            "source_ids": ["official-handbook", "govuk-justice"],
        },
        "exam-03-q06": {
            "why_correct_en": (
                "The answer is Bonnie Prince Charlie, or Charles Edward Stuart. In 1745 "
                "he landed in Scotland, raised an army with support from Highland clans "
                "and tried to restore the Stuart dynasty. The Jacobite rising ended in "
                "defeat at Culloden in 1746."
            ),
            "source_ids": ["official-handbook", "national-archives-education"],
        },
        "exam-03-q17": {
            "why_correct_en": (
                "The two answers are setting the school's strategic direction and "
                "monitoring and evaluating its performance. School governors are members "
                "of a governing body, not government officials. Their third central role "
                "is ensuring accountability."
            ),
            "source_ids": ["official-handbook"],
        },
        "exam-13-q10": {
            "why_correct_en": (
                "The answer is the Highlands. In 1745 Charles Edward Stuart, known as "
                "Bonnie Prince Charlie, raised an army with the support of Highland clans "
                "during the Jacobite attempt to restore the Stuart dynasty."
            ),
            "source_ids": ["official-handbook", "national-archives-education"],
        },
        "exam-14-q17": {
            "why_correct_en": (
                "The answer is an Ulster Fry, Northern Ireland's traditional cooked "
                "breakfast. It commonly includes bacon, sausages, eggs and tomato with "
                "pan-fried soda bread and potato bread. 'Fry' means the whole cooked "
                "breakfast, not simply fried potatoes."
            ),
            "source_ids": ["official-handbook", "discover-ni-ulster-fry"],
        },
        "exam-15-q12": {
            "why_correct_en": (
                "The source-set answer is Ernest Rutherford. He pioneered nuclear physics "
                "and directed the Cavendish Laboratory; in 1932 John Cockcroft and Ernest "
                "Walton split an atomic nucleus using accelerated protons under his direction.\n\n"
                "The original explanation wrongly implies that Rutherford joined the "
                "Manhattan Project. He died in 1937 and did not take part. For the exam, "
                "remember the link between Rutherford's team and 'splitting the atom'."
            ),
            "source_ids": ["official-handbook", "cambridge-splitting-atom"],
        },
        "exam-17-q02": {
            "why_correct_en": (
                "The answer is the potato. From 1845, repeated potato blight destroyed "
                "Ireland's staple crop and contributed to the Great Famine. Around one "
                "million people died from starvation and disease, while many others emigrated."
            ),
            "source_ids": ["official-handbook", "parliament-great-famine"],
        },
    }
)


NON_AI_VISUAL_IDS = {"exam-01-q02", "exam-01-q05"}


AI_VISUAL_ALT_OVERRIDES = {
    "exam-01-q17": (
        "英国投票卡AI学习插图，标有选举日期、投票时间、指定投票站、"
        "选民姓名、地址和选民编号；所有个人资料均为虚构样例。"
    ),
}


REAL_VISUAL_OVERRIDES = {
    "exam-01-q08": {
        "src": "/images/featured/the-cenotaph-whitehall.jpg",
        "kind": "licensed_real_photo",
        "alt_zh": "伦敦白厅道路中央的The Cenotaph实景照片，碑前摆放着纪念花圈。",
        "credit": "Photo: Paul the Archivist / Wikimedia Commons (CC BY-SA 4.0)",
        "credit_url": "https://commons.wikimedia.org/wiki/File:The_Cenotaph,_Whitehall,_London.jpg",
    },
    "exam-01-q20": {
        "src": "/images/featured/channel-islands-map.svg",
        "kind": "original_location_map",
        "alt_zh": "海峡群岛位置图：Jersey、Guernsey、Alderney和Sark位于英吉利海峡、法国诺曼底近海，英格兰在其北方。",
        "credit": "Original schematic map based on Government of Jersey location information",
        "credit_url": "https://www.londonoffice.gov.je/about-jersey/",
    },
    **{
        question_id: {
            "src": "/images/featured/margaret-thatcher-1983.jpg",
            "kind": "licensed_real_photo",
            "alt_zh": "玛格丽特·撒切尔1983年的黑白肖像照片。",
            "credit": "Photo: Rob Bogaerts / Anefo / Nationaal Archief (CC0)",
            "credit_url": "https://commons.wikimedia.org/wiki/File:Margaret_Thatcher_(1983).jpg",
        }
        for question_id in ("exam-01-q09", "exam-11-q08", "exam-17-q05")
    },
}


def visual_content_key(question: dict) -> str:
    """Return the stable content key used to reuse an image for exact duplicates."""
    return json.dumps(
        [question["question"], question["correct_answers"]],
        ensure_ascii=False,
        separators=(",", ":"),
    )


# Ordered phrases are intentionally conservative: the first matching subject terms
# become the visible study cues. A fallback still guarantees one exact source span.
KEYWORD_PHRASES = [
    "men and women", "women’s rights", "women's rights", "right to vote",
    "age of 21", "age of 30", "British citizen", "permanent resident",
    "Prime Minister", "House of Commons", "House of Lords", "Houses of Parliament",
    "European Union", "United Nations", "National Insurance", "general election",
    "local election", "civil war", "First World War", "Second World War", "World War II",
    "Battle of Hastings", "Spanish Armada", "Dunkirk spirit", "Magna Carta",
    "Bill of Rights", "Emancipation Act", "Industrial Revolution", "Bayeux Tapestry",
    "Alan Turing", "Winston Churchill", "Emmeline Pankhurst", "Florence Nightingale",
    "William Shakespeare", "William Wilberforce", "Mary, Queen of Scots",
    "Mary Stuart", "Elizabeth I", "Henry VIII", "William the Conqueror", "Big Ben",
    "Wallace and Gromit", "Nick Park", "Stonehenge", "Hadrian’s Wall", "Hadrian's Wall",
    "Home Secretary", "Chief Constable", "Crown dependency", "Crown Dependency",
    "overseas territory", "national park", "capital city", "patron Saint", "public holiday",
    "bank holiday", "minimum age", "Great Britain", "Northern Ireland", "New Year’s Eve",
    "Church of England", "Church of Scotland", "Tower of London", "Crown Jewels",
    "police complaints", "civil servants", "devolved administrations", "small claims procedure",
    "written constitution", "World Wide Web", "Black Death", "Norman Conquest",
    "Great Depression", "Glorious Revolution", "Middle Ages", "Divine Right of Kings",
    "National Citizen Service", "Scottish Parliament", "Welsh Assembly", "Youth Court",
]

KEYWORD_STOPWORDS = {
    "about", "after", "again", "also", "among", "before", "being", "below", "between",
    "could", "country", "during", "following", "given", "happened", "having", "known",
    "made", "most", "other", "right", "should", "statement", "these", "those", "through",
    "under", "which", "would", "where", "when", "what", "whose", "there", "their",
    "from", "into", "than", "that", "this", "were", "have", "does", "with", "years",
}


def question_keywords(question: str) -> list[str]:
    """Return one to three exact, non-overlapping study spans from the source question."""
    if re.search(r"\b(?:what|which) are two\b", question, re.IGNORECASE):
        return [re.search(r"\btwo\b", question, re.IGNORECASE).group(0)]

    matches: list[tuple[int, int, str]] = []
    for phrase in KEYWORD_PHRASES:
        match = re.search(re.escape(phrase), question, re.IGNORECASE)
        if match:
            matches.append((match.start(), match.end(), match.group(0)))

    for match in re.finditer(r"\b(?:1[0-9]{3}|20[0-9]{2}|\d{1,3}(?:st|nd|rd|th)?(?:\s+century)?)\b", question, re.IGNORECASE):
        matches.append((match.start(), match.end(), match.group(0)))

    for match in re.finditer(r"[‘’“\"]([^‘’”\"]{3,48})[’”\"]", question):
        matches.append((match.start(1), match.end(1), match.group(1)))

    ignored_capitals = {"what", "which", "who", "when", "where", "why", "how", "is", "in", "the", "a", "as", "by", "during", "several", "anyone", "police"}
    for match in re.finditer(r"\b(?:[A-Z]{2,}|[A-Z][a-z]+(?:[’'][A-Za-z]+)?)(?:[-\s]+(?:of|the|and|I|II|[A-Z]{2,}|[A-Z][a-z]+(?:[’'][A-Za-z]+)?)){0,4}\b", question):
        if match.group(0).lower() not in ignored_capitals:
            matches.append((match.start(), match.end(), match.group(0)))

    selected: list[tuple[int, int, str]] = []
    for candidate in sorted(matches, key=lambda item: (item[0], -(item[1] - item[0]))):
        if any(candidate[2] == text for _, _, text in selected):
            continue
        if any(candidate[0] < end and candidate[1] > start for start, end, _ in selected):
            continue
        selected.append(candidate)
        if len(selected) == 3:
            break
    if selected:
        return [item[2] for item in sorted(selected)]

    words = [
        match for match in re.finditer(r"[A-Za-z][A-Za-z’'-]{3,}", question)
        if match.group(0).lower().strip("’'") not in KEYWORD_STOPWORDS
    ]
    if not words:
        words = list(re.finditer(r"[A-Za-z0-9]+", question))
    best = max(words, key=lambda match: (len(match.group(0)), -match.start()))
    return [best.group(0)]


FILM_CONNECTIONS = {
    "suffragette": {
        "title": "Suffragette",
        "year": 2015,
        "relationship": "background",
        "poster_src": "/images/media/suffragette-2015-poster.jpg",
        "poster_alt_en": "The theatrical poster for Suffragette (2015).",
        "poster_alt_zh": "电影《Suffragette》（2015）的正式海报。",
        "fun_fact_en": (
            "Suffragette (2015) follows ordinary British women fighting for the vote in the early 1910s. "
            "It helps explain the campaign behind this topic, but it does not dramatise the 1928 Act that "
            "finally gave women the vote at 21 on the same terms as men."
        ),
        "fun_fact_zh": (
            "《Suffragette》（2015）讲述20世纪10年代初普通英国女性争取选举权的经历。它适合帮助理解这道题背后的运动，"
            "但电影并没有直接重现1928年女性最终以21岁、与男性同等条件获得投票权的法案。"
        ),
        "source_title": "Suffragette (2015) — BFI",
        "source_url": "https://www.bfi.org.uk/film/7a9dc7f9-58d2-57a7-b70e-8b1b81d4566f/suffragette",
        "poster_provider": "TMDB",
        "poster_provider_url": "https://www.themoviedb.org/movie/245168-suffragette",
        "poster_credit_notice": "This product uses the TMDB API but is not endorsed or certified by TMDB.",
    },
    "suffragette-pankhurst": {
        "title": "Suffragette",
        "year": 2015,
        "relationship": "background",
        "poster_src": "/images/media/suffragette-2015-poster.jpg",
        "poster_alt_en": "The theatrical poster for Suffragette (2015).",
        "poster_alt_zh": "电影《Suffragette》（2015）的正式海报。",
        "fun_fact_en": "In Suffragette (2015), the historical Emmeline Pankhurst is played by Meryl Streep. She appears only briefly, delivering a balcony speech that inspires the fictional composite character Maud Watts and other campaigners. The speech was assembled from Pankhurst's real speeches rather than reproducing one event word for word.",
        "fun_fact_zh": "电影《Suffragette》（2015）中，真实历史人物Emmeline Pankhurst由Meryl Streep饰演。她出场很短，主要在阳台演讲，鼓舞虚构的综合角色Maud Watts及其他争取选举权的女性。影片中的演说综合改编自Pankhurst的多篇真实演讲，并非逐字复原某一次演说。",
        "source_title": "Suffragette (2015) — BFI",
        "source_url": "https://www.bfi.org.uk/film/7a9dc7f9-58d2-57a7-b70e-8b1b81d4566f/suffragette",
        "poster_provider": "TMDB",
        "poster_provider_url": "https://www.themoviedb.org/movie/245168-suffragette",
        "poster_credit_notice": "This product uses the TMDB API but is not endorsed or certified by TMDB.",
    },
    "dunkirk": {
        "title": "Dunkirk",
        "year": 2017,
        "relationship": "direct",
        "poster_src": "/images/media/dunkirk-2017-poster.jpg",
        "poster_alt_en": "The theatrical poster for Dunkirk (2017).",
        "poster_alt_zh": "电影《Dunkirk》（2017）的正式海报。",
        "fun_fact_en": "Dunkirk (2017) directly dramatises the 1940 evacuation behind the phrase ‘Dunkirk spirit’, including the role of civilian boats.",
        "fun_fact_zh": "《Dunkirk》（2017）直接取材于1940年的敦刻尔克大撤退，也呈现了民用小船参与救援的历史背景，这正是“Dunkirk spirit”的来源。",
        "source_title": "Dunkirk (2017) — BFI",
        "source_url": "https://www.bfi.org.uk/film/1ab19d70-c33f-510c-9612-8af2e27fa459/dunkirk",
        "poster_provider": "TMDB",
        "poster_provider_url": "https://www.themoviedb.org/movie/374720-dunkirk",
        "poster_credit_notice": "This product uses the TMDB API but is not endorsed or certified by TMDB.",
    },
    "imitation-game": {
        "title": "The Imitation Game",
        "year": 2014,
        "relationship": "background",
        "poster_src": "/images/media/the-imitation-game-2014-poster.jpg",
        "poster_alt_en": "An official theatrical poster for The Imitation Game (2014).",
        "poster_alt_zh": "电影《The Imitation Game》（2014）的正式海报。",
        "fun_fact_en": "The Imitation Game (2014) is a biographical drama about Alan Turing and wartime codebreaking. The exam question asks about his earlier theoretical Turing machine, so the film is useful context rather than a direct explanation of that invention.",
        "fun_fact_zh": "《The Imitation Game》（2014）是一部关于艾伦·图灵和战时代码破译的传记剧情片。考试题问的是他更早提出的理论“图灵机”，所以电影提供的是人物背景，而不是对这项发明的直接讲解。",
        "source_title": "The Imitation Game (2014) — BFI",
        "source_url": "https://www.bfi.org.uk/film/3186b089-c5f3-5572-b7f7-a119132a34c6/the-imitation-game",
        "poster_provider": "TMDB",
        "poster_provider_url": "https://www.themoviedb.org/movie/205596-the-imitation-game",
        "poster_credit_notice": "This product uses the TMDB API but is not endorsed or certified by TMDB.",
    },
}


def film_connection_for(question: dict) -> dict | None:
    text = f"{question['question']} {question.get('explanation', '')}".lower()
    if question["id"] == "exam-03-q20":
        return FILM_CONNECTIONS["suffragette-pankhurst"]
    if question["id"] in {"exam-01-q03", "exam-04-q11", "exam-09-q07"}:
        return FILM_CONNECTIONS["suffragette"]
    if "dunkirk spirit" in text:
        return FILM_CONNECTIONS["dunkirk"]
    if "alan turing" in text or "turing machine" in text:
        return FILM_CONNECTIONS["imitation-game"]
    return None


def visual_family(category_id: str) -> str:
    if category_id in {"73", "74", "78", "79", "80", "81"}:
        return "history"
    if category_id in {"70", "89"}:
        return "geography"
    if category_id in {"83", "84", "85", "86", "87", "88"}:
        return "society"
    if category_id in {"91", "92", "93", "95", "96", "98", "101"}:
        return "government"
    return "values"


def wrap(text: str, width: int, max_lines: int) -> list[str]:
    lines = textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    return lines or [""]


def fit_text(
    text: str, *, max_width_px: int, start_font: int, min_font: int, max_lines: int
) -> tuple[list[str], int]:
    """Choose a font size and wrapping width that keeps all text visible."""
    for font_size in range(start_font, min_font - 1, -1):
        approximate_character_width = font_size * 0.56
        width = max(10, int(max_width_px / approximate_character_width))
        lines = textwrap.wrap(
            text, width=width, break_long_words=False, break_on_hyphens=False
        ) or [""]
        if len(lines) <= max_lines:
            return lines, font_size
    width = max(10, int(max_width_px / (min_font * 0.56)))
    return wrap(text, width, max_lines), min_font


def motif(family: str, accent: str) -> str:
    if family == "history":
        return f'''<path d="M155 438H485" stroke="{accent}" stroke-width="8" stroke-linecap="round"/>
<circle cx="190" cy="438" r="18" fill="{accent}"/><circle cx="320" cy="438" r="18" fill="{accent}"/><circle cx="450" cy="438" r="18" fill="{accent}"/>
<path d="M320 248l58 48-22 78h-72l-22-78z" fill="none" stroke="{accent}" stroke-width="10"/>'''
    if family == "geography":
        return f'''<circle cx="320" cy="340" r="126" fill="none" stroke="{accent}" stroke-width="10"/>
<path d="M320 226l28 94-28 22-28-22zM320 454l-28-94 28-22 28 22z" fill="{accent}"/>
<text x="320" y="195" text-anchor="middle" fill="{accent}" font-size="34" font-weight="700">N</text>'''
    if family == "government":
        return f'''<path d="M180 316l140-86 140 86zM198 340h244M218 340v120M282 340v120M358 340v120M422 340v120M190 460h260" fill="none" stroke="{accent}" stroke-width="10" stroke-linejoin="round"/>
<circle cx="320" cy="276" r="14" fill="{accent}"/>'''
    if family == "society":
        return f'''<path d="M320 222v236M202 340h236" stroke="{accent}" stroke-width="10" stroke-linecap="round" opacity=".45"/>
<circle cx="320" cy="340" r="112" fill="none" stroke="{accent}" stroke-width="10"/>
<circle cx="320" cy="340" r="34" fill="{accent}"/>
<circle cx="320" cy="228" r="14" fill="{accent}"/><circle cx="432" cy="340" r="14" fill="{accent}"/><circle cx="320" cy="452" r="14" fill="{accent}"/><circle cx="208" cy="340" r="14" fill="{accent}"/>'''
    return f'''<path d="M205 390l72 72 160-182" fill="none" stroke="{accent}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="320" cy="350" r="132" fill="none" stroke="{accent}" stroke-width="8" opacity=".45"/>'''


def make_svg(question: dict, category_name: str) -> str:
    family = visual_family(str(question["category_id"]))
    background, accent, foreground = PALETTES[family]
    answer = "  •  ".join(question["correct_answers"])
    question_lines, question_font = fit_text(
        question["question"], max_width_px=510, start_font=31, min_font=20, max_lines=4
    )
    answer_lines, answer_font = fit_text(
        answer, max_width_px=510, start_font=38, min_font=20, max_lines=5
    )
    question_line_height = round(question_font * 1.28)
    answer_line_height = round(answer_font * 1.3)
    question_tspans = "".join(
        f'<tspan x="590" dy="{0 if index == 0 else question_line_height}">{escape(line)}</tspan>'
        for index, line in enumerate(question_lines)
    )
    answer_tspans = "".join(
        f'<tspan x="590" dy="{0 if index == 0 else answer_line_height}">{escape(line)}</tspan>'
        for index, line in enumerate(answer_lines)
    )
    title = escape(f'{question["question"]} Correct answer: {answer}')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675" role="img" aria-labelledby="title desc">
<title id="title">{title}</title>
<desc id="desc">Answer memory card shown after answering the question.</desc>
<rect width="1200" height="675" rx="36" fill="{background}"/>
<circle cx="320" cy="340" r="210" fill="#FFFFFF" opacity=".045"/>
{motif(family, accent)}
<text x="590" y="82" fill="{accent}" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" letter-spacing="2">ANSWER MEMORY CARD · {escape(question["id"].upper())}</text>
<text x="590" y="126" fill="{foreground}" opacity=".76" font-family="Arial, Helvetica, sans-serif" font-size="18">{escape(category_name)}</text>
<text x="590" y="172" fill="{foreground}" font-family="Arial, Helvetica, sans-serif" font-size="{question_font}" font-weight="600">{question_tspans}</text>
<line x1="590" y1="345" x2="1110" y2="345" stroke="{accent}" stroke-width="3" opacity=".55"/>
<text x="590" y="392" fill="{accent}" font-family="Arial, Helvetica, sans-serif" font-size="20" font-weight="700" letter-spacing="2">CORRECT ANSWER</text>
<text x="590" y="438" fill="{foreground}" font-family="Arial, Helvetica, sans-serif" font-size="{answer_font}" font-weight="700">{answer_tspans}</text>
</svg>
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate enriched runtime data for all exams or selected exams."
    )
    parser.add_argument(
        "--exam",
        action="append",
        type=int,
        help="Exam number to generate. Repeat to generate more than one; omit for all 17.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    exam_numbers = sorted(set(args.exam or range(1, 18)))
    invalid_exam_numbers = [number for number in exam_numbers if not 1 <= number <= 17]
    if invalid_exam_numbers:
        raise SystemExit(f"Exam numbers must be between 1 and 17: {invalid_exam_numbers}")

    question_data = json.loads((DATA / "lifeintheuktestweb_questions.json").read_text("utf-8"))
    authority = json.loads((DATA / "authority_sources.json").read_text("utf-8"))
    categories = authority["category_map"]
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    ENRICHED_EXAM_DIR.mkdir(parents=True, exist_ok=True)
    WEB_EXAM_DIR.mkdir(parents=True, exist_ok=True)

    canonical_visual_ids: dict[str, str] = {}
    for question in question_data["questions"]:
        content_key = visual_content_key(question)
        canonical_visual_ids.setdefault(content_key, question["id"])

    generated_question_count = 0
    for exam_number in exam_numbers:
        translation_path = TRANSLATION_DIR / f"exam-{exam_number:02d}.json"
        translations = json.loads(translation_path.read_text("utf-8"))
        learning_override_path = LEARNING_OVERRIDE_DIR / f"exam-{exam_number:02d}.json"
        exam_learning_overrides = (
            json.loads(learning_override_path.read_text("utf-8"))
            if learning_override_path.exists()
            else {}
        )
        exam_questions = [
            question
            for question in question_data["questions"]
            if question["exam_number"] == exam_number
        ]
        enriched_questions = []
        referenced_source_ids: set[str] = set()

        for question in exam_questions:
            category_id = str(question["category_id"])
            category = categories[category_id]
            content_key = visual_content_key(question)
            canonical_visual_id = canonical_visual_ids[content_key]
            ai_image_path = AI_IMAGE_DIR / f"{canonical_visual_id}.webp"
            visual_override = REAL_VISUAL_OVERRIDES.get(question["id"])
            use_ai_image = (
                visual_override is None
                and canonical_visual_id not in NON_AI_VISUAL_IDS
                and film_connection_for(question) is None
                and ai_image_path.exists()
            )
            image_relative = (
                visual_override["src"]
                if visual_override
                else f"/images/ai/{canonical_visual_id}.webp"
                if use_ai_image
                else f"/images/questions/{question['id']}.svg"
            )
            (IMAGE_DIR / f"{question['id']}.svg").write_text(
                make_svg(question, category["name"]), encoding="utf-8"
            )
            answers = "；".join(question["correct_answers"])
            learning_override = {
                **LEARNING_OVERRIDES.get(question["id"], {}),
                **exam_learning_overrides.get(question["id"], {}),
            }
            source_ids = learning_override.get("source_ids", category["source_ids"])
            referenced_source_ids.update(source_ids)
            enriched_questions.append(
                {
                    **question,
                    "category_name": category["name"],
                    "handbook_locator": category["chapter"],
                    "learning": {
                        "why_correct_en": learning_override.get(
                            "why_correct_en", question["explanation"]
                        ),
                        "why_correct_zh": translations[question["id"]],
                        "answer_summary_zh": f"正确选项：{answers}。",
                        "source_note_zh": "官方教材是答案和考试范围的主要依据；其他权威来源用于补充该主题背景。",
                        "keywords": question_keywords(question["question"]),
                    },
                    "authoritative_source_ids": source_ids,
                    "visual": {
                        "src": image_relative,
                        "kind": (
                            visual_override["kind"]
                            if visual_override
                            else "ai_learning_illustration"
                            if use_ai_image
                            else "answer_memory_card"
                        ),
                        "display_after_answer": True,
                        "alt_zh": (
                            visual_override["alt_zh"]
                            if visual_override
                            else AI_VISUAL_ALT_OVERRIDES.get(canonical_visual_id)
                            if use_ai_image and canonical_visual_id in AI_VISUAL_ALT_OVERRIDES
                            else f"根据题目“{question['question']}”及正确答案“{answers}”生成的AI学习插图。"
                            if use_ai_image
                            else f"题目：{question['question']}；正确答案：{answers}"
                        ),
                        "fact_source_ids": source_ids,
                        **(
                            {
                                "credit": visual_override["credit"],
                                "credit_url": visual_override["credit_url"],
                            }
                            if visual_override
                            else {}
                        ),
                    },
                    "film_connection": film_connection_for(question),
                }
            )

        output = {
            "dataset": question_data["dataset"],
            "exam_number": exam_number,
            "question_count": len(enriched_questions),
            "content_policy": {
                "visuals": (
                    "Question-and-answer-specific AI learning illustrations are preferred when present; "
                    "real licensed media and original SVG fallbacks remain available. All answer visuals "
                    "display only after the learner answers."
                ),
                "primary_authority": "official-handbook",
                "source_roles": "The handbook supports exam answers; supplemental sources provide authoritative topic context.",
            },
            "authority_sources": {
                source_id: authority["sources"][source_id]
                for source_id in sorted(referenced_source_ids)
            },
            "questions": enriched_questions,
        }
        serialized_output = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
        filename = f"exam-{exam_number:02d}.json"
        (ENRICHED_EXAM_DIR / filename).write_text(serialized_output, encoding="utf-8")
        (WEB_EXAM_DIR / filename).write_text(serialized_output, encoding="utf-8")
        generated_question_count += len(enriched_questions)

    print(
        json.dumps(
            {
                "exams": exam_numbers,
                "questions": generated_question_count,
                "images": generated_question_count,
            }
        )
    )


if __name__ == "__main__":
    main()
