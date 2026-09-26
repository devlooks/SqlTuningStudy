# SQLP 실기 테마 교안

- **위상:** 학습 내용의 정본. 무엇을 어떻게 판단하는지를 담는다
- **자매 문서:** `SQLP_실기_테마별_숙련도.md`(진도·숙련도) / `이력/`(풀이 기록) / `AGENTS.md`(출제·채점·세션 운영)
- **인코딩:** UTF-8 (LF)
- **최종 재구성:** 2026-09-26. Oracle 기본 동작 기준으로 서술을 정정하고 중복을 제거했다. 절 번호 §1.3~§1.5, §2와 K번호·Pattern ID는 이력 참조를 위해 유지한다
- **2026-09-26 개정:** R1에 ⓪ 지표 선택 추가, R2를 병목 유형 분기표로 일반화(기존 집계 위치 판별은 R2-집계), K01·K09·K17·K18·K19·K22·K25 개정, §1.8 두 트랙(SQLP / 전 영역) 신설, G11·A13 신설

---

## 0. 사용법

1. 문제를 받으면 §1.2 표준 동선대로 판단한다. 테마를 먼저 찾지 않는다.
2. 병목을 확정한 뒤 §2의 해당 테마에서 답안 골격과 보강을 본다.
3. 첨삭·오답 기록의 지적은 `K번호` / `G1-①~④` / `R1-STEP`으로 인용한다.
4. 신규 기준이 확립되면 §1.5에 K번호를 부여해 추가한다.
5. Pattern ID별 숙련도는 이 문서가 아니라 `SQLP_실기_테마별_숙련도.md` §9에 기록한다.

---

# 1. 공통 기반

## 1.1 실행계획 기본 규칙

### 실행 순서

- 자식이 부모보다 먼저 실행되고, 같은 부모 아래 형제는 **위에서 아래 순서**로 실행된다.
- `NESTED LOOPS`: 첫 번째 자식 = Outer(드라이빙), 두 번째 자식 = Inner. Inner는 Outer가 반환한 행마다 실행된다.
- `HASH JOIN`: 첫 번째 자식 = Build(해시 테이블 생성), 두 번째 자식 = Probe.
- `MERGE JOIN`: 두 입력을 조인키로 정렬(`SORT JOIN`)한 뒤 병합한다.
- `FILTER`에 자식이 둘 이상이면 첫 자식의 행마다 나머지 자식(서브쿼리)이 조건적으로 실행된다.

### 런타임 통계 열

| 열 | 의미 | 기준 |
|---|---|---|
| `Starts` | Operation 실행 횟수 | 회 |
| `E-Rows` | **1회 실행당** 예상 건수 | 비교하려면 `E-Rows × Starts` |
| `A-Rows` | **전체 Starts 합계** 실제 반환 건수 | 건 |
| `Buffers` | **전체 Starts 합계** 논리 I/O(consistent + current). **자식 포함 누적값** | 블록 |
| `Reads` / `Writes` | 물리 읽기 / 쓰기(Temp 포함). 누적값 | 블록 |
| `A-Time` | 실제 경과 시간. 누적값 | 시간 |
| `OMem` / `1Mem` / `Used-Mem` | 최적 / 1-pass / 실사용 작업 메모리 | Sort·Hash |
| `Used-Tmp` / `TempSpc` | Temp 사용량 | 메모리 초과 신호 |
| `Pstart` / `Pstop` | 접근한 파티션 범위. `KEY`는 실행 시 결정 | 프루닝 판독 |

- **자기 Buffers** = 내 Buffers − 직계 자식 Buffers 합
- 회당 비용 = Buffers ÷ Starts, 1건당 비용 = Buffers ÷ A-Rows

### 블록을 읽는 노드

| 구분 | Operation |
|---|---|
| 블록을 직접 읽는다 | `TABLE ACCESS FULL`, `INDEX UNIQUE/RANGE/FULL/FAST FULL/SKIP SCAN`, `TABLE ACCESS BY INDEX ROWID`(자식 인덱스가 있어도 테이블 블록 방문 비용을 자기 Buffers로 가진다) |
| DML에서 블록을 직접 읽는다 | `UPDATE`, `DELETE`, `INSERT`, `MERGE`, `LOAD AS SELECT` — 변경 대상 블록을 current 모드로 읽는다(K01 예외) |
| 자기 Buffers가 0이다 | `NESTED LOOPS`, `HASH JOIN`, `MERGE JOIN`, `SORT`, `HASH/SORT GROUP BY`, `HASH/SORT UNIQUE`, `FILTER`, `UNION-ALL`, `VIEW`, `COUNT STOPKEY`, `PARTITION RANGE ...` |

**검산식:** 블록을 직접 읽는 노드의 자기 Buffers 합 = Id 0 Buffers

### Predicate Information

- `access(...)`: 인덱스 탐색 범위를 정하는 조건. 읽는 양 자체를 줄인다.
- `filter(...)`: 이미 읽은 행을 거르는 조건. 읽은 블록은 줄지 않고 A-Rows만 준다.
- 테이블 액세스 노드의 `filter`는 **인덱스가 넘긴 ROWID를 전부 방문한 뒤 버린다**는 뜻이다.

### 물리 수치 기준 (8KB 블록 기준 근사)

| 항목 | 근사값 |
|---|---|
| 테이블 블록당 행 수 | 행 100B 기준 약 80행 |
| 인덱스 리프 블록당 엔트리 | 약 200~400개 |
| 인덱스 높이(루트 → 리프) | 보통 2~4 |
| `TABLE ACCESS FULL` Buffers | HWM 아래 전체 블록 수. 필터로 줄지 않는다. 멀티블록 I/O라 블록당 비용이 싸다 |
| `INDEX RANGE SCAN` Buffers | 읽은 엔트리 수 ÷ 리프당 엔트리 + 높이 × Starts |
| `TABLE ACCESS BY INDEX ROWID` 자기 Buffers | 방문 행 수 × 0.1~1.0 (클러스터링 팩터가 좋을수록 0.1, 나쁠수록 1.0) |
| NL Inner가 FULL일 때 | Starts × 테이블 블록 수 |

---

## 1.2 답안 표준 동선

```
R1  병목 판독 (⓪ 지표 선택 + 5-STEP) →  병목 Id + 낭비율 + 비중
R2  처방 판별 (병목 유형 분기표)     →  개선 방향 한 줄 → 해당 테마 답안 골격
    개선 SQL 작성          →  G1을 작성하는 동안 채운다
G1  힌트 사전검증 4항      →  물리적으로 성립하지 않는 힌트 차단
G2  결과집합 3문장         →  행 수 / NULL / 중복
```

- 진단(R1), 처방(R2~SQL), 검증(G1·G2)은 서로 다른 능력이다. 각각 채점하고 각각 훈련한다.
- 힌트는 판단의 결론을 옮겨 적는 것이다. 판단 없이 힌트부터 쓰지 않는다(K35).
- 같은 오류가 3회 이상 반복되면 지식을 다시 설명하지 않고 답안 칸을 분리한다(AGENTS §4.6).

---

## 1.3 루틴 (R)

### R1. 병목 판독: ⓪ 지표 선택 + 5-STEP

SQL을 보기 전에 실행계획·통계 표만으로 수행한다. 열 규칙은 §1.1을 따른다.

**⓪ 지표 선택 — 무엇이 응답 시간을 지배하는가**

| 문제에 주어진 신호 | 판독 지표 | 진행 |
|---|---|---|
| 실행계획 Buffers가 크고 Temp·대기 신호가 없다 | Buffers | 아래 ①~⑤ |
| `Reads`·`Writes`·`TempSpc`·`Used-Tmp`가 크다, 1-pass/multi-pass | Temp·물리 I/O | Sort·Hash 노드도 병목 후보에 넣는다(자기 Buffers가 0이어도). 입력 건수와 메모리로 판단 (T07·T13 TR07) |
| Trace의 Parse·Execute·Fetch 횟수가 결과 건수에 비례한다 | 호출 횟수 | T11 답안 골격 |
| elapsed ≫ cpu, 락 대기 이벤트, 블로커 정보 | 대기 시간 | T12 답안 골격 |
| PX 서버별 처리량 편차 | 편차 | T09 (TR08) |

두 가지 이상이 겹치면 응답 시간 비중이 큰 쪽부터 판독한다. 이하 ①~⑤는 Buffers 지표일 때의 절차다.

| STEP | 산출 | 공식 | 사용 열 | 근거 |
|:---:|---|---|---|---|
| ① | 목표 건수 | Id 0의 A-Rows. **병목이 집계 노드(`GROUP BY`·`DISTINCT`·`SORT AGGREGATE`) 아래에 있으면 가장 가까운 상위 집계 노드의 입력 건수(집계 직전 A-Rows)** | A-Rows | K09 |
| ② | 병목 Id | 자기 Buffers가 최대인 노드 | Buffers | K01, K02, K11 |
| ③ | 낭비율 (`배`) | 병목 A-Rows ÷ ① 목표 건수 | **A-Rows만** | K09, K10 |
| ③' | 1건당 블록 수 (`블록/건`) | 병목 자기 Buffers ÷ 병목 A-Rows | Buffers, A-Rows | K09 |
| ④ | 비중 (`%`) | 병목 자기 Buffers ÷ Id 0 Buffers | **Buffers만** | K04 |
| ⑤ | 검산 | 블록을 읽는 노드의 자기 Buffers 합 = Id 0 Buffers | Buffers | K03 |

**병목 유형 판정 (K09)**

```
③ ≥ 2 (뚜렷이 1보다 큼) → 행 낭비형   : 많이 가져와 상위의 조인·필터에서 버린다
                                        (집계에 의한 압축은 ①에서 이미 제외했다)
③ < 2 (1 근처 또는 미만) → 블록 낭비형 : 필요한 행에 블록을 많이 쓴다. ③'와 노드 종류로 원인을 가른다
   ├ 병목이 NL Inner의 인덱스(또는 그 위 ROWID 노드) + Starts 큼
   │   + 회당 Buffers(Buffers ÷ Starts) ≈ 인덱스 높이                 → NL 반복 탐색 → 조인 방식 판단(K17~K19)
   ├ 병목 Id에 filter 있음 + 자식 인덱스 A-Rows ≫ 병목 A-Rows         → 테이블 필터로 버림 → 인덱스 설계(K31·K33)
   ├ filter 없음 + ③' ≈ 0.1~1.0 (ROWID 접근)                       → 랜덤 I/O (클러스터링 팩터)
   └ filter 없음 + ③' > 1 (ROWID 접근, 반복 탐색 아님)                → 행 이주·체이닝 의심
```

③이 1 미만인 경우는 병목 위의 1:N 조인이 최종 건수를 늘린 경우다. 1 미만이 나왔다고 분자·분모를 뒤집지 않는다.

**단위 검산 (K10)**
- ③은 `배`, ④는 `%`. 단위가 맞지 않으면 열을 잘못 읽은 것이다.
- ③과 ③'의 값이 같으면 ③에 Buffers가 들어간 것이다.

**R1 답안 양식**

```text
⓪ 판독 지표 = Buffers / Temp·물리 I/O / 호출 횟수 / 대기 시간 (하나 선택, 근거 한 줄)
① 목표 건수 = Id ___ A-Rows ______   (병목 위에 집계 노드가 있으면 집계 직전 노드, 없으면 Id 0)
② 병목 Id ______ / 자기 Buffers ______
③  낭비율     = 병목 A-Rows ______ ÷ ① 목표 건수 ______ = ______ 배
③' 1건당 블록 = 병목 자기 Buffers ______ ÷ 병목 A-Rows ______ = ______ 블록/건
   유형: 행 낭비형 / 블록 낭비형 (근거 한 줄)
④ 비중       = 병목 자기 Buffers ______ ÷ Id 0 Buffers ______ = ______ %
⑤ 검산       = 블록을 읽는 노드 자기 Buffers 합 ______ = Id 0 Buffers ______
```

### R2. 처방 판별: 병목 유형 분기표

R1에서 확정한 병목 유형으로 처방 방향을 고르고, 해당 테마의 답안 골격(§2)으로 넘어간다. 판정을 한 줄로 적은 뒤 SQL을 쓰고, 제출 전 판정 문장과 SQL 구조를 대조한다(K35).

| 병목 유형 (R1 결과) | 처방 판단 | 기준 | 답안 골격 |
|---|---|---|---|
| NL Inner 반복 탐색 (Starts 큼, 회당 ≈ 높이) | 조인 방식·순서를 바꿀지, Outer를 줄일지 | K13~K19 | T03 |
| 테이블 필터로 버림 / 인덱스 filter / 테이블 방문 과다 | 인덱스 컬럼 추가·순서 변경, 커버링, 조건 재작성 | K30~K33 | T02 |
| 조건 가공·형변환으로 FULL 또는 프루닝 실패 | 조건 재작성 (범위식·타입 일치) | K06 | T02 / T08 |
| 조인·필터 뒤 대량 집계, 1:N 증폭 뒤 집계 | 집계 위치 (아래 R2-집계) | K20~K24 | T07 |
| 1:N 증폭 뒤 DISTINCT, 존재 확인용 조인 | 세미·안티 전환 후 DISTINCT 제거 | K29 | T04 |
| 서브쿼리 반복 (FILTER·스칼라 Starts 큼) / 필터 시점이 늦음 | UNNEST vs NO_UNNEST+PUSH_SUBQ, 조인+1회 집계 | K25~K28 | T05 |
| 입력값 유무·OR로 한 계획이 모든 호출을 처리 | 분기 SQL / UNION ALL + 배타 조건 | K34 | T06 |
| 정렬 후 N건만 사용, WINDOW SORT 후 소수 사용 | 정렬 생략 인덱스 + Stopkey | K19, K32 | T07 |
| 병렬 재분배·복제 과다 | 분배 방식 / PWJ | K17·K18 | T09 |
| 대량 변경의 Undo·Redo·인덱스 유지 | DML vs 재구성(CTAS·EXCHANGE·TRUNCATE) | — | T10 |
| 호출 횟수 과다 (⓪에서 호출 지표) | 집합 처리, Array·Bulk | — | T11 |
| 대기 시간 지배 (⓪에서 대기 지표) | 블로커·트랜잭션 범위·FK 인덱스 | — | T12 |
| Temp 사용 (⓪에서 Temp 지표) | 입력 축소(선필터·선집계) 또는 방식 변경 | K20 | T07 / T13 |

- 한 문제에 병목 유형이 둘 이상이면 **건수를 바꾸는 처방(조건 재작성·선필터·선집계·세미 전환)을 먼저 정하고, 조인 방식은 그 결과 건수로 마지막에 정한다.** 건수가 바뀌면 K18의 Outer 건수가 바뀌어 조인 방식 결론이 뒤집힐 수 있다.

#### R2-집계: 집계 위치 판별

| STEP | 확정할 것 |
|:---:|---|
| ① | **팩트 테이블** = `SUM`/`COUNT` 대상 컬럼이 속한 테이블 |
| ② | **B** = 팩트 테이블 액세스 노드의 A-Rows (조인 전 팩트 건수) |
| ③ | **C** = 최종 `GROUP BY` 바로 아래 노드의 A-Rows (모든 조인·필터 후 집계 직전 건수) |
| ④ | **조인의 역할** — 행을 줄이는 필터인가, 컬럼만 붙이는가 (K21) |
| ⑤ | 결론: `B ≈ C` 또는 `C > B` → **선집계** / `C`가 `B`보다 자릿수로 작음 → **후집계** |
| ⑥ | 선집계라면 집계 결과 건수로 **조인 방식을 다시 판단**한다(K18의 Outer 건수 = 집계 결과 건수) |

```text
1. 금액·건수 컬럼이 속한 팩트 테이블:
2. 조인 전 팩트 건수(B): [팩트 테이블 액세스 노드의 Id와 A-Rows]
3. 모든 조인·필터 후 집계 직전 건수(C): [최종 GROUP BY 바로 아래 Id와 A-Rows]
4. 조인의 역할: [행을 줄이는 필터 / 컬럼만 붙이는 조인]
5. 집계 위치 결론: [조인 전 선집계 / 조인·필터 후 후집계]
```

---

## 1.4 게이트 (G)

### G1. 힌트 사전검증 4항

SQL을 작성하는 동안 힌트를 쓸 때마다 해당 항을 함께 확인한다.

| # | 점검 | 불통과 시 증상 |
|:---:|---|---|
| ① | **LEADING 인접성** — 나열 순서상 인접한 두 테이블 사이에 조인 조건이 있는가 | 카티션 곱 (K15) |
| ② | **힌트 짝 정합성** — `PUSH_PRED`는 NL에서만 성립한다. `USE_HASH`와 함께 쓰면 무효 | 힌트 무효화 (K28) |
| ③ | **인덱스 실존** — 지정한 인덱스가 존재하는가. 신규 설계라면 NL Inner 인덱스의 선두가 조인키인가 | 미존재 인덱스 지정 (K30) |
| ④ | **손익분기** — `Outer 건수 × Inner 1회 블록 수` 와 `Inner FULL 블록 수`를 숫자로 비교했는가 | 감에 의한 조인 방식 선택 (K17, K18) |

### G2. 결과집합 동일성 3문장

| # | 문장 |
|:---:|---|
| ① | **행 수** — 개선 후 행 수가 원본과 같은 근거 (조인 차수, 세미 전환, 집계 단위) |
| ② | **NULL** — OUTER 보존 여부, `SUM`·`COUNT(col)`은 NULL을 무시하고 `COUNT(*)`는 센다 |
| ③ | **중복** — 증폭 제거 근거. `DISTINCT`를 뺐다면 더 이상 필요 없는 이유 (K29) |

답안 하단 고정 위치에 세 칸을 먼저 만들고 시작한다.

---

## 1.5 판단 기준 K01~K36

### A. 실행계획 판독 (K01~K07)

| K | 기준 | 내용 |
|:---:|---|---|
| **K01** | Buffers 누적 규칙 | 부모 Buffers = 자기 것 + 자식 전부. 조회문에서 블록을 직접 읽는 노드는 테이블·인덱스 액세스 노드뿐이며, `TABLE ACCESS BY INDEX ROWID`는 자식 인덱스를 뺀 나머지가 자기 비용이다. 이 노드들의 자기 Buffers 합 = Id 0 Buffers. **예외:** DML 문의 `UPDATE`·`DELETE`·`INSERT`·`MERGE`·`LOAD AS SELECT` 노드는 변경할 블록을 current 모드로 읽으므로 자기 Buffers를 가진다. 이때는 이 노드도 검산식의 항에 넣는다 |
| **K02** | 블록 미접근 노드 | `HASH JOIN` / `NESTED LOOPS` / `SORT` / `GROUP BY` / `FILTER` / `UNION-ALL` / `PARTITION RANGE ...`는 자기 Buffers가 0이다 |
| **K03** | 검산 | 항의 개수 = 블록을 읽는 노드의 개수. 부모의 누적값을 항에 넣으면 자식이 중복되어 합계가 초과한다. 실제로 더해서 확인한다 |
| **K04** | 병목 후보 컷오프 | 전체 Buffers 비중 5% 미만인 노드는 병목 후보에서 제외한다 |
| **K05** | 오퍼레이션 의미 | `SORT AGGREGATE`는 정렬이 아니라 단일행 집계다. 메인 쿼리 위에 붙은 별도 노드의 Starts가 메인 A-Rows와 같으면 SELECT 절 스칼라 서브쿼리가 행마다 실행된 것이다 |
| **K06** | 파티션 프루닝 신호 | `Pstart 1 / Pstop N`(전체 파티션)이면 프루닝 실패다. 파티션 키 조건이 없거나 키가 가공된 경우다 |
| **K07** | 열 분별 | Starts·E-Rows·A-Rows를 각자의 열에서 읽는다. E-Rows는 1회당 추정값, A-Rows는 전체 실측 합계다 |

### B. 병목 판정 (K08~K12)

| K | 기준 | 내용 |
|:---:|---|---|
| **K08** | 병목의 정의 | 비용이 큰 곳 중에서 **줄이거나 뒤로 미룰 수 있는 낭비**가 있는 곳이다. 판정 질문은 "이 작업을 줄이거나 나중에 해도 결과가 같은가"이다 |
| **K09** | 병목의 두 유형 | 낭비율 ③의 분모(목표 건수)는 Id 0 A-Rows다. 단 병목 위에 집계 노드(`GROUP BY`·`DISTINCT`·`SORT AGGREGATE`)가 있으면 **집계 직전 노드의 A-Rows**를 쓴다. 집계에 의한 행 감소는 필요한 작업이지 낭비가 아니기 때문이다(K08). ③이 뚜렷이 1보다 크면(대략 2배 이상) 행 낭비형, 1 근처 또는 미만이면 블록 낭비형이며 ③'(자기 Buffers ÷ A-Rows)와 노드 종류로 원인을 가른다. NL Inner 인덱스의 회당 Buffers가 인덱스 높이와 같으면 반복 탐색이다. 1 미만이 나왔다고 분자·분모를 뒤집지 않는다 |
| **K10** | ③·④ 상호검산 | ③은 `배`, ④는 `%`. ③이 1 근처인데 ④가 크면 블록 낭비형 판정이 빠진 것이다 |
| **K11** | 반복 횟수 ≠ 병목 | Starts가 크다고 병목이 아니다. 판정은 자기 Buffers로 한다 |
| **K12** | FULL ≠ 병목 | `TABLE ACCESS FULL`은 대량 처리에서 정상 경로다. 비중(K04)을 먼저 본다 |

### C. 조인 순서 · 드라이빙 (K13~K16)

| K | 기준 | 내용 |
|:---:|---|---|
| **K13** | 드라이빙 선정 | 총 건수가 아니라 **자기 조건을 적용한 뒤 남는 건수**가 가장 적은 테이블. 조건이 없는 테이블은 드라이빙 후보가 아니다 |
| **K14** | 3순위 이후 순서 | 이미 읽은 테이블이 다음 테이블의 조인키를 갖고 있는가(도달 가능성)와 조인 후 건수 감소 폭으로 정한다 |
| **K15** | LEADING 카티션 방지 | 나열 순서에서 인접한 두 테이블 사이에 조인 조건이 있어야 한다. 양쪽과 연결된 허브 테이블은 앞이나 가운데에 둔다 |
| **K16** | USE_NL 대상 | `USE_NL(t)`의 `t`는 Inner 테이블이다. LEADING 1순위 테이블에는 조인 방식 힌트를 걸지 않는다 |

### D. 조인 방식 (K17~K19)

| K | 기준 | 내용 |
|:---:|---|---|
| **K17** | 자릿수 어림 (1차) | `Outer 건수`와 `Inner FULL 블록 수`를 나란히 적어 자릿수를 본다. Outer가 한 자릿수 이상 작으면 NL 쪽, 같은 자릿수 이상이면 HASH 쪽이 거의 확실하다. **어림일 뿐이며 결론은 K18 계산으로 낸다.** 두 기준이 다르게 보이는 구간(Outer ≈ 블록 수의 1/10~1/4)은 반드시 K18로 판정한다 |
| **K18** | 손익분기 정량식 | **비교식:** NL의 Inner 비용 = Outer 건수 × Inner 1회 비용, HASH의 Inner 비용 = Inner FULL 블록 수(1회). Outer를 읽는 비용은 양쪽에 똑같이 들므로 **비교에서 뺀다**(전체 Buffers를 추정할 때만 더한다). **Inner 1회 비용** = 인덱스 높이 + Outer 1건당 Inner 행 수(테이블 방문). 높이 3·1건당 1행이면 4이므로 손익분기 Outer 건수 ≈ Inner FULL 블록 수 ÷ 4. 1건당 N행이면 ÷(높이 + N)으로 계산한다. **값의 출처:** Outer 건수 = Outer 노드의 A-Rows(= NL Inner의 Starts). 선집계 뒤에 조인하면 집계 결과 건수. Inner FULL 블록 수 = **테이블 통계의 블록 수**. 실행계획에 찍힌 NL Inner 노드의 Buffers는 NL 실측 비용이지 FULL 비용이 아니다. **예외:** Inner에 조인키로 시작하는 인덱스가 없으면 NL 비용 = Outer 건수 × Inner FULL 블록 수이므로 HASH다. FULL은 멀티블록 I/O라 실제 손익분기는 계산값보다 낮다. Inner를 FULL로 읽을 때는 `USE_HASH`와 함께 쓴다 |
| **K19** | 전체범위 vs 부분범위 | 판단 질문은 "온라인인가"가 아니라 **"결과를 전부 쓰는가, 앞의 N건에서 멈추는가"**다. 온라인 화면이라도 결과를 전부 가져가면 전체범위 처리이므로 K18 숫자로 정한다. 배치·집계는 전체범위다. 부분범위 처리(`ROWNUM`/Top-N)이고 정렬을 드라이빙 인덱스로 해결해 Stopkey가 가능하면, K18의 Outer 건수에는 전체 후보 건수가 아니라 **실제로 조인까지 가는 N건**을 넣는다. 이 경우 NL + 인덱스 + Stopkey가 유리하다. 정렬을 인덱스로 해결하지 못하면 전체를 읽고 정렬해야 하므로 전체범위로 본다 |

### E. 집계 위치 (K20~K24)

| K | 기준 | 내용 |
|:---:|---|---|
| **K20** | 선집계 판별 | 조인이 행을 크게 줄이면(필터 조인) **후집계**, 조인이 행을 유지하거나 늘리면(붙이기·1:N) **선집계**. R2-집계의 B와 C를 비교해 판정한다 |
| **K21** | 조인의 역할 | 조인 상대가 PK/UK이고, 상대 쪽에 조건이 없고, 조인 컬럼이 NOT NULL이며 무결성이 보장되면 행 수는 변하지 않는다(붙이기). 상대 쪽에 WHERE 조건이 있으면 필터 조인이다 |
| **K22** | 변환 가능 집계함수 | `SUM`·`COUNT`·`MIN`·`MAX`는 두 단계로 나눠 집계할 수 있다. 단 **바깥 단계의 함수가 바뀐다**: 안 `SUM` → 밖 `SUM`, 안 `COUNT(*)`·`COUNT(col)` → 밖 **`SUM(건수)`**(밖에서 `COUNT`를 쓰면 그룹 수를 세게 된다), 안 `MIN`/`MAX` → 밖 `MIN`/`MAX`. `AVG`는 안에서 `SUM`과 `COUNT(col)`로 분해해 밖에서 `SUM(합) / SUM(건수)`로 나눈다. `COUNT(DISTINCT)`는 두 단계로 나눌 수 없다 |
| **K23** | 선집계 안전 조건 | 선집계 결과와 조인하는 상대가 그 키에 대해 유일(PK/UK)해야 한다. 아니면 집계값이 중복 가산된다 |
| **K24** | 선집계 인라인뷰 골격 | 뷰의 `GROUP BY`에 바깥 조인키를 포함하고, 뷰 병합을 막으려면 `NO_MERGE`를 쓴다. 조건을 뷰 안으로 내릴 때 다른 지표가 사라지지 않는지 확인한다(예: 상태코드 조건을 WHERE로 내려 취소 건수가 사라짐 → `CASE WHEN`으로 처리) |

### F. 서브쿼리 · 쿼리변환 (K25~K29)

| K | 기준 | 내용 |
|:---:|---|---|
| **K25** | UNNEST 시 LEADING 구성 | 서브쿼리를 풀면 서브쿼리 테이블도 조인 순서의 대상이다. `LEADING`에 포함하고, 필터 효과가 크면 앞쪽(보통 2순위)에 둔다. 서브쿼리 테이블은 다른 쿼리 블록의 별칭이므로 서브쿼리에 `QB_NAME(qb)`를 주고 메인 힌트에서는 `별칭@qb`로 쓴다 |
| **K26** | 두 접근안 병기 | 서브쿼리 필터 시점 문제는 ① `UNNEST` + 세미조인, ② `NO_UNNEST` + `PUSH_SUBQ` 두 안을 모두 검토하고 손익분기로 택한다 |
| **K27** | NO_MERGE / PUSH_PRED 선택 | 뷰가 행을 줄이면 `NO_MERGE`로 독립 실행한다. 뷰 결과 전체가 필요하면 `USE_HASH`, 바깥 행에 해당하는 일부만 필요하면 `PUSH_PRED` + `USE_NL`로 뷰 안의 인덱스를 쓴다 |
| **K28** | PUSH_PRED 짝 | 조인 조건 푸시다운은 NL에서만 성립한다. `USE_HASH`와 함께 쓰면 무효다. `PUSH_PRED(뷰별칭)`은 뷰 바깥 쿼리 블록에 쓴다 |
| **K29** | DISTINCT 제거 순서 | 먼저 증폭 원인을 제거하고(일반 조인 → `EXISTS`), 그 결과로 `DISTINCT`가 불필요해진다. 순서를 바꾸면 결과집합이 깨진다 |

### G. 인덱스 설계 (K30~K33)

| K | 기준 | 내용 |
|:---:|---|---|
| **K30** | 선두 컬럼 분별 | NL Inner로 쓰이는 인덱스는 조인키가 선두다. 단독으로 범위를 읽는 커버링 인덱스는 등치 조건 → 범위 조건 순이며 집계 컬럼까지 포함한다 |
| **K31** | 커버링 점검 | 그 테이블에서 쓰는 `SELECT`·`WHERE`·`GROUP BY`·`ORDER BY` 컬럼이 모두 인덱스에 있는가. 하나라도 없으면 인덱스가 넘긴 행 수만큼 테이블을 방문한다 |
| **K32** | 스캔 방향 | 역순 정렬은 오름차순 인덱스를 거꾸로 읽어 해결할 수 있다(`INDEX RANGE SCAN DESCENDING`). `INDEX` 힌트는 방향을 지정하지 않으므로 방향을 보장하려면 `INDEX_DESC`를 쓴다 |
| **K33** | access vs filter | 인덱스 컬럼 조건이 access로 쓰이면 스캔 범위가 준다. filter로 쓰이면 읽은 뒤 거를 뿐이라 블록은 줄지 않는다 |

### H. 작성 규율 (K34~K36)

| K | 기준 | 내용 |
|:---:|---|---|
| **K34** | UNION ALL vs CASE WHEN | 쿼리 블록 수만큼 스캔한다. 조건마다 액세스 경로가 다르면 `UNION ALL`, 같으면 `CASE WHEN`으로 1회 집계한다 |
| **K35** | 판정 → SQL 이관 | 판별한 결론을 SQL 구조에 반영한다. 제출 전 판정 문장과 SQL 구조를 나란히 놓고 대조한다 |
| **K36** | 구문 일관성 | 콤마 조인과 ANSI `JOIN` 구문을 한 쿼리에서 섞지 않는다 |

---

## 1.6 핵심 튜닝 원리

### 1.6.1 조인 순서

드라이빙은 **자기 조건 적용 후 건수가 가장 적은 테이블**이다(K13). 이후에는 조인키로 도달 가능한 테이블 중 건수를 가장 많이 줄이는 순서로 간다(K14).

| 구조 | 형태 | 순서 결정 |
|---|---|---|
| 스타형 | 중심 테이블(주문·거래) + 부모 테이블 여러 개 | 조건이 가장 강한 부모 → 중심 → 나머지 부모(PK 조회) |
| 체인형 | 부모 → 자식 → 손자 직렬 | 조건이 가장 강한 노드에서 출발해 양쪽으로 전파 |
| 마스터-디테일 집계 | 마스터 + 대량 디테일 집계 | 디테일이 대량이면 HASH 조인 또는 선집계(§1.6.5) |
| Top-N | `ORDER BY` + `ROWNUM` | 정렬 컬럼 인덱스를 가진 테이블을 드라이빙해 NL로 부분범위 처리. 필터 조건이 희소하면 N건을 채우기 전에 많이 읽으므로 비용을 확인한다 |
| Outer 조인 | 보존 테이블 + 선택 테이블 | NL에서는 보존 테이블이 Outer여야 한다. HASH는 `HASH JOIN RIGHT OUTER`로 선택 테이블을 Build로 둘 수 있다 |
| Semi/Anti | `EXISTS` / `NOT EXISTS` | 메인이 먼저. 서브쿼리 쪽은 첫 매칭에서 멈춘다 |

### 1.6.2 조인 방식

| 방식 | 동작 | 유리한 조건 | 비용 |
|---|---|---|---|
| NL | Outer 행마다 Inner를 탐색 | Outer 건수가 적고 Inner에 조인키 인덱스가 있음. 부분범위 처리 가능 | Outer 건수 × Inner 1회 비용 (랜덤 I/O) |
| HASH | Build로 해시 테이블 생성 후 Probe | 대량 등치 조인. 인덱스 불필요 | 양쪽 입력을 1회씩 읽음 + PGA. 메모리 초과 시 Temp |
| MERGE | 양쪽 정렬 후 병합 | 이미 정렬된 입력, 비등치(범위) 조인 | 정렬 비용 |

- 방식 선택은 K17·K18 손익분기로 숫자를 비교한다.
- `A-Rows`가 크다는 사실보다 **Inner 1회 비용 × Starts**가 판단 근거다.
- Hash Join은 일반적으로 작은 입력이 Build가 되지만, 실제 역할은 실행계획의 첫 자식으로 확인한다.

### 1.6.3 결합 인덱스 설계

**컬럼 순서:** 등치(`=`, 조인키 포함) 조건 → 범위 조건 → (정렬 생략이 필요하면) 정렬 컬럼 → (커버링이 필요하면) 조회 컬럼

- 등치 조건 컬럼끼리는 순서를 바꿔도 스캔 범위가 같다.
- 범위 조건 컬럼 뒤의 컬럼은 access가 아니라 filter로만 쓰인다.
- **정렬 생략 조건:** 등치 조건 컬럼 바로 뒤에 `ORDER BY` 컬럼이 같은 순서로 모두 있어야 한다. 범위 조건 컬럼이 `ORDER BY` 첫 컬럼과 같으면 그 컬럼을 범위이자 정렬 컬럼으로 쓸 수 있다.
- 정렬 컬럼이 두 개 이상인데 일부가 빠지면 `SORT ORDER BY`가 남는다.
- NL Inner 인덱스는 조인키가 선두다(K30). 커버링이면 테이블 방문이 사라진다(K31).

### 1.6.4 힌트 작성

```sql
SELECT /*+ LEADING(A B C)            -- 조인 순서
           USE_NL(B) USE_HASH(C)     -- Inner 테이블에 조인 방식
           INDEX(A IX_A_01)          -- 액세스 경로
           INDEX(B IX_B_01) */
```

- 조인 순서 + 조인 방식 + 액세스 경로를 함께 지정해야 의도한 계획이 고정된다.
- 힌트는 별칭을 대상으로 한다. 다른 쿼리 블록의 객체는 `QB_NAME`과 `@qb`로 지정한다.
- 목적이 없는 힌트는 넣지 않는다.

### 1.6.5 서브쿼리 · 뷰 제어

**서브쿼리 힌트**

| 의도 | 힌트 위치 | 힌트 |
|---|---|---|
| 서브쿼리를 조인(세미/안티)으로 푼다 | 서브쿼리 안 | `UNNEST` (+ 필요 시 `NL_SJ`/`HASH_SJ`/`NL_AJ`/`HASH_AJ`) |
| 풀린 서브쿼리 테이블의 순서·방식 제어 | 메인 쿼리 (서브쿼리에는 `QB_NAME(qb)`) | `LEADING(메인 서브Q별칭@qb ...)`, `INDEX(서브Q별칭@qb 인덱스)` 등. 다른 쿼리 블록의 별칭이므로 `@qb`를 붙인다(§1.6.4) |
| 풀지 않고 FILTER로 남긴다 | 서브쿼리 안 | `NO_UNNEST` |
| FILTER를 조인 중간에 먼저 수행한다 | 서브쿼리 안 | `NO_UNNEST PUSH_SUBQ` |

- `PUSH_SUBQ`는 풀지 않은 서브쿼리에만 의미가 있다. 제거되는 행이 많을 때 유리하고, 서브쿼리 1회 비용이 크면 역효과다.
- `FILTER`로 남은 서브쿼리는 같은 입력값에 대해 결과를 캐싱하므로, 상관키의 종류가 적으면 Starts가 외부 건수보다 적다.

**뷰 병합**

- 단순 뷰는 기본적으로 병합된다. `GROUP BY`·`DISTINCT`가 있는 뷰는 Complex View Merging 대상이며 비용 기반으로 병합 여부가 결정된다.
- 다음이 포함된 뷰는 일반적으로 병합되지 않는다: `ROWNUM`, 분석함수, 집합연산자(`UNION` 등), `CONNECT BY`, `MODEL`.
- 병합을 막으려면 뷰 안에 `NO_MERGE` 또는 바깥에 `NO_MERGE(뷰별칭)`을 쓴다.

**튜너가 `NO_MERGE`를 쓰는 경우**
1. 선집계: 대량 테이블을 `GROUP BY`로 먼저 줄인 뒤 조인
2. 선중복제거: `DISTINCT`로 먼저 줄인 뒤 조인
3. 조인 순서 통제: 일부 테이블을 독립 블록으로 묶음
4. 함수 호출 지연: 최종 소량 결과에 대해서만 사용자 함수 호출

**뷰와 조인하는 방식**
- 뷰 결과 전체가 필요하면 `USE_HASH(V)`.
- 바깥 행이 소량이고 뷰 안 테이블에 조인키 인덱스가 있으면 `PUSH_PRED(V)` + `USE_NL(V)`로 바깥 행마다 인덱스 탐색을 한다. 집계 뷰라서 인덱스를 못 쓰는 것이 아니다.

**스칼라 서브쿼리 → 조인 변환**
1. 스칼라 서브쿼리는 매칭이 없어도 메인 행을 남기므로 `LEFT OUTER JOIN`으로 바꾼다. 매칭이 없을 때 `SUM`·`MAX` 등은 NULL, `COUNT`는 0을 반환하므로 `COUNT` 지표에만 `NVL(…, 0)`을 씌운다.
2. 같은 테이블에서 지표 여러 개를 구하면 인라인 뷰 하나에서 `CASE WHEN`으로 한 번에 집계한다(K34).
3. `COUNT(CASE WHEN 조건 THEN 1 END)`는 조건 건수, `COUNT(CASE WHEN 조건 THEN 1 ELSE 0 END)`는 전체 건수가 된다. `ELSE 0`을 쓰려면 `SUM`을 쓴다.
4. 조인 방식은 바깥 건수로 정한다. 대량이면 `USE_HASH(V)`, 소량이면 `PUSH_PRED` + `USE_NL`.

### 1.6.6 흔히 틀리는 설명

| 틀린 설명 | 올바른 설명 |
|---|---|
| NL은 Inner에 인덱스가 필수다 | 인덱스는 효율화 수단일 뿐 필수가 아니다. 비용은 Outer 건수 × Inner 1회 비용으로 본다 |
| NL 출력 = Outer A-Rows × Inner Starts | Outer A-Rows가 Inner Starts를 만들고, NL 출력은 실제 매칭 건수의 합이다 |
| Unnesting = 세미조인 변환 | 서브쿼리 블록을 조인 가능한 형태로 바꾸는 것이며 결과는 세미·안티·일반 조인 등 다양하다 |
| 세미조인은 중복을 제거한다 | 내부 중복이 외부 행을 여러 번 출력시키지 않는 존재 확인 조인이다 |
| FULL SCAN·PX SEND가 보이면 병목이다 | 처리량, 프루닝, 분배 목적, Buffers 비중을 함께 보고 판단한다 |
| 집계 뷰와는 NL 조인을 할 수 없다 | 조인 조건 푸시다운(`PUSH_PRED`)으로 뷰 안 인덱스를 NL로 탐색할 수 있다 |
| HASH JOIN에서는 파티션 프루닝이 안 된다 | Build 결과로 블룸 필터를 만들어 Probe 쪽 파티션을 거를 수 있다(`:BF0000`) |
| 작은 테이블은 항상 Broadcast | 작은 입력 크기 × DOP만큼 복제되므로 크기와 DOP를 함께 본다 |

---

## 1.7 시험 전략

### 근거 등급 (A/B/C/D)

- **A:** 공식 발표·공식 문서로 확인된 내용
- **B:** 복수 자료와 Oracle 원리가 교차 지지하는 내용
- **C:** 제한적 사례 또는 간접 근거
- **D:** 추정. 단독 출제 근거로 쓰지 않는다

복원 문제·후기는 공식 자료와 같은 수준으로 취급하지 않는다.

### 실기 핵심 범위

- Cardinality · Selectivity · Starts · A-Rows
- 조건 가공, 암묵 형변환, 날짜 범위 재작성
- 인덱스 액세스와 결합 인덱스 설계
- NL · Hash · Merge와 조인 순서
- Semi · Anti · Outer · 1:N 결과집합 의미
- 스칼라 서브쿼리 · Unnest · OR Expansion 등 쿼리 변환
- DISTINCT · GROUP BY · Top-N · Sort
- 파티션 프루닝, Full/Partial Partition-Wise Join, 병렬 분배
- 대량 DML · 파티션 DDL
- 개선 SQL의 결과집합 동일성

세부 중요도는 §2 패턴 목록의 S/A 등급을 따른다.

### 단정하지 않는 것

- TO-BE Plan이 항상 제공된다 / 항상 제공되지 않는다
- 특정 힌트가 항상 등장한다
- FULL SCAN·PX SEND가 보이면 병목이다
- 인덱스 스캔이 항상 FULL SCAN보다 낫다
- 작은 테이블은 항상 Broadcast가 정답이다

### 답안 작성 순서

1. 결과집합과 관계 확인: 출력 컬럼, PK/FK/UK, 일반·세미·안티·아우터 관계
2. 건수 흐름 계산: 필터 결과, 조인 증폭·축소, Starts/A-Rows, 집계 결과
3. 병목 특정: Operation 이름이 아니라 불필요 처리량의 원인을 수치로 쓴다
4. 개선안 작성: SQL / 힌트 / 인덱스 / DDL 중 필요한 수단
5. 결과집합 동일성 검증(G2)
6. TO-BE 실행계획 흐름 확인

### 힌트와 버전

- 공식 지원 힌트를 우선하고, 대상 별칭과 쿼리 블록을 정확히 지정한다.
- 버전 의존적 기능(`FETCH FIRST`, `LATERAL` 등 12c+)을 쓸 때는 `ROWNUM`·`ROW_NUMBER` 기반 원리도 함께 설명할 수 있어야 한다.

---

## 1.8 패턴 체계

### 중요도 등급

| 등급 | 의미 | 문제화 |
|:---:|---|---|
| **S** | 실기 문제 해결의 중심축. 독립 식별·개선·검증까지 숙달 | 단독 + 복합 |
| **A** | S와 자주 결합되는 핵심 보조축 | 단독 + 복합 |
| **B** | Oracle 튜닝에서 중요하나 직접 출제 근거가 S/A보다 약함 | S/A와 결합한 복합 문제 우선 |
| **C** | 이론상 유효하나 실기 직접 근거가 부족함 | 개념 확인 위주 |
| **F** | 공식 범위이나 튜닝 직접성이 낮은 문법 항목 | 안전망(§3.1) |

Oracle 기능이 존재한다는 사실만으로 S/A로 올리지 않는다. 패턴 표의 `근거` 열은 §1.7 근거 등급이다.

### 두 트랙: 출제 우선순위와 숙달 범위

중요도 등급(S/A/B/C/F)은 **SQLP 출제 우선순위**다. 숙달 범위는 이와 별도로 **SQL 튜닝 전 영역**으로 잡는다. 등급별 목표 수준은 다음과 같다.

| 등급 | SQLP 트랙 (시험 전, 2회독 종료 조건) | 전 영역 트랙 (시험 후 숙달 기준) |
|:---:|---|---|
| S / A | 실전 가능 — 진급 게이트 대상 | 실전 가능 |
| B | 개념 설명 가능 | 적용 가능 (실기형 문제에서 처방으로 쓸 수 있음) |
| C | 위치만 확인 | 개념 설명 가능 |
| F | 위치만 확인 | 위치만 확인 |

- **실전 가능:** 테마 비공개 실기형 문제에서 첫 제출로 진단·처방·검증을 완주한다.
- **적용 가능:** 해당 패턴이 들어간 실기형 문제에서 처방 방향을 고르고 SQL·DDL로 옮긴다.
- **개념 설명 가능:** 원리와 대표 징후를 한두 문장으로 설명하고, 실행계획·지표에서 알아본다.

**등급과 무관하게 전 영역 트랙에서 "적용 가능"을 목표로 하는 항목**

| ID | 항목 | 이유 |
|---|---|---|
| X02~X04 | SQL Plan Baseline / SQL Profile / SQL Patch | SQL을 고칠 수 없는 운영 환경의 1차 수단 |
| X10~X12 | 대기 이벤트 / AWR·ASH / SQL Monitor | Troubleshooting(TR) 판단의 증거 지표 |
| X09 | IOT / Cluster | 액세스 경로 설계의 선택지 |

출제는 SQLP 트랙을 따른다. 전 영역 트랙 항목은 SQLP 트랙 완료 전에는 S/A 문제에 결합하는 형태로만 다룬다.

### 분류

| # | 영역 | ID | 테마 |
|:---:|---|---|---|
| 1 | 결과집합 / Cardinality / Selectivity | C | T01 |
| 2 | Optimizer Statistics | S | T01 |
| 3 | Predicate / Sargability / 데이터 타입 | P | T02 |
| 4 | Table & Index Access Path | A | T02 |
| 5 | Index 설계 / 물리 특성 | I | T02 |
| 6 | Join Method / Order / Semantics | J | T03 |
| 7 | Subquery / Query Transformation | Q | T05 |
| 8 | SQL Rewrite / Query Block / Hint | R | T05 |
| 9 | Sort / DISTINCT / Set Operation | O | T04 |
| 10 | Group By / Aggregate / Analytic / Top-N | G | T07 |
| 11 | Partition | PT | T08 |
| 12 | Parallel Execution | PX | T09 |
| 13 | DML / Batch / DDL | D | T10 |
| 14 | Execution Plan / Runtime Statistics | E | T01 |
| 15 | Data Model Semantics | M | T01 |
| 16 | SQL 수행 구조 / Database Call | SC | T11 |
| 17 | SQL Trace / Response Time | T | T11 |
| 18 | Lock / Transaction / Concurrency | L | T12 |
| 19 | Performance Troubleshooting | TR | T13 |
| 20 | Plan Stability / 기타 | X | T13 |
| 21 | 복합 패턴 | CP | T13 |
| 22 | 공식범위 안전망 | F | 부록 |

---

# 2. 테마별 교안

## T01 Cardinality / 실행계획 기본

- **범위:** `C01~C10`, `S01~S10`, `E01~E12`, `M01~M05`
- **대표 판단:** 입력 → 출력 건수, Starts, 관계 다중성
- **핵심 기준:** K01~K12

### T01 · 답안 골격

§1.3 R1 판독 5-STEP을 그대로 쓴다. 모든 서술에 실측 수치를 인용한다.

### T01 · 패턴 목록

#### 결과집합 / Cardinality / Selectivity

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 Plan·징후 | 대응 |
|---|---|:---:|:---:|---|---|---|
| C01 | 단계별 결과 건수 계산 | S | A | 각 Row Source의 입력 → 필터 → 조인 → 집계 흐름을 계산한다 | 모든 Plan의 A-Rows 흐름 | 데이터 흐름 순서로 판독 |
| C02 | 선택도 | S | A | 조건이 전체 중 몇 %를 남기는지가 액세스·조인 방식 선택의 핵심 | Access/Filter Predicate | 조건식·통계·인덱스 재검토 |
| C03 | NDV 기반 등치조건 추정 | A | B | 균등 분포 가정 시 등치 선택도 ≈ 1/NDV | E-Rows 괴리 | 통계·히스토그램 검토 |
| C04 | 범위조건 Cardinality | A | B | 범위 폭과 값 분포가 건수를 결정 | INDEX RANGE SCAN / FTS | 범위 재작성·통계 검토 |
| C05 | 조인 Cardinality | S | A | PK/FK, NDV, 중복도에 따라 조인 출력이 늘거나 준다 | HASH/NL/MERGE JOIN | 조인 관계(1:1, 1:N, N:M)부터 명시 |
| C06 | Semi Join Cardinality | S | A | `EXISTS`는 존재만 확인하므로 내부 중복이 외부 행을 늘리지 않는다 | HASH/NL SEMI | 외부 건수가 상한 |
| C07 | Anti Join Cardinality | S | A | `NOT EXISTS`는 매칭되지 않는 외부 행만 반환 | HASH/NL ANTI | 제거 비율 확인 |
| C08 | GROUP BY 입출력 건수 | S | A | 입력 행 수와 그룹키 NDV가 출력 행 수를 결정 | HASH/SORT GROUP BY | 선집계·후집계 판단 |
| C09 | DISTINCT 전후 건수 | S | A | 1:N 증폭 후 DISTINCT가 중복 제거 비용을 만든다 | HASH/SORT UNIQUE | 세미조인·선집계로 구조 변경 |
| C10 | Top-N 결과 건수 | A | A | N건만 필요하면 전체 처리 전에 멈출 수 있는지 본다 | COUNT STOPKEY / SORT ORDER BY STOPKEY | ROWNUM·ROW_NUMBER 구조 점검 |

#### Optimizer Statistics

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 징후 | 대응 |
|---|---|:---:|:---:|---|---|---|
| S01 | E-Rows vs A-Rows 괴리 | S | A | 추정 오류가 액세스 경로·조인 순서·방식 오류로 전파된다 | `E-Rows × Starts` ≪/≫ A-Rows | 통계·분포·조건 상관성 점검 |
| S02 | 통계 없음 / 오래된 통계 | A | B | 부정확한 통계는 비용 추정을 왜곡 | 동적 통계 Note, 비정상 E-Rows | DBMS_STATS 수집 |
| S03 | NDV 오류 | A | B | 실제 NDV와 통계 NDV 차이가 선택도 오류 유발 | 등치조건 E-Rows 오차 | 통계 갱신 |
| S04 | Histogram / Skew | A | B | 편중 데이터에서 균등 분포 추정이 틀린다 | 특정 값에서만 Plan 악화 | 히스토그램 검토 |
| S05 | 컬럼 상관관계 | B | C | 선택도를 독립으로 곱하면 상관관계를 반영하지 못한다 | 복합조건 E-Rows 과소 | Column Group 통계 |
| S06 | Bind Peeking | B | C | 첫 실행의 바인드 값으로 계획이 정해진다 | 바인드 값별 성능 편차 | ACS·SQL 분기 검토 |
| S07 | Adaptive Cursor Sharing | C | C | 바인드 선택도별로 자식 커서를 분리 | 자식 커서 증가 | 개념 확인 |
| S08 | Dynamic Statistics | C | C | 통계 부족 시 파싱 시점 샘플링 | Plan Note | 통계 품질 개선 우선 |
| S09 | Statistics Feedback | C | C | 실행 결과를 다음 최적화에 반영 | 재실행 후 계획 변화 | 개념 확인 |
| S10 | System Statistics | B | C | CPU·I/O 특성이 비용 계산에 영향 | 같은 SQL의 비용 차이 | 개념 확인 |

#### Execution Plan / Runtime Statistics

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 지표 |
|---|---|:---:|:---:|---|---|
| E01 | Starts | S | A | Row Source 실행 횟수. NL·서브쿼리·PX 판독의 핵심 | Starts |
| E02 | A-Rows | S | A | 전체 실행 합계 실제 행 수. Starts로 나눠 회당 값을 구한다 | A-Rows |
| E03 | E-Rows | S | A | 1회 실행당 추정 행 수 | E-Rows |
| E04 | Buffers | A | B | 누적 논리 I/O. 자식을 빼서 자기 비용을 구한다 | Buffers |
| E05 | Reads / Writes | B | B | 물리 I/O·Temp 쓰기 | Reads/Writes |
| E06 | A-Time / E-Time | B | B | 실제·추정 시간. 병렬에서는 누적 의미에 주의 | A-Time |
| E07 | OMem / 1Mem / Used-Mem | B | B | Sort·Hash 작업 메모리 적합성 | OMem/1Mem |
| E08 | TempSpc | A | B | Sort·Hash가 메모리를 넘어 Temp를 쓴 신호 | TempSpc |
| E09 | Predicate Information | S | A | access·filter 조건의 실제 적용 위치 | Predicate Info |
| E10 | Pstart / Pstop | S | A | 파티션 프루닝 여부 | Pstart/Pstop |
| E11 | Row Source 데이터 흐름 | S | A | 자식 → 부모 입력과 Starts를 연결해 판독 | Plan tree |
| E12 | 필수 연산 vs 제거 가능 연산 | S | A | SORT·UNIQUE·PX SEND도 목적이 있으면 필수다 | 연산 목적 |

#### Data Model Semantics

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 진단 포인트 | 대응 |
|---|---|:---:|:---:|---|---|---|
| M01 | 관계 1:1 / 1:N / N:M | S | A | 관계 다중성이 조인 출력 건수와 중복 가능성을 결정 | PK/FK/UK, 조인 후 A-Rows | 관계를 먼저 명시 |
| M02 | 필수 / 선택 관계 | A | A | 선택 관계면 INNER 조인 시 행이 사라진다 | NULL 가능 FK | INNER/OUTER 결과 비교 |
| M03 | PK/FK 기반 결과 예측 | S | A | PK/FK로 조인 출력과 유일성을 판단 | 1:N 증폭 | DISTINCT·세미조인 필요성 판단 |
| M04 | 데이터 모델 → 조인 의미 | S | A | 출력 요구(존재 확인/상세 조회)와 관계로 INNER/OUTER/SEMI/ANTI 결정 | SELECT 컬럼 | 논리 관계 먼저 확정 |
| M05 | 유일성 증명과 DISTINCT 제거 | S | A | PK/UK·관계로 유일성이 보장되면 DISTINCT 불필요 | Unique key | 제거 전 유일성 증명 |

---

## T02 Predicate / Access / Index

- **범위:** `P01~P10`, `A01~A13`, `I01~I08`
- **대표 판단:** 조건의 인덱스 사용 가능성, access/filter, 인덱스 설계
- **핵심 기준:** K30~K33

### T02 · 답안 골격

| | 확정할 것 |
|---|---|
| ① | 인덱스를 못 쓰게 만드는 조건: 컬럼 가공, 형변환, `NVL`, `LIKE '%x'` |
| ② | 인덱스 컬럼 순서: 등치(조인키 포함) → 범위 → 정렬 (§1.6.3) |
| ③ | access / filter 분리: 테이블 filter를 인덱스 컬럼 추가로 access나 인덱스 filter로 옮길 수 있는가 |

개선 효과는 인덱스 스캔 비용과 테이블 방문 비용의 차이로 쓴다.

### T02 · 패턴 목록

#### Predicate / Sargability / 데이터 타입

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 징후 | 대응 |
|---|---|:---:|:---:|---|---|---|
| P01 | 컬럼 함수 가공 | S | A | `TRUNC(col)`, `TO_CHAR(col)` 등은 일반 B-tree 인덱스와 프루닝을 막는다 | FTS, filter | 범위식 재작성 / FBI |
| P02 | 암묵적 형변환 | S | A | 타입 불일치로 컬럼 쪽이 변환되면 인덱스를 못 쓴다 | `INTERNAL_FUNCTION`, `TO_NUMBER(col)` | 타입 일치 |
| P03 | 날짜 등치 → 범위 | S | A | `TRUNC(dt)=:d` → `dt >= :d AND dt < :d+1` | RANGE SCAN 가능 | 반개구간 |
| P04 | NVL/DECODE/CASE 조건 | A | B | 조건을 식으로 감싸면 인덱스·OR Expansion 가능성이 달라진다 | FILTER/FTS | 분기 검토 |
| P05 | 선택적 조건 | S | A | `:b IS NULL OR col = :b`는 선택도가 다른 호출을 한 SQL로 묶는다 | 단일 비효율 Plan | 분기 SQL / UNION ALL |
| P06 | LIKE 선행 와일드카드 | B | C | `'%abc'`는 B-tree 선두 탐색 불가 | FTS/FFS | 요구사항·인덱스 전략 재검토 |
| P07 | IN vs OR | A | B | 같은 의미라도 변환·액세스 경로가 다를 수 있다 | INLIST ITERATOR / CONCATENATION | 비교 |
| P08 | NULL과 인덱스 | A | A | 단일 컬럼 B-tree는 NULL 키를 저장하지 않는다 | `IS NULL` 조건 FTS | NOT NULL 컬럼 결합·상수 추가 |
| P09 | NOT IN + NULL | S | A | 서브쿼리 결과에 NULL이 있으면 `NOT IN`은 결과가 없다 | 안티조인 변환 제약 | `NOT EXISTS` |
| P10 | Access vs Filter | S | A | 탐색 범위를 줄이는 조건과 읽은 뒤 거르는 조건을 구분 | Predicate Info | 컬럼 순서·조건 수정 |

#### Table & Index Access Path

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 Plan | 대응 |
|---|---|:---:|:---:|---|---|---|
| A01 | TABLE ACCESS FULL | S | A | 대량 범위에서는 정상 경로이며 그 자체가 병목은 아니다 | TABLE ACCESS FULL | 비중·선택도·파티션·병렬과 함께 판단 |
| A02 | INDEX UNIQUE SCAN | A | A | PK/UK 전체 키 등치 탐색 | INDEX UNIQUE SCAN | Starts와 1건성 확인 |
| A03 | INDEX RANGE SCAN | S | A | 선두 컬럼 조건 범위만큼 리프를 읽는다 | INDEX RANGE SCAN | 조건·컬럼 순서 최적화 |
| A04 | INDEX FULL SCAN | B | B | 인덱스 순서대로 전체 리프를 싱글블록으로 읽는다 | INDEX FULL SCAN | 정렬 생략 가능성 |
| A05 | INDEX FAST FULL SCAN | B | B | 인덱스 전체를 멀티블록으로 읽되 순서는 보장하지 않는다 | INDEX FAST FULL SCAN | 커버링 |
| A06 | INDEX SKIP SCAN | B | C | 선두 컬럼 NDV가 낮을 때 비선두 조건으로 분할 탐색 | INDEX SKIP SCAN | 새 인덱스와 비용 비교 |
| A07 | INDEX MIN/MAX | B | C | 인덱스 한쪽 끝만 읽어 MIN/MAX 계산 | INDEX FULL SCAN (MIN/MAX) | 인덱스 활용 |
| A08 | 역순 인덱스 스캔 | B | C | 인덱스를 거꾸로 읽어 내림차순 정렬 생략 | INDEX RANGE SCAN DESCENDING | `INDEX_DESC` (K32) |
| A09 | TABLE ACCESS BY INDEX ROWID | S | A | ROWID로 테이블 블록 방문. 비용은 방문 건수 × 클러스터링 | TABLE ACCESS BY INDEX ROWID | 커버링·선택도 검토 |
| A10 | Batched ROWID Access | C | C | ROWID 방문을 묶어 블록 접근 효율을 높인다 | ... ROWID BATCHED | 개념 확인 |
| A11 | Bitmap Index | B | C | 낮은 NDV 다중 조건 분석에 유리, DML 동시성 취약 | BITMAP ... | OLTP 여부 판단 |
| A12 | Function-Based Index | A | B | 반복되는 식을 인덱스 키로 저장 | RANGE SCAN on FBI | SQL 재작성과 비교 |
| A13 | 행 이주 · 체이닝 | B | B | UPDATE로 커진 행이 다른 블록으로 옮겨가면 ROWID 방문 1회에 블록을 2개 이상 읽는다 | ROWID 노드의 1건당 블록 수 > 1 (반복 탐색 아님, K09) | PCTFREE 조정 후 재구성(MOVE·CTAS) |

#### Index 설계 / 물리 특성

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 진단 포인트 | 대응 |
|---|---|:---:|:---:|---|---|---|
| I01 | 결합 인덱스 컬럼 순서 | S | A | 등치/범위, 조인, 정렬을 종합해 선두·후행 결정 | access 범위 | 인덱스 재설계 |
| I02 | 선두 컬럼 조건 부재 | S | A | 선두 조건이 없으면 Range Scan 불가 또는 비효율 | Skip/Full/FTS | 새 인덱스 / Skip 비교 |
| I03 | 커버링 인덱스 | A | B | 필요한 컬럼이 모두 인덱스에 있으면 테이블 방문 제거 | 테이블 액세스 노드 | 포함 컬럼 검토 |
| I04 | 클러스터링 팩터 | A | B | 인덱스 순서와 테이블 저장 순서의 일치도가 ROWID 방문 비용을 결정 | ROWID 1건당 블록 수 | FTS와 비교, 재구성 |
| I05 | 인덱스 선택도 한계 | S | A | 결과가 많으면 인덱스보다 FTS가 싸다 | 인덱스 강제 시 Buffers 증가 | 인덱스 강제 금지 |
| I06 | 중복·유사 인덱스 | B | C | 과도한 인덱스는 DML·공간 비용 증가 | 선두 컬럼 중복 | 통합·삭제 |
| I07 | Local Index | A | A | 파티션과 같은 단위로 분할된 인덱스. 관리성·프루닝 유리 | PARTITION + INDEX | 파티션 키 조건 확인 |
| I08 | Global Index | A | A | 테이블 전체에 대한 단일 정렬 구조. 파티션 DDL 시 유지 비용 | UNUSABLE | `UPDATE GLOBAL INDEXES` |

### T02 · 보강

결합 인덱스 설계 원리는 §1.6.3을 본다.

---

## T03 Join Method / Join Order

- **범위:** `J01~J12`
- **대표 판단:** NL/Hash/Merge, 드라이빙, Build/Probe
- **핵심 기준:** K13~K19

### T03 · 답안 골격

| | 확정할 것 |
|---|---|
| ① | 건수 축소 순서: 테이블별 `[조건] 전체 N건 → M건`을 축소 효과가 큰 순으로 |
| ② | 조인 순서: `T1 → T2 → T3` + 인접한 두 테이블마다 조인 조건 한 줄 (K15) |
| ③ | 조인 방식: K18 비교식과 K19 범위 판단을 따른다 |

```
NL 쪽   = Outer 건수 × Inner 1회 비용(인덱스 높이 + 1건당 Inner 행 수)
HASH 쪽 = Inner FULL 블록 수 (테이블 통계)
Outer 읽는 비용은 양쪽 공통이라 비교에서 뺀다 → NL 쪽 < HASH 쪽이면 NL + 인덱스, 아니면 HASH + FULL
```

NL의 Inner를 FULL로 읽으면 Outer 건수만큼 풀스캔이 반복된다. FULL은 `USE_HASH`와 함께 쓴다.

### T03 · 패턴 목록

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 Plan | 대응 |
|---|---|:---:|:---:|---|---|---|
| J01 | Nested Loops | S | A | Outer 행마다 Inner 실행. Inner 인덱스는 효율화 수단이지 필수가 아니다 | NESTED LOOPS | LEADING/USE_NL, Inner 액세스 개선 |
| J02 | Hash Join | S | A | Build로 해시 테이블을 만들고 Probe로 대량 등치 조인 | HASH JOIN | USE_HASH, 선필터 |
| J03 | Merge Join | A | A | 두 입력을 정렬 후 병합. 범위 조인·이미 정렬된 입력에 유리 | MERGE JOIN / SORT JOIN | USE_MERGE |
| J04 | 조인 순서 / 드라이빙 | S | A | 앞 단계의 축소가 후속 Starts·입력 건수에 연쇄 영향 | LEADING 순서 | K13~K15 |
| J05 | Build/Probe 판단 | A | B | 작은 입력이 Build가 유리하나 실제 역할은 Plan으로 확인 | HASH JOIN 자식 순서 | 순서·SWAP_JOIN_INPUTS |
| J06 | Outer Join | S | A | 보존 테이블 행을 유지. 조건을 ON에서 WHERE로 옮기면 결과가 바뀐다 | NL/HASH OUTER | 결과 동일성 검증 |
| J07 | Semi Join | S | A | 존재만 필요하면 내부 중복이 외부 행을 늘리지 않는다 | NL/HASH SEMI | `EXISTS`, NL_SJ/HASH_SJ |
| J08 | Anti Join | S | A | 부재 조건을 조인으로 처리해 반복 FILTER를 줄인다 | NL/HASH ANTI | NL_AJ/HASH_AJ, 손익분기 |
| J09 | Cartesian Join | A | B | 조인 조건 누락 또는 의도적 조합 | MERGE JOIN CARTESIAN | 조인 조건 검증 |
| J10 | 1:N 증폭 | S | A | 다측과 일반 조인하면 기준 행이 중복 출력된다 | 조인 후 A-Rows 급증 | 세미조인·선집계 |
| J11 | 조인 조건 누락 | S | A | 상관·조인 조건 누락은 결과집합 자체를 바꾼다 | 카티션·과대 건수 | 조건 복원 |
| J12 | 조인 방식 강제의 함정 | A | A | USE_NL/USE_HASH만으로는 좋은 계획이 보장되지 않는다 | 힌트 후에도 비효율 | 순서·액세스와 함께 지정 |

### T03 · 보강

조인 순서와 방식의 원리는 §1.6.1, §1.6.2를 본다.

---

## T04 Semi / Anti / DISTINCT

- **범위:** `J07`/`J08`/`J10`, `Q01`/`Q02`, `R02`/`R03`/`R07`, `O01~O06`, `CP01~CP03`
- **대표 판단:** 존재·부재 확인, 중복 증폭 제거
- **핵심 기준:** K29, K21, K17, K18

### T04 · 답안 골격

| | 확정할 것 |
|---|---|
| ① | 논리 관계: 존재 확인(세미) / 부재 확인(안티) / 값 필요(조인) |
| ② | 1:N 증폭이면 `EXISTS`/`NOT EXISTS`로 전환한 뒤 DISTINCT 제거 (K29) |
| ③ | NULL: `NOT IN`은 서브쿼리 결과에 NULL이 하나라도 있으면 결과가 없다 → `NOT EXISTS` |

### T04 · 패턴 목록

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 Plan | 대응 |
|---|---|:---:|:---:|---|---|---|
| O01 | SORT ORDER BY | A | A | 정렬 입력 건수와 메모리·Temp가 비용 결정 | SORT ORDER BY | 입력 축소 / 인덱스 순서 활용 |
| O02 | SORT UNIQUE | S | A | 정렬 기반 중복 제거 | SORT UNIQUE | 중복 원인 제거 |
| O03 | HASH UNIQUE | S | A | 해시 기반 중복 제거 | HASH UNIQUE | 조인 증폭 여부 확인 |
| O04 | UNION vs UNION ALL | A | B | UNION은 중복 제거 비용이 추가된다 | SORT/HASH UNIQUE | 중복 제거 필요성 확인 |
| O05 | SORT JOIN | A | B | Merge Join을 위한 정렬 | SORT JOIN | 기존 정렬 활용 |
| O06 | Temp Spill | A | B | 정렬·해시가 메모리를 넘으면 Temp I/O | TempSpc / 1Mem | 입력 축소 / 방식 변경 |

### T04 · 보강

`EXISTS` 전환과 서브쿼리 제어는 §1.6.5를 본다. 세미조인은 첫 매칭에서 Inner 탐색을 멈춘다.

---

## T05 Scalar Subquery / Query Transformation

- **범위:** `Q01~Q18`, `R01~R17`
- **대표 판단:** 반복 Starts, Unnest, Push, Merge
- **핵심 기준:** K25~K28

### T05 · 답안 골격

| | 확정할 것 |
|---|---|
| ① | 서브쿼리 필터의 선택도와 현재 적용 시점 (조인 앞인가 뒤인가) |
| ② | 풀 것인가(UNNEST) 둘 것인가(NO_UNNEST) → LEADING 구성이 달라진다 (K25, K26) |
| ③ | 스칼라 서브쿼리라면 `LEFT OUTER JOIN` + `CASE WHEN` 1회 집계 + 바깥 건수에 맞는 조인 방식 |

```
풀지 않음 → 서브쿼리에 NO_UNNEST PUSH_SUBQ, LEADING에는 서브쿼리 테이블 없음
풀기     → 서브쿼리에 QB_NAME(qb) UNNEST, 메인 LEADING에 서브쿼리 테이블을 별칭@qb로 포함 + NL_SJ/HASH_SJ 등
인라인 뷰 → NO_UNNEST가 아니라 NO_MERGE
```

같은 상관키가 반복되면 FILTER의 서브쿼리 결과 캐싱으로 `NO_UNNEST`가 유리할 수 있다.

### T05 · 패턴 목록

#### Subquery / Query Transformation

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 Plan·징후 | 대응 |
|---|---|:---:|:---:|---|---|---|
| Q01 | 상관 서브쿼리 FILTER | S | A | 외부 행마다 서브쿼리가 반복 실행 | FILTER + Inner Starts | Unnest / 세미·안티 / 조인 변환 |
| Q02 | Subquery Unnesting | S | A | 서브쿼리 블록을 조인 가능한 형태로 변환. 결과는 세미·안티·일반 조인 등 | SEMI/ANTI/JOIN | UNNEST/NO_UNNEST, 결과 동일성 |
| Q03 | 스칼라 서브쿼리 반복 | S | A | 외부 행마다 단일값 서브쿼리 실행 | 메인 위의 별도 노드 Starts | 조인·선집계로 변환 |
| Q04 | 스칼라 서브쿼리 캐싱 | B | C | 같은 입력값이면 캐시된 결과 재사용 | Starts < 외부 건수 | 실제 Starts 확인 |
| Q05 | View Merging | A | B | 뷰 경계를 제거해 조인 순서·조건 최적화 범위를 넓힌다 | VIEW 제거 | MERGE/NO_MERGE |
| Q06 | Predicate Pushdown | A | A | 조건을 뷰 안으로 밀어 입력을 줄인다. 조인 조건 푸시다운은 NL에서 성립 | VIEW PUSHED PREDICATE | PUSH_PRED/NO_PUSH_PRED |
| Q07 | OR Expansion | S | A | 선택도가 다른 조건을 분기해 각기 다른 액세스 경로 사용 | CONCATENATION / UNION ALL | USE_CONCAT/NO_EXPAND |
| Q08 | WITH / Materialization | A | B | 공통 집합 재사용 또는 최적화 경계 생성 | TEMP TABLE TRANSFORMATION | 재사용 횟수와 Temp 비용 비교 |
| Q09 | Join Factorization | C | C | UNION ALL 분기의 공통 조인을 인수분해 | Plan 변형 | 개념 확인 |
| Q10 | Join Elimination | C | C | 제약조건으로 불필요한 조인 제거 | 조인 노드 부재 | 개념 확인 |
| Q11 | Star Transformation | C | C | 팩트-디멘션 환경의 비트맵 기반 변환 | BITMAP / STAR | 개념 확인 |
| Q12 | MV Query Rewrite | C | C | 사전 집계 MV로 쿼리 재작성 | MAT_VIEW REWRITE | 개념 확인 |
| Q13 | Subquery Pushing | A | A | 풀지 않은 서브쿼리의 평가 시점을 앞당겨 후속 입력을 줄인다 | FILTER 위치·Starts 변화 | 제거 행 수 vs 1회 비용 |
| Q14 | PUSH_SUBQ / NO_PUSH_SUBQ | A | A | 이른 평가 / 늦은 평가 유도. 항상 PUSH가 유리하지 않다 | 조인 전후 Starts | 손익 비교 |
| Q15 | 조건절 전이 | A | B | 등치 관계로 다른 테이블 조건을 유도 | Predicate의 파생 조건 | 유도 조건의 안전성 확인 |
| Q16 | Table Expansion | C | C | 파티션별로 다른 액세스 경로를 쓰도록 분기 | 분기된 UNION-ALL | 개념 확인 |
| Q17 | 공통 표현식 제거 | C | C | 반복 조건·식의 중복 평가 제거 | Predicate 단순화 | 개념 확인 |
| Q18 | 집합연산 → 조인 재작성 | C | C | MINUS/INTERSECT 일부를 안티·세미 조인으로 | SET OP 제거 | NULL·중복 의미 검증 |

#### SQL Rewrite / Query Block / Hint

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 진단·대응 |
|---|---|:---:|:---:|---|---|
| R01 | 결과집합 동일성 | S | A | 행 수·NULL·중복·정렬 의미를 보존 | G2 |
| R02 | JOIN → EXISTS | S | A | 상대 테이블 컬럼이 필요 없고 존재만 필요하면 세미조인 | DISTINCT 제거 가능 |
| R03 | NOT EXISTS FILTER → Anti Join | S | A | 반복 부재 검사를 조인으로 전환 | Starts 감소 |
| R04 | 스칼라 서브쿼리 → 조인 + 집계 | S | A | 반복 집계를 한 번의 집합 연산으로 | OUTER JOIN, 집계 위치 |
| R05 | OR → UNION ALL | S | A | 분기별 최적 액세스 경로 | 분기 상호배타성(LNNVL) |
| R06 | 선집계 후 조인 | A | B | 다측을 먼저 줄여 조인 입력·증폭을 막는다 | K20~K24 |
| R07 | 불필요 DISTINCT 제거 | S | A | 증폭 원인이 제거되면 Unique 연산 불필요 | PK·관계로 유일성 증명 |
| R08 | QB_NAME | A | A | 힌트를 정확한 쿼리 블록에 적용 | `QB_NAME`, `@qb` |
| R09 | LEADING | S | A | 조인 순서 제어 | K15 인접성 |
| R10 | USE_NL / USE_HASH / USE_MERGE | S | A | Inner 테이블에 조인 방식 지정 | K16 |
| R11 | INDEX / FULL | S | A | 액세스 경로 지정 | 선택도·비용이 명확할 때 |
| R12 | NO_MERGE / MERGE | A | B | 뷰 병합 경계 제어 | 목적 명확화 |
| R13 | UNNEST / NO_UNNEST | A | B | 서브쿼리 변환 여부 제어 | 세미·안티·조인 가능성 |
| R14 | 최소 힌트 | S | A | 필요한 제어만 사용 | 힌트마다 목적 설명 |
| R15 | PUSH_SUBQ / NO_PUSH_SUBQ | A | A | 풀지 않은 서브쿼리의 수행 시점 제어. UNNEST와 목적이 다르다 | 조인 입력·Starts 비교 |
| R16 | SWAP_JOIN_INPUTS | A | B | Hash Join의 Build/Probe 역할 제어 | 메모리·Temp 비교 |
| R17 | USE_CONCAT / NO_EXPAND | A | B | OR Expansion 유도·억제 | 분기별 선택도·인덱스 |

### T05 · 보강

#### 서브쿼리 조기 필터링: 두 접근안

당일 예약 10,000건을 진료과·의사와 조인한 뒤 마지막에 응급로그(20건)로 거르는 비효율을 해소한다.

```sql
-- 안 1: 풀지 않고 조인 전에 필터 수행
SELECT R.RESV_NO, R.PATIENT_ID, D.DEPT_NM, DOC.DOC_NM
  FROM TB_RESERV R, TB_DEPT D, TB_DOCTOR DOC
 WHERE R.DEPT_CD = D.DEPT_CD
   AND R.DOC_ID = DOC.DOC_ID
   AND R.RESV_STAT_CD = '01'
   AND R.RESV_DT = '20260817'
   AND EXISTS (SELECT /*+ NO_UNNEST PUSH_SUBQ INDEX(E IX_EMRG_01) */ 1
                 FROM TB_EMERGENCY_LOG E
                WHERE E.PATIENT_ID = R.PATIENT_ID
                  AND E.EMRG_LEVEL = 'L1'
                  AND E.LOG_DT >= '20260817');

-- 안 2: 풀어서 세미조인을 2순위로 수행
SELECT /*+ LEADING(R E@SQ D DOC) USE_NL(D) USE_NL(DOC)
           INDEX(R IX_RESV_01) INDEX(E@SQ IX_EMRG_01)
           INDEX(D PK_TB_DEPT) INDEX(DOC PK_TB_DOCTOR) */
       R.RESV_NO, R.PATIENT_ID, D.DEPT_NM, DOC.DOC_NM
  FROM TB_RESERV R, TB_DEPT D, TB_DOCTOR DOC
 WHERE R.DEPT_CD = D.DEPT_CD
   AND R.DOC_ID = DOC.DOC_ID
   AND R.RESV_STAT_CD = '01'
   AND R.RESV_DT = '20260817'
   AND EXISTS (SELECT /*+ QB_NAME(SQ) UNNEST NL_SJ */ 1
                 FROM TB_EMERGENCY_LOG E
                WHERE E.PATIENT_ID = R.PATIENT_ID
                  AND E.EMRG_LEVEL = 'L1'
                  AND E.LOG_DT >= '20260817');
```

- 조인 조건이 없는 D와 DOC를 R보다 먼저 두면 카티션 곱이 된다(K15).
- 서브쿼리는 상관키(`PATIENT_ID`)를 공급하는 R을 읽은 뒤에만 수행할 수 있다.
- 안 2에서 E는 서브쿼리 블록의 별칭이므로 메인 힌트에서는 `QB_NAME(SQ)`로 이름을 붙이고 `E@SQ`로 지정한다. 세미조인 방식은 서브쿼리 안의 `NL_SJ`가 정한다.

#### 스칼라 서브쿼리 → OUTER JOIN + 1회 집계

배송기사 15,000명마다 1,500만 건 배송이력의 완료금액과 실패건수를 스칼라 서브쿼리 두 개로 구하던 SQL을 바꾼다.

```sql
SELECT /*+ LEADING(D P V) USE_NL(P) USE_HASH(V)
           INDEX(D IX_DRIVER_01) INDEX(P PK_TB_DRIVER_PROFILE) */
       D.DRIVER_ID, D.DRIVER_NM, P.CAR_TYPE_CD,
       V.DONE_FEE_AMT,                       -- 원본 SUM 스칼라: 매칭 없으면 NULL
       NVL(V.FAIL_CNT, 0) AS FAIL_CNT        -- 원본 COUNT 스칼라: 매칭 없으면 0
  FROM TB_DRIVER D
  LEFT OUTER JOIN TB_DRIVER_PROFILE P
    ON P.DRIVER_ID = D.DRIVER_ID
  LEFT OUTER JOIN (SELECT /*+ NO_MERGE */
                          L.DRIVER_ID,
                          SUM(CASE WHEN L.DELIV_STAT_CD = 'DONE' THEN L.DELIV_FEE END) AS DONE_FEE_AMT,
                          COUNT(CASE WHEN L.DELIV_STAT_CD = 'FAIL' THEN 1 END)          AS FAIL_CNT
                     FROM TB_DELIVERY_LOG L
                    WHERE L.DELIV_DT >= '20260101'
                    GROUP BY L.DRIVER_ID) V
    ON V.DRIVER_ID = D.DRIVER_ID
 WHERE D.AREA_CD = 'SEOUL'
   AND D.JOIN_DT >= '20260101';
```

- 상태코드 조건을 뷰 WHERE로 내리면 다른 지표가 사라지므로 `CASE WHEN`으로 처리한다(K24).
- 바깥 기사 수가 소량이고 `TB_DELIVERY_LOG(DRIVER_ID, DELIV_DT)` 인덱스가 있으면 `PUSH_PRED(V) USE_NL(V)`로 기사별 탐색을 하는 안도 비교한다(K27).
- 매칭 행이 없을 때 `SUM` 스칼라 서브쿼리는 NULL, `COUNT` 스칼라 서브쿼리는 0을 반환한다. OUTER JOIN으로 바꾸면 둘 다 NULL이 되므로 `COUNT` 쪽만 `NVL(…, 0)`으로 원본과 맞춘다(G2-②).

---

## T06 Optional Predicate / OR Expansion

- **범위:** `P04`/`P05`/`P07`, `Q07`, `R05`/`R17`, `CP05`/`CP25`/`CP43`
- **대표 판단:** 호출 유형별 선택도와 분기
- **핵심 기준:** K34

### T06 · 답안 골격

| | 확정할 것 |
|---|---|
| ① | 분기 간 상호배타성: UNION ALL 분기가 겹치면 중복 발생 → `LNNVL` 등으로 배타 조건 추가 |
| ② | 분기별 인덱스: 각 분기가 어떤 인덱스를 쓰는지 1:1로 지정 |
| ③ | 분기 순서: 호출 빈도와 선택도가 높은 분기부터 |

①이 먼저다. 중복이 생기면 결과집합이 깨진다.

### T06 · 패턴 목록

`P04`, `P05`, `P07`(T02), `Q07`, `R05`, `R17`(T05)을 본다.

### T06 · 보강

#### 선택적 조건 유형

| 유형 | AS-IS | 문제 | TO-BE |
|---|---|---|---|
| 단일 컬럼 NVL | `COL = NVL(:b, COL)` | 옵티마이저가 `:b` NULL/NOT NULL 분기로 자동 확장하기도 하지만, 원래 의미상 `COL`이 NULL인 행은 `COL = COL`에서 탈락한다 | `:b IS NULL OR COL = :b`와 결과가 다른지 먼저 확인. 분기 SQL 또는 UNION ALL |
| 다중 컬럼 NVL | `A = NVL(:a, A) AND B = NVL(:b, B)` | 입력 조합마다 최적 경로가 다른데 계획은 하나 | 입력 조합별 UNION ALL 분기 |
| 컬럼 간 OR | `A_CD = :a OR B_CD = :b` | 한 인덱스로 두 컬럼 조건을 동시에 탐색할 수 없다 | UNION ALL + `LNNVL` |
| IN-List + Top-N | `STAT_CD IN ('A','B') ORDER BY REG_DT DESC` + Top 10 | 값별로는 정렬되어 있어도 합친 결과는 정렬되어 있지 않아 `SORT ORDER BY`가 남는다 | 값별 Top-N 후 합쳐 다시 Top-N |

#### LNNVL을 이용한 상호배타 분기

`LNNVL(조건)`은 조건이 FALSE 또는 UNKNOWN(NULL)일 때 TRUE를 반환한다. 앞 분기에서 이미 나온 행을 뒤 분기에서 제외하되, 비교 컬럼이 NULL인 행은 남긴다.

```sql
SELECT /*+ INDEX(A IX_TB_DOC_01) */ DOC_NO, REG_DT, CUST_ID, DEPT_CD
  FROM TB_DOC A
 WHERE CUST_ID = :CUST_ID
UNION ALL
SELECT /*+ INDEX(A IX_TB_DOC_02) */ DOC_NO, REG_DT, CUST_ID, DEPT_CD
  FROM TB_DOC A
 WHERE DEPT_CD = :DEPT_CD
   AND LNNVL(CUST_ID = :CUST_ID);
```

`AND (CUST_ID <> :CUST_ID OR CUST_ID IS NULL)`과 같은 의미다.

#### IN-List + Top-N

```sql
-- 인덱스: IX_TB_ORD_01 (STAT_CD, ORD_DT)
SELECT *
  FROM (SELECT *
          FROM (SELECT ORD_NO, ORD_DT, STAT_CD, ORD_AMT
                  FROM (SELECT ORD_NO, ORD_DT, STAT_CD, ORD_AMT
                          FROM TB_ORD
                         WHERE STAT_CD = 'A'
                         ORDER BY ORD_DT DESC)
                 WHERE ROWNUM <= 10
                UNION ALL
                SELECT ORD_NO, ORD_DT, STAT_CD, ORD_AMT
                  FROM (SELECT ORD_NO, ORD_DT, STAT_CD, ORD_AMT
                          FROM TB_ORD
                         WHERE STAT_CD = 'B'
                         ORDER BY ORD_DT DESC)
                 WHERE ROWNUM <= 10)
         ORDER BY ORD_DT DESC)
 WHERE ROWNUM <= 10;
```

각 분기는 인덱스를 역순으로 읽어 정렬 없이 10건에서 멈추고(`COUNT STOPKEY`), 최종 정렬은 20건만 한다. 분기 안에 `ORDER BY`를 두어야 정렬 의미가 보장된다.

#### 판단 포인트

- `USE_CONCAT`은 비용 기반으로 거부될 수 있다. 계획을 확정해야 하면 UNION ALL로 직접 작성한다.
- 분기 재작성 후에는 NULL 허용 컬럼의 배타 조건을 G2-②로 확인한다.

---

## T07 GROUP BY / Sort / Top-N

- **범위:** `C08~C10`, `O01~O06`, `G01~G11`
- **대표 판단:** 집계 위치, 정렬 생략, Stopkey, 분석함수
- **핵심 기준:** K20~K24, K32

### T07 · 답안 골격

| | 확정할 것 |
|---|---|
| ① | 집계 위치: R2-집계로 B와 C를 비교해 선집계/후집계 판정. 선집계면 `NO_MERGE` 인라인 뷰 |
| ② | 정렬 생략 인덱스: `(등치 조건, 정렬 컬럼1, 정렬 컬럼2 …)`로 SORT 제거 |
| ③ | Stopkey 성립: 인라인 뷰의 `ORDER BY`가 인덱스 순서로 처리되어 `ROWNUM <= N`에서 멈추는가 |

### T07 · 패턴 목록

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 Plan | 대응 |
|---|---|:---:|:---:|---|---|---|
| G01 | HASH GROUP BY | S | A | 해시 기반 그룹 집계. 비용은 입력 행 수와 메모리 | HASH GROUP BY | 선필터 / 선집계 |
| G02 | SORT GROUP BY | S | A | 정렬 기반 그룹 집계. 인덱스 순서로 입력이 오면 정렬 생략 가능 | SORT GROUP BY (NOSORT) | 인덱스 / 입력 축소 |
| G03 | GROUP BY 위치 | S | A | 조인 전후 집계 위치가 중간 건수와 결과 의미를 바꾼다 | GROUP BY 자식 A-Rows | R2-집계, K20~K24 |
| G04 | COUNT(*) vs COUNT(col) | A | B | `COUNT(col)`은 NULL을 세지 않는다 | Aggregate | NULL 의미 확인 |
| G05 | WINDOW SORT | A | A | 분석함수는 PARTITION BY·ORDER BY 순서로 정렬 | WINDOW SORT | 입력 축소 / 인덱스 |
| G06 | WINDOW NOSORT | A | A | 입력이 이미 요구 순서면 정렬 생략 | WINDOW NOSORT | `(PARTITION BY 컬럼, ORDER BY 컬럼)` 인덱스 |
| G07 | STOPKEY | S | A | N건 이후 처리를 멈춘다 | COUNT STOPKEY / SORT ORDER BY STOPKEY | 정렬을 인덱스로 대체 |
| G08 | ROWNUM Top-N | S | A | `ORDER BY`를 인라인 뷰 안에 두고 바깥에서 `ROWNUM` | COUNT STOPKEY | 적용 순서 검증 |
| G09 | ROW_NUMBER Top-N | S | A | 그룹별 Top-N. `rn <= N` 조건이 WINDOW 단계에서 조기 종료되는지 확인 | WINDOW SORT PUSHED RANK / NOSORT STOPKEY | 인덱스 / 조인 푸시다운 |
| G10 | FETCH FIRST | A | A | 12c+ Top-N 문법. 내부적으로 ROW_NUMBER로 변환된다 | WINDOW ... STOPKEY | ROWNUM 대안도 숙지 |
| G11 | 페이징 쿼리 | A | B | 뒤 페이지로 갈수록 앞 페이지 행을 모두 읽고 버린다. 정렬 인덱스 + Stopkey로 읽는 양을 `끝 행 번호`로 제한하고, 깊은 페이지는 직전 페이지의 마지막 키로 이어 읽는다 | COUNT STOPKEY + 바깥 `RNUM >= 시작` filter | 3단 ROWNUM 인라인 뷰 / 키 기반 페이징 |

### T07 · 보강

#### 다측 선집계 인라인 뷰

```
AS-IS: 마스터 10만 × 상세 1,000만 → 조인 결과 1,000만 행 → HASH GROUP BY
TO-BE: 상세 1,000만 → GROUP BY → 10만 행 → 마스터 10만과 조인
```

```sql
SELECT /*+ LEADING(C V) USE_HASH(V) */
       C.CUST_ID, C.CUST_NM,
       NVL(V.ORD_CNT, 0)   AS ORD_CNT,
       NVL(V.TOTAL_AMT, 0) AS TOTAL_AMT
  FROM TB_CUST C
  LEFT OUTER JOIN (SELECT /*+ NO_MERGE */
                          CUST_ID,
                          COUNT(*)     AS ORD_CNT,
                          SUM(ORD_AMT) AS TOTAL_AMT
                     FROM TB_ORD
                    WHERE ORD_DT >= '20260101'
                      AND ORD_DT <  '20260701'
                    GROUP BY CUST_ID) V
    ON V.CUST_ID = C.CUST_ID
 WHERE C.GRADE_CD = 'VIP';
```

- 뷰의 `GROUP BY`에 바깥 조인키(`CUST_ID`)가 있어야 한다(K24). 조인 상대 `TB_CUST`는 `CUST_ID`가 PK라 증폭이 없다(K23).
- 원본이 고객을 모두 보존했다면 `LEFT OUTER JOIN`, 주문이 있는 고객만 나왔다면 INNER JOIN이다(G2-①).
- 원본이 `ORD_CNT`가 없는 고객을 NULL로 보여줬다면 `NVL`을 씌우지 않는다(G2-②).
- **판정 주의:** 위 SQL은 VIP가 아닌 고객의 주문까지 모두 집계한다. VIP 조건이 고객을 크게 줄이면 조인이 필터 역할을 하므로(K21), 선집계보다 VIP 고객별로 주문을 인덱스 탐색하는 방식(`PUSH_PRED` + `USE_NL`)이나 후집계가 더 쌀 수 있다. R2-집계의 B와 C로 판단한다.

#### 그룹별 최신 1건

**해법 1: 바깥 행마다 인덱스로 1건만 읽기** (바깥 건수가 소량일 때)

```sql
-- 인덱스: IX_TB_APPR_01 (EMP_ID, APPR_DT)
SELECT /*+ LEADING(E V) USE_NL(V) */
       E.EMP_ID, E.EMP_NM, V.APPR_NO, V.APPR_DT, V.APPR_AMT
  FROM TB_EMP E
 CROSS APPLY (SELECT A.APPR_NO, A.APPR_DT, A.APPR_AMT
                FROM TB_APPR A
               WHERE A.EMP_ID = E.EMP_ID
               ORDER BY A.APPR_DT DESC
               FETCH FIRST 1 ROWS ONLY) V
 WHERE E.DEPT_CD = 'D01';
```

- `CROSS APPLY`/`LATERAL`(12c+)은 상관 조건이 명시되어 있어 `PUSH_PRED` 없이 사원마다 인덱스를 역순으로 1건 읽는다.
- 결재가 없는 사원도 보존하려면 `OUTER APPLY`를 쓴다.
- 11g에는 `CROSS APPLY`가 없다. 또 스칼라 서브쿼리 안에 "정렬 인라인 뷰 + 바깥 `ROWNUM`"을 두면 상관 참조가 두 단계 깊이가 되어 11g에서는 ORA-00904가 난다. 11g 대안은 둘이다.
  - **단일 블록 스칼라 서브쿼리:** `(SELECT /*+ INDEX_DESC(A IX_TB_APPR_01) */ A.APPR_AMT FROM TB_APPR A WHERE A.EMP_ID = E.EMP_ID AND ROWNUM <= 1)`. `ORDER BY` 없이 인덱스 역순 탐색에 기대는 방식이라 인덱스가 바뀌면 결과가 틀어질 수 있다. 필요한 컬럼마다 서브쿼리가 하나씩 필요하다.
  - **KEEP 집계:** `MAX(A.APPR_AMT) KEEP (DENSE_RANK LAST ORDER BY A.APPR_DT)`로 사원별 최신 행의 값을 구한다. 결과는 정확하지만 대상 사원의 결재를 모두 읽는다.

**해법 2: ROW_NUMBER + 인덱스 순서** (전체 대상 배치일 때)

```sql
SELECT EMP_ID, APPR_NO, APPR_DT, APPR_AMT
  FROM (SELECT A.*, ROW_NUMBER() OVER (PARTITION BY EMP_ID ORDER BY APPR_DT DESC) AS RN
          FROM TB_APPR A)
 WHERE RN = 1;
```

`(EMP_ID, APPR_DT)` 인덱스를 순서대로 읽으면 `WINDOW NOSORT`로 정렬은 생략되지만 전체 행은 읽는다. 전체 대상 배치에 적합하다.

#### 판단 포인트

| 질문 | 답 |
|---|---|
| 선집계 뷰에 `NO_MERGE`가 필요한 이유 | 옵티마이저가 Complex View Merging으로 뷰를 풀어 조인 후 집계로 되돌릴 수 있기 때문이다 |
| 선집계 뷰와는 HASH만 가능한가 | 아니다. 바깥 건수가 소량이면 `PUSH_PRED` + `USE_NL`로 뷰 안 인덱스를 탐색할 수 있다 |
| `PUSH_PRED`에 USE_NL이 필요한 이유 | 바깥 행의 값을 받아 뷰를 행마다 실행하는 구조이므로 NL에서만 성립한다 |
| 집계 순서를 바꿔도 되는 함수 | `SUM`·`COUNT`·`MIN`·`MAX`. 바깥 단계에서 `COUNT`는 `SUM(건수)`로 바꾸고, `AVG`는 `SUM(합)/SUM(건수)`로 분해한다 (K22) |

---

## T08 Partition / Pruning

- **범위:** `PT01~PT10`, `P01`/`P03`
- **대표 판단:** Static/Dynamic Pruning, 로컬/글로벌 인덱스, 파티션 DDL
- **핵심 기준:** K06

### T08 · 답안 골격

| | 확정할 것 |
|---|---|
| ① | 프루닝 성립: 파티션 키에 가공·형변환이 있는가 |
| ② | 결정 시점: 상수 → 파싱 시(Static), 바인드·조인·서브쿼리 → 실행 시(Dynamic, `KEY`) |
| ③ | 인덱스: 파티션 키 조건이 없는 Top-N이면 로컬 인덱스는 전 파티션을 읽는다 → 글로벌 인덱스 검토 |

①이 무너지면 조인 순서와 무관하게 전 파티션을 읽는다.

### T08 · 패턴 목록

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 Plan | 대응 |
|---|---|:---:|:---:|---|---|---|
| PT01 | Range/List/Hash 파티션 | A | A | 파티션 키와 분할 방식이 접근·관리·조인에 영향 | PARTITION ... | 파티션 키 확인 |
| PT02 | Static Pruning | S | A | 파싱 시 결정 가능한 조건으로 대상 파티션 확정 | PARTITION RANGE SINGLE / ITERATOR, 숫자 Pstart | 조건 형태 확인 |
| PT03 | Dynamic Pruning | S | A | 실행 시 바인드·조인값으로 대상 파티션 결정 | `KEY`, `KEY(SQ)`, `:BF0000` | NL 조인 / 블룸 필터 |
| PT04 | 파티션 키 가공 | S | A | 함수·형변환이 파티션 범위 추론을 막는다 | PARTITION RANGE ALL | 조건 재작성 |
| PT05 | Full Partition-Wise Join | S | A | 양쪽이 조인키로 같은 방식·같은 경계로 파티션되어 파티션 쌍끼리 조인 | 재분배 없음 | 파티션 키 = 조인키 |
| PT06 | Partial Partition-Wise Join | S | A | 한쪽만 조인키로 파티션. 다른 쪽을 그 기준으로 재분배 | PX SEND PARTITION (KEY) | 파티션된 쪽 확인 |
| PT07 | Local Index | A | A | 파티션과 같은 경계로 분할된 인덱스 | PARTITION + INDEX | 관리성 |
| PT08 | Global Index + 파티션 DDL | A | A | DROP/TRUNCATE/EXCHANGE 시 글로벌 인덱스가 UNUSABLE 될 수 있다 | UNUSABLE | `UPDATE GLOBAL INDEXES` |
| PT09 | EXCHANGE PARTITION | S | A | 데이터 복사 없이 세그먼트를 교환 | DDL | 인덱스·제약·검증 옵션 |
| PT10 | SPLIT/MERGE/MOVE/TRUNCATE | B | B | 유지보수와 인덱스 상태를 함께 판단 | DDL | 대상량·락 |

### T08 · 보강

#### Static vs Dynamic Pruning

| 구분 | Static | Dynamic |
|---|---|---|
| 결정 시점 | 파싱 시 | 실행 시 |
| 조건 형태 | 상수 리터럴 | 바인드 변수, NL 조인값, 서브쿼리, 블룸 필터 |
| Pstart / Pstop | 파티션 번호 | `KEY`, `KEY(SQ)`, `:BF0000` |
| 주의 | 파티션 키 가공·형변환 금지 | NL은 Outer 행마다 `KEY`로 파티션 선택. HASH JOIN은 Build 결과로 블룸 필터를 만들어 Probe 쪽 파티션을 거른다(`PART JOIN FILTER CREATE`) |

#### 파티션 키 없는 Top-N: 로컬 vs 글로벌 인덱스

- 로컬 인덱스는 파티션마다 따로 정렬되어 있다. 파티션 키 조건 없이 `ORDER BY REG_DT DESC` Top-10을 구하면 모든 파티션 인덱스를 읽고 합쳐 정렬해야 한다.
- 글로벌 비파티션 인덱스 `(ORD_STAT, REG_DT)`는 테이블 전체가 하나로 정렬되어 있어 역순으로 10건만 읽고 멈춘다.
- 대가로 파티션 DDL 시 글로벌 인덱스 유지 비용이 생긴다.

#### 판단 포인트

- 파티션 키 컬럼 타입과 비교값 타입을 일치시킨다. `VARCHAR2` 키에 `DATE` 값을 비교하면 컬럼이 변환되어 프루닝이 깨진다.
- 파티션 DDL 뒤에는 글로벌 인덱스 상태를 확인하고 필요하면 `UPDATE GLOBAL INDEXES`를 붙인다.
- `EXCHANGE PARTITION`은 세그먼트 교환이라 데이터량과 무관하게 빠르지만, 인덱스·제약 조건 정합성을 미리 맞춰야 한다(T10 보강).

---

## T09 PWJ / Parallel

- **범위:** `PT05`/`PT06`, `PX01~PX12`
- **대표 판단:** Full/Partial PWJ, PX 분배, DOP
- **핵심 기준:** 전용 K 없음. 판독은 K01~K12, 조인 방식은 K17·K18

### T09 · 답안 골격

| | 확정할 것 |
|---|---|
| ① | 양쪽 파티션 키와 조인키 일치 여부 → Full PWJ / Partial PWJ / 불가 |
| ② | 분배 방식: `PQ_DISTRIBUTE(Inner, Outer 분배, Inner 분배)` |
| ③ | 복제량 점검: BROADCAST는 입력 크기 × DOP만큼 복제된다. 대량 입력은 HASH 분배 |

```
Full PWJ       → PQ_DISTRIBUTE(B, NONE, NONE)
Partial PWJ    → PQ_DISTRIBUTE(B, PARTITION, NONE)   (B가 조인키로 파티션됨)
               → PQ_DISTRIBUTE(B, NONE, PARTITION)   (A가 조인키로 파티션됨)
소량 ↔ 대량    → PQ_DISTRIBUTE(B, BROADCAST, NONE)   (Outer A가 소량)
대량 ↔ 대량    → PQ_DISTRIBUTE(B, HASH, HASH)
```

### T09 · 패턴 목록

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 Plan | 대응 |
|---|---|:---:|:---:|---|---|---|
| PX01 | Query Coordinator | S | A | QC가 PX 서버 흐름과 최종 결과를 조정 | PX COORDINATOR / PX SEND QC | 흐름 판독 |
| PX02 | PX SEND / RECEIVE | S | A | 생산자·소비자 세트 간 데이터 이동. SEND 자체를 병목으로 단정하지 않는다 | PX SEND ..., PX RECEIVE | 이동 건수·목적 |
| PX03 | PX BLOCK ITERATOR | S | A | 블록 범위 단위로 스캔을 PX 서버에 분배 | PX BLOCK ITERATOR | 스캔량 |
| PX04 | PX SEND HASH | S | A | 조인·집계 키로 해시 재분배 | PX SEND HASH | 재분배 필요성 |
| PX05 | BROADCAST | S | A | 작은 입력을 모든 소비자에게 복제 | PX SEND BROADCAST | 크기 × DOP |
| PX06 | HASH-HASH 분배 | S | A | 양쪽을 조인키로 재분배. 대량 ↔ 대량 | 양쪽 PX SEND HASH | 이동량 |
| PX07 | PARTITION 분배 | S | A | 상대 파티션 구조에 맞춰 재분배 | PX SEND PARTITION (KEY) | PWJ 조건 |
| PX08 | PQ_DISTRIBUTE 문법 | S | A | `PQ_DISTRIBUTE(Inner, Outer 분배, Inner 분배)` | 힌트 | Inner/Outer 식별 |
| PX09 | DOP와 Starts | A | A | 병렬 노드의 Starts는 PX 서버 수·granule 수와 관련 | Starts ≈ DOP 등 | 합계 A-Rows로 판독 |
| PX10 | 병렬 집계 | A | A | 부분 집계 → 재분배 → 최종 집계로 이동량 축소 | GROUP BY 2단 | 선집계 |
| PX11 | Skew | A | B | 해시 키 편중으로 일부 PX 서버에 작업 집중 | PX별 편차 | 분배키 검토 |
| PX12 | 병렬 DML/DDL | B | B | 병렬 DML은 세션에서 활성화해야 한다 | PX + DML | `ENABLE PARALLEL DML` |

### T09 · 보강

#### PQ_DISTRIBUTE 선택

| 상황 | 분배 | 힌트 예 | 이동 |
|---|---|---|---|
| 소량 ↔ 대량 | BROADCAST | `LEADING(A B) USE_HASH(B) PQ_DISTRIBUTE(B, BROADCAST, NONE)` | 소량 A를 모든 소비자에 복제, B는 이동 없음 |
| 대량 ↔ 대량 | HASH-HASH | `LEADING(A B) USE_HASH(B) PQ_DISTRIBUTE(B, HASH, HASH)` | 양쪽을 조인키 해시로 분할 이동 |
| B만 조인키로 파티션 | Partial PWJ | `LEADING(A B) USE_HASH(B) PQ_DISTRIBUTE(B, PARTITION, NONE)` | A를 B의 파티션 기준으로 이동 |
| 양쪽 동일 파티션 | Full PWJ | `LEADING(A B) USE_HASH(B) PQ_DISTRIBUTE(B, NONE, NONE)` | 이동 없음 |

`PQ_DISTRIBUTE`는 조인 순서와 방식이 정해진 상태에서 의미가 있으므로 `LEADING`, `USE_HASH`와 함께 쓴다.

#### Slave Set 판독

- **1개 세트:** 재분배가 없는 경우(Full PWJ, 단순 병렬 스캔). 같은 PX 서버가 스캔과 조인을 모두 한다. TQ가 QC로 가는 것 하나다.
- **2개 세트:** `PX SEND HASH/BROADCAST/PARTITION` → `PX RECEIVE`가 있는 경우. 생산자 세트가 읽어서 보내고 소비자 세트가 받는다. PX 서버는 최대 DOP × 2개다.

#### 판단 포인트

- Full PWJ는 조인키가 파티션 키이고 양쪽 파티션 방식·경계(또는 해시 파티션 수)가 같아야 한다.
- 병렬 DML은 `ALTER SESSION ENABLE PARALLEL DML`이 필요하다. 병렬 조회는 기본 활성화되어 있다.

---

## T10 DML / Batch / DDL

- **범위:** `D01~D09`, `PT08~PT10`
- **대표 판단:** DELETE/INSERT/UPDATE vs CTAS/EXCHANGE
- **핵심 기준:** 전용 K 없음

### T10 · 답안 골격

| | 확정할 것 |
|---|---|
| ① | 변경 비율: 소량이면 DML, 대량이면 CTAS·EXCHANGE·TRUNCATE 검토 |
| ② | 부대 비용: Undo/Redo, 인덱스 유지, HWM, 락 유지 시간 |
| ③ | 절차: CTAS / EXCHANGE 사전 인덱스 / 인덱스 UNUSABLE → Direct Path → REBUILD |

### T10 · 패턴 목록

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 진단 포인트 | 대응 |
|---|---|:---:|:---:|---|---|---|
| D01 | 대량 DELETE 비용 | S | A | 행 단위 삭제는 Undo/Redo와 인덱스 유지 비용이 크다 | 삭제 비율 | TRUNCATE·CTAS·파티션 |
| D02 | DELETE+INSERT vs EXCHANGE | S | A | 파티션 대부분 교체는 세그먼트 교환이 유리 | 교체 비율 | 스테이징 + EXCHANGE |
| D03 | CTAS | A | A | 대량 재구성을 Direct Path로 수행 | 보존 비율 | CTAS 절차 |
| D04 | Direct-Path INSERT | A | B | HWM 위에 버퍼캐시를 거치지 않고 적재 | 공간·락·Redo 조건 | `APPEND` |
| D05 | TRUNCATE | A | A | 세그먼트 단위 제거. Undo가 거의 없고 롤백 불가 | 전체 삭제 여부 | TRUNCATE [PARTITION] |
| D06 | MERGE | B | B | 대량 Upsert의 조인 방식과 DML 비용 | matched 비율 | 소스 선필터·선집계 |
| D07 | Undo/Redo | A | A | 변경량에 비례하는 로그·복구 비용 | 대량 변경량 | Direct Path·DDL 대안 |
| D08 | 대량 DML과 동시성 | B | B | 장시간 DML은 락 유지 시간을 늘린다 | 락 유지 시간 | 작업 단위 분할 |
| D09 | 대량 UPDATE | S | A | 대상 탐색 비용 + 변경 컬럼 인덱스 유지 + Undo/Redo + 락 | 대상 건수, 변경 인덱스 수 | 조건 개선, 집합 UPDATE/MERGE, 재구성 |

---

## T11 Runtime / Trace / DB Call

- **범위:** `SC01~SC10`, `T01~T07`
- **대표 판단:** Parse/Execute/Fetch, 호출 횟수, 응답 시간 구성
- **핵심 기준:** 전용 K 없음. K05가 인접

### T11 · 답안 골격

| | 확정할 것 |
|---|---|
| ① | 호출 횟수: Fetch 횟수 ≈ 결과 건수 ÷ Array Size (+1) |
| ② | 행 단위 반복을 집합 처리로 바꿀 지점 |
| ③ | Array Size·Bulk 처리로 줄어드는 호출 수를 수치로 제시 |

### T11 · 패턴 목록

#### SQL 수행 구조 / Database Call

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 징후 | 대응 |
|---|---|:---:|:---:|---|---|---|
| SC01 | Parse / Execute / Fetch | A | A | SQL 수행 단계별 호출 | Trace call count | 단계별 call·rows 해석 |
| SC02 | Hard Parse vs Soft Parse | A | A | 공유 커서가 없으면 최적화부터 다시 한다 | Parse CPU, library cache 경합 | 바인드·공유성 |
| SC03 | 커서 공유 | A | A | 같은 SQL 텍스트 재사용이 Parse 부하를 줄인다 | 유사 SQL 다수 | 리터럴 남발 점검 |
| SC04 | Fetch Call 과다 | A | A | 작은 Array Size로 호출이 반복된다 | Fetch calls ≈ rows | Array Size 조정 |
| SC05 | Database Call 최소화 | A | A | 행 단위 반복 호출보다 집합 SQL이 호출·전환 비용을 줄인다 | Execute 반복 | 집합화 / Bulk |
| SC06 | Row-by-row → Set | A | A | 루프 처리를 집합 SQL로 치환 | 같은 SQL 고빈도 실행 | MERGE / INSERT SELECT / 집합 UPDATE |
| SC07 | Bind Variable | A | A | 공유성을 높이지만 분포 편중 컬럼은 계획 안정성 문제 | 리터럴 SQL 다수 | 공유성과 선택도 균형 |
| SC08 | Logical / Physical I/O | A | B | 버퍼캐시 경유 여부로 I/O를 구분 | Buffers, Reads, direct path | 읽기 방식 판단 |
| SC09 | Shared Pool / Library Cache | B | B | 커서 재사용 구조와 Parse 비용 | parse count, child cursor | 공유 실패 원인 |
| SC10 | PGA / Workarea | B | B | 작업 메모리 크기에 따라 optimal / one-pass / multi-pass | OMem/1Mem, TempSpc | 입력 축소 / 계획 변경 |

#### SQL Trace / Response Time

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 지표 | 대응 |
|---|---|:---:|:---:|---|---|---|
| T01 | Call Count | A | A | Parse/Execute/Fetch 횟수와 rows로 호출 비효율 판단 | call, count, rows | 호출 축소 |
| T02 | CPU vs Elapsed | A | A | Elapsed ≫ CPU면 I/O·대기·락 등 비CPU 요인 | cpu, elapsed | 대기 정보와 교차 분석 |
| T03 | disk / query / current | A | A | 물리 읽기 / consistent 읽기 / current 읽기 | disk, query, current | 액세스·DML 특성 연계 |
| T04 | Rows per Fetch | A | A | Fetch당 행 수가 작으면 호출 비효율 | fetch count, rows | Array Fetch |
| T05 | Trace + Plan 교차분석 | S | A | Trace의 비용과 Plan의 Row Source 흐름을 함께 봐 병목 특정 | call stats + Plan | Starts/A-Rows/Buffers 대조 |
| T06 | TKPROF 해석 | B | B | SQL별 CPU·Elapsed·I/O·Rows 집계 | TKPROF report | 고비용 SQL 우선순위 |
| T07 | 응답 시간 분해 | A | A | CPU, I/O, 대기, 호출 구조로 나눠 원인별 개선 | elapsed 구성 | 유형별 개선안 |

---

## T12 Lock / Transaction / Concurrency

- **범위:** `L01~L07`, `D07~D09`
- **대표 판단:** 락 종류, 블로커, 트랜잭션 길이, 커밋 주기
- **핵심 기준:** 전용 K 없음

### T12 · 답안 골격

| | 확정할 것 |
|---|---|
| ① | 락 종류: 행 경합(TX)인가, 테이블 DML 락(TM)인가 |
| ② | 블로커 추적: 대기 세션 → 락 보유 세션 → 보유 트랜잭션의 SQL·시작 시점 |
| ③ | 해소책: FK 인덱스 생성 / 트랜잭션 범위 축소 / 커밋 단위 조정 / 처리 순서 통일 |

### T12 · 패턴 목록

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 징후 | 대응 |
|---|---|:---:|:---:|---|---|---|
| L01 | TX Row Lock 경합 | A | A | 같은 행에 대한 동시 변경은 먼저 잡은 트랜잭션이 끝날 때까지 대기 | enq: TX - row lock contention | 트랜잭션 범위·접근 순서 |
| L02 | TM Lock | B | B | 테이블 DML 락은 DDL, 비인덱스 FK와 충돌 | enq: TM - contention | FK 인덱스, DDL 시점 |
| L03 | Blocking / Waiting | A | A | 대기 세션이 아니라 블로커의 트랜잭션을 찾아야 한다 | blocker/waiter | 블로커 SQL 분석 |
| L04 | Long Transaction | A | A | 락 유지 시간·Undo 사용량·복구 부담 증가 | 장시간 트랜잭션 | 작업 단위 재설계 |
| L05 | Commit 주기 | A | A | 너무 잦으면 log file sync 증가, 너무 드물면 락·Undo 부담 | log file sync, 락 유지 | 업무 단위 기준 |
| L06 | Hot Block / Hot Key | B | B | 특정 블록·키에 동시 접근 집중 | buffer busy, enq 경합 | 키 분산 |
| L07 | 인덱스 유지와 동시성 | B | B | 인덱스 수가 동시 DML 비용과 경합에 영향 | DML 지연 | 불필요 인덱스 제거 |

---

## T10~T12 보강

### 대량 DELETE의 비용

- **Undo/Redo:** 삭제되는 모든 행의 이전 이미지를 Undo에, 변경 내용을 Redo에 기록한다.
- **인덱스 유지:** 테이블의 모든 인덱스에서 해당 엔트리를 지운다. 인덱스 수만큼 추가 블록 변경이 생긴다.
- **HWM 유지:** DELETE는 HWM을 내리지 않으므로 이후 FULL SCAN은 빈 블록까지 읽는다.

### CTAS 재구성 절차

```sql
-- 1. 보존할 데이터만 새 테이블로 적재
CREATE TABLE 신규테이블 NOLOGGING PARALLEL 4
AS SELECT /*+ FULL(A) PARALLEL(A 4) */ *
     FROM 원본테이블 A
    WHERE 보존조건;

-- 2. 인덱스·제약조건 생성 (적재 후 생성해야 빠르다)
CREATE UNIQUE INDEX PK_신규 ON 신규테이블 (PK컬럼) NOLOGGING PARALLEL 4;
ALTER TABLE 신규테이블 ADD CONSTRAINT PK_신규 PRIMARY KEY (PK컬럼) USING INDEX PK_신규;
CREATE INDEX IX_신규_01 ON 신규테이블 (일반컬럼) NOLOGGING PARALLEL 4;

-- 3. 이름 교체 (원본은 검증이 끝날 때까지 보관)
RENAME 원본테이블 TO 원본테이블_OLD;
RENAME 신규테이블 TO 원본테이블;

-- 4. 속성 원복
ALTER TABLE 원본테이블 LOGGING NOPARALLEL;
ALTER INDEX PK_신규 LOGGING NOPARALLEL;
ALTER INDEX IX_신규_01 LOGGING NOPARALLEL;

-- 5. 검증 후 원본 제거
DROP TABLE 원본테이블_OLD PURGE;
```

- 권한(GRANT), 트리거, 참조 제약(FK), 통계를 다시 만들어야 한다.
- NOLOGGING 작업은 미디어 복구가 안 되므로 작업 후 백업한다.

### EXCHANGE PARTITION

```sql
-- 스테이징 테이블에 파티션 테이블의 로컬 인덱스와 같은 구조의 인덱스를 미리 만든다
CREATE UNIQUE INDEX PK_STG ON 스테이징테이블 (PK컬럼1, PK컬럼2);
ALTER TABLE 스테이징테이블 ADD CONSTRAINT PK_STG PRIMARY KEY (PK컬럼1, PK컬럼2) USING INDEX PK_STG;
CREATE INDEX IX_STG_01 ON 스테이징테이블 (일반컬럼1, 일반컬럼2);

ALTER TABLE 파티션테이블
  EXCHANGE PARTITION 대상파티션 WITH TABLE 스테이징테이블
  INCLUDING INDEXES
  WITHOUT VALIDATION
  UPDATE GLOBAL INDEXES;
```

- 데이터를 옮기지 않고 세그먼트를 맞바꾸므로 데이터량과 무관하게 빠르다.
- `INCLUDING INDEXES`는 스테이징 인덱스를 로컬 인덱스 파티션과 교환한다. 대응하는 인덱스가 없으면 그 로컬 인덱스 파티션은 UNUSABLE이 된다.
- `WITHOUT VALIDATION`은 데이터가 파티션 범위에 맞는지 검사하지 않는다. 범위가 보장될 때만 쓴다.
- 글로벌 인덱스는 `UPDATE GLOBAL INDEXES`가 없으면 UNUSABLE이 된다.

### Direct-Path INSERT

```sql
ALTER SESSION ENABLE PARALLEL DML;

INSERT /*+ APPEND PARALLEL(T 4) */ INTO 타겟테이블 T (컬럼1, 컬럼2)
SELECT /*+ FULL(S) PARALLEL(S 4) */ 컬럼1, 컬럼2
  FROM 소스테이블 S;

COMMIT;
```

- HWM 위에 버퍼캐시를 거치지 않고 기록한다. 테이블 데이터에 대한 Undo는 거의 생기지 않는다.
- Redo가 최소화되는 것은 테이블이 NOLOGGING이거나 DB가 NOARCHIVELOG일 때다. `APPEND`만으로는 Redo가 줄지 않는다.
- 테이블(또는 파티션)에 배타적 TM 락이 걸리고, 커밋 전에는 같은 세션도 그 테이블을 조회할 수 없다(ORA-12838).
- 인덱스는 적재 중 유지되므로 대량이면 UNUSABLE → 적재 → REBUILD 순서를 검토한다.

### Set-Based MERGE

```sql
MERGE INTO 타겟테이블 T
USING (SELECT 조인키, SUM(금액) AS SUM_AMT
         FROM 소스테이블
        GROUP BY 조인키) S
   ON (T.조인키 = S.조인키)
 WHEN MATCHED THEN
      UPDATE SET T.총금액 = T.총금액 + S.SUM_AMT
 WHEN NOT MATCHED THEN
      INSERT (조인키, 총금액) VALUES (S.조인키, S.SUM_AMT);
```

- 소스가 타겟 한 행에 여러 행 대응하면 ORA-30926이 난다. 소스를 조인키로 선집계한다.
- `ON` 절에 쓴 컬럼은 `UPDATE SET`으로 바꿀 수 없다.

### Parse / Execute / Fetch

| 단계 | 하는 일 |
|---|---|
| Parse | 문법·의미·권한 확인, 공유 커서 검색, 없으면 최적화(Hard Parse) |
| Execute | 바인드 적용 후 실행. DML은 이 단계에서 데이터를 변경한다 |
| Fetch | SELECT 결과 행을 Array Size 단위로 클라이언트에 전달 |

- Fetch 횟수 ≈ 결과 건수 ÷ Array Size (+ 마지막 확인 1회).
- Array Size를 키우면 호출 수와 블록 재방문이 줄지만 클라이언트 메모리 사용이 늘어난다.
- TKPROF `query`는 consistent 모드 읽기(주로 조회), `current`는 current 모드 읽기(주로 DML)다.

### PL/SQL Bulk 처리

```sql
DECLARE
    CURSOR C1 IS SELECT ... FROM 소스테이블 WHERE ...;
    TYPE T_TAB IS TABLE OF C1%ROWTYPE;
    V_TAB T_TAB;
BEGIN
    OPEN C1;
    LOOP
        FETCH C1 BULK COLLECT INTO V_TAB LIMIT 1000;
        FORALL i IN 1 .. V_TAB.COUNT
            INSERT INTO 타겟테이블 VALUES V_TAB(i);
        EXIT WHEN C1%NOTFOUND;
    END LOOP;
    CLOSE C1;
    COMMIT;
END;
```

단일 SQL로 처리할 수 있으면 그쪽이 먼저다. Bulk는 SQL과 PL/SQL 사이 전환 횟수를 줄이는 수단이다.

### 락

- **TX 락:** 행을 변경한 트랜잭션이 끝날 때까지 같은 행을 변경하려는 세션은 대기한다.
- **TM 락과 FK 인덱스:** 자식 테이블 FK 컬럼에 인덱스가 없으면 부모의 PK 변경·삭제 때 자식 테이블에 Share 수준 TM 락이 필요하다. 자식에 미커밋 DML이 있으면 부모 DML이 대기하고, 락을 잡는 동안 자식 DML이 막힌다. FK 컬럼에 인덱스를 만들어 해소한다.

```sql
CREATE INDEX IX_자식_FK ON 자식테이블 (FK컬럼);
```

- **커밋 주기:** 행마다 커밋하면 log file sync 대기가 늘고, 커밋하며 같은 커서를 계속 읽으면 ORA-01555 위험이 커진다. 한 번에 너무 크게 하면 락 유지 시간과 Undo가 늘어난다. 업무 단위와 재처리 가능성을 기준으로 정한다.

```sql
SELECT ... FROM 테이블 WHERE 조건 FOR UPDATE NOWAIT;      -- 즉시 실패 (ORA-00054)
SELECT ... FROM 테이블 WHERE 조건 FOR UPDATE WAIT 3;      -- 3초 대기 후 실패
SELECT ... FROM 테이블 WHERE 조건 FOR UPDATE SKIP LOCKED; -- 잠긴 행 건너뜀 (큐 처리)
```

---

## T13 종합 복합 튜닝

- **범위:** `CP01~CP45` 중 S/A, `TR01~TR10`, `X01~X13`
- **대표 판단:** 테마 비공개 AS-IS → TO-BE 종합 판단
- **핵심 기준:** 전 K. 한 문항에 두 개 이상의 K가 함께 걸린다

### T13 · 복합 패턴

| ID | 복합 패턴 | 결합 원자 패턴 | 핵심 진단 | 개선 방향 | 중요도 |
|---|---|---|---|---|:---:|
| CP01 | 1:N 조인 증폭 → DISTINCT | J10 + C09 + O02/O03 | 조인 후 증폭 뒤 Unique | 세미조인, 선집계 | S |
| CP02 | EXISTS를 일반 조인으로 잘못 재작성 | J07 + R01/R02 | 결과 건수 증가 | 세미 성격 보존 | S |
| CP03 | NOT EXISTS FILTER 반복 → Anti Join | Q01 + J08 + R03 | Inner Starts 폭증 | 안티조인 / Unnest | S |
| CP04 | 스칼라 서브쿼리 반복 + GROUP BY | Q03 + G01/G02 | 같은 테이블 반복 + 외부 집계 | 조인 + 선집계 | S |
| CP05 | 선택적 조건 + 단일 Plan | P05 + A01/A03 + R05 | 호출 유형별 선택도 차이 | UNION ALL 분기 | S |
| CP06 | 컬럼 가공 + 인덱스 미사용 | P01/P03 + A03 | FTS·filter 증가 | 범위 재작성 / FBI | S |
| CP07 | 암묵 형변환 + 조인 액세스 악화 | P02 + J01/A03 | Inner 인덱스 미사용 | 타입 일치 | S |
| CP08 | 추정 오류 → 조인 순서·방식 오류 | S01 + J04/J01/J02 | E/A-Rows 괴리 연쇄 | 통계·조건 수정 | S |
| CP09 | NL Outer 과대 + Inner 반복 | J01 + E01 + A09 | Inner Starts 과다 | Outer 축소 / HASH 전환 / 액세스 개선 | S |
| CP10 | Hash Join 대량 + Temp | J02 + O06/E08 | 입력 과대로 Temp 사용 | 선필터 / 선집계 | A |
| CP11 | 조인 후 GROUP BY vs 선집계 | J10 + G03 | 중간 건수 폭증 | 다측 선집계 | S |
| CP12 | Top-N + WINDOW SORT 대량 | G05/G09 + G07 | 전체 분석 후 소수 결과 | Stopkey / 인덱스 순서 | S |
| CP13 | ORDER BY + 인덱스 순서 | O01 + A04/A08 | 정렬 제거 가능 | 인덱스 설계 | A |
| CP14 | 파티션 키 가공 → 프루닝 실패 | PT04 + P01 | PARTITION RANGE ALL | 조건 재작성 | S |
| CP15 | 프루닝 실패 + 병렬 FULL | PT04 + PX03 | 불필요 파티션 병렬 스캔 | 프루닝 복구 | S |
| CP16 | 프루닝 실패 + HASH 재분배 | PT04 + PX04/PX06 | 스캔량 + 이동량 증가 | 프루닝 / PWJ | S |
| CP17 | Full PWJ 가능한데 HASH-HASH | PT05 + PX06 | 불필요 양쪽 재분배 | 파티션 쌍 조인 | S |
| CP18 | Partial PWJ + PARTITION(KEY) | PT06 + PX07 | 한쪽만 파티션 | 비파티션쪽 PARTITION 분배 | S |
| CP19 | 대량 ↔ 소량 + Broadcast | PX05 + J02 | 작은 집합 복제 | 적정 Broadcast | S |
| CP20 | 대량 ↔ 대량 + HASH-HASH | PX06 + J02 | 양쪽 재분배 | 필요성 검증 / PWJ | S |
| CP21 | 병렬 집계 2단계 | PX10 + G01 | 부분 집계 후 재분배 | 부분 집계 활용 | A |
| CP22 | 대량 DELETE + Undo/Redo | D01 + D07 | 행 단위 대량 변경 | TRUNCATE / CTAS / 파티션 | S |
| CP23 | 파티션 대부분 교체 + DELETE/INSERT | D02 + PT09 | 불필요 대량 DML | EXCHANGE | S |
| CP24 | 파티션 DDL + 글로벌 인덱스 | PT08 + D08 | UNUSABLE / 유지 비용 | UPDATE INDEXES | A |
| CP25 | OR 조건 + 인덱스별 선택도 | P07 + Q07 + R05 | 단일 경로 비효율 | OR Expansion / UNION ALL | S |
| CP26 | 뷰 + 조건 미푸시 | Q05/Q06 + C01 | 뷰 전체 처리 후 필터 | Merge / Push | A |
| CP27 | WITH Materialization + Temp | Q08 + O06 | 중간 집합 저장 비용 | Inline / 재사용 횟수 비교 | B |
| CP28 | DISTINCT 제거 후 결과 변형 | R07 + R01 | 중복 의미 오판 | 유일성 증명 후 제거 | S |
| CP29 | Outer Join + 조건 위치 변경 | J06 + R01 | 보존 행 소실 | ON/WHERE 의미 검증 | S |
| CP30 | NOT IN NULL + Anti 재작성 | P09 + J08 | 결과 불일치 | NOT EXISTS, NULL 검증 | S |
| CP31 | FILTER 조기 수행 → 후속 조인 감소 | Q01 + Q13/Q14 + J04 | 일찍 거르면 후속 조인량 감소 | PUSH_SUBQ | A |
| CP32 | 고비용 서브쿼리 조기 수행 역효과 | Q13/Q14 + E01 | 반복 비용 > 제거 이득 | NO_PUSH_SUBQ / Unnest | A |
| CP33 | UNNEST vs FILTER + PUSH_SUBQ | Q02 + Q13/Q14 + R13/R15 | 변환과 수행 시점 혼동 | 변환 가능성 → 수행 시점 순서로 판단 | S |
| CP34 | 선택 관계 + INNER JOIN → 행 소실 | M02 + M04 + J06 | 선택 관계를 필수로 처리 | OUTER JOIN / 조건 위치 | S |
| CP35 | 1:N 관계 + DISTINCT | M01/M03 + J10 + O02/O03 | 관계 다중성으로 중복 | 세미조인 / 선집계 / 유일성 증명 | S |
| CP36 | Parse 과다 + 리터럴 SQL | SC02/SC03/SC07 + TR05 | 공유 실패로 Hard Parse | 바인드 / 공유 구조 | A |
| CP37 | Fetch Call 과다 | SC04 + T04 | 호출 증가 | Array Fetch | A |
| CP38 | 행 단위 애플리케이션 호출 | SC05/SC06 + T01 | Execute/Fetch 폭증 | 집합 처리 / Bulk | A |
| CP39 | Lock Wait + Long Transaction | L01/L03/L04 + TR06 | 대기 시간이 지배 | 블로커 / 트랜잭션 범위 | A |
| CP40 | Temp Spill + 대량 Hash/Sort | O06 + E08 + TR07 | 메모리 초과 Temp I/O | 입력 축소 / 계획 변경 | A |
| CP41 | 조건절 전이 → 인덱스 액세스 | Q15 + P10 + A03 | 파생 조건이 access로 사용 | 전이 가능성·NULL 의미 검증 | A |
| CP42 | Hash Join + SWAP_JOIN_INPUTS | J02/J05 + R16 | Build/Probe 역할 비효율 | 순서와 입력 역할 함께 검증 | A |
| CP43 | OR Expansion + USE_CONCAT/NO_EXPAND | Q07 + R17 + P05/P07 | 분기별 경로 차이 | 분기 배타성 검증 | A |
| CP44 | Logical I/O 과다 + 호출 반복 | SC05/SC08 + TR03 | 블록 접근과 호출이 함께 증가 | 집합 처리 + 액세스 개선 | A |
| CP45 | 대량 UPDATE + 인덱스 유지 + Undo/Redo/Lock | D09 + D07 + L01/L04/L05 | 변경 컬럼이 여러 인덱스에 포함 | 대상 축소, 인덱스 영향 검토, 재구성 대안 | S |

### Performance Troubleshooting

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 | 대표 징후 | 대응 |
|---|---|:---:|:---:|---|---|---|
| TR01 | CPU 중심 SQL | A | A | 논리 I/O·연산량·함수·정렬이 CPU를 쓴다 | elapsed ≈ CPU | 논리 I/O·연산량 축소 |
| TR02 | I/O 중심 SQL | A | A | 많은 블록 읽기·비효율 액세스가 응답 시간을 지배 | Reads/Buffers 큼 | 액세스·인덱스·파티션 개선 |
| TR03 | 논리 I/O 과다 | S | A | 물리 I/O가 없어도 buffer get이 CPU와 래치 부담 | Buffers/query 큼 | 읽는 행·블록 축소 |
| TR04 | 물리 I/O 증가 | A | A | 캐시 미스·대량 FTS·Temp가 디스크 읽기 증가 | disk 큼 | 원인 구분 |
| TR05 | Parse 병목 | A | A | Hard Parse가 CPU와 library cache 경합 유발 | parse count 큼 | 바인드·공유 |
| TR06 | 락·동시성 병목 | A | A | SQL 비용보다 대기가 응답 시간을 지배 | elapsed ≫ CPU, enqueue | 블로커·트랜잭션 개선 |
| TR07 | Temp Spill 병목 | A | A | Sort/Hash 메모리 초과 | TempSpc, 1-pass/multi-pass | 입력 축소 / 방식 변경 |
| TR08 | 병렬 Skew | A | B | PX 서버 간 작업량 편중 | PX별 편차 | 분배키 개선 |
| TR09 | 추정 오류 연쇄 | S | A | 잘못된 추정이 액세스 → 순서 → 방식 → 메모리로 전파 | E/A-Rows 괴리 | 통계·조건 근본 수정 |
| TR10 | 진단 순서 | S | A | 증상을 CPU/I/O/Parse/Lock/Temp/PX/SQL 구조로 분류 후 증거로 좁힌다 | 여러 런타임 지표 | Trace·Plan 교차 검증 |

### Plan Stability / 기타

SQLP 직접 출제 근거가 약한 영역이다. SQLP 트랙에서는 B/C 우선순위로 개념 위치만 확인하고, 전 영역 트랙의 목표 수준은 §1.8 두 트랙 표를 따른다(X02~X04, X09~X12는 적용 가능 목표).

| ID | 패턴 | 중요도 | 근거 | 핵심 원리 |
|---|---|:---:|:---:|---|
| X01 | ALL_ROWS / FIRST_ROWS | B | C | 목표 응답 특성이 계획 선택에 영향 |
| X02 | SQL Plan Baseline | C | C | 검증된 계획 집합으로 계획 고정 |
| X03 | SQL Profile | C | C | 추정 보정 정보로 계획 개선 |
| X04 | SQL Patch | C | C | SQL 변경 없이 힌트 적용 |
| X05 | Adaptive Plan | C | C | 실행 중 통계로 조인 방식 등 일부 결정 변경 |
| X06 | Bloom / Join Filter | B | C | Build 결과로 Probe 쪽 행·파티션을 미리 거름 |
| X07 | One-pass / Multi-pass | B | C | 작업 메모리 부족 정도가 Temp I/O를 결정 |
| X08 | Child Cursor | C | C | 환경·바인드 차이로 커서가 분리 |
| X09 | IOT / Cluster | C | C | 특수 저장 구조의 액세스 경로 |
| X10 | Wait 기반 진단 | C | C | 시스템·세션 대기 이벤트 분석 |
| X11 | AWR / ASH / ADDM | C | C | 시스템 성능 진단 도구 |
| X12 | SQL Monitor | C | C | 장시간·병렬 SQL 실시간 통계 |
| X13 | 옵티마이저 파라미터 | C | C | 변환·비용 동작에 영향. 답안은 SQL·통계·힌트 중심 |

---

# 3. 부록

## 3.1 공식범위 안전망

튜닝 실기 학습축과 분리해 관리한다.

| ID | 항목 | 중요도 | 근거 | 핵심 의미 |
|---|---|:---:|:---:|---|
| F01 | 계층형 질의 / SELF JOIN | B | B | 결과집합·조인 의미 보존 관점으로만 연결 |
| F02 | PIVOT / UNPIVOT | C | B | 행 ↔ 열 변환 문법과 결과집합 |
| F03 | 정규표현식 함수 | C | B | REGEXP 조건의 의미와 CPU 비용 |
| F04 | TCL | C | B | COMMIT/ROLLBACK/SAVEPOINT. 성능은 L05·D07과 연결 |
| F05 | DCL | C | B | GRANT/REVOKE |
| F06 | 기본 SQL 문법 | C | A | SELECT/GROUP BY/HAVING/집합연산/NULL 의미 |

## 3.2 검증 축 → Pattern ID 색인

| 검증 축 | 주요 ID |
|---|---|
| 조건 가공 | P01~P05, CP06 |
| 인덱스 사용·설계 | A02~A13, I01~I08 |
| NL/Hash/Merge | J01~J05 |
| 조인 순서 | J04 |
| Semi/Anti | J07/J08, R02/R03 |
| Cardinality/Starts/A-Rows | C01~C10, E01~E03 |
| DISTINCT·중복 증폭 | C09, O02/O03, CP01 |
| Top-N/Stopkey/분석함수·페이징 | G05~G11 |
| GROUP BY | C08, G01~G04 |
| 파티션 프루닝 | PT02~PT04 |
| Full/Partial PWJ | PT05/PT06 |
| PX 분배 | PX01~PX08 |
| 대량 DML·DDL | D01~D09, PT09/PT10 |
| 결과집합 동일성 | R01 |
| PUSH_SUBQ | Q13/Q14, R15, CP31~CP33 |
| 데이터 모델 관계 | M01~M05, CP34/CP35 |
| Parse/Execute/Fetch | SC01~SC07 |
| SQL Trace | T01~T07 |
| Lock | L01~L07 |
| Troubleshooting | TR01~TR10 |
| 보조 변환 | Q15~Q18 |
| SWAP_JOIN_INPUTS / USE_CONCAT | R16, R17, CP42, CP43 |
| I/O·Shared Pool·PGA 기본 | SC08~SC10 |
| 공식범위 안전망 | F01~F06 |

## 3.3 표준 정답 아카이브 (2026-09-07 출제)

### 1) 정렬 생략 + Top-N

```sql
CREATE INDEX IDX_ORD_02 ON TB_ORDER (BRANCH_CD, ORD_DT);   -- 등치 선두, 정렬 컬럼 후행

SELECT *
  FROM (SELECT /*+ INDEX_DESC(O IDX_ORD_02) */
               O.ORD_NO, O.ORD_DT, O.CUST_ID, O.ORD_AMT, O.ORD_STAT
          FROM TB_ORDER O
         WHERE O.BRANCH_CD = 'B017'
           AND O.ORD_DT >= TO_DATE('20260801', 'YYYYMMDD')   -- TO_CHAR 가공 제거
           AND O.ORD_DT <  TO_DATE('20260901', 'YYYYMMDD')   -- 시분초 안전한 반개구간
         ORDER BY O.ORD_DT DESC)
 WHERE ROWNUM <= 20;
```

Buffers 100,253 → 24. 인덱스를 역순으로 읽어 정렬 없이 20건에서 멈춘다.

### 2) 조인 통로 인덱스 + 후집계

```sql
CREATE INDEX IDX_SALES_02 ON TB_SALES (CUST_ID, SALE_DT);  -- NL Inner: 조인키 선두

SELECT /*+ LEADING(R C O) USE_NL(C) INDEX(C PK_CUST)
                          USE_NL(O) INDEX(O IDX_SALES_02) */
       R.CUST_ID, C.CUST_NM, COUNT(*) AS SALE_CNT, SUM(O.SALE_AMT) AS SALE_AMT
  FROM TB_CAMP_RESP R, TB_CUST C, TB_SALES O
 WHERE R.CAMP_ID = 'C2608'
   AND C.CUST_ID = R.CUST_ID
   AND O.CUST_ID = R.CUST_ID
   AND O.SALE_DT >= TO_DATE('20260801', 'YYYYMMDD')
   AND O.SALE_DT <  TO_DATE('20260901', 'YYYYMMDD')
 GROUP BY R.CUST_ID, C.CUST_NM;
```

Buffers 636,018 → 58,018. 캠페인 응답 고객이 필터 역할을 하므로 500만 건을 집계하지 않고 응답 고객의 매출만 인덱스로 읽는다.

### 3) 세미 / 안티 분별

```sql
CREATE INDEX IDX_PUR_02 ON TB_PURCHASE (CUST_ID, PUR_DT);  -- 커버링: 테이블 방문 없음

SELECT C.CUST_ID, C.CUST_NM, C.GRADE_CD                    -- PK + 비증폭이라 DISTINCT 불필요
  FROM TB_MEMBER C
 WHERE C.GRADE_CD = 'VIP'
   AND EXISTS (SELECT /*+ NL_SJ INDEX(P IDX_PUR_02) */ 1
                 FROM TB_PURCHASE P
                WHERE P.CUST_ID = C.CUST_ID
                  AND P.PUR_DT >= TRUNC(SYSDATE) - 90)
   AND NOT EXISTS (SELECT /*+ HASH_AJ FULL(M) */ 1
                     FROM TB_CLAIM M
                    WHERE M.CUST_ID = C.CUST_ID
                      AND M.CLAIM_DT >= TRUNC(SYSDATE) - 90);
```

Buffers 633,200 → 123,200. 한 SQL 안의 두 서브쿼리가 손익분기에 따라 다른 방식을 쓴다(Inner 600,000블록 → NL, Inner 3,200블록 → HASH).

### 4) 선집계

```sql
CREATE INDEX IDX_SALE_02 ON TB_SALE_DTL (SALE_DT, PROD_ID, QTY, AMT);  -- 범위키 선두 + 커버링

SELECT /*+ LEADING(D P G) USE_HASH(P) USE_HASH(G) */
       P.PROD_ID, P.PROD_NM, G.CATE_NM, D.SALE_QTY, D.SALE_AMT
  FROM (SELECT /*+ NO_MERGE INDEX(D2 IDX_SALE_02) */
               D2.PROD_ID, SUM(D2.QTY) AS SALE_QTY, SUM(D2.AMT) AS SALE_AMT
          FROM TB_SALE_DTL D2
         WHERE D2.SALE_DT >= TO_DATE('20260801', 'YYYYMMDD')
           AND D2.SALE_DT <  TO_DATE('20260901', 'YYYYMMDD')
         GROUP BY D2.PROD_ID) D,                                  -- 500만 → 8만
       TB_PROD P, TB_CATEGORY G
 WHERE P.PROD_ID = D.PROD_ID
   AND G.CATE_CD = P.CATE_CD;
```

Buffers 601,005 → 약 23,700, Temp 사용 소멸. P·G는 PK 조인이라 행이 늘지 않으므로 바깥 GROUP BY가 필요 없다.
