def load_obj(filename):
    vertices = []
    faces = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.split('#')[0].strip()
                if not line:
                    continue
                parts = line.split()
                if not parts:
                    continue
                if parts[0] == 'v':
                    vertices.append([float(parts[1]), float(parts[2]), float(parts[3]), 1.0])
                elif parts[0] == 'f':
                    face_indices = []
                    for p in parts[1:]:
                        face_indices.append(int(p.split('/')[0]) - 1)
                    faces.append(face_indices)
        return vertices, faces
    except FileNotFoundError:
        print(f"OBJ 파일을 찾을 수 없습니다: {filename}")
        return [], []
