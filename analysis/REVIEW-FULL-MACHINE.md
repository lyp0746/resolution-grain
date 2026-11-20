# 通读审计（source-v2，2026-11-20）

> 机器可查项一次数完；人读结论另见各节评注。由 `analysis/audit_full_read.py` 生成。

## 一、每章读数

| 章 | 汉字 | 节 | 表 | 图 | 段 | 题记 | 数据源 | 定义框 | 破折号 | 加粗 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 10420 | 8 | 4 | 1 | 106 | 1 | 5 | 1 | 43 | 149 |
| 2 | 11477 | 8 | 8 | 1 | 107 | 2 | 8 | 0 | 31 | 169 |
| 3 | 11928 | 10 | 6 | 3 | 102 | 1 | 6 | 0 | 44 | 182 |
| 4 | 10439 | 10 | 7 | 1 | 93 | 1 | 7 | 0 | 44 | 154 |
| 5 | 9075 | 9 | 4 | 1 | 93 | 1 | 4 | 0 | 41 | 148 |
| 6 | 10707 | 11 | 7 | 3 | 91 | 1 | 7 | 0 | 48 | 202 |
| 7 | 8718 | 8 | 4 | 1 | 88 | 1 | 6 | 0 | 45 | 182 |
| 8 | 9993 | 10 | 3 | 1 | 108 | 1 | 4 | 0 | 54 | 223 |
| 9 | 9089 | 8 | 7 | 1 | 112 | 1 | 6 | 0 | 24 | 117 |
| 10 | 9452 | 9 | 7 | 2 | 103 | 1 | 6 | 0 | 18 | 129 |
| 11 | 8268 | 10 | 4 | 1 | 106 | 1 | 1 | 0 | 11 | 96 |
| 12 | 9305 | 10 | 3 | 1 | 114 | 1 | 2 | 0 | 17 | 148 |
| 13 | 11334 | 10 | 7 | 1 | 100 | 1 | 8 | 0 | 65 | 205 |
| 14 | 9073 | 8 | 6 | 1 | 83 | 1 | 6 | 0 | 39 | 181 |
| 15 | 9767 | 10 | 4 | 1 | 94 | 1 | 5 | 0 | 43 | 217 |
| 16 | 9218 | 8 | 5 | 1 | 80 | 1 | 7 | 0 | 60 | 196 |
| 17 | 9267 | 10 | 5 | 1 | 88 | 1 | 7 | 0 | 50 | 186 |
| 18 | 8825 | 8 | 4 | 1 | 89 | 1 | 5 | 0 | 41 | 204 |
| 19 | 8926 | 9 | 3 | 2 | 90 | 1 | 4 | 0 | 47 | 212 |
| 20 | 8204 | 9 | 4 | 1 | 77 | 1 | 4 | 0 | 40 | 191 |
| 21 | 9264 | 8 | 2 | 1 | 97 | 1 | 3 | 0 | 42 | 228 |
| 22 | 8902 | 8 | 3 | 1 | 88 | 1 | 4 | 0 | 47 | 209 |
| 23 | 10101 | 9 | 4 | 2 | 94 | 1 | 5 | 0 | 50 | 221 |
| 24 | 12833 | 10 | 5 | 1 | 106 | 1 | 6 | 0 | 52 | 206 |
| 25 | 9343 | 11 | 3 | 1 | 83 | 1 | 4 | 0 | 32 | 174 |
| 26 | 9329 | 10 | 6 | 1 | 91 | 1 | 6 | 0 | 36 | 185 |
| 27 | 9347 | 10 | 3 | 1 | 89 | 1 | 5 | 0 | 46 | 195 |
| 28 | 8631 | 10 | 4 | 1 | 83 | 1 | 5 | 0 | 40 | 188 |
| 29 | 10322 | 11 | 5 | 1 | 98 | 1 | 7 | 0 | 41 | 238 |
| 30 | 10076 | 10 | 3 | 1 | 99 | 1 | 5 | 0 | 46 | 220 |
| 31 | 8997 | 10 | 2 | 2 | 93 | 1 | 2 | 0 | 43 | 184 |
| 32 | 12943 | 12 | 4 | 1 | 126 | 1 | 5 | 0 | 65 | 305 |
| 33 | 9847 | 10 | 4 | 1 | 99 | 3 | 5 | 0 | 60 | 216 |

合计：汉字 323420；表 150；图 41；节 312。

## 二、问题清单（按严重度）

### P0（0）

无。

### P1（2）

- `ch12.html`：版本史「第一版」第 128 行
- `ch33.html`：缺：本章小结

### P2（0）

无。

## 三、重复段落

- `ch03.html` 与 `ch02.html`：Shannon,C.E.(1948).AMathematicalTheoryofCommunication.BellSystemTechni…
- `ch05.html` 与 `ch01.html`：Turing,A.M.(1950).Computingmachineryandintelligence（《计算机器与智能》）.Mind,59…
- `ch06.html` 与 `ch02.html`：Bennett,W.R.(1948).SpectraofQuantizedSignals.BellSystemTechnicalJourna…
- `ch13.html` 与 `ch02.html`：Monderer,D.,&amp;Shapley,L.S.(1996).PotentialGames.GamesandEconomicBeh…
- `ch17.html` 与 `ch01.html`：Frontinus,S.J.（弗朗提努斯）(97CE).DeaquaeductuurbisRomae（《论罗马的水道》）.（九条渠、quin…
- `ch28.html` 与 `ch27.html`：Granovetter,M.(1973).Thestrengthofweakties.AmericanJournalofSociology,…
- `ch28.html` 与 `ch25.html`：Turchin,P.,etal.(2015).Seshat:TheGlobalHistoryDatabank.Cliodynamics,6(…
- `ch29.html` 与 `ch01.html`：Murray,J.A.H.(ed.)(1884).ANewEnglishDictionaryonHistoricalPrinciples,P…
- `ch33.html` 与 `ch32.html`：Meehl,P.E.(1978).Theoreticalrisksandtabularasterisks.JournalofConsulti…

## 四、符号使用频次（`<i>字母</i>`）

| 符号 | 次数 | 首见 |
|---|---|---|
| C | 876 | ch02.html |
| w | 560 | ch01.html |
| T | 385 | ch01.html |
| λ | 329 | ch01.html |
| γ | 308 | ch01.html |
| ν | 295 | ch01.html |
| q | 293 | ch01.html |
| k | 243 | ch02.html |
| A | 226 | ch02.html |
| v | 219 | ch01.html |
| ρ | 194 | ch06.html |
| μ | 186 | ch01.html |
| D | 147 | ch01.html |
| κ | 147 | ch03.html |
| n | 139 | ch01.html |
| b | 135 | ch03.html |
| H | 134 | ch02.html |
| τ | 127 | ch02.html |
| R | 119 | ch01.html |
| Φ | 115 | ch02.html |
| p | 101 | ch06.html |
| δ | 98 | ch02.html |
| I | 96 | ch01.html |
| θ | 90 | ch02.html |
| a | 89 | ch02.html |
| c | 73 | ch07.html |
| r | 71 | ch02.html |
| g | 70 | ch15.html |
| B | 69 | ch03.html |
| M | 67 | ch02.html |
| φ | 67 | ch03.html |
| t | 66 | ch03.html |
| s | 60 | ch08.html |
| Δ | 52 | ch06.html |
| K | 52 | ch14.html |
| e | 44 | ch03.html |
| F | 42 | ch02.html |
| L | 41 | ch02.html |
| h | 36 | ch08.html |
| i | 26 | ch03.html |
| V | 25 | ch20.html |
| N | 23 | ch11.html |
| U | 21 | ch03.html |
| β | 20 | ch11.html |
| j | 19 | ch03.html |
| d | 18 | ch02.html |
| u | 18 | ch08.html |
| Π | 17 | ch03.html |
| ω | 15 | ch01.html |
| α | 12 | ch27.html |
| W | 10 | ch08.html |
| χ | 9 | ch10.html |
| G | 8 | ch02.html |
| P | 8 | ch02.html |
| J | 8 | ch03.html |
| X | 8 | ch03.html |
| Λ | 7 | ch01.html |
| y | 6 | ch08.html |
| ξ | 6 | ch14.html |
| η | 6 | ch21.html |
| σ | 5 | ch31.html |
| f | 4 | ch27.html |
| Y | 4 | ch30.html |
| π | 3 | appendix_a.html |
| E | 3 | appendix_a.html |
| O | 2 | ch03.html |
| Q | 2 | ch12.html |
| z | 2 | ch25.html |

## 五、文风读数

- 正文汉字 323420；句 10133；句长中位 36，p90 72
- 段 2951；段长中位 122
- 破折号 1405（约 1/230 字）；感叹号 0；加粗 6260

## 六、索引事实

- sec：378
- tab：150
- fig：43
- eq：18
