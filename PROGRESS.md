# PROGRESS

2026-07-03 修复 P0 三项并验证：install.sh 拒绝空/路径参数（沙盒实测）；magnitude_consistency 前缀按幂次换算（15 用例+smoketest 通过）；fno-burgers 真值改为细网格求解+谱截断（收敛到 float32 精度），全量重跑 2072s——FNO 6.67%→4.41%（差值即原伪影），超分辨率带 4.2–4.7% 变平坦，相关文档数字已同步。遗留：paper.pdf 无 tex 源，仍含旧数字；P1/P2 bug 未修。

2026-07-03 全库 bug 审查（~5000 行）：确认 12 个真实 bug。P0：install.sh 空参数会清空用户 skills 目录（已实测复现）；fno-burgers 的 ν=1e-3@128 真值欠分辨（实测污染 5.9% rel-L2，与 FNO 实测误差 6.7% 同量级，headline 结果失真）；magnitude_consistency 的 mm²/cm³ 前缀换算错 10~1000 倍。均未修复，待处理。
