옵티마이저

31.
  - 조건서브쿼리 + 서브쿼리 블록 이용( ex)qb_name(subq) ) 조인 유도
  - 메인 쿼리에서 사용 ex) leading(거래@subq)
  - unnest(@subq) leading(거래@subq) use_nl(c)
 
 32.
  - /*+ unnest aj_hash index_ffs(거래 거래_pk)
  - aj_hash(not exists 조건 사용시)

33.

  - /*+ no_unnest push_subq */ -> 서브 쿼리 조건 -> 조건 선처리
   
36.
  - /*+ no_merge(t) leading(t) use_nl(c) */

37.
```
/*+ merge(t) leading(c) use_nl(t)
    index ~
*/
```

38.
```
/*+ no_merge(t) push_pred(t) leading(c) use_nl(t)
    index ~
*/
``` 

39.
```
/*+ no_merge(t) push_pred(t) orderd use_nl(t) index ~ */
```

41.
```
조인 Pushdown, 조건절 pushdown -> 둘중 하나 선택
```












