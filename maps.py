# maps.py

# MAP1 - 기존 배치
CURRENT_MAP_1 = {
    "obstacles": [
        {
            "filename": "Pond1.png",
            "x": 768.90,
            "y": 523.05,
            "scale": 1.0
        },
        {
            "filename": "Rock2.png",
            "x": 320.05,
            "y": 191.50,
            "scale": 0.2
        },
        {
            "filename": "Rock1.png",
            "x": 1278.15,
            "y": 237.25,
            "scale": 0.2
        },
        {
            "filename": "Rock1.png",
            "x": 1278.15,
            "y": 798.55,
            "scale": 0.2
        },
        {
            "filename": "Rock2.png",
            "x": 320.05,
            "y": 941.35,
            "scale": 0.2
        }
    ],
    "enemy_infos": [
        {"x": 621.05, "y": 198.07, "enemy_type": "enemy1"},
        {"x": 1111.45, "y": 237.25, "enemy_type": "enemy2"},
        {"x": 1513.25, "y": 457.20, "enemy_type": "enemy1"},
        {"x": 1513.25, "y": 645.50, "enemy_type": "enemy2"},
        {"x": 1178.65, "y": 1014.52, "enemy_type": "enemy1"},
        {"x": 598.72, "y": 991.75, "enemy_type": "enemy2"},
        {"x": 214.42, "y": 642.32, "enemy_type": "enemy1"},
        {"x": 214.42, "y": 429.20, "enemy_type": "enemy2"},
    ]
}


# -------------------------------
# MAP2 - 호수 양옆 + 중앙 Rock2
# -------------------------------

CURRENT_MAP_2 = {
    "obstacles": [
        {
            "filename": "FallenLog1.png",
            "x": 776,
            "y": 530,
            "scale": 0.2
        },
        {
            "filename": "Pond1.png",
            "x": 1200,
            "y": 350,
            "scale": 0.4
        },
        {
            "filename": "Rock2.png",
            "x": 200,
            "y": 700,
            "scale": 0.3
        },
        {
            "filename": "Tree1.png",
            "x": 200,
            "y": 100,
            "scale": 0.2
        },
        # {
        #     "filename": "Rock1.png",
        #     "x": 400,
        #     "y": 150,
        #     "scale": 0.2
        # },
        # {
        #     "filename": "Rock3.png",
        #     "x": 800,
        #     "y": 100,
        #     "scale": 0.1
        # },
        # {
        #     "filename": "Rock2.png",
        #     "x": 1100,
        #     "y": 150,
        #     "scale": 0.2
        # },
        # {
        #     "filename": "Rock1.png",
        #     "x": 300,
        #     "y": 800,
        #     "scale": 0.2
        # },
        # {
        #     "filename": "Rock3.png",
        #     "x": 900,
        #     "y": 850,
        #     "scale": 0.1
        # },
        # {
        #     "filename": "Rock2.png",
        #     "x": 1200,
        #     "y": 700,
        #     "scale": 0.2
        # }
    ],
    "enemy_infos": [
        {"x": 664.97, "y": 906.05, "enemy_type": "enemy1"},
        {"x": 505.20, "y": 658.97, "enemy_type": "enemy2"},
        {"x": 394.00, "y": 341.12, "enemy_type": "enemy1"},
        {"x": 188.95, "y": 289.22, "enemy_type": "enemy2"},
        {"x": 832.10, "y": 313.30, "enemy_type": "enemy1"},
        {"x": 1172.10, "y": 427.0, "enemy_type": "enemy2"},
        {"x": 1440.70, "y": 717.73, "enemy_type": "enemy1"},
        {"x": 1332.32, "y": 1007.25, "enemy_type": "enemy2"},
        {"x": 962.07, "y": 718.43, "enemy_type": "enemy1"},
    ]
}


CURRENT_MAP_3 = {
    "obstacles": [
        {
            "filename": "Pond1.png",
            "x": 600,
            "y": 100,
            "scale": 0.3
        },
        {
            "filename": "Rock1.png",
            "x": 308,
            "y": 219,
            "scale": 0.3
        },
        {
            "filename": "Rock1.png",
            "x": 1284,
            "y": 248,
            "scale": 0.3
        },
    ],
    "enemy_infos": [
        {"x": 185.65, "y": 108.50, "enemy_type": "enemy1"},
        {"x": 393.70, "y": 376.40, "enemy_type": "enemy2"},
        {"x": 829.20, "y": 119.80, "enemy_type": "enemy1"},
        {"x": 1171.10, "y": 364.00, "enemy_type": "enemy2"},
        {"x": 1399.20, "y": 141.70, "enemy_type": "enemy1"},
    ],
    "crop_rect": {
        "x_ratio": 1.0,
        "y_ratio": 0.4
    }
}
