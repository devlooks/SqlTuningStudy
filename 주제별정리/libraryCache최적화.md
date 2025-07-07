📌 라이브러리 캐시 최적화 – 세부 보완 완전판

[비용 기반 옵티마이저]
비용: SQL 실행 시 사용될 리소스 추정치
→ 단순 시간이 아닌 CPU, I/O 연산 횟수 기반

옵티마이저가 사용하는 통계:
테이블/컬럼/인덱스 통계
시스템 파라미터 (optimizer_index_cost_adj 등)

실행 계획 선택 기준:
다양한 실행 계획을 생성하고 최소 비용 경로 선택

[오브젝트 통계 항목]
테이블 통계:
- 레코드 수 (NUM_ROWS)
- 블록 수 (BLOCKS)
- 평균 행 길이 (AVG_ROW_LEN)

컬럼 통계:
- 고유 값 수 (NUM_DISTINCT)
- NULL 비율 (NUM_NULLS / NUM_ROWS)
- 값 분포도 (히스토그램 → 컬럼별 분포 정보 저장)

인덱스 통계:
- 인덱스 높이 (BLEVEL)
- 클러스터링 팩터 (CLUSTERING_FACTOR)
- 리프 블록 수 (LEAF_BLOCKS)

📌 참고: 통계가 부정확하면 옵티마이저가 비효율적인 계획을 선택할 수 있음
→ DBMS_STATS.GATHER_*로 최신화 필요

[SQL 처리과정]
Parser
- Syntax Check → SQL 문법 오류 확인
- Semantic Check → 객체 존재, 권한, 타입 확인
- Cursor Lookup → 동일 SQL 커서 탐색

Optimizer
- Query Transformer서]
Child Cursor
- 바인드 변수 사용 중에도 실행환경(NLS, PLAN 등) 차이 → 별도 커서 생성
- 확인 뷰: V$SQLAREA.VERSION_COUNT

커서 Invalidation
- 다음 이벤트 발생 시 커서 재사용 불가:
  - DDL (ALTER TABLE 등)
  - 통계 정보 변경 (DBMS_STATS)
  - 권한 변경 (GRANT, REVOKE)
  - 인덱스 리빌드 등

진단용 V$뷰
뷰                 설명
V$SQLAREA         SQL별 실행/Parse/Version 통계
V$LIBRARYCACHE    GETS, PINS, INVALIDATIONS
V$OPEN_CURSOR     세션별 열린 커서 확인
V$SESSION         세션 정보 + 대기 이벤트 분석

대기 이벤트
이벤트                   설명
latch free              Latch 획득 실패
library cache lock     SQL 실행 중 객체 변경 충돌
cursor: pin S wait on X Mutex Pin 경합 (10g 이후)
