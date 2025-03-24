from math import radians, sin, cos, sqrt, atan2

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    두 지점 간의 거리를 계산합니다 (Haversine 공식 사용).
    
    Args:
        lat1: 첫 번째 지점의 위도
        lon1: 첫 번째 지점의 경도
        lat2: 두 번째 지점의 위도
        lon2: 두 번째 지점의 경도
        
    Returns:
        float: 두 지점 간의 거리 (km)
    """
    R = 6371  # 지구의 반경 (km)
    
    # 위도와 경도를 라디안으로 변환
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # 위도와 경도의 차이
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine 공식
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # 거리 계산 (km)
    distance = R * c
    
    return distance 