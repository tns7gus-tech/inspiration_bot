"""
토양체질 (Earth Yang Constitution) 식생표 데이터
8체질 의학 기반 음식 호불호 차트

등급:
  ◎ (best)   - 매우 좋은 식품
  ○ (good)   - 좋은 식품
  ✕ (bad)    - 나쁜 식품
  ✕✕ (worst) - 매우 나쁜 식품 (절대 금지)
"""

TOYANG_FOOD_CHART = {
    "동물성 단백질": {
        "best": [
            "돼지고기", "대부분의 바다생선", "굴", "새우", "조개류",
            "전복", "가리비", "꽃게", "대하", "가재",
            "문어", "잉어", "붉은살생선", "복어"
        ],
        "good": [
            "쇠고기", "생우유", "유제품", "메기", "자라",
            "우렁이", "민물새우", "향어", "가물치"
        ],
        "bad": [
            "흰조기", "계란노른자"
        ],
        "worst": [
            "닭고기", "오리고기", "개고기", "염소고기", "양고기"
        ]
    },
    "식물성 단백질": {
        "best": [],
        "good": [
            "두부", "콩", "땅콩", "호두", "잣",
            "들깨", "강낭콩"
        ],
        "bad": [
            "아몬드", "마른도토리"
        ],
        "worst": []
    },
    "탄수화물(곡류)": {
        "best": [
            "보리", "녹두"
        ],
        "good": [
            "쌀", "파스타", "묵"
        ],
        "bad": [
            "현미", "밀", "수제비", "수수", "율무", "옥수수", "누룽지"
        ],
        "worst": [
            "찹쌀", "찰옥수수"
        ]
    },
    "기름": {
        "best": [
            "라드유(돼지기름)"
        ],
        "good": [
            "콩기름", "버터"
        ],
        "bad": [],
        "worst": []
    },
    "뿌리채소": {
        "best": [],
        "good": [
            "무", "당근", "도라지", "감자", "도토리"
        ],
        "bad": [],
        "worst": [
            "양파", "마", "고구마", "생강", "연근"
        ]
    },
    "잎/줄기채소": {
        "best": [
            "청국장", "오이", "콩나물", "숙주나물", "미나리"
        ],
        "good": [
            "누런호박", "열무", "배추", "미역", "된장국",
            "고구마줄기", "다시마"
        ],
        "bad": [
            "시금치", "쑥갓", "매실", "아보카도", "부추",
            "가지", "고사리", "깻잎"
        ],
        "worst": [
            "고추", "마늘", "양배추", "생강", "파",
            "팽이버섯"
        ]
    },
    "양념류": {
        "best": [],
        "good": [
            "마늘", "설탕"
        ],
        "bad": [
            "겨자"
        ],
        "worst": [
            "고추가루", "후추", "카레", "계피", "생강"
        ]
    },
    "해조류": {
        "best": [],
        "good": [
            "김", "미역", "다시마"
        ],
        "bad": [],
        "worst": []
    },
    "과일": {
        "best": [
            "메론", "참외", "딸기", "석류"
        ],
        "good": [
            "바나나", "수박", "복숭아", "포도",
            "블루베리", "크랜베리"
        ],
        "bad": [
            "망고", "키위", "대추", "무화과",
            "노니", "단감", "홍시"
        ],
        "worst": [
            "사과", "귤", "오렌지", "자몽",
            "레몬", "유자", "한라봉", "다래"
        ]
    },
    "약재류": {
        "best": [
            "구기자", "영지버섯", "산수유", "참깨", "비타민B"
        ],
        "good": [
            "녹용", "오디", "포도즙"
        ],
        "bad": [
            "비타민C"
        ],
        "worst": [
            "산삼", "인삼", "홍삼", "꿀", "대추"
        ]
    },
    "음료": {
        "best": [
            "커피"
        ],
        "good": [
            "콤부차", "보리차", "율피차"
        ],
        "bad": [
            "모과차"
        ],
        "worst": [
            "인삼차", "꿀물", "미숫가루", "대추차", "홍삼차"
        ]
    }
}


def get_diet_prompt_context() -> str:
    """
    Gemini 프롬프트에 삽입할 토양체질 식이 가이드 텍스트를 생성합니다.
    """
    lines = []
    lines.append("## 토양체질 식생표 (8체질 의학 기반)")
    lines.append("")
    lines.append("아래 식품 분류에 따라 요리를 설계하세요.")
    lines.append("◎ (매우 좋음), ○ (좋음) 식품 위주로 요리를 구성하고,")
    lines.append("✕ (나쁨), ✕✕ (매우 나쁨) 식품은 절대 사용하지 마세요.")
    lines.append("")

    for category, ratings in TOYANG_FOOD_CHART.items():
        lines.append(f"### {category}")
        if ratings["best"]:
            lines.append(f"  ◎ 매우 좋음: {', '.join(ratings['best'])}")
        if ratings["good"]:
            lines.append(f"  ○ 좋음: {', '.join(ratings['good'])}")
        if ratings["bad"]:
            lines.append(f"  ✕ 나쁨 (사용 금지): {', '.join(ratings['bad'])}")
        if ratings["worst"]:
            lines.append(f"  ✕✕ 매우 나쁨 (절대 금지): {', '.join(ratings['worst'])}")
        lines.append("")

    lines.append("## 핵심 규칙")
    lines.append("1. 닭고기, 오리고기, 양고기 절대 사용 금지")
    lines.append("2. 고추가루, 후추, 카레, 생강, 양파 절대 사용 금지")
    lines.append("3. 돼지고기, 해산물(새우, 굴, 조개 등) 적극 활용")
    lines.append("4. 보리, 녹두 곡류 우선, 쌀도 가능")
    lines.append("5. 들기름/올리브유 대신 콩기름 또는 버터 사용")
    lines.append("6. 인삼, 홍삼, 꿀 절대 사용 금지")
    lines.append("7. 고추, 마늘, 파 등 매운 양념류 절대 사용 금지")
    lines.append("8. 청국장, 오이, 콩나물, 미나리 적극 활용")
    lines.append("")

    return "\n".join(lines)


def get_forbidden_foods() -> list:
    """절대 금지 식품(✕✕) 목록 반환 (검증용)"""
    forbidden = []
    for ratings in TOYANG_FOOD_CHART.values():
        forbidden.extend(ratings.get("worst", []))
    return forbidden


def get_recommended_foods() -> list:
    """추천 식품(◎ + ○) 목록 반환"""
    recommended = []
    for ratings in TOYANG_FOOD_CHART.values():
        recommended.extend(ratings.get("best", []))
        recommended.extend(ratings.get("good", []))
    return recommended
