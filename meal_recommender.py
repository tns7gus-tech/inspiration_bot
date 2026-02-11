"""
Inspiration Bot - 토양체질 Meal Recommender
Uses Gemini AI to generate 8-constitution compliant dinner menus
"""
import re
from google import genai
from loguru import logger

from config import settings
from toyang_diet import get_diet_prompt_context
from meal_history import MealHistory


class MealRecommender:
    """
    토양체질 저녁 식단 추천 엔진
    Gemini AI를 활용하여 단백질+면역력 중심 5가지 요리를 난이도별로 추천
    """

    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = self._get_best_model()
        self.history = MealHistory()
        self.diet_context = get_diet_prompt_context()
        logger.info(f"🍽️ MealRecommender 초기화 완료 (모델: {self.model})")

    def _get_best_model(self) -> str:
        """사용 가능한 최신 flash 모델 자동 감지"""
        try:
            models = self.client.models.list()
            model_names = [m.name for m in models]

            priority_models = [
                'gemini-2.0-flash',
                'gemini-1.5-flash',
                'gemini-1.5-flash-latest',
                'gemini-2.0-flash-lite',
            ]

            for preferred in priority_models:
                for name in model_names:
                    clean_name = name.replace('models/', '')
                    if clean_name == preferred:
                        return clean_name

            for name in model_names:
                clean_name = name.replace('models/', '')
                if 'flash' in clean_name.lower() and 'exp' not in clean_name.lower():
                    return clean_name

        except Exception as e:
            logger.warning(f"모델 목록 조회 실패: {e}")

        return settings.gemini_model

    async def generate_dinner_menu(self) -> str:
        """
        토양체질 맞춤 저녁 식단 5가지를 생성합니다.

        Returns:
            포맷팅된 5가지 저녁 메뉴 추천 문자열
        """
        # 최근 추천 메뉴 (중복 방지)
        recent_meals = self.history.get_recent_meals()
        recent_context = ""
        if recent_meals:
            recent_context = (
                "\n**최근 추천된 메뉴 (중복 절대 금지):**\n"
                + "\n".join([f"- {m}" for m in recent_meals])
            )

        prompt = f"""당신은 8체질 의학에 정통한 영양 전문가이자 요리 연구가입니다.
아래 '토양체질 식생표'를 **절대적으로** 준수하여 저녁 식단을 추천하세요.

{self.diet_context}

{recent_context}

**목표:**
퇴근 후 배달음식 대신 직접 요리할 수 있는 건강한 저녁 메뉴 5가지를 추천하세요.
**단백질 + 면역력 강화**에 초점을 맞추고, 토양체질에 최적화된 식재료만 사용하세요.

**필수 규칙:**
1. 5가지 메뉴를 **난이도 순** (쉬운 것부터 어려운 것까지)으로 정렬
2. 토양체질 ✕✕(절대 금지) 식품은 어떤 메뉴에도 절대 포함하지 마세요
3. 토양체질 ✕(나쁨) 식품도 가급적 제외
4. ◎(매우 좋음)과 ○(좋음) 식품 위주로 구성
5. 각 메뉴는 서로 다른 주재료 사용
6. 실제로 맛있고 실용적인 레시피
7. 유튜브 영상은 검색 키워드 기반 유튜브 검색 URL 형식으로 제공
   예시: https://www.youtube.com/results?search_query=돼지고기+된장찌개+레시피

**응답 형식 (정확히 이 형식을 따라주세요):**

🍽️ *토양체질 저녁 식단 추천*

━━━━━━━━━━━━━━━

*1️⃣ [메뉴 이름]*
⭐ 난이도: ★☆☆☆☆

🥘 *재료:*
- 재료1 (양)
- 재료2 (양)
- ...

👨‍🍳 *만드는 방법:*
① 첫 번째 단계
② 두 번째 단계
③ ...

📺 *참고 영상:*
[메뉴이름 레시피](유튜브 검색 URL)

📊 *영양성분 (1인분 기준):*
- 칼로리: 000kcal
- 탄수화물: 00g | 단백질: 00g | 지방: 00g

⏱️ *소요 시간:* 00분

━━━━━━━━━━━━━━━

*2️⃣ [메뉴 이름]*
⭐ 난이도: ★★☆☆☆
... (같은 형식)

━━━━━━━━━━━━━━━

*3️⃣ [메뉴 이름]*
⭐ 난이도: ★★★☆☆
...

━━━━━━━━━━━━━━━

*4️⃣ [메뉴 이름]*
⭐ 난이도: ★★★★☆
...

━━━━━━━━━━━━━━━

*5️⃣ [메뉴 이름]*
⭐ 난이도: ★★★★★
...

━━━━━━━━━━━━━━━

💡 *오늘의 추천:* (5개 중 가장 추천하는 1개와 그 이유)

위 형식으로 5가지 메뉴를 생성해주세요."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            result = response.text.strip()

            # 메뉴 제목 추출하여 히스토리 저장
            try:
                titles = re.findall(
                    r'[1-5]️⃣\s*\[?([^\]\n*]+)\]?',
                    result
                )
                if not titles:
                    # 대체 패턴
                    titles = re.findall(
                        r'\*[1-5]️⃣\s*([^*\n]+)\*',
                        result
                    )
                if titles:
                    clean_titles = [
                        t.strip().strip('*').strip('[').strip(']')
                        for t in titles
                    ]
                    self.history.record_meals(clean_titles)
                    logger.info(f"🍽️ 메뉴 제목 추출: {clean_titles}")
            except Exception as h_e:
                logger.warning(f"메뉴 히스토리 저장 실패: {h_e}")

            logger.success("🍽️ 저녁 식단 추천 생성 완료")
            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ 식단 추천 생성 실패: {error_msg}")
            return (
                "⚠️ 식단 추천 생성 중 오류가 발생했습니다!\n\n"
                f"에러: {error_msg}\n\n"
                "잠시 후 다시 시도합니다."
            )


# Test
async def test_recommender():
    """테스트 함수"""
    recommender = MealRecommender()
    menu = await recommender.generate_dinner_menu()
    print(menu)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_recommender())
