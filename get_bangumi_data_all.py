import requests
import json
import time
from tqdm import tqdm

# --- 配置区 ---
BASE_URL = "https://api.bgm.tv/v0"


ACCESS_TOKEN = '---' # 此处填入bangumi api 

HEADERS = {
    'User-Agent': 'BangumiKnowledgeBaseBuilder/2.0 (YourContactInfo)',
    'Authorization': f'Bearer {ACCESS_TOKEN}',
}
OUTPUT_FILE = 'data.json'

# 建议保留一个较小的延迟，避免对API造成冲击
REQUEST_DELAY = 0.5 

# --- 脚本核心逻辑 ---

def get_top_anime_ids():
    """
    分页获取Bangumi **所有** 动画作品的ID。
    """
    print("开始获取 **所有** 动画ID (此过程可能耗时很久)...")
    subject_ids = []
    offset = 0
    page = 1
    
    while True:
        try:
            print(f"正在获取第 {page} 页的ID (offset: {offset})...")
            params = {
                'type': 2,
                'sort': 'rank', # 保留rank排序，即使中途中断，获取到的也是价值更高的数据
                'limit': 100,
                'offset': offset
            }
            response = requests.get(f"{BASE_URL}/subjects", headers=HEADERS, params=params)
            response.raise_for_status()
            
            data = response.json().get('data', [])
            
            # 退出循环的条件：当API返回的数据列表为空时
            if not data:
                print("API返回空数据，认定已获取所有ID。")
                break
                
            for item in data:
                subject_ids.append(item['id'])
            
            print(f"第 {page} 页获取成功，当前总计ID数: {len(subject_ids)}")
            
            offset += 100
            page += 1
            
            time.sleep(REQUEST_DELAY)

        except requests.exceptions.RequestException as e:
            print(f"获取ID列表时发生网络错误: {e}")
            print("程序将中断，但已获取的ID列表会返回。")
            break # 发生错误时中断
            
    print(f"ID获取阶段完成。成功获取 {len(subject_ids)} 个动画ID。")
    return subject_ids

def get_subject_details(subject_id):
    """根据作品ID获取其详细信息。"""
    try:
        response = requests.get(f"{BASE_URL}/subjects/{subject_id}", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # 在长时间运行中，单个请求失败不应中断整个过程，只打印错误并返回None
        print(f"\n警告: 获取作品ID {subject_id} 的详细信息时失败: {e}")
        return None

def main():
    """主执行函数"""
    anime_ids = get_top_anime_ids()
    if not anime_ids:
        print("未能获取动画ID列表，程序退出。")
        return

    knowledge_base = []
    print(f"\n开始为 {len(anime_ids)} 个动画获取详细信息...")
    
    for subject_id in tqdm(anime_ids, desc="处理动画详细信息"):
        details = get_subject_details(subject_id)
        if details:
            # 提取评分人数并加入最终数据
            rating_total = details.get('rating', {}).get('total', 0)
            
            anime_info = {
                "id": details.get('id'),
                "name": details.get('name_cn') or details.get('name', 'N/A'),
                "score": details.get('rating', {}).get('score', 0),
                "rank": details.get('rank', 0),
                "rating_total": rating_total, 
                "tags": [tag['name'] for tag in details.get('tags', [])[:10]],
                "summary": details.get('summary', '无简介').replace('\r\n', '\n'),
                "reviews": [] 
            }
            knowledge_base.append(anime_info)
        
        time.sleep(REQUEST_DELAY)

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, ensure_ascii=False, indent=4)
        print(f"\n处理完成！共 {len(knowledge_base)} 条动画信息已保存至 {OUTPUT_FILE}")
    except IOError as e:
        print(f"写入文件时出错: {e}")

if __name__ == '__main__':
    main()