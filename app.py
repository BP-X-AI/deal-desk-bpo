import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import time
import hashlib
import json
from fpdf import FPDF

# Configuração de Página
st.set_page_config(page_title="IA Agent Deal Desk (Beta)", layout="wide", initial_sidebar_state="expanded")

# Inicialização de Estado (i18n e GenAI)
if 'lang' not in st.session_state: st.session_state.lang = 'pt'
if 'genai_pitch' not in st.session_state: st.session_state.genai_pitch = None

# Dicionário de Traduções (i18n)
DIC = {
    'pt': {
        'title': 'IA Agent Deal Desk (Beta)',
        'tab1': '1️⃣ Configuração (Setup)', 'tab2': '🔍 Vendor Matrix', 'tab3': '🎯 Aprovação Executiva', 'tab4': '🧮 Cockpit DRE', 'tab5': '🤖 GenAI Advisor',
        'op_vol': 'Operação & Volumetria', 'sessions': 'Sessões Mês (Volume)', 'aht': 'AHT Atual (seg)', 'rate': 'Blended Rate ($/h)', 'hours': 'Horas / Semana', 'inf': 'Dissídio Anual (%)',
        'serv_cap': 'Serviços & CapEx', 'impl_mo': 'Meses Implantação', 'setup_cost': 'Custo Setup ($)', 'setup_margin': 'Margem Setup (%)', 'maint_cost': 'Maint. Interna/Mês ($)', 'maint_margin': 'Margem Maint (%)',
        'ai_eff': 'Eficiência AI', 'cont': 'Containment Alvo (%)', 'aht_over': 'Penalidade Transbordo (%)', 'copilot': 'Ativar Copilot', 'copilot_red': 'Redução Copilot (%)', 'copilot_cost': 'Licença Assist ($/FTE)',
        'token': 'Roteamento Semântico (LLMs)', 'in_tok': 'In Tokens/Sessão', 'out_tok': 'Out Tokens/Sessão', 'cache': 'Cache Hit Rate (%)', 'v_base_sidebar': 'Vendor Oficial (Baseline)',
        't1_split': 'Tráfego Tier 1 (Modelos Rápidos) %', 't1_label': 'Tier 1 (Ex: Flash, Haiku)', 't2_label': 'Tier 2 (Ex: Pro, GPT-4o)',
        'cost_in_c': 'In Cached ($/1M)', 'cost_in_nc': 'In Non-Cached ($/1M)', 'cost_out': 'Output ($/1M)',
        'com_mod': 'Modelos Comerciais', 'markup_lab': 'Markup Labor (%)', 'markup_tech': 'Markup s/ Tech (%)', 'gain_share': 'Gain-Share (%)', 'out_price': 'Ticket SaaS ($)',
        'v_matrix': 'OpEx Matrix', 'strat': 'Estratégia de Negócio:',
        'ebitda': 'EBITDA BPO (3A)', 'margin': 'Margem Operacional', 'sav': 'Net Savings Cliente (3A)', 'vs_leg': 'vs Legado', 'cash': 'Fluxo de Caixa',
        'chart_title': 'Comparativo de EBITDA Acumulado', 'dre_res': 'DRE Resumida', 'rev': 'Faturamento Total', 'cost': 'Custos Totais', 'profit': 'EBITDA', 'cli_sav': 'Savings Cliente',
        'cockpit_title': 'Cockpit Financeiro Executivo', 'sel_cenario': 'Selecione o cenário:', 'waterfall_title': 'Composição do EBITDA (Waterfall)', 'op_labor': 'Custos Laborais', 'op_tech': 'Custos Nuvem/Tech',
        'dre_full': 'Matriz DRE Analítica', 'down_xls': '📊 Baixar Planilha (XLSX)', 'down_pdf': '📄 Baixar Report (PDF)',
        'adv_title': 'GenAI Deal Advisor', 'adv_btn': '✨ Gerar Análise Arquitetural & Pitch', 'adv_warn': 'Gere a análise para obter os insights.'
    },
    'en': {
        'title': 'IA Agent Deal Desk (Beta)',
        'tab1': '1️⃣ Configuration (Setup)', 'tab2': '🔍 Vendor Matrix', 'tab3': '🎯 Executive Approval', 'tab4': '🧮 P&L Cockpit', 'tab5': '🤖 GenAI Advisor',
        'op_vol': 'Operation & Volume', 'sessions': 'Monthly Sessions', 'aht': 'Current AHT (sec)', 'rate': 'Blended Rate ($/h)', 'hours': 'Hours / Week', 'inf': 'Wage Inflation (%)',
        'serv_cap': 'Services & CapEx', 'impl_mo': 'Implementation Mo.', 'setup_cost': 'Setup Cost ($)', 'setup_margin': 'Setup Margin (%)', 'maint_cost': 'Maint. Cost/Mo ($)', 'maint_margin': 'Maint Margin (%)',
        'ai_eff': 'AI Efficiency', 'cont': 'Target Containment (%)', 'aht_over': 'Overflow Penalty (%)', 'copilot': 'Enable Copilot', 'copilot_red': 'Copilot Reduction (%)', 'copilot_cost': 'Assist License ($/FTE)',
        'token': 'Semantic Routing (LLMs)', 'in_tok': 'In Tokens/Session', 'out_tok': 'Out Tokens/Session', 'cache': 'Cache Hit Rate (%)', 'v_base_sidebar': 'Official Vendor (Baseline)',
        't1_split': 'Tier 1 Traffic (Fast Models) %', 't1_label': 'Tier 1 (e.g. Flash, Haiku)', 't2_label': 'Tier 2 (e.g. Pro, GPT-4o)',
        'cost_in_c': 'In Cached ($/1M)', 'cost_in_nc': 'In Non-Cached ($/1M)', 'cost_out': 'Output ($/1M)',
        'com_mod': 'Commercial Models', 'markup_lab': 'Labor Markup (%)', 'markup_tech': 'Tech Markup (%)', 'gain_share': 'Gain-Share (%)', 'out_price': 'SaaS Ticket ($)',
        'v_matrix': 'OpEx Matrix', 'strat': 'Business Strategy:',
        'ebitda': 'BPO EBITDA (3Y)', 'margin': 'Operating Margin', 'sav': 'Client Net Savings (3Y)', 'vs_leg': 'vs Legacy', 'cash': 'Cash Flow',
        'chart_title': 'Cumulative EBITDA Comparison', 'dre_res': 'Summarized P&L', 'rev': 'Total Revenue', 'cost': 'Total Costs', 'profit': 'EBITDA', 'cli_sav': 'Client Savings',
        'cockpit_title': 'Executive Financial Cockpit', 'sel_cenario': 'Select scenario:', 'waterfall_title': 'EBITDA Composition (Waterfall)', 'op_labor': 'Labor Costs', 'op_tech': 'Cloud/Tech Costs',
        'dre_full': 'Analytical P&L Matrix', 'down_xls': '📊 Download Spreadsheet', 'down_pdf': '📄 Download Report',
        'adv_title': 'GenAI Deal Advisor', 'adv_btn': '✨ Generate Architectural Analysis & Pitch', 'adv_warn': 'Generate the analysis to get insights.'
    }
}
def t(key): return DIC[st.session_state.lang].get(key, key)

# CSS Material Design
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
    </style>
""", unsafe_allow_html=True)

# SIDEBAR (Global Vendor Selection)
with st.sidebar:
    st.markdown(f"### ⚙️ {t('v_base_sidebar')}")
    vendor_global = st.selectbox("", ["Kore.AI", "Omilia", "Cresta"], label_visibility="collapsed", key="v_glob")

col_title, col_us, col_br = st.columns([10, 1, 1])
with col_title: st.markdown(f"<h2 style='color: #202124; margin-bottom: 24px;'>{t('title')}</h2>", unsafe_allow_html=True)
with col_us: 
    if st.button("🇺🇸", key="btn_us"): st.session_state.lang = 'en'; st.rerun()
with col_br: 
    if st.button("🇧🇷", key="btn_br"): st.session_state.lang = 'pt'; st.rerun()

# ==========================================
# MÓDULO 1: MOTORES DE CÁLCULO CORE
# ==========================================
def get_llm_cost_per_session(p):
    c_t1 = (((p["input_tokens"] * p["cache_hit_rate"]) / 1e6 * p["t1_in_c"]) +
            ((p["input_tokens"] * (1.0 - p["cache_hit_rate"])) / 1e6 * p["t1_in_nc"]) +
            (p["output_tokens"] / 1e6 * p["t1_out"]))
    c_t2 = (((p["input_tokens"] * p["cache_hit_rate"]) / 1e6 * p["t2_in_c"]) +
            ((p["input_tokens"] * (1.0 - p["cache_hit_rate"])) / 1e6 * p["t2_in_nc"]) +
            (p["output_tokens"] / 1e6 * p["t2_out"]))
    return (p["t1_split"] * c_t1) + ((1.0 - p["t1_split"]) * c_t2)

def get_platform_monthly_cost(p, monthly_ai_sessions):
    if p["vendor"] == "Kore.AI": return (monthly_ai_sessions * p["kore_session"]) + (p["kore_support_3y"] / 36.0) + (p["kore_expert_1y"] / 12.0)
    elif p["vendor"] == "Omilia": return (monthly_ai_sessions * p["omilia_session"]) + p["omilia_rag_month"] + ((monthly_ai_sessions * (p["omilia_chars_per_session"]/1e6)) * p["omilia_tts_1m"])
    elif p["vendor"] == "Cresta": return monthly_ai_sessions * p["cresta_ai_mins"] * p["cresta_per_min"]
    return 0.0

def get_payback(savings_acum_array):
    pos_idx = np.where(savings_acum_array > 0)[0]
    return int(pos_idx[0] + 1) if len(pos_idx) > 0 else 99

# ==========================================
# MÓDULO 2: ENGENHARIA DE VALOR (UI)
# ==========================================
tab_eng, tab_vendor, tab_dash, tab_dre, tab_advisor = st.tabs([t('tab1'), t('tab2'), t('tab3'), t('tab4'), t('tab5')])

with tab_eng:
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        st.markdown(f"#### 💼 {t('op_vol')}")
        sessions_month = st.number_input(t('sessions'), 1, value=30000, step=1000, key="i_sess")
        aht_seconds = st.number_input(t('aht'), 1, value=750, step=10, key="i_aht")
        agent_cost_hr = st.number_input(t('rate'), 0.1, value=3.45, step=0.1, key="i_rate")
        productive_hours_week = st.number_input(t('hours'), 1.0, value=40.0, step=1.0, key="i_hrs")
        fte_inflation_rate = st.number_input(t('inf'), value=5.0, key="i_inf") / 100.0
        st.markdown(f"#### 🔧 {t('serv_cap')}")
        implementation_months = st.number_input(t('impl_mo'), 0, 36, value=6, key="i_impl")
        setup_cost_internal = st.number_input(t('setup_cost'), 0.0, value=35714.0, key="i_setup_c")
        setup_fee = setup_cost_internal * (1.0 + (st.number_input(t('setup_margin'), value=40.0, key="i_setup_m") / 100.0))
        maint_cost_internal = st.number_input(t('maint_cost'), 0.0, value=3385.0, key="i_maint_c")
        maint_fee_month = maint_cost_internal * (1.0 + (st.number_input(t('maint_margin'), value=47.7, key="i_maint_m")/100.0))
        
    with col_in2:
        st.markdown(f"#### 🤖 {t('ai_eff')}")
        containment_mean = st.slider(t('cont'), 0, 100, 35, key="i_cont") / 100.0
        aht_overflow_variation = st.slider(t('aht_over'), 0, 50, 15, key="i_aht_o") / 100.0
        use_agent_assist = st.toggle(t('copilot'), key="i_use_aa")
        agent_assist_reduction = st.slider(t('copilot_red'), 0, 50, 20, key="i_aa_red") / 100.0 if use_agent_assist else 0.0
        agent_assist_cost_fte = st.number_input(t('copilot_cost'), 0.0, value=40.0, key="i_aa_c") if use_agent_assist else 0.0
        
        st.markdown(f"#### 💰 {t('com_mod')}")
        bpo_markup = st.number_input(t('markup_lab'), value=30.0, key="i_mk_lab") / 100.0
        tech_markup = st.number_input(t('markup_tech'), value=10.0, key="i_mk_tch") / 100.0
        bpo_gain_share = st.number_input(t('gain_share'), value=40.0, key="i_gs") / 100.0
        outcome_price = st.number_input(t('out_price'), 0.01, value=1.20, key="i_out_p")

    with col_in3:
        st.markdown(f"#### ☁️ {t('token')} 2.0")
        input_tokens = st.number_input(t('in_tok'), 100, value=50000, key="i_in_t")
        output_tokens = st.number_input(t('out_tok'), 100, value=1000, key="i_out_t")
        cache_hit_rate = st.slider(t('cache'), 0, 100, 50, key="i_chr") / 100.0
        
        t1_split = st.slider(t('t1_split'), 0, 100, 70, key="i_t1_s") / 100.0
        
        c_llm1, c_llm2 = st.columns(2)
        with c_llm1:
            st.caption(f"**{t('t1_label')}**")
            t1_in_c = st.number_input("In Cache ($)", value=0.02, format="%.3f", key="i_t1_in_c")
            t1_in_nc = st.number_input("In Non-C ($)", value=0.08, format="%.3f", key="i_t1_in_nc")
            t1_out = st.number_input("Out ($)", value=0.30, format="%.3f", key="i_t1_out")
        with c_llm2:
            st.caption(f"**{t('t2_label')}**")
            t2_in_c = st.number_input("In Cache ($) ", value=1.25, format="%.3f", key="i_t2_in_c")
            t2_in_nc = st.number_input("In Non-C ($) ", value=2.50, format="%.3f", key="i_t2_in_nc")
            t2_out = st.number_input("Out ($) ", value=10.00, format="%.3f", key="i_t2_out")

    st.divider()
    v1, v2, v3 = st.columns(3)
    with v1:
        st.write("**Kore.AI**")
        kore_session = st.number_input("Session ($)", value=0.116, format="%.3f", key="i_k_s")
        kore_support_3y = st.number_input("Support 3Y ($)", value=28000.0, key="i_k_sup")
        kore_expert_1y = st.number_input("Expert 1Y ($)", value=7000.0, key="i_k_exp")
    with v2:
        st.write("**Omilia**")
        omilia_session = st.number_input("Call ($)", value=0.045, format="%.3f", key="i_o_s")
        omilia_rag_month = st.number_input("RAG/Mo ($)", value=750.0, key="i_o_rag")
        omilia_tts_1m = st.number_input("TTS/1M ($)", value=7.0, key="i_o_tts")
        omilia_chars_per_session = 3750
    with v3:
        st.write("**Cresta**")
        cresta_per_min = st.number_input("Min Price ($)", value=0.10, format="%.2f", key="i_c_pm")
        cresta_ai_mins = st.number_input("Mins/Session", value=5.0, key="i_c_am")

params = {
    "sessions_month": sessions_month, "aht_seconds": aht_seconds, "aht_std_dev": 50, "agent_cost_hr": agent_cost_hr,
    "fte_inflation_rate": fte_inflation_rate, "productive_hours_week": productive_hours_week,
    "containment_mean": containment_mean, "containment_std_dev": 0.05, "aht_overflow_variation": aht_overflow_variation,
    "agent_assist_reduction": agent_assist_reduction, "agent_assist_cost_fte": agent_assist_cost_fte,
    "implementation_months": implementation_months, "setup_cost_internal": setup_cost_internal, "setup_fee": setup_fee,
    "maint_cost_internal": maint_cost_internal, "maint_fee_month": maint_fee_month,
    "input_tokens": input_tokens, "output_tokens": output_tokens, "cache_hit_rate": cache_hit_rate,
    "t1_split": t1_split, "t1_in_c": t1_in_c, "t1_in_nc": t1_in_nc, "t1_out": t1_out,
    "t2_in_c": t2_in_c, "t2_in_nc": t2_in_nc, "t2_out": t2_out,
    "bpo_markup": bpo_markup, "tech_markup": tech_markup, "bpo_gain_share": bpo_gain_share, "outcome_price": outcome_price,
    "vendor": vendor_global, "kore_session": kore_session, "kore_support_3y": kore_support_3y, "kore_expert_1y": kore_expert_1y,
    "omilia_session": omilia_session, "omilia_rag_month": omilia_rag_month, "omilia_tts_1m": omilia_tts_1m, "omilia_chars_per_session": omilia_chars_per_session,
    "cresta_per_min": cresta_per_min, "cresta_ai_mins": cresta_ai_mins
}

# --- HASH CHECK PARA PREVENIR STALE DATA NO AI ADVISOR ---
current_state_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode('utf-8')).hexdigest()
if 'last_params_hash' not in st.session_state:
    st.session_state.last_params_hash = current_state_hash

if st.session_state.last_params_hash != current_state_hash:
    st.session_state.genai_pitch = None
    st.session_state.last_params_hash = current_state_hash

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
    with vcol1: st.markdown(f"<div class='g-card'><div class='g-label'>Kore.AI</div><div class='g-value'>${(plat_k + llm_mensal_bpo):,.2f}</div><div class='g-delta-neutral'>Platform: ${plat_k:,.0f} | LLM: ${llm_mensal_bpo:,.0f}</div></div>", unsafe_allow_html=True)
    with vcol2: st.markdown(f"<div class='g-card'><div class='g-label'>Omilia</div><div class='g-value'>${(plat_o + llm_mensal_bpo):,.2f}</div><div class='g-delta-neutral'>Platform: ${plat_o:,.0f} | LLM: ${llm_mensal_bpo:,.0f}</div></div>", unsafe_allow_html=True)
    with vcol3: st.markdown(f"<div class='g-card'><div class='g-label'>Cresta</div><div class='g-value'>${(plat_c + llm_mensal_bpo):,.2f}</div><div class='g-delta-neutral'>Platform: ${plat_c:,.0f} | LLM: ${llm_mensal_bpo:,.0f}</div></div>", unsafe_allow_html=True)

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
    p50_ftes = np.percentile((human_sessions * new_human_aht / 3600.0) / productive_hours_month, 50)
    p50_asis_mo = np.percentile(matriz_asis_labor, 50, axis=0)
    p50_tobe_mo = np.percentile(matriz_tobe_misto, 50, axis=0)
    
    llm_cps = get_llm_cost_per_session(p)
    plat_mo = get_platform_monthly_cost(p, p50_ai_sessions)
    llm_mo = p50_ai_sessions * llm_cps
    
    agent_assist_tech_mo = p50_ftes * p["agent_assist_cost_fte"]
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
    c2_cost_labor = c1_cost_labor; c2_cost_tech = c1_cost_tech
    
    c3_outcome_rev_mo = (p50_ai_sessions * p["outcome_price"]) * live_mask
    c3_bpo_rev_mo = (p50_tobe_mo * (1.0 + p["bpo_markup"])) + c3_outcome_rev_mo + (p["maint_fee_month"] * live_mask)
    c3_bpo_cost_mo = bpo_custo_labor_array + bpo_custo_maint_mo + bpo_custo_tech_mo
    c3_bpo_ebitda_mo = c3_bpo_rev_mo - c3_bpo_cost_mo
    c3_bpo_rev_total = np.sum(c3_bpo_rev_mo) + p["setup_fee"]
    c3_bpo_ebitda_total = np.sum(c3_bpo_ebitda_mo) + (p["setup_fee"] - p["setup_cost_internal"])
    c3_cliente_tco = c3_bpo_rev_mo + np.array([p["setup_fee"] if m == 1 else 0.0 for m in meses])
    c3_cliente_savings_acum = np.cumsum(faturamento_asis_cliente - c3_cliente_tco)
    c3_cost_labor = c1_cost_labor; c3_cost_tech = c1_cost_tech

    def agrupar_anos(array_mensal): return [np.sum(array_mensal[0:12]), np.sum(array_mensal[12:24]), np.sum(array_mensal[24:36])]
    def agrupar_anos_tech(array_mensal, setup): return [np.sum(array_mensal[0:12]) + setup, np.sum(array_mensal[12:24]), np.sum(array_mensal[24:36])]
    
    rev_legado = np.sum(faturamento_asis_cliente)
    ebitda_legado = rev_legado - np.sum(p50_asis_mo)
    labor_arr_total = bpo_custo_labor_array + bpo_custo_maint_mo
    
    return {
        "c1": {"rev": c1_bpo_rev_total, "ebitda": c1_bpo_ebitda_total, "sav": c1_cliente_savings_acum[-1], "payback": get_payback(c1_cliente_savings_acum), "labor": c1_cost_labor, "tech": c1_cost_tech, "rev_y": agrupar_anos(c1_bpo_rev_mo), "ebitda_y": agrupar_anos(c1_bpo_ebitda_mo), "sav_y": agrupar_anos(c1_monthly_savings), "tech_y": agrupar_anos_tech(bpo_custo_tech_mo, p["setup_cost_internal"]), "labor_y": agrupar_anos(labor_arr_total)},
        "c2": {"rev": c2_bpo_rev_total, "ebitda": c2_bpo_ebitda_total, "sav": c2_cliente_savings_acum[-1], "payback": get_payback(c2_cliente_savings_acum), "labor": c2_cost_labor, "tech": c2_cost_tech, "rev_y": agrupar_anos(c2_bpo_rev_mo), "ebitda_y": agrupar_anos(c2_bpo_ebitda_mo), "sav_y": agrupar_anos(faturamento_asis_cliente - c2_cliente_tco), "tech_y": agrupar_anos_tech(bpo_custo_tech_mo, p["setup_cost_internal"]), "labor_y": agrupar_anos(labor_arr_total)},
        "c3": {"rev": c3_bpo_rev_total, "ebitda": c3_bpo_ebitda_total, "sav": c3_cliente_savings_acum[-1], "payback": get_payback(c3_cliente_savings_acum), "labor": c3_cost_labor, "tech": c3_cost_tech, "rev_y": agrupar_anos(c3_bpo_rev_mo), "ebitda_y": agrupar_anos(c3_bpo_ebitda_mo), "sav_y": agrupar_anos(faturamento_asis_cliente - c3_cliente_tco), "tech_y": agrupar_anos_tech(bpo_custo_tech_mo, p["setup_cost_internal"]), "labor_y": agrupar_anos(labor_arr_total)},
        "legado": {"rev": rev_legado, "ebitda": ebitda_legado, "rev_y": agrupar_anos(faturamento_asis_cliente), "ebitda_y": agrupar_anos(faturamento_asis_cliente - p50_asis_mo)}
    }

sim = run_deal_desk_simulation(params)
def calc_margin(ebitda, rev): return (ebitda / rev) * 100.0 if rev > 0 else 0.0

# ==========================================
# MÓDULO 4: DASHBOARDS (MATERIAL DESIGN)
# ==========================================
with tab_dash:
    col_m, col_h = st.columns([1, 4])
    with col_m: cenario_ativo = st.radio(t('strat'), [t('leg'), t('c1'), t('c2'), t('c3')], key="rad_strat")
    
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
    drill_cenario = st.selectbox(t('sel_cenario'), ["C1 (Completo)", "C2 (Gain-Share)", "C3 (SaaS Ticket)"], key="sel_drill")
    k_drill = "c1" if "C1" in drill_cenario else "c2" if "C2" in drill_cenario else "c3"
    d_drill = sim[k_drill]
    
    cw1, cw2 = st.columns([1, 1.5])
    with cw1:
        st.markdown(f"**{t('waterfall_title')}**")
        fig_wf = go.Figure(go.Waterfall(
            name = "20", orientation = "v", measure = ["relative", "relative", "relative", "total"],
            x = [t('rev'), t('op_labor'), t('op_tech'), t('profit')],
            y = [d_drill['rev'], -d_drill['labor'], -d_drill['tech'], d_drill['ebitda']], textposition = "outside",
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
                return p.output(dest='S').encode('latin-1')
            st.download_button(t('down_pdf'), data=make_pdf(), file_name="P_L_Summary.pdf", mime="application/pdf", use_container_width=True)

# ==========================================
# MÓDULO 6: AI ADVISOR (GENAI)
# ==========================================
with tab_advisor:
    st.markdown(f"<h3 style='color:#202124;'>{t('adv_title')}</h3>", unsafe_allow_html=True)
    
    if st.button(t('adv_btn'), type="primary", key="btn_genai"):
        with st.spinner("🤖 Analisando arquitetura semântica e DRE..."):
            time.sleep(1.5) # Simula chamada de API LLM
            
            ai_vol = params['sessions_month'] * params['containment_mean']
            c_t2_only = (((params["input_tokens"] * params["cache_hit_rate"]) / 1e6 * params["t2_in_c"]) +
                         ((params["input_tokens"] * (1.0 - params["cache_hit_rate"])) / 1e6 * params["t2_in_nc"]) +
                         (params["output_tokens"] / 1e6 * params["t2_out"]))
            
            llm_mensal_100_t2 = ai_vol * c_t2_only
            llm_mensal_routed = ai_vol * get_llm_cost_per_session(params)
            economia_routing = (llm_mensal_100_t2 - llm_mensal_routed) * 36
            
            c3_eb = sim['c3']['ebitda']
            is_pt = st.session_state.lang == 'pt'
            
            # Tratamento visual do Mês 99 (Payback Frustrado)
            c3_payback = sim['c3']['payback']
            pb_text_pt = f"mês {c3_payback}" if c3_payback <= 36 else "nunca (ROI Negativo)"
            pb_text_en = f"month {c3_payback}" if c3_payback <= 36 else "never (Negative ROI)"
            payback_str = pb_text_pt if is_pt else pb_text_en
            
            pitch = f"""
            #### 📊 Diagnóstico Estratégico (GenAI Analysis)
            
            Analisei a DRE consolidada e a arquitetura de Tokenomics proposta.
            
            **1. Impacto do Roteamento Semântico (Semantic Routing):**
            Ao desviar {params['t1_split']*100:.0f}% das intenções mais simples para o modelo Tier 1, e reservar o Tier 2 apenas para {100 - params['t1_split']*100:.0f}% de casos complexos, a operação está **economizando ${economia_routing:,.0f}** em nuvem ao longo de 36 meses. Essa economia foi injetada diretamente na sua margem EBITDA.
            
            **2. Recomendação Comercial (Otimizada para EBITDA):**
            Sugiro empurrar o **Cenário 3 (Outcome-Based)** para o cliente. 
            Como dominamos a eficiência da nuvem via Roteamento Semântico e *Prompt Caching*, nosso custo de produção despencou. Cobrando ${params['outcome_price']:.2f} por ticket retido, o BPO garante um EBITDA projetado de **${c3_eb:,.0f}** (com payback do cliente no **{payback_str}**), enquanto o blinda de oscilações tecnológicas.
            
            **3. Pontos de Atenção (Gargalos):**
            """
            
            if params['implementation_months'] > 4:
                pitch += f"- **Atraso de ROI:** A Curva J está muito longa ({params['implementation_months']} meses). Tente fatiar o Go-Live para faturar *Outcomes* mais rápido.\n"
            if params['cache_hit_rate'] < 0.8:
                pitch += f"- **Vazamento de OpEx:** O Cache Hit Rate de {params['cache_hit_rate']*100:.0f}% está baixo para GenAI. Otimize os *System Prompts* para passar de 80%.\n"
            if c3_payback > 36:
                pitch += f"- **Alerta Comercial:** O payback não ocorre dentro da janela de 36 meses. O Setup está sufocando o business case.\n"
                
            st.session_state.genai_pitch = pitch
            
    if st.session_state.genai_pitch:
        st.markdown(f"<div class='g-pitch-box' style='background-color:#f1f8ff; border-left-color:#1a73e8;'>{st.session_state.genai_pitch}</div>", unsafe_allow_html=True)
    else:
        st.info(t('adv_warn'))