# SQLP 실기 2회독 통합패턴맵 v2.3 (최종 확정)

- 기준일: 2026-08-11
- 목적: SQLP 실기에서 필요한 SQL 튜닝 패턴을 누락 없이 관리하고, Oracle 튜닝 이론을 시험 직접성에 따라 구분하여 2회독 문제 출제·복습·숙련도 판정의 기준 문서로 사용한다.
- 대체 대상: `SQLP_실기_2회독_통합패턴맵_v2_2_최종보완`
- v2.3 보완 목적: 최종 심층 리서치 재검증 결과를 반영하여, 실기 직접 핵심의 마지막 누락인 대량 UPDATE 튜닝을 추가하고 공식 SQLP 전체 범위의 저우선 안전망(SQL 활용/문법)을 보완한다.
- 최종 감사 원칙: 공식 SQLP 범위와 Oracle 공식 튜닝 원리를 기준으로 `실기 직접 핵심(S/A)`과 `공식/이론 보조(B/C)`를 분리한다.

## 0. 근거 및 적용 원칙

### 0.1 우선 참조 소스
1. `SQLP_실기_검증된_출제경향_및_시험전략_v1`
2. `SQLP_실기_2회독_문제출제규칙_v1`
3. `SQLP_실기_2회독_학습계획_v1`
4. `deep-research-report.md`
5. 기존 `SQLP_실기_2회독_통합패턴맵_v1`

### 0.2 중요도 등급
- **S**: SQLP 실기 문제 해결의 중심축. 독립 식별·개선·검증까지 반드시 숙달.
- **A**: 빈번하게 S 패턴과 결합되는 핵심 보조축. 실전 문제화 대상.
- **B**: Oracle 튜닝에서 중요하고 SQLP 복합문제의 기반이 될 수 있으나 직접 출제 근거가 S/A보다 약함.
- **C**: Oracle 이론상 유효하지만 현재 프로젝트 소스에서 SQLP 실기 직접 출제 근거가 부족함. 개념 확인 중심.

### 0.3 출제근거 신뢰도
- **A**: 공식/프로젝트 검증 근거
- **B**: 복수 자료 및 Oracle 원리와 교차검증
- **C**: 제한적 출제 사례 또는 간접 근거
- **D**: 추정. 문제 출제의 단독 근거로 사용하지 않음

### 0.4 숙련도 기록 원칙
- 실제 문제 풀이 기록으로 확인되지 않은 숙련도는 **미평가**로 기록한다.
- 최근 성공일/오답일/반복 오류는 실제 대화 또는 제출 답안에 근거가 있을 때만 갱신한다.

### 0.5 문제화 원칙
- S/A: 단독 문제 + 복합 문제 모두 출제
- B: S/A와 결합한 복합문제 우선
- C: 원리 확인 또는 보충문제 위주. 실전 비중을 과도하게 늘리지 않음

### 0.6 최종 심층 리서치 감사 결과 적용 원칙
- 심층 리서치에서 '누락'으로 표시되었더라도 현재 v2.1에 이미 존재하는 항목(View Merge, MV Rewrite, OR Expansion, PUSH_SUBQ, Bind Peeking/ACS, Extended Statistics 등)은 **중복 추가하지 않는다**.
- 최종 보완은 현재 문서와 외부 감사 결과의 **차집합**만 반영한다.
- 공식 SQLP 범위에 포함될 수 있으나 최근 실기 직접 출제 근거가 약한 항목은 B/C로 유지한다.
- Oracle 기능이 존재한다는 사실만으로 SQLP S/A로 승격하지 않는다.
- 공식 SQLP 전체 범위에 존재하지만 실기 튜닝 직접성이 낮은 SQL 문법/활용 항목은 `F`(Foundation Safety Net) 영역에서 B/C로 별도 관리한다.

---

# 1. 전체 Taxonomy

1. 결과집합 / Cardinality / Selectivity
2. Optimizer Statistics / 추정오류
3. Predicate / Sargability / 데이터 타입
4. Table & Index Access Path
5. Index 설계 / 물리 특성
6. Join Method / Join Order / Join Semantics
7. Subquery / Query Transformation
8. SQL Rewrite / Query Block / Hint
9. Sort / DISTINCT / Set Operation
10. Group By / Aggregate / Analytic / Top-N
11. Partition
12. Parallel Execution
13. DML / Batch / DDL
14. Execution Plan / Runtime Statistics
15. Data Model Semantics / Relationship
16. SQL 수행 구조 / Parse-Execute-Fetch / Database Call
17. SQL Trace / Response Time Analysis
18. Lock / Transaction / Concurrency
19. Performance Troubleshooting
20. Plan Stability / Runtime Adaptation / 기타 Oracle 튜닝
21. SQLP 공식범위 안전망 / SQL 활용·문법

---

# 2. 원자 패턴맵

> 공통 필드: `ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 Plan/징후 | Cardinality/진단 포인트 | 대응 | Hint/DDL | 혼동 패턴 | 2회독 처리 | 숙련도`

## 2.1 결과집합 / Cardinality / Selectivity

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 Plan/징후 | Cardinality/진단 포인트 | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|---|
| C01 | 단계별 결과 건수 계산 | S | A | 각 Row Source의 입력→필터→조인→집계 결과 흐름을 계산한다 | 모든 Plan | A-Rows 흐름, 입력/출력 건수 | SQL/Plan을 위에서 아래가 아니라 데이터 흐름 기준으로 판독 | 필수 반복 | 숙달 (2026-08-16) |
| C02 | 선택도(Selectivity) | S | A | 조건이 전체 중 몇 %를 남기는지가 접근/조인 방식 선택의 핵심 | Filter/Access Predicate | 조건 후 A-Rows | 조건식·통계·인덱스 재검토 | 필수 | 숙달 (2026-08-16) |
| C03 | NDV 기반 등치조건 추정 | A | B | 균등분포 가정 시 등치조건 선택도는 NDV와 연관 | E-Rows 괴리 | NDV, 분포 왜곡 | 통계/히스토그램 검토 | 보강 | 숙달 (2026-08-31) |
| C04 | 범위조건 Cardinality | A | B | BETWEEN, >, < 범위는 값 분포와 경계에 따라 건수 결정 | INDEX RANGE SCAN/FTS | 범위 폭과 실제 분포 | 범위조건 재작성/통계 검토 | 보강 | 미평가 |
| C05 | 조인 Cardinality | S | A | PK/FK, NDV, 중복도에 따라 조인 출력이 증폭/축소 | HASH/NL/MERGE JOIN | 1:1, 1:N, N:M | 조인 관계부터 명시 | 필수 | 미평가 |
| C06 | Semi Join Cardinality | S | A | EXISTS는 외부 행의 존재 여부만 필요하여 내부 중복이 외부행을 증폭시키지 않음 | HASH/NL SEMI | 외부 결과 상한 | EXISTS/Semi Join 활용 | 필수 | 미평가 |
| C07 | Anti Join Cardinality | S | A | NOT EXISTS는 매칭되지 않는 외부 행만 반환 | HASH/NL ANTI | 제거 비율 | Anti Join 변환 검토 | 필수 | 미평가 |
| C08 | GROUP BY 입출력 건수 | S | A | 입력행 수와 그룹 NDV가 출력행 수를 결정 | HASH/SORT GROUP BY | 그룹키 NDV | 선집계/후집계 위치 판단 | 필수 | 미평가 |
| C09 | DISTINCT 전후 건수 | S | A | 1:N 조인 증폭 후 DISTINCT가 중복 제거 비용을 만든다 | HASH UNIQUE/SORT UNIQUE | 증폭 건수와 최종 유일건수 | Semi Join/사전집계 등 구조 변경 | 필수 | 미평가 |
| C10 | Top-N 결과 건수 | A | A | 전체 정렬/분석 전에 N건만 필요하면 Stopkey 가능성 | COUNT STOPKEY/SORT ORDER BY STOPKEY | N과 입력건수 | ROWNUM/FETCH/ROW_NUMBER 구조 점검 | 필수 | 미평가 |

## 2.2 Optimizer Statistics / 추정오류

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 징후 | 진단 포인트 | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|---|
| S01 | E-Rows vs A-Rows 괴리 | S | A | 추정 오류가 잘못된 Access/Join Order/Join Method로 전파될 수 있음 | E-Rows≪/≫A-Rows | A-Rows/Starts와 E-Rows 비교 | 통계·분포·조건 상관성 점검 | 필수 | 미평가 |
| S02 | 통계 없음/오래된 통계 | A | B | 부정확한 통계는 비용 추정을 왜곡 | Note/동적 통계, 비정상 E-Rows | Last analyzed, stale 여부 | DBMS_STATS 등 검토 | 보강 | 미평가 |
| S03 | NDV 오류 | A | B | 실제 고유값 수와 통계 NDV 차이가 선택도 오류 유발 | 등치조건 E-Rows 오차 | NDV 비교 | 통계 갱신 | 보강 | 미평가 |
| S04 | Histogram / Skew | A | B | 데이터 편중 시 단순 균등분포 추정이 틀릴 수 있음 | 특정 리터럴에서만 Plan 악화 | 값별 빈도 | 적절한 히스토그램 검토 | 보강 | 미평가 |
| S05 | 컬럼 상관관계 / Extended Statistics | B | C | 독립 선택도 곱셈이 실제 상관관계를 반영하지 못할 수 있음 | 복합조건 E-Rows 오차 | 다중컬럼 상관 | Column Group 통계 검토 | 개념+복합 | 미평가 |
| S06 | Bind Peeking | B | C | 최초 바인드 값의 분포 특성이 계획 선택에 영향을 줄 수 있음 | 바인드값별 성능 편차 | 첫 실행/분포 | ACS/통계/SQL 구조 검토 | 개념 | 미평가 |
| S07 | Adaptive Cursor Sharing | C | C | 바인드 선택도 차이를 커서별로 분리할 수 있음 | Child cursor 다양화 | Bind sensitivity | 개념 확인 | 저우선 | 미평가 |
| S08 | Dynamic Statistics | C | C | 통계 부족 시 실행/파싱 시점의 추가 샘플링으로 추정 보완 | Plan Note | dynamic statistics 사용 | 통계 품질 개선 우선 | 저우선 | 미평가 |
| S09 | Cardinality/Statistics Feedback | C | C | 실행 결과를 다음 최적화에 활용하는 재최적화 메커니즘 | 재파싱 후 계획 변화 | 버전별 기능 차이 | 개념 확인 | 저우선 | 미평가 |
| S10 | System Statistics | B | C | CPU/I/O 특성 등 시스템 통계가 Cost 계산에 영향을 줄 수 있음 | 동일 SQL의 비용/Plan 선택 차이 | 통계 존재 여부와 비용모델 영향 확인 | 개념+복합 | 미평가 |

## 2.3 Predicate / Sargability / 데이터 타입

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 징후 | 진단 포인트 | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|---|
| P01 | 컬럼 함수 가공 | S | A | `TRUNC(col)`, `TO_CHAR(col)` 등은 일반 B-tree 인덱스/프루닝 가용성을 약화할 수 있음 | FTS, FILTER | Access vs Filter Predicate | 범위식으로 재작성/FBI 검토 | 필수 | 숙달 (2026-09-06) |
| P02 | 암묵적 형변환 | S | A | 데이터 타입 불일치가 컬럼 쪽 변환으로 귀결되면 인덱스 사용성과 추정이 악화될 수 있음 | INTERNAL_FUNCTION/TO_NUMBER 등 | Predicate Information | 타입 일치 | 필수 | 숙달 (2026-08-20) |
| P03 | 날짜 등치 → 범위 재작성 | S | A | `TRUNC(dt)=:d` 대신 `dt>=:d AND dt<:d+1` 형태로 접근범위를 열 수 있음 | RANGE SCAN 가능 | 경계값 포함성 | 반개구간 사용 | 필수 | 숙달 (2026-08-20) |
| P04 | NVL/DECODE/CASE 조건 | A | B | 선택조건을 표현식으로 감싸면 Index/OR-expansion 가능성이 달라짐 | FILTER/FTS | 호출 유형별 선택도 | 분기/OR-expansion 검토 | 보강 | 숙달 (2026-08-18) |
| P05 | Optional Predicate | S | A | `:b IS NULL OR col=:b`는 서로 다른 선택도의 호출을 한 SQL로 묶음 | 단일 비효율 Plan | NULL/NOT NULL 호출 건수 | 분기 SQL/UNION ALL 검토 | 필수 | 숙달 (2026-08-18) |
| P06 | LIKE Leading Wildcard | B | C | `%abc`는 일반 B-tree 선두 탐색이 어렵다 | FTS/FFS | 패턴 형태 | 요구사항/인덱스 전략 재검토 | 개념 | 미평가 |
| P07 | IN vs OR | A | B | 동등한 조건이라도 변환/접근경로가 달라질 수 있음 | INLIST ITERATOR/CONCATENATION | 값 개수/선택도 | OR-expansion/INLIST 비교 | 보강 | 숙달 (2026-08-18) |
| P08 | NULL 의미와 인덱스 | A | A | 단일 B-tree 인덱스는 전부 NULL인 키 엔트리를 저장하지 않는 특성이 조건 처리에 영향 | INDEX 사용 여부 | `IS NULL`, 복합인덱스 | 인덱스 구성 검토 | 보강 | 미평가 |
| P09 | NOT IN + NULL | S | A | 서브쿼리 결과에 NULL이 있으면 3-valued logic으로 결과가 달라질 수 있음 | Anti 변환 제약 | NULL 가능성 | NOT EXISTS + 상관조건 검토 | 필수 | 미평가 |
| P10 | Access Predicate vs Filter Predicate | S | A | 인덱스 탐색 범위를 줄이는 조건과 읽은 뒤 거르는 조건을 구분해야 함 | Predicate Info | access()/filter() | 인덱스 컬럼순서/SQL 조건 수정 | 필수 | 미평가 |

## 2.4 Table & Index Access Path

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 Plan | 진단 포인트 | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|---|
| A01 | TABLE ACCESS FULL | S | A | 전체/대량 범위에서는 FTS가 정상일 수 있으며 FTS 자체가 병목을 의미하지 않음 | TABLE ACCESS FULL | 읽을 필요가 있는 비율, Buffers | 선택도·파티션·병렬과 함께 판단 | 필수 | 미평가 |
| A02 | INDEX UNIQUE SCAN | A | A | Unique/PK 전체키 등치 탐색 시 단건 접근 | INDEX UNIQUE SCAN | Starts와 1건성 | PK/UK 조건 검토 | 보강 | 미평가 |
| A03 | INDEX RANGE SCAN | S | A | 선두키 조건과 범위에 따라 리프 구간 탐색 | INDEX RANGE SCAN | 스캔 엔트리 수 | 조건/컬럼순서 최적화 | 필수 | 미평가 |
| A04 | INDEX FULL SCAN | B | B | 인덱스 순서를 유지하며 전체 리프를 순차 탐색 | INDEX FULL SCAN | 정렬 제거 가능성 | ORDER BY/커버링과 연계 | 개념+복합 | 미평가 |
| A05 | INDEX FAST FULL SCAN | B | B | 인덱스를 멀티블록 방식으로 전체 읽되 정렬순서는 보장하지 않음 | INDEX FAST FULL SCAN | 테이블 대신 인덱스만 읽는 이점 | 커버링 여부 | 개념 | 미평가 |
| A06 | INDEX SKIP SCAN | B | C | 선두키 NDV가 낮을 때 비선두 조건으로 반복 탐색 가능 | INDEX SKIP SCAN | 선두 NDV/반복 수 | 새 인덱스와 비용 비교 | 개념 | 미평가 |
| A07 | INDEX MIN/MAX SCAN | B | C | 적절한 인덱스에서 MIN/MAX를 극소 범위로 처리 | INDEX FULL SCAN (MIN/MAX) | 집계 입력 최소화 | 인덱스 활용 | 개념 | 미평가 |
| A08 | Descending Index Scan | B | C | 정렬 방향과 인덱스 순서를 이용해 정렬 생략 가능 | INDEX RANGE SCAN DESCENDING | ORDER BY 방향 | 인덱스/Top-N 결합 | 개념 | 미평가 |
| A09 | TABLE ACCESS BY INDEX ROWID | S | A | 인덱스에서 얻은 ROWID로 테이블 블록을 방문 | TABLE ACCESS BY INDEX ROWID | 방문건수·클러스터링 | 커버링/선택도 검토 | 필수 | 미평가 |
| A10 | Batched ROWID Access | C | C | ROWID 방문을 묶어 블록 접근 효율을 높이는 실행 형태 | TABLE ACCESS BY INDEX ROWID BATCHED | 버전/Plan 형태 | 개념 확인 | 저우선 | 미평가 |
| A11 | Bitmap Index Access | B | C | 낮은 NDV 다중조건 분석형 환경에서 비트연산이 유리할 수 있음 | BITMAP INDEX ... | DML 동시성 주의 | OLTP 여부 판단 | 개념 | 미평가 |
| A12 | Function-Based Index | A | B | 반복되는 표현식 조건을 인덱스 키로 저장 | INDEX RANGE SCAN on FBI | 표현식 일치 | SQL 재작성 vs FBI 비교 | 보강 | 미평가 |

## 2.5 Index 설계 / 물리 특성

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 진단 포인트 | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|
| I01 | 복합인덱스 컬럼 순서 | S | A | 등치/범위, 선택도, 정렬, 조인조건을 종합해 선두/후행 컬럼을 정함 | Access Predicate 범위 | 인덱스 재설계 | 필수 | 부분숙달 (2026-09-03, 오답일 2026-09-03) — 조인통로 인덱스 선두에 조인키(BRANCH_CD) 누락, 필터키(STAT_CD) 선두 배치 오류 |
| I02 | 선두컬럼 부재 | S | A | 선두키 조건이 없으면 일반 Range Scan 효율이 떨어질 수 있음 | Skip/Full/FTS | 호출 조건 | 새 인덱스/Skip 비교 | 필수 | 미평가 |
| I03 | 커버링 인덱스 | A | B | 필요한 컬럼을 인덱스에서 모두 해결하면 ROWID 테이블 접근 제거 가능 | Table Access 제거 | 인덱스 크기/쓰기비용 | 포함 컬럼 검토 | 보강 | 미평가 |
| I04 | Clustering Factor | A | B | 인덱스 순서와 테이블 블록 배치 상관이 ROWID 방문 비용에 영향 | Range Scan 비용 | CF vs blocks/rows | FTS와 비교 | 보강 | 미평가 |
| I05 | 인덱스 선택도 한계 | S | A | 결과 건수가 많으면 인덱스가 있어도 FTS가 더 나을 수 있음 | INDEX 강제 시 Buffers 증가 | 필터 후 건수 | 무조건 INDEX 금지 | 필수 | 미평가 |
| I06 | 중복/유사 인덱스 | B | C | 과도한 인덱스는 DML/공간/관리비용 증가 | DML 비용 | 컬럼 prefix 중복 | 통합/삭제 검토 | 개념 | 미평가 |
| I07 | Local Index | A | A | 파티션과 정렬된 인덱스 파티션은 관리성과 프루닝에 유리 | PARTITION + INDEX | 파티션 키/인덱스 구조 | Local 설계 | 필수 | 숙달 (2026-08-20) |
| I08 | Global Index | A | A | 비파티션 정렬 구조로 전역 접근에 유리하지만 파티션 DDL 영향 고려 | Global index maintenance | DDL 후 상태 | UPDATE INDEXES 등 검토 | 필수 | 숙달 (2026-08-20) |

## 2.6 Join Method / Order / Semantics

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 Plan | 진단 포인트 | 대응/Hint | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|---|
| J01 | Nested Loops | S | A | Outer에서 나온 각 행에 대해 Inner Row Source를 반복 실행. Inner 인덱스는 흔한 효율화 수단이지 절대 필수는 아님 | NESTED LOOPS | Outer A-Rows, Inner Starts, Inner 1회 비용 | LEADING/USE_NL, Access 개선 | 필수 | 숙달 (2026-08-16) |
| J02 | Hash Join | S | A | 한 입력으로 해시 구조를 만들고 다른 입력을 probe하여 대량 등치조인 처리 | HASH JOIN | build/probe 크기, 메모리/Temp | USE_HASH, 선필터 | 필수 | 숙달 (2026-08-16) |
| J03 | Merge Join | A | A | 조인키 순서가 필요한 두 입력을 병합. 비등치/정렬활용 상황도 고려 | MERGE JOIN | SORT JOIN 존재 여부 | USE_MERGE | 보강 | 미평가 |
| J04 | Join Order / Driving | S | A | 앞 단계에서 얼마나 줄이는지가 후속 Starts/입력건수에 연쇄 영향 | LEADING order | 각 단계 A-Rows | LEADING/ORDERED 신중 사용 | 필수 | 부분숙달 (2026-09-06, 오답일 2026-09-06) — Driving 선정은 완벽하나 조인통로 인덱스 선두 조인키 누락 재발 |
| J05 | Hash Build/Probe 판단 | A | B | 일반적으로 작은 쪽 build가 유리하나 메모리·통계·변환에 따라 실제 역할 확인 필요 | HASH JOIN children | 입력 크기 | 조인순서/선필터 | 보강 | 미평가 |
| J06 | Outer Join | S | A | 보존측 행을 유지하므로 필터 위치 변경 시 결과집합이 변할 수 있음 | HASH/NL OUTER | ON vs WHERE | 결과동일성 검증 | 필수 | 미평가 |
| J07 | Semi Join | S | A | 존재만 필요하면 내부 중복을 외부 결과에 증폭시키지 않음 | HASH/NL SEMI | 일반 Join+DISTINCT와 비교 | EXISTS/IN, HASH_SJ 등 | 필수 | 숙달 (2026-09-06) — EXISTS 세미 관계 유지 및 1:N 증폭 제거 완벽 |
| J08 | Anti Join | S | A | 부재 조건을 조인으로 처리해 반복 FILTER를 줄일 수 있음 | HASH/NL ANTI | NOT EXISTS Starts | HASH_AJ/NL_AJ 등 | 필수 | 미평가 |
| J09 | Cartesian Join | A | B | 조인조건 누락 또는 의도적 조합으로 곱집합 발생 | MERGE JOIN CARTESIAN | 급격한 A-Rows 증가 | 조인조건 검증 | 보강 | 미평가 |
| J10 | 1:N 증폭 | S | A | 다측과 일반 Join하면 기준 엔터티가 중복 출력될 수 있음 | Join 후 rows 급증 | 관계/PK-FK | Semi/집계/Distinct 필요성 판단 | 필수 | 숙달 (2026-09-01) |
| J11 | Join Predicate 누락 | S | A | 상관/조인 조건 누락은 결과집합 자체를 변경 | FILTER/Cartesian/과대건수 | SQL 논리 | 조건 복원 | 필수 | 미평가 |
| J12 | Join Method 강제의 함정 | A | A | USE_NL/HASH만으로 좋은 계획이 보장되지 않으며 Access/Order와 함께 결정 | Hint 적용 후 비효율 | 데이터량/접근비용 | 최소 힌트 | 보강 | 미평가 |

## 2.7 Subquery / Query Transformation

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 Plan/징후 | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|
| Q01 | Correlated Subquery FILTER | S | A | 외부행마다 서브쿼리가 반복 실행되면 Starts가 커질 수 있음 | FILTER + Inner Starts | Unnest/Semi/Anti/Join 변환 검토 | 필수 | 숙달 (2026-09-03) — 스칼라 서브쿼리 8,000회 반복 구동 진단 정확 |
| Q02 | Subquery Unnesting | S | A | 서브쿼리 QB를 조인 가능한 형태로 변환하여 Join Method 선택 폭을 넓힘. 항상 Semi Join이 되는 것은 아님 | SEMI/ANTI/일반 JOIN 등 | UNNEST/NO_UNNEST, 결과동일성 | 필수 | 숙달 (2026-09-06) — UNNEST NL_SJ 힌트 스스로 보완하여 완벽 달성 |
| Q03 | Scalar Subquery 반복 | S | A | 외부행마다 단일값 서브쿼리가 반복되어 Starts 증가 가능 | SCALAR SUBQUERY/FILTER | Join/사전집계로 변환 | 필수 | 부분숙달 (2026-09-03, 오답일 2026-09-03) — 조인 변환 구조는 도출, 지표 2개 중 1개 소실(결과집합 왜곡) |
| Q04 | Scalar Subquery Caching | B | C | 동일 키 반복 시 캐싱 효과가 있을 수 있어 Starts/비용을 단순 외부건수와 동일시하면 안 됨 | 실제 Starts 관찰 | 실제 Plan statistics 확인 | 개념 | 미평가 |
| Q05 | View Merge | A | B | 뷰 경계를 제거해 조인순서·Predicate 최적화 범위를 넓힐 수 있음 | VIEW 제거 | MERGE/NO_MERGE | 보강 | 미평가 |
| Q06 | Predicate Pushdown | A | A | 필터를 더 안쪽에 적용해 입력건수를 줄일 수 있음. Push가 항상 유리한 것은 아님 | VIEW PUSHED PREDICATE 등 | PUSH_PRED/NO_PUSH_PRED | 필수 | 숙달 (2026-08-19) |
| Q07 | OR Expansion | S | A | 상이한 선택도 조건을 분기해 각기 다른 Access Path를 허용 | CONCATENATION/UNION ALL | USE_CONCAT/NO_EXPAND | 필수 | 숙달 (2026-08-18) |
| Q08 | WITH / Materialization | A | B | 공통집합 재사용 또는 최적화 경계 생성이 장단점 | TEMP TABLE TRANSFORMATION 가능 | INLINE/MATERIALIZE는 버전·공식성 주의 | 보강 | 미평가 |
| Q09 | Join Factorization | C | C | UNION ALL branches의 공통 조인을 인수분해하는 변환 | Plan 변형 | 개념 확인 | 저우선 | 미평가 |
| Q10 | Join Elimination | C | C | 제약조건과 불필요 컬럼 사용 여부에 따라 조인 제거 가능 | Join row source 부재 | 개념 확인 | 저우선 | 미평가 |
| Q11 | Star Transformation | C | C | 다차원/팩트-디멘션 환경의 특수 변환 | BITMAP/STAR | SQLP 직접성 낮음 | 저우선 | 미평가 |
| Q12 | Materialized View Rewrite | C | C | 사전집계 MV로 쿼리를 Rewrite할 수 있음 | MAT_VIEW REWRITE | SQLP 직접성 낮음 | 저우선 | 미평가 |
| Q13 | Subquery Pushing | A | A | FILTER 형태로 유지되는 nonmerged subquery의 평가 시점을 앞당겨 후속 Row Source 입력을 줄일 수 있음. Unnesting과는 별개 판단 | FILTER의 위치/Starts 변화 | 조기 수행 시 제거되는 행수와 1회 수행비용 비교 | 필수 | 숙달 (2026-08-17) |
| Q14 | PUSH_SUBQ / NO_PUSH_SUBQ | A | A | `PUSH_SUBQ`는 가능한 이른 시점 평가, `NO_PUSH_SUBQ`는 늦은 평가를 유도. 항상 PUSH가 유리한 것은 아님 | FILTER + 조인 전/후 Starts 변화 | Early Filtering 이득 vs Subquery 반복비용 비교 | 필수 | 취약 (2026-09-03, 오답일 2026-09-03) — PUSH_SUBQ 접근안 3회 연속 미제출 |
| Q15 | Predicate Transitivity / 조건절 전이 | A | B | 등치관계 등을 이용해 한 조건에서 다른 조건을 유도하여 추가 Access/Join Predicate를 생성할 수 있음 | Predicate Information에 파생 조건, Access 범위 변화 | 유도된 조건이 논리적으로 안전한지와 Access Path 개선 여부 확인 | 보강 | 미평가 |
| Q16 | Table Expansion | C | C | 파티션/부분 영역별로 서로 다른 Access Path를 쓰도록 옵티마이저가 UNION ALL 성격의 계획으로 확장할 수 있음 | 분기된 UNION-ALL/partition별 상이한 access | 특수 상황에서만 개념 확인 | 저우선 | 미평가 |
| Q17 | Common Expression Elimination | C | C | 반복되는 공통 표현식/조건의 중복 평가를 줄이는 변환 계열 | Plan/Predicate 단순화 | SQLP 직접성 낮음, 원리 확인 | 저우선 | 미평가 |
| Q18 | Set Operation → Join Rewrite | C | C | UNION/MINUS/INTERSECT 계열 일부 논리를 Join/Semi/Anti 형태로 재작성할 수 있으나 결과집합 의미 보존이 우선 | SORT UNIQUE/SET OP 제거 후 JOIN 계열 | NULL/중복/집합 의미 검증 | 저우선 | 미평가 |

## 2.8 SQL Rewrite / Query Block / Hint

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 진단/대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|
| R01 | 결과집합 동일성 | S | A | 튜닝 SQL은 원본과 결과집합·NULL·중복·정렬 의미를 보존해야 함 | Before/After 논리 검증 | 모든 문제 필수 | 미평가 |
| R02 | JOIN → EXISTS | S | A | 출력에 상대 테이블 컬럼이 필요 없고 존재만 필요하면 Semi 성격 검토 | DISTINCT 제거 가능성 | 필수 | 숙달 (2026-08-16) |
| R03 | NOT EXISTS FILTER → Anti Join | S | A | 반복 부재검사를 조인으로 전환 | Starts 감소 | 필수 | 미평가 |
| R04 | Scalar Subquery → Join + Aggregate | S | A | 반복 집계를 한 번의 집합연산으로 전환 | Group By 위치/중복 주의 | 필수 | 부분숙달 (2026-09-03, 오답일 2026-09-03) — LEFT OUTER JOIN 판단 성공, CASE WHEN 1회 집계 미적용 + 상태코드를 뷰 WHERE로 내려 지표 소실, USE_HASH(V) 미지정 |
| R05 | OR → UNION ALL | S | A | 호출 유형/선택도가 크게 다를 때 분기별 최적 Access Path 허용 | 중복/분기조건 상호배타성 검증 | 필수 | 숙달 (2026-08-18) |
| R06 | 선집계 후 Join | A | B | 다측을 먼저 줄여 조인 증폭을 막음 | 집계 기준키·결과동일성 | 보강 | 미평가 |
| R07 | 불필요 DISTINCT 제거 | S | A | 원인이 제거되면 Unique 연산 자체를 제거 | PK/관계로 유일성 증명 | 필수 | 숙달 (2026-09-01) |
| R08 | QB_NAME | A | A | 힌트가 정확한 Query Block에 적용되도록 식별 | `QB_NAME`, `@qb` | 필수 | 미평가 |
| R09 | LEADING | S | A | 조인 순서를 제어하되 논리/데이터량 검증 필요 | `LEADING` | 필수 | 취약 (2026-09-03, 오답일 2026-09-03) — UNNEST 시 LEADING 2순위 배치 재발 실패, 조인조건 없는 부모 선행 배치(카티시안), LEADING 1순위에 USE_NL 지정 오류 |
| R10 | USE_NL/HASH/MERGE | S | A | 조인 방법 힌트는 대상과 조인순서를 함께 이해해야 함 | 공식 힌트 우선 | 필수 | 숙달 (2026-08-16) |
| R11 | INDEX/FULL | S | A | Access Path 강제는 선택도와 비용이 명확할 때 사용 | 공식 힌트 | 필수 | 미평가 |
| R12 | NO_MERGE / MERGE | A | B | View 변환 경계를 제어 | 결과/Plan 목적 명확화 | 보강 | 숙달 (2026-08-17) |
| R13 | UNNEST / NO_UNNEST | A | B | 서브쿼리 변환 여부 제어 | Semi/Anti/일반 Join 가능성 | 보강 | 취약 (2026-09-03, 오답일 2026-09-03) — NL_SJ 무시 메커니즘 미서술, NO_UNNEST 접근안 미제출 (3회 연속 미해소) |
| R14 | 최소 힌트 원칙 | S | A | 불필요한 힌트가 계획을 과도하게 고정하지 않도록 필요한 제어만 사용 | 힌트 하나씩 목적 설명 | 필수 | 미평가 |
| R15 | PUSH_SUBQ / NO_PUSH_SUBQ | A | A | FILTER 유지 시 서브쿼리 수행 위치를 제어한다. `UNNEST/NO_UNNEST`와 목적을 혼동하지 않는다 | 수행 시점 전후 후속 Join 입력과 Starts 비교 | 필수 | 취약 (2026-09-03, 오답일 2026-09-03) — NO_UNNEST+PUSH_SUBQ 접근안 3회 연속 미제출 |
| R16 | SWAP_JOIN_INPUTS / NO_SWAP_JOIN_INPUTS | A | B | Hash Join의 입력 역할/순서를 제어하는 힌트 계열. `LEADING`/Join Order와 함께 해석해야 하며 독립적으로 좋은 계획을 보장하지 않음 | Hash Join 자식 입력과 Build/Probe 역할, 메모리/Temp 비교 | 보강 | 미평가 |
| R17 | USE_CONCAT / NO_EXPAND | A | B | OR Expansion을 유도/억제하는 힌트. 분기별 선택도·인덱스 가용성과 UNION ALL 의미를 함께 검증 | CONCATENATION/UNION ALL 여부 | 보강 | 숙달 (2026-08-18) |

## 2.9 Sort / DISTINCT / Set Operation

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 Plan | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|
| O01 | SORT ORDER BY | A | A | 정렬 입력 건수와 메모리/Temp가 비용 결정 | SORT ORDER BY | 입력 축소/인덱스 순서 활용 | 필수 | 숙달 (2026-09-06) — INDEX_DESC 스캔 방향 일치 완벽 |
| O02 | SORT UNIQUE | S | A | 정렬 기반 중복 제거 | SORT UNIQUE | 중복 발생 원인 제거 | 필수 | 숙달 (2026-08-19) |
| O03 | HASH UNIQUE | S | A | 해시 기반 중복 제거 | HASH UNIQUE | Join 증폭 여부 | 필수 | 숙달 (2026-08-19) |
| O04 | UNION vs UNION ALL | A | B | UNION은 중복제거 비용, UNION ALL은 그대로 결합 | SORT/HASH UNIQUE | 중복 제거 필요성 | 보강 | 미평가 |
| O05 | SORT JOIN | A | B | Merge Join을 위한 정렬 | SORT JOIN | 기존 정렬 활용 여부 | 보강 | 미평가 |
| O06 | Temp Spill | A | B | 정렬/해시가 메모리를 넘으면 Temp I/O 발생 | TempSpc/OMem/1Mem | 입력 축소/PGA/방법 변경 | 보강 | 숙달 (2026-08-19) |

## 2.10 Group By / Aggregate / Analytic / Top-N

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 Plan | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|
| G01 | HASH GROUP BY | S | A | 해시 기반 그룹 집계 | HASH GROUP BY | 입력·그룹수·메모리 | 선필터/선집계 | 필수 | 숙달 (2026-09-03) — 선집계 인라인 뷰 구조 도출 유지 |
| G02 | SORT GROUP BY | S | A | 정렬 기반 그룹 집계 | SORT GROUP BY | 정렬 필요성과 Temp | 인덱스/입력 축소 | 필수 | 미평가 |
| G03 | GROUP BY 위치 | S | A | 조인 전/후 집계 위치가 중간건수와 결과 의미를 바꿈 | Group By child rows | 결과동일성 | 필수 | 숙달 (2026-08-18) |
| G04 | COUNT(*) vs COUNT(col) | A | B | NULL 포함 여부가 결과 의미를 바꿈 | Aggregate | NULL 의미 | 보강 | 미평가 |
| G05 | Analytic WINDOW SORT | A | A | ROW_NUMBER 등 분석함수는 파티션/정렬 입력에 따라 비용 발생 | WINDOW SORT | 입력건수/partition by/order by | Top-N 구조 검토 | 필수 | 숙달 (2026-08-19) |
| G06 | WINDOW NOSORT | A | A | 입력이 요구 순서를 이미 만족하면 정렬 생략 가능 | WINDOW NOSORT | 인덱스 순서 | 인덱스/Access 설계 | 보강 | 숙달 (2026-08-19) |
| G07 | STOPKEY | S | A | 필요한 N건 이후 처리를 중단할 수 있으면 대량 불필요 처리 제거 | COUNT STOPKEY/SORT ... STOPKEY | N 이전에 정렬이 필요한지 | 쿼리 구조 수정 | 필수 | 숙달 (2026-08-18) |
| G08 | ROWNUM Top-N | S | A | ORDER BY와 ROWNUM의 적용 순서가 결과를 결정 | STOPKEY | inline view 위치 | 결과동일성 검증 | 필수 | 숙달 (2026-08-18) |
| G09 | ROW_NUMBER Top-N | S | A | 그룹별 Top-N에 적합하지만 전체 Window 처리 여부 확인 | WINDOW SORT/NOSORT | PARTITION BY 단위 | 인덱스/Pushdown | 필수 | 숙달 (2026-08-19) |
| G10 | FETCH FIRST | A | A | 12c+ Top-N 문법. 기본 원리는 Stopkey/정렬과 동일 | STOPKEY 계열 | 버전 범용성 | ROWNUM 대안도 숙지 | 보강 | 미평가 |

## 2.11 Partition

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 Plan | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|
| PT01 | Range/List/Hash Partition 기본 | A | A | 파티션 키와 분할 방식이 접근/관리/조인에 영향 | PARTITION ... | 파티션키 | 필수기초 | 미평가 |
| PT02 | Static Partition Pruning | S | A | 컴파일 시 결정 가능한 조건으로 대상 파티션 최소화 | PARTITION RANGE SINGLE/ITERATOR | Pstart/Pstop | 필수 | 숙달 (2026-08-20) |
| PT03 | Dynamic Partition Pruning | S | A | 실행 시점 조인/바인드 등에 따라 대상 파티션 결정 | KEY 등 표시 | Pstart/Pstop | 필수 | 숙달 (2026-08-20) |
| PT04 | 파티션 키 가공으로 Pruning 저하 | S | A | 함수/형변환이 파티션 키 범위 추론을 방해할 수 있음 | RANGE ALL 등 | Predicate | 조건 재작성 | 필수 | 숙달 (2026-08-20) |
| PT05 | Full Partition-Wise Join | S | A | 양쪽이 조인키 기준으로 동등하게 파티션되어 로컬 파티션끼리 조인 가능 | PX PARTITION + JOIN, 재분배 최소 | 파티션키=조인키 | 필수 | 미평가 |
| PT06 | Partial Partition-Wise Join | S | A | 한쪽 파티션 구조를 활용하고 다른 쪽을 파티션 키 기준으로 재분배 | PX SEND PARTITION(KEY) 등 | 어느 쪽이 파티션됨 | 필수 | 숙달 (2026-08-22) |
| PT07 | Local Partitioned Index | A | A | 파티션 관리와 정렬된 인덱스 구조 | INDEX PARTITION access | 관리성 | 필수 | 숙달 (2026-08-20) |
| PT08 | Global Index + Partition DDL | A | A | 파티션 DROP/TRUNCATE/EXCHANGE 등에서 글로벌 인덱스 상태/유지비용 고려 | UNUSABLE 가능성 | DDL 옵션 | 필수 | 숙달 (2026-08-20) |
| PT09 | EXCHANGE PARTITION | S | A | 대량 교체를 row-by-row DELETE/INSERT 대신 메타데이터 중심으로 수행 가능 | DDL 시나리오 | 결과/제약/인덱스 | 필수 | 취약 (2026-08-24) |
| PT10 | SPLIT/MERGE/MOVE/TRUNCATE PARTITION | B | B | 파티션 유지보수와 인덱스 상태를 함께 판단 | DDL | 대상량/락 | 보강 | 미평가 |

## 2.12 Parallel Execution

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 Plan | 진단 포인트 | 대응/Hint | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|---|
| PX01 | PX Coordinator / QC | S | A | Query Coordinator가 PX 서버 간 흐름과 최종 결과를 조정 | PX COORDINATOR / PX SEND QC | TQ 흐름 | Plan 흐름 독해 | 필수 | 미평가 |
| PX02 | PX SEND / PX RECEIVE | S | A | 생산자·소비자 PX 세트 사이 데이터 이동을 나타냄. SEND 자체를 곧 병목으로 단정하지 않음 | PX SEND ..., PX RECEIVE | 이동 건수 | 분배 목적 판단 | 필수 | 미평가 |
| PX03 | PX BLOCK ITERATOR | S | A | 블록 기반 granule을 PX 서버에 분배해 스캔 | PX BLOCK ITERATOR | Starts/DOP와 총 A-Rows | 스캔량 판독 | 필수 | 미평가 |
| PX04 | PX SEND HASH | S | A | 조인/집계 키를 기준으로 해시 재분배 | PX SEND HASH | 이동량·키 | 재분배 필요성 | 필수 | 미평가 |
| PX05 | BROADCAST | S | A | 작은 입력을 모든 소비자 PX에 복제 | PX SEND BROADCAST | 작은 집합 크기×DOP | PQ_DISTRIBUTE | 필수 | 숙달 (2026-08-22) |
| PX06 | HASH HASH Distribution | S | A | 양쪽을 조인키 기준 재분배하는 대량↔대량 전략 | 양측 PX SEND HASH | 양측 이동량 | PQ_DISTRIBUTE | 필수 | 미평가 |
| PX07 | PARTITION Distribution | S | A | 파티션 배치에 맞춰 다른 입력을 분배 | PX SEND PARTITION(KEY) | PWJ 조건 | PQ_DISTRIBUTE | 필수 | 숙달 (2026-08-22) |
| PX08 | PQ_DISTRIBUTE 문법/Outer-Inner | S | A | `PQ_DISTRIBUTE(inner, outer_dist, inner_dist)`의 위치 의미를 정확히 판독 | Hint | Inner/Outer 식별 | 필수 | 숙달 (2026-08-22) |
| PX09 | DOP와 Starts 해석 | A | A | 병렬 Row Source의 Starts는 DOP/Slave set 구조와 연관되므로 단순 직렬 의미로 해석하지 않음 | Starts≈DOP 등 | 총 A-Rows/Slave | 필수 | 미평가 |
| PX10 | Parallel Aggregate | A | A | 부분집계→재분배→최종집계로 이동량 축소 가능 | HASH GROUP BY + PX SEND HASH | 1단/2단 집계 | 선집계 | 필수 | 미평가 |
| PX11 | Skew / Data Distribution | A | B | 해시 키 편중은 특정 PX에 작업 집중 | PX별 편차 | 키 분포 | 분배키/통계 검토 | 보강 | 미평가 |
| PX12 | Parallel DML/DDL | B | B | Query 병렬과 DML/DDL 병렬은 활성화·제약이 다름 | PX + DML/DDL | 세션/힌트/락 | 개념 | 미평가 |

## 2.13 DML / Batch / DDL

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 진단 포인트 | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|
| D01 | 대량 DELETE 비용 | S | A | 대량 row-by-row 삭제는 Undo/Redo, 인덱스 유지비용이 큼 | 삭제 비율/건수 | TRUNCATE/Partition 전략 검토 | 필수 | 취약 (2026-08-24) |
| D02 | DELETE + INSERT vs EXCHANGE | S | A | 파티션 대부분 교체 시 EXCHANGE 같은 구조적 교체가 유리할 수 있음 | 교체 비율 | 작업테이블 + EXCHANGE | 필수 | 취약 (2026-08-24) |
| D03 | CTAS | A | A | 대량 재구성/복제 시 집합기반·Direct Path 성격 활용 | 데이터량/후속 인덱스 | CTAS 검토 | 필수 | 취약 (2026-08-24) |
| D04 | Direct-Path INSERT / APPEND | A | B | 버퍼캐시를 우회하는 직접경로 적재로 대량 Insert 특성 변화 | 공간/락/Redo 조건 | APPEND 검토 | 보강 | 취약 (2026-08-24) |
| D05 | TRUNCATE | A | A | 전체/파티션 단위 제거에서 row-by-row DELETE와 다른 DDL 특성 | 범위 전체 여부 | TRUNCATE [PARTITION] | 필수 | 미평가 |
| D06 | MERGE | B | B | 대량 Upsert에서 조인/매칭 방식과 인덱스·DML 비용 고려 | matched/not matched 비율 | 소스 선필터/Join 개선 | 보강 | 미평가 |
| D07 | Undo/Redo | A | A | DML 방식 선택 시 논리적 작업량 외 로그·복구 비용 고려 | 대량 변경량 | Direct path/DDL 대안 | 필수 | 취약 (2026-08-24) |
| D08 | Lock/Concurrency | B | B | 장시간 대량 DML/DDL은 성능뿐 아니라 동시성 영향 고려 | lock duration | 작업단위/DDL 성격 | 보강 | 미평가 |
| D09 | 대량 UPDATE 튜닝 | S | A | 대량 UPDATE는 대상행 탐색비용뿐 아니라 변경 컬럼의 인덱스 유지, Undo/Redo, Lock 유지시간까지 함께 비용이 발생한다 | UPDATE 대상 건수, 변경 인덱스 수, Buffers/Redo/Undo/Lock | 조건 선택도 개선, 불필요 인덱스 영향 검토, 집합 UPDATE/MERGE/재구성 대안 비교 | 필수 | 숙달 (2026-08-25) |

## 2.14 Execution Plan / Runtime Statistics

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 지표 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|
| E01 | Starts | S | A | Row Source가 몇 번 시작됐는지. 반복 서브쿼리/NL/PX 판독 핵심 | Starts | 필수 | 숙달 (2026-08-31) |
| E02 | A-Rows | S | A | 실제 수행 결과 행수. Starts와 함께 총량/1회당 값을 구분 | A-Rows | 필수 | 미평가 |
| E03 | E-Rows | S | A | 옵티마이저 추정행수. A-Rows와 괴리 분석 | E-Rows | 필수 | 미평가 |
| E04 | Buffers | A | B | 논리 I/O 규모를 나타내는 핵심 런타임 지표 | Buffers | 보강 | 미평가 |
| E05 | Reads/Writes | B | B | 물리 I/O/Temp 쓰기 등과 병목 연계 | Reads/Writes | 보강 | 미평가 |
| E06 | A-Time / E-Time | B | B | 실제/추정 시간은 환경·병렬 누적 의미에 주의 | A-Time/E-Time | 보강 | 미평가 |
| E07 | OMem / 1Mem / Used-Mem | B | B | Sort/Hash workarea의 메모리 적합성 판단 | OMem/1Mem | 보강 | 미평가 |
| E08 | TempSpc | A | B | Hash/Sort spill의 직접 징후 | TempSpc | 보강 | 미평가 |
| E09 | Predicate Information | S | A | Access/Filter/Join predicate의 실제 적용 위치 확인 | Predicate Info | 필수 | 미평가 |
| E10 | Pstart/Pstop | S | A | Partition pruning 여부 확인 | Pstart/Pstop | 필수 | 미평가 |
| E11 | Row Source 데이터 흐름 | S | A | 들여쓰기만 보는 것이 아니라 자식→부모 입력과 Starts를 연결해 병목 판단 | Plan tree | 필수 | 미평가 |
| E12 | 필수 연산 vs 제거 가능 연산 | S | A | PX SEND, SORT, UNIQUE 등은 목적이 있으면 필수일 수 있음 | 연산 목적 | 필수 | 미평가 |

## 2.15 Data Model Semantics / Relationship

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 진단 포인트 | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|
| M01 | 관계 Cardinality 1:1 / 1:N / N:M | S | A | 테이블 관계의 다중성이 Join 출력 건수와 중복 발생 가능성을 결정 | PK/FK/UK, 조인 후 A-Rows | 관계를 먼저 명시한 뒤 Cardinality 계산 | 필수 | 미평가 |
| M02 | Optionality / Mandatory 관계 | A | A | 선택관계 여부에 따라 INNER/OUTER JOIN 사용 가능성이 달라지고 결과집합 보존 여부가 결정 | NULL 가능 FK, 업무 규칙 | INNER/OUTER 결과집합 비교 | 필수 | 미평가 |
| M03 | PK/FK 기반 결과집합 예측 | S | A | PK/FK는 Join Cardinality와 유일성 판단의 핵심 근거 | 1:N 증폭, N측 중복 | DISTINCT/Semi 필요성 판단 | 필수 | 미평가 |
| M04 | 데이터모델 → Join Semantics | S | A | 출력 요구가 존재확인인지 상세조회인지, 관계가 필수/선택인지에 따라 INNER/OUTER/SEMI/ANTI를 결정 | SELECT 컬럼, 관계 optionality | 논리적 관계를 먼저 확정 | 필수 | 미평가 |
| M05 | 유일성 증명과 DISTINCT 제거 | S | A | PK/UK/관계 제약으로 결과 유일성이 보장되면 불필요 DISTINCT 제거 가능 | Unique key, Join 관계 | 제거 전 결과집합 증명 | 필수 | 미평가 |

## 2.16 SQL 수행 구조 / Parse-Execute-Fetch / Database Call

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 징후 | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|
| SC01 | Parse / Execute / Fetch 구분 | A | A | SQL 수행은 Parse→Execute→Fetch 단계로 나뉘며 과도한 호출 위치가 성능 저하 원인이 될 수 있음 | Trace call count | 단계별 call/row 수 해석 | 필수 | 미평가 |
| SC02 | Hard Parse vs Soft Parse | A | A | 공유 가능한 커서가 없으면 Hard Parse 비용과 경합이 증가 | Parse CPU/Elapsed, library cache 관련 징후 | 바인드/공유성 점검 | 필수 | 미평가 |
| SC03 | Cursor Reuse / SQL Sharing | A | A | 동일 SQL 재사용이 Parse 부하와 Shared Pool 비용을 줄임 | 유사 SQL 다수/child cursor | Literal 남발 여부, 공유 실패 원인 점검 | 필수 | 미평가 |
| SC04 | Fetch Call 과다 | A | A | 작은 fetch array로 반복 네트워크/DB call이 발생하면 응답시간 증가 | Fetch calls 대비 rows | Array fetch 크기/애플리케이션 호출 방식 | 필수 | 미평가 |
| SC05 | Database Call 최소화 | A | A | Row-by-row 반복 호출보다 Set 기반 SQL이 DB call과 context switch를 줄임 | Execute/Fetch 반복 | SQL 집합화/Bulk 처리 | 필수 | 미평가 |
| SC06 | Row-by-row → Set Processing | A | A | 반복 SQL/루프 처리를 집합 SQL로 치환하면 호출·I/O·락 비용을 줄일 수 있음 | 동일 SQL 고빈도 실행 | MERGE/INSERT SELECT/집합 UPDATE 등 검토 | 필수 | 숙달 (2026-08-25) |
| SC07 | Bind Variable 활용 | A | A | 적절한 바인드는 SQL 공유성을 높이지만 분포 차이가 큰 컬럼에서는 계획 안정성 이슈와 함께 봐야 함 | literal SQL 다수, bind-sensitive | 공유성과 선택도 균형 | 필수 | 미평가 |
| SC08 | Database I/O 기본 구조 | A | B | Logical I/O와 Physical I/O, Buffer Cache 경유 여부를 구분해 SQL 비용을 해석 | Buffers, Reads, direct path 관련 지표 | 실행계획/Trace와 연계해 읽기 방식 판단 | 보강 | 미평가 |
| SC09 | Shared Pool / Library Cache 기본 | B | B | SQL 공유·파싱 비용은 Shared Pool/Library Cache의 커서 재사용 구조와 연결됨 | parse count, child cursor, library cache 관련 징후 | SQL 공유 실패 원인과 Parse 부하 연결 | 보강 | 미평가 |
| SC10 | PGA / Workarea 기본 | B | B | Sort/Hash/Bitmap 등 작업영역은 PGA/Workarea 크기에 따라 optimal/one-pass/multi-pass 및 Temp 사용이 달라짐 | OMem/1Mem/Used-Mem, TempSpc | 입력 축소/Workarea/Plan 변경 | 보강 | 미평가 |

## 2.17 SQL Trace / Response Time Analysis

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 지표 | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|
| T01 | SQL Trace Call Count | A | A | Parse/Execute/Fetch 횟수와 Rows를 함께 봐 호출 비효율을 판단 | call, count, rows | 과도한 call 축소 | 필수 | 미평가 |
| T02 | CPU vs Elapsed | A | A | Elapsed가 CPU보다 크면 I/O/대기/동시성 등 비CPU 요인을 의심 | cpu, elapsed | 추가 대기/IO/락 정보와 교차분석 | 필수 | 미평가 |
| T03 | Disk / Query / Current | A | A | 물리읽기, consistent get, current mode get을 구분해 I/O 특성을 판단 | disk/query/current | Access Path/DML 특성과 연계 | 필수 | 미평가 |
| T04 | Rows per Fetch | A | A | Fetch 호출 대비 반환 행수가 지나치게 작으면 애플리케이션 호출 비효율 가능 | fetch count, rows | Array Fetch/요청 구조 개선 | 필수 | 미평가 |
| T05 | SQL Trace + Execution Plan 교차분석 | S | A | Trace의 실제 비용과 Plan의 Row Source 흐름을 함께 봐 병목을 특정 | call stats + Plan | Starts/A-Rows/Buffers와 대조 | 필수 | 미평가 |
| T06 | TKPROF 기본 해석 | B | B | Trace 집계를 SQL 단위로 정리해 CPU/Elapsed/I/O/Rows를 비교 | TKPROF report | 고비용 SQL 우선순위화 | 보강 | 미평가 |
| T07 | Response Time Breakdown | A | A | 응답시간을 DB CPU, I/O, 대기, 호출구조 등으로 분해하여 원인별 개선 | elapsed 구성 | 병목 유형별 개선안 | 필수 | 미평가 |

## 2.18 Lock / Transaction / Concurrency

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 징후 | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|
| L01 | TX Row Lock Contention | A | A | 동일 행/키에 대한 동시 DML은 TX 대기를 유발할 수 있음 | row lock wait | 트랜잭션 범위/접근순서 개선 | 필수 | 미평가 |
| L02 | TM Lock / DML Lock | B | B | 테이블 수준 DML lock은 DDL 및 일부 참조무결성 상황과 충돌할 수 있음 | TM enqueue | FK/index/DDL 시점 점검 | 보강 | 미평가 |
| L03 | Blocking / Waiting Session | A | A | 대기 세션만 보지 말고 blocker와 트랜잭션 원인을 찾아야 함 | blocker/waiter | blocker SQL/트랜잭션 분석 | 필수 | 미평가 |
| L04 | Long Transaction | A | A | 긴 트랜잭션은 락 유지시간, Undo 사용량, 장애복구 부담을 키움 | long txn/undo 증가 | 작업 단위 재설계 | 필수 | 미평가 |
| L05 | Commit Frequency | A | A | 너무 잦은 Commit과 너무 큰 트랜잭션 모두 비용/일관성 측면의 trade-off가 있음 | commit wait/redo/lock duration | 업무 단위 기준 설계 | 필수 | 미평가 |
| L06 | Hot Block / Hot Key | B | B | 특정 블록/키에 동시 접근이 집중되면 경합이 발생 | latch/enqueue/segment contention | 키 분산/설계 변경 | 보강 | 미평가 |
| L07 | DML + Index Maintenance Concurrency | B | B | 인덱스 수와 구조가 동시 DML 비용과 경합에 영향 | DML latency | 불필요 인덱스 제거/키 분산 | 보강 | 미평가 |

## 2.19 Performance Troubleshooting

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 대표 징후 | 대응 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|---|---|
| TR01 | CPU-bound SQL | A | A | 논리 I/O, 연산량, 함수/정렬/해시 과다가 CPU를 소비 | CPU high, elapsed≈CPU | SQL 연산량/Logical I/O 축소 | 필수 | 미평가 |
| TR02 | I/O-bound SQL | A | A | 많은 블록 읽기나 비효율 Access Path가 응답시간을 지배 | Reads/Buffers high | Access/Index/Partition 개선 | 필수 | 미평가 |
| TR03 | Excessive Logical I/O | S | A | 물리 I/O가 없어도 과도한 buffer get은 CPU와 latch 부담을 키움 | Buffers/query high | 읽는 row/block 수 축소 | 필수 | 미평가 |
| TR04 | Physical I/O 증가 | A | A | Cache miss·대량 FTS·Temp spill 등이 실제 디스크 읽기를 증가시킬 수 있음 | disk reads high | Working set/Access/Temp 원인 구분 | 필수 | 미평가 |
| TR05 | Parse Bottleneck | A | A | Hard Parse/공유 실패가 CPU와 library cache 경합을 유발 | parse count high | bind/share/SQL 구조 개선 | 필수 | 미평가 |
| TR06 | Lock/Concurrency Bottleneck | A | A | SQL 자체 비용보다 대기/블로킹이 응답시간을 지배할 수 있음 | elapsed≫CPU, enqueue wait | blocker/transaction 개선 | 필수 | 미평가 |
| TR07 | Temp Spill Bottleneck | A | A | Sort/Hash가 메모리를 초과하면 Temp I/O로 응답시간 급증 | TempSpc/1-pass/multi-pass | 입력 축소/Workarea/방법 변경 | 필수 | 미평가 |
| TR08 | Parallel Skew | A | B | PX간 데이터/작업량 편중으로 일부 slave가 병목 | PX별 편차 | 분배키/Skew 개선 | 보강 | 미평가 |
| TR09 | Cardinality Error Cascade | S | A | 잘못된 추정이 Access→Join Order→Join Method→Memory 사용으로 연쇄 전파 | E/A Rows 괴리 + bad plan | 통계/Predicate 근본 원인 수정 | 필수 | 미평가 |
| TR10 | Troubleshooting Decision Tree | S | A | 증상을 CPU/I/O/Parse/Lock/Temp/PX/SQL 구조로 분류한 뒤 증거 기반으로 원인을 좁힘 | 여러 런타임 지표 | Trace/Plan/Runtime 지표 교차검증 | 필수 | 미평가 |

## 2.20 Plan Stability / Runtime Adaptation / 기타 Oracle 튜닝

> 아래는 Oracle 튜닝 이론 Coverage를 위한 영역이다. 현재 프로젝트 소스에서 SQLP 직접 출제 근거가 상대적으로 약하므로 **B/C 우선순위**로 관리한다.

| ID | 패턴 | 중요도 | SQLP 근거 | 핵심 원리 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|
| X01 | Optimizer Mode ALL_ROWS/FIRST_ROWS | B | C | 목표 응답 특성이 비용모델/계획 선택에 영향 | 개념+복합 | 미평가 |
| X02 | SQL Plan Baseline | C | C | 검증된 Plan 집합을 이용한 Plan 안정화 | 개념 | 미평가 |
| X03 | SQL Profile | C | C | 옵티마이저 추정 보조 정보로 계획 개선 가능 | 개념 | 미평가 |
| X04 | SQL Patch | C | C | SQL 텍스트 변경 없이 힌트성 제어 적용 가능 | 개념 | 미평가 |
| X05 | Adaptive Plan | C | C | 런타임 정보에 따라 일부 계획 의사결정이 적응 | 개념 | 미평가 |
| X06 | Bloom/Join Filter | B | C | 대량/병렬 조인에서 Probe 측 스캔을 줄이는 필터 | PX 복합문제 보조 | 미평가 |
| X07 | Workarea One-pass/Multi-pass | B | C | Hash/Sort 메모리 부족 정도가 Temp I/O를 결정 | Sort/Hash 복합 | 미평가 |
| X08 | Cursor Sharing / Child Cursor | C | C | SQL 공유와 환경/바인드 차이가 커서 수와 계획에 영향 | 개념 | 미평가 |
| X09 | IOT / Cluster Access | C | C | 특수 저장구조에 따른 Access Path | 저우선 | 미평가 |
| X10 | System/Wait 기반 성능진단 | C | C | SQL 튜닝 외 시스템/세션 병목 진단 축. 현재 프로젝트의 SQLP 실기 직접 출제근거는 부족 | 별도 보조 Coverage | 미평가 |
| X11 | AWR / ASH / ADDM 기본 위치 | C | C | 시스템/세션 성능 트러블슈팅 도구이지만 현재 프로젝트 기준 SQLP 실기 직접 출제 깊이는 불확실 | 개념 위치만 확인 | 미평가 |
| X12 | SQL Monitor 기본 위치 | C | C | 장시간/병렬 SQL의 실시간 실행 통계를 볼 수 있는 도구이지만 직접 출제 근거는 약함 | 개념 위치만 확인 | 미평가 |
| X13 | Optimizer Parameter 영향 | C | C | 일부 옵티마이저 파라미터가 변환/비용/Adaptive 동작에 영향을 줄 수 있으나 시험 답안은 가급적 SQL/통계/힌트 중심으로 접근 | 개념 | 미평가 |

## 2.21 SQLP 공식범위 안전망 / SQL 활용·문법

> 이 영역은 **SQLP 자격 전체 공식 범위 누락 방지용 안전망**이다. SQL 실기 튜닝의 핵심 S/A 학습축과 분리하며, 2회독 실기 진도를 지연시키지 않는다.

| ID | 항목 | 중요도 | SQLP 근거 | 핵심 의미 | 2회독 처리 | 숙련도 |
|---|---|---|---|---|---|---|
| F01 | 계층형 질의 / SELF JOIN | B | B | 계층형 관계 표현과 자기참조 Join의 SQL 의미를 이해한다. 실기에서는 결과집합/Join 의미 보존 관점으로만 연결 | 개념+보조문제 | 미평가 |
| F02 | PIVOT / UNPIVOT | C | B | 행↔열 변환 문법. 실기 튜닝 직접성은 낮으므로 문법 의미와 결과집합만 확인 | 개념 확인 | 미평가 |
| F03 | 정규표현식 함수 | C | B | REGEXP 계열 조건/가공의 SQL 의미를 이해한다. 필요 시 함수가 Predicate/CPU 비용에 미치는 영향만 연결 | 개념 확인 | 미평가 |
| F04 | TCL | C | B | COMMIT/ROLLBACK/SAVEPOINT 등 트랜잭션 제어 문법. 성능 측면은 L05/D07과 연결 | 개념 확인 | 미평가 |
| F05 | DCL | C | B | GRANT/REVOKE 등 권한 제어 문법. SQL 튜닝 실기 직접성은 매우 낮음 | 개념 확인 | 미평가 |
| F06 | 기본 SQL 문법 Safety Net | C | A | SELECT/WHERE/GROUP BY/HAVING/ORDER BY/집합연산/NULL 처리의 의미를 정확히 보존해야 튜닝 Rewrite 결과집합 검증 가능 | 객관식/기초 복습으로 분리 | 미평가 |


---

# 3. 복합 패턴맵

| ID | 복합 패턴 | 결합 원자 패턴 | 핵심 진단 | 대표 개선 방향 | 중요도 |
|---|---|---|---|---|---|
| CP01 | 1:N Join 증폭 → DISTINCT | J10 + C09 + O02/O03 | 조인 후 대량 증폭 뒤 Unique | 존재만 필요하면 Semi Join, 선집계 | S |
| CP02 | EXISTS가 일반 Join으로 잘못 Rewrite → 중복 | J07 + R01/R02 | 결과집합 증가 | Semi 성격 보존 | S |
| CP03 | NOT EXISTS FILTER 반복 → Anti Join | Q01 + J08 + R03 | Inner Starts 폭증 | Anti Join/Unnest | S |
| CP04 | Scalar Subquery 반복 + GROUP BY | Q03 + G01/G02 | 동일 테이블 반복 + 외부집계 | Join + 사전집계 | S |
| CP05 | Optional Predicate + 단일 Plan | P05 + A01/A03 + R05 | NULL/NOT NULL 호출의 선택도 극단 차이 | UNION ALL/분기 | S |
| CP06 | 컬럼가공 + Index 미사용 | P01/P03 + A03 | FTS/Filter 증가 | 조건 범위 재작성/FBI | S |
| CP07 | 암묵변환 + Join Access 악화 | P02 + J01/A03 | Inner Index 미사용/추정오류 | 타입 일치 | S |
| CP08 | 잘못된 Cardinality → 잘못된 Join Order/Method | S01 + J04/J01/J02 | E/A Rows 괴리 후 계획 연쇄오류 | 통계/Predicate 수정 | S |
| CP09 | NL Outer 과대 + Inner 반복 접근 | J01 + E01 + A09 | Inner Starts 과다 | Outer 축소/Hash 전환/Access 개선 | S |
| CP10 | Hash Join 대량 + Temp Spill | J02 + O06/E08 | Hash 입력 크고 Temp 발생 | 선필터/선집계/메모리 | A |
| CP11 | Join 후 GROUP BY vs 선집계 | J10 + G03 | 중간건수 폭증 | 다측 선집계 | S |
| CP12 | Top-N + WINDOW SORT 대량 | G05/G09 + G07 | 전체 분석 후 소수 결과 | Stopkey/Index ordered access | S |
| CP13 | ORDER BY + Index 순서 활용 | O01 + A04/A08 | Sort 제거 가능성 | 인덱스 순서 설계 | A |
| CP14 | Partition Key 가공 → Pruning 실패 | PT04 + P01 | PARTITION RANGE ALL | 조건 재작성 | S |
| CP15 | Pruning 실패 + Parallel Full Scan | PT04 + PX03 | 불필요 파티션 전체 병렬 스캔 | Pruning 복구 | S |
| CP16 | Pruning 실패 + PX HASH Redistribution | PT04 + PX04/PX06 | 스캔량+이동량 동시 증가 | Pruning/PWJ | S |
| CP17 | Full PWJ인데 HASH HASH 재분배 | PT05 + PX06 | 불필요 양측 PX SEND HASH | 로컬 파티션 조인 활용 | S |
| CP18 | Partial PWJ + PARTITION(KEY) | PT06 + PX07 | 한쪽만 파티션 | 비파티션측 partition distribution | S |
| CP19 | 대량↔소량 조인 + Broadcast | PX05 + J02 | 작은 집합 복제 | 적정 Broadcast 선택 | S |
| CP20 | 대량↔대량 + HASH HASH | PX06 + J02 | 양측 재분배 | 필요성 검증/PWJ 가능성 | S |
| CP21 | Parallel Aggregate 2단계 | PX10 + G01 | 로컬집계 후 그룹키 재분배 | 부분집계 활용 | A |
| CP22 | DELETE 대량 + Undo/Redo 폭증 | D01 + D07 | row-by-row 대량 변경 | TRUNCATE/CTAS/Partition 전략 | S |
| CP23 | 파티션 대부분 교체 + DELETE/INSERT | D02 + PT09 | 불필요 대량 DML | EXCHANGE PARTITION | S |
| CP24 | Partition DDL + Global Index 관리 | PT08 + D08 | 인덱스 unusable/유지비용 | UPDATE INDEXES/설계 검토 | A |
| CP25 | OR 조건 + 서로 다른 인덱스 선택도 | P07 + Q07 + R05 | 단일 Access Path 비효율 | OR Expansion/UNION ALL | S |
| CP26 | View + Predicate 미Push | Q05/Q06 + C01 | 뷰 전체 처리 후 외부필터 | Merge/Push 가능성 검토 | A |
| CP27 | WITH Materialization + 과도한 Temp | Q08 + O06 | 중간집합 저장비용 | Inline/재사용 횟수 비교 | B |
| CP28 | DISTINCT 제거 후 결과집합 변형 | R07 + R01 | 중복 의미 오판 | PK/FK/유일성 증명 후 제거 | S |
| CP29 | Outer Join + Filter 위치 변경 | J06 + R01 | 보존행 소실 | ON/WHERE 의미 검증 | S |
| CP30 | NOT IN NULL 함정 + Anti Rewrite | P09 + J08 | 결과집합 불일치 | NOT EXISTS와 NULL 조건 검증 | S |
| CP31 | FILTER Subquery 조기 수행 → 후속 Join 입력 감소 | Q01 + Q13/Q14 + J04 | 서브쿼리를 일찍 수행하면 많은 행이 제거되어 후속 조인량 감소 | PUSH_SUBQ 검토 | A |
| CP32 | 고비용 Subquery 조기 수행 → PUSH_SUBQ 역효과 | Q13/Q14 + E01 | 제거율보다 반복 수행비용이 커 전체비용 증가 | NO_PUSH_SUBQ 또는 Unnest 검토 | A |
| CP33 | UNNEST vs FILTER 유지 + PUSH_SUBQ | Q02 + Q13/Q14 + R13/R15 | 조인 변환과 수행시점 제어를 혼동 | 먼저 논리적 변환 가능성, 이후 수행시점 판단 | S |
| CP34 | Optional Relationship + INNER JOIN → 행 소실 | M02 + M04 + J06 | 선택관계를 필수관계처럼 처리해 결과집합 변경 | OUTER JOIN/조건 위치 재검증 | S |
| CP35 | 1:N 관계 + DISTINCT | M01/M03 + J10 + O02/O03 | 관계 다중성으로 중복 발생 | Semi Join/선집계/유일성 증명 | S |
| CP36 | Parse 과다 + Literal SQL | SC02/SC03/SC07 + TR05 | SQL 공유 실패로 Hard Parse 증가 | Bind/공유 구조 개선 | A |
| CP37 | Fetch Call 과다 + 소량 Array Fetch | SC04 + T04 | 네트워크/DB call 증가 | Array Fetch/호출구조 개선 | A |
| CP38 | Row-by-row Application Call + 반복 SQL | SC05/SC06 + T01 | Execute/Fetch 호출 폭증 | Set Processing/Bulk | A |
| CP39 | Lock Wait + Long Transaction | L01/L03/L04 + TR06 | SQL 비용보다 Blocking 시간이 지배 | blocker/transaction 범위 개선 | A |
| CP40 | Temp Spill + Hash/Sort 대량 | O06 + E08 + TR07 | PGA 초과 후 Temp I/O 급증 | 입력 축소/Workarea/Plan 변경 | A |
| CP41 | Predicate Transitivity → Index Access 개선 | Q15 + P10 + A03 | 파생된 조건이 인덱스 Access Predicate로 사용되어 스캔 범위 축소 | 조건 전이 가능성과 데이터 타입/NULL 의미 검증 | A |
| CP42 | Hash Join + SWAP_JOIN_INPUTS | J02/J05 + R16 | Build/Probe 역할이 비효율적이거나 메모리/Temp가 증가 | Join Order와 입력 역할을 함께 검증 | A |
| CP43 | OR Expansion + USE_CONCAT/NO_EXPAND | Q07 + R17 + P05/P07 | 분기별 Access Path 차이를 옵티마이저 변환/힌트로 제어 | 결과 중복/분기 배타성 검증 | A |
| CP44 | Logical I/O 과다 + Database Call 반복 | SC05/SC08 + TR03 | SQL 자체 블록 접근과 애플리케이션 반복 호출이 동시에 비용 증가 | Set Processing + Access Path 개선 | A |
| CP45 | 대량 UPDATE + 인덱스 유지 + Undo/Redo/Lock 증가 | D09 + D07 + L01/L04/L05 | 대상행은 많고 변경 컬럼이 여러 인덱스에 포함되어 DML 비용과 트랜잭션 부담이 동시 증가 | 대상행 축소, 인덱스 영향 검토, 작업단위/집합처리/재구성 대안 비교 | S |

---

# 4. 기존 v1의 주요 수정 사항

1. **패턴 범위 확대**
   - v1의 예시 4개 중심 구조를 15개 상위 영역과 원자/복합 패턴으로 확장.

2. **Nested Loops 설명 수정**
   - 기존: `Inner쪽에 인덱스 필수`
   - 수정: Inner 인덱스는 대표적인 효율화 수단이지만 **논리적·물리적으로 필수는 아님**. 실제 비용은 Outer 건수 × Inner Row Source 1회 처리비용과 Starts로 판단.

3. **NL Cardinality 설명 수정**
   - 기존의 `NL Outer A-Rows × NL Inner Starts` 식 표현은 부정확.
   - 수정: Outer A-Rows는 Inner Starts를 유발하는 주요 요인이며, NL 출력은 실제 조인 매칭 건수의 합으로 결정. `Starts`, `A-Rows`, 1회당 Inner 결과를 분리해서 본다.

4. **Subquery Unnesting 설명 수정**
   - 기존: EXISTS/ANY를 JOIN으로 변환하며 `SEM(H)` 처리라는 단순화.
   - 수정: Unnesting은 서브쿼리 QB를 조인 가능한 형태로 변환하는 최적화이며, 서브쿼리 의미에 따라 Semi/Anti/일반 Join 등 여러 결과가 가능. 변환 가능성은 SQL 의미와 제약에 좌우됨.

5. **Semi Join 설명 정교화**
   - `Semi Join은 중복을 제거한다`가 아니라, **내부측 중복이 외부행을 여러 번 출력시키지 않는 존재성 조인**으로 표현.

6. **FTS/PX SEND 단정 금지**
   - Full Scan 또는 PX SEND가 보인다는 사실만으로 병목으로 판정하지 않는다. 처리해야 할 데이터량, Pruning, 분배 목적, Buffers/Temp 등과 함께 판단.

7. **숙련도 임의기재 제거**
   - v1 예시의 미숙달/부분숙달 등은 실제 기록 근거가 없으므로 전부 `미평가`로 초기화.

---

# 5. SQLP 출제경향 대비 누락 점검표

| 검증 축 | 패턴맵 반영 | 주요 ID |
|---|---|---|
| 상수/범위 vs 가공 컬럼 | 완료 | P01~P05, CP06 |
| Index 사용/설계 | 완료 | A02~A12, I01~I08 |
| NL/Hash/Merge | 완료 | J01~J05 |
| Join Order | 완료 | J04 |
| Semi/Anti | 완료 | J07/J08, R02/R03 |
| Cardinality/Starts/A-Rows | 완료 | C01~C10, E01~E03 |
| DISTINCT/중복 증폭 | 완료 | C09, O02/O03, CP01 |
| Top-N/Stopkey/Analytic | 완료 | G05~G10 |
| Group By | 완료 | C08, G01~G04 |
| Partition Pruning | 완료 | PT02~PT04 |
| Full/Partial PWJ | 완료 | PT05/PT06 |
| PX SEND/Receive | 완료 | PX01~PX08 |
| Hash/Broadcast/Partition Distribution | 완료 | PX04~PX08 |
| DDL/대량 배치 | 완료 | D01~D08, PT09/PT10 |
| 결과집합 동일성 | 완료 | R01 및 모든 Rewrite 복합패턴 |
| AS-IS→Rewrite→TO-BE 검증 | 완료 | 전체 운영원칙 |
| PUSH_SUBQ / NO_PUSH_SUBQ | 완료(v2.1) | Q13/Q14, R15, CP31~CP33 |
| 데이터모델 관계/Optionality | 완료(v2.1) | M01~M05, CP34/CP35 |
| Parse/Execute/Fetch / DB Call | 완료(v2.1) | SC01~SC07 |
| SQL Trace / 응답시간 분석 | 완료(v2.1) | T01~T07 |
| Lock / Transaction / Concurrency | 완료(v2.1) | L01~L07 |
| Performance Troubleshooting | 완료(v2.1) | TR01~TR10 |
| Predicate Transitivity | 완료(v2.2) | Q15, CP41 |
| Table Expansion | 보조 Coverage(v2.2) | Q16 |
| Common Expression Elimination | 보조 Coverage(v2.2) | Q17 |
| Set Operation→Join Rewrite | 보조 Coverage(v2.2) | Q18 |
| SWAP_JOIN_INPUTS / NO_SWAP_JOIN_INPUTS | 완료(v2.2) | R16, CP42 |
| USE_CONCAT / NO_EXPAND | 완료(v2.2) | R17, CP43 |
| System Statistics | 보조 Coverage(v2.2) | S10 |
| DB I/O / Shared Pool / PGA 기본 | 완료(v2.2) | SC08~SC10 |
| AWR/ASH/ADDM/SQL Monitor | 저우선 Coverage(v2.2) | X11/X12 |
| 대량 UPDATE 튜닝 | 완료(v2.3) | D09, CP45 |
| 계층형 질의 / SELF JOIN | 공식범위 안전망(v2.3) | F01 |
| PIVOT / UNPIVOT | 공식범위 안전망(v2.3) | F02 |
| 정규표현식 | 공식범위 안전망(v2.3) | F03 |
| TCL / DCL | 공식범위 안전망(v2.3) | F04/F05 |
| 기본 SQL 문법 | 공식범위 안전망(v2.3) | F06 |

---

# 6. Oracle 튜닝 이론 Coverage 분리

## 6.1 SQLP 실전 직접 Coverage
- Cardinality / Selectivity
- Predicate / Sargability
- Index / Access Path
- Join / Join Order / Semi / Anti
- Subquery / Query Transformation 핵심
- SQL Rewrite / Hint / Query Block
- Sort / DISTINCT / Aggregate / Top-N
- Partition / PWJ
- Parallel / PQ Distribution
- DML / Batch / Partition DDL / 대량 UPDATE
- Execution Plan Runtime Statistics
- Data Model Semantics / Relationship
- SQL 수행 구조 / Parse-Execute-Fetch / Database Call
- SQL Trace / Response Time Analysis
- Lock / Transaction / Concurrency
- Performance Troubleshooting

## 6.2 SQLP 공식범위 저우선 안전망
- 계층형 질의 / SELF JOIN
- PIVOT / UNPIVOT
- 정규표현식
- TCL / DCL
- 기본 SQL 문법 의미 보존

## 6.3 Oracle 튜닝 보조 Coverage
- Histogram / Extended Statistics
- Bind Peeking / ACS
- Dynamic Statistics / Feedback
- Bitmap / FBI / Skip Scan 등 세부 Access
- Materialization / Join Factorization / Join Elimination / Star Transformation
- Plan Baseline / Profile / Patch
- Adaptive Plan
- Bloom Filter
- Workarea One-pass/Multi-pass
- Wait/System 관점 진단
- Predicate Transitivity / Table Expansion / Common Expression Elimination
- System Statistics / Optimizer Parameter 영향
- AWR / ASH / ADDM / SQL Monitor의 위치와 역할(저우선)

> 이 보조 Coverage는 “『오라클 성능 고도화 원리와 해법』 전체를 완전히 망라했다”는 의미가 아니다. 현재 프로젝트에 책의 전체 원문/전체 목차 대조표가 없으므로 **교재 전체 Coverage 보장은 불가**하다. 향후 교재 목차 또는 사용자 보유 소스를 입력받으면 `교재 장/절 ↔ Pattern ID` 역대조표를 추가한다.

---

# 7. 2회독 운영 기준

## 7.1 우선순위
1. **S 패턴**: 테마별 날짜를 지정하고 해당 날짜 내 기본→중급→고급을 진행. 한 패턴을 무제한 파지 않음.
2. **A 패턴**: S 테마와 결합하여 출제. 독립 훈련은 취약할 때만.
3. **B 패턴**: 복합문제에서 보조축으로 등장.
4. **C 패턴**: 개념 확인 위주. 2회독 진도를 늦추지 않음.

## 7.2 한 테마 종료 조건
- 병목 Row Source 식별
- 건수 흐름/Starts 계산
- 논리적 관계(일반/Semi/Anti/Outer) 판정
- SQL/Hint/Index/DDL 개선안 제시
- 결과집합 동일성 설명
- 예상 TO-BE Plan의 핵심 Row Source 설명

## 7.3 숙련도 판정
- **미학습**: 원리 설명 불가
- **미숙달**: 단독 패턴에서도 반복 오류
- **부분숙달**: 단독은 가능하지만 복합에서 오류
- **숙달**: 테마 비공개 상태에서 식별→개선→검증 독립 수행

## 7.4 출제 방식
- 기본 출력 순서: `1. AS-IS 병목 판단 → 2. SQL + Hint/Index/DDL 재작성 → 3. TO-BE 실행계획 예상`
- 초급: 단일 S 패턴
- 중급: S + A 2~3개
- 고급: S/A 다수 + Cardinality 연쇄
- 실전: 테마 비공개 + 불필요 Row Source/힌트 함정 + 결과집합 검증

---

# 8. 문제 생성 시 필수 검수 체크리스트

1. SQL과 Execution Plan 일치 여부
2. AS-IS와 TO-BE 구분
3. Starts / A-Rows / 단계별 Cardinality 재계산
4. 일반 Join / Semi / Anti / Outer의 논리적 관계
5. NL / Hash / Merge의 물리적 수행 가능성
6. Partition / PX 계획의 데이터 흐름
7. Hint가 정확한 QB/테이블에 적용되는지
8. 제거한다고 한 Row Source가 실제로 불필요한지
9. 개선 SQL과 원본 SQL의 결과집합 동일성
10. Top-N/NULL/중복/Outer Join 의미 보존
11. 제안 TO-BE가 물리적으로 가능한 Plan인지
12. 문제 수치와 Plan의 Starts/A-Rows가 서로 모순되지 않는지
13. 최소 1회 추가 검산

---

# 9. 최종 감사 후 남는 불확실성

현재 v2.3은 **SQLP 실기 2회독 마스터 패턴맵**으로 사용 가능하며, 공식 SQLP 전체 범위에서 실기와 직접 연결되지 않는 문법/활용 항목도 F01~F06 안전망으로 표시했다.

다만 다음 항목은 “SQLP 실기 필수”라고 단정할 공식 근거가 충분하지 않다.

- 개별 Wait Event의 세부 암기 수준
- AWR/ASH/ADDM/SQL Monitor의 실제 실기 출제 깊이
- TKPROF 세부 옵션·도구 운용법
- SQL Plan Management / SQL Profile / SQL Patch의 실기 직접 출제 가능성
- Star Transformation / MV Rewrite / Table Expansion / IOT / Cluster 등의 직접 출제 가능성
- 모든 Optimizer Parameter의 시험 직접성
- 『오라클 성능 고도화 원리와 해법』 전 장/절의 완전 대조

따라서 위 항목은 B/C 저우선 Coverage로 유지하고, **S/A 학습 일정의 진도를 방해하지 않는다**.

---

# 10. v2.3 최종 사용 선언

이 v2.3 문서를 2회독의 **마스터 패턴 인덱스**로 사용한다.

- 학습계획은 S/A 패턴의 누락 여부를 이 문서로 확인한다.
- 문제 출제는 Pattern ID를 내부적으로 지정하되 숙련 단계에서는 사용자에게 테마를 노출하지 않는다.
- 오답 발생 시 해당 Pattern ID와 복합 Pattern ID를 함께 기록한다.
- 특정 패턴이 실제 문제에서 안정적으로 재현되면 숙련도를 갱신한다.
- 새로운 SQLP 근거 또는 교재 소스가 추가되면 이 문서에 먼저 반영한 뒤 학습계획을 수정한다.
- 현재 기준으로 `SQLP 실기 2회독 범위 누락 여부`는 이 문서를 기준으로 판단해도 된다.
- SQLP 자격 전체 범위의 문법/활용 누락 여부는 F01~F06 안전망까지 포함하여 판단한다.
- 단, B/C 보조영역은 '시험 필수'가 아니라 공식/Oracle 이론 Coverage를 위한 안전망으로 취급한다.


---

# 11. v2.3 최종 심층 리서치 반영 내역

## 11.1 실제 신규 추가
- Q15 Predicate Transitivity
- Q16 Table Expansion
- Q17 Common Expression Elimination
- Q18 Set Operation → Join Rewrite
- R16 SWAP_JOIN_INPUTS / NO_SWAP_JOIN_INPUTS
- R17 USE_CONCAT / NO_EXPAND
- S10 System Statistics
- SC08 Database I/O 기본 구조
- SC09 Shared Pool / Library Cache 기본
- SC10 PGA / Workarea 기본
- X11 AWR / ASH / ADDM 기본 위치
- X12 SQL Monitor 기본 위치
- X13 Optimizer Parameter 영향
- CP41~CP44 복합패턴

## 11.2 심층 리서치에서 누락으로 지적됐으나 이미 v2.1에 존재하여 중복 추가하지 않은 항목
- PUSH_SUBQ / NO_PUSH_SUBQ → Q13/Q14, R15
- View Merge → Q05
- Materialized View Rewrite → Q12
- Star Transformation → Q11
- Join Factorization → Q09
- Join Elimination → Q10
- OR Expansion → Q07
- Bind Peeking / ACS → S06/S07
- Extended Statistics → S05
- SQL 수행구조 / DB Call → SC01~SC07
- Lock / Transaction → L01~L07
- 데이터모델 Optionality → M01~M05

## 11.3 최종 판정
- **SQLP 실기 직접 핵심 Coverage:** 마스터 패턴맵으로 사용 가능
- **SQLP 공식 과목 전체의 이론 Coverage:** 주요 축 포함, 일부 고급/도구 영역은 B/C 안전망으로 관리
- **『오라클 성능 고도화 원리와 해법』 전체 Coverage:** 책 전체 목차 1:1 대조가 없으므로 완전 보장은 하지 않음


## 11.4 v2.3 추가 반영
- D09 대량 UPDATE 튜닝 — S / 근거 A
- CP45 대량 UPDATE + 인덱스 유지 + Undo/Redo/Lock
- F01 계층형 질의 / SELF JOIN — B
- F02 PIVOT / UNPIVOT — C
- F03 정규표현식 — C
- F04 TCL — C
- F05 DCL — C
- F06 기본 SQL 문법 Safety Net — C

## 11.5 최종 결론
- **SQLP 실기 직접 핵심:** 추가 보완 후 별도 중대 누락 없음
- **SQLP 자격 전체 범위:** 실기 핵심과 저우선 문법 안전망을 구분하여 추적 가능
- **운영 원칙:** S/A만 2회독 실전 문제화의 중심으로 사용하고, F/B/C 영역은 객관식·기초 복습 또는 복합문제 보조용으로 사용



---

## [2026-09-03 갱신] Cycle B03 — 서브쿼리/쿼리변환 보강 세션 반영

- **반영 근거:** 2026-09-03 B03 세션 3문항 채점 결과 (35 / 30 / 48점)
- **숙달 승격:** `J04` (부분숙달 → 숙달) — Driving 선정 및 인덱스 대상 테이블 선택 2회 연속 정확
- **숙달 유지·날짜 갱신:** `Q01`, `J07`, `G01`
- **숙달 → 부분숙달 하향:** `Q02`, `Q03`, `R04`, `I01`
- **부분숙달 → 취약 하향:** `R13`, `R15`, `Q14`, `R09`
- **3회 연속 미해소 경보:** `R13` / `R15` / `Q14` (NO_UNNEST + PUSH_SUBQ 접근안 미제출), `R09` (UNNEST 시 LEADING 2순위 배치)
- **차기 조치:** Cycle B03-R(재도전) 세션에서 위 4개 Pattern ID 단독 변형 문항으로 정면 재출제
