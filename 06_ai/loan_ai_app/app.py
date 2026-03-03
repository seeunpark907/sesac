from dotenv import load_dotenv
import streamlit as st
from config import FINETUNED_MODEL, SYSTEM_PROMPT
from rag import search_context, build_context_string
from langchain_openai import CahtOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import re

load_dotenv()

# ------------------------------- 페이지 설정 -------------------------------
st.set_page_config(
    page_title="🏠전세자금대출 AI 상담사",
    page_icon="🏠",
    layout="centered"
)
st.title("🏠전세자금대출 AI 상담사")
st.caption(
    "국민은행 · 신한은행 · 하나은행 상품설명서 기반 |"
    f"파인튜닝 모델 '{FINETUNED_MODEL}')"

# -------------------------------- LangChain ChatOpenAI 모델 정의 -------------------------------
@st.cache_resource
def get_llm():
    return ChatOpenAI(
        model=FINETUNED_MODEL,
        temperature=0,
        streaming=True
    )

model = get_llm()

# -------------------------------- 세션 상태 초기화 -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []              # LangChain 메시지 객체 리스트 (모델 전달)
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []      # 화면 표시용 딕셔너리 리스트

# --------------------------- 사이드바: 사용자 프로필 입력 -------------------------------
with st.sidebar:
    st.header("🪪내 금융 프로필")
    st.caption("입력 시 더 정확한 진단이 가능합니다.")

    target_bank = st.selectbox(
        "희망 은행",
        ["선택 안 함", "국민은행", "신한은행", "하나은행", "비교해서 추천"]
    )

    loan_purpose = st.selectbox(
        "대출 목적",
        ["선택", "전세자금", "전세 연장", "보증기관 선택", "금리 유형 선택", "기타"]
    )

    annual_income = st.number_input(
        "연소득 (만원)", min_value=0, max_value=10_000, value=4_000, step=100
    )

    credit_score = st.number_input(
        "신용점수 (점)", min_value=0, max_value=10_000, value=4_000, step=100
    )

    existing_loan = st.number_input(
        "기존 월 상환액(만원)", min_value=0, max_value=10_000, value=0, step=10
    )

    target_amount = st.number_input(
        "전세금 / 희망 대출액(만원)", min_value=0, max_value=500_000, value=20_000, step=500
    )

    if st.button("프로필 기반 진단 시작", use_container_width=True):
        if annual_income > 0:
        # 프로필 문자열 생성 (사용자 입력값(input_data) 재정의)
        profile_lines = [
            f"-희망 은행: {target_bank if target_bank != '선택 안 함'else '미정'}",
            f"-대출 목적: {loan_purpose if loan_purpose != '선택' else '미정'}",
            f"-연소득: {annual_income:,}만원",
            f"-신용점수: {credit_score}점{'(미입력)' if credit_score == 0 else ''}",
            f"-전세금/희망 대출액: {f'{target_amount:},만원' if target_amount > 0 else '미정'}"
    ]

    input_data = "\n".join(profile_lines)