"""
Inspiration Bot - AI Idea Generator
Uses Google Gemini API to generate creative project ideas
Auto-detects latest available model
"""
import json
import random
import re
from difflib import SequenceMatcher

from google import genai
from google.genai import types
from loguru import logger

from config import settings
from idea_history import IdeaHistory
from idea_summary_store import IdeaSummaryStore


class IdeaGenerator:
    """
    Gemini AI를 사용한 창의적 프로젝트 아이디어 생성
    자동으로 최신 flash 모델 감지
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = self._get_best_model()
        self.history = IdeaHistory()
        self.summary_store = IdeaSummaryStore()
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
    
    async def generate_idea(self, idea_type: str = "mixed") -> str:
        """
        창의적인 프로젝트 아이디어 생성
        
        Args:
            idea_type: "mixed" (하드웨어+SW) or "software" (한국인 페인포인트 SW)

        Returns:
            포맷팅된 아이디어 문자열
        """
        # 최근 아이디어 목록 가져오기 (중복 방지용)
        recent_ideas = self.history.get_recent_titles()
        summary_context = self.summary_store.get_recent_context(limit=80)
        recent_context = ""
        if recent_ideas:
            recent_context = f"\n**제외할 이전 아이디어들 (중복 절대 금지):**\n" + "\n".join([f"- {t}" for t in recent_ideas])
        summary_file_context = ""
        if summary_context:
            summary_file_context = (
                "\n**기존 아이디어 요약 파일 내용 (유사/중복 절대 금지):**\n"
                f"{summary_context}\n"
            )
        
        if idea_type == "software":
            # SW 전용 (한국인 페인포인트)
            age_groups = ["20대", "30대"]
            target_age = random.choice(age_groups)
            
            prompt = f"""당신은 한국인의 실제 불편함을 해결하는 소프트웨어 서비스 기획 전문가입니다.

**타겟 유저:** {target_age} 한국인
{recent_context}
{summary_file_context}

**목표:**
하드웨어 없이 웹(Web) 또는 앱(App)만으로 2-3일 내 프로토타입 구현이 가능한 서비스를 기획하세요.
실제 한국 커뮤니티(DC, 펨코, 네이트판, 맘카페 등)에서 자주 호소하는 구체적인 '불편함(Pain Point)'을 해결해야 합니다.

**규칙:**
1. **100% 소프트웨어 아이디어** (하드웨어 필요 없음)
2. **한국 특화** (한국의 문화, 법규, 생활 습관 반영)
3. 수익화 가능성이나 유저 확보 전략 포함
4. 개발 난이도: 주말에 혼자서 MVP 개발 가능 수준
5. 기존 아이디어 요약 파일과 제목/핵심 해결 방식이 겹치면 안 됨
6. 이미 널리 알려진 기존 서비스(국내/해외 상용 서비스)를 단순 복제한 아이디어는 금지

**응답 형식:**

영감봇 (소프트웨어 ver.)
**프로젝트 이름:** "프로젝트명" ({target_age} 타겟)

**타겟의 불편함:**
(구체적인 상황 묘사와 실제 겪는 문제점)

**해결 솔루션:**
(웹/앱으로 어떻게 해결하는지)

**핵심 기능:**
1. 기능1
2. 기능2

**기술 스택:**
- 프론트엔드/모바일:
- 백엔드/DB:
- 주요 API/라이브러리:

**기대 효과:**
(사용자가 얻는 이득)

---
위 형식으로 아이디어를 생성해주세요."""

        else:
            # 기존 Mixed (하드웨어+SW)
            prompt = f"""당신은 개발자들에게 영감을 주는 창의적인 프로젝트 아이디어를 제안하는 전문가입니다.
{recent_context}
{summary_file_context}

재미있고 신박한 토이 프로젝트 아이디어를 하나 생성해주세요. (하드웨어, IoT, SW 결합 환영)

**규칙:**
1. 실현 가능하면서도 독특한 아이디어
2. IoT, 자동화, AI, 웹, 모바일, 하드웨어 등 다양한 분야 가능
3. 유머러스하거나 실용적인 동기 포함
4. **이전에 제안한 것과 겹치지 않는 새로운 주제**
5. 기존 아이디어 요약 파일과 겹치거나 핵심 메커니즘이 유사하면 안 됨
6. 이미 상용화/대중화된 서비스의 단순 모방은 금지

**응답 형식:**

영감봇 (Maker ver.)
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

        return await self._generate_with_novelty_checks(
            base_prompt=prompt,
            idea_type=idea_type,
            summary_context=summary_context,
        )

    def _normalize_text(self, value: str) -> str:
        cleaned = re.sub(r"\s+", "", value.lower())
        return re.sub(r"[^\w가-힣]", "", cleaned)

    def _extract_title(self, idea: str) -> str:
        match = re.search(r'\*\*프로젝트 이름:\*\*\s*"([^"]+)"', idea)
        if match:
            return match.group(1).strip()
        fallback = re.search(r"\*\*프로젝트 이름:\*\*\s*(.+)", idea)
        if fallback:
            return fallback.group(1).strip().strip('"')
        return ""

    def _extract_short_summary(self, idea: str) -> str:
        one_line = re.search(r"\*\*한 줄 설명:\*\*\s*(.+)", idea)
        if one_line:
            return one_line.group(1).strip()[:180]

        solution = re.search(
            r"\*\*해결 솔루션:\*\*\s*(.+?)(?:\n\s*\n|\n\*\*)",
            idea,
            flags=re.DOTALL,
        )
        if solution:
            text = " ".join(solution.group(1).split())
            return text[:180]

        lines = [ln.strip() for ln in idea.splitlines() if ln.strip()]
        if len(lines) > 3:
            return lines[3][:180]
        return idea[:180]

    def _is_too_similar(self, title: str, candidates: list[str]) -> bool:
        norm_title = self._normalize_text(title)
        if not norm_title:
            return False

        for existing in candidates:
            norm_existing = self._normalize_text(existing)
            if not norm_existing:
                continue
            if norm_title == norm_existing:
                return True
            ratio = SequenceMatcher(None, norm_title, norm_existing).ratio()
            if ratio >= 0.82:
                return True
        return False

    def _extract_json_object(self, text: str) -> dict:
        content = text.strip()
        block = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if block:
            content = block.group(0)
        return json.loads(content)

    def _validate_novelty_with_search(
        self,
        idea: str,
        title: str,
        summary_context: str,
    ) -> dict:
        """
        Gemini 검색 도구를 사용해 중복/기존 서비스 여부를 검증합니다.
        """
        validate_prompt = f"""아래 프로젝트 아이디어가 '새로운 아이디어'인지 엄격히 심사하세요.

검사 기준:
1) 기존 아이디어 요약 목록과 제목/핵심 해결 방식이 유사하면 탈락
2) 이미 국내외에서 널리 서비스 중인 제품/앱/웹과 본질적으로 같으면 탈락
3) 단순한 UI/기능 이름 바꾸기 수준도 탈락

기존 아이디어 요약 목록:
{summary_context if summary_context else "(비어 있음)"}

검사 대상 제목:
{title}

검사 대상 상세:
{idea}

반드시 아래 JSON 한 줄만 출력하세요:
{{"is_novel": true/false, "reason": "판정 이유", "similar_examples": ["유사 서비스1", "유사 서비스2"]}}"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=validate_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    tools=[
                        types.Tool(
                            google_search=types.GoogleSearch()
                        )
                    ],
                ),
            )
            parsed = self._extract_json_object(response.text or "")
            is_novel = bool(parsed.get("is_novel", False))
            reason = str(parsed.get("reason", "")).strip()
            examples = parsed.get("similar_examples", [])
            if not isinstance(examples, list):
                examples = []
            return {
                "is_novel": is_novel,
                "reason": reason or "검증 결과 사유 미제공",
                "similar_examples": [str(x) for x in examples][:5],
            }
        except Exception as e:
            # 검색 검증 실패 시, 발송 중단보다는 생성 흐름 유지
            logger.warning(f"검색 기반 신규성 검증 실패(폴백): {e}")
            return {
                "is_novel": True,
                "reason": "검색 검증 실패로 폴백 허용",
                "similar_examples": [],
            }

    async def _generate_with_novelty_checks(
        self,
        base_prompt: str,
        idea_type: str,
        summary_context: str,
        max_attempts: int = 4,
    ) -> str:
        rejected_reasons: list[str] = []

        try:
            for attempt in range(1, max_attempts + 1):
                retry_context = ""
                if rejected_reasons:
                    retry_context = (
                        "\n\n**이전 시도 탈락 사유 (반드시 회피):**\n"
                        + "\n".join([f"- {r}" for r in rejected_reasons[-5:]])
                    )

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=base_prompt + retry_context,
                    config=types.GenerateContentConfig(temperature=0.9),
                )
                idea = (response.text or "").strip()
                title = self._extract_title(idea)

                if not title:
                    rejected_reasons.append("프로젝트 이름 추출 실패")
                    logger.warning(f"아이디어 재시도 {attempt}/{max_attempts}: 제목 추출 실패")
                    continue

                # 1차: 로컬 유사도 검사
                history_titles = self.history.get_recent_titles(limit=120)
                summary_titles = self.summary_store.get_all_titles()
                title_pool = list(set(history_titles + summary_titles))
                if self._is_too_similar(title, title_pool):
                    rejected_reasons.append(f"기존 아이디어와 제목 유사: {title}")
                    logger.warning(f"아이디어 재시도 {attempt}/{max_attempts}: 제목 유사도 탈락")
                    continue

                # 2차: 검색 기반 신규성 검사
                novelty = self._validate_novelty_with_search(
                    idea=idea,
                    title=title,
                    summary_context=summary_context,
                )
                if not novelty["is_novel"]:
                    examples = ", ".join(novelty["similar_examples"]) if novelty["similar_examples"] else "없음"
                    reason = f"{novelty['reason']} (유사 예시: {examples})"
                    rejected_reasons.append(reason)
                    logger.warning(f"아이디어 재시도 {attempt}/{max_attempts}: 검색 검증 탈락 - {reason}")
                    continue

                # 통과: 히스토리 + 요약 파일 저장
                self.history.record_idea(title, idea_type)
                summary = self._extract_short_summary(idea)
                self.summary_store.append_summary(title, idea_type, summary)
                logger.success(f"💡 새로운 아이디어 생성 완료 ({idea_type})")
                return idea

            return (
                "⚠️ 오늘은 기존 아이디어와 겹치지 않는 새 아이디어를 확정하지 못했습니다.\n\n"
                "내일 다시 더 엄격한 기준으로 새로운 아이디어를 탐색해보겠습니다."
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ 아이디어 생성 실패: {error_msg}")

            if "404" in error_msg or "not found" in error_msg.lower():
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
