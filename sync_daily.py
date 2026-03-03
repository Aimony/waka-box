import os
import requests
import math

# 配置参数
WAKA_KEY = os.getenv('WAKATIME_API_KEY')
GIST_ID = os.getenv('GIST_ID_DAILY')
BAR_WIDTH = 20  # 进度条总长度

def generate_bar(percent):
    syms = "░▏▎▍▌▋▊▉█"
    filled_len = (percent / 100) * BAR_WIDTH
    full_blocks = int(filled_len)
    if full_blocks >= BAR_WIDTH:
        return "█" * BAR_WIDTH
    
    remainder = filled_len - full_blocks
    idx = int(remainder * 8)
    return "█" * full_blocks + syms[idx] + "░" * (BAR_WIDTH - full_blocks - 1)

def fetch_stats():
    url = f"https://wakatime.com/api/v1/users/current/summaries?start=today&end=today&api_key={WAKA_KEY}"
    response = requests.get(url).json()
    
    data = response['data'][0]
    total_time = data['grand_total']['text']
    languages = data['languages'][:5] # 仅取前5种语言
    
    lines = [f"Today's Total Time: {total_time}", ""]
    
    for lang in languages:
        name = lang['name'].ljust(12)
        time_text = lang['text'].ljust(15)
        percent = lang['percent']
        bar = generate_bar(percent)
        lines.append(f"{name} {time_text} {bar} {percent:5.1f} %")
    
    return "\n".join(lines)

def update_gist(content):
    gh_token = os.getenv('GH_TOKEN')
    gist_id = os.getenv('GIST_ID_DAILY')
    
    if not gh_token or not gist_id:
        print("Missing GH_TOKEN or GIST_ID_DAILY")
        return
        
    headers = {
        "Authorization": f"token {gh_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 获取现有 gist 的第一个文件名
    get_url = f"https://api.github.com/gists/{gist_id}"
    get_res = requests.get(get_url, headers=headers)
    
    if get_res.status_code != 200:
        print(f"Failed to fetch gist: {get_res.status_code} - {get_res.text}")
        return
        
    files = get_res.json().get('files', {})
    filename = list(files.keys())[0] if files else "📊 Today's Activity.txt"
        
    data = {
        "files": {
            filename: {
                "content": content
            }
        }
    }
    
    response = requests.patch(get_url, headers=headers, json=data)
    if response.status_code == 200:
        print("Daily Gist updated successfully!")
    else:
        print(f"Failed to update daily gist: {response.status_code} - {response.text}")

if __name__ == "__main__":
    content = fetch_stats()
    with open("daily_stats.txt", "w", encoding="utf-8") as f:
        f.write(content)
    # 并将内容推送到 Gist
    update_gist(content)
