# SQLP 실기 검증된 출제경향 및 시험전략 v1.1

- **기준일:** 2026-08-11
- **마스터 범위 문서:** `SQLP_실기_2회독_통합패턴맵_v2_3_최종확정`
- **문서 목적:** SQLP 실기 대비에서 확인된 출제형식·핵심 경향과, 공식/Oracle 이론 Coverage를 분리하여 학습 우선순위를 판단한다.
- **예상 시험일:** `2027-03-06`은 기존 프로젝트에서 사용하는 **가정일**이며 공식 확정일로 취급하지 않는다.

---

# 1. 정보 신뢰도 기준

- **A:** 공식 발표/공식 문서 또는 프로젝트에서 공식근거로 검증된 내용
- **B:** 복수 자료와 Oracle 원리가 교차 지지하는 내용
- **C:** 제한적 사례 또는 간접 근거
- **D:** 추정. 단독 출제근거로 사용하지 않음

복원문제·후기 기반 정보는 공식자료와 동일한 수준으로 취급하지 않는다.

# 2. 공개자료의 한계

- 공개된 과거 기출/복원 자료는 전체 시험을 완전하게 대표한다고 단정할 수 없다.
- 특정 회차/후기에 등장했다는 이유만으로 `항상 출제`, `필수 Hint`, `고정 Plan 형태`로 일반화하지 않는다.
- 출제경향과 Oracle 기능의 존재 여부를 구분한다.

# 3. 실기 문제 형식에 대한 운영 가정

프로젝트에서 확인·정리한 문제 형식은 다음 세 축으로 관리한다.

1. **AS-IS Only 진단형**: AS-IS SQL/Plan을 보고 문제를 진단하고 개선안을 작성
2. **목표 Plan 역설계형**: 목표 TO-BE Plan 또는 일부 목표를 보고 SQL/Hint를 구성
3. **부분 TO-BE 혼합형**: 일부 Plan/Hint만 주고 나머지를 추론

중요: `언제나 TO-BE가 제공된다` 또는 `언제나 제공되지 않는다`고 가정하지 않는다.

기존 v1의 `AS-IS Only 최근 사례 많음 = 신뢰도 A` 표현은 공식근거와 복원자료 근거가 혼재할 수 있으므로, **공식근거가 별도 확인되지 않는 한 B 이하로 보수적으로 취급**한다.

# 4. 실기 직접 핵심 경향

현재 프로젝트 소스에서 실기 직접성이 높은 축은 다음과 같다.

- Cardinality / Selectivity / Starts / A-Rows
- Predicate 가공, 암묵변환, 날짜 범위 재작성
- Index Access 및 복합인덱스 설계
- NL / Hash / Merge 및 Join Order
- Semi / Anti / Outer / 1:N 결과집합 의미
- Scalar Subquery / Unnest / OR Expansion 등 핵심 Transformation
- DISTINCT / GROUP BY / Top-N / Sort
- Partition Pruning
- Full / Partial Partition-Wise Join
- Parallel Execution / PX Distribution
- DML / Batch / Partition DDL / 대량 UPDATE
- 개선 SQL의 결과집합 동일성

각 세부 중요도는 **통합패턴맵 최신 버전의 S/A 등급**을 따른다.

# 5. 통합패턴맵 확장영역의 해석

통합패턴맵 v2.3에는 다음 영역도 포함되어 있다.

- Parse / Execute / Fetch / Database Call
- SQL Trace / Response Time
- Lock / Transaction / Concurrency
- Performance Troubleshooting
- Optimizer Statistics 세부
- Plan Stability / Adaptive / 도구 영역
- SQLP 공식범위 문법 Safety Net

이 항목들이 패턴맵에 존재한다는 사실과 **최근 실기에서 동일한 깊이로 빈번하게 출제된다는 주장**은 동일하지 않다.

따라서:
- 통합패턴맵에서 **S/A**인 항목은 2회독 실전 대비 범위로 다룬다.
- **B/C/F**는 보조 Coverage/안전망으로 유지한다.
- 출제 빈도에 대한 별도 근거가 없으면 `최근 중요 출제경향`으로 과장하지 않는다.

# 6. 근거 부족으로 단정하지 않는 주장

다음은 단정하지 않는다.

- 언제나 TO-BE Plan이 제공된다.
- 특정 Hint가 항상 등장한다.
- TABLE ACCESS FULL이면 무조건 병목이다.
- PX SEND가 보이면 무조건 병목이다.
- Index가 존재하면 Index Scan이 항상 우월하다.
- 작은 테이블은 항상 Broadcast가 정답이다.
- Hash Join은 항상 작은 쪽이 특정 자식 위치에 있어야 한다.

실제 판단은 처리량, 선택도, Starts/A-Rows, 파티션/분배 구조, 결과집합 의미를 함께 본다.

# 7. 시험 답안 작성 원칙

기본 답안 사고 흐름은 다음으로 통일한다.

1. **결과집합/관계 확인**
   - 출력 컬럼
   - PK/FK/UK
   - 일반/Semi/Anti/Outer 관계
2. **건수 흐름 계산**
   - 필터 결과
   - Join 증폭/축소
   - Starts/A-Rows
   - GROUP BY/DISTINCT 결과
3. **AS-IS 병목 특정**
   - 단순 Operation명이 아니라 불필요 처리량의 직접 원인을 설명
4. **개선안 작성**
   - SQL / Hint / Index / DDL 중 필요한 수단 선택
5. **결과집합 동일성 검증**
6. **TO-BE Plan 핵심 흐름 검증**

# 8. Hint 사용 원칙

- Hint는 정답을 과도하게 고정하는 수단이 아니라 필요한 계획 의도를 전달하는 수단으로 사용한다.
- 공식 지원되는 Hint를 우선한다.
- `QB_NAME`, `LEADING`, Join Method, Access Path, `PQ_DISTRIBUTE` 등의 대상과 역할을 정확히 설명할 수 있어야 한다.
- 비공식/버전 의존성이 의심되는 Hint는 시험 기본답안의 필수 요소로 두지 않는다.

# 9. Oracle 버전 범용성

- 프로젝트 소스만으로 SQLP가 특정 Oracle 버전을 고정한다고 단정하지 않는다.
- 가능한 경우 버전 공통 원리를 우선한다.
- `FETCH FIRST` 같은 12c+ 문법을 사용할 경우 ROWNUM/ROW_NUMBER 기반 원리도 함께 이해한다.
- 기능의 존재 여부와 시험에서 해당 버전 세부동작을 요구한다는 주장을 구분한다.

# 10. 학습·출제 문서와의 역할 분리

- **통합패턴맵:** 무엇을 공부할지와 중요도 결정
- **학습계획:** 언제/어떤 순서/어떤 Cycle로 공부할지 결정
- **문제출제규칙:** Pattern ID를 어떻게 문제화하고 검수할지 결정
- **본 문서:** 왜 해당 범위를 우선하며 어떤 출제 주장까지 신뢰할지 결정

본 문서가 패턴 목록을 중복 관리하지 않으며, 세부 범위는 통합패턴맵 최신 버전을 따른다.

# 11. v1 → v1.1 수정사항

1. 기준일을 2026-08-11로 갱신.
2. 예상 시험일을 공식 확정일이 아닌 기존 프로젝트의 가정일로 명확히 표시.
3. `AS-IS Only 최근 사례 많음 = 신뢰도 A`를 보수적으로 수정.
4. 통합패턴맵 v2.3의 S/A와 B/C/F를 출제경향과 혼동하지 않도록 역할 분리.
5. 대량 UPDATE 및 확대된 S/A 영역을 학습 Coverage에 연결.
6. FTS/PX SEND/Index/Broadcast 등을 Operation명만으로 단정하지 않는 원칙 강화.
7. 범위 목록의 Single Source of Truth를 통합패턴맵으로 통일.
