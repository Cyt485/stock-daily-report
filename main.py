import os
import requests
from openai import OpenAI
from get_data import get_stock_info   # 刚刚改好的统一函数
from get_news import get_latest_news  # 需要你先完成 get_news.py
from get_data import get_stock_info, get_industry_info
import pandas as pd

# ========== 配置区（改你私人的信息） ==========
DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY"   # 必填
STOCK_CODES = [
    {"code": "000100", "market": "a"},
    {"code": "605020", "market": "a"},
    {"code": "00189", "market": "hk"},
    {"code": "09992", "market": "hk"},
]
# 推送方式二选一，把不用的留空字符串
SERVERCHAN_SENDKEY = "SERVERCHAN_SENDKEY"          # Server酱 SendKey
WECHAT_WEBHOOK_URL = ""         # 企业微信机器人 webhook
# =============================================

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def build_analysis_prompt(stock_info, news_summary, industry_text):
    name = stock_info['名称']
    code = stock_info['代码']
    price = stock_info['最新价']
    change = stock_info['涨跌幅']
    amount = stock_info['成交额']
    fin = stock_info.get('财务摘要', '暂无数据')

    if 'N/A' in fin or '失败' in fin or '暂无' in fin:
        fin_note = "（暂无最新财务摘要，请仅基于技术面和新闻分析）"
    else:
        fin_note = fin

    change_sign = "📈" if change > 0 else "📉" if change < 0 else "➖"

    prompt = f"""作为金融分析师，请分析以下股票。回复严格遵循格式，不要多余内容。

股票: {name} ({code})
行情: 现价{price}，涨跌幅{change}%，成交额{amount}亿
财务: {fin_note}
行业: {industry_text if industry_text else '暂无行业数据'}
相关新闻: {news_summary}

格式要求：
**{name} ({code})** 现价{price} ({change_sign}{change}%)
🔹 技术面: [一句话]
🔹 基本面: [一句话]
🔹 行业: [一句话点评该行业今日整体表现及对个股影响]
🔹 舆情: [一句话]
🟢/🟡/🔴 综合评级: [一句话]
"""
    return prompt

def push_serverchan(sendkey, title, content):
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    data = {"title": title, "desp": content}
    r = requests.post(url, data=data)
    print(f"Server酱推送: {r.status_code}")

def push_wechat_webhook(webhook_url, content):
    headers = {"Content-Type": "application/json"}
    payload = {
        "msgtype": "markdown",
        "markdown": {"content": content}
    }
    r = requests.post(webhook_url, json=payload, headers=headers)
    print(f"企业微信推送: {r.status_code}")

def main():
    print("🔄 获取市场资讯...")
    news_text = get_latest_news(count=15)

    stock_prompts = []
    for cfg in STOCK_CODES:
        code = cfg["code"]
        market = cfg["market"]
        print(f"📊 获取 {market.upper()} {code} ...")
        info = get_stock_info(code, market)
        if info is None:
            print(f"⚠️ 跳过 {code}，数据获取失败")
            continue
        industry_info = get_industry_info(code, market)
        prompt_text = build_analysis_prompt(info, news_text, industry_info)
        stock_prompts.append({"role": "user", "content": prompt_text})

    if not stock_prompts:
        print("❌ 没有可分析的股票数据，结束运行。")
        return

    summary_prompt = "请用30字以内，概述今日以上所有市场资讯的总体基调。"
    stock_prompts.append({"role": "user", "content": summary_prompt})

    print("🤖 调用 DeepSeek 分析中...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业且极度精简的金融数据助理。回复必须确切，不添加任何无关解释。"},
                *stock_prompts
            ],
            temperature=0.3,
            max_tokens=800,
        )
        full_report = response.choices[0].message.content
        usage = response.usage
        print(f"✅ Token 消耗：输入 {usage.prompt_tokens}，输出 {usage.completion_tokens}")
        print("📄 报告内容：\n", full_report)
    except Exception as e:
        full_report = f"AI 分析失败: {e}"
        print(full_report)

    now_str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
    final_message = f"📈 股票晨报 - {now_str}\n\n{full_report}"

    if SERVERCHAN_SENDKEY:
        push_serverchan(SERVERCHAN_SENDKEY, "AI股票晨报", final_message)
    elif WECHAT_WEBHOOK_URL:
        push_wechat_webhook(WECHAT_WEBHOOK_URL, final_message)
    else:
        print("⚠️ 未配置推送方式，仅打印报告。")

if __name__ == "__main__":
    main()