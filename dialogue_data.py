merchant_dialogue = [
    # 0
    {
        "speaker": "상인",
        "text": "왜 왔는가? 나에게 요구할 것이 있나? 천천히 쉬다 가게. 시간은 많으니. 아, 자네에게는 아닐 수도 있겠군.",
        "choices": None,
        "effect": None,
        "next": 1
    },
    # 1
    {
        "speaker": "상인",
        "text": "필요한 것이 있는가? 말만 하게. 최대한 협력하겠네.",
        "choices": [
            {"text": "체력 회복", "next": 2},
            {"text": "탄약 게이지 회복", "next": 3},
            {"text": "나가기", "next": 4}
        ],
        "effect": None,
        "next": None
    },
    # 2
    {
        "speaker": "상인",
        "choices": None,
        "effect": {"type": "hp_recover", "amount": 50},
        "effect_messages": {
            "success": "좋아. 체력을 {gained} 회복해주지. (-{cost} 악의 정수)",
            "full": "이미 최상의 컨디션이군. 치료는 필요 없지.",
            "insufficient": "악의 정수가 부족하군. 거래는 성립되지 않는다. (부족: {need})"
        },
        "next": 1
    },
    # 3
    {
        "speaker": "상인",
        "choices": None,
        "effect": {"type": "ammo_recover", "amount": 50},
        "effect_messages": {
            "success": "보급 완료. 탄약 게이지 {gained} 회복. (-{cost} 악의 정수)",
            "full": "탄약은 이미 충분해 보이는군.",
            "insufficient": "악의 정수가 부족해. 이건 거래가 아니지. (부족: {need})"
        },
        "next": 1
    },
    # 4
    {
        "speaker": "상인",
        "text": "몸 다치지 말고, 조심하게나!",
        "choices": None,
        "effect": None,
        "next": None  # None == 대화 종료
    }
]

doctorNF_dialogue = [
    # 0
    {
        "speaker": "새친 연구원",
        "text": "다행히 제 시간에 늦지않고 왔네. 내가 게임에 필요한 기본적인 것들을 알려줄께. 좌클릭을 통해 대화를 넘겨봐.",
        "choices": None,
        "effect": None,
        "next": 1
    },
    # 1
    {
        "speaker": "새친 연구원",
        "text": "궁금한게 있어?",
        "choices": [
            {"text": "조작법", "next": 2},
            {"text": "공격", "next": 4},
            {"text": "체력", "next": 6},
            {"text": "적", "next": 8},
            {"text": "없습니다", "next": 10}
        ],
        "effect": None,
        "next": None
    },
    # 2
    {
        "speaker": "새친 연구원",
        "text": "기본적인 이동방법은 이미 알고있겠지. W, A, S, D를 통해 이동할 수 있어. 추가로, 여기서 Shift키까지 누르면 달리기도 가능하지. 하지만 주의해. 달리는 도중에 다시 무기를 쓰면, 강제로 걷는 상태로 변경될거야.",
        "choices": None,
        "effect": None,
        "next": 3
    },
    # 3
    {
        "speaker": "새친 연구원",
        "text": "Tab을 누르면 UI창을 열 수 있어. 간단히 너의 상태를 볼 수 있고, 상단의 버튼들을 눌러서 너가 들고 있는 무기들의 여러가지 정보를 알 수도 있지. 또한, 무기를 주으려면 Space키를 누르면 돼.",
        "choices": None,
        "effect": None,
        "next": 1
    },
    # 4
    {
        "speaker": "새친 연구원",
        "text": "좌/우클릭으로 무기를 발사할 수 있어. 하지만, 탄약 게이지를 소모하지. 탄약 게이지가 바닥나면, 너는 강제로 V키를 눌러서 근접 공격을 해야해. 근접 공격을 할시엔, 탄약 게이지 오브가 떨어지니 참고하라고.",
        "choices": None,
        "effect": None,
        "next": 5
    },
    # 5
    {
        "speaker": "새친 연구원",
        "text": "무기는 총 1등급부터 5등급까지 있어. 물론 등급이 올라갈수록 위력이 높아지겠지만, 소모되는 탄약 게이지량도 증가하겠지. 탄약 게이지를 얻는 방법은 상인에게 말을 걸거나, 적을 죽이면 오브가 나와.",
        "choices": None,
        "effect": None,
        "next": 1
    },
    # 6
    {
        "speaker": "새친 연구원",
        "text": "체력이 0이 되면 사망한다. 물론 발생해서는 안되는 일이지.",
        "choices": None,
        "effect": None,
        "next": 7
    },
    # 7
    {
        "speaker": "새친 연구원",
        "text": "체력을 회복하는 수단은 크게 두가지가 있어. 첫번째는, 적을 죽이면 체력 오브가 나오는데, 그것을 얻는 방법이야. 두번째는, 상인에게 말을 걸면 일정 체력을 회복할 수 있어.",
        "choices": None,
        "effect": None,
        "next": 1
    },
    # 8
    {
        "speaker": "새친 연구원",
        "text": "적의 등급은 1등급부터 10등급까지 있어. 등급이 높을수록 떨어뜨리는 오브의 양, 위력, 체력 등등이 증가하지. 또한, 10등급은 보스만 가지고 있는 등급이니 참고하는게 좋아. 그리고, 보스는 매 스테이지 나오니깐 주의하라고.",
        "choices": None,
        "effect": None,
        "next": 9
    },
    # 9
    {
        "speaker": "새친 연구원",
        "text": "등급에 따른 적을 처치하면 악의 정수라는 포인트를 얻는다. 너는 이 포인트를 상점에서 사용해서 상태를 회복하거나 무기들을 구매할 수 있지.",
        "choices": None,
        "effect": None,
        "next": 1
    },
    # 10
    {
        "speaker": "새친 연구원",
        "text": "모두 이해되었지? 나도 최선으로 도와줄테니 한번 가보자고.",
        "choices": None,
        "effect": None,
        "next": None
    }
]
