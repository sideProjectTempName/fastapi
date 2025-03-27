"""
데이터베이스 쿼리 모음
"""

from typing import List

def get_tourist_spots_query(category_patterns: List[str]) -> str:
    """관광지와 음식점 데이터를 가져오는 쿼리"""
    like_conditions = " OR ".join(["c.category_code LIKE %s" for _ in category_patterns])
    # 음식점에서 'A05020900'과 'A05021000'은 제외 (카페,클럽)
    return f"""
        SELECT 
            d.destination_id,
            d.name,
            d.addr1,
            d.addr2,
            d.latitude,
            d.longitude,
            d.content_id,
            c.category_code,
            c.name as category_name,
            CASE 
                WHEN c.category_code LIKE 'A05%%' THEN 'restaurant'
                ELSE 'tourist_spot'
            END as type
        FROM destination d
        JOIN category c ON d.category_id = c.category_id
        JOIN address a ON d.address_id = a.address_id
        WHERE a.area_code = %s
        AND a.sigungu_code = %s
        AND ({like_conditions}
            OR c.category_code LIKE 'A0502%%'
            AND c.category_code NOT IN ('A05020900', 'A05021000') 
            )
        AND d.latitude IS NOT NULL 
        AND d.longitude IS NOT NULL
        ORDER BY RANDOM();
    """

def get_accommodations_query() -> str:
    """숙소 데이터를 가져오는 쿼리"""
    return """
        SELECT 
            d.destination_id,
            d.name,
            d.addr1,
            d.addr2,
            d.latitude,
            d.longitude,
            d.content_id
        FROM destination d
        JOIN category c ON d.category_id = c.category_id
        JOIN address a ON d.address_id = a.address_id
        WHERE a.area_code = %s
        AND a.sigungu_code = %s
        AND c.category_code LIKE 'B02%%'
        AND d.latitude IS NOT NULL 
        AND d.longitude IS NOT NULL
        ORDER BY RANDOM()
        LIMIT 5;
    """ 