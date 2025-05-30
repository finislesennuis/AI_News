import os
import streamlit as st
import requests
import google.generativeai as genai

# ✅ API 키 설정
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
genai.configure(api_key=GEMINI_API_KEY)

# ✅ 페이지 기본 설정
st.set_page_config(page_title="뉴스 요약 챗봇", page_icon="📰", layout="centered")
st.title("📰 Gemini 뉴스 요약 챗봇")
st.markdown("뉴스 키워드를 입력하면 네이버 뉴스에서 기사 10개를 가져와 Gemini로 요약합니다.")

# ✅ 검색어 입력
query = st.text_input("🔍 뉴스 검색 키워드", "총선")

# ✅ Gemini 요약 함수
def summarize_with_gemini(title, description):
    try:
        prompt = f"제목: {title}\n\n내용: {description}\n\n위 뉴스를 한국어로 세 문장으로 요약해 주세요."

        model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ 반드시 이 모델 사용
        response = model.generate_content([{"role": "user", "parts": [{"text": prompt}]}])

        if hasattr(response, "text") and response.text.strip():
            return response.text.strip()
        else:
            return "(⚠️ Gemini 응답이 비어 있습니다)"
    except Exception as e:
        return f"(❌ Gemini 호출 오류: {e})"


# ✅ 네이버 뉴스 검색
def fetch_naver_news(query):
    try:
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        params = {
            "query": query,
            "display": 10,
            "sort": "date"
        }
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
        items = res.json().get("items", [])
        return [{
            "title": item["title"].replace("<b>", "").replace("</b>", ""),
            "link": item["link"],
            "description": item["description"].replace("<b>", "").replace("</b>", "")
        } for item in items]
    except Exception as e:
        st.error(f"네이버 뉴스 오류: {e}")
        return []

# ✅ 버튼 실행
if st.button("📡 뉴스 검색 및 요약"):
    with st.spinner("뉴스 검색 중..."):
        articles = fetch_naver_news(query)
        if not articles:
            st.warning("검색 결과 없음")
        else:
            for i, article in enumerate(articles, 1):
                with st.expander(f"{i}. {article['title']}"):
                    st.markdown(f"[🔗 기사 링크]({article['link']})")
                    st.markdown("**🧠 Gemini 요약:**")
                    summary = summarize_with_gemini(article["title"], article["description"])
                    st.write(summary)
