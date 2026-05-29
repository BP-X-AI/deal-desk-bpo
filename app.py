import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import time
import hashlib
import json
import math
from fpdf import FPDF

# Configuração de Página (Wide & Clean)
st.set_page_config(page_title="IA Deal Desk (Beta)", layout="wide", initial_sidebar_state="expanded")

# Inicialização de Estado
if 'lang' not in st.session_state: st.session_state.lang = 'pt'
if 'genai_pitch' not in st.session_state: st.session_state.genai_pitch = None
if 'genai_alerts' not in st.session_state: st.session_state.genai_alerts = None
if 'genai_impact' not in st.session_state: st.session_state.genai_impact = None

# Dicionário de Traduções (QA Fix: 100% Mapeado)
DIC = {
    'pt': {
        'title': 'Agentic Deal Desk',
        'tab1': '1️⃣ Key Drivers', 'tab2': '🔍 Vendor Matrix', 'tab3': '🎯 Radar Executivo', 'tab4': '🧮 DRE Cockpit', 'tab5': '🤖 GenAI Advisor',
        'v_base_sidebar': 'Estratégia de Vendor', 'adv_btn': '✨ Gerar Análise Executiva',
        'sel_kpi': 'Selecione o Cenário para Ver KPIs:', 'fin_cen': 'Cenário Financeiro:',
        'wf_comp': 'Composição (Waterfall)', 'mat_ana': 'Matriz Analítica (3 Anos)',
        'capex_eff': 'Eficiência CapEx', 'profit': 'EBITDA ($)', 'cli_sav': 'Savings Cliente ($)'
    },
    'en': {
        'title': 'Agentic Deal Desk',
        'tab1': '1️⃣ Key Drivers', 'tab2': '🔍 Vendor Matrix', 'tab3': '🎯 Executive Radar', 'tab4': '🧮 P&L Cockpit', 'tab5': '🤖 GenAI Advisor',
        'v_base_sidebar': 'Vendor Strategy', 'adv_btn': '✨ Generate Executive Analysis',
        'sel_kpi': 'Select Scenario to view KPIs:', 'fin_cen': 'Financial Scenario:',
        'wf_comp': 'Composition (Waterfall)', 'mat_ana': 'Analytical Matrix (3 Years)',
        'capex_eff': 'CapEx Efficiency', 'profit': 'EBITDA ($)', 'cli_sav': 'Client Savings ($)'
    }
}
def t(key): return DIC[st.session_state.lang].get(key, key)

# --- GOOGLE MATERIAL DESIGN CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Google Sans', sans-serif; }
    
    .g-card { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); transition: box-shadow 0.2s; margin-bottom: 16px;}
    .g-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .g-label { color: #5f6368; font-size: 0.85rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .g-value { color: #202124; font-size: 2.2rem; font-weight: 500; line-height: 1.1; }
    .g-sub { color: #5f6368; font-size: 0.9rem; margin-top: 8px; font-weight: 400;}
    
    .ai-impact { background: #e6f4ea; border-left: 4px solid #34a853; padding: 20px; border-radius: 8px; margin-bottom: 16px; color: #137333;}
    .ai-alert { background: #fef7e0; border-left: 4px solid #fbbc04; padding: 20px; border-radius: 8px; margin-bottom: 16px; color: #b06000;}
    .ai-pitch { background: #e8f0fe; border-left: 4px solid #1a73e8; padding: 20px; border-radius: 8px; margin-bottom: 16px; color: #174ea6; font-style: italic; font-size: 1.1rem;}
    
    .section-title { font-size: 1.2rem; color: #202124; font-weight: 500; margin-bottom: 16px; margin-top: 8px; border-bottom: 1px solid #e0e0e0; padding-bottom: 8px;}
    .sku-title { color: #1a73e8; font-size: 0.95rem; font-weight: 600; margin-top: 16px; margin-bottom: -15px; border-bottom: 1px solid #e8eaed; padding-bottom: 4px; }
    </style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown(f"### ⚙️ {t('v_base_sidebar')}")
    vendor_global = st.selectbox("", ["Kore.AI", "Omilia", "Cresta"], label_visibility="collapsed", key="v_glob")
    st.caption("Altera toda a matriz de custos instantaneamente." if st.session_state.lang == 'pt' else "Instantly changes the entire cost matrix.")

col_title, col_us, col_br = st.columns([10, 1, 1])
with col_title: st.markdown(f"<h2 style='color: #202124; margin-bottom: 24px; font-weight: 500;'>{t('title')}</h2>", unsafe_allow_html=True)
with col_us: 
    if st.button("🇺🇸", key="btn_us"): st.session_state.lang = 'en'; st.rerun()
with col_br: 
    if st.button("🇧🇷", key="btn_br"): st.session_state.lang = 'pt'; st.rerun()

# ==========================================
# MÓDULO 1 & 2: ENGINE & PROGRESSIVE DISCLOSURE
# ==========================================
tab_eng, tab_vendor, tab_dash, tab_dre, tab_advisor = st.tabs([t('tab1'), t('tab2'), t('tab3'), t('tab4'), t('tab5')])

with tab_eng:
    st.markdown("<div class='section-title'>🎯 Key Value Drivers</div>", unsafe_allow_html=True)
    
    c_kd1, c_kd2, c_kd3, c_kd4, c_kd5 = st.columns(5)
    sessions_month = c_kd1.number_input("Volume", 1, value=30000, step=1000, key="i_sess")
    aht_seconds = c_kd2.number_input("AHT (Seg/Sec)", 1, value=750, step=10, key="i_aht")
    containment_mean = c_kd3.slider("Contenção/Containment", 0, 100, 35, key="i_cont", format="%d%%") / 100.0
    agent_cost_hr = c_kd4.number_input("Blended Rate ($)", 0.1, value=3.45, step=0.1, key="i_rate")
    implementation_months = c_kd5.number_input("Go-Live (Meses/Mo)", 0, 36, value=6, key="i_impl")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("⚙️ Advanced Settings (Tokenomics, Markups & SKUs)", expanded=False):
        c_adv1, c_adv2, c_adv3 = st.columns(3)
        with c_adv1:
            st.markdown("**1. Setup & Maint. Internos**")
            setup_cost_internal = st.number_input("Custo Setup ($)", 0.0, value=35714.0, key="i_setup_c")
            setup_fee = setup_cost_internal * (1.0 + (st.number_input("Margem Setup (%)", value=40.0, key="i_setup_m") / 100.0))
            maint_cost_internal = st.number_input("Maint. Mês ($)", 0.0, value=3385.0, key="i_maint_c")
            maint_fee_month = maint_cost_internal * (1.0 + (st.number_input("Margem Maint (%)", value=47.7, key="i_maint_m")/100.0))
            productive_hours_week = st.number_input("Horas/Semana", 1.0, value=40.0, step=1.0, key="i_hrs")
            fte_inflation_rate = st.number_input("Dissídio (%)", value=5.0, key="i_inf") / 100.0
            
        with c_adv2:
            st.markdown("**2. Modelos Comerciais & AI Ops**")
            bpo_markup = st.number_input("Markup Labor (%)", value=30.0, key="i_mk_lab") / 100.0
            tech_markup = st.number_input("Markup Tech (%)", value=10.0, key="i_mk_tch") / 100.0
            bpo_gain_share = st.number_input("Gain-Share (%)", value=40.0, key="i_gs") / 100.0
            outcome_price = st.number_input("Ticket SaaS ($)", 0.01, value=1.20, key="i_out_p")
            aht_overflow_variation = st.number_input("Penalidade Transbordo (%)", value=15.0, key="i_aht_o") / 100.0
            use_agent_assist = st.toggle("Ativar Copilot", key="i_use_aa")
            agent_assist_reduction = st.number_input("Redução Copilot (%)", value=20.0, key="i_aa_red") / 100.0 if use_agent_assist else 0.0
            agent_assist_cost_fte = st.number_input("Licença Assist ($/FTE)", value=40.0, key="i_aa_c") if use_agent_assist else 0.0

        with c_adv3:
            st.markdown("**3. Tokenomics & Routing**")
            input_tokens = st.number_input("In Tokens", 100, value=50000, key="i_in_t")
            output_tokens = st.number_input("Out Tokens", 100, value=1000, key="i_out_t")
            cache_hit_rate = st.number_input("Cache Hit (%)", value=50.0, key="i_chr") / 100.0
            t1_split = st.number_input("Trafego Tier 1 (%)", value=70.0, key="i_t1_s") / 100.0
            
            c_llm1, c_llm2 = st.columns(2)
            with c_llm1:
                st.caption("Tier 1 (Flash)")
                t1_in_c = st.number_input("In Cache ($)", value=0.02, format="%.3f", key="i_t1_in_c")
                t1_in_nc = st.number_input("In Non-C ($)", value=0.08, format="%.3f", key="i_t1_in_nc")
                t1_out = st.number_input("Out ($)", value=0.30, format="%.3f", key="i_t1_out")
            with c_llm2:
                st.caption("Tier 2 (Pro)")
                t2_in_c = st.number_input("In Cache ($)", value=1.25, format="%.3f", key="i_t2_in_c")
                t2_in_nc = st.number_input("In Non-C ($)", value=2.50, format="%.3f", key="i_t2_in_nc")
                t2_out = st.number_input("Out ($)", value=10.00, format="%.3f", key="i_t2_out")

        st.divider()
        st.markdown("**4. Vendor SKUs & Pricing**")
        v1, v2, v3 = st.columns(3)
        with v1:
            st.markdown("<div class='sku-title'>Kore.AI: AI for Services</div>", unsafe_allow_html=True)
            kx1, kx2 = st.columns(2)
            k_ses_val = kx1.number_input("Sessão ($)", value=0.116, format="%.3f", key="k_ses_v")
            k_ses_desc = kx2.number_input("Desc (%)", value=0.0, key="k_ses_d")
            st.markdown("<div class='sku-title'>Kore.AI: Gateway (TTS/ASR)</div>", unsafe_allow_html=True)
            kx3, kx4 = st.columns(2)
            k_gw_val = kx3.number_input("Gateway ($)", value=0.050, format="%.3f", key="k_gw_v")
            k_gw_desc = kx4.number_input("Desc (%)", value=0.0, key="k_gw_d")
            st.markdown("<div class='sku-title'>Kore.AI: Enterprise Support</div>", unsafe_allow_html=True)
            kx5, kx6 = st.columns(2)
            k_sup_val = kx5.number_input("Valor 3Y ($)", value=28000.0, key="k_sup_v")
            k_sup_desc = kx6.number_input("Desc (%)", value=0.0, key="k_sup_d")
            st.markdown("<div class='sku-title'>Kore.AI: Expert Services</div>", unsafe_allow_html=True)
            kx7, kx8 = st.columns(2)
            k_exp_val = kx7.number_input("Valor ($)", value=7000.0, key="k_exp_v")
            k_exp_desc = kx8.number_input("Desc (%)", value=0.0, key="k_exp_d")
        with v2:
            st.markdown("<div class='sku-title'>Omilia Layer</div>", unsafe_allow_html=True)
            omilia_session = st.number_input("Call ($)", value=0.045, format="%.3f", key="i_o_s")
            omilia_rag_month = st.number_input("RAG/Mo ($)", value=750.0, key="i_o_rag")
            omilia_tts_1m = st.number_input("TTS/1M ($)", value=7.0, key="i_o_tts")
            omilia_chars_per_session = 3750
        with v3:
            st.markdown("<div class='sku-title'>Cresta Usage</div>", unsafe_allow_html=True)
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
    "vendor": vendor_global, 
    "k_ses_val": k_ses_val, "k_ses_desc": k_ses_desc, "k_gw_val": k_gw_val, "k_gw_desc": k_gw_desc,
    "k_sup_val": k_sup_val, "k_sup_desc": k_sup_desc, "k_exp_val": k_exp_val, "k_exp_desc": k_exp_desc,
    "omilia_session": omilia_session, "omilia_rag_month": omilia_rag_month, "omilia_tts_1m": omilia_tts_1m, "omilia_chars_per_session": omilia_chars_per_session,
    "cresta_per_min": cresta_per_min, "cresta_ai_mins": cresta_ai_mins
}

current_state_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode('utf-8')).hexdigest()
if 'last_params_hash' not in st.session_state: st.session_state.last_params_hash = current_state_hash
if st.session_state.last_params_hash != current_state_hash:
    st.session_state.genai_pitch = None
    st.session_state.genai_impact = None
    st.session_state.genai_alerts = None
    st.session_state.last_params_hash = current_state_hash

def get_llm_cost_per_session(p):
    if p.get("vendor") != "Kore.AI": return 0.0
    c_t1 = (((p["input_tokens"] * p["cache_hit_rate"]) / 1e6 * p["t1_in_c"]) + ((p["input_tokens"] * (1.0 - p["cache_hit_rate"])) / 1e6 * p["t1_in_nc"]) + (p["output_tokens"] / 1e6 * p["t1_out"]))
    c_t2 = (((p["input_tokens"] * p["cache_hit_rate"]) / 1e6 * p["t2_in_c"]) + ((p["input_tokens"] * (1.0 - p["cache_hit_rate"])) / 1e6 * p["t2_in_nc"]) + (p["output_tokens"] / 1e6 * p["t2_out"]))
    return (p["t1_split"] * c_t1) + ((1.0 - p["t1_split"]) * c_t2)

def get_platform_monthly_cost(p, monthly_ai_sessions):
    if p["vendor"] == "Kore.AI": 
        sess_mult = math.ceil(p["aht_seconds"] / 900.0)
        return (monthly_ai_sessions * sess_mult * (p["k_ses_val"] * (1.0 - p["k_ses_desc"]/100.0))) + (monthly_ai_sessions * sess_mult * (p["k_gw_val"] * (1.0 - p["k_gw_desc"]/100.0))) + ((p["k_sup_val"] * (1.0 - p["k_sup_desc"]/100.0)) / 36.0)
    elif p["vendor"] == "Omilia": return (monthly_ai_sessions * p["omilia_session"]) + p["omilia_rag_month"] + ((monthly_ai_sessions * (p["omilia_chars_per_session"]/1e6)) * p["omilia_tts_1m"])
    elif p["vendor"] == "Cresta": return monthly_ai_sessions * p["cresta_ai_mins"] * p["cresta_per_min"]
    return 0.0

def get_platform_capex_cost(p): return p["k_exp_val"] * (1.0 - p["k_exp_desc"]/100.0) if p["vendor"] == "Kore.AI" else 0.0
def get_payback(savings_acum_array):
    pos_idx = np.where(savings_acum_array > 0)[0]
    return int(pos_idx[0] + 1) if len(pos_idx) > 0 else 99

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
    vendor_capex_cost = get_platform_capex_cost(p)
    
    llm_mo = p50_ai_sessions * llm_cps
    agent_assist_tech_mo = p50_ftes * p["agent_assist_cost_fte"]
    
    bpo_custo_tech_mo = np.array([plat_mo + llm_mo for m in meses]) + (agent_assist_tech_mo * live_mask)
    bpo_custo_labor_array = p50_tobe_mo
    bpo_custo_maint_mo = p["maint_cost_internal"] * live_mask
    
    faturamento_asis_cliente = p50_asis_mo * (1.0 + p["bpo_markup"])
    
    c1_faturamento_tech = bpo_custo_tech_mo * (1.0 + p["tech_markup"])
    c1_bpo_rev_mo = (p50_tobe_mo * (1.0 + p["bpo_markup"])) + (p["maint_fee_month"] * live_mask) + c1_faturamento_tech
    c1_bpo_cost_mo = bpo_custo_labor_array + bpo_custo_maint_mo + bpo_custo_tech_mo
    client_setup_bill_c1 = p["setup_fee"] + (vendor_capex_cost * (1.0 + p["tech_markup"]))
    bpo_setup_cost_total = p["setup_cost_internal"] + vendor_capex_cost
    
    c1_bpo_ebitda_mo = c1_bpo_rev_mo - c1_bpo_cost_mo
    c1_bpo_rev_total = np.sum(c1_bpo_rev_mo) + client_setup_bill_c1
    c1_bpo_ebitda_total = c1_bpo_rev_total - np.sum(c1_bpo_cost_mo) - bpo_setup_cost_total
    c1_cliente_tco = c1_bpo_rev_mo + np.array([client_setup_bill_c1 if m == 1 else 0.0 for m in meses])
    c1_monthly_savings = faturamento_asis_cliente - c1_cliente_tco
    c1_cliente_savings_acum = np.cumsum(c1_monthly_savings)
    c1_cost_labor = np.sum(bpo_custo_labor_array) + np.sum(bpo_custo_maint_mo)
    c1_cost_tech = np.sum(bpo_custo_tech_mo) + bpo_setup_cost_total
    
    c2_gain_share_rev = np.where((c1_cliente_savings_acum > 0) & (c1_monthly_savings > 0), c1_monthly_savings * p["bpo_gain_share"], 0.0)
    c2_cliente_tco = c1_cliente_tco + c2_gain_share_rev
    c2_cliente_savings_acum = np.cumsum(faturamento_asis_cliente - c2_cliente_tco)
    c2_bpo_rev_mo = c1_bpo_rev_mo + c2_gain_share_rev
    c2_bpo_ebitda_mo = c2_bpo_rev_mo - c1_bpo_cost_mo
    c2_bpo_rev_total = np.sum(c2_bpo_rev_mo) + client_setup_bill_c1
    c2_bpo_ebitda_total = c2_bpo_rev_total - np.sum(c1_bpo_cost_mo) - bpo_setup_cost_total
    c2_cost_labor = c1_cost_labor; c2_cost_tech = c1_cost_tech
    
    c3_outcome_rev_mo = (p50_ai_sessions * p["outcome_price"]) * live_mask
    c3_bpo_rev_mo = (p50_tobe_mo * (1.0 + p["bpo_markup"])) + c3_outcome_rev_mo + (p["maint_fee_month"] * live_mask)
    c3_bpo_cost_mo = bpo_custo_labor_array + bpo_custo_maint_mo + bpo_custo_tech_mo
    c3_bpo_ebitda_mo = c3_bpo_rev_mo - c3_bpo_cost_mo
    client_setup_bill_c3 = p["setup_fee"]
    c3_bpo_rev_total = np.sum(c3_bpo_rev_mo) + client_setup_bill_c3
    c3_bpo_ebitda_total = c3_bpo_rev_total - np.sum(c3_bpo_cost_mo) - bpo_setup_cost_total
    c3_cliente_tco = c3_bpo_rev_mo + np.array([client_setup_bill_c3 if m == 1 else 0.0 for m in meses])
    c3_cliente_savings_acum = np.cumsum(faturamento_asis_cliente - c3_cliente_tco)
    c3_cost_labor = c1_cost_labor; c3_cost_tech = c1_cost_tech

    def agrupar_anos(array_mensal): return [np.sum(array_mensal[0:12]), np.sum(array_mensal[12:24]), np.sum(array_mensal[24:36])]
    def agrupar_anos_tech(array_mensal, setup_bpo_total): return [np.sum(array_mensal[0:12]) + setup_bpo_total, np.sum(array_mensal[12:24]), np.sum(array_mensal[24:36])]
    
    rev_legado = np.sum(faturamento_asis_cliente)
    ebitda_legado = rev_legado - np.sum(p50_asis_mo)
    labor_arr_total = bpo_custo_labor_array + bpo_custo_maint_mo
    
    return {
        "c1": {"rev": c1_bpo_rev_total, "ebitda": c1_bpo_ebitda_total, "sav": c1_cliente_savings_acum[-1], "payback": get_payback(c1_cliente_savings_acum), "labor": c1_cost_labor, "tech": c1_cost_tech, "rev_y": agrupar_anos(c1_bpo_rev_mo), "ebitda_y": agrupar_anos(c1_bpo_ebitda_mo), "sav_y": agrupar_anos(c1_monthly_savings), "tech_y": agrupar_anos_tech(bpo_custo_tech_mo, bpo_setup_cost_total), "labor_y": agrupar_anos(labor_arr_total)},
        "c2": {"rev": c2_bpo_rev_total, "ebitda": c2_bpo_ebitda_total, "sav": c2_cliente_savings_acum[-1], "payback": get_payback(c2_cliente_savings_acum), "labor": c2_cost_labor, "tech": c2_cost_tech, "rev_y": agrupar_anos(c2_bpo_rev_mo), "ebitda_y": agrupar_anos(c2_bpo_ebitda_mo), "sav_y": agrupar_anos(faturamento_asis_cliente - c2_cliente_tco), "tech_y": agrupar_anos_tech(bpo_custo_tech_mo, bpo_setup_cost_total), "labor_y": agrupar_anos(labor_arr_total)},
        "c3": {"rev": c3_bpo_rev_total, "ebitda": c3_bpo_ebitda_total, "sav": c3_cliente_savings_acum[-1], "payback": get_payback(c3_cliente_savings_acum), "labor": c3_cost_labor, "tech": c3_cost_tech, "rev_y": agrupar_anos(c3_bpo_rev_mo), "ebitda_y": agrupar_anos(c3_bpo_ebitda_mo), "sav_y": agrupar_anos(faturamento_asis_cliente - c3_cliente_tco), "tech_y": agrupar_anos_tech(bpo_custo_tech_mo, bpo_setup_cost_total), "labor_y": agrupar_anos(labor_arr_total)},
        "legado": {"rev": rev_legado, "ebitda": ebitda_legado, "rev_y": agrupar_anos(faturamento_asis_cliente), "ebitda_y": agrupar_anos(faturamento_asis_cliente - p50_asis_mo)}
    }

sim = run_deal_desk_simulation(params)
def calc_margin(ebitda, rev): return (ebitda / rev) * 100.0 if rev > 0 else 0.0

# ==========================================
# MÓDULO 3: VENDOR MATRIX
# ==========================================
with tab_vendor:
    st.markdown("<div class='section-title'>🔍 Benchmarking de OpEx (Tecnologia)</div>", unsafe_allow_html=True)
    ai_vol_target = sessions_month * containment_mean
    
    plat_k = get_platform_monthly_cost({**params, "vendor": "Kore.AI"}, ai_vol_target)
    plat_o = get_platform_monthly_cost({**params, "vendor": "Omilia"}, ai_vol_target)
    plat_c = get_platform_monthly_cost({**params, "vendor": "Cresta"}, ai_vol_target)
    llm_mensal_k = ai_vol_target * get_llm_cost_per_session({**params, "vendor": "Kore.AI"})
    
    vcol1, vcol2, vcol3 = st.columns(3)
    with vcol1: st.markdown(f"<div class='g-card'><div class='g-label'>Kore.AI</div><div class='g-value'>${(plat_k + llm_mensal_k):,.2f}</div><div class='g-sub'>Plataforma: ${plat_k:,.0f} | LLM: ${llm_mensal_k:,.0f}</div></div>", unsafe_allow_html=True)
    with vcol2: st.markdown(f"<div class='g-card'><div class='g-label'>Omilia</div><div class='g-value'>${plat_o:,.2f}</div><div class='g-sub'>Plataforma: ${plat_o:,.0f} | LLM: $0</div></div>", unsafe_allow_html=True)
    with vcol3: st.markdown(f"<div class='g-card'><div class='g-label'>Cresta</div><div class='g-value'>${plat_c:,.2f}</div><div class='g-sub'>Plataforma: ${plat_c:,.0f} | LLM: $0</div></div>", unsafe_allow_html=True)

# ==========================================
# MÓDULO 4: DASHBOARDS & RADAR CHART
# ==========================================
with tab_dash:
    st.markdown("<div class='section-title'>🎯 Radar Estratégico de Decisão</div>", unsafe_allow_html=True)
    
    # QA FIX: Normalização segura contra valores negativos no gráfico polar
    def norm(val, max_val): return max(0, (val / max_val * 100)) if max_val > 0 else 0
    
    max_ebitda = max(sim['c1']['ebitda'], sim['c2']['ebitda'], sim['c3']['ebitda'], 1)
    max_sav = max(sim['c1']['sav'], sim['c2']['sav'], sim['c3']['sav'], 1)
    custos = [sim['c1']['tech'], sim['c2']['tech'], sim['c3']['tech']]
    min_cost = min(custos); max_cost = max(custos)
    def eff(c): return 100 - ((c - min_cost) / (max_cost - min_cost) * 100) if max_cost > min_cost else 100

    col_radar, col_kpi = st.columns([1.2, 1])
    
    with col_radar:
        fig_radar = go.Figure()
        categorias = [t('profit'), t('cli_sav'), t('capex_eff')]
        
        fig_radar.add_trace(go.Scatterpolar(r=[norm(sim['c1']['ebitda'], max_ebitda), norm(sim['c1']['sav'], max_sav), eff(sim['c1']['tech'])], theta=categorias, fill='toself', name='C1', line_color='#34a853'))
        fig_radar.add_trace(go.Scatterpolar(r=[norm(sim['c2']['ebitda'], max_ebitda), norm(sim['c2']['sav'], max_sav), eff(sim['c2']['tech'])], theta=categorias, fill='toself', name='C2', line_color='#fbbc04'))
        fig_radar.add_trace(go.Scatterpolar(r=[norm(sim['c3']['ebitda'], max_ebitda), norm(sim['c3']['sav'], max_sav), eff(sim['c3']['tech'])], theta=categorias, fill='toself', name='C3', line_color='#1a73e8'))
        
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), showlegend=True, margin=dict(t=30, b=30, l=30, r=30), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Google Sans", color="#5f6368"))
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_kpi:
        cenario_ativo = st.selectbox(t('sel_kpi'), ["C1", "C2", "C3"], key="rad_strat")
        dados = sim['c1'] if "C1" in cenario_ativo else sim['c2'] if "C2" in cenario_ativo else sim['c3']
        m_ativa = calc_margin(dados['ebitda'], dados['rev'])
        m_legado = calc_margin(sim['legado']['ebitda'], sim['legado']['rev'])
        
        st.markdown(f"<div class='g-card'><div class='g-label'>EBITDA (3Y)</div><div class='g-value'>${dados['ebitda']:,.0f}</div><div class='g-sub'><b>{m_ativa:.1f}%</b> Margin</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='g-card'><div class='g-label'>Net Savings</div><div class='g-value'>${dados['sav']:,.0f}</div><div class='g-sub'>Payback: M <b>{dados['payback'] if dados['payback']<=36 else 'N/A'}</b></div></div>", unsafe_allow_html=True)

# ==========================================
# MÓDULO 5: DRE COCKPIT
# ==========================================
with tab_dre:
    st.markdown("<div class='section-title'>🧮 DRE Executiva Interativa</div>", unsafe_allow_html=True)
    drill_cenario = st.radio(t('fin_cen'), ["C1", "C2", "C3"], horizontal=True, key="sel_drill")
    d_drill = sim[drill_cenario.lower()]
    
    cw1, cw2 = st.columns([1, 1.2])
    with cw1:
        st.markdown(f"**{t('wf_comp')}**")
        fig_wf = go.Figure(go.Waterfall(
            orientation = "v", measure = ["relative", "relative", "relative", "total"],
            x = ['Rev', 'Labor', 'Tech', 'EBITDA'],
            y = [d_drill['rev'], -d_drill['labor'], -d_drill['tech'], d_drill['ebitda']],
            text = [f"${d_drill['rev']/1000:,.0f}k", f"(${d_drill['labor']/1000:,.0f}k)", f"(${d_drill['tech']/1000:,.0f}k)", f"${d_drill['ebitda']/1000:,.0f}k"], textposition = "outside",
            decreasing = {"marker":{"color":"#ea4335"}}, increasing = {"marker":{"color":"#34a853"}}, totals = {"marker":{"color":"#1a73e8"}},
            connector = {"line":{"color":"#e0e0e0"}}
        ))
        fig_wf.update_layout(height=380, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Google Sans"))
        fig_wf.update_yaxes(showgrid=True, gridcolor='#f1f3f4', zerolinecolor='#bdc1c6')
        st.plotly_chart(fig_wf, use_container_width=True)
        
    with cw2:
        st.markdown(f"**{t('mat_ana')}**")
        # QA FIX: Prevenção contra ZeroDivisionError se a receita (rev) for muito baixa ou zero.
        safe_rev = d_drill['rev'] if d_drill['rev'] > 0 else 1
        df_dre = pd.DataFrame({
            "Rubrica": ["Receita Total", "Custos Labor", "Custos Tech", "EBITDA Final", "Client Savings"],
            "Ano 1": [d_drill['rev_y'][0], -d_drill['labor_y'][0], -d_drill['tech_y'][0], d_drill['ebitda_y'][0], d_drill['sav_y'][0]],
            "Ano 2": [d_drill['rev_y'][1], -d_drill['labor_y'][1], -d_drill['tech_y'][1], d_drill['ebitda_y'][1], d_drill['sav_y'][1]],
            "Ano 3": [d_drill['rev_y'][2], -d_drill['labor_y'][2], -d_drill['tech_y'][2], d_drill['ebitda_y'][2], d_drill['sav_y'][2]],
            "Total": [d_drill['rev'], -d_drill['labor'], -d_drill['tech'], d_drill['ebitda'], d_drill['sav']],
            "Margem": [100, (d_drill['labor']/safe_rev)*100, (d_drill['tech']/safe_rev)*100, calc_margin(d_drill['ebitda'], safe_rev), 0]
        })
        
        st.dataframe(
            df_dre,
            column_config={
                "Rubrica": st.column_config.TextColumn("Rubrica", width="medium"),
                "Ano 1": st.column_config.NumberColumn("Y1", format="$ %d"),
                "Ano 2": st.column_config.NumberColumn("Y2", format="$ %d"),
                "Ano 3": st.column_config.NumberColumn("Y3", format="$ %d"),
                "Total": st.column_config.NumberColumn("Total", format="$ %d"),
                "Margem": st.column_config.ProgressColumn("% Receita", format="%d%%", min_value=0, max_value=100)
            }, hide_index=True, use_container_width=True
        )

# ==========================================
# MÓDULO 6: GENAI ADVISOR
# ==========================================
with tab_advisor:
    st.markdown("<div class='section-title'>🤖 GenAI Deal Advisor</div>", unsafe_allow_html=True)
    
    if st.button(t('adv_btn'), type="primary", key="btn_genai"):
        with st.status("🧠 Processing Deal Architecture...", expanded=True) as status:
            time.sleep(0.6)
            time.sleep(0.6)
            time.sleep(0.8)
            status.update(label="Análise Concluída!" if st.session_state.lang == 'pt' else "Analysis Complete!", state="complete", expanded=False)
            
        ai_vol = params['sessions_month'] * params['containment_mean']
        c3_eb = sim['c3']['ebitda']
        c3_payback = sim['c3']['payback']
        payback_str = f"Mês {c3_payback}" if c3_payback <= 36 else "Nunca (ROI Negativo)"
        
        if params['vendor'] == 'Kore.AI':
            c_t2_only = (((params["input_tokens"] * params["cache_hit_rate"]) / 1e6 * params["t2_in_c"]) + ((params["input_tokens"] * (1.0 - params["cache_hit_rate"])) / 1e6 * params["t2_in_nc"]) + (params["output_tokens"] / 1e6 * params["t2_out"]))
            llm_mensal_100_t2 = ai_vol * c_t2_only
            llm_mensal_routed = ai_vol * get_llm_cost_per_session({**params, "vendor": "Kore.AI"})
            economia_routing = (llm_mensal_100_t2 - llm_mensal_routed) * 36
            net_exp_cost = params["k_exp_val"] * (1.0 - params["k_exp_desc"] / 100.0)
            
            st.session_state.genai_impact = f"<b>Efeito Semantic Routing:</b> Desviar {params['t1_split']*100:.0f}% do tráfego para modelos rápidos gerou uma economia em nuvem de <b>${economia_routing:,.0f}</b> em 3 anos. O Setup de Expert Services consome <b>${net_exp_cost:,.0f}</b> no D0."
            st.session_state.genai_pitch = f"“Avançaremos com o modelo de Outcome-Based (C3). Cobrando ${params['outcome_price']:.2f} por ticket retido, garantimos um EBITDA interno de ${c3_eb:,.0f}, blindando o cliente de oscilações tecnológicas de GenAI. O payback dele ocorre no {payback_str}.”"
        else:
            st.session_state.genai_impact = f"<b>Previsibilidade Máxima:</b> Na arquitetura {params['vendor']}, os custos de LLM já estão blindados no licenciamento. A operação não sofre variação de faturamento de Tokenomics no OpEx."
            st.session_state.genai_pitch = f"“Apresentaremos o Cenário Outcome-Based (C3). A ${params['outcome_price']:.2f} por ticket, garantimos um EBITDA interno de ${c3_eb:,.0f}. O cliente recupera o investimento no {payback_str}.”"

        alerts = []
        if params['implementation_months'] > 4: alerts.append(f"Atraso de ROI: Curva J longa ({params['implementation_months']} meses). Fatie o Go-Live.")
        if params['cache_hit_rate'] < 0.8 and params['vendor'] == 'Kore.AI': alerts.append(f"Vazamento de OpEx: Cache de {params['cache_hit_rate']*100:.0f}% está baixo. Otimize os Prompts para >80%.")
        if c3_payback > 36: alerts.append("O payback do cliente estourou o contrato (>36m). O Setup Fee está sufocando o business case.")
        st.session_state.genai_alerts = "<br>".join([f"⚠️ {a}" for a in alerts]) if alerts else "✅ Deal perfeitamente equilibrado. Sem alertas operacionais."

    if st.session_state.genai_pitch:
        st.markdown(f"<div class='ai-impact'>{st.session_state.genai_impact}</div>", unsafe_allow_html=True)
        if "⚠️" in st.session_state.genai_alerts: st.markdown(f"<div class='ai-alert'>{st.session_state.genai_alerts}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai-pitch'><b>Pitch Sugerido:</b><br>{st.session_state.genai_pitch}</div>", unsafe_allow_html=True)
    else:
        st.info("💡 " + t('adv_warn'))