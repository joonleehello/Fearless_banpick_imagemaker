import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import win32clipboard
import json

version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
version_response = requests.get(version_url)
versions = version_response.json()

CURRENT_VERSION = versions[0]


champ_url = f"https://ddragon.leagueoflegends.com/cdn/{CURRENT_VERSION}/data/ko_KR/champion.json"
champ_response = requests.get(champ_url)
champ_data = champ_response.json()["data"]

champ_name_map = {}
for champ_id, champ_info in champ_data.items():
    korean_name = champ_info["name"]
    english_id = champ_info["id"]
    champ_name_map[korean_name] = english_id

custom_name = {
    "갱플": "Gangplank",
    "글가": "Gragas",
    "그브": "Graves",
    "노틸": "Nautilus",
    "누누": "Nunu",
    "누누와윌럼프": "Nunu",
    "다리": "Darius",
    "레나타": "Renata",
    "레나타글라스크": "Renata",
    "레넥": "Renekton",
    "리신" : "LeeSin",
    "리산": "Lissandra",
    "마이": "MasterYi",
    "마스터이": "MasterYi",
    "말파": "Malphite",
    "모데": "Mordekaiser",
    "문도": "DrMundo",
    "문박": "DrMundo",
    "문도박사": "DrMundo",
    "미포": "MissFortune",
    "미스포츈": "MissFortune",
    "볼베": "Volibear",
    "블라디": "Vladimir",
    "블츠": "Blitzcrank",
    "블리츠": "Blitzcrank",
    "블랭": "Blitzcrank",
    "사일": "Sylas",
    "세주": "Sejuani",
    "신짜오": "XinZhao",
    "짜오" : "XinZhao",
    "아우렐리온솔": "AurelionSol",
    "아우솔": "AurelionSol",
    "솔": "AurelionSol",
    "아트": "Aatrox",
    "아펠": "Aphelios",
    "알리": "Alistar",
    "위웍": "Warwick",
    "워웍": "Warwick",
    "위윅": "Warwick",
    "워윅": "Warwick",
    "이렐": "Irelia",
    "이즈": "Ezreal",
    "자르반": "JarvanIV",
    "자르반4세": "JarvanIV",
    "카시": "Cassiopeia",
    "카타": "Katarina",
    "칼리": "Kalista",
    "케틀": "Caitlyn",
    "킨드": "Kindred",
    "트타": "Tristana",
    "트리": "Tristana",
    "트린": "Tryndamere",
    "트페": "TwistedFate",
    "트위스티드페이트": "TwistedFate",
    "탐켄치": "TahmKench",
    "켄치": "TahmKench",
    "피들": "Fiddlesticks",
    "딩거": "Heimerdinger",
    "하이머": "Heimerdinger",
}

champ_name_map.update(custom_name)

ICON_SIZE = (64, 64)
CENTER_WIDTH = 150

def download_champ_icon(eng_name):
    url = f"http://ddragon.leagueoflegends.com/cdn/{CURRENT_VERSION}/img/champion/{eng_name}.png"
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content)).resize(ICON_SIZE)
    else:
        print(f" 다운로드 실패: {eng_name}")
        return None


def create_team_image(team_list):
    images = []
    for champ in team_list:
        eng_name = champ_name_map.get(champ)

        if not eng_name:
            messagebox.showerror("오류", f"매핑 없음: {champ}")
            return None

        img = download_champ_icon(eng_name)

        if img:
            images.append(img)

    total_width = ICON_SIZE[0] * len(images)
    result = Image.new("RGB", (total_width, ICON_SIZE[1]), (255, 255, 255))
    x_offset = 0

    for img in images:
        result.paste(img, (x_offset, 0))
        x_offset += ICON_SIZE[0]

    return result


def copy_image_to_clipboard(image):

    output = io.BytesIO()
    image.convert("RGB").save(output, "BMP")

    data = output.getvalue()[14:]

    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

def generate_image():
    game_number = entry_game.get()
    champ_input = entry_champs.get()
    champ_list = champ_input.strip().split()

    if not game_number.isdigit():
        messagebox.showerror("오류","게임 번호는 숫자여야 합니다.")
        return

    if len(champ_list) != 10:

        messagebox.showerror("오류","챔피언의 개수는 10개여야 합니다.")
        return

    left_team = champ_list[:5]
    right_team = champ_list[5:]

    left_img = create_team_image(left_team)
    right_img = create_team_image(right_team)

    if left_img is None or right_img is None:
        return

    total_width = left_img.width + CENTER_WIDTH + right_img.width
    total_height = ICON_SIZE[1]

    final_image = Image.new("RGB",(total_width,total_height),(240,240,250))

    final_image.paste(left_img, (0,0))

    draw = ImageDraw.Draw(final_image)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    text = f"GAME {game_number}"
    bbox = draw.textbbox((0,0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_x = left_img.width + (CENTER_WIDTH - text_width) // 2
    text_y = (total_height - text_height) // 2


    draw.text((text_x, text_y), text, fill=(0,0,0), font=font)

    final_image.paste(right_img, (left_img.width+ CENTER_WIDTH,0))

    copy_image_to_clipboard(final_image)
    messagebox.showinfo("완료", "클립보트에 복사되었습니다. Ctrl+V로 붙여넣기 하세요.")






root = tk.Tk()
root.title("피어리스 벤픽 이미지 생성기")

tk.Label(root, text="몇번째 게임인지 숫자로 입력하세요 (예시: 1)").pack()
entry_game = tk.Entry(root)
entry_game.pack()

tk.Label(root, text="챔피언 이름을 10개 입력하세요.(예시: 트페 리산 리신 누누와윌럼프 가렌 갈리오 그브 녹턴 다이애나 알리) ").pack()
entry_champs = tk.Entry(root, width=60)
entry_champs.pack()

tk.Button(root, text="이미지 생성", command=generate_image).pack()

root.mainloop()