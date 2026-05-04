import akshare as ak
import pandas as pd

def get_stock_info(code, market='a'):
    """
    获取A股或港股的基本行情和财务摘要。
    code: 股票代码，如 '600519' (A股) 或 '00700' (港股)
    market: 'a' 表示A股，'hk' 表示港股
    返回: 包含行情和财务信息的字典，失败返回 None
    """
    try:
        if market == 'a':
            # ---------- A股行情 ----------
            df_spot = ak.stock_zh_a_spot_em()
            stock_row = df_spot[df_spot['代码'] == code]
            if stock_row.empty:
                print(f"⚠️ 未找到A股 {code}，请检查代码是否正确。")
                return None
            row = stock_row.iloc[0]
            info = {
    '代码': code,
    '名称': row['名称'],
    '最新价': float(row['最新价']),
    '涨跌幅': float(row['涨跌幅']),
    '成交额': round(float(row['成交额']) / 1e8, 2),
    '今开': float(row['今开']),
    '昨收': float(row['昨收']),
            }
            # A股财务摘要
            try:
                fin_df = ak.stock_financial_abstract_ths(symbol=code, indicator="按报告期")
                if not fin_df.empty:
                    latest = fin_df.iloc[0]
                    info['财务摘要'] = f"归属净利润:{latest.get('归属净利润', 'N/A')}, 营收:{latest.get('营业收入', 'N/A')}"
                else:
                    info['财务摘要'] = "暂无财务数据"
            except Exception:
                info['财务摘要'] = "财务数据获取失败"

        elif market == 'hk':
            # ---------- 港股行情 ----------
            df_spot = ak.stock_hk_spot_em()
            stock_row = df_spot[df_spot['代码'] == code]
            if stock_row.empty:
                print(f"⚠️ 未找到港股 {code}，请检查代码是否正确。")
                return None
            row = stock_row.iloc[0]
            info = {
    '代码': code,
    '名称': row['名称'],
    '最新价': float(row['最新价']),
    '涨跌幅': float(row['涨跌幅']),
    '成交额': round(float(row['成交额']) / 1e8, 2),
    '今开': float(row['今开']),
    '昨收': float(row['昨收']),
            }
            # 港股财务摘要
            try:
                fin_df = ak.stock_hk_financial_abstract_ths(symbol=code)
                if not fin_df.empty:
                    latest = fin_df.iloc[0]
                    info['财务摘要'] = f"营收:{latest.get('营业收入', 'N/A')}, 净利润:{latest.get('归属净利润', 'N/A')}"
                else:
                    info['财务摘要'] = "暂无财务数据"
            except Exception:
                info['财务摘要'] = "财务数据获取失败"
        else:
            print(f"❌ 未知市场类型: {market}")
            return None

        return info

    except Exception as e:
        print(f"❌ 获取 {code} 数据时出错: {e}")
        return None


# ---------- 测试 ----------
if __name__ == "__main__":
    # 测试A股
    print(get_stock_info('600519', 'a'))
    # 测试港股
    print(get_stock_info('00700', 'hk'))