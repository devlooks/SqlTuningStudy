import re

file_path = r'C:\devLab\SqlTuningStudy\practice\SQLP_실기_2회독_통합패턴맵_v2_3_최종확정.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# O01
content = re.sub(
    r'(\| O01 \|.*?)숙달 \([^\)]+\)(.*?)', 
    r'\1숙달 (2026-09-06) — INDEX_DESC 스캔 방향 일치 완벽\2', 
    content, count=1
)
# P01
content = re.sub(
    r'(\| P01 \|.*?)숙달 \([^\)]+\)(.*?)', 
    r'\1숙달 (2026-09-06)\2', 
    content, count=1
)
# J04
content = re.sub(
    r'(\| J04 \|.*?)숙달 \([^\)]+\).*?(\|)', 
    r'\1부분숙달 (2026-09-06, 오답일 2026-09-06) — Driving 선정은 완벽하나 조인통로 인덱스 선두 조인키 누락 재발 \2', 
    content, count=1
)
# J07
content = re.sub(
    r'(\| J07 \|.*?)숙달 \([^\)]+\).*?(\|)', 
    r'\1숙달 (2026-09-06) — EXISTS 세미 관계 유지 및 1:N 증폭 제거 완벽 \2', 
    content, count=1
)
# Q02
content = re.sub(
    r'(\| Q02 \|.*?)부분숙달 \([^\)]+\).*?(\|)', 
    r'\1숙달 (2026-09-06) — UNNEST NL_SJ 힌트 스스로 보완하여 완벽 달성 \2', 
    content, count=1
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Pattern Map Updated')
