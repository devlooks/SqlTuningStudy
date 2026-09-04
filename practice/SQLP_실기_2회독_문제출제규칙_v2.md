# SQLP 실기 2회독 문제출제규칙 v2

- **기준일:** 2026-08-11
- **마스터 범위 문서:** `SQLP_실기_2회독_통합패턴맵_v2_3_최종확정`
- **학습 운영 문서:** `SQLP_실기_2회독_학습계획_v2_1`
- **목적:** SQLP 실기 2회독에서 통합패턴맵의 Pattern ID를 기준으로 문제를 생성·검수하고, SQL·Execution Plan·Cardinality·결과집합이 서로 모순되지 않는 문제만 제공한다.

---

# 1. 적용 우선순위

1. 문제 범위와 중요도는 **통합패턴맵 최신 버전**을 따른다.
2. 학습일·난이도·순환 단계는 **학습계획 최신 버전**을 따른다.
3. 출제경향은 `검증된 출제경향 및 시험전략`의 근거 수준을 참고한다.
4. 본 문서와 통합패턴맵이 충돌하면 통합패턴맵을 우선한다.
5. 패턴맵에 없는 내용을 임의로 S/A 실전 핵심으로 승격하지 않는다.

# 2. Pattern ID 기반 출제

문제 생성 전 내부적으로 다음을 지정한다.

- Primary Pattern ID: 반드시 1개 이상
- Secondary Pattern ID: 필요 시 추가
- Composite Pattern ID: 복합문제일 때 지정
- 중요도: S/A/B/C/F
- 난이도: 초/중/고/실전
- TO-BE 제공 유형: A/B/C/D

### 중요도별 출제 원칙

- **S:** 단독 + 복합 모두 출제. 2회독 주력.
- **A:** S와 결합 우선. 반복오답 시 단독 보강 가능.
- **B:** S/A 복합의 보조축.
- **C/F:** 개념/안전망 확인 중심. 실전 핵심 진도를 지연시키지 않음.

# 3. 문제 입력정보

필요한 정보만 제공하되, 정답 판단에 필요한 정보는 누락하지 않는다.

- 테이블 DDL: 컬럼, 데이터 타입, PK/UK/FK, NULL 허용 여부
- 인덱스: 컬럼 순서, Unique 여부, Local/Global 등 필요한 물리정보
- 파티션: 방식, 파티션 키, 필요한 경우 파티션별 건수
- 데이터량: 전체 건수, 조건별 건수 또는 선택도
- NDV/분포: Cardinality 판단에 필요할 때 제공
- AS-IS SQL
- AS-IS Execution Plan
- 필요 시 Predicate Information
- 필요 시 Runtime Statistics: Starts/A-Rows/E-Rows/Buffers/TempSpc/Pstart/Pstop 등
- Trace형 문제라면 Parse/Execute/Fetch, cpu/elapsed/disk/query/current/rows 등 필요한 수치
- Lock/DML 문제라면 대상행 수, 인덱스 영향, 트랜잭션/동시성 조건 등 필요한 정보

# 4. 데이터량 / NDV 설계

`수천~수십만`으로 고정하지 않는다. 패턴의 물리적 특성이 자연스럽게 드러나는 규모를 사용한다.

예:
- 선택도/인덱스: 수천~수백만
- 대량 Hash Join/PX/Partition: 수백만~수천만 이상 가능
- 대량 DML/Batch: 변경 비율과 Undo/Redo/Lock 차이가 의미 있게 드러나는 규모

수치는 반드시 **SQL과 Plan의 Starts/A-Rows 계산이 논리적으로 일치하도록 역산**한다.

# 5. 테마 공개 여부

- 기본/부분숙달: 필요한 최소 단서만 제공 가능
- 고급: 테마명을 정답 방향으로 노출하지 않음
- 실전: 테마 비공개를 기본으로 함
- Pattern ID는 내부 관리용이며 사용자에게 원칙적으로 노출하지 않는다.

# 6. 난이도 설계

난이도는 단순 테이블 수가 아니라 판단의 상호의존성으로 정한다.

- **초:** 핵심 판단 1개가 독립적
- **중:** S/A 2~3개 판단이 연결
- **고:** 한 판단 오류가 Join Order/Starts/Cardinality 등 후속 판단에 연쇄 영향
- **실전:** 테마 비공개 + 불필요/필수 연산 혼재 + 시간제한 + 결과집합 함정 가능

# 7. 기본 문제 출력 형식

## 1. AS-IS 병목 판단

- Row Source 식별
- 단계별 Cardinality
- Starts/A-Rows
- Access/Filter Predicate
- 일반/Semi/Anti/Outer 관계
- 병목의 직접 원인

## 2. SQL + Hint / Index / DDL 재작성

- 원본 결과집합 보존
- 필요한 최소 Hint만 사용
- 문제 유형에 따라 Index/DDL/Trace 대응으로 대체 가능

## 3. TO-BE 실행계획 예상

- 핵심 Row Source
- Access Path
- Join Method/Order
- 제거/추가되는 연산
- 예상 Starts/A-Rows 변화
- Partition/PX 문제는 데이터 이동까지 설명

# 8. TO-BE 제공 유형

- **A형 AS-IS Only:** TO-BE 미제공. 스스로 개선안 도출.
- **B형 목표 Plan 제공:** 목표 Plan을 보고 SQL/Hint를 역설계.
- **C형 부분 TO-BE:** 일부 Plan/Hint만 제공.
- **D형 실전:** 테마·개선방향·TO-BE 모두 비공개.

유형은 숙련도만으로 기계적으로 결정하지 않고 학습 목적에 따라 혼합한다.

# 9. 문제 유형 Coverage

문제 유형은 고정 목록이 아니라 통합패턴맵의 최신 S/A Pattern ID를 따른다. 현재 v2.3 기준 대표 유형은 다음과 같다.

1. Cardinality / Starts / Execution Plan
2. Predicate / Sargability / Data Type
3. Access Path / Index 설계
4. Join Method / Join Order / Join Semantics
5. Semi / Anti / DISTINCT / 1:N 증폭
6. Scalar Subquery / Unnest / PUSH_SUBQ / View Transformation
7. Optional Predicate / OR Expansion
8. Sort / GROUP BY / Analytic / Top-N
9. Partition Pruning / Partition DDL
10. Full/Partial Partition-Wise Join
11. Parallel Execution / PQ Distribution
12. DELETE / INSERT / CTAS / EXCHANGE / 대량 UPDATE
13. Runtime Statistics / SQL Trace / Database Call
14. Lock / Transaction / Concurrency
15. Performance Troubleshooting
16. Composite Pattern 종합 튜닝

통합패턴맵에서 S/A가 추가·삭제되면 이 목록보다 **Pattern ID 최신 상태를 우선**한다.

# 10. Cardinality / Starts 설계 규칙

1. 각 Row Source의 입력·출력 건수를 먼저 정의한다.
2. NL의 Inner Starts는 Outer 흐름과 물리 수행을 기준으로 계산한다.
3. FILTER/Scalar Subquery는 상관조건과 캐싱 가능성을 구분한다.
4. Semi Join은 내부 중복으로 외부 결과를 증폭시키지 않는다.
5. Anti Join은 제거율을 명시한다.
6. GROUP BY/DISTINCT는 입력건수와 결과 NDV를 함께 정의한다.
7. PX Starts는 DOP와 Slave set 특성을 직렬 Starts처럼 단순 해석하지 않는다.
8. A-Rows가 `총량`인지 `Starts당`인지 문제 표기 방식과 계산이 모순되지 않게 한다.

# 11. SQL / Execution Plan 일치 규칙

문제의 AS-IS SQL이 제시 Plan을 물리적으로 만들 수 있는지 검증한다.

특히 다음을 확인한다.

- SQL에 없는 Join/Filter가 Plan에 등장하지 않는가
- 필요한 Join Predicate가 누락되지 않았는가
- INDEX/FULL/PARTITION 접근이 DDL과 조건상 가능한가
- Semi/Anti/Outer 의미가 SQL과 Plan에서 일치하는가
- PX SEND/RECEIVE와 Distribution이 파티션/조인 구조와 맞는가
- Group By/Distinct/Sort/Stopkey 위치가 SQL 의미와 맞는가

# 12. 결과집합 동일성 검증

정답 SQL은 성능 개선보다 먼저 결과 동일성을 만족해야 한다.

필수 확인 항목:

- 중복
- NULL
- NOT IN/NOT EXISTS 3-valued logic
- Outer Join의 보존행
- ON vs WHERE 필터 위치
- Top-N의 정렬 순서
- GROUP BY 기준키
- COUNT(*) vs COUNT(col)
- UNION vs UNION ALL
- JOIN → EXISTS 변환 시 상대 테이블 컬럼 사용 여부
- 선집계 시 원본 상세행 의미 보존

가능하면 실제 데이터 비교, 그렇지 않으면 논리적으로 동일함을 증명한다.

# 13. Hint 검수

1. Hint는 목적이 명확한 것만 사용한다.
2. `QB_NAME`/`@qb` 대상이 정확한지 확인한다.
3. `LEADING`과 `USE_NL/HASH/MERGE`의 대상/순서가 물리적으로 맞는지 확인한다.
4. `UNNEST`와 `PUSH_SUBQ`의 목적을 혼동하지 않는다.
5. `PQ_DISTRIBUTE(inner, outer_dist, inner_dist)`의 Inner/Outer 위치를 검증한다.
6. `USE_CONCAT/NO_EXPAND`, `SWAP_JOIN_INPUTS` 등은 해당 변환/입력 역할의 필요성이 있을 때만 사용한다.
7. 불필요한 Hint를 정답에 추가하지 않는다.

# 14. Partition / Parallel 검수

- Static/Dynamic Pruning 조건 확인
- 파티션 키 가공 여부 확인
- Full PWJ 조건: 양쪽 파티션 정렬/조인키 관계 확인
- Partial PWJ 조건: 한쪽 파티션 구조와 다른 입력의 PARTITION(KEY) 재분배 가능성 확인
- PX SEND HASH/BROADCAST/PARTITION의 이동 목적 확인
- SEND 자체를 병목으로 단정하지 않음
- DOP와 데이터 이동량을 고려

# 15. DML / Batch 검수

대량 DML 문제는 접근비용만 보지 않는다.

- 대상행 수/비율
- 변경 컬럼이 포함된 인덱스 수
- Undo/Redo
- Lock 유지시간
- DELETE/INSERT vs TRUNCATE/CTAS/EXCHANGE
- 대량 UPDATE vs MERGE/집합 UPDATE/재구성 대안
- Global/Local Index와 Partition DDL 영향

# 16. Runtime / Trace / Troubleshooting 검수

문제에서 실제로 제공한 지표만 근거로 판단하도록 구성한다.

- Parse/Execute/Fetch
- cpu vs elapsed
- disk/query/current
- Buffers/Reads/Writes
- OMem/1Mem/Used-Mem/TempSpc
- Blocking/Waiting 정보
- PX skew가 필요한 경우 PX별 편차

지표가 없는데 특정 원인을 단정하도록 문제를 만들지 않는다.

# 17. 오답 재출제

오답은 같은 문제 즉시 반복보다 변형을 우선한다.

1. 동일 Pattern, 다른 수치/데이터 모델
2. 동일 Pattern + 다른 A Pattern
3. Composite Pattern
4. 테마 비공개 실전

반복오답 Pattern ID는 학습계획의 다음 Cycle 보강 대상으로 전달한다.

# 18. 전 문제 공통 필수 사전 검수 14대 체크리스트 (Zero-Defect Gate)

특정 테마에 국한되지 않고, **어떠한 문제를 출제하든 사용자에게 출력하기 직전에 아래 14대 항목을 전수 교차 검증**한다. 단 하나라도 위배 시 출제를 중단하고 수치와 구조를 재설계한다.

1. **실행계획 트리 계층 & 순서 정합성:**
   - `NESTED LOOPS` / `HASH JOIN` / `MERGE JOIN`에서 상단(1st Child) 노드가 Driving(Outer), 하단(2nd Child) 노드가 Driven(Inner)으로 정확히 배치되었는가?
   - 부모-자식 들여쓰기와 Operation Id 순서가 오라클 표준 계층 구조와 100% 일치하는가?
2. **Starts / A-Rows 전파 산술식 검증:**
   - Outer 노드의 `A-Rows`와 Inner 노드의 `Starts` 수치가 논리적/산술적으로 일치하는가? (스칼라/필터 서브쿼리, NL 루프 등)
   - 서브쿼리 캐싱이나 Short-Circuit(조기 탈출) 발생 시 `Starts`와 `A-Rows`의 실제 동작이 일치하는가?
3. **SQL과 Execution Plan 일치:** SQL의 구문/조건과 Plan의 오퍼레이션이 1:1로 정확히 대응하는가?
4. **DDL / Index Access Path 물리적 실현 가능성:**
   - 주어진 인덱스 컬럼 구성 및 PK/FK 제약 조건 하에서 해당 Plan(Range/Unique Scan, Index Fast Full Scan 등)이 실제로 유효한가?
5. **Predicate Information 매핑 검증:**
   - Plan의 Operation Id와 Predicate Information 번호가 완벽히 일치하며, `access`와 `filter` 조건절이 물리적으로 정확히 구분되었는가?
6. **Buffers / I/O 수치 역산 일치:** 테이블/인덱스 블록 수 및 클러스터링 팩터 대비 버퍼 수치가 상식적이고 물리적으로 타당한가?
7. **일반 / Semi / Anti / Outer 논리관계 검증:** 데이터 모델 관계(1:1, 1:N) 및 서브쿼리 의미론이 Plan과 일치하는가?
8. **Partition / PX 데이터 흐름:** 파티션 프루닝(`Pstart/Pstop`), PX 분배 방식(`SEND HASH/BROADCAST` 등)이 데이터 모델과 일치하는가?
9. **Hint의 유효성 및 QB 매핑:** 힌트 구문 문법 오류가 없으며 정확한 Query Block / Table Alias를 타겟팅하는가?
10. **AS-IS와 TO-BE 명확한 분리:** AS-IS의 비효율 원인이 명확하고 제거 대상 Row Source가 실재하는가?
11. **개선 SQL과 원본 SQL 결과집합 동일성 (Semantic Equality):** NULL, 중복 데이터, 1:N 조인 증폭, 집계 키 보존 여부가 100% 검증되었는가?
12. **Top-N / Sort / Stopkey 보존:** 정렬 기준 및 결과 건수 왜곡이 없는가?
13. **TO-BE Plan 실현 가능성:** 개선 SQL 및 인덱스 적용 시 제시하는 TO-BE Plan이 오라클 옵티마이저 원리상 실현 가능한가?
14. **문제 정보의 충분성:** 제약 조건과 튜닝 지침이 충분하여 정답이 논리적으로 수렴하는가?

# 19. 내부 검수 프로세스 (3단계 강제 게이트)

- **1단계 (생성 직후):** DDL, 인덱스, 데이터량, SQL, Plan 1차 작성
- **2단계 (정답 역산):** TO-BE SQL, 힌트, 예상 Plan 및 결과집합 동일성 역산 검증
- **3단계 (최종 출력 직전):** 14대 무결성 체크리스트 전수 대조 후 이상 없을 시에만 사용자 화면에 출력

# 20. 정답/채점 규칙

1. 사용자의 답에서 먼저 맞은 부분과 틀린 부분을 분리한다.
2. Pattern ID별로 오류 위치를 내부 기록한다.
3. 단순 용어 차이와 결과집합/물리수행 오류를 구분한다.
4. Cardinality 계산은 중간 과정까지 검산한다.
5. 여러 개선안이 논리적으로 가능하면 하나만 정답으로 강제하지 않는다.
6. 단, 문제에서 요구한 목표 Plan/Hint 조건이 있으면 그 제약을 우선한다.
7. 정답 근거가 통합패턴맵/소스에 없으면 임의로 단정하지 않는다.

# 21. 최종 원칙

- 범위는 통합패턴맵이 결정한다.
- 문제는 Pattern ID를 내부적으로 지정한다.
- S/A가 2회독 문제의 중심이다.
- FTS/PX SEND/Sort/Unique 같은 연산은 존재 자체로 병목으로 단정하지 않는다.
- 성능 개선보다 결과집합 동일성이 우선이다.
- Starts/A-Rows/Cardinality는 모든 문제에서 검증한다.
- 정답 TO-BE는 SQL과 물리적으로 실현 가능한 Plan이어야 한다.
- 불확실한 근거는 불확실하다고 표시한다.
