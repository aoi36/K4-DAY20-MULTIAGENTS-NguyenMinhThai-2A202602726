# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| | | |

- Nhà cung cấp và mô hình: ban đầu `google_genai:gemini-2.5-flash` (hết hạn mức), sau đó `google_genai:gemini-3.5-flash-lite`; nhiệt độ cấu hình 0 (model mới bỏ qua nhiệt độ), `recursion_limit` mặc định 60 (thử lại `code-learn` với 120).
- Deep Agents 0.7.21 (theo `pyproject.toml`), Windows, chạy trực tiếp trong `.venv`.
- Đã chạy nhiều lượt học `baseline`, `subagents`, `skills-auto`; một số lượt 429 theo hạn mức 15 yêu cầu/phút của model mới. Ba kết quả `baseline` và `subagents` cuối không có lỗi. `baseline` và `subagents` học dùng `gemini-3.5-flash-lite` sau các lần thử đầu; `skills-auto` Phần 3.4 chưa đủ ba lượt.
- Commit của tag `freeze`: `74716c5` (giả thuyết commit trước đó: `2c698a3`).

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Dự đoán không tăng điểm trung bình tác vụ đánh giá: cả ba tác vụ học đạt bằng điểm baseline (6/10, 5/8, 6/9) dù `subagents` tốn nhiều token hơn (275.313/536.682/185.493 so với 158.468/278.079/78.520).
- H2 (skills-auto so với baseline): Dự đoán không tăng điểm đánh giá rõ rệt: Phần 3.4 trên tác vụ học đạt 6/10, 5/8, 6/9 (bằng baseline); `code-learn` không đọc skill (`skills_read=0`), `data-learn` đọc 2, `logs-learn` đọc 1 mà không tăng điểm.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm đánh giá thấp hơn điểm học vì có thêm quy ước mới chưa xuất hiện trong phản hồi học; bản giả thuyết này đã được commit trước tag `freeze`.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Theo thiết kế của lab, có 1 tác tử chính (coordinator) nhận yêu cầu, điều phối và kiểm tra kết quả; Deep Agents cung cấp sẵn 1 subagent `general-purpose` xử lý việc được giao. Chế độ `subagents` dự kiến bổ sung 2–3 subagent chuyên trách, ví dụ `explorer` đọc và báo cáo, `implementer` sửa mã và chạy kiểm tra, `reviewer` rà soát độc lập. `get_subagents()` và `build_agent()` đã được cài đặt; số lần subagent thực sự được gọi cần xác nhận từ `run.json` của điều kiện `subagents`.
2. Coordinator giao việc qua công cụ `task`, gửi mô tả kèm quy tắc và đường dẫn cần thiết; mỗi lần gọi tạo ngữ cảnh subagent riêng. Subagent dùng công cụ để thực hiện và trả về một báo cáo cuối; coordinator kiểm tra báo cáo trước khi sử dụng hoặc giao tiếp việc.
3. Các agent dùng chung khả năng của backend truy cập sandbox: công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` và công cụ shell `execute`. Subagent tự định nghĩa không tự thừa kế skill của tác tử chính; cần cấu hình `skills` riêng nếu muốn chia sẻ. Không có logging, monitoring hay knowledge base dùng chung được định nghĩa trong phần này.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | G | Bot báo các test gốc đã bị sửa; cần giữ nguyên các tệp test ban đầu. |
| `code-learn` | `rule_type_hints` | E | `RULE: every public function ... has type annotations`. |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py ... at least 3`. |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md ...`. |
| `data-learn` | `rule_money_in_cents` | E | `RULE: money values in answer.json are integer cents`. |
| `data-learn` | `rule_meta_block` | E | `RULE: answer.json has an object meta` ghi nguồn và số hàng. |
| `data-learn` | `rule_clean_csv` | E | `RULE: write workspace/clean.csv ... amount in integer cents`. |
| `logs-learn` | `rule_service_names` | E | `RULE: service names ... lower-case with '-' replaced by '_'`. |
| `logs-learn` | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then timestamp_utc`. |
| `logs-learn` | `rule_schema_header` | E | `RULE: ... schema_version: 2 and generated_by: log-triage`. |

Nhận xét: `baseline` hiện đạt `code-learn` 6/10, `data-learn` 5/8, `logs-learn` 6/9, không lỗi API. 9 trong 10 check trượt thuộc nhóm E (quy ước tổ chức); skill quy trình có thể giúp tác tử chú ý các yêu cầu này, nhưng chưa có bằng chứng hiệu quả trên tác vụ đánh giá.

## 5. Điều kiện `subagents` (Phần 2.3)

- Đã định nghĩa `explorer` (đọc đặc tả), `implementer` (sửa và kiểm tra), `reviewer` (rà soát độc lập).
- `subagent_calls`: `code-learn` 1 (`implementer`), `data-learn` 3 (`general-purpose`/`implementer`), `logs-learn` 1 (`implementer`); đều đạt cùng điểm baseline tương ứng 6/10, 5/8, 6/9.
- Thông tin giao việc: `data-learn` gửi yêu cầu đọc README, xử lý trùng lặp/ngày/múi giờ và kiểm tra kết quả; `logs-learn` nêu lại cấu trúc JSON nhưng không có các quy ước ẩn, nên vẫn trượt ba `rule_`. Vết chỉ hiện luồng chính, không hiện bước nội bộ subagent.
- Ảnh hưởng token/thời gian (`subagents` so với `baseline`): `code-learn` 275.313/114,2 giây so với 158.468/53,5 giây; `data-learn` 536.682/211,1 giây so với 278.079/71 giây; `logs-learn` 185.493/84,8 giây so với 78.520/16,9 giây. Không cải thiện điểm, tăng chi phí.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Chạy curator 1 lần trên phản hồi `baseline` học; sinh 2 skill, chưa xóa skill nào. Lúc curator chạy, `code-learn` là lượt lỗi 429 và `data-learn`/`logs-learn` dùng model khác; đây là nguy cơ nhiễu. Phần 3.4 đã chạy đủ và lưu tại `results/skills-auto-dev/`: `code-learn` 6/10, `skills_read=0`; `data-learn` 5/8, đọc 2; `logs-learn` 6/9, đọc 1. Lượt `data-learn` đầu bị dừng, lần kế tiếp lỗi giới hạn đệ quy 40 và được chạy lại thành công với 80; các bản ghi lỗi không được dùng để phân tích. Chưa thấy cải thiện điểm.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `python-type-annotations-and-regression-tests` | Quy tắc chung cho bảo trì gói Python | Khớp check về annotation, test hồi quy và changelog; cần đối chiếu với yêu cầu từng dự án | 8 dòng, mô tả nêu thời điểm áp dụng; `code-learn` đọc 0 skill, không áp dụng. |
| `json-data-cleaning-and-normalization` | Quy trình chung cho dữ liệu thô/JSON/CSV | Phần lớn khớp phản hồi, nhưng 'cast to integers' có thể làm mất độ chính xác tiền tệ: nên dùng Decimal và làm tròn đúng; **không áp dụng chỉ dẫn đó** khi xử lý tiền | 8 dòng, mô tả nêu thời điểm áp dụng; `data-learn` đọc 2 skill, `logs-learn` đọc 1 nhưng điểm không đổi. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
Tạm thời (chưa có kết quả đánh giá subagents hoặc skills-auto):
| Task | baseline | subagents |
|---|---|---|
| code-learn | 6/10 | 6/10 |
| data-learn | 5/8 | 5/8 |
| logs-learn | 6/9 | 6/9 |
| code-eval | 6/11 | - |
| data-eval | 5/9 | - |
| logs-eval | 6/10 | - |
| Mean score - learning tasks | 0.63 | 0.63 |
| Mean score - evaluation tasks | 0.57 | - |
| Mean tokens per run | 153,992 | 332,496 |

check_breakdown.py: baseline learn technical 17/18, rule 0/9; baseline eval technical 17/18, rule 0/12; subagents learn technical 17/18, rule 0/9.
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. Trên tác vụ học, `subagents` và `skills-auto-dev` cùng đạt 6/10, 5/8, 6/9 như `baseline`; chưa có đủ điểm đánh giá hai điều kiện còn lại để kết luận về chuyển giao.
2. `baseline` đạt check kỹ thuật 17/18 trên cả học và đánh giá, check quy ước 0/9 và 0/12; `subagents` học cũng 17/18 và 0/9. Trong thử nghiệm trước đóng băng, skill chưa cải thiện điểm tổng; check quy ước mới của đánh giá không xuất hiện trong prompt curator nên không thể giả định skill giúp được.
3. `code-learn` `skills_read=0`: ba check `rule_` trượt; `logs-learn` đọc một skill mà vẫn trượt `rule_service_names`, `rule_sorted_errors`, `rule_schema_header`. Chưa có ví dụ check quy ước *được skill giúp đạt* trong dữ liệu hiện có.
4. Token trung bình `baseline` 153.992/lượt (6 lượt), `subagents` 332.496/lượt (3 lượt học), trong khi điểm học trung bình đều 0,63; trên tập học, `baseline` tiết kiệm hơn. Chưa có token `skills-auto` sau đóng băng để xếp hạng đầy đủ.
5. Hai skill qua `validate_skill` (không chứa định danh chỉ có ở đánh giá); tuy nhiên skill dữ liệu có ví dụ số tiền và cách 'cast to integers' thiếu an toàn về độ chính xác. Chưa có bằng chứng rò rỉ định danh; rủi ro quá khớp quy ước học vẫn còn.
6. Bản sao `results/skills-auto-dev/` ghi 6/10, 5/8, 6/9; chưa chạy lại sau đóng băng vì quota, nên chưa đo được chênh lệch nhiễu. Không gán khác biệt chưa đo thành tác dụng của skill.

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1. Chỉ ba tác vụ mỗi vai trò: chênh lệch một check có thể làm thay đổi đáng kể điểm trung bình, khó suy rộng.
2. Mỗi điều kiện/tác vụ chỉ có một lượt hợp lệ: nhiễu mô hình và giới hạn gọi API ảnh hưởng kết luận; cần lặp nhiều lần khi quota phục hồi.
3. Dùng một nhà cung cấp và thay model giữa thử nghiệm ban đầu và lượt hợp lệ: kết luận chỉ áp dụng cho cấu hình sau cùng; không gộp số liệu model cũ.
4. Quy ước chấm do lab thiết kế và không có trong instruction: check `rule_` đo khả năng suy từ phản hồi và skill hơn là làm đúng chỉ dẫn công khai.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

Hai cấu hình `baseline` và `subagents` cùng đạt 0,63 trung bình trên tác vụ học, nhưng `subagents` tốn nhiều hơn gấp đôi token. Skill do curator sinh hợp lệ về cấu trúc, song chưa cải thiện điểm ở lần kiểm tra trước đóng băng. Vì quota 429 cản trở các lượt đánh giá còn lại, chưa thể kết luận về hiệu quả trên tác vụ mới. Bước tiếp theo là chạy lại các lượt còn thiếu trên cùng model sau khi quota phục hồi, rồi kiểm tra freeze và so sánh với số liệu học đã sao lưu.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác: Đã hoàn thành các lượt học Phần 3.4 và lưu `results/skills-auto-dev/`; đã commit giả thuyết và tag `freeze`. Ba lượt đánh giá `baseline` hợp lệ, nhưng `subagents/code-eval` và `data-eval` bị 429 do hết 500 yêu cầu/ngày; đã bỏ hai bản ghi lỗi và dừng trước `logs-eval`. Chưa chạy `skills-auto` chính thức và chưa thể hoàn thành bảng 3 điều kiện; cần chờ quota hồi phục, chạy lại `subagents --tasks eval`, rồi `skills-auto --tasks all`, kiểm tra `verify_freeze.py`, lập bảng và hoàn tất phân tích.
