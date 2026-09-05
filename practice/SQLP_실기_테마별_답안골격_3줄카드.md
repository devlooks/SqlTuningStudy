# 🧭 [공통] 테마별 답안 골격 3줄 카드

- **작성일:** 2026-09-05
- **목적:** 힌트/SQL을 쓰기 **전에** 판단 근거를 확정시켜, 반복 슬립(LEADING 구성 오류·대량 FULL 강제·결과집합 미서술)을 구조적으로 차단
- **기준 문서:** `AGENTS.md`, `SQLP_실기_2회독_학습계획_v2_1.md`, `SQLP_실기_2회독_통합패턴맵_v2_3_최종확정.md`
- **적용 기간:** Cycle B (~10/10) 명시 작성 → 10/10 점검 이후 암묵 검산 → Cycle C(10/24~) 생략

---

## 0. 골격의 원리

옵티마이저가 비용을 계산하는 순서와 동일하게 판단한다.

```
① 지배 변수 확정  →  ② 구조/순서 확정  →  ③ 방식 확정  →  힌트는 '받아쓰기'
```

**힌트를 먼저 쓰면 안 되는 이유:** 힌트는 판단의 결론을 문자로 옮긴 것이다.
판단이 없으면 LEADING/USE_NL은 매번 새로 지어내는 추측이 되고, 같은 슬립이 반복된다.

**공통 마감 2종 (테마 무관, 모든 답안 필수)**

- 결과집합 동일성 3문장: 행 수 / NULL / 중복
- 셀프 게이트 6항목 체크

---

## 1. 테마별 ①②③ 항목표

### T01 Cardinality / 실행계획 기본

| | 확정할 것 |
|---|---|
| ① | 단계별 건수 흐름: 각 Row Source의 Starts·A-Rows 예상값을 위에서 아래로 적는다 |
| ② | 병목 Row Source 지목: `Starts × 건당 Buffers` 가 최대인 Id |
| ③ | 낭비량 정량화: (최종 결과 건수 ÷ 병목 A-Rows) → 폐기 비율 % |

> 서술 규칙: 모든 문장에 실측 수치를 인용한다. 수치 없는 문장은 부분점수가 붙지 않는다.

### T02 Predicate / Access / Index

| | 확정할 것 |
|---|---|
| ① | Sargable 판정: 컬럼 가공·형변환·`NVL`·`LIKE '%x'` 로 인덱스가 죽는 조건이 있는가 |
| ② | 인덱스 컬럼 순서: **'=' 조건 → 범위 조건 → 정렬 컬럼** (조인키는 '=' 에 포함) |
| ③ | Access / Filter 분리: 테이블 랜덤 액세스를 인덱스 컬럼 추가로 제거 가능한가 |

> Buffers 차이 = 인덱스 스캔 비용 vs 테이블 랜덤 액세스 비용. 뺄셈으로 서술한다.

### T03 Join Method / Join Order

| | 확정할 것 |
|---|---|
| ① | 건수 축소 순서: `[조건] N건 → M건` 을 축소 효과가 큰 순으로 나열 |
| ② | 조인 순서: `T1 → T2 → T3 → T4` + **인접 쌍마다 조인 조건 1줄** (카티시안 방지) |
| ③ | 조인 방식: 바깥 건수 vs **손익분기 = 안쪽 테이블 블록수 ÷ 4** 비교 |

```
NL   비용 ≈ 바깥건수 × (인덱스높이 + 1)   ≈ ×4
HASH 비용 ≈ 안쪽 테이블 총 블록수 (1회)
→ 바깥건수 > 블록수÷4 이면 HASH+FULL, 아니면 NL+인덱스
```

> FULL은 `USE_HASH` 와 세트다. NL의 inner에 FULL을 걸면 바깥 건수만큼 풀스캔이 반복된다.

### T04 Semi / Anti / DISTINCT

| | 확정할 것 |
|---|---|
| ① | 논리 관계 판정: 존재성(Semi) / 부재성(Anti) / 값 필요(Join) 중 무엇인가 |
| ② | 1:N 증폭 여부 → 증폭이면 `EXISTS`/`NOT EXISTS` 로 전환해 DISTINCT 제거 |
| ③ | NULL 함정: `NOT IN` 은 대상 컬럼에 NULL 1건만 있어도 전건 탈락 → `NOT EXISTS` |

### T05 Scalar Subquery / Query Transformation

| | 확정할 것 |
|---|---|
| ① | 서브쿼리 필터의 **선택도**와 현재 **적용 시점** (조인 앞인가 뒤인가) |
| ② | 풀 것인가 말 것인가 → **LEADING 구성이 갈린다** |
| ③ | 스칼라라면: `LEFT OUTER JOIN` + `CASE WHEN` 1회 집계 + `USE_HASH(V)` |

```
안 푼다 → 서브Q에 /*+ NO_UNNEST PUSH_SUBQ */ , LEADING에서 서브Q 제외
푼다   → 서브Q에 /*+ UNNEST */ , LEADING 2순위에 서브Q + USE_NL + NL_SJ
인라인 뷰 → NO_UNNEST가 아니라 /*+ NO_MERGE */
```

> 동일 상관키가 반복 유입되면 `FILTER`의 서브쿼리 결과 캐싱이 작동해 NO_UNNEST 쪽이 유리할 수 있다.

### T06 Optional Predicate / OR Expansion

| | 확정할 것 |
|---|---|
| ① | **분기 간 상호배타성**: UNION ALL 분기가 겹치면 중복(Double Counting) 발생 → `LNNVL` |
| ② | 분기별 인덱스 매핑: 각 블록이 어떤 인덱스를 타는지 1:1로 지정 |
| ③ | 선택도 우선순위: 고객(50%) → 부서(40%) → 전체(10%) 식으로 분기 순서 결정 |

> ①이 건수 축소보다 먼저다. 중복이 생기면 결과집합이 깨져 튜닝 자체가 무효.

### T07 GROUP BY / Sort / Top-N

| | 확정할 것 |
|---|---|
| ① | 집계 위치: 조인 **전** 선집계(다측 축소)인가, 조인 후인가 → `NO_MERGE` 필요 여부 |
| ② | 정렬 생략 인덱스: `(=조건, 정렬컬럼1, 정렬컬럼2 …)` 로 SORT 오퍼레이션 제거 |
| ③ | Stopkey 성립: `ROWNUM <=` 가 정렬 이전에 걸리는가 (`INDEX_DESC` + `COUNT STOPKEY`) |

### T08 Partition / Pruning

| | 확정할 것 |
|---|---|
| ① | **프루닝 성립 여부**: 파티션 키에 가공·암묵적 형변환(VARCHAR2↔DATE)이 있는가 |
| ② | Static인가 Dynamic인가: 상수 조건 → Static, NL 조인 통한 공급 → Dynamic(KEY~KEY) |
| ③ | 인덱스 종류: 파티션 키가 조건에 없는 Top-N이면 로컬 인덱스는 전 파티션 순회 → Global |

> ①이 무너지면 조인 순서를 아무리 잘 짜도 전 파티션 스캔이다.

### T09 PWJ / Parallel

| | 확정할 것 |
|---|---|
| ① | 양측 **파티션 키 일치 여부** → Full PWJ / Partial PWJ / 불가 |
| ② | 재분배 방식: `PQ_DISTRIBUTE(t, outer, inner)` 조합 확정 |
| ③ | 대량 BROADCAST 참사 점검: 소량측만 BROADCAST, 대량측은 HASH/NONE |

```
Full PWJ    → PQ_DISTRIBUTE(t, NONE, NONE)
Partial PWJ → PQ_DISTRIBUTE(t, PARTITION, NONE)
양측 대량   → PQ_DISTRIBUTE(t, HASH, HASH)
```

### T10 DML / Batch / DDL

| | 확정할 것 |
|---|---|
| ① | **변경 비율(%)**: 소량이면 DML, 대량(수십 %↑)이면 CTAS/EXCHANGE로 전환 |
| ② | 부대 비용: Undo/Redo, 인덱스 유지, HWM 잔존 여부 |
| ③ | 절차 순서 확정: CTAS 5단계 / EXCHANGE 사전 인덱스 / UNUSABLE→Direct-Path→REBUILD |

> 건수 축소 축이 없다. ①은 "얼마나 줄이나"가 아니라 "얼마나 바꾸나"다.

### T11 Runtime / Trace / DB Call

| | 확정할 것 |
|---|---|
| ① | Call 횟수 공식: `Fetch 횟수 ≈ 결과건수 ÷ Array Size + 1` 로 역산 |
| ② | Row-by-Row → Set Processing 전환 지점 |
| ③ | Array Fetch / Bulk 크기 조정으로 줄어드는 Call 수를 수치로 제시 |

### T12 Lock / Transaction / Concurrency

| | 확정할 것 |
|---|---|
| ① | Lock 종류 판정: 행 경합(TX) 인가 테이블 경합(TM) 인가 |
| ② | Blocker 추적 경로: 대기 세션 → 보유 세션 → 보유 객체 |
| ③ | 해소책: FK 인덱스 생성 / Commit 주기 조정 / 처리 순서 통일 |

> FK 컬럼에 인덱스가 없으면 부모 DML이 자식 테이블 전체 TM Lock을 유발한다.

---

## 2. 사용 방식 (단계적 제거 계획)

| 시기 | 사용법 |
|---|---|
| ~10/10 (Cycle B) | 답안에 ①②③을 **명시적으로 작성**. 채점 대상에 포함 |
| 10/10 최종 점검 | 머릿속으로만 확정하고 답안에는 결론만 |
| 10/24~ (Cycle C) | 생략. 게이트 위반이 나온 경우에만 역추적 |

> 학습계획 §9.2 숙달 조건은 "테마 비공개 문제에서 **독립 수행**"이다.
> 골격을 계속 들고 있는 상태는 숙달이 아니다. 슬립 재발이 3회 연속 0건이면 즉시 뗀다.

---

## 3. 셀프 게이트 6항목 (제출 직전)

1. LEADING 목록의 테이블 수 == 실제 조인 대상 수인가 (UNNEST면 서브Q 포함 / NO_UNNEST면 제외)
2. LEADING 1순위에 USE_NL을 걸지 않았는가
3. LEADING 인접 두 테이블 사이에 조인 조건이 실재하는가 (카티시안 방지)
4. FULL을 건 테이블이 인덱스로 도달 가능한 소량 집합은 아닌가 (FULL은 USE_HASH와 세트)
5. 신규 인덱스의 선두 컬럼이 '=' 조건(조인키 포함)인가
6. 결과 행 수 / NULL / 중복 3가지를 각각 한 문장씩 적었는가
