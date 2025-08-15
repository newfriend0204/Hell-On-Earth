START_MAP = {
    "obstacles": [],
    "enemy_infos": [],# [{"x": 200, "y": 200, "enemy_type": "enemy27"}], # 적 스폰 테스트용
    "npc_infos": [
        {"x": 100, "y": 100, "npc_type": "doctorNF_npc"},
        {"x": 100, "y": 100, "npc_type": "scientist1_npc"}
    ],
    "crop_rect": {"x_ratio": 0.5, "y_ratio": 0.5}
}

END_MAP = {
    "obstacles": [],
    "enemy_infos": [],
    "crop_rect": {"x_ratio": 0.5, "y_ratio": 0.5}
}

BOSS_MAP_1 = {
    "obstacles": [],
    "enemy_infos": [{"x": 1080, "y": 810, "enemy_type": "boss1"}],
    "crop_rect": {"x_ratio": 2, "y_ratio": 2}
}

BOSS_MAP_2 = {
    "obstacles": [],
    "enemy_infos": [{"x": 1080, "y": 810, "enemy_type": "boss2"}],
    "crop_rect": {"x_ratio": 2, "y_ratio": 2}
}

BOSS_MAP_3 = {
    "obstacles": [],
    "enemy_infos": [{"x": 1080, "y": 810, "enemy_type": "enemy1"}],  # 디버그용
    "crop_rect": {"x_ratio": 2, "y_ratio": 2}
}

ACQUIRE_MAP_1 = {
    "obstacles": [],
    "enemy_infos": [],
    "crop_rect": {"x_ratio": 0.5, "y_ratio": 0.5}
}

ACQUIRE_MAP_2 = {
    "obstacles": [],
    "enemy_infos": [],
    "crop_rect": {"x_ratio": 0.5, "y_ratio": 0.5}
}

ACQUIRE_MAP_3 = {
    "obstacles": [],
    "enemy_infos": [],
    "crop_rect": {"x_ratio": 0.5, "y_ratio": 0.5}
}

S1_FIGHT_MAP_1 = {
    "obstacles": [
        {"filename": "Pond1.png", "x": 768.90, "y": 523.05, "scale": 1.0},
        {"filename": "Rock2.png", "x": 320.05, "y": 191.50, "scale": 0.2},
        {"filename": "Rock1.png", "x": 1278.15, "y": 237.25, "scale": 0.2},
        {"filename": "Rock1.png", "x": 1278.15, "y": 798.55, "scale": 0.2},
        {"filename": "Rock2.png", "x": 320.05, "y": 941.35, "scale": 0.2}
    ],
    "enemy_infos": [
        {"x": 621.05, "y": 198.07},
        {"x": 1111.45, "y": 237.25},
        {"x": 1513.25, "y": 457.20},
        {"x": 1513.25, "y": 645.50},
        {"x": 1178.65, "y": 1014.52},
        {"x": 598.72, "y": 991.75},
        {"x": 214.42, "y": 642.32},
        {"x": 214.42, "y": 429.20}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S1_FIGHT_MAP_2 = {
    "obstacles": [
        {"filename": "FallenLog2.png", "x": 233.51, "y": 157.60, "scale": 0.2},
        {"filename": "Tree1.png", "x": 907.00, "y": 175.11, "scale": 0.3},
        {"filename": "Pond1.png", "x": 717.00, "y": 542.85, "scale": 0.4},
        {"filename": "Rock1.png", "x": 263.93, "y": 542.85, "scale": 0.2},
        {"filename": "Rock2.png", "x": 1167.55, "y": 542.85, "scale": 0.2},
        {"filename": "FallenLog1.png", "x": 931.99, "y": 862.23, "scale": 0.2},
        {"filename": "Tree2.png", "x": 403.93, "y": 862.23, "scale": 0.3}
    ],
    "enemy_infos": [
        {"x": 498.15, "y": 262.66},
        {"x": 996.30, "y": 262.66},
        {"x": 253.51, "y": 682.90},
        {"x": 717.00, "y": 682.90},
        {"x": 1167.55, "y": 682.90},
        {"x": 537.15, "y": 962.23},
        {"x": 996.30, "y": 962.23}
    ],
    "crop_rect": {"x_ratio": 0.9, "y_ratio": 0.9}
}

S1_FIGHT_MAP_3 = {
    "obstacles": [
        {"filename": "FallenLog1.png", "x": 173.70, "y": 350.98, "scale": 0.2},
        {"filename": "Rock2.png", "x": 448.72, "y": 305.88, "scale": 0.2},
        {"filename": "Tree1.png", "x": 824.08, "y": 200.65, "scale": 0.3},
        {"filename": "Tree2.png", "x": 969.83, "y": 366.01, "scale": 0.3},
        {"filename": "Rock1.png", "x": 1346.18, "y": 290.85, "scale": 0.2}
    ],
    "enemy_infos": [
        {"x": 289.50, "y": 210.46},
        {"x": 593.48, "y": 150.33},
        {"x": 796.13, "y": 375.81},
        {"x": 1085.63, "y": 450.98},
        {"x": 1150.00, "y": 225.50},
        {"x": 400.00, "y": 500.00},
        {"x": 700.00, "y": 100.00},
        {"x": 1300.00, "y": 500.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 0.5}
}

S1_FIGHT_MAP_4 = {
    "obstacles": [
        {"filename": "Tree1.png", "x": 200.00, "y": 150.00, "scale": 0.25},
        {"filename": "Tree1.png", "x": 500.00, "y": 100.00, "scale": 0.20},
        {"filename": "Tree1.png", "x": 800.00, "y": 200.00, "scale": 0.30},
        {"filename": "Tree1.png", "x": 300.00, "y": 600.00, "scale": 0.25},
        {"filename": "Tree2.png", "x": 650.00, "y": 400.00, "scale": 0.20},
        {"filename": "Tree2.png", "x": 1000.00, "y": 300.00, "scale": 0.25},
        {"filename": "Tree2.png", "x": 900.00, "y": 650.00, "scale": 0.30},
        {"filename": "Tree2.png", "x": 400.00, "y": 750.00, "scale": 0.20}
    ],
    "enemy_infos": [
        {"x": 350.00, "y": 180.00},
        {"x": 600.00, "y": 250.00},
        {"x": 750.00, "y": 500.00},
        {"x": 800.00, "y": 700.00},
        {"x": 341.00, "y": 350.00},
        {"x": 144.00, "y": 295.00}
    ],
    "crop_rect": {"x_ratio": 0.7, "y_ratio": 0.7}
}

S1_FIGHT_MAP_5 = {
    "obstacles": [
        {"filename": "FallenLog2.png", "x": 134.68, "y": 181.77, "scale": 0.15},
        {"filename": "FallenLog2.png", "x": 404.07, "y": 100.94, "scale": 0.15},
        {"filename": "Rock1.png", "x": 583.63, "y": 131.53, "scale": 0.15},
        {"filename": "Tree1.png", "x": 179.58, "y": 404.72, "scale": 0.25},
        {"filename": "Pond1.png", "x": 583.63, "y": 455.31, "scale": 0.25}
    ],
    "enemy_infos": [
        {"x": 300.00, "y": 150.00},
        {"x": 500.00, "y": 300.00},
        {"x": 423.63, "y": 455.31},
        {"x": 200.00, "y": 500.00},
        {"x": 400.00, "y": 300.00}
    ],
    "crop_rect": {"x_ratio": 0.5, "y_ratio": 0.5}
}

S1_FIGHT_MAP_6 = {
    "obstacles": [
        {"filename": "Rock1.png", "x": 200.00, "y": 150.00, "scale": 0.15},
        {"filename": "Rock1.png", "x": 400.00, "y": 150.00, "scale": 0.15},
        {"filename": "Rock2.png", "x": 800.00, "y": 200.00, "scale": 0.20},
        {"filename": "Rock2.png", "x": 300.00, "y": 500.00, "scale": 0.15},
        {"filename": "Rock3.png", "x": 650.00, "y": 350.00, "scale": 0.15},
        {"filename": "Rock3.png", "x": 900.00, "y": 300.00, "scale": 0.20},
        {"filename": "Rock3.png", "x": 800.00, "y": 650.00, "scale": 0.20},
        {"filename": "Rock2.png", "x": 400.00, "y": 650.00, "scale": 0.15}
    ],
    "enemy_infos": [
        {"x": 300.00, "y": 250.00},
        {"x": 550.00, "y": 200.00},
        {"x": 750.00, "y": 500.00},
        {"x": 600.00, "y": 600.00},
        {"x": 500.00, "y": 400.00},
        {"x": 150.00, "y": 600.00},
        {"x": 950.00, "y": 150.00}
    ],
    "crop_rect": {"x_ratio": 0.7, "y_ratio": 0.7}
}

S1_FIGHT_MAP_7 = {
    "obstacles": [
        {"filename": "Pond1.png", "x": 300.00, "y": 200.00, "scale": 0.3},
        {"filename": "Pond2.png", "x": 1000.00, "y": 760.00, "scale": 0.3},
        {"filename": "FallenLog1.png", "x": 450.00, "y": 300.00, "scale": 0.15},
        {"filename": "FallenLog2.png", "x": 800.00, "y": 250.00, "scale": 0.15},
        {"filename": "Tree1.png", "x": 200.00, "y": 500.00, "scale": 0.2},
        {"filename": "Tree2.png", "x": 600.00, "y": 600.00, "scale": 0.25},
        {"filename": "Tree1.png", "x": 1000.00, "y": 200.00, "scale": 0.2},
        {"filename": "Tree2.png", "x": 400.00, "y": 800.00, "scale": 0.2},
        {"filename": "Tree1.png", "x": 850.00, "y": 750.00, "scale": 0.25},
        {"filename": "Rock1.png", "x": 700.00, "y": 400.00, "scale": 0.2},
        {"filename": "Rock2.png", "x": 300.00, "y": 700.00, "scale": 0.2},
        {"filename": "Rock3.png", "x": 1050.00, "y": 500.00, "scale": 0.2}
    ],
    "enemy_infos": [
        {"x": 300.00, "y": 450.00},
        {"x": 500.00, "y": 450.00},
        {"x": 750.00, "y": 650.00},
        {"x": 1100.00, "y": 150.00},
        {"x": 950.00, "y": 650.00},
        {"x": 500.00, "y": 750.00},
        {"x": 650.00, "y": 200.00},
        {"x": 850.00, "y": 400.00}
    ],
    "crop_rect": {"x_ratio": 0.8, "y_ratio": 0.8}
}

S1_FIGHT_MAP_8 = {
    "obstacles": [
        {"filename": "Pond1.png", "x": 560.00, "y": 900.00, "scale": 0.5},
        {"filename": "FallenLog1.png", "x": 180.00, "y": 250.00, "scale": 0.15},
        {"filename": "FallenLog2.png", "x": 800.00, "y": 300.00, "scale": 0.15},
        {"filename": "FallenLog1.png", "x": 300.00, "y": 1450.00, "scale": 0.15},
        {"filename": "FallenLog2.png", "x": 800.00, "y": 1550.00, "scale": 0.15},
        {"filename": "Tree1.png", "x": 400.00, "y": 500.00, "scale": 0.2},
        {"filename": "Tree2.png", "x": 750.00, "y": 600.00, "scale": 0.2},
        {"filename": "Tree1.png", "x": 200.00, "y": 1000.00, "scale": 0.2},
        {"filename": "Tree2.png", "x": 850.00, "y": 1100.00, "scale": 0.25},
        {"filename": "Tree1.png", "x": 400.00, "y": 1300.00, "scale": 0.2},
        {"filename": "Rock1.png", "x": 600.00, "y": 400.00, "scale": 0.2},
        {"filename": "Rock3.png", "x": 250.00, "y": 700.00, "scale": 0.2},
        {"filename": "Rock1.png", "x": 700.00, "y": 1250.00, "scale": 0.2},
        {"filename": "Rock2.png", "x": 850.00, "y": 1450.00, "scale": 0.2},
        {"filename": "Rock3.png", "x": 500.00, "y": 1600.00, "scale": 0.2}
    ],
    "enemy_infos": [
        {"x": 130.00, "y": 200.00},
        {"x": 830.00, "y": 200.00},
        {"x": 350.00, "y": 600.00},
        {"x": 750.00, "y": 500.00},
        {"x": 800.00, "y": 950.00},
        {"x": 250.00, "y": 1300.00},
        {"x": 850.00, "y": 1250.00},
        {"x": 800.00, "y": 1700.00}
    ],
    "crop_rect": {"x_ratio": 0.6, "y_ratio": 1.5}
}

S1_FIGHT_MAP_9 = {
    "obstacles": [
        {"filename": "Pond2.png",  "x": 768.00,  "y": 540.00, "scale": 0.80},
        {"filename": "Rock1.png",  "x": 1400.00, "y": 220.00, "scale": 0.22},
        {"filename": "Rock2.png",  "x": 140.00,  "y": 240.00, "scale": 0.22},
        {"filename": "Tree1.png",  "x": 1400.00, "y": 900.00, "scale": 0.26},
        {"filename": "Tree2.png",  "x": 140.00,  "y": 900.00, "scale": 0.26},
        {"filename": "Rock3.png",  "x": 1400.00, "y": 540.00, "scale": 0.20},
        {"filename": "Tree1.png",  "x": 140.00,  "y": 540.00, "scale": 0.24},
        {"filename": "FallenLog2.png", "x": 768.00, "y": 980.00, "scale": 0.18}
    ],
    "enemy_infos": [
        {"x": 300.00, "y": 220.00}, {"x": 1230.00, "y": 220.00},
        {"x": 1450.00, "y": 540.00}, {"x": 90.00,   "y": 540.00},
        {"x": 300.00, "y": 880.00}, {"x": 1230.00, "y": 880.00},
        {"x": 768.00, "y": 260.00}, {"x": 768.00,  "y": 820.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S1_FIGHT_MAP_10 = {
    "obstacles": [
        {"filename": "FallenLog2.png", "x": 320.00,  "y": 280.00, "scale": 0.20},
        {"filename": "FallenLog1.png", "x": 1210.00, "y": 780.00, "scale": 0.20},
        {"filename": "Rock3.png",      "x": 1300.00, "y": 240.00, "scale": 0.22},
        {"filename": "Tree1.png",      "x": 420.00,  "y": 900.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 120.00,  "y": 780.00, "scale": 0.24},
        {"filename": "Rock1.png",      "x": 760.00,  "y": 180.00, "scale": 0.20},
        {"filename": "Rock2.png",      "x": 760.00,  "y": 930.00, "scale": 0.20},
        {"filename": "Tree1.png",      "x": 1010.00, "y": 940.00, "scale": 0.24},
        {"filename": "Tree2.png",      "x": 250.00,  "y": 140.00, "scale": 0.24}
    ],
    "enemy_infos": [
        {"x": 290.00, "y": 600.00}, {"x": 1240.00,"y": 600.00},
        {"x": 560.00, "y": 320.00}, {"x": 980.00, "y": 320.00},
        {"x": 560.00, "y": 860.00}, {"x": 980.00, "y": 860.00},
        {"x": 760.00, "y": 520.00}, {"x": 760.00, "y": 760.00}
    ],
    "crop_rect": {"x_ratio": 0.9, "y_ratio": 0.9}
}

S1_FIGHT_MAP_11 = {
    "obstacles": [
        {"filename": "Pond1.png",  "x": 420.00,  "y": 540.00, "scale": 0.68},
        {"filename": "Pond2.png",  "x": 1120.00, "y": 540.00, "scale": 0.68},
        {"filename": "Rock1.png",  "x": 230.00,  "y": 240.00, "scale": 0.20},
        {"filename": "Rock2.png",  "x": 1310.00, "y": 820.00, "scale": 0.20},
        {"filename": "Tree1.png",  "x": 980.00,  "y": 740.00, "scale": 0.24},
        {"filename": "Tree2.png",  "x": 540.00,  "y": 340.00, "scale": 0.24},
        {"filename": "Rock3.png",  "x": 960.00,  "y": 360.00, "scale": 0.22},
        {"filename": "Rock2.png",  "x": 560.00,  "y": 760.00, "scale": 0.20}
    ],
    "enemy_infos": [
        {"x": 760.00, "y": 260.00}, {"x": 760.00, "y": 840.00},
        {"x": 1060.00,"y": 540.00}, {"x": 460.00, "y": 540.00},
        {"x": 300.00, "y": 740.00}, {"x": 1220.00,"y": 340.00},
        {"x": 760.00, "y": 540.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S1_FIGHT_MAP_12 = {
    "obstacles": [
        {"filename": "Tree1.png",      "x": 330.00,  "y": 320.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1200.00, "y": 320.00, "scale": 0.26},
        {"filename": "Tree1.png",      "x": 330.00,  "y": 820.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1200.00, "y": 820.00, "scale": 0.26},
        {"filename": "Rock1.png",      "x": 560.00,  "y": 400.00, "scale": 0.20},
        {"filename": "Rock2.png",      "x": 960.00,  "y": 680.00, "scale": 0.20},
        {"filename": "Rock3.png",      "x": 760.00,  "y": 860.00, "scale": 0.20},
        {"filename": "FallenLog2.png", "x": 760.00,  "y": 180.00, "scale": 0.18}
    ],
    "enemy_infos": [
        {"x": 540.00, "y": 360.00}, {"x": 980.00, "y": 360.00},
        {"x": 540.00, "y": 720.00}, {"x": 980.00, "y": 720.00},
        {"x": 760.00, "y": 540.00}, {"x": 300.00, "y": 540.00},
        {"x": 1220.00,"y": 540.00}
    ],
    "crop_rect": {"x_ratio": 0.8, "y_ratio": 0.8}
}

S1_FIGHT_MAP_13 = {
    "obstacles": [
        {"filename": "FallenLog2.png", "x": 340.00,  "y": 540.00, "scale": 0.20},
        {"filename": "FallenLog2.png", "x": 1180.00, "y": 540.00, "scale": 0.20},
        {"filename": "FallenLog1.png", "x": 760.00,  "y": 320.00, "scale": 0.20},
        {"filename": "FallenLog1.png", "x": 760.00,  "y": 820.00, "scale": 0.20},
        {"filename": "Rock1.png",      "x": 960.00,  "y": 420.00, "scale": 0.20},
        {"filename": "Rock2.png",      "x": 560.00,  "y": 420.00, "scale": 0.20},
        {"filename": "Rock3.png",      "x": 960.00,  "y": 660.00, "scale": 0.20},
        {"filename": "Tree2.png",      "x": 560.00,  "y": 700.00, "scale": 0.24}
    ],
    "enemy_infos": [
        {"x": 560.00, "y": 540.00}, {"x": 960.00, "y": 540.00},
        {"x": 760.00, "y": 380.00}, {"x": 760.00, "y": 700.00},
        {"x": 290.00, "y": 320.00}, {"x": 1240.00,"y": 820.00},
        {"x": 760.00, "y": 540.00}
    ],
    "crop_rect": {"x_ratio": 0.9, "y_ratio": 0.9}
}

S1_FIGHT_MAP_14 = {
    "obstacles": [
        {"filename": "Rock3.png",  "x": 320.00,  "y": 300.00, "scale": 0.24},
        {"filename": "Rock1.png",  "x": 1240.00, "y": 300.00, "scale": 0.22},
        {"filename": "Tree1.png",  "x": 320.00,  "y": 800.00, "scale": 0.25},
        {"filename": "Tree2.png",  "x": 1240.00, "y": 800.00, "scale": 0.25},
        {"filename": "Rock2.png",  "x": 760.00,  "y": 900.00, "scale": 0.20},
        {"filename": "Rock1.png",  "x": 760.00,  "y": 200.00, "scale": 0.20},
        {"filename": "Tree1.png",  "x": 520.00,  "y": 660.00, "scale": 0.24},
        {"filename": "Tree2.png",  "x": 1000.00, "y": 420.00, "scale": 0.24},
        {"filename": "FallenLog2.png","x": 150.00,  "y": 540.00, "scale": 0.18}
    ],
    "enemy_infos": [
        {"x": 760.00, "y": 260.00}, {"x": 760.00, "y": 840.00},
        {"x": 520.00, "y": 540.00}, {"x": 1000.00,"y": 540.00},
        {"x": 260.00, "y": 540.00}, {"x": 1260.00,"y": 540.00},
        {"x": 760.00, "y": 540.00}, {"x": 960.00, "y": 360.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S1_FIGHT_MAP_15 = {
    "obstacles": [
        {"filename": "Pond1.png",  "x": 960.00,  "y": 720.00, "scale": 0.62},
        {"filename": "Rock2.png",  "x": 1180.00, "y": 920.00, "scale": 0.22},
        {"filename": "Rock1.png",  "x": 380.00,  "y": 200.00, "scale": 0.22},
        {"filename": "Tree1.png",  "x": 300.00,  "y": 860.00, "scale": 0.24},
        {"filename": "Tree2.png",  "x": 1220.00, "y": 300.00, "scale": 0.24},
        {"filename": "Rock3.png",  "x": 560.00,  "y": 900.00, "scale": 0.20},
        {"filename": "Rock1.png",  "x": 1140.00, "y": 560.00, "scale": 0.20},
        {"filename": "Tree2.png",  "x": 760.00,  "y": 420.00, "scale": 0.24}
    ],
    "enemy_infos": [
        {"x": 290.00, "y": 560.00}, {"x": 1240.00,"y": 560.00},
        {"x": 560.00, "y": 340.00}, {"x": 980.00, "y": 340.00},
        {"x": 560.00, "y": 820.00}, {"x": 980.00, "y": 820.00},
        {"x": 760.00, "y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.85, "y_ratio": 1.0}
}

S1_FIGHT_MAP_16 = {
    "obstacles": [
        {"filename": "FallenLog1.png", "x": 260.00,  "y": 400.00, "scale": 0.20},
        {"filename": "FallenLog1.png", "x": 1260.00, "y": 680.00, "scale": 0.20},
        {"filename": "Tree2.png",      "x": 960.00,  "y": 260.00, "scale": 0.24},
        {"filename": "Rock3.png",      "x": 560.00,  "y": 840.00, "scale": 0.22},
        {"filename": "Tree1.png",      "x": 360.00,  "y": 720.00, "scale": 0.24},
        {"filename": "Rock1.png",      "x": 1060.00, "y": 420.00, "scale": 0.20},
        {"filename": "Rock2.png",      "x": 860.00,  "y": 760.00, "scale": 0.20},
        {"filename": "Tree2.png",      "x": 1260.00, "y": 260.00, "scale": 0.24},
        {"filename": "Rock1.png",      "x": 260.00,  "y": 880.00, "scale": 0.20}
    ],
    "enemy_infos": [
        {"x": 760.00, "y": 260.00}, {"x": 760.00, "y": 840.00},
        {"x": 560.00, "y": 540.00}, {"x": 960.00, "y": 540.00},
        {"x": 290.00, "y": 540.00}, {"x": 1240.00,"y": 540.00},
        {"x": 760.00, "y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.7, "y_ratio": 1.2}
}

S1_FIGHT_MAP_17 = {
    "obstacles": [
        {"filename": "Tree1.png",  "x": 300.00,  "y": 360.00, "scale": 0.24},
        {"filename": "Tree2.png",  "x": 1220.00, "y": 360.00, "scale": 0.24},
        {"filename": "Tree1.png",  "x": 300.00,  "y": 720.00, "scale": 0.24},
        {"filename": "Tree2.png",  "x": 1220.00, "y": 720.00, "scale": 0.24},
        {"filename": "Rock2.png",  "x": 760.00,  "y": 900.00, "scale": 0.20},
        {"filename": "Rock1.png",  "x": 960.00,  "y": 260.00, "scale": 0.20},
        {"filename": "Rock3.png",  "x": 960.00,  "y": 720.00, "scale": 0.20},
        {"filename": "Tree1.png",  "x": 560.00,  "y": 260.00, "scale": 0.24},
        {"filename": "Rock2.png",  "x": 300.00,  "y": 900.00, "scale": 0.20}
    ],
    "enemy_infos": [
        {"x": 520.00, "y": 540.00}, {"x": 1000.00,"y": 540.00},
        {"x": 760.00, "y": 360.00}, {"x": 760.00, "y": 720.00},
        {"x": 260.00, "y": 540.00}, {"x": 1260.00,"y": 540.00},
        {"x": 760.00, "y": 560.00}, {"x": 960.00, "y": 360.00}
    ],
    "crop_rect": {"x_ratio": 1.2, "y_ratio": 0.7}
}

S1_FIGHT_MAP_18 = {
    "obstacles": [
        {"filename": "Rock1.png",  "x": 520.00,  "y": 360.00, "scale": 0.22},
        {"filename": "Rock2.png",  "x": 1000.00, "y": 360.00, "scale": 0.22},
        {"filename": "Rock3.png",  "x": 760.00,  "y": 780.00, "scale": 0.22},
        {"filename": "Tree1.png",  "x": 300.00,  "y": 820.00, "scale": 0.24},
        {"filename": "Tree2.png",  "x": 1220.00, "y": 300.00, "scale": 0.24},
        {"filename": "Rock1.png",  "x": 300.00,  "y": 360.00, "scale": 0.20},
        {"filename": "Rock2.png",  "x": 1220.00, "y": 760.00, "scale": 0.20},
        {"filename": "Tree1.png",  "x": 760.00,  "y": 480.00, "scale": 0.24}
    ],
    "enemy_infos": [
        {"x": 300.00, "y": 300.00}, {"x": 1220.00,"y": 300.00},
        {"x": 300.00, "y": 780.00}, {"x": 1220.00,"y": 780.00},
        {"x": 760.00, "y": 540.00}, {"x": 560.00, "y": 540.00},
        {"x": 960.00, "y": 540.00}
    ],
    "crop_rect": {"x_ratio": 0.85, "y_ratio": 0.85}
}

S1_FIGHT_MAP_19 = {
    "obstacles": [
        {"filename": "Rock1.png",  "x": 520.00,  "y": 360.00, "scale": 0.24},
        {"filename": "Rock2.png",  "x": 1000.00, "y": 360.00, "scale": 0.24},
        {"filename": "Tree1.png",  "x": 520.00,  "y": 720.00, "scale": 0.26},
        {"filename": "Tree2.png",  "x": 1000.00, "y": 720.00, "scale": 0.26},
        {"filename": "Rock3.png",  "x": 760.00,  "y": 220.00, "scale": 0.20},
        {"filename": "Rock2.png",  "x": 760.00,  "y": 860.00, "scale": 0.20},
        {"filename": "Tree1.png",  "x": 300.00,  "y": 540.00, "scale": 0.24},
        {"filename": "Tree2.png",  "x": 1220.00, "y": 540.00, "scale": 0.24}
    ],
    "enemy_infos": [
        {"x": 760.00, "y": 260.00}, {"x": 760.00, "y": 840.00},
        {"x": 560.00, "y": 540.00}, {"x": 960.00, "y": 540.00},
        {"x": 290.00, "y": 540.00}, {"x": 1240.00,"y": 540.00},
        {"x": 760.00, "y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.75, "y_ratio": 0.75}
}

S1_FIGHT_MAP_20 = {
    "obstacles": [
        {"filename": "Pond1.png",  "x": 560.00,  "y": 360.00, "scale": 0.60},
        {"filename": "Pond2.png",  "x": 980.00,  "y": 720.00, "scale": 0.60},
        {"filename": "Rock1.png",  "x": 280.00,  "y": 860.00, "scale": 0.22},
        {"filename": "Rock2.png",  "x": 1240.00, "y": 240.00, "scale": 0.22},
        {"filename": "Tree1.png",  "x": 320.00,  "y": 320.00, "scale": 0.24},
        {"filename": "Tree2.png",  "x": 1220.00, "y": 820.00, "scale": 0.24},
        {"filename": "Rock3.png",  "x": 960.00,  "y": 900.00, "scale": 0.20},
        {"filename": "Rock1.png",  "x": 560.00,  "y": 180.00, "scale": 0.20},
        {"filename": "Tree2.png",  "x": 1040.00, "y": 960.00, "scale": 0.24}
    ],
    "enemy_infos": [
        {"x": 290.00, "y": 560.00}, {"x": 1240.00,"y": 560.00},
        {"x": 560.00, "y": 300.00}, {"x": 980.00, "y": 300.00},
        {"x": 560.00, "y": 820.00}, {"x": 980.00, "y": 820.00},
        {"x": 760.00, "y": 560.00}, {"x": 960.00, "y": 360.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S1_FIGHT_MAP_21 = {
    "obstacles": [
        {"filename": "Pond1.png",      "x": 768.00,  "y": 540.00, "scale": 0.62},
        {"filename": "Rock1.png",      "x": 300.00,  "y": 280.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 1230.00, "y": 800.00, "scale": 0.22},
        {"filename": "Tree1.png",      "x": 300.00,  "y": 840.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1230.00, "y": 280.00, "scale": 0.26},
        {"filename": "Rock3.png",      "x": 1080.00, "y": 360.00, "scale": 0.22},
        {"filename": "FallenLog2.png", "x": 760.00,  "y": 920.00, "scale": 0.19},
        {"filename": "FallenLog1.png", "x": 760.00,  "y": 180.00, "scale": 0.19}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 220.00}, {"x": 1230.00,"y": 220.00},
        {"x": 300.00,"y": 880.00}, {"x": 1230.00,"y": 880.00},
        {"x": 560.00,"y": 340.00}, {"x": 980.00,"y": 740.00},
        {"x": 760.00,"y": 220.00}, {"x": 760.00,"y": 860.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S1_FIGHT_MAP_22 = {
    "obstacles": [
        {"filename": "Pond2.png",      "x": 1040.00, "y": 360.00, "scale": 0.60},
        {"filename": "Tree1.png",      "x": 320.00,  "y": 320.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1240.00, "y": 820.00, "scale": 0.26},
        {"filename": "Rock1.png",      "x": 560.00,  "y": 860.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 960.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Rock3.png",      "x": 320.00,  "y": 880.00, "scale": 0.22},
        {"filename": "FallenLog1.png", "x": 760.00,  "y": 180.00, "scale": 0.20},
        {"filename": "FallenLog2.png", "x": 760.00,  "y": 920.00, "scale": 0.20}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 360.00}, {"x": 980.00,"y": 760.00},
        {"x": 760.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.95, "y_ratio": 0.95}
}

S1_FIGHT_MAP_23 = {
    "obstacles": [
        {"filename": "Rock1.png",      "x": 320.00,  "y": 320.00, "scale": 0.24},
        {"filename": "Rock2.png",      "x": 1240.00, "y": 320.00, "scale": 0.24},
        {"filename": "Tree1.png",      "x": 320.00,  "y": 780.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1240.00, "y": 780.00, "scale": 0.26},
        {"filename": "Rock3.png",      "x": 760.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Rock1.png",      "x": 760.00,  "y": 860.00, "scale": 0.22},
        {"filename": "FallenLog1.png", "x": 520.00,  "y": 560.00, "scale": 0.19},
        {"filename": "FallenLog2.png", "x": 1000.00, "y": 560.00, "scale": 0.19}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 320.00}, {"x": 1000.00,"y": 320.00},
        {"x": 520.00,"y": 800.00}, {"x": 1000.00,"y": 800.00},
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 0.92}
}

S1_FIGHT_MAP_24 = {
    "obstacles": [
        {"filename": "Pond1.png",      "x": 520.00,  "y": 760.00, "scale": 0.58},
        {"filename": "Pond2.png",      "x": 1000.00, "y": 320.00, "scale": 0.58},
        {"filename": "Tree1.png",      "x": 300.00,  "y": 220.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1220.00, "y": 900.00, "scale": 0.26},
        {"filename": "Rock1.png",      "x": 560.00,  "y": 920.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 980.00,  "y": 180.00, "scale": 0.22},
        {"filename": "Rock3.png",      "x": 760.00,  "y": 540.00, "scale": 0.20}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 320.00}, {"x": 1220.00,"y": 320.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 760.00,"y": 200.00}, {"x": 760.00,"y": 920.00},
        {"x": 980.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.92, "y_ratio": 0.92}
}

S1_FIGHT_MAP_25 = {
    "obstacles": [
        {"filename": "FallenLog2.png", "x": 300.00,  "y": 540.00, "scale": 0.20},
        {"filename": "FallenLog2.png", "x": 1220.00, "y": 540.00, "scale": 0.20},
        {"filename": "FallenLog1.png", "x": 760.00,  "y": 320.00, "scale": 0.20},
        {"filename": "FallenLog1.png", "x": 760.00,  "y": 820.00, "scale": 0.20},
        {"filename": "Rock2.png",      "x": 560.00,  "y": 420.00, "scale": 0.22},
        {"filename": "Rock1.png",      "x": 960.00,  "y": 660.00, "scale": 0.22},
        {"filename": "Tree1.png",      "x": 520.00,  "y": 760.00, "scale": 0.25},
        {"filename": "Tree2.png",      "x": 1000.00, "y": 360.00, "scale": 0.25}
    ],
    "enemy_infos": [
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00},
        {"x": 760.00,"y": 380.00}, {"x": 760.00,"y": 700.00},
        {"x": 300.00,"y": 320.00}, {"x": 1220.00,"y": 820.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 320.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S1_FIGHT_MAP_26 = {
    "obstacles": [
        {"filename": "Rock3.png",      "x": 320.00,  "y": 320.00, "scale": 0.24},
        {"filename": "Rock1.png",      "x": 1240.00, "y": 320.00, "scale": 0.22},
        {"filename": "Tree1.png",      "x": 320.00,  "y": 780.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1240.00, "y": 780.00, "scale": 0.26},
        {"filename": "Rock2.png",      "x": 760.00,  "y": 900.00, "scale": 0.22},
        {"filename": "Rock1.png",      "x": 760.00,  "y": 200.00, "scale": 0.22},
        {"filename": "Tree1.png",      "x": 520.00,  "y": 660.00, "scale": 0.24},
        {"filename": "Tree2.png",      "x": 1000.00, "y": 420.00, "scale": 0.24}
    ],
    "enemy_infos": [
        {"x": 560.00,"y": 540.00}, {"x": 960.00,"y": 540.00},
        {"x": 760.00,"y": 360.00}, {"x": 760.00,"y": 720.00},
        {"x": 300.00,"y": 540.00}, {"x": 1220.00,"y": 540.00},
        {"x": 960.00,"y": 360.00}, {"x": 560.00,"y": 720.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S1_FIGHT_MAP_27 = {
    "obstacles": [
        {"filename": "Pond2.png",      "x": 960.00,  "y": 720.00, "scale": 0.60},
        {"filename": "Tree1.png",      "x": 320.00,  "y": 280.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1240.00, "y": 880.00, "scale": 0.26},
        {"filename": "Rock1.png",      "x": 560.00,  "y": 900.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 980.00,  "y": 260.00, "scale": 0.22},
        {"filename": "Rock3.png",      "x": 320.00,  "y": 900.00, "scale": 0.22},
        {"filename": "FallenLog2.png", "x": 760.00,  "y": 180.00, "scale": 0.19},
        {"filename": "FallenLog1.png", "x": 760.00,  "y": 940.00, "scale": 0.19}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 880.00}, {"x": 1220.00,"y": 880.00},
        {"x": 760.00,"y": 200.00}, {"x": 760.00,"y": 960.00},
        {"x": 560.00,"y": 560.00}, {"x": 980.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.94, "y_ratio": 0.92}
}

S1_FIGHT_MAP_28 = {
    "obstacles": [
        {"filename": "Rock1.png",      "x": 520.00,  "y": 360.00, "scale": 0.24},
        {"filename": "Rock2.png",      "x": 1000.00, "y": 360.00, "scale": 0.24},
        {"filename": "Tree1.png",      "x": 520.00,  "y": 720.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1000.00, "y": 720.00, "scale": 0.26},
        {"filename": "Rock3.png",      "x": 760.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 760.00,  "y": 860.00, "scale": 0.22},
        {"filename": "Tree1.png",      "x": 300.00,  "y": 540.00, "scale": 0.24},
        {"filename": "Tree2.png",      "x": 1220.00, "y": 540.00, "scale": 0.24}
    ],
    "enemy_infos": [
        {"x": 760.00,"y": 260.00}, {"x": 760.00,"y": 840.00},
        {"x": 560.00,"y": 540.00}, {"x": 960.00,"y": 540.00},
        {"x": 300.00,"y": 540.00}, {"x": 1220.00,"y": 540.00},
        {"x": 560.00,"y": 760.00}, {"x": 960.00,"y": 320.00}
    ],
    "crop_rect": {"x_ratio": 0.90, "y_ratio": 0.90}
}

S1_FIGHT_MAP_29 = {
    "obstacles": [
        {"filename": "FallenLog1.png", "x": 240.00,  "y": 360.00, "scale": 0.20},
        {"filename": "FallenLog1.png", "x": 1290.00, "y": 740.00, "scale": 0.20},
        {"filename": "Tree2.png",      "x": 1040.00, "y": 260.00, "scale": 0.26},
        {"filename": "Rock3.png",      "x": 560.00,  "y": 840.00, "scale": 0.22},
        {"filename": "Tree1.png",      "x": 360.00,  "y": 720.00, "scale": 0.26},
        {"filename": "Rock1.png",      "x": 1080.00, "y": 420.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 860.00,  "y": 760.00, "scale": 0.22},
        {"filename": "Tree2.png",      "x": 1240.00, "y": 260.00, "scale": 0.26}
    ],
    "enemy_infos": [
        {"x": 760.00,"y": 260.00}, {"x": 760.00,"y": 840.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00},
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.86, "y_ratio": 1.06}
}

S1_FIGHT_MAP_30 = {
    "obstacles": [
        {"filename": "Pond1.png",      "x": 560.00,  "y": 360.00, "scale": 0.58},
        {"filename": "Pond2.png",      "x": 980.00,  "y": 760.00, "scale": 0.58},
        {"filename": "Rock1.png",      "x": 280.00,  "y": 860.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 1240.00, "y": 240.00, "scale": 0.22},
        {"filename": "Tree1.png",      "x": 320.00,  "y": 320.00, "scale": 0.25},
        {"filename": "Tree2.png",      "x": 1220.00, "y": 820.00, "scale": 0.25},
        {"filename": "Rock3.png",      "x": 960.00,  "y": 900.00, "scale": 0.20},
        {"filename": "Rock1.png",      "x": 560.00,  "y": 180.00, "scale": 0.22},
        {"filename": "Tree2.png",      "x": 1040.00, "y": 960.00, "scale": 0.25}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 560.00,"y": 300.00}, {"x": 980.00,"y": 300.00},
        {"x": 560.00,"y": 820.00}, {"x": 980.00,"y": 820.00},
        {"x": 760.00,"y": 560.00}, {"x": 960.00,"y": 360.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S1_FIGHT_MAP_31 = {
    "obstacles": [
        {"filename": "Rock1.png",      "x": 520.00,  "y": 360.00, "scale": 0.24},
        {"filename": "Rock2.png",      "x": 1000.00, "y": 360.00, "scale": 0.24},
        {"filename": "Rock3.png",      "x": 760.00,  "y": 540.00, "scale": 0.22},
        {"filename": "Tree1.png",      "x": 320.00,  "y": 760.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1200.00, "y": 320.00, "scale": 0.26},
        {"filename": "FallenLog1.png", "x": 280.00,  "y": 900.00, "scale": 0.19},
        {"filename": "FallenLog2.png", "x": 1240.00, "y": 220.00, "scale": 0.19}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 300.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 540.00}, {"x": 960.00,"y": 540.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 920.00}
    ],
    "crop_rect": {"x_ratio": 0.96, "y_ratio": 0.96}
}

S1_FIGHT_MAP_32 = {
    "obstacles": [
        {"filename": "Pond2.png",      "x": 760.00,  "y": 560.00, "scale": 0.64},
        {"filename": "Tree1.png",      "x": 320.00,  "y": 280.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1200.00, "y": 840.00, "scale": 0.26},
        {"filename": "Rock1.png",      "x": 560.00,  "y": 360.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 960.00,  "y": 760.00, "scale": 0.22},
        {"filename": "FallenLog1.png", "x": 1080.00, "y": 220.00, "scale": 0.20},
        {"filename": "FallenLog2.png", "x": 440.00,  "y": 900.00, "scale": 0.20}
    ],
    "enemy_infos": [
        {"x": 280.00,"y": 280.00}, {"x": 1240.00,"y": 280.00},
        {"x": 280.00,"y": 840.00}, {"x": 1240.00,"y": 840.00},
        {"x": 560.00,"y": 800.00}, {"x": 960.00,"y": 320.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 920.00}
    ],
    "crop_rect": {"x_ratio": 1.02, "y_ratio": 0.90}
}

S1_FIGHT_MAP_33 = {
    "obstacles": [
        {"filename": "Rock3.png",      "x": 320.00,  "y": 320.00, "scale": 0.24},
        {"filename": "Rock1.png",      "x": 1240.00, "y": 320.00, "scale": 0.24},
        {"filename": "Tree1.png",      "x": 540.00,  "y": 220.00, "scale": 0.25},
        {"filename": "Tree2.png",      "x": 980.00,  "y": 900.00, "scale": 0.25},
        {"filename": "Rock2.png",      "x": 760.00,  "y": 180.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 760.00,  "y": 920.00, "scale": 0.22},
        {"filename": "FallenLog2.png", "x": 280.00,  "y": 900.00, "scale": 0.19},
        {"filename": "FallenLog1.png", "x": 1240.00, "y": 220.00, "scale": 0.19}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 540.00}, {"x": 1000.00,"y": 540.00},
        {"x": 760.00,"y": 360.00}, {"x": 760.00,"y": 720.00},
        {"x": 300.00,"y": 540.00}, {"x": 1220.00,"y": 540.00},
        {"x": 560.00,"y": 320.00}, {"x": 960.00,"y": 760.00}
    ],
    "crop_rect": {"x_ratio": 0.90, "y_ratio": 0.90}
}

S1_FIGHT_MAP_34 = {
    "obstacles": [
        {"filename": "Pond1.png",      "x": 980.00,  "y": 760.00, "scale": 0.60},
        {"filename": "Tree1.png",      "x": 320.00,  "y": 280.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1220.00, "y": 880.00, "scale": 0.26},
        {"filename": "Rock1.png",      "x": 560.00,  "y": 900.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 960.00,  "y": 260.00, "scale": 0.22},
        {"filename": "Rock3.png",      "x": 320.00,  "y": 900.00, "scale": 0.22},
        {"filename": "FallenLog1.png", "x": 760.00,  "y": 180.00, "scale": 0.19}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 880.00}, {"x": 1220.00,"y": 880.00},
        {"x": 560.00,"y": 560.00}, {"x": 980.00,"y": 560.00},
        {"x": 760.00,"y": 920.00}
    ],
    "crop_rect": {"x_ratio": 0.94, "y_ratio": 0.94}
}

S1_FIGHT_MAP_35 = {
    "obstacles": [
        {"filename": "Rock1.png",      "x": 520.00,  "y": 360.00, "scale": 0.24},
        {"filename": "Rock2.png",      "x": 1000.00, "y": 360.00, "scale": 0.24},
        {"filename": "Tree1.png",      "x": 520.00,  "y": 720.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1000.00, "y": 720.00, "scale": 0.26},
        {"filename": "Rock3.png",      "x": 760.00,  "y": 540.00, "scale": 0.22},
        {"filename": "FallenLog1.png", "x": 280.00,  "y": 540.00, "scale": 0.20},
        {"filename": "FallenLog2.png", "x": 1240.00, "y": 540.00, "scale": 0.20}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 540.00}, {"x": 1000.00,"y": 540.00},
        {"x": 760.00,"y": 360.00}, {"x": 760.00,"y": 720.00},
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 800.00},
        {"x": 300.00,"y": 800.00}, {"x": 1220.00,"y": 300.00}
    ],
    "crop_rect": {"x_ratio": 1.02, "y_ratio": 0.88}
}

S1_FIGHT_MAP_36 = {
    "obstacles": [
        {"filename": "Pond2.png",      "x": 760.00,  "y": 560.00, "scale": 0.62},
        {"filename": "Tree1.png",      "x": 540.00,  "y": 220.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 980.00,  "y": 900.00, "scale": 0.26},
        {"filename": "Rock1.png",      "x": 320.00,  "y": 820.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 1200.00, "y": 320.00, "scale": 0.22},
        {"filename": "Rock3.png",      "x": 760.00,  "y": 900.00, "scale": 0.22},
        {"filename": "FallenLog2.png", "x": 760.00,  "y": 180.00, "scale": 0.20}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 300.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 360.00}, {"x": 960.00,"y": 760.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.96, "y_ratio": 0.96}
}

S1_FIGHT_MAP_37 = {
    "obstacles": [
        {"filename": "Rock3.png",      "x": 300.00,  "y": 300.00, "scale": 0.24},
        {"filename": "Rock1.png",      "x": 1220.00, "y": 300.00, "scale": 0.24},
        {"filename": "Rock2.png",      "x": 300.00,  "y": 780.00, "scale": 0.24},
        {"filename": "Rock1.png",      "x": 1220.00, "y": 780.00, "scale": 0.24},
        {"filename": "Tree1.png",      "x": 520.00,  "y": 540.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1000.00, "y": 540.00, "scale": 0.26},
        {"filename": "FallenLog1.png", "x": 760.00,  "y": 320.00, "scale": 0.20},
        {"filename": "FallenLog2.png", "x": 760.00,  "y": 820.00, "scale": 0.20}
    ],
    "enemy_infos": [
        {"x": 760.00,"y": 220.00}, {"x": 760.00,"y": 900.00},
        {"x": 520.00,"y": 360.00}, {"x": 1000.00,"y": 720.00},
        {"x": 520.00,"y": 720.00}, {"x": 1000.00,"y": 360.00},
        {"x": 300.00,"y": 540.00}, {"x": 1220.00,"y": 540.00}
    ],
    "crop_rect": {"x_ratio": 0.90, "y_ratio": 1.00}
}

S1_FIGHT_MAP_38 = {
    "obstacles": [
        {"filename": "Pond1.png",      "x": 520.00,  "y": 320.00, "scale": 0.58},
        {"filename": "Pond2.png",      "x": 1000.00, "y": 800.00, "scale": 0.58},
        {"filename": "Tree1.png",      "x": 320.00,  "y": 900.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1220.00, "y": 220.00, "scale": 0.26},
        {"filename": "Rock1.png",      "x": 560.00,  "y": 920.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 960.00,  "y": 360.00, "scale": 0.22},
        {"filename": "Rock3.png",      "x": 760.00,  "y": 560.00, "scale": 0.20}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 540.00}, {"x": 960.00,"y": 540.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.92, "y_ratio": 0.92}
}

S1_FIGHT_MAP_39 = {
    "obstacles": [
        {"filename": "Rock1.png",      "x": 520.00,  "y": 360.00, "scale": 0.24},
        {"filename": "Rock2.png",      "x": 1000.00, "y": 360.00, "scale": 0.24},
        {"filename": "Rock3.png",      "x": 760.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Rock1.png",      "x": 760.00,  "y": 860.00, "scale": 0.22},
        {"filename": "Tree1.png",      "x": 300.00,  "y": 540.00, "scale": 0.25},
        {"filename": "Tree2.png",      "x": 1220.00, "y": 540.00, "scale": 0.25},
        {"filename": "FallenLog2.png", "x": 280.00,  "y": 900.00, "scale": 0.19},
        {"filename": "FallenLog1.png", "x": 1240.00, "y": 220.00, "scale": 0.19}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 540.00}, {"x": 1000.00,"y": 540.00},
        {"x": 760.00,"y": 360.00}, {"x": 760.00,"y": 720.00},
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 800.00},
        {"x": 300.00,"y": 800.00}, {"x": 1220.00,"y": 300.00}
    ],
    "crop_rect": {"x_ratio": 0.88, "y_ratio": 0.96}
}

S1_FIGHT_MAP_40 = {
    "obstacles": [
        {"filename": "Pond2.png",      "x": 560.00,  "y": 360.00, "scale": 0.60},
        {"filename": "Pond1.png",      "x": 980.00,  "y": 760.00, "scale": 0.60},
        {"filename": "Tree1.png",      "x": 300.00,  "y": 860.00, "scale": 0.26},
        {"filename": "Tree2.png",      "x": 1240.00, "y": 240.00, "scale": 0.26},
        {"filename": "Rock1.png",      "x": 320.00,  "y": 320.00, "scale": 0.22},
        {"filename": "Rock2.png",      "x": 1220.00, "y": 820.00, "scale": 0.22},
        {"filename": "Rock3.png",      "x": 760.00,  "y": 560.00, "scale": 0.20},
        {"filename": "FallenLog1.png", "x": 1060.00, "y": 960.00, "scale": 0.19},
        {"filename": "FallenLog2.png", "x": 460.00,  "y": 180.00, "scale": 0.19}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 300.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 360.00}, {"x": 980.00,"y": 760.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S1_FIGHT_DEBUG = { # 디버그
    "obstacles": [
    ],
    "enemy_infos": [
    ],
    "crop_rect": {"x_ratio": 0.4, "y_ratio": 0.4}
}










S2_FIGHT_MAP_1 = {
    "obstacles": [
        {"filename": "Vehicle1.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 220.00, "scale": 0.26},
        {"filename": "Dump1.png",      "x": 1140.00, "y": 260.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 380.00,  "y": 820.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 260.00, "y": 560.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 1060.00, "y": 540.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 960.00,  "y": 900.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 280.00,"y": 540.00}, {"x": 1240.00,"y": 540.00},
        {"x": 320.00,"y": 860.00}, {"x": 1200.00,"y": 220.00},
        {"x": 760.00,"y": 420.00}, {"x": 760.00,"y": 900.00},
        {"x": 1040.00,"y": 360.00}, {"x": 480.00,"y": 760.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S2_FIGHT_MAP_2 = {
    "obstacles": [
        {"filename": "Vehicle3.png",   "x": 520.00,  "y": 740.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 1000.00, "y": 300.00, "scale": 0.50},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 860.00, "scale": 0.26},
        {"filename": "Dump2.png",      "x": 560.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 960.00,  "y": 560.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 260.00,  "y": 360.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 1260.00,"y": 760.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 1060.00, "y": 920.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 280.00,"y": 320.00}, {"x": 1240.00,"y": 320.00},
        {"x": 320.00,"y": 860.00}, {"x": 1200.00,"y": 860.00},
        {"x": 760.00,"y": 520.00}, {"x": 760.00,"y": 920.00},
        {"x": 1080.00,"y": 740.00}, {"x": 440.00,"y": 300.00}
    ],
    "crop_rect": {"x_ratio": 0.95, "y_ratio": 0.95}
}

S2_FIGHT_MAP_3 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 760.00,  "y": 560.00, "scale": 0.62},
        {"filename": "Vehicle2.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle1.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 480.00,  "y": 900.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 1040.00, "y": 220.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 260.00,  "y": 560.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 1260.00,"y": 560.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 320.00}, {"x": 1220.00,"y": 320.00},
        {"x": 300.00,"y": 840.00}, {"x": 1220.00,"y": 840.00},
        {"x": 560.00,"y": 860.00}, {"x": 980.00,"y": 260.00},
        {"x": 320.00,"y": 680.00}, {"x": 1200.00,"y": 440.00}
    ],
    "crop_rect": {"x_ratio": 0.9, "y_ratio": 0.9}
}

S2_FIGHT_MAP_4 = {
    "obstacles": [
        {"filename": "Barricade1.png", "x": 300.00,  "y": 540.00, "scale": 0.28},
        {"filename": "Barricade1.png", "x": 1220.00, "y": 540.00, "scale": 0.28},
        {"filename": "Vehicle3.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Dump2.png",      "x": 520.00,  "y": 840.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 1000.00, "y": 260.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 760.00,  "y": 360.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 760.00, "y": 900.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 520.00}, {"x": 1000.00,"y": 560.00},
        {"x": 300.00,"y": 360.00}, {"x": 1220.00,"y": 720.00},
        {"x": 300.00,"y": 720.00}, {"x": 1220.00,"y": 360.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 0.9}
}

S2_FIGHT_MAP_5 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 480.00,  "y": 360.00, "scale": 0.58},
        {"filename": "Hole1.png",      "x": 1040.00, "y": 760.00, "scale": 0.58},
        {"filename": "Vehicle1.png",   "x": 1000.00, "y": 320.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 520.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 960.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 560.00,  "y": 900.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 760.00,  "y": 540.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 840.00}, {"x": 1220.00,"y": 840.00},
        {"x": 760.00,"y": 200.00}, {"x": 760.00,"y": 920.00},
        {"x": 320.00,"y": 600.00}, {"x": 1200.00,"y": 480.00}
    ],
    "crop_rect": {"x_ratio": 0.9, "y_ratio": 0.9}
}

S2_FIGHT_MAP_6 = {
    "obstacles": [
        {"filename": "Barricade1.png", "x": 760.00,  "y": 300.00, "scale": 0.28},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 780.00, "scale": 0.28},
        {"filename": "Vehicle3.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Dump2.png",      "x": 520.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 1000.00, "y": 560.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 260.00, "y": 840.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 1260.00, "y": 280.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 280.00,"y": 560.00}, {"x": 1240.00,"y": 560.00},
        {"x": 300.00,"y": 320.00}, {"x": 1220.00,"y": 800.00},
        {"x": 760.00,"y": 520.00}, {"x": 760.00,"y": 920.00},
        {"x": 520.00,"y": 160.00}, {"x": 1000.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S2_FIGHT_MAP_7 = {
    "obstacles": [
        {"filename": "Vehicle1.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 1000.00, "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle3.png",   "x": 520.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 540.00, "scale": 0.26},
        {"filename": "Dump1.png",      "x": 560.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 960.00,  "y": 860.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 760.00,  "y": 900.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 540.00}, {"x": 1220.00,"y": 540.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 900.00},
        {"x": 360.00,"y": 300.00}, {"x": 1160.00,"y": 300.00},
        {"x": 360.00,"y": 780.00}, {"x": 1160.00,"y": 780.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 0.95}
}

S2_FIGHT_MAP_8 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 760.00,  "y": 560.00, "scale": 0.60},
        {"filename": "Dump2.png",      "x": 300.00,  "y": 320.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 1220.00, "y": 800.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 540.00,  "y": 860.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 980.00,  "y": 260.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 1260.00,"y": 320.00, "scale": 0.22},
        {"filename": "Vehicle4.png",   "x": 560.00,  "y": 760.00, "scale": 0.50}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 220.00}, {"x": 1220.00,"y": 900.00},
        {"x": 300.00,"y": 900.00}, {"x": 1220.00,"y": 220.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 920.00},
        {"x": 980.00,"y": 560.00}, {"x": 540.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.9, "y_ratio": 0.9}
}

S2_FIGHT_MAP_9 = {
    "obstacles": [
        {"filename": "Vehicle2.png",   "x": 560.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle3.png",   "x": 960.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle1.png",   "x": 560.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 960.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 300.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 1220.00, "y": 560.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 760.00, "y": 420.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 760.00,  "y": 700.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 200.00}, {"x": 1220.00,"y": 200.00},
        {"x": 300.00,"y": 920.00}, {"x": 1220.00,"y": 920.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00},
        {"x": 220.00,"y": 560.00}, {"x": 1300.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S2_FIGHT_MAP_10 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 480.00,  "y": 760.00, "scale": 0.56},
        {"filename": "Vehicle1.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Barricade1.png", "x": 1220.00, "y": 540.00, "scale": 0.26},
        {"filename": "Dump2.png",      "x": 1000.00, "y": 260.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 560.00,  "y": 520.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 260.00, "y": 860.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 200.00}, {"x": 1220.00,"y": 200.00},
        {"x": 300.00,"y": 920.00}, {"x": 1220.00,"y": 920.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 960.00},
        {"x": 1120.00,"y": 360.00}, {"x": 400.00,"y": 720.00}
    ],
    "crop_rect": {"x_ratio": 0.88, "y_ratio": 0.95}
}

S2_FIGHT_MAP_11 = {
    "obstacles": [
        {"filename": "Vehicle3.png",   "x": 960.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 560.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 1080.00, "y": 220.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 460.00,  "y": 900.00, "scale": 0.22},
        {"filename": "Barricade1.png", "x": 220.00,  "y": 540.00, "scale": 0.26},
        {"filename": "ElectricBox1.png","x": 560.00, "y": 540.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 960.00,  "y": 540.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 1260.00, "y": 540.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 360.00}, {"x": 960.00,"y": 720.00},
        {"x": 320.00,"y": 560.00}, {"x": 1200.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 0.9}
}

S2_FIGHT_MAP_12 = {
    "obstacles": [
        {"filename": "Vehicle4.png",   "x": 1000.00, "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle3.png",   "x": 520.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Dump2.png",      "x": 1180.00, "y": 900.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 360.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 160.00, "scale": 0.24},
        {"filename": "ElectricBox1.png","x": 560.00, "y": 860.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 960.00,  "y": 860.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 260.00,  "y": 540.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 760.00,"y": 360.00}, {"x": 760.00,"y": 720.00},
        {"x": 520.00,"y": 520.00}, {"x": 1000.00,"y": 520.00}
    ],
    "crop_rect": {"x_ratio": 0.95, "y_ratio": 0.88}
}

S2_FIGHT_MAP_13 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 980.00,  "y": 540.00, "scale": 0.56},
        {"filename": "Vehicle1.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 320.00,  "y": 860.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 1240.00, "y": 240.00, "scale": 0.22},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 900.00, "scale": 0.26},
        {"filename": "ElectricBox1.png","x": 560.00, "y": 380.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 960.00,  "y": 700.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 260.00,"y": 540.00}, {"x": 1280.00,"y": 540.00},
        {"x": 560.00,"y": 320.00}, {"x": 960.00,"y": 320.00},
        {"x": 560.00,"y": 760.00}, {"x": 960.00,"y": 760.00},
        {"x": 760.00,"y": 140.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.9, "y_ratio": 0.9}
}

S2_FIGHT_MAP_14 = {
    "obstacles": [
        {"filename": "Vehicle3.png",   "x": 1000.00, "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 520.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Dump2.png",      "x": 1180.00, "y": 900.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 360.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 900.00, "scale": 0.26},
        {"filename": "ElectricBox1.png","x": 560.00, "y": 540.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 960.00,  "y": 540.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 260.00,  "y": 540.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 360.00}, {"x": 960.00,"y": 720.00},
        {"x": 520.00,"y": 180.00}, {"x": 1000.00,"y": 920.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S2_FIGHT_MAP_15 = {
    "obstacles": [
        {"filename": "Vehicle1.png",   "x": 960.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 560.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle3.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Dump2.png",      "x": 560.00,  "y": 420.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 960.00,  "y": 700.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 260.00, "y": 560.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 1260.00, "y": 560.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00},
        {"x": 360.00,"y": 360.00}, {"x": 1160.00,"y": 760.00},
        {"x": 360.00,"y": 760.00}, {"x": 1160.00,"y": 360.00}
    ],
    "crop_rect": {"x_ratio": 0.9, "y_ratio": 1.0}
}

S2_FIGHT_MAP_16 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 520.00,  "y": 320.00, "scale": 0.56},
        {"filename": "Hole1.png",      "x": 1000.00, "y": 800.00, "scale": 0.56},
        {"filename": "Vehicle4.png",   "x": 1000.00, "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle3.png",   "x": 520.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 980.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 560.00,  "y": 900.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 760.00,  "y": 560.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 220.00}, {"x": 1220.00,"y": 900.00},
        {"x": 300.00,"y": 900.00}, {"x": 1220.00,"y": 220.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 960.00},
        {"x": 980.00,"y": 560.00}, {"x": 540.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.85, "y_ratio": 0.9}
}

S2_FIGHT_MAP_17 = {
    "obstacles": [
        {"filename": "Vehicle2.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle1.png",   "x": 1000.00, "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 520.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle3.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 540.00, "scale": 0.26},
        {"filename": "ElectricBox1.png","x": 760.00, "y": 900.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 760.00,  "y": 220.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 540.00}, {"x": 1220.00,"y": 540.00},
        {"x": 360.00,"y": 300.00}, {"x": 1160.00,"y": 300.00},
        {"x": 360.00,"y": 780.00}, {"x": 1160.00,"y": 780.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S2_FIGHT_MAP_18 = {
    "obstacles": [
        {"filename": "Vehicle3.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 560.00,  "y": 340.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 960.00,  "y": 780.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 260.00, "y": 540.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 1260.00, "y": 540.00, "scale": 0.22},
        {"filename": "Vehicle1.png",   "x": 520.00,  "y": 760.00, "scale": 0.50}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 220.00}, {"x": 1220.00,"y": 220.00},
        {"x": 300.00,"y": 900.00}, {"x": 1220.00,"y": 900.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 940.00},
        {"x": 1040.00,"y": 560.00}, {"x": 480.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.95, "y_ratio": 0.95}
}

S2_FIGHT_MAP_19 = {
    "obstacles": [
        {"filename": "Vehicle3.png",   "x": 560.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 960.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 560.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle1.png",   "x": 960.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Dump2.png",      "x": 300.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 1220.00, "y": 560.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 760.00,  "y": 920.00, "scale": 0.30},
        {"filename": "ElectricBox1.png","x": 760.00, "y": 200.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 200.00}, {"x": 1220.00,"y": 200.00},
        {"x": 300.00,"y": 920.00}, {"x": 1220.00,"y": 920.00},
        {"x": 220.00,"y": 560.00}, {"x": 1300.00,"y": 560.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00}
    ],
    "crop_rect": {"x_ratio": 0.9, "y_ratio": 0.9}
}

S2_FIGHT_MAP_20 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 560.00,  "y": 360.00, "scale": 0.56},
        {"filename": "Hole1.png",      "x": 980.00,  "y": 760.00, "scale": 0.56},
        {"filename": "Vehicle1.png",   "x": 520.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 1000.00, "y": 300.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 320.00,  "y": 320.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 1220.00, "y": 820.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 1060.00,"y": 960.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 460.00,  "y": 180.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 220.00}, {"x": 1220.00,"y": 900.00},
        {"x": 300.00,"y": 900.00}, {"x": 1220.00,"y": 220.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 960.00},
        {"x": 980.00,"y": 560.00}, {"x": 540.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S2_FIGHT_MAP_21 = {
    "obstacles": [
        {"filename": "Vehicle1.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 1000.00, "y": 780.00, "scale": 0.50},
        {"filename": "Hole1.png",      "x": 760.00,  "y": 560.00, "scale": 0.56},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 220.00, "scale": 0.26},
        {"filename": "Dump1.png",      "x": 1140.00, "y": 260.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 380.00,  "y": 820.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 260.00, "y": 560.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 1060.00, "y": 540.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 960.00,  "y": 900.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 240.00}, {"x": 1220.00,"y": 240.00},
        {"x": 300.00,"y": 840.00}, {"x": 1220.00,"y": 840.00},
        {"x": 560.00,"y": 360.00}, {"x": 960.00,"y": 760.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 1.00, "y_ratio": 1.00}
}

S2_FIGHT_MAP_22 = {
    "obstacles": [
        {"filename": "Vehicle3.png",   "x": 1160.00, "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 360.00,  "y": 780.00, "scale": 0.50},
        {"filename": "Barricade1.png", "x": 220.00,  "y": 540.00, "scale": 0.26},
        {"filename": "Dump1.png",      "x": 1080.00, "y": 220.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 460.00,  "y": 900.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 560.00, "y": 540.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 960.00,  "y": 540.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 1260.00, "y": 540.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 280.00}, {"x": 1220.00,"y": 280.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 760.00,"y": 360.00}, {"x": 760.00,"y": 760.00},
        {"x": 560.00,"y": 920.00}, {"x": 960.00,"y": 160.00}
    ],
    "crop_rect": {"x_ratio": 0.96, "y_ratio": 0.92}
}

S2_FIGHT_MAP_23 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 980.00,  "y": 540.00, "scale": 0.58},
        {"filename": "Vehicle2.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle1.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 320.00,  "y": 860.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 1240.00, "y": 240.00, "scale": 0.22},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 900.00, "scale": 0.26},
        {"filename": "ElectricBox1.png","x": 560.00, "y": 380.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 960.00,  "y": 700.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 260.00,"y": 540.00}, {"x": 1280.00,"y": 540.00},
        {"x": 560.00,"y": 320.00}, {"x": 960.00,"y": 320.00},
        {"x": 560.00,"y": 760.00}, {"x": 960.00,"y": 760.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.92, "y_ratio": 0.92}
}

S2_FIGHT_MAP_24 = {
    "obstacles": [
        {"filename": "Vehicle3.png",   "x": 320.00,  "y": 320.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 1200.00, "y": 780.00, "scale": 0.50},
        {"filename": "Hole1.png",      "x": 760.00,  "y": 720.00, "scale": 0.56},
        {"filename": "Dump2.png",      "x": 560.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 960.00,  "y": 900.00, "scale": 0.22},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 160.00, "scale": 0.26},
        {"filename": "ElectricBox1.png","x": 280.00, "y": 860.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 1240.00, "y": 240.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 860.00}, {"x": 1220.00,"y": 860.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00},
        {"x": 760.00,"y": 920.00}, {"x": 760.00,"y": 360.00}
    ],
    "crop_rect": {"x_ratio": 0.94, "y_ratio": 0.96}
}

S2_FIGHT_MAP_25 = {
    "obstacles": [
        {"filename": "Barricade1.png", "x": 300.00,  "y": 540.00, "scale": 0.26},
        {"filename": "Barricade1.png", "x": 1220.00, "y": 540.00, "scale": 0.26},
        {"filename": "Vehicle1.png",   "x": 520.00,  "y": 320.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Dump2.png",      "x": 520.00,  "y": 820.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 1000.00, "y": 280.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 760.00, "y": 900.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 760.00,  "y": 220.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 520.00}, {"x": 1000.00,"y": 560.00},
        {"x": 300.00,"y": 360.00}, {"x": 1220.00,"y": 720.00},
        {"x": 300.00,"y": 720.00}, {"x": 1220.00,"y": 360.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 1.00, "y_ratio": 0.90}
}

S2_FIGHT_MAP_26 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 520.00,  "y": 360.00, "scale": 0.58},
        {"filename": "Hole1.png",      "x": 1000.00, "y": 760.00, "scale": 0.58},
        {"filename": "Vehicle3.png",   "x": 1180.00, "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 340.00,  "y": 820.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 980.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 560.00,  "y": 900.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 260.00, "y": 540.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 1260.00, "y": 540.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 280.00}, {"x": 1220.00,"y": 280.00},
        {"x": 300.00,"y": 840.00}, {"x": 1220.00,"y": 840.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.90, "y_ratio": 0.92}
}

S2_FIGHT_MAP_27 = {
    "obstacles": [
        {"filename": "Vehicle1.png",   "x": 320.00,  "y": 320.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 1200.00, "y": 320.00, "scale": 0.50},
        {"filename": "Vehicle3.png",   "x": 320.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 1200.00, "y": 760.00, "scale": 0.50},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 540.00, "scale": 0.26},
        {"filename": "Dump1.png",      "x": 560.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 960.00,  "y": 860.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 760.00,  "y": 900.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 540.00}, {"x": 1220.00,"y": 540.00},
        {"x": 360.00,"y": 300.00}, {"x": 1160.00,"y": 300.00},
        {"x": 360.00,"y": 780.00}, {"x": 1160.00,"y": 780.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 1.00, "y_ratio": 0.95}
}

S2_FIGHT_MAP_28 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 760.00,  "y": 560.00, "scale": 0.60},
        {"filename": "Vehicle4.png",   "x": 560.00,  "y": 780.00, "scale": 0.50},
        {"filename": "Vehicle3.png",   "x": 960.00,  "y": 280.00, "scale": 0.50},
        {"filename": "Dump2.png",      "x": 300.00,  "y": 320.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 1220.00, "y": 800.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 540.00,  "y": 860.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 980.00, "y": 220.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 220.00}, {"x": 1220.00,"y": 900.00},
        {"x": 300.00,"y": 900.00}, {"x": 1220.00,"y": 220.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00},
        {"x": 980.00,"y": 560.00}, {"x": 540.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.90, "y_ratio": 0.90}
}

S2_FIGHT_MAP_29 = {
    "obstacles": [
        {"filename": "Vehicle2.png",   "x": 560.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle1.png",   "x": 960.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 300.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 1220.00, "y": 560.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 760.00, "y": 420.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 760.00,  "y": 700.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 760.00,  "y": 940.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 200.00}, {"x": 1220.00,"y": 200.00},
        {"x": 300.00,"y": 920.00}, {"x": 1220.00,"y": 920.00},
        {"x": 220.00,"y": 560.00}, {"x": 1300.00,"y": 560.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00}
    ],
    "crop_rect": {"x_ratio": 1.00, "y_ratio": 1.00}
}

S2_FIGHT_MAP_30 = {
    "obstacles": [
        {"filename": "Vehicle3.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Hole1.png",      "x": 480.00,  "y": 760.00, "scale": 0.56},
        {"filename": "Dump2.png",      "x": 960.00,  "y": 260.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 560.00,  "y": 520.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 260.00, "y": 860.00, "scale": 0.22},
        {"filename": "Barricade1.png", "x": 1220.00, "y": 540.00, "scale": 0.26}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 220.00}, {"x": 1220.00,"y": 900.00},
        {"x": 300.00,"y": 900.00}, {"x": 1220.00,"y": 220.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00},
        {"x": 1120.00,"y": 360.00}, {"x": 400.00,"y": 720.00}
    ],
    "crop_rect": {"x_ratio": 0.88, "y_ratio": 0.94}
}

S2_FIGHT_MAP_31 = {
    "obstacles": [
        {"filename": "Vehicle1.png",   "x": 960.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 560.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle3.png",   "x": 320.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 1200.00, "y": 760.00, "scale": 0.50},
        {"filename": "Dump2.png",      "x": 560.00,  "y": 420.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 960.00,  "y": 700.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 260.00, "y": 560.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 1260.00, "y": 560.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00},
        {"x": 360.00,"y": 360.00}, {"x": 1160.00,"y": 760.00},
        {"x": 360.00,"y": 760.00}, {"x": 1160.00,"y": 360.00}
    ],
    "crop_rect": {"x_ratio": 0.92, "y_ratio": 1.00}
}

S2_FIGHT_MAP_32 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 980.00,  "y": 360.00, "scale": 0.58},
        {"filename": "Vehicle2.png",   "x": 520.00,  "y": 860.00, "scale": 0.50},
        {"filename": "Vehicle1.png",   "x": 1000.00, "y": 220.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 320.00,  "y": 900.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 1240.00, "y": 220.00, "scale": 0.22},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 900.00, "scale": 0.26},
        {"filename": "ElectricBox1.png","x": 560.00, "y": 380.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 960.00,  "y": 700.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 260.00,"y": 540.00}, {"x": 1280.00,"y": 540.00},
        {"x": 560.00,"y": 320.00}, {"x": 960.00,"y": 320.00},
        {"x": 560.00,"y": 760.00}, {"x": 960.00,"y": 760.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.94, "y_ratio": 0.90}
}

S2_FIGHT_MAP_33 = {
    "obstacles": [
        {"filename": "Vehicle3.png",   "x": 1200.00, "y": 780.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 320.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Hole1.png",      "x": 760.00,  "y": 360.00, "scale": 0.56},
        {"filename": "Dump2.png",      "x": 560.00,  "y": 900.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 960.00,  "y": 220.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 280.00, "y": 860.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 1240.00, "y": 240.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 760.00,  "y": 920.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 860.00}, {"x": 1220.00,"y": 860.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00},
        {"x": 760.00,"y": 720.00}, {"x": 760.00,"y": 160.00}
    ],
    "crop_rect": {"x_ratio": 0.96, "y_ratio": 0.96}
}

S2_FIGHT_MAP_34 = {
    "obstacles": [
        {"filename": "Vehicle1.png",   "x": 1180.00, "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 340.00,  "y": 780.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 1080.00, "y": 220.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 460.00,  "y": 900.00, "scale": 0.22},
        {"filename": "Barricade1.png", "x": 220.00,  "y": 540.00, "scale": 0.26},
        {"filename": "ElectricBox1.png","x": 560.00, "y": 540.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 960.00,  "y": 540.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 1260.00, "y": 540.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 280.00}, {"x": 1220.00,"y": 280.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 360.00}, {"x": 960.00,"y": 720.00},
        {"x": 320.00,"y": 560.00}, {"x": 1200.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 1.00, "y_ratio": 0.92}
}

S2_FIGHT_MAP_35 = {
    "obstacles": [
        {"filename": "Vehicle3.png",   "x": 1000.00, "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 520.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Dump2.png",      "x": 1180.00, "y": 900.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 360.00,  "y": 220.00, "scale": 0.22},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 900.00, "scale": 0.26},
        {"filename": "ElectricBox1.png","x": 560.00, "y": 540.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 960.00,  "y": 540.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 260.00,  "y": 540.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 360.00}, {"x": 960.00,"y": 720.00},
        {"x": 520.00,"y": 180.00}, {"x": 1000.00,"y": 920.00}
    ],
    "crop_rect": {"x_ratio": 0.98, "y_ratio": 0.98}
}

S2_FIGHT_MAP_36 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 560.00,  "y": 700.00, "scale": 0.56},
        {"filename": "Vehicle1.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Barricade1.png", "x": 1220.00, "y": 540.00, "scale": 0.26},
        {"filename": "Dump2.png",      "x": 1000.00, "y": 260.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 560.00,  "y": 520.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 260.00, "y": 860.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 200.00}, {"x": 1220.00,"y": 920.00},
        {"x": 300.00,"y": 920.00}, {"x": 1220.00,"y": 200.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00},
        {"x": 1120.00,"y": 360.00}, {"x": 400.00,"y": 720.00}
    ],
    "crop_rect": {"x_ratio": 0.90, "y_ratio": 0.94}
}

S2_FIGHT_MAP_37 = {
    "obstacles": [
        {"filename": "Vehicle2.png",   "x": 520.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle1.png",   "x": 1000.00, "y": 300.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 520.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle3.png",   "x": 1000.00, "y": 760.00, "scale": 0.50},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 540.00, "scale": 0.26},
        {"filename": "ElectricBox1.png","x": 760.00, "y": 900.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 760.00,  "y": 220.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 540.00}, {"x": 1220.00,"y": 540.00},
        {"x": 360.00,"y": 300.00}, {"x": 1160.00,"y": 300.00},
        {"x": 360.00,"y": 780.00}, {"x": 1160.00,"y": 780.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 1.02, "y_ratio": 0.96}
}

S2_FIGHT_MAP_38 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 980.00,  "y": 540.00, "scale": 0.58},
        {"filename": "Vehicle3.png",   "x": 320.00,  "y": 880.00, "scale": 0.50},
        {"filename": "Vehicle4.png",   "x": 1200.00, "y": 240.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 540.00,  "y": 340.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 980.00,  "y": 780.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 260.00, "y": 560.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 1260.00, "y": 560.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 760.00,  "y": 160.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00},
        {"x": 760.00,"y": 920.00}, {"x": 760.00,"y": 360.00}
    ],
    "crop_rect": {"x_ratio": 0.94, "y_ratio": 0.94}
}

S2_FIGHT_MAP_39 = {
    "obstacles": [
        {"filename": "Vehicle1.png",   "x": 1180.00, "y": 780.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 340.00,  "y": 300.00, "scale": 0.50},
        {"filename": "Dump2.png",      "x": 300.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Dump1.png",      "x": 1220.00, "y": 560.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 760.00, "y": 420.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 760.00,  "y": 700.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 760.00,  "y": 940.00, "scale": 0.30},
        {"filename": "Barricade1.png", "x": 760.00,  "y": 180.00, "scale": 0.26}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 200.00}, {"x": 1220.00,"y": 200.00},
        {"x": 300.00,"y": 920.00}, {"x": 1220.00,"y": 920.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00},
        {"x": 220.00,"y": 560.00}, {"x": 1300.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.98, "y_ratio": 0.98}
}

S2_FIGHT_MAP_40 = {
    "obstacles": [
        {"filename": "Hole1.png",      "x": 560.00,  "y": 360.00, "scale": 0.56},
        {"filename": "Hole1.png",      "x": 1000.00, "y": 760.00, "scale": 0.56},
        {"filename": "Vehicle1.png",   "x": 520.00,  "y": 760.00, "scale": 0.50},
        {"filename": "Vehicle2.png",   "x": 1000.00, "y": 300.00, "scale": 0.50},
        {"filename": "Dump1.png",      "x": 320.00,  "y": 320.00, "scale": 0.22},
        {"filename": "Dump2.png",      "x": 1220.00, "y": 820.00, "scale": 0.22},
        {"filename": "TrashCan1.png",  "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "ElectricBox1.png","x": 1060.00,"y": 960.00, "scale": 0.22},
        {"filename": "FirePlug1.png",  "x": 460.00,  "y": 180.00, "scale": 0.30}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 220.00}, {"x": 1220.00,"y": 900.00},
        {"x": 300.00,"y": 900.00}, {"x": 1220.00,"y": 220.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00},
        {"x": 980.00,"y": 560.00}, {"x": 540.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 1.00, "y_ratio": 1.00}
}

S2_FIGHT_DEBUG = { # 디버그
    "obstacles": [
        {"filename": "TrashCan1.png", "x": 100.00, "y": 100.00, "scale": 0.3}
    ],
    "enemy_infos": [
        {"x": 130.00, "y": 200.00},
    ],
    "crop_rect": {"x_ratio": 0.4, "y_ratio": 0.4}
}










S3_FIGHT_MAP_1 = {
    "obstacles": [
        {"filename": "LavaPond1.png",       "x": 760.00,  "y": 560.00, "scale": 0.62},
        {"filename": "Altar1.png",          "x": 320.00,  "y": 320.00, "scale": 0.28},
        {"filename": "Altar2.png",          "x": 1200.00, "y": 800.00, "scale": 0.28},
        {"filename": "BrokenStoneStatue1.png","x": 1200.00,"y": 320.00, "scale": 0.26},
        {"filename": "Coffin1.png",         "x": 320.00,  "y": 820.00, "scale": 0.32},
        {"filename": "LavaStone1.png",      "x": 560.00,  "y": 300.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 960.00,  "y": 820.00, "scale": 0.22},
        {"filename": "Skull1.png",          "x": 560.00,  "y": 820.00, "scale": 0.22},
        {"filename": "Skull2.png",          "x": 960.00,  "y": 300.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 280.00}, {"x": 1220.00,"y": 280.00},
        {"x": 300.00,"y": 840.00}, {"x": 1220.00,"y": 840.00},
        {"x": 560.00,"y": 380.00}, {"x": 960.00,"y": 740.00},
        {"x": 760.00,"y": 200.00}, {"x": 760.00,"y": 920.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S3_FIGHT_MAP_2 = {
    "obstacles": [
        {"filename": "Coffin2.png",         "x": 1220.00, "y": 280.00, "scale": 0.32},
        {"filename": "Coffin1.png",         "x": 320.00,  "y": 820.00, "scale": 0.32},
        {"filename": "Altar2.png",          "x": 300.00,  "y": 320.00, "scale": 0.28},
        {"filename": "Altar1.png",          "x": 1240.00, "y": 800.00, "scale": 0.28},
        {"filename": "LavaStone1.png",      "x": 560.00,  "y": 540.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 960.00,  "y": 540.00, "scale": 0.22},
        {"filename": "Skull3.png",          "x": 760.00,  "y": 320.00, "scale": 0.22},
        {"filename": "Skull1.png",          "x": 760.00,  "y": 760.00, "scale": 0.22},
        {"filename": "BrokenStoneStatue1.png","x": 760.00,"y": 900.00, "scale": 0.26}
    ],
    "enemy_infos": [
        {"x": 280.00,"y": 560.00}, {"x": 1240.00,"y": 560.00},
        {"x": 560.00,"y": 320.00}, {"x": 960.00,"y": 320.00},
        {"x": 560.00,"y": 800.00}, {"x": 960.00,"y": 800.00},
        {"x": 760.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.95, "y_ratio": 0.95}
}

S3_FIGHT_MAP_3 = {
    "obstacles": [
        {"filename": "LavaPond1.png",       "x": 1040.00, "y": 360.00, "scale": 0.60},
        {"filename": "Altar1.png",          "x": 320.00,  "y": 320.00, "scale": 0.28},
        {"filename": "Altar2.png",          "x": 320.00,  "y": 780.00, "scale": 0.28},
        {"filename": "Coffin1.png",         "x": 1180.00, "y": 920.00, "scale": 0.32},
        {"filename": "BrokenStoneStatue1.png","x": 560.00,"y": 900.00, "scale": 0.26},
        {"filename": "Skull2.png",          "x": 960.00,  "y": 760.00, "scale": 0.22},
        {"filename": "LavaStone1.png",      "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Skull1.png",          "x": 1240.00, "y": 540.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 220.00}, {"x": 300.00,"y": 900.00},
        {"x": 1240.00,"y": 220.00},{"x": 1240.00,"y": 900.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 960.00},
        {"x": 520.00,"y": 560.00}, {"x": 980.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.92, "y_ratio": 0.92}
}

S3_FIGHT_MAP_4 = {
    "obstacles": [
        {"filename": "Coffin2.png",         "x": 300.00,  "y": 320.00, "scale": 0.32},
        {"filename": "Coffin1.png",         "x": 1220.00, "y": 800.00, "scale": 0.32},
        {"filename": "Altar1.png",          "x": 520.00,  "y": 280.00, "scale": 0.28},
        {"filename": "Altar2.png",          "x": 1000.00, "y": 820.00, "scale": 0.28},
        {"filename": "LavaStone1.png",      "x": 520.00,  "y": 560.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 1000.00, "y": 560.00, "scale": 0.22},
        {"filename": "Skull3.png",          "x": 760.00,  "y": 420.00, "scale": 0.22},
        {"filename": "Skull2.png",          "x": 760.00,  "y": 700.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 320.00}, {"x": 1000.00,"y": 320.00},
        {"x": 520.00,"y": 800.00}, {"x": 1000.00,"y": 800.00},
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 0.90}
}

S3_FIGHT_MAP_5 = {
    "obstacles": [
        {"filename": "LavaPond1.png",       "x": 520.00,  "y": 760.00, "scale": 0.58},
        {"filename": "LavaPond1.png",       "x": 1000.00, "y": 320.00, "scale": 0.58},
        {"filename": "Altar2.png",          "x": 1240.00, "y": 900.00, "scale": 0.28},
        {"filename": "Altar1.png",          "x": 300.00,  "y": 200.00, "scale": 0.28},
        {"filename": "Skull1.png",          "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "LavaStone1.png",      "x": 320.00,  "y": 900.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 1180.00, "y": 180.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 320.00}, {"x": 1220.00,"y": 320.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00},
        {"x": 980.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.90, "y_ratio": 0.90}
}

S3_FIGHT_MAP_6 = {
    "obstacles": [
        {"filename": "Altar1.png",          "x": 760.00,  "y": 240.00, "scale": 0.30},
        {"filename": "Altar2.png",          "x": 760.00,  "y": 880.00, "scale": 0.30},
        {"filename": "Coffin1.png",         "x": 520.00,  "y": 340.00, "scale": 0.32},
        {"filename": "Coffin2.png",         "x": 1000.00, "y": 780.00, "scale": 0.32},
        {"filename": "Skull1.png",          "x": 300.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Skull2.png",          "x": 1220.00, "y": 560.00, "scale": 0.22},
        {"filename": "LavaStone1.png",      "x": 520.00,  "y": 780.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 1000.00, "y": 340.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 560.00}, {"x": 1000.00,"y": 560.00},
        {"x": 760.00,"y": 420.00}, {"x": 760.00,"y": 700.00},
        {"x": 300.00,"y": 320.00}, {"x": 1220.00,"y": 800.00},
        {"x": 300.00,"y": 800.00}, {"x": 1220.00,"y": 320.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S3_FIGHT_MAP_7 = {
    "obstacles": [
        {"filename": "LavaPond1.png",       "x": 760.00,  "y": 560.00, "scale": 0.60},
        {"filename": "BrokenStoneStatue1.png","x": 320.00,"y": 320.00, "scale": 0.26},
        {"filename": "BrokenStoneStatue1.png","x": 1200.00,"y": 800.00, "scale": 0.26},
        {"filename": "Altar1.png",          "x": 320.00,  "y": 800.00, "scale": 0.28},
        {"filename": "Altar2.png",          "x": 1200.00, "y": 320.00, "scale": 0.28},
        {"filename": "Skull3.png",          "x": 560.00,  "y": 300.00, "scale": 0.22},
        {"filename": "Skull1.png",          "x": 960.00,  "y": 820.00, "scale": 0.22},
        {"filename": "LavaStone1.png",      "x": 560.00,  "y": 820.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 960.00,  "y": 300.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 280.00}, {"x": 1220.00,"y": 280.00},
        {"x": 300.00,"y": 840.00}, {"x": 1220.00,"y": 840.00},
        {"x": 560.00,"y": 380.00}, {"x": 960.00,"y": 740.00},
        {"x": 760.00,"y": 920.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 0.95}
}

S3_FIGHT_MAP_8 = {
    "obstacles": [
        {"filename": "Coffin1.png",         "x": 1180.00, "y": 220.00, "scale": 0.32},
        {"filename": "Coffin2.png",         "x": 360.00,  "y": 900.00, "scale": 0.32},
        {"filename": "Altar2.png",          "x": 300.00,  "y": 300.00, "scale": 0.28},
        {"filename": "Altar1.png",          "x": 1240.00, "y": 820.00, "scale": 0.28},
        {"filename": "LavaStone1.png",      "x": 540.00,  "y": 540.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 980.00,  "y": 540.00, "scale": 0.22},
        {"filename": "Skull2.png",          "x": 760.00,  "y": 360.00, "scale": 0.22},
        {"filename": "Skull3.png",          "x": 760.00,  "y": 740.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 320.00}, {"x": 1000.00,"y": 320.00},
        {"x": 520.00,"y": 800.00}, {"x": 1000.00,"y": 800.00},
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 560.00}, {"x": 760.00,"y": 920.00}
    ],
    "crop_rect": {"x_ratio": 0.96, "y_ratio": 0.92}
}

S3_FIGHT_MAP_9 = {
    "obstacles": [
        {"filename": "LavaPond1.png",       "x": 960.00,  "y": 720.00, "scale": 0.60},
        {"filename": "Altar1.png",          "x": 320.00,  "y": 300.00, "scale": 0.28},
        {"filename": "Altar2.png",          "x": 1240.00, "y": 880.00, "scale": 0.28},
        {"filename": "Coffin1.png",         "x": 1180.00, "y": 260.00, "scale": 0.32},
        {"filename": "Skull1.png",          "x": 540.00,  "y": 900.00, "scale": 0.22},
        {"filename": "Skull2.png",          "x": 980.00,  "y": 260.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 560.00,  "y": 540.00, "scale": 0.22},
        {"filename": "BrokenStoneStatue1.png","x": 760.00,"y": 360.00, "scale": 0.26}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 280.00}, {"x": 1220.00,"y": 280.00},
        {"x": 300.00,"y": 840.00}, {"x": 1220.00,"y": 840.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 960.00},
        {"x": 560.00,"y": 720.00}, {"x": 980.00,"y": 520.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 0.90}
}

S3_FIGHT_MAP_10 = {
    "obstacles": [
        {"filename": "Coffin2.png",         "x": 320.00,  "y": 240.00, "scale": 0.32},
        {"filename": "Coffin1.png",         "x": 1220.00, "y": 900.00, "scale": 0.32},
        {"filename": "Altar2.png",          "x": 520.00,  "y": 320.00, "scale": 0.28},
        {"filename": "Altar1.png",          "x": 1000.00, "y": 820.00, "scale": 0.28},
        {"filename": "LavaStone1.png",      "x": 520.00,  "y": 760.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 1000.00, "y": 380.00, "scale": 0.22},
        {"filename": "Skull1.png",          "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Skull3.png",          "x": 760.00,  "y": 900.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 560.00,"y": 320.00}, {"x": 1000.00,"y": 320.00},
        {"x": 560.00,"y": 800.00}, {"x": 1000.00,"y": 800.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00}
    ],
    "crop_rect": {"x_ratio": 0.90, "y_ratio": 0.95}
}

S3_FIGHT_MAP_11 = {
    "obstacles": [
        {"filename": "LavaPond1.png",       "x": 760.00,  "y": 560.00, "scale": 0.60},
        {"filename": "Altar1.png",          "x": 520.00,  "y": 240.00, "scale": 0.28},
        {"filename": "Altar2.png",          "x": 1000.00, "y": 880.00, "scale": 0.28},
        {"filename": "Skull2.png",          "x": 320.00,  "y": 820.00, "scale": 0.22},
        {"filename": "Skull1.png",          "x": 1200.00, "y": 320.00, "scale": 0.22},
        {"filename": "LavaStone1.png",      "x": 560.00,  "y": 820.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 960.00,  "y": 300.00, "scale": 0.22},
        {"filename": "BrokenStoneStatue1.png","x": 760.00,"y": 920.00, "scale": 0.26}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 300.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 380.00}, {"x": 960.00,"y": 740.00},
        {"x": 760.00,"y": 180.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 0.92}
}

S3_FIGHT_MAP_12 = {
    "obstacles": [
        {"filename": "Coffin1.png",         "x": 1180.00, "y": 900.00, "scale": 0.32},
        {"filename": "Coffin2.png",         "x": 360.00,  "y": 220.00, "scale": 0.32},
        {"filename": "Altar1.png",          "x": 1200.00, "y": 320.00, "scale": 0.28},
        {"filename": "Altar2.png",          "x": 320.00,  "y": 800.00, "scale": 0.28},
        {"filename": "Skull3.png",          "x": 760.00,  "y": 420.00, "scale": 0.22},
        {"filename": "Skull2.png",          "x": 760.00,  "y": 700.00, "scale": 0.22},
        {"filename": "LavaStone1.png",      "x": 520.00,  "y": 560.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 1000.00, "y": 560.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 320.00}, {"x": 1000.00,"y": 320.00},
        {"x": 520.00,"y": 800.00}, {"x": 1000.00,"y": 800.00},
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.95, "y_ratio": 0.90}
}

S3_FIGHT_MAP_13 = {
    "obstacles": [
        {"filename": "LavaPond1.png",       "x": 980.00,  "y": 540.00, "scale": 0.60},
        {"filename": "Altar2.png",          "x": 300.00,  "y": 320.00, "scale": 0.28},
        {"filename": "Altar1.png",          "x": 1240.00, "y": 760.00, "scale": 0.28},
        {"filename": "Coffin2.png",         "x": 320.00,  "y": 860.00, "scale": 0.32},
        {"filename": "Coffin1.png",         "x": 1240.00, "y": 220.00, "scale": 0.32},
        {"filename": "Skull1.png",          "x": 760.00,  "y": 320.00, "scale": 0.22},
        {"filename": "Skull2.png",          "x": 760.00,  "y": 760.00, "scale": 0.22},
        {"filename": "LavaStone1.png",      "x": 560.00,  "y": 560.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 260.00,"y": 540.00}, {"x": 1280.00,"y": 540.00},
        {"x": 560.00,"y": 320.00}, {"x": 960.00,"y": 320.00},
        {"x": 560.00,"y": 760.00}, {"x": 960.00,"y": 760.00},
        {"x": 760.00,"y": 140.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.92, "y_ratio": 0.92}
}

S3_FIGHT_MAP_14 = {
    "obstacles": [
        {"filename": "Coffin1.png",         "x": 1000.00, "y": 280.00, "scale": 0.32},
        {"filename": "Coffin2.png",         "x": 520.00,  "y": 820.00, "scale": 0.32},
        {"filename": "Altar1.png",          "x": 300.00,  "y": 900.00, "scale": 0.28},
        {"filename": "Altar2.png",          "x": 1220.00, "y": 220.00, "scale": 0.28},
        {"filename": "LavaStone1.png",      "x": 540.00,  "y": 360.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 980.00,  "y": 760.00, "scale": 0.22},
        {"filename": "Skull3.png",          "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Skull1.png",          "x": 760.00,  "y": 900.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 300.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00},
        {"x": 760.00,"y": 180.00}
    ],
    "crop_rect": {"x_ratio": 0.96, "y_ratio": 0.96}
}

S3_FIGHT_MAP_15 = {
    "obstacles": [
        {"filename": "LavaPond1.png",       "x": 760.00,  "y": 720.00, "scale": 0.62},
        {"filename": "Altar1.png",          "x": 520.00,  "y": 260.00, "scale": 0.28},
        {"filename": "Altar2.png",          "x": 1000.00, "y": 860.00, "scale": 0.28},
        {"filename": "BrokenStoneStatue1.png","x": 300.00,"y": 540.00, "scale": 0.26},
        {"filename": "Skull1.png",          "x": 1220.00, "y": 540.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 560.00,  "y": 900.00, "scale": 0.22},
        {"filename": "LavaStone1.png",      "x": 960.00,  "y": 360.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 280.00}, {"x": 1220.00,"y": 280.00},
        {"x": 300.00,"y": 880.00}, {"x": 1220.00,"y": 880.00},
        {"x": 760.00,"y": 200.00}, {"x": 760.00,"y": 960.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.90, "y_ratio": 1.0}
}

S3_FIGHT_MAP_16 = {
    "obstacles": [
        {"filename": "Coffin2.png",         "x": 300.00,  "y": 320.00, "scale": 0.32},
        {"filename": "Coffin1.png",         "x": 1220.00, "y": 800.00, "scale": 0.32},
        {"filename": "Altar2.png",          "x": 320.00,  "y": 820.00, "scale": 0.28},
        {"filename": "Altar1.png",          "x": 1200.00, "y": 300.00, "scale": 0.28},
        {"filename": "Skull2.png",          "x": 760.00,  "y": 420.00, "scale": 0.22},
        {"filename": "Skull3.png",          "x": 760.00,  "y": 700.00, "scale": 0.22},
        {"filename": "LavaStone1.png",      "x": 520.00,  "y": 560.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 1000.00, "y": 560.00, "scale": 0.22},
        {"filename": "BrokenStoneStatue1.png","x": 760.00,"y": 920.00, "scale": 0.26}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 320.00}, {"x": 1000.00,"y": 320.00},
        {"x": 520.00,"y": 800.00}, {"x": 1000.00,"y": 800.00},
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00}
    ],
    "crop_rect": {"x_ratio": 0.86, "y_ratio": 1.08}
}

S3_FIGHT_MAP_17 = {
    "obstacles": [
        {"filename": "LavaPond1.png",       "x": 540.00,  "y": 360.00, "scale": 0.60},
        {"filename": "LavaPond1.png",       "x": 1040.00, "y": 760.00, "scale": 0.58},
        {"filename": "Skull1.png",          "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Altar1.png",          "x": 320.00,  "y": 900.00, "scale": 0.28},
        {"filename": "Altar2.png",          "x": 1200.00, "y": 220.00, "scale": 0.28},
        {"filename": "Coffin1.png",         "x": 320.00,  "y": 220.00, "scale": 0.32},
        {"filename": "Coffin2.png",         "x": 1200.00, "y": 900.00, "scale": 0.32}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 300.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 1.10, "y_ratio": 0.86}
}

S3_FIGHT_MAP_18 = {
    "obstacles": [
        {"filename": "Coffin2.png",         "x": 1180.00, "y": 760.00, "scale": 0.32},
        {"filename": "Coffin1.png",         "x": 360.00,  "y": 300.00, "scale": 0.32},
        {"filename": "Altar1.png",          "x": 1000.00, "y": 280.00, "scale": 0.28},
        {"filename": "Altar2.png",          "x": 520.00,  "y": 800.00, "scale": 0.28},
        {"filename": "LavaStone1.png",      "x": 560.00,  "y": 360.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 960.00,  "y": 760.00, "scale": 0.22},
        {"filename": "Skull2.png",          "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Skull3.png",          "x": 760.00,  "y": 900.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00},
        {"x": 760.00,"y": 180.00}
    ],
    "crop_rect": {"x_ratio": 0.94, "y_ratio": 0.94}
}

S3_FIGHT_MAP_19 = {
    "obstacles": [
        {"filename": "LavaPond1.png",       "x": 760.00,  "y": 560.00, "scale": 0.60},
        {"filename": "Altar2.png",          "x": 300.00,  "y": 220.00, "scale": 0.28},
        {"filename": "Altar1.png",          "x": 1220.00, "y": 900.00, "scale": 0.28},
        {"filename": "Coffin1.png",         "x": 300.00,  "y": 900.00, "scale": 0.32},
        {"filename": "Coffin2.png",         "x": 1220.00, "y": 220.00, "scale": 0.32},
        {"filename": "LavaStone2.png",      "x": 560.00,  "y": 300.00, "scale": 0.22},
        {"filename": "LavaStone1.png",      "x": 960.00,  "y": 820.00, "scale": 0.22},
        {"filename": "Skull1.png",          "x": 760.00,  "y": 920.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 300.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 380.00}, {"x": 960.00,"y": 740.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.90, "y_ratio": 0.90}
}

S3_FIGHT_MAP_20 = {
    "obstacles": [
        {"filename": "LavaPond1.png",       "x": 520.00,  "y": 320.00, "scale": 0.58},
        {"filename": "LavaPond1.png",       "x": 1000.00, "y": 800.00, "scale": 0.58},
        {"filename": "Altar1.png",          "x": 320.00,  "y": 900.00, "scale": 0.28},
        {"filename": "Altar2.png",          "x": 1200.00, "y": 220.00, "scale": 0.28},
        {"filename": "Skull2.png",          "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "LavaStone1.png",      "x": 560.00,  "y": 920.00, "scale": 0.22},
        {"filename": "LavaStone2.png",      "x": 960.00,  "y": 360.00, "scale": 0.22},
        {"filename": "BrokenStoneStatue1.png","x": 760.00,"y": 140.00, "scale": 0.26},
        {"filename": "Skull3.png",          "x": 760.00,  "y": 900.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 540.00}, {"x": 960.00,"y": 540.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 960.00}
    ],
    "crop_rect": {"x_ratio": 1.0, "y_ratio": 1.0}
}

S3_FIGHT_MAP_21 = {
    "obstacles": [
        {"filename": "LavaPond1.png", "x": 760.00,  "y": 560.00, "scale": 0.60},
        {"filename": "Altar1.png",    "x": 320.00,  "y": 320.00, "scale": 0.28},
        {"filename": "Altar2.png",    "x": 1200.00, "y": 800.00, "scale": 0.28},
        {"filename": "Coffin1.png",   "x": 320.00,  "y": 840.00, "scale": 0.32},
        {"filename": "Coffin2.png",   "x": 1200.00, "y": 280.00, "scale": 0.32},
        {"filename": "LavaStone1.png","x": 560.00,  "y": 320.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 960.00,  "y": 800.00, "scale": 0.22},
        {"filename": "Skull1.png",    "x": 560.00,  "y": 820.00, "scale": 0.22},
        {"filename": "Skull2.png",    "x": 960.00,  "y": 300.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 860.00}, {"x": 1220.00,"y": 860.00},
        {"x": 560.00,"y": 360.00}, {"x": 960.00,"y": 760.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 1.00, "y_ratio": 1.00}
}

S3_FIGHT_MAP_22 = {
    "obstacles": [
        {"filename": "Coffin1.png",   "x": 1220.00, "y": 260.00, "scale": 0.32},
        {"filename": "Coffin2.png",   "x": 320.00,  "y": 840.00, "scale": 0.32},
        {"filename": "Altar2.png",    "x": 320.00,  "y": 320.00, "scale": 0.28},
        {"filename": "Altar1.png",    "x": 1220.00, "y": 820.00, "scale": 0.28},
        {"filename": "LavaStone1.png","x": 560.00,  "y": 540.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 960.00,  "y": 540.00, "scale": 0.22},
        {"filename": "Skull2.png",    "x": 760.00,  "y": 360.00, "scale": 0.22},
        {"filename": "Skull3.png",    "x": 760.00,  "y": 740.00, "scale": 0.22},
        {"filename": "BrokenStoneStatue1.png","x":760.00,"y": 900.00,"scale":0.26}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 320.00}, {"x": 1000.00,"y": 320.00},
        {"x": 520.00,"y": 800.00}, {"x": 1000.00,"y": 800.00},
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 560.00}, {"x": 760.00,"y": 160.00}
    ],
    "crop_rect": {"x_ratio": 0.96, "y_ratio": 0.94}
}

S3_FIGHT_MAP_23 = {
    "obstacles": [
        {"filename": "LavaPond1.png", "x": 980.00,  "y": 360.00, "scale": 0.58},
        {"filename": "Altar1.png",    "x": 320.00,  "y": 320.00, "scale": 0.28},
        {"filename": "Altar2.png",    "x": 320.00,  "y": 780.00, "scale": 0.28},
        {"filename": "Coffin1.png",   "x": 1180.00, "y": 920.00, "scale": 0.32},
        {"filename": "BrokenStoneStatue1.png","x":560.00,"y": 900.00,"scale":0.26},
        {"filename": "Skull2.png",    "x": 960.00,  "y": 760.00, "scale": 0.22},
        {"filename": "LavaStone1.png","x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Skull1.png",    "x": 1240.00, "y": 540.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 220.00}, {"x": 300.00,"y": 900.00},
        {"x": 1240.00,"y": 220.00},{"x": 1240.00,"y": 900.00},
        {"x": 520.00,"y": 560.00}, {"x": 980.00,"y": 560.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 960.00}
    ],
    "crop_rect": {"x_ratio": 0.92, "y_ratio": 0.92}
}

S3_FIGHT_MAP_24 = {
    "obstacles": [
        {"filename": "Coffin2.png",   "x": 320.00,  "y": 320.00, "scale": 0.32},
        {"filename": "Coffin1.png",   "x": 1220.00, "y": 800.00, "scale": 0.32},
        {"filename": "Altar1.png",    "x": 520.00,  "y": 280.00, "scale": 0.28},
        {"filename": "Altar2.png",    "x": 1000.00, "y": 820.00, "scale": 0.28},
        {"filename": "LavaStone1.png","x": 520.00,  "y": 560.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 1000.00, "y": 560.00, "scale": 0.22},
        {"filename": "Skull3.png",    "x": 760.00,  "y": 420.00, "scale": 0.22},
        {"filename": "Skull2.png",    "x": 760.00,  "y": 700.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 320.00}, {"x": 1000.00,"y": 320.00},
        {"x": 520.00,"y": 800.00}, {"x": 1000.00,"y": 800.00},
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 560.00}, {"x": 760.00,"y": 920.00}
    ],
    "crop_rect": {"x_ratio": 1.00, "y_ratio": 0.92}
}

S3_FIGHT_MAP_25 = {
    "obstacles": [
        {"filename": "LavaPond1.png", "x": 520.00,  "y": 760.00, "scale": 0.58},
        {"filename": "LavaPond1.png", "x": 1000.00, "y": 320.00, "scale": 0.58},
        {"filename": "Altar2.png",    "x": 1240.00, "y": 900.00, "scale": 0.28},
        {"filename": "Altar1.png",    "x": 300.00,  "y": 200.00, "scale": 0.28},
        {"filename": "Skull1.png",    "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "LavaStone1.png","x": 320.00,  "y": 900.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 1180.00, "y": 180.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 320.00}, {"x": 1220.00,"y": 320.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00},
        {"x": 980.00,"y": 560.00}, {"x": 540.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.92, "y_ratio": 0.92}
}

S3_FIGHT_MAP_26 = {
    "obstacles": [
        {"filename": "Altar1.png",    "x": 760.00,  "y": 240.00, "scale": 0.30},
        {"filename": "Altar2.png",    "x": 760.00,  "y": 880.00, "scale": 0.30},
        {"filename": "Coffin1.png",   "x": 520.00,  "y": 340.00, "scale": 0.32},
        {"filename": "Coffin2.png",   "x": 1000.00, "y": 780.00, "scale": 0.32},
        {"filename": "Skull1.png",    "x": 300.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Skull2.png",    "x": 1220.00, "y": 560.00, "scale": 0.22},
        {"filename": "LavaStone1.png","x": 520.00,  "y": 780.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 1000.00, "y": 340.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 560.00}, {"x": 1000.00,"y": 560.00},
        {"x": 760.00,"y": 420.00}, {"x": 760.00,"y": 700.00},
        {"x": 300.00,"y": 320.00}, {"x": 1220.00,"y": 800.00},
        {"x": 300.00,"y": 800.00}, {"x": 1220.00,"y": 320.00}
    ],
    "crop_rect": {"x_ratio": 1.02, "y_ratio": 1.00}
}

S3_FIGHT_MAP_27 = {
    "obstacles": [
        {"filename": "LavaPond1.png", "x": 760.00,  "y": 560.00, "scale": 0.60},
        {"filename": "BrokenStoneStatue1.png","x": 320.00,"y": 320.00,"scale":0.26},
        {"filename": "BrokenStoneStatue1.png","x": 1200.00,"y": 800.00,"scale":0.26},
        {"filename": "Altar1.png",    "x": 320.00,  "y": 800.00, "scale": 0.28},
        {"filename": "Altar2.png",    "x": 1200.00, "y": 320.00, "scale": 0.28},
        {"filename": "Skull3.png",    "x": 560.00,  "y": 300.00, "scale": 0.22},
        {"filename": "Skull1.png",    "x": 960.00,  "y": 820.00, "scale": 0.22},
        {"filename": "LavaStone1.png","x": 560.00,  "y": 820.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 960.00,  "y": 300.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 280.00}, {"x": 1220.00,"y": 280.00},
        {"x": 300.00,"y": 840.00}, {"x": 1220.00,"y": 840.00},
        {"x": 560.00,"y": 380.00}, {"x": 960.00,"y": 740.00},
        {"x": 760.00,"y": 920.00}, {"x": 760.00,"y": 200.00}
    ],
    "crop_rect": {"x_ratio": 1.00, "y_ratio": 0.96}
}

S3_FIGHT_MAP_28 = {
    "obstacles": [
        {"filename": "Coffin1.png",   "x": 1180.00, "y": 220.00, "scale": 0.32},
        {"filename": "Coffin2.png",   "x": 360.00,  "y": 900.00, "scale": 0.32},
        {"filename": "Altar2.png",    "x": 300.00,  "y": 300.00, "scale": 0.28},
        {"filename": "Altar1.png",    "x": 1240.00, "y": 820.00, "scale": 0.28},
        {"filename": "LavaStone1.png","x": 540.00,  "y": 540.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 980.00,  "y": 540.00, "scale": 0.22},
        {"filename": "Skull2.png",    "x": 760.00,  "y": 360.00, "scale": 0.22},
        {"filename": "Skull3.png",    "x": 760.00,  "y": 740.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 320.00}, {"x": 1000.00,"y": 320.00},
        {"x": 520.00,"y": 800.00}, {"x": 1000.00,"y": 800.00},
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 560.00}, {"x": 760.00,"y": 920.00}
    ],
    "crop_rect": {"x_ratio": 0.96, "y_ratio": 0.92}
}

S3_FIGHT_MAP_29 = {
    "obstacles": [
        {"filename": "LavaPond1.png", "x": 960.00,  "y": 720.00, "scale": 0.60},
        {"filename": "Altar1.png",    "x": 320.00,  "y": 300.00, "scale": 0.28},
        {"filename": "Altar2.png",    "x": 1240.00, "y": 880.00, "scale": 0.28},
        {"filename": "Coffin1.png",   "x": 1180.00, "y": 260.00, "scale": 0.32},
        {"filename": "Skull1.png",    "x": 540.00,  "y": 900.00, "scale": 0.22},
        {"filename": "Skull2.png",    "x": 980.00,  "y": 260.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 560.00,  "y": 540.00, "scale": 0.22},
        {"filename": "BrokenStoneStatue1.png","x":760.00,"y": 360.00,"scale":0.26}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 280.00}, {"x": 1220.00,"y": 280.00},
        {"x": 300.00,"y": 840.00}, {"x": 1220.00,"y": 840.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 960.00},
        {"x": 560.00,"y": 720.00}, {"x": 980.00,"y": 520.00}
    ],
    "crop_rect": {"x_ratio": 1.00, "y_ratio": 0.92}
}

S3_FIGHT_MAP_30 = {
    "obstacles": [
        {"filename": "Coffin2.png",   "x": 320.00,  "y": 240.00, "scale": 0.32},
        {"filename": "Coffin1.png",   "x": 1220.00, "y": 900.00, "scale": 0.32},
        {"filename": "Altar2.png",    "x": 520.00,  "y": 320.00, "scale": 0.28},
        {"filename": "Altar1.png",    "x": 1000.00, "y": 820.00, "scale": 0.28},
        {"filename": "LavaStone1.png","x": 520.00,  "y": 760.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 1000.00, "y": 380.00, "scale": 0.22},
        {"filename": "Skull1.png",    "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Skull3.png",    "x": 760.00,  "y": 900.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 560.00,"y": 320.00}, {"x": 1000.00,"y": 320.00},
        {"x": 560.00,"y": 800.00}, {"x": 1000.00,"y": 800.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00}
    ],
    "crop_rect": {"x_ratio": 0.92, "y_ratio": 0.96}
}

S3_FIGHT_MAP_31 = {
    "obstacles": [
        {"filename": "LavaPond1.png", "x": 760.00,  "y": 560.00, "scale": 0.60},
        {"filename": "Altar1.png",    "x": 520.00,  "y": 240.00, "scale": 0.28},
        {"filename": "Altar2.png",    "x": 1000.00, "y": 880.00, "scale": 0.28},
        {"filename": "Skull2.png",    "x": 320.00,  "y": 820.00, "scale": 0.22},
        {"filename": "Skull1.png",    "x": 1200.00, "y": 320.00, "scale": 0.22},
        {"filename": "LavaStone1.png","x": 560.00,  "y": 820.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 960.00,  "y": 300.00, "scale": 0.22},
        {"filename": "BrokenStoneStatue1.png","x":760.00,"y": 920.00,"scale":0.26}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 300.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 380.00}, {"x": 960.00,"y": 740.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.98, "y_ratio": 0.94}
}

S3_FIGHT_MAP_32 = {
    "obstacles": [
        {"filename": "Coffin1.png",   "x": 1180.00, "y": 900.00, "scale": 0.32},
        {"filename": "Coffin2.png",   "x": 360.00,  "y": 220.00, "scale": 0.32},
        {"filename": "Altar1.png",    "x": 1200.00, "y": 320.00, "scale": 0.28},
        {"filename": "Altar2.png",    "x": 320.00,  "y": 800.00, "scale": 0.28},
        {"filename": "Skull3.png",    "x": 760.00,  "y": 420.00, "scale": 0.22},
        {"filename": "Skull2.png",    "x": 760.00,  "y": 700.00, "scale": 0.22},
        {"filename": "LavaStone1.png","x": 520.00,  "y": 560.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 1000.00, "y": 560.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 320.00}, {"x": 1000.00,"y": 320.00},
        {"x": 520.00,"y": 800.00}, {"x": 1000.00,"y": 800.00},
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00}
    ],
    "crop_rect": {"x_ratio": 0.94, "y_ratio": 0.92}
}

S3_FIGHT_MAP_33 = {
    "obstacles": [
        {"filename": "LavaPond1.png", "x": 980.00,  "y": 540.00, "scale": 0.60},
        {"filename": "Altar2.png",    "x": 300.00,  "y": 320.00, "scale": 0.28},
        {"filename": "Altar1.png",    "x": 1240.00, "y": 760.00, "scale": 0.28},
        {"filename": "Coffin2.png",   "x": 320.00,  "y": 860.00, "scale": 0.32},
        {"filename": "Coffin1.png",   "x": 1240.00, "y": 220.00, "scale": 0.32},
        {"filename": "Skull1.png",    "x": 760.00,  "y": 320.00, "scale": 0.22},
        {"filename": "Skull2.png",    "x": 760.00,  "y": 760.00, "scale": 0.22},
        {"filename": "LavaStone1.png","x": 560.00,  "y": 560.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 260.00,"y": 540.00}, {"x": 1280.00,"y": 540.00},
        {"x": 560.00,"y": 320.00}, {"x": 960.00,"y": 320.00},
        {"x": 560.00,"y": 760.00}, {"x": 960.00,"y": 760.00},
        {"x": 760.00,"y": 140.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.92, "y_ratio": 0.92}
}

S3_FIGHT_MAP_34 = {
    "obstacles": [
        {"filename": "Coffin1.png",   "x": 1000.00, "y": 280.00, "scale": 0.32},
        {"filename": "Coffin2.png",   "x": 520.00,  "y": 820.00, "scale": 0.32},
        {"filename": "Altar1.png",    "x": 300.00,  "y": 900.00, "scale": 0.28},
        {"filename": "Altar2.png",    "x": 1220.00, "y": 220.00, "scale": 0.28},
        {"filename": "LavaStone1.png","x": 540.00,  "y": 360.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 980.00,  "y": 760.00, "scale": 0.22},
        {"filename": "Skull3.png",    "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Skull1.png",    "x": 760.00,  "y": 900.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 300.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.96, "y_ratio": 0.96}
}

S3_FIGHT_MAP_35 = {
    "obstacles": [
        {"filename": "LavaPond1.png", "x": 760.00,  "y": 720.00, "scale": 0.62},
        {"filename": "Altar1.png",    "x": 520.00,  "y": 260.00, "scale": 0.28},
        {"filename": "Altar2.png",    "x": 1000.00, "y": 860.00, "scale": 0.28},
        {"filename": "BrokenStoneStatue1.png","x":300.00,"y": 540.00,"scale":0.26},
        {"filename": "Skull1.png",    "x": 1220.00, "y": 540.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 560.00,  "y": 900.00, "scale": 0.22},
        {"filename": "LavaStone1.png","x": 960.00,  "y": 360.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 280.00}, {"x": 1220.00,"y": 280.00},
        {"x": 300.00,"y": 880.00}, {"x": 1220.00,"y": 880.00},
        {"x": 760.00,"y": 200.00}, {"x": 760.00,"y": 960.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00}
    ],
    "crop_rect": {"x_ratio": 0.92, "y_ratio": 1.00}
}

S3_FIGHT_MAP_36 = {
    "obstacles": [
        {"filename": "Coffin2.png",   "x": 300.00,  "y": 320.00, "scale": 0.32},
        {"filename": "Coffin1.png",   "x": 1220.00, "y": 800.00, "scale": 0.32},
        {"filename": "Altar2.png",    "x": 320.00,  "y": 820.00, "scale": 0.28},
        {"filename": "Altar1.png",    "x": 1200.00, "y": 300.00, "scale": 0.28},
        {"filename": "Skull2.png",    "x": 760.00,  "y": 420.00, "scale": 0.22},
        {"filename": "Skull3.png",    "x": 760.00,  "y": 700.00, "scale": 0.22},
        {"filename": "LavaStone1.png","x": 520.00,  "y": 560.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 1000.00, "y": 560.00, "scale": 0.22},
        {"filename": "BrokenStoneStatue1.png","x":760.00,"y": 920.00,"scale":0.26}
    ],
    "enemy_infos": [
        {"x": 520.00,"y": 320.00}, {"x": 1000.00,"y": 320.00},
        {"x": 520.00,"y": 800.00}, {"x": 1000.00,"y": 800.00},
        {"x": 300.00,"y": 560.00}, {"x": 1220.00,"y": 560.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 960.00}
    ],
    "crop_rect": {"x_ratio": 0.88, "y_ratio": 1.04}
}

S3_FIGHT_MAP_37 = {
    "obstacles": [
        {"filename": "LavaPond1.png", "x": 540.00,  "y": 360.00, "scale": 0.60},
        {"filename": "LavaPond1.png", "x": 1040.00, "y": 760.00, "scale": 0.58},
        {"filename": "Skull1.png",    "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Altar1.png",    "x": 320.00,  "y": 900.00, "scale": 0.28},
        {"filename": "Altar2.png",    "x": 1200.00, "y": 220.00, "scale": 0.28},
        {"filename": "Coffin1.png",   "x": 320.00,  "y": 220.00, "scale": 0.32},
        {"filename": "Coffin2.png",   "x": 1200.00, "y": 900.00, "scale": 0.32}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 300.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00},
        {"x": 760.00,"y": 160.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 1.06, "y_ratio": 0.90}
}

S3_FIGHT_MAP_38 = {
    "obstacles": [
        {"filename": "Coffin2.png",   "x": 1180.00, "y": 760.00, "scale": 0.32},
        {"filename": "Coffin1.png",   "x": 360.00,  "y": 300.00, "scale": 0.32},
        {"filename": "Altar1.png",    "x": 1000.00, "y": 280.00, "scale": 0.28},
        {"filename": "Altar2.png",    "x": 520.00,  "y": 800.00, "scale": 0.28},
        {"filename": "LavaStone1.png","x": 560.00,  "y": 360.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 960.00,  "y": 760.00, "scale": 0.22},
        {"filename": "Skull2.png",    "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "Skull3.png",    "x": 760.00,  "y": 900.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 560.00}, {"x": 960.00,"y": 560.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 960.00}
    ],
    "crop_rect": {"x_ratio": 0.96, "y_ratio": 0.96}
}

S3_FIGHT_MAP_39 = {
    "obstacles": [
        {"filename": "LavaPond1.png", "x": 760.00,  "y": 560.00, "scale": 0.60},
        {"filename": "Altar2.png",    "x": 300.00,  "y": 220.00, "scale": 0.28},
        {"filename": "Altar1.png",    "x": 1220.00, "y": 900.00, "scale": 0.28},
        {"filename": "Coffin1.png",   "x": 300.00,  "y": 900.00, "scale": 0.32},
        {"filename": "Coffin2.png",   "x": 1220.00, "y": 220.00, "scale": 0.32},
        {"filename": "LavaStone2.png","x": 560.00,  "y": 300.00, "scale": 0.22},
        {"filename": "LavaStone1.png","x": 960.00,  "y": 820.00, "scale": 0.22},
        {"filename": "Skull1.png",    "x": 760.00,  "y": 920.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 300.00}, {"x": 1220.00,"y": 300.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 380.00}, {"x": 960.00,"y": 740.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 940.00}
    ],
    "crop_rect": {"x_ratio": 0.92, "y_ratio": 0.92}
}

S3_FIGHT_MAP_40 = {
    "obstacles": [
        {"filename": "LavaPond1.png", "x": 520.00,  "y": 320.00, "scale": 0.58},
        {"filename": "LavaPond1.png", "x": 1000.00, "y": 800.00, "scale": 0.58},
        {"filename": "Altar1.png",    "x": 320.00,  "y": 900.00, "scale": 0.28},
        {"filename": "Altar2.png",    "x": 1200.00, "y": 220.00, "scale": 0.28},
        {"filename": "Skull2.png",    "x": 760.00,  "y": 560.00, "scale": 0.22},
        {"filename": "LavaStone1.png","x": 560.00,  "y": 920.00, "scale": 0.22},
        {"filename": "LavaStone2.png","x": 960.00,  "y": 360.00, "scale": 0.22},
        {"filename": "BrokenStoneStatue1.png","x":760.00,"y": 140.00,"scale":0.26},
        {"filename": "Skull3.png",    "x": 760.00,  "y": 900.00, "scale": 0.22}
    ],
    "enemy_infos": [
        {"x": 300.00,"y": 260.00}, {"x": 1220.00,"y": 260.00},
        {"x": 300.00,"y": 820.00}, {"x": 1220.00,"y": 820.00},
        {"x": 560.00,"y": 540.00}, {"x": 960.00,"y": 540.00},
        {"x": 760.00,"y": 180.00}, {"x": 760.00,"y": 960.00}
    ],
    "crop_rect": {"x_ratio": 1.00, "y_ratio": 1.00}
}

S3_FIGHT_DEBUG = { # 디버그
    "obstacles": [
        {"filename": "Altar1.png", "x": 100.00, "y": 100.00, "scale": 0.3}
    ],
    "enemy_infos": [
    ],
    "crop_rect": {"x_ratio": 0.4, "y_ratio": 0.4}
}










# S1_FIGHT_MAPS = [
#     S1_FIGHT_MAP_1, S1_FIGHT_MAP_2, S1_FIGHT_MAP_3, S1_FIGHT_MAP_4, S1_FIGHT_MAP_5,
#     S1_FIGHT_MAP_6, S1_FIGHT_MAP_7, S1_FIGHT_MAP_8, S1_FIGHT_MAP_9, S1_FIGHT_MAP_10,
#     S1_FIGHT_MAP_11, S1_FIGHT_MAP_12, S1_FIGHT_MAP_13, S1_FIGHT_MAP_14, S1_FIGHT_MAP_15,
#     S1_FIGHT_MAP_16, S1_FIGHT_MAP_17, S1_FIGHT_MAP_18, S1_FIGHT_MAP_19, S1_FIGHT_MAP_20,
#     S1_FIGHT_MAP_21, S1_FIGHT_MAP_22, S1_FIGHT_MAP_23, S1_FIGHT_MAP_24, S1_FIGHT_MAP_25,
#     S1_FIGHT_MAP_26, S1_FIGHT_MAP_27, S1_FIGHT_MAP_28, S1_FIGHT_MAP_29, S1_FIGHT_MAP_30,
#     S1_FIGHT_MAP_31, S1_FIGHT_MAP_32, S1_FIGHT_MAP_33, S1_FIGHT_MAP_34, S1_FIGHT_MAP_35,
#     S1_FIGHT_MAP_36, S1_FIGHT_MAP_37, S1_FIGHT_MAP_38, S1_FIGHT_MAP_39, S1_FIGHT_MAP_40
# ]
S1_FIGHT_MAPS = [S1_FIGHT_DEBUG]
S2_FIGHT_MAPS = [
    S2_FIGHT_MAP_1, S2_FIGHT_MAP_2, S2_FIGHT_MAP_3, S2_FIGHT_MAP_4, S2_FIGHT_MAP_5,
    S2_FIGHT_MAP_6, S2_FIGHT_MAP_7, S2_FIGHT_MAP_8, S2_FIGHT_MAP_9, S2_FIGHT_MAP_10,
    S2_FIGHT_MAP_11, S2_FIGHT_MAP_12, S2_FIGHT_MAP_13, S2_FIGHT_MAP_14, S2_FIGHT_MAP_15,
    S2_FIGHT_MAP_16, S2_FIGHT_MAP_17, S2_FIGHT_MAP_18, S2_FIGHT_MAP_19, S2_FIGHT_MAP_20,
    S2_FIGHT_MAP_21, S2_FIGHT_MAP_22, S2_FIGHT_MAP_23, S2_FIGHT_MAP_24, S2_FIGHT_MAP_25,
    S2_FIGHT_MAP_26, S2_FIGHT_MAP_27, S2_FIGHT_MAP_28, S2_FIGHT_MAP_29, S2_FIGHT_MAP_30,
    S2_FIGHT_MAP_31, S2_FIGHT_MAP_32, S2_FIGHT_MAP_33, S2_FIGHT_MAP_34, S2_FIGHT_MAP_35,
    S2_FIGHT_MAP_36, S2_FIGHT_MAP_37, S2_FIGHT_MAP_38, S2_FIGHT_MAP_39, S2_FIGHT_MAP_40
]

S3_FIGHT_MAPS = [
    S3_FIGHT_MAP_1, S3_FIGHT_MAP_2, S3_FIGHT_MAP_3, S3_FIGHT_MAP_4, S3_FIGHT_MAP_5,
    S3_FIGHT_MAP_6, S3_FIGHT_MAP_7, S3_FIGHT_MAP_8, S3_FIGHT_MAP_9, S3_FIGHT_MAP_10,
    S3_FIGHT_MAP_11, S3_FIGHT_MAP_12, S3_FIGHT_MAP_13, S3_FIGHT_MAP_14, S3_FIGHT_MAP_15,
    S3_FIGHT_MAP_16, S3_FIGHT_MAP_17, S3_FIGHT_MAP_18, S3_FIGHT_MAP_19, S3_FIGHT_MAP_20,
    S3_FIGHT_MAP_21, S3_FIGHT_MAP_22, S3_FIGHT_MAP_23, S3_FIGHT_MAP_24, S3_FIGHT_MAP_25,
    S3_FIGHT_MAP_26, S3_FIGHT_MAP_27, S3_FIGHT_MAP_28, S3_FIGHT_MAP_29, S3_FIGHT_MAP_30,
    S3_FIGHT_MAP_31, S3_FIGHT_MAP_32, S3_FIGHT_MAP_33, S3_FIGHT_MAP_34, S3_FIGHT_MAP_35,
    S3_FIGHT_MAP_36, S3_FIGHT_MAP_37, S3_FIGHT_MAP_38, S3_FIGHT_MAP_39, S3_FIGHT_MAP_40
]

MAPS = [START_MAP, END_MAP, ACQUIRE_MAP_1, ACQUIRE_MAP_2, ACQUIRE_MAP_3]
BOSS_MAPS = [BOSS_MAP_1, BOSS_MAP_2, BOSS_MAP_3]
FIGHT_MAPS = S1_FIGHT_MAPS
