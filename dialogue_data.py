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
        "text": "회복이라. 간단한 치료를 해주지. (50hp 회복)",
        "choices": None,
        "effect": {"type": "hp_recover", "amount": 50},
        "next": 1
    },
    # 3
    {
        "speaker": "상인",
        "text": "총알이 부족하나? 여기 여분이 있네. (50탄약 게이지 회복)",
        "choices": None,
        "effect": {"type": "ammo_recover", "amount": 50},
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

dialogue_tree = {
    "doctorNF_npc": {
        1: {
            "speaker": "의사",
            "text": "왔나? 마침 잘 왔군. 대부분의 조작법을 알려주겠다. 원하는걸 말해봐.",
            "choices": [
                {"text": "이동", "next": 2},
                {"text": "공격", "next": 4},
                {"text": "체력", "next": 6},
                {"text": "탄약 게이지", "next": 8},
                {"text": "없습니다", "next": 10}
            ]
        },
        2: {
            "speaker": "의사",
            "text": "W, A, S, D 키를 사용해서 상하좌우로 이동할 수 있지.",
            "next": 3
        },
        3: {
            "speaker": "의사",
            "text": "장애물은 통과할 수 없고, 적과 닿으면 피해를 입을 수 있으니 주의하게.",
            "next": 1
        },
        4: {
            "speaker": "의사",
            "text": "좌클릭을 누르면 무기를 발사할 수 있어.",
            "next": 5
        },
        5: {
            "speaker": "의사",
            "text": "무기는 탄약을 소모하며, 무기에 따라 특성이 다르니 잘 활용하게.",
            "next": 1
        },
        6: {
            "speaker": "의사",
            "text": "HP가 0이 되면 죽는다. 간단하지.",
            "next": 7
        },
        7: {
            "speaker": "의사",
            "text": "HP는 회복 아이템이나 의사를 통해 회복할 수 있지.",
            "next": 1
        },
        8: {
            "speaker": "의사",
            "text": "탄약 게이지는 무기를 쓸 때 소모된다네.",
            "next": 9
        },
        9: {
            "speaker": "의사",
            "text": "회복 오브를 통해 보충할 수 있고, 무기마다 소비량이 다르지.",
            "next": 1
        },
        10: {
            "speaker": "의사",
            "text": "모두 조작법을 알고 있나? 그럼 되었다. 죽지만 마라.",
            "next": None
        }
    },
}