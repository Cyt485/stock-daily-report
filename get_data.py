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
def get_industry_info(code, market='a'):
    """
    获取股票所属行业的今日行情摘要（一句话）。
    """
    try:
        if market == 'a':
            # --- A股：通过个股资料获取所属行业，再查行业板块表现 ---
            # 1. 获取个股所属行业名称（取第一个行业）
            ind_df = ak.stock_individual_info_em(symbol=code)
            industry_name = None
            if 'item' in ind_df.columns and 'value' in ind_df.columns:
                industry_row = ind_df[ind_df['item'] == '行业']
                if not industry_row.empty:
                    industry_name = industry_row['value'].values[0].split('，')[0].split(',')[0].strip()
            
            if not industry_name:
                return f"行业数据暂缺"

            # 2. 查询此行业板块的今日表现（修复版）
            # 先获取所有行业板块的实时数据
            board_df = ak.stock_board_industry_name_em()
            
            # 尝试精确匹配行业名称
            matched = board_df[board_df['板块名称'] == industry_name]
            
            # 如果精确匹配不到，再尝试模糊匹配
            if matched.empty:
                matched = board_df[board_df['板块名称'].str.contains(industry_name, na=False)]
                
            if not matched.empty:
                row = matched.iloc[0]
                pct = row['涨跌幅']
                lead_stock = row.get('领涨股票', '')
                
                # 构建返回信息
                return f"行业：{industry_name}（今日{'+' if pct > 0 else ''}{pct}%），领涨股：{lead_stock}"
            else:
                return f"行业：{industry_name}（今日行情数据暂缺）"

        elif market == 'hk':
            # --- 港股行业数据（暂时返回空，后续可优化）---
            return "（港股行业数据暂缺）"
        
        return ""
    except Exception as e:
        print(f"获取行业信息失败({code}): {e}")
        return ""