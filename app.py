import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
from fpdf import FPDF

# Configuração de Página
st.set_page_config(page_title="IA Agent Deal Desk (Beta)", layout="wide", initial_sidebar_state="expanded")

# Inicialização de Idioma
if 'lang' not in st.session_state:
    st.session_state.lang = 'pt'

# Dicionário de Traduções (i18n)
DIC = {
    'pt': {
        'title': 'IA Agent Deal Desk (Beta)',
        'tab1': '1️⃣ Configuração (Setup)', 'tab2': '🔍 Vendor Matrix', 'tab3': '🎯 Aprovação Executiva', 'tab4': '🧮 Cockpit DRE', 'tab5': '🤖 AI Advisor',
        'config_desc': 'Ajuste as premissas operacionais.',
        'op_vol': 'Operação & Volumetria', 'sessions': 'Sessões Mês (Volume)', 'aht': 'AHT Atual (seg)', 'rate': 'Blended Rate ($/h)', 'hours': 'Horas / Semana', 'inf': 'Dissídio Anual (%)',
        'serv_cap': 'Serviços & CapEx', 'impl_mo': 'Meses Implantação', 'setup_cost': 'Custo Setup ($)', 'setup_margin': 'Margem Setup (%)', 'maint_cost': 'Maint. Interna/Mês ($)', 'maint_margin': 'Margem Maint (%)',
        'ai_eff': 'Eficiência AI', 'cont': 'Containment Alvo (%)', 'aht_over': 'Penalidade Transbordo (%)', 'copilot': 'Ativar Copilot', 'copilot_red': 'Redução Copilot (%)', 'copilot_cost': 'Licença Assist ($/FTE)',
        'token': 'Tokenomics Base', 'in_tok': 'In Tokens / Sessão', 'out_tok': 'Out Tokens / Sessão', 'cache': 'Cache Hit Rate (%)', 'v_base_sidebar': 'Vendor Oficial (Baseline)',
        'com_mod': 'Modelos Comerciais', 'markup_lab': 'Markup Labor (%)', 'markup_tech': 'Markup s/ Tech (%)', 'gain_share': 'Gain-Share (%)', 'out_price': 'Ticket SaaS ($)',
        'v_matrix': 'OpEx Matrix',
        'strat': 'Estratégia de Negócio:', 'leg': '🏢 As-Is', 'c1': '🟢 C1 (Completo)', 'c2': '🟡 C2 (Gain-Share)', 'c3': '🔵 C3 (SaaS Ticket)',
        'ebitda': 'EBITDA BPO (3A)', 'margin': 'Margem Operacional', 'sav': 'Net Savings Cliente (3A)', 'vs_leg': 'vs Legado', 'cash': 'Fluxo de Caixa',
        'chart_title': 'Comparativo de EBITDA Acumulado', 'dre_res': 'DRE Resumida', 'rev': 'Faturamento Total', 'cost': 'Custos Totais', 'profit': 'EBITDA', 'cli_sav': 'Savings Cliente',
        'cockpit_title': 'Cockpit Financeiro Executivo', 'sel_cenario': 'Selecione o cenário para drill-down financeiro:', 'waterfall_title': 'Composição do EBITDA (Waterfall)', 'op_labor': 'Custos Laborais', 'op_tech': 'Custos Nuvem/Tech',
        'dre_full': 'Matriz DRE Analítica', 'down_xls': '📊 Baixar Planilha (XLSX)', 'down_pdf': '📄 Baixar Report (PDF)',
        'adv_title': 'Assistente Virtual Estratégico', 'adv_alert': 'ALERTA DE INVIABILIDADE', 'adv_ok': 'DEAL VIÁVEL',
        'win_cli': 'Vencedor p/ Cliente', 'win_bpo': 'Vencedor p/ BPO', 'score_title': 'Deal Viability Score',
        'exec_sum': 'Sumário Executivo', 'tech_ana': 'Análise Técnica', 'improve': 'Sugestões de Melhoria (TCO & EBITDA)'
    },
    'en': {
        'title': 'IA Agent Deal Desk (Beta)',
        'tab1': '1️⃣ Configuration (Setup)', 'tab2': '🔍 Vendor Matrix', 'tab3': '🎯 Executive Approval', 'tab4': '🧮 P&L Cockpit', 'tab5': '🤖 AI Advisor',
        'config_desc': 'Adjust the operational assumptions.',
        'op_vol': 'Operation & Volume', 'sessions': 'Monthly Sessions', 'aht': 'Current AHT (sec)', 'rate': 'Blended Rate ($/h)', 'hours': 'Hours / Week', 'inf': 'Wage Inflation (%)',
        'serv_cap': 'Services & CapEx', 'impl_mo': 'Implementation Mo.', 'setup_cost': 'Setup Cost ($)', 'setup_margin': 'Setup Margin (%)', 'maint_cost': 'Maint. Cost/Mo ($)', 'maint_margin': 'Maint Margin (%)',
        'ai_eff': 'AI Efficiency', 'cont': 'Target Containment (%)', 'aht_over': 'Overflow Penalty (%)', 'copilot': 'Enable Copilot', 'copilot_red': 'Copilot Reduction (%)', 'copilot_cost': 'Assist License ($/FTE)',
        'token': 'Tokenomics Base', 'in_tok': 'In Tokens / Sess', 'out_tok': 'Out Tokens / Sess', 'cache': 'Cache Hit Rate (%)', 'v_base_sidebar': 'Official Vendor (Baseline)',
        'com_mod': 'Commercial Models', 'markup_lab': 'Labor Markup (%)', 'markup_tech': 'Tech Markup (%)', 'gain_share': 'Gain-Share (%)', 'out_price': 'SaaS Ticket ($)',
        'v_matrix': 'OpEx Matrix',
        'strat': 'Business Strategy:', 'leg': '🏢 As-Is', 'c1': '🟢 C1 (Full)', 'c2': '🟡 C2 (Gain-Share)', 'c3': '🔵 C3 (SaaS Ticket)',
        'ebitda': 'BPO EBITDA (3Y)', 'margin': 'Operating Margin', 'sav': 'Client Net Savings (3Y)', 'vs_leg': 'vs Legacy', 'cash': 'Cash Flow',
        'chart_title': 'Cumulative EBITDA Comparison', 'dre_res': 'Summarized P&L', 'rev': 'Total Revenue', 'cost': 'Total Costs', 'profit': 'EBITDA', 'cli_sav': 'Client Savings',
        'cockpit_title': 'Executive Financial Cockpit', 'sel_cenario': 'Select scenario for financial drill-down:', 'waterfall_title': 'EBITDA Composition (Waterfall)', 'op_labor': 'Labor Costs', 'op_tech': 'Cloud/Tech Costs',
        'dre_full': 'Analytical P&L Matrix', 'down_xls': '📊 Download Spreadsheet', 'down_pdf': '📄 Download Report',
        'adv_title': 'Strategic Virtual Assistant', 'adv_alert': 'UNVIABILITY ALERT', 'adv_ok': 'VIABLE DEAL',
        'win_cli': 'Winner for Client', 'win_bpo': 'Winner for BPO', 'score_title': 'Deal Viability Score',
        'exec_sum': 'Executive Summary', 'tech_ana': 'Technical Analysis', 'improve': 'Improvement Suggestions (TCO & EBITDA)'
    }
}

def t(key): return DIC[st.session_state.lang].get(key, key)

# CSS Customizado
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    .g-card { background-color: #ffffff; border: 1px solid #dadce0; border-radius: 8px; padding: 24px; box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3); margin-bottom: 16px; }
    .g-label { color: #5f6368; font-size: 0.875rem; font-weight: 500; text-transform: uppercase; margin-bottom: 8px; }
    .g-value { color: #202124; font-size: 2.1rem; font-weight: 400; line-height: 1.2; }
    .g-delta-positive { color: #1a73e8; font-size: 0.875rem; font-weight: 500; margin-top: 8px;}
    .g-delta-negative { color: #ea4335; font-size: 0.875rem; font-weight: 500; margin-top: 8px;}
    .g-delta-neutral { color: #5f6368; font-size: 0.875rem; font-weight: 500; margin-top: 8px;}
    .g-pitch-box { background-color: #e8f0fe; padding: 20px; border-radius: 8px; border-left: 4px solid #1a73e8; font-size: 1.05rem; color: #202124; line-height: 1.5; margin-bottom:15px;}
    </style>
""", unsafe_allow_html=True)

# SIDEBAR (Global Vendor Selection corrigida)
with st.sidebar:
    st.markdown(f"### ⚙️ {t('v_base_sidebar')}")
    vendor_global = st.selectbox("", ["Kore.AI", "Omilia", "Cresta"], label_visibility="collapsed")
    st.info("O vendor selecionado aqui guia toda a matriz financeira das abas executivas.")

# Top Header com Bandeiras
col_title, col_us, col_br = st.columns([10, 1, 1])
with col_title: st.markdown(f"<h2 style='color: #202124; font-weight: 400; margin-bottom: 24px;'>{t('title')}</h2>", unsafe_allow_html=True)
with col_us: 
    if st.button("🇺🇸"): st.session_state.lang = 'en'; st.rerun()
with col_br: 
    if st.button("🇧🇷"): st.session_state.lang = 'pt'; st.rerun()

# ==========================================
# MÓDULO 1: MOTORES DE CÁLCULO CORE 
# ==========================================
def get_llm_cost_per_session(p):
    return (((p["input_tokens"] * p["cache_hit_rate"]) / 1e6 * p["cost_input_cached_m"]) +
            ((p["input_tokens"] * (1.0 - p["cache_hit_rate"])) / 1e6 * p["cost_input_noncached_m"]) +
            (p["output_tokens"] / 1e6 * p["cost_output_m"]))

def get_platform_monthly_cost(p, monthly_ai_sessions):
    if p["vendor"] == "Kore.AI": return (monthly_ai_sessions * p["kore_session"]) + (p["kore_support_3y"] / 36.0) + (p["kore_expert_1y"] / 12.0)
    elif p["vendor"] == "Omilia": return (monthly_ai_sessions * p["omilia_session"]) + p["omilia_rag_month"] + ((monthly_ai_sessions * (p["omilia_chars_per_session"]/1e6)) * p["omilia_tts_1m"])
    elif p["vendor"] == "Cresta": return monthly_ai_sessions * p["cresta_ai_mins"] * p["cresta_per_min"]
    return 0.0

def get_payback(savings_acum_array):
    pos_idx = np.where(savings_acum_array > 0)[0]
    return int(pos_idx[0] + 1) if len(pos_idx) > 0 else 99

def calculate_viability_score(margin, savings, payback_months, legacy_rev):
    score = 0
    score += min(max((margin / 35.0) * 40, 0), 40)
    sav_pct = savings / legacy_rev if legacy_rev > 0 else 0
    score += min(max((sav_pct / 0.10) * 40, 0), 40)
    if payback_months <= 6: score += 20
    elif payback_months > 36: score += 0
    else: score += 20 * (1 - (payback_months - 6)/30.0)
    return min(max(int(score), 0), 100)

# ==========================================
# MÓDULO 2: ENGENHARIA DE VALOR (UI)
# ==========================================
tab_eng, tab_vendor, tab_dash, tab_dre, tab_advisor = st.tabs([t('tab1'), t('tab2'), t('tab3'), t('tab4'), t('tab5')])

with tab_eng:
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        st.markdown(f"#### 💼 {t('op_vol')}")
        sessions_month = st.number_input(t('sessions'), 1, value=30000, step=1000)
        aht_seconds = st.number_input(t('aht'), 1, value=750, step=10)
        agent_cost_hr = st.number_input(t('rate'), 0.1, value=3.45, step=0.1)
        productive_hours_week = st.number_input(t('hours'), 1.0, value=40.0, step=1.0)
        fte_inflation_rate = st.number_input(t('inf'), value=5.0) / 100.0
        st.markdown(f"#### 🔧 {t('serv_cap')}")
        implementation_months = st.number_input(t('impl_mo'), 0, 36, value=6)
        setup_cost_internal = st.number_input(t('setup_cost'), 0.0, value=35714.0)
        setup_fee = setup_cost_internal * (1.0 + (st.number_input(t('setup_margin'), value=40.0) / 100.0))
        maint_cost_internal = st.number_input(t('maint_cost'), 0.0, value=3385.0)
        maint_fee_month = maint_cost_internal * (1.0 + (st.number_input(t('maint_margin'), value=47.7)/100.0))
    with col_in2:
        st.markdown(f"#### 🤖 {t('ai_eff')}")
        containment_mean = st.slider(t('cont'), 0, 100, 35) / 100.0
        aht_overflow_variation = st.slider(t('aht_over'), 0, 50, 15) / 100.0
        use_agent_assist = st.toggle(t('copilot'))
        agent_assist_reduction = st.slider(t('copilot_red'), 0, 50, 20) / 100.0 if use_agent_assist else 0.0
        agent_assist_cost_fte = st.number_input(t('copilot_cost'), 0.0, value=40.0) if use_agent_assist else 0.0
        st.markdown(f"#### ☁️ {t('token')}")
        input_tokens = st.number_input(t('in_tok'), 100, value=50000)
        output_tokens = st.number_input(t('out_tok'), 100, value=1000)
        cache_hit_rate = st.slider(t('cache'), 0, 100, 50) / 100.0
        cost_input_cached_m = 0.18; cost_input_noncached_m = 1.75; cost_output_m = 14.00
    with col_in3:
        st.markdown(f"#### 💰 {t('com_mod')}")
        bpo_markup = st.number_input(t('markup_lab'), value=30.0) / 100.0
        tech_markup = st.number_input(t('markup_tech'), value=10.0) / 100.0
        bpo_gain_share = st.number_input(t('gain_share'), value=40.0) / 100.0
        outcome_price = st.number_input(t('out_price'), 0.01, value=1.20)

    st.divider()
    v1, v2, v3 = st.columns(3)
    with v1:
        st.write("**Kore.AI**")
        kore_session = st.number_input("Session ($)", value=0.116, format="%.3f")
        kore_support_3y = st.number_input("Support 3Y ($)", value=28000.0)
        kore_expert_1y = st.number_input("Expert 1Y ($)", value=7000.0)
    with v2:
        st.write("**Omilia**")
        omilia_session = st.number_input("Call ($)", value=0.045, format="%.3f")
        omilia_rag_month = st.number_input("RAG/Mo ($)", value=750.0)
        omilia_tts_1m = st.number_input("TTS/1M ($)", value=7.0)
        omilia_chars_per_session = 3750
    with v3:
        st.write("**Cresta**")
        cresta_per_min = st.number_input("Min Price ($)", value=0.10, format="%.2f")
        cresta_ai_mins = st.number_input("Mins/Session", value=5.0)

params = {
    "sessions_month": sessions_month, "aht_seconds": aht_seconds, "aht_std_dev": 50, "agent_cost_hr": agent_cost_hr,
    "fte_inflation_rate": fte_inflation_rate, "productive_hours_week": productive_hours_week,
    "containment_mean": containment_mean, "containment_std_dev": 0.05, "aht_overflow_variation": aht_overflow_variation,
    "agent_assist_reduction": agent_assist_reduction, "agent_assist_cost_fte": agent_assist_cost_fte,
    "implementation_months": implementation_months, "setup_cost_internal": setup_cost_internal, "setup_fee": setup_fee,
    "maint_cost_internal": maint_cost_internal, "maint_fee_month": maint_fee_month,
    "input_tokens": input_tokens, "output_tokens": output_tokens, "cache_hit_rate": cache_hit_rate,
    "cost_input_cached_m": cost_input_cached_m, "cost_input_noncached_m": cost_input_noncached_m, "cost_output_m": cost_output_m,
    "bpo_markup": bpo_markup, "tech_markup": tech_markup, "bpo_gain_share": bpo_gain_share, "outcome_price": outcome_price,
    "vendor": vendor_global,
    "kore_session": kore_session, "kore_support_3y": kore_support_3y, "kore_expert_1y": kore_expert_1y,
    "omilia_session": omilia_session, "omilia_rag_month": omilia_rag_month, "omilia_tts_1m": omilia_tts_1m, "omilia_chars_per_session": omilia_chars_per_session,
    "cresta_per_min": cresta_per_min, "cresta_ai_mins": cresta_ai_mins
}

# ==========================================
# MÓDULO 3: VENDORS E SIMULAÇÃO CORE
# ==========================================
with tab_vendor:
    st.markdown(f"<h3 style='color:#202124;'>{t('v_matrix')}</h3>", unsafe_allow_html=True)
    ai_vol_target = sessions_month * containment_mean
    plat_k = get_platform_monthly_cost({"vendor": "Kore.AI", **params}, ai_vol_target)
    plat_o = get_platform_monthly_cost({"vendor": "Omilia", **params}, ai_vol_target)
    plat_c = get_platform_monthly_cost({"vendor": "Cresta", **params}, ai_vol_target)
    llm_mensal_bpo = ai_vol_target * get_llm_cost_per_session(params)
    
    vcol1, vcol2, vcol3 = st.columns(3)
    with vcol1: st.markdown(f"<div class='g-card'><div class='g-label'>Kore.AI</div><div class='g-value'>${(plat_k + llm_mensal_bpo):,.2f} <span style='font-size:1rem;color:#5f6368;'>/mo</span></div><div class='g-delta-neutral'>Platform: ${plat_k:,.0f} | LLM: ${llm_mensal_bpo:,.0f}</div></div>", unsafe_allow_html=True)
    with vcol2: st.markdown(f"<div class='g-card'><div class='g-label'>Omilia</div><div class='g-value'>${(plat_o + llm_mensal_bpo):,.2f} <span style='font-size:1rem;color:#5f6368;'>/mo</span></div><div class='g-delta-neutral'>Platform: ${plat_o:,.0f} | LLM: ${llm_mensal_bpo:,.0f}</div></div>", unsafe_allow_html=True)
    with vcol3: st.markdown(f"<div class='g-card'><div class='g-label'>Cresta</div><div class='g-value'>${(plat_c + llm_mensal_bpo):,.2f} <span style='font-size:1rem;color:#5f6368;'>/mo</span></div><div class='g-delta-neutral'>Platform: ${plat_c:,.0f} | LLM: ${llm_mensal_bpo:,.0f}</div></div>", unsafe_allow_html=True)

@st.cache_data
def run_deal_desk_simulation(p):
    np.random.seed(42)
    ITERATIONS = 3000
    productive_hours_month = (30.42 / 7.0) * p["productive_hours_week"]
    
    sim_containment = np.clip(np.random.normal(p["containment_mean"], p["containment_std_dev"], ITERATIONS), 0.0, 1.0)
    sim_aht = np.clip(np.random.normal(p["aht_seconds"], p["aht_std_dev"], ITERATIONS), 60.0, None)
    
    ai_sessions = p["sessions_month"] * sim_containment
    human_sessions = p["sessions_month"] * (1.0 - sim_containment)
    new_human_aht = sim_aht * (1.0 + p["aht_overflow_variation"]) * (1.0 - p["agent_assist_reduction"])
    
    base_asis_labor = (p["sessions_month"] * sim_aht / 3600.0) * p["agent_cost_hr"]
    base_tobe_labor = (human_sessions * new_human_aht / 3600.0) * p["agent_cost_hr"]
    
    meses = np.arange(1, 37)
    inflation_multiplier = np.array([(1.0 + p["fte_inflation_rate"])**((m-1)//12) for m in meses])
    
    matriz_asis_labor = base_asis_labor[:, None] * inflation_multiplier[None, :]
    matriz_tobe_labor = base_tobe_labor[:, None] * inflation_multiplier[None, :]
    
    impl_mask = np.array([1.0 if m <= p["implementation_months"] else 0.0 for m in meses])
    live_mask = 1.0 - impl_mask
    matriz_tobe_misto = (matriz_asis_labor * impl_mask[None, :]) + (matriz_tobe_labor * live_mask[None, :])
    
    p50_ai_sessions = np.percentile(ai_sessions, 50)
    p50_asis_mo = np.percentile(matriz_asis_labor, 50, axis=0)
    p50_tobe_mo = np.percentile(matriz_tobe_misto, 50, axis=0)
    
    llm_cps = get_llm_cost_per_session(p)
    plat_mo = get_platform_monthly_cost(p, p50_ai_sessions)
    llm_mo = p50_ai_sessions * llm_cps
    
    # QA FIX: Precisamos do número de FTEs para calcular licença do Agent Assist
    tobe_ftes_mo = np.percentile((human_sessions * new_human_aht / 3600.0) / productive_hours_month, 50)
    agent_assist_tech_mo = tobe_ftes_mo * p["agent_assist_cost_fte"]
    
    bpo_custo_tech_mo = np.array([plat_mo + llm_mo for m in meses]) + (agent_assist_tech_mo * live_mask)
    bpo_custo_labor_array = p50_tobe_mo
    bpo_custo_maint_mo = p["maint_cost_internal"] * live_mask
    
    faturamento_asis_cliente = p50_asis_mo * (1.0 + p["bpo_markup"])
    
    # CENÁRIOS
    c1_faturamento_tech = bpo_custo_tech_mo * (1.0 + p["tech_markup"])
    c1_bpo_rev_mo = (p50_tobe_mo * (1.0 + p["bpo_markup"])) + (p["maint_fee_month"] * live_mask) + c1_faturamento_tech
    c1_bpo_cost_mo = bpo_custo_labor_array + bpo_custo_maint_mo + bpo_custo_tech_mo
    c1_bpo_ebitda_mo = c1_bpo_rev_mo - c1_bpo_cost_mo
    c1_bpo_rev_total = np.sum(c1_bpo_rev_mo) + p["setup_fee"]
    c1_bpo_ebitda_total = np.sum(c1_bpo_ebitda_mo) + (p["setup_fee"] - p["setup_cost_internal"])
    c1_cliente_tco = c1_bpo_rev_mo + np.array([p["setup_fee"] if m == 1 else 0.0 for m in meses])
    c1_monthly_savings = faturamento_asis_cliente - c1_cliente_tco
    c1_cliente_savings_acum = np.cumsum(c1_monthly_savings)
    
    c1_cost_labor = np.sum(bpo_custo_labor_array) + np.sum(bpo_custo_maint_mo)
    c1_cost_tech = np.sum(bpo_custo_tech_mo) + p["setup_cost_internal"]
    
    c2_gain_share_rev = np.where((c1_cliente_savings_acum > 0) & (c1_monthly_savings > 0), c1_monthly_savings * p["bpo_gain_share"], 0.0)
    c2_cliente_tco = c1_cliente_tco + c2_gain_share_rev
    c2_cliente_savings_acum = np.cumsum(faturamento_asis_cliente - c2_cliente_tco)
    c2_bpo_rev_mo = c1_bpo_rev_mo + c2_gain_share_rev
    c2_bpo_ebitda_mo = c2_bpo_rev_mo - c1_bpo_cost_mo
    c2_bpo_rev_total = np.sum(c2_bpo_rev_mo) + p["setup_fee"]
    c2_bpo_ebitda_total = np.sum(c2_bpo_ebitda_mo) + (p["setup_fee"] - p["setup_cost_internal"])
    
    c3_outcome_rev_mo = (p50_ai_sessions * p["outcome_price"]) * live_mask
    c3_bpo_rev_mo = (p50_tobe_mo * (1.0 + p["bpo_markup"])) + c3_outcome_rev_mo + (p["maint_fee_month"] * live_mask)
    c3_bpo_cost_mo = bpo_custo_labor_array + bpo_custo_maint_mo + bpo_custo_tech_mo
    c3_bpo_ebitda_mo = c3_bpo_rev_mo - c3_bpo_cost_mo
    c3_bpo_rev_total = np.sum(c3_bpo_rev_mo) + p["setup_fee"]
    c3_bpo_ebitda_total = np.sum(c3_bpo_ebitda_mo) + (p["setup_fee"] - p["setup_cost_internal"])
    c3_cliente_tco = c3_bpo_rev_mo + np.array([p["setup_fee"] if m == 1 else 0.0 for m in meses])
    c3_cliente_savings_acum = np.cumsum(faturamento_asis_cliente - c3_cliente_tco)

    # QA FIX: DRE Functions alinhadas para garantir que Tech y1 inclui CapEx Setup e Labor Opex existe
    def agrupar_anos(array_mensal): return [np.sum(array_mensal[0:12]), np.sum(array_mensal[12:24]), np.sum(array_mensal[24:36])]
    def agrupar_anos_tech(array_mensal, setup): return [np.sum(array_mensal[0:12]) + setup, np.sum(array_mensal[12:24]), np.sum(array_mensal[24:36])]
    
    rev_legado = np.sum(faturamento_asis_cliente)
    ebitda_legado = rev_legado - np.sum(p50_asis_mo)
    labor_arr_total = bpo_custo_labor_array + bpo_custo_maint_mo
    
    return {
        "c1": {"rev": c1_bpo_rev_total, "ebitda": c1_bpo_ebitda_total, "sav": c1_cliente_savings_acum[-1], "payback": get_payback(c1_cliente_savings_acum), "labor": c1_cost_labor, "tech": c1_cost_tech, "rev_y": agrupar_anos(c1_bpo_rev_mo), "ebitda_y": agrupar_anos(c1_bpo_ebitda_mo), "sav_y": agrupar_anos(c1_monthly_savings), "tech_y": agrupar_anos_tech(bpo_custo_tech_mo, p["setup_cost_internal"]), "labor_y": agrupar_anos(labor_arr_total)},
        "c2": {"rev": c2_bpo_rev_total, "ebitda": c2_bpo_ebitda_total, "sav": c2_cliente_savings_acum[-1], "payback": get_payback(c2_cliente_savings_acum), "labor": c1_cost_labor, "tech": c1_cost_tech, "rev_y": agrupar_anos(c2_bpo_rev_mo), "ebitda_y": agrupar_anos(c2_bpo_ebitda_mo), "sav_y": agrupar_anos(faturamento_asis_cliente - c2_cliente_tco), "tech_y": agrupar_anos_tech(bpo_custo_tech_mo, p["setup_cost_internal"]), "labor_y": agrupar_anos(labor_arr_total)},
        "c3": {"rev": c3_bpo_rev_total, "ebitda": c3_bpo_ebitda_total, "sav": c3_cliente_savings_acum[-1], "payback": get_payback(c3_cliente_savings_acum), "labor": c1_cost_labor, "tech": c1_cost_tech, "rev_y": agrupar_anos(c3_bpo_rev_mo), "ebitda_y": agrupar_anos(c3_bpo_ebitda_mo), "sav_y": agrupar_anos(faturamento_asis_cliente - c3_cliente_tco), "tech_y": agrupar_anos_tech(bpo_custo_tech_mo, p["setup_cost_internal"]), "labor_y": agrupar_anos(labor_arr_total)},
        "legado": {"rev": rev_legado, "ebitda": ebitda_legado, "rev_y": agrupar_anos(faturamento_asis_cliente), "ebitda_y": agrupar_anos(faturamento_asis_cliente - p50_asis_mo)}
    }

sim = run_deal_desk_simulation(params)
def calc_margin(ebitda, rev): return (ebitda / rev) * 100.0 if rev > 0 else 0.0

# ==========================================
# MÓDULO 4: DASHBOARDS (MATERIAL DESIGN)
# ==========================================
with tab_dash:
    col_m, col_h = st.columns([1, 4])
    with col_m: cenario_ativo = st.radio(t('strat'), [t('leg'), t('c1'), t('c2'), t('c3')])
    
    dados = sim['legado'] if "As-Is" in cenario_ativo or "Legacy" in cenario_ativo else sim['c1'] if "C1" in cenario_ativo else sim['c2'] if "C2" in cenario_ativo else sim['c3']
    s_cli = 0 if "As-Is" in cenario_ativo or "Legacy" in cenario_ativo else dados['sav']
    m_ativa = calc_margin(dados['ebitda'], dados['rev'])
    m_legado = calc_margin(sim['legado']['ebitda'], sim['legado']['rev'])
    
    delta_ebitda = dados['ebitda'] - sim['legado']['ebitda']
    
    with col_h:
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='g-card'><div class='g-label'>{t('ebitda')}</div><div class='g-value'>${dados['ebitda']:,.0f}</div><div class='{'g-delta-positive' if delta_ebitda >=0 else 'g-delta-negative'}'>{'↑' if delta_ebitda>=0 else '↓'} ${abs(delta_ebitda):,.0f} {t('vs_leg')}</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='g-card'><div class='g-label'>{t('margin')}</div><div class='g-value'>{m_ativa:.1f}%</div><div class='g-delta-neutral'>{m_ativa - m_legado:+.1f} p.p. {t('vs_leg')}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='g-card'><div class='g-label'>{t('sav')}</div><div class='g-value'>${s_cli:,.0f}</div><div class='{'g-delta-positive' if s_cli >=0 else 'g-delta-negative'}'>{'↑' if s_cli>=0 else '↓'} {t('cash')}</div></div>", unsafe_allow_html=True)
        
    col_g, col_t = st.columns([1.5, 1])
    with col_g:
        fig = go.Figure()
        cores = ["#dadce0", "#1a73e8" if "C1" in cenario_ativo else "#dadce0", "#fbbc04" if "C2" in cenario_ativo else "#dadce0", "#34a853" if "C3" in cenario_ativo else "#dadce0"]
        fig.add_trace(go.Bar(x=['As-Is', 'C1', 'C2', 'C3'], y=[sim['legado']['ebitda'], sim['c1']['ebitda'], sim['c2']['ebitda'], sim['c3']['ebitda']], marker_color=cores))
        fig.update_layout(title=t('chart_title'), height=320, plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Roboto, sans-serif", color="#5f6368"))
        st.plotly_chart(fig, use_container_width=True)
    with col_t:
        st.markdown(f"<div class='g-label'>{t('dre_res')}</div>", unsafe_allow_html=True)
        dre_df = pd.DataFrame({"Rubrica": [t('rev'), t('cost'), t('profit'), t('cli_sav')], "Valor": [f"${dados['rev']:,.0f}", f"${dados['rev'] - dados['ebitda']:,.0f}", f"${dados['ebitda']:,.0f}", f"${s_cli:,.0f}"]})
        st.dataframe(dre_df, hide_index=True)

# ==========================================
# MÓDULO 5: COCKPIT DRE EXECUTIVE
# ==========================================
with tab_dre:
    st.markdown(f"<h3 style='color:#202124;'>🧮 {t('cockpit_title')}</h3>", unsafe_allow_html=True)
    
    drill_cenario = st.selectbox(t('sel_cenario'), ["C1 (Completo)", "C2 (Gain-Share)", "C3 (SaaS Ticket)"])
    k_drill = "c1" if "C1" in drill_cenario else "c2" if "C2" in drill_cenario else "c3"
    d_drill = sim[k_drill]
    
    cw1, cw2 = st.columns([1, 1.5])
    with cw1:
        st.markdown(f"**{t('waterfall_title')}**")
        fig_wf = go.Figure(go.Waterfall(
            name = "20", orientation = "v",
            measure = ["relative", "relative", "relative", "total"],
            x = [t('rev'), t('op_labor'), t('op_tech'), t('profit')],
            y = [d_drill['rev'], -d_drill['labor'], -d_drill['tech'], d_drill['ebitda']],
            textposition = "outside",
            text = [f"${d_drill['rev']/1000:,.0f}k", f"-${d_drill['labor']/1000:,.0f}k", f"-${d_drill['tech']/1000:,.0f}k", f"${d_drill['ebitda']/1000:,.0f}k"],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
            decreasing = {"marker":{"color":"#ea4335"}}, increasing = {"marker":{"color":"#1a73e8"}}, totals = {"marker":{"color":"#34a853"}}
        ))
        fig_wf.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Roboto, sans-serif"))
        st.plotly_chart(fig_wf, use_container_width=True)
        
    with cw2:
        st.markdown(f"**{t('dre_full')}**")
        def b_rows(ck):
            d = sim[ck]
            return [[f"{ck.upper()} - {t('rev')}", f"${d['rev_y'][0]:,.0f}", f"${d['rev_y'][1]:,.0f}", f"${d['rev_y'][2]:,.0f}", f"${d['rev']:,.0f}"],
                    [f"{ck.upper()} - {t('op_labor')}", f"${d['labor_y'][0]:,.0f}", f"${d['labor_y'][1]:,.0f}", f"${d['labor_y'][2]:,.0f}", f"${d['labor']:,.0f}"],
                    [f"{ck.upper()} - Cloud / Tech", f"${d['tech_y'][0]:,.0f}", f"${d['tech_y'][1]:,.0f}", f"${d['tech_y'][2]:,.0f}", f"${d['tech']:,.0f}"],
                    [f"{ck.upper()} - {t('profit')}", f"${d['ebitda_y'][0]:,.0f}", f"${d['ebitda_y'][1]:,.0f}", f"${d['ebitda_y'][2]:,.0f}", f"${d['ebitda']:,.0f}"],
                    [f"{ck.upper()} - {t('cli_sav')}", f"${d['sav_y'][0]:,.0f}", f"${d['sav_y'][1]:,.0f}", f"${d['sav_y'][2]:,.0f}", f"${d['sav']:,.0f}"]]
        df_all = b_rows('c1') + b_rows('c2') + b_rows('c3')
        st.dataframe(pd.DataFrame(df_all, columns=["Metric", "Year 1", "Year 2", "Year 3", "Total"]), use_container_width=True, hide_index=True)
        
        cx1, cx2 = st.columns(2)
        with cx1:
            oxl = io.BytesIO()
            with pd.ExcelWriter(oxl, engine='xlsxwriter') as w: pd.DataFrame(df_all).to_excel(w, sheet_name='DRE', index=False)
            st.download_button(t('down_xls'), data=oxl.getvalue(), file_name="DRE_Matrix.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
        with cx2:
            def make_pdf():
                p = FPDF(); p.add_page(); p.set_font("Arial", size=14, style='B'); p.cell(200, 10, "Executive Financial Cockpit", ln=True, align='C')
                p.set_font("Arial", size=11); p.cell(200, 10, f"Vendor: {params['vendor']} | Volume: {params['sessions_month']} calls", ln=True)
                return bytes(p.output())
            st.download_button(t('down_pdf'), data=make_pdf(), file_name="P_L_Summary.pdf", mime="application/pdf", use_container_width=True)

# ==========================================
# MÓDULO 6: AI ADVISOR & PITCH
# ==========================================
with tab_advisor:
    st.markdown(f"<h3 style='color:#202124;'>{t('adv_title')}</h3>", unsafe_allow_html=True)
    c1_sav, c2_sav, c3_sav = sim['c1']['sav'], sim['c2']['sav'], sim['c3']['sav']
    c1_eb, c2_eb, c3_eb = sim['c1']['ebitda'], sim['c2']['ebitda'], sim['c3']['ebitda']
    
    best_for_client = "C1" if c1_sav >= c2_sav and c1_sav >= c3_sav else "C2" if c2_sav >= c3_sav else "C3"
    best_for_bpo = "C3" if c3_eb >= c2_eb and c3_eb >= c1_eb else "C2" if c2_eb >= c1_eb else "C1"
    
    ref_data = sim['c3'] if best_for_bpo == "C3" else sim['c2'] if best_for_bpo == "C2" else sim['c1']
    v_score = calculate_viability_score(calc_margin(ref_data['ebitda'], ref_data['rev']), ref_data['sav'], ref_data['payback'], sim['legado']['rev'])
    
    col_gauge, col_adv1, col_adv2 = st.columns([1.5, 1, 1])
    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = v_score, title = {'text': t('score_title'), 'font': {'size': 18, 'color': '#5f6368'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#1a73e8"},
                'steps': [{'range': [0, 40], 'color': "#fce8e6"}, {'range': [40, 70], 'color': "#fef7e0"}, {'range': [70, 100], 'color': "#e6f4ea"}],
                'threshold': {'line': {'color': "#ea4335", 'width': 4}, 'thickness': 0.75, 'value': 90}
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with col_adv1: 
        st.markdown(f"<div class='g-card' style='height: 100%;'><div class='g-label'>{t('win_cli')}</div><div class='g-value' style='font-size:1.5rem;'>{best_for_client}</div></div>", unsafe_allow_html=True)
    with col_adv2: 
        st.markdown(f"<div class='g-card' style='height: 100%;'><div class='g-label'>{t('win_bpo')}</div><div class='g-value' style='font-size:1.5rem;'>{best_for_bpo}</div></div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='g-label'>{t('exec_sum')}</div>", unsafe_allow_html=True)
    is_pt = st.session_state.lang == 'pt'
    exec_txt = f"Este business case processa **{params['sessions_month']:,}** interações mensais. A meta é transferir {params['containment_mean']*100:.0f}% desse volume para o framework cognitivo da **{params['vendor']}**. O projeto exige **{params['implementation_months']} meses** de implantação e um CapEx de **${params['setup_fee']:,.0f}**. O Payback do cliente ocorre no mês **{ref_data['payback']}**." if is_pt else f"This business case processes **{params['sessions_month']:,}** monthly interactions. The goal is to transfer {params['containment_mean']*100:.0f}% of this volume to the cognitive framework of **{params['vendor']}**. The project requires **{params['implementation_months']} months** of implementation and a CapEx of **${params['setup_fee']:,.0f}**. Client Payback occurs in month **{ref_data['payback']}**."
    st.markdown(f"<div class='g-pitch-box' style='background-color:#f8f9fa; border-left-color:#dadce0;'>{exec_txt}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='g-label'>{t('tech_ana')}</div>", unsafe_allow_html=True)
    tech_txt = f"A arquitetura LLM consumirá {params['input_tokens']:,} tokens/sessão. O *Cache Hit Rate* está em **{params['cache_hit_rate']*100:.0f}%**." if is_pt else f"LLM architecture consumes {params['input_tokens']:,} tokens/session. *Cache Hit Rate* is at **{params['cache_hit_rate']*100:.0f}%**."
    st.markdown(f"<div class='g-pitch-box' style='background-color:#f8f9fa; border-left-color:#dadce0;'>{tech_txt}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='g-label'>{t('improve')}</div>", unsafe_allow_html=True)
    imp_list = []
    if params['cache_hit_rate'] < 0.8:
        imp_list.append("🔹 Aumentar o Cache Hit Rate para 80%+ via Prompt Engineering. Isso injeta margem direta no EBITDA." if is_pt else "🔹 Increase Cache Hit Rate to 80%+ via Prompt Engineering to inject direct margin into EBITDA.")
    if params['implementation_months'] > 4:
        imp_list.append("🔹 Reduzir o Go-Live para 3-4 meses. Implantações longas arrastam a 'Curva J' e destroem o TCO no Ano 1." if is_pt else "🔹 Reduce Go-Live to 3-4 months. Long implementations drag the financial 'J-Curve'.")
    if params['containment_mean'] < 0.4:
        imp_list.append("🔹 Focar no tuning das Top 3 intenções operacionais para forçar a contenção acima de 40%." if is_pt else "🔹 Focus on tuning the Top 3 operational intents to push containment above 40%.")
    for imp in imp_list: st.markdown(f"<div style='margin-bottom:8px; color:#202124;'>{imp}</div>", unsafe_allow_html=True)