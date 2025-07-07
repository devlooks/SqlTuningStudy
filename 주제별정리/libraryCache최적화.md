
library Cache 최적화

[비용 기반 옵티마이저]
- 비용: SQL 수행 시간, 수행 일량
- 자원 기준: I/O, CPU → 오브젝트 통계 기반으로 비용 계산
- 옵티마이저는 다양한 실행계획 중 가장 낮은 비용 선택

[오브젝트 통계 항목]
- 테이블 통계: 레코드 수, 블록 수, 평균 행 길이
- 컬럼 통계: Distinct 값 수, Null 비율, 컬럼값 분포도
- 인덱스 통계: 인덱스 높이(Level), 클러스터링 팩터, 리프 블록 수, BLEVEL

[SQL 처리과정]
- Parser: SQL 문법(Syntax) 검사, 의미(Semantic) 분석, Cursor Lookup 수행
- Optimizer:
    - Query Transformer: View Merge, Subquery Unnest 등
    - Estimator: 통계 기반 비용 계산
    - Plan Generator: 다양한 실행계획 생성 후 비용 비교
- Row-Source Generator → 실행 루틴 생성
- Execution → SQL 실행

[Soft Parsing]
- 라이브러리 캐시에 실행계획 존재 시 재사용
- Hard Parse보다 훨씬 빠름, latch 소모 낮음

[Hard Parsing]
- SQL 캐시 미존재 → 최적화 → 실행계획 생성
- CPU 사용, Shared Pool Latch 경합, 메타데이터 접근 발생

[라이브러리 캐시 구조]
- SQL 실행계획, PL/SQL 오브젝트, 커서 등 저장
- 해시 기반 구조 → 해시키 통해 커서 탐색
- LCO Handle, Heap으로 구성됨
- LRU 알고리즘 기반으로 Cache 유지/삭제 관리

[SHARED POOL 래치]
- Shared Pool 내 Library Cache, Dictionary Cache 존재
- 이들 보호를 위해 래치 사용 → 경합 발생 가능
- 특히 Hard Parse 시 경합 심화

[library Cache 래치]
- 커서 탐색 시 래치 필요
- Soft/Hard Parse 시 latch 획득 시도
- CPU 수만큼 latch 존재 → 고빈도 Parse 시 경합률 증가

[library Cache 최적화]
- library Cache lock/pin 발생:
    - Lock: 커서 접근 보호
    - Pin: 커서 변경 보호
- SQL 수행 중 DDL 발생 시 해당 커서에 lock/pin 충돌
- 경합 시 대기 이벤트: 'library cache lock', 'cursor: pin S wait on X'

[라이브러리 캐시 최적화 전략]
- 바인드 변수 사용 → 커서 공유 가능
- 세션 커서 캐싱 → Softest Soft Parse 유도
- 애플리케이션 커서 캐싱 → Parse Call 자체 감소

[세션 커서]
- PGA에 생성되며, 공유 커서를 가리킴
- 커서 정보:
    - 커서 포인터
    - 커서 이름 (명시적 커서명 포함)
    - 바인드 변수
    - 커서 상태
    - SQL 실행에 필요한 부가 정보

[커서 구분]
- 공유커서 → Library Cache의 Shared SQL Area
- 세션커서 → PGA 내 존재
- 애플리케이션 커서 → 클라이언트 측에서 세션 커서를 참조

[이름 없는 SQL]
- SQL 문장 자체가 커서 식별자
- 동적 SQL → Dictionary 미저장
- 매 실행마다 최적화, 캐시 여유 없으면 재최적화

[바인드 변수 부작용 해소]
- Bind Peeking:
    - 첫 수행 시 바인드 값 기반으로 실행계획 수립
    - 이후 성능 저하 발생 가능
- Adaptive Cursor Sharing:
    - 바인드 값에 따라 커서를 분기하여 실행계획 분리
- 리터럴 사용 고려:
    - 라이브러리 캐시 부하 ↓
    - 조건 컬럼 값 종류가 적은 경우 효율적
    - Batch, Long Running 쿼리, OLTP 저빈도 쿼리에 적합

[세션 커서 캐싱]
- 사용자 커서를 닫을 때 Parse Call ≥ 3 이면 세션 커서 캐시에 저장
- 세션 커서 캐시 구성:
    - SQL 텍스트 + 공유 커서 포인터
    - LRU 알고리즘으로 관리
- 닫힌 커서도 참조 유지 가능 → 커서 재오픈 속도 향상
- 관련 파라미터: SESSION_CACHED_CURSORS

[보완 키워드]
- Child Cursor: 동일 SQL이라도 환경이 다르면 별도 커서 생성
- V$SQLAREA.VERSION_COUNT로 확인 가능
- 커서 Invalidation 요인: DDL, 통계 변경, 권한 변경
- 관련 뷰:
    - V$SQLAREA, V$LIBRARYCACHE, V$OPEN_CURSOR, V$SESSION
    - 대기 이벤트 분석: latch free, library cache lock, mutex S/X
