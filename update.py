import os
import time
import json
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ttkbootstrap as ttk

chrome_driver_path = r"C:\Users\khalil\hiso\chromedriver.exe"
output_file = "en.1.json"

def load_existing_data():
    """ تحميل البيانات المخزنة مسبقًا """
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"matches": []}

def update_or_add_match(matches_data, new_match):
    """ تحديث المباراة إذا كانت موجودة، أو إضافتها إذا لم تكن موجودة """
    for i, existing_match in enumerate(matches_data["matches"]):
        if existing_match["date"] == new_match["date"] and existing_match["team1"] == new_match["team1"] and existing_match["team2"] == new_match["team2"]:
            # تحديث البيانات إذا كانت المباراة موجودة
            matches_data["matches"][i] = new_match
            return

    matches_data["matches"].append(new_match)  # المباراة جديدة، تتم إضافتها

def extract_match_details(driver, match, date_input, comp_name):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", match)
        driver.execute_script("arguments[0].click();", match)
        time.sleep(4)
        match_tab = match.find_element(By.CSS_SELECTOR, "div.match_tab")
        match_feed = match_tab.find_element(By.CSS_SELECTOR, "div.match_feed")
    except:
        match_feed = None

    try:
        display_time = match.find_element(By.CSS_SELECTOR, ".the_time").text.strip()
    except:
        display_time = "غير معروف"

    if not display_time or display_time == "غير معروف":
        try:
            display_time = driver.find_element(By.CSS_SELECTOR, "div.match_info li.match_time span").text.strip()
        except:
            display_time = "غير معروف"

    try:
        match_status_text = driver.find_element(By.CSS_SELECTOR, "li.match_inner_status span").text.strip("()").strip()
    except:
        match_status_text = "غير معروف"

    try:
        team1 = match.find_element(By.CSS_SELECTOR, ".hometeam .the_team").text.strip()
        team2 = match.find_element(By.CSS_SELECTOR, ".awayteam .the_team").text.strip()
    except:
        return None

    goals, substitutions, cards, var_decisions = [], [], [], []
    if match_feed:
        for side in ["hometeam", "awayteam"]:
            try:
                team_ul = match_feed.find_element(By.CSS_SELECTOR, f"ul.{side}")
            except:
                continue

            events = team_ul.find_elements(By.CSS_SELECTOR, "li.item_row")
            for event in events:
                try:
                    item = event.find_element(By.CLASS_NAME, "item")
                    html = event.get_attribute("innerHTML")
                    raw_minute = item.find_element(By.CLASS_NAME, "minute").text.strip().replace("'", "")
                    minute = raw_minute if "+" in raw_minute else str(int(raw_minute)) if raw_minute.isdigit() else "0"
                    team_side = "home" if side == "hometeam" else "away"
                    classes = item.get_attribute("class")

                    if "goals" in classes:
                        scorer = item.find_element(By.CLASS_NAME, "details").text.strip()
                        assist = None
                        is_penalty = "ضربة جزاء" in html
                        try:
                            second_row = event.find_element(By.CLASS_NAME, "second_row").text
                            if "صناعة:" in second_row:
                                assist = second_row.split("صناعة:")[-1].strip()
                        except:
                            pass
                        if "في مرماه" in scorer:
                            scorer = scorer.replace("في مرماه", "").strip()
                            team_side = "away" if team_side == "home" else "home"
                        goals.append({
                            "scorer": scorer,
                            "minute": minute,
                            "assist": assist,
                            "penalty": is_penalty,
                            "team": team_side
                        })

                    elif "substitution" in classes:
                        player_in = item.find_element(By.CLASS_NAME, "player_in").text.strip()
                        player_out = item.find_element(By.CLASS_NAME, "player_out").text.strip()
                        substitutions.append({
                            "in": player_in,
                            "out": player_out,
                            "minute": int(''.join(filter(str.isdigit, raw_minute))),
                            "team": team_side
                        })

                    elif "card" in classes:
                        player = item.find_element(By.CLASS_NAME, "details").text.strip()
                        card_type = "yellow" if "yellowcard" in html else "red"
                        cards.append({
                            "player": player,
                            "type": card_type,
                            "minute": int(''.join(filter(str.isdigit, raw_minute))),
                            "team": team_side
                        })

                    elif "var_icon" in html:
                        var_player = ""
                        try:
                            var_player = item.find_element(By.CLASS_NAME, "details").text.strip()
                        except:
                            pass
                        note = ""
                        try:
                            note = event.find_element(By.CLASS_NAME, "second_row").text.strip()
                        except:
                            pass
                        var_decisions.append({
                            "minute": minute,
                            "team": team_side,
                            "player": var_player,
                            "note": note or "VAR decision"
                        })
                except:
                    continue

    score_ft = []
    try:
        score_text = match.find_element(By.CSS_SELECTOR, ".match_score").text.strip()
        if "-" in score_text:
            parts = score_text.split("-")
            score_home = int(''.join(filter(str.isdigit, parts[0])))
            score_away = int(''.join(filter(str.isdigit, parts[1])))
            score_ft = [score_home, score_away]
    except:
        pass

    return {
        "date": date_input,
        "time": display_time,
        "status": match_status_text,
        "competition": comp_name,
        "team1": team1,
        "team2": team2,
        "score": {"ft": score_ft},
        "goals": goals,
        "substitutions": substitutions,
        "cards": cards,
        "var": var_decisions
    }

def scrape_competition():
    date_input = date_entry.get().strip()
    comp_input = comp_entry.get().strip()

    matches_data = load_existing_data()

    service = Service(chrome_driver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    url = f"https://jdwel.com/matches/?date={date_input}"
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.comp_matches_list"))
        )
    except:
        messagebox.showinfo("❌", "لم يتم العثور على مباريات.")
        driver.quit()
        return

    comp_blocks = driver.find_elements(By.CSS_SELECTOR, "ul.comp_matches_list")
    for block in comp_blocks:
        try:
            comp_title = block.find_element(By.CSS_SELECTOR, "div.comp_separator h4.title").text.strip()
        except:
            continue

        if comp_input in comp_title:
            matches = block.find_elements(By.CSS_SELECTOR, "li.single_match")
            for match in matches:
                match_data = extract_match_details(driver, match, date_input, comp_title)
                if match_data:
                    update_or_add_match(matches_data, match_data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(matches_data, f, indent=2, ensure_ascii=False)

    driver.quit()
    messagebox.showinfo("✅ نجاح", f"تم حفظ مباريات {comp_input} في {output_file}")

root = ttk.Window("⚽ أداة جمع مباريات البطولة", themename="superhero")
root.geometry("480x400")
root.resizable(False, False)

ttk.Label(root, text="📅 التاريخ (YYYY-MM-DD):").pack(pady=(10, 0))
date_entry = ttk.Entry(root)
date_entry.pack(pady=5)

ttk.Label(root, text="🏆 اسم البطولة (جزء من الاسم يكفي):").pack()
comp_entry = ttk.Entry(root)
comp_entry.pack(pady=5)

ttk.Button(root, text="📥 جمع بيانات البطولة", bootstyle="primary", command=scrape_competition).pack(pady=20)

root.mainloop()
