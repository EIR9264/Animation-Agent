import json

# --- 配置区 ---
SOURCE_JSON_FILE = 'data.json'
OUTPUT_MD_FILE = '知识库.md'
# 使用清晰的分隔符，便于Dify进行文本分块(Chunking)
CHUNK_SEPARATOR = "\n---\n\n"

# --- 脚本核心逻辑 ---

def load_data_from_json(filepath):
    """
    从JSON文件中加载数据。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误: 未找到源文件 '{filepath}'。请先运行 get_bangumi_data.py 脚本。")
        return None
    except json.JSONDecodeError:
        print(f"错误: 文件 '{filepath}' 不是一个有效的JSON文件。")
        return None

def format_anime_to_markdown(anime_data):
    """
    将单个动画的数据格式化为Markdown文本块。
    """
    # 基础信息
    md_block = f"# 作品：{anime_data.get('name', 'N/A')}\n\n"
    md_block += f"**Bangumi ID**: {anime_data.get('id')}\n"
    md_block += f"**综合排名**: {anime_data.get('rank', '未排名')}\n"
    md_block += f"**平均评分**: {anime_data.get('score', '暂无评分')}\n\n"
    
    # 标签部分
    tags = anime_data.get('tags', [])
    if tags:
        md_block += "**核心标签**:\n"
        for tag in tags:
            md_block += f"- {tag}\n"
        md_block += "\n"
        
    # 简介部分
    summary = anime_data.get('summary', '无简介')
    if summary:
        md_block += f"**故事简介**:\n{summary}\n\n"
        
        
    return md_block

def main():
    """
    主执行函数
    """
    anime_list = load_data_from_json(SOURCE_JSON_FILE)
    
    if not anime_list:
        return

    print(f"开始将 {len(anime_list)} 条动画数据格式化为Markdown...")
    
    all_markdown_content = []
    for anime in anime_list:
        all_markdown_content.append(format_anime_to_markdown(anime))
        
    # 使用分隔符连接
    final_content = CHUNK_SEPARATOR.join(all_markdown_content)
    
    try:
        with open(OUTPUT_MD_FILE, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"成功！知识库文件已生成: {OUTPUT_MD_FILE}")
        print("您现在可以将此文件上传到Dify知识库中。")
        print("Dify会自动处理文本分块、向量化和索引。")
    except IOError as e:
        print(f"写入Markdown文件时出错: {e}")

if __name__ == '__main__':
    main()