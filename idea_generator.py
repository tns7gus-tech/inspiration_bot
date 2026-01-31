"""
Inspiration Bot - AI Idea Generator
Uses Google Gemini API to generate creative project ideas
Auto-detects latest available model
"""
from google import genai
from loguru import logger

from config import settings


class IdeaGenerator:
    """
    Gemini AI를 사용한 창의적 프로젝트 아이디어 생성
    자동으로 최신 flash 모델 감지
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = self._get_best_model()
        logger.info(f"💡 IdeaGenerator 초기화 완료 (모델: {self.model})")
    
    def _get_best_model(self) -> str:
        """
        사용 가능한 최신 flash 모델 자동 감지
        우선순위: gemini-2.0-flash > gemini-1.5-flash > 기타 flash
        """
        try:
            models = self.client.models.list()
            model_names = [m.name for m in models]
            
            # 우선순위 순으로 체크
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
                        logger.info(f"🔍 자동 감지된 최신 모델: {clean_name}")
                        return clean_name
            
            # 우선순위에 없으면 아무 flash 모델이나 사용
            for name in model_names:
                clean_name = name.replace('models/', '')
                if 'flash' in clean_name.lower() and 'exp' not in clean_name.lower():
                    logger.info(f"🔍 감지된 flash 모델: {clean_name}")
                    return clean_name
            
        except Exception as e:
            logger.warning(f"모델 목록 조회 실패: {e}")
        
        # 폴백: 설정된 모델 사용
        return settings.gemini_model
    
    def get_available_models_info(self) -> str:
        """사용 가능한 모델 목록 조회"""
        try:
            models = self.client.models.list()
            flash_models = []
            for m in models:
                if 'flash' in m.name.lower() or 'pro' in m.name.lower():
                    flash_models.append(m.name)
            return "\n".join(flash_models[:10])  # 상위 10개만
        except Exception as e:
            return f"조회 실패: {e}"
    
    async def generate_idea(self) -> str:
        """
        창의적인 프로젝트 아이디어 생성
        
        Returns:
            포맷팅된 아이디어 문자열
        """
        prompt = """당신은 개발자들에게 영감을 주는 창의적인 프로젝트 아이디어를 제안하는 전문가입니다.

재미있고 신박한 토이 프로젝트 아이디어를 하나 생성해주세요.

**규칙:**
1. 실현 가능하면서도 독특한 아이디어
2. IoT, 자동화, AI, 웹, 모바일, 하드웨어 등 다양한 분야 가능
3. 유머러스하거나 실용적인 동기 포함
4. 구체적인 기술 스택 제안
5. 현실적인 개발 시간 예상

**응답 형식 (정확히 이 형식만 사용):**

영감봇
**프로젝트 이름:** "프로젝트명"

**한 줄 설명:** 이 프로젝트가 무엇인지 한 문장으로 설명

**왜 이걸 만들어?** 재미있거나 공감가는 동기 설명

**어떻게 작동해?** 구체적인 작동 원리 설명 (2-4문장)

**기술 스택:**
- 기술1 (용도)
- 기술2 (용도)
- 기술3 (용도)

**예상 개발 시간:** N시간

---
아이디어를 생성해주세요."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            idea = response.text.strip()
            logger.success("💡 새로운 아이디어 생성 완료")
            return idea
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ 아이디어 생성 실패: {error_msg}")
            
            # 모델 에러시 최신 모델 추천
            if '404' in error_msg or 'not found' in error_msg.lower():
                # 최신 모델 조회
                best_model = self._get_best_model()
                return (
                    f"⚠️ 아이디어 생성 중 오류가 발생했습니다!\n\n"
                    f"에러: 404 NOT_FOUND\n"
                    f"현재 모델 '{self.model}'을(를) 찾을 수 없습니다.\n\n"
                    f"🔄 최신 모델 '{best_model}'(으)로 변경해주세요!\n\n"
                    f"📝 .env 파일 수정 필요:\n"
                    f"GEMINI_MODEL={best_model}"
                )
            
            return f"⚠️ 아이디어 생성 중 오류가 발생했습니다: {e}"


# Test
async def test_generator():
    """테스트 함수"""
    generator = IdeaGenerator()
    idea = await generator.generate_idea()
    print(idea)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_generator())
