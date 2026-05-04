import akshare as ak

def get_latest_news(count=20):
    """
    获取财联社最新电报资讯，返回拼接好的字符串。
    """
    try:
        df = ak.stock_info_global_cls()
        # 取最新的 count 条，只保留标题和时间
        latest = df.head(count)
        news_list = []
        for _, row in latest.iterrows():
            title = row['标题']
            time = row['发布时间']
            news_list.append(f"[{time}] {title}")
        return "\n".join(news_list)
    except Exception as e:
        print(f"获取资讯失败: {e}")
        return "暂无资讯"

if __name__ == '__main__':
    print(get_latest_news())