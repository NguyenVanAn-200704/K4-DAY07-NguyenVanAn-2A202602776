# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G04
**Thành viên:** Nguyễn Văn An, Trương Thị Lan Anh, Lưu Xuân Dũng, Tạ Quang Dũng, Nguyễn Duy Khánh, Nguyễn Long Khánh
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định học bổng ở Đại Học

**Tại sao nhóm chọn chủ đề này?**

> Học bổng đại học là thông tin được nhiều sinh viên và phụ huynh tìm kiếm thường xuyên nhưng lại phân tán trên nhiều nguồn khác nhau (website trường, văn bản pháp quy, báo chí). Chủ đề này phù hợp lý tưởng để kiểm thử RAG vì có cấu trúc rõ ràng (điều khoản, mức tiền, điều kiện xét), đa dạng đối tượng (sinh viên giỏi, sinh viên khó khăn, sinh viên quốc tế), và câu hỏi có thể kiểm chứng được từ văn bản gốc.

### Danh sách tài liệu (Data Inventory)

| #   | Tên tài liệu                                                  | Nguồn (Source URL)                                                                                                       | Ngày lấy / Phiên bản    | Số ký tự | Metadata đã gán                                                                    |
| --- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------- | -------- | ---------------------------------------------------------------------------------- |
| 1   | Mức học bổng học sinh sinh viên mới nhất (LuatVietnam)        | https://luatvietnam.vn/tin-phap-luat/hoc-bong-sinh-vien-hoc-sinh-230-28958-article.html                                  | 2026-09-19 / not-stated | 12.453   | audience=student, department=government, category=scholarship-amount               |
| 2   | Tổng quan học bổng RMIT Việt Nam                              | https://www.rmit.edu.vn/vi/hoc-tap-tai-rmit/hoc-bong                                                                     | 2026-09-19 / not-stated | 4.412    | audience=applicant, department=scholarships-office, category=scholarship-overview  |
| 3   | Kết quả học bổng RMIT VN 2024                                 | https://www.rmit.edu.vn/vi/tin-tuc/tat-ca-tin-tuc/2024/oct/rmit-viet-nam-ton-vinh-tac-dong                               | 2026-09-19 / 2024-10    | 8.103    | audience=student, department=scholarships-office, category=scholarship-results     |
| 4   | Học bổng đại học RMIT cho sinh viên tương lai 2026            | https://www.rmit.edu.vn/vi/hoc-tap-tai-rmit/hoc-bong/hoc-bong-dai-hoc-cho-sinh-vien-tuong-lai                            | 2026-09-19 / 2026       | 11.047   | audience=applicant, department=scholarships-office, category=scholarship-admission |
| 5   | ĐH Đà Nẵng vinh danh thủ khoa và trao học bổng Nâng bước 2025 | https://daibieunhandan.vn/dai-hoc-da-nang-vinh-danh-thu-khoa-va-trao-hoc-bong-nang-buoc-sinh-vien-nam-2025-10393397.html | 2026-09-19 / 2025       | 8.514    | audience=student, department=student-affairs, category=scholarship-announcement    |
| 6   | Tuyển sinh học bổng sớm 3 trường ĐH 2025 (Tuổi Trẻ)           | https://tuoitre.vn/3-truong-dai-hoc-bat-dau-nhan-ho-so-xet-tuyen-nam-2025-20250116100857543.htm                          | 2026-09-19 / 2025-01-16 | ~15.000  | audience=applicant, department=admissions, category=early-admission                |
| 7   | UEH mở rộng học bổng trao đổi quốc tế 2026–2027               | https://tuoitre.vn/dai-hoc-kinh-te-tphcm-mo-rong-hoc-bong-tang-co-hoi-xuat-ngoai-cho-sinh-vien-20260320191254681.htm     | 2026-09-19 / 2026-03-20 | ~16.000  | audience=student, department=international-office, category=exchange-scholarship   |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata    | Kiểu              | Ví dụ giá trị                                | Tại sao hữu ích cho truy xuất (retrieval)?                      |
| ------------------ | ----------------- | -------------------------------------------- | --------------------------------------------------------------- |
| `source_url`       | string            | `https://rmit.edu.vn/...`                    | Truy vết nguồn gốc câu trả lời; kiểm tra tính mới của thông tin |
| `retrieved_at`     | string (ISO date) | `2026-09-19`                                 | Kiểm tra độ mới dữ liệu; loại bỏ thông tin hết hạn              |
| `document_version` | string            | `2026`, `2025-01-16`                         | Lọc theo năm học / đợt xét học bổng                             |
| `audience`         | string            | `student`, `applicant`                       | Lọc chunk phù hợp đối tượng (sv hiện tại vs sv tương lai)       |
| `department`       | string            | `scholarships-office`, `government`          | Lọc theo cơ quan ban hành (trường vs pháp quy)                  |
| `category`         | string            | `scholarship-amount`, `scholarship-overview` | Lọc theo loại thông tin cần (mức tiền, điều kiện, kết quả)      |
| `doc_id`           | string            | `rmit-vn-undergrad-scholarships-2026`        | Xóa/cập nhật tài liệu theo `delete_document(doc_id)`            |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu (chunk_size=200):

| Tài liệu                                      | Chiến lược (Strategy)            | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không?                          |
| --------------------------------------------- | -------------------------------- | -------------- | ----------------- | ------------------------------------------------- |
| rmit-vn-scholarship-overview (4.412 ký tự)    | FixedSizeChunker (`fixed_size`)  | 30             | 195.4             | Không — cắt ngang giữa điều khoản                 |
| rmit-vn-scholarship-overview (4.412 ký tự)    | SentenceChunker (`by_sentences`) | 6              | 730.8             | Có — giữ trọn câu, nhưng chunk quá lớn            |
| rmit-vn-scholarship-overview (4.412 ký tự)    | RecursiveChunker (`recursive`)   | 26             | 167.8             | Có — tôn trọng ranh giới đoạn                     |
| luatvietnam-scholarship-levels (12.453 ký tự) | FixedSizeChunker (`fixed_size`)  | 83             | 199.4             | Không — cắt ngang điều khoản pháp luật            |
| luatvietnam-scholarship-levels (12.453 ký tự) | SentenceChunker (`by_sentences`) | 15             | 821.1             | Có — nhưng mỗi chunk chứa nhiều điều khoản        |
| luatvietnam-scholarship-levels (12.453 ký tự) | RecursiveChunker (`recursive`)   | 77             | 157.9             | Có — tách theo `\n\n` trước, tôn trọng điều khoản |
| udn-nang-buoc-scholarship-2025 (8.514 ký tự)  | FixedSizeChunker (`fixed_size`)  | 57             | 198.5             | Không — cắt ngang nội dung bài báo                |
| udn-nang-buoc-scholarship-2025 (8.514 ký tự)  | SentenceChunker (`by_sentences`) | 10             | 835.2             | Có — giữ đoạn văn hoàn chỉnh                      |
| udn-nang-buoc-scholarship-2025 (8.514 ký tự)  | RecursiveChunker (`recursive`)   | 42             | 157.9             | Có — tốt với cấu trúc bài báo                     |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Văn An**

- **Loại chiến lược:** RecursiveChunker (custom tuned)
- **Mô tả & lý do chọn cho chủ đề này:** Tài liệu học bổng có cấu trúc phân cấp rõ (section → paragraph → sentence), RecursiveChunker với `chunk_size=300` ưu tiên tách theo `\n\n` (ranh giới điều khoản) trước khi xuống `\n` (dòng), tránh cắt đứt giữa điều kiện xét học bổng. Phù hợp với tài liệu pháp quy và website trường.
- **Code snippet:**

```python
chunker = RecursiveChunker(
    separators=["\n\n", "\n", ". ", " ", ""],
    chunk_size=300
)
```

**Thành viên 2 — Trương Thị Lan Anh**

- **Loại chiến lược:** SentenceChunker (max_sentences=2)
- **Mô tả & lý do chọn:** Tài liệu pháp quy học bổng (Nghị định, thông tư) thường có mỗi câu là một điều khoản độc lập. Chunking theo 2 câu/chunk giúp mỗi chunk chứa một quy định cụ thể, dễ truy xuất chính xác khi hỏi về điều kiện cụ thể.
- **Code snippet:**

```python
chunker = SentenceChunker(max_sentences_per_chunk=2)
```

**Thành viên 3 — Lưu Xuân Dũng**

- **Loại chiến lược:** FixedSizeChunker với overlap lớn
- **Mô tả & lý do chọn:** Dùng `chunk_size=400, overlap=100` để đảm bảo chunk nào cũng chứa đủ ngữ cảnh; overlap lớn giúp thông tin ở ranh giới chunk không bị mất trong quá trình truy xuất.
- **Code snippet:**

```python
chunker = FixedSizeChunker(chunk_size=400, overlap=100)
```

**Thành viên 4 — Tạ Quang Dũng**

- **Loại chiến lược:** Custom — QAChunker (tách theo cặp Câu hỏi–Điều kiện)
- **Mô tả & lý do chọn:** Tài liệu học bổng thường có dạng FAQ: "Điều kiện nhận học bổng X là gì? → Trả lời cụ thể." Tách theo pattern `Điều kiện|Yêu cầu|Mức học bổng|Đối tượng` giúp mỗi chunk là một cặp chính sách-giải thích hoàn chỉnh.
- **Code snippet:**

```python
class QAChunker:
    """Tách tài liệu học bổng theo các tiêu đề điều khoản."""
    SECTION_PATTERN = r'(?=^(Điều kiện|Yêu cầu|Mức học bổng|Đối tượng|Nguyên tắc))'

    def chunk(self, text: str) -> list[str]:
        import re
        parts = re.split(self.SECTION_PATTERN, text, flags=re.MULTILINE)
        return [p.strip() for p in parts if p and p.strip()]
```

**Thành viên 5 — Nguyễn Duy Khánh**

- **Loại chiến lược:** RecursiveChunker với separators mở rộng cho tài liệu pháp quy
- **Mô tả & lý do chọn:** Bổ sung separator `";\n"` và `"•"` vào danh sách để tách đúng với định dạng bullet và điều khoản liệt kê trong Nghị định, giúp mỗi chunk là một điều khoản pháp quy hoàn chỉnh.
- **Code snippet:**

```python
chunker = RecursiveChunker(
    separators=["\n\n", ";\n", "\n", "• ", ". ", " ", ""],
    chunk_size=250
)
```

**Thành viên 6 — Nguyễn Long Khánh**

- **Loại chiến lược:** SentenceChunker (max_sentences=3)
- **Mô tả & lý do chọn:** Với tài liệu tin tức học bổng (Tuổi Trẻ, Đại biểu Nhân dân), các đoạn tin thường 3-5 câu mô tả một sự kiện/thông báo hoàn chỉnh. Chunking 3 câu/chunk phù hợp với cấu trúc bài báo về học bổng.
- **Code snippet:**

```python
chunker = SentenceChunker(max_sentences_per_chunk=3)
```

### So Sánh Giữa Các Thành Viên

| Thành viên         | Chiến lược (Strategy)                 | Điểm truy xuất (/10) | Điểm mạnh                                        | Điểm yếu                                |
| ------------------ | ------------------------------------- | -------------------- | ------------------------------------------------ | --------------------------------------- |
| Nguyễn Văn An      | RecursiveChunker (chunk_size=300)     | 8/10                 | Tôn trọng cấu trúc điều khoản, chunk size hợp lý | Chunk quá nhỏ với tài liệu bài báo      |
| Trương Thị Lan Anh | SentenceChunker (2 câu)               | 7/10                 | Mỗi chunk là điều khoản rõ ràng                  | Chunk quá nhỏ, thiếu ngữ cảnh liên câu  |
| Lưu Xuân Dũng      | FixedSizeChunker (overlap=100)        | 6/10                 | Đảm bảo độ phủ context                           | Cắt ngang câu, nhiều chunk trùng lặp    |
| Tạ Quang Dũng      | QAChunker (custom)                    | 9/10                 | Chunk bám sát cấu trúc nội dung học bổng         | Cần regex tuning cho từng loại tài liệu |
| Nguyễn Duy Khánh   | RecursiveChunker (separators mở rộng) | 8/10                 | Xử lý tốt tài liệu pháp quy bullet               | Phức tạp, có thể over-split             |
| Nguyễn Long Khánh  | SentenceChunker (3 câu)               | 7/10                 | Phù hợp bài báo tin tức học bổng                 | Chunk quá lớn với tài liệu điều khoản   |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> Chiến lược QAChunker (tùy chỉnh) của thành viên Tạ Quang Dũng cho kết quả tốt nhất (9/10) vì nó tách đúng theo ranh giới ngữ nghĩa của tài liệu học bổng — mỗi điều khoản "Điều kiện", "Mức học bổng", "Đối tượng" là một đơn vị thông tin hoàn chỉnh. RecursiveChunker cũng hiệu quả (8/10) vì tôn trọng cấu trúc phân cấp của văn bản, nhưng không nhận biết được ngữ nghĩa của các section tiêu đề. Cả hai đều vượt trội FixedSizeChunker — vốn cắt ngang điều khoản pháp quy và làm mất ngữ cảnh quan trọng.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| #   | Câu hỏi (Query)                                                                                                                                      | Câu trả lời chuẩn (Gold Answer)                                                                                                                                               | Chunk nào chứa thông tin?                                                                                                          |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 1   | RMIT Việt Nam đã trao tổng giá trị học bổng bao nhiêu và cho bao nhiêu sinh viên?                                                                    | Hơn 613 tỉ đồng cho hơn 1.900 sinh viên ở khắp Việt Nam và trên toàn thế giới                                                                                                 | `rmit-vn-scholarship-overview` — đoạn "trường đã trao các học bổng với tổng giá trị hơn 613 tỉ đồng"                               |
| 2   | Điều kiện nhận học bổng khuyến khích học tập tại cơ sở giáo dục đại học là gì?                                                                       | Kết quả học tập, rèn luyện từ loại Khá trở lên, không bị kỷ luật từ mức khiển trách trở lên trong kỳ xét                                                                      | `luatvietnam-scholarship-levels` — điều khoản "người học đang học trong cơ sở giáo dục nghề nghiệp, cơ sở giáo dục đại học"        |
| 3   | Mức học bổng loại Giỏi và loại Xuất sắc khác nhau thế nào?                                                                                           | Loại Giỏi: cao hơn loại Khá, do hiệu trưởng quy định, yêu cầu ĐTBCHTB loại Giỏi và rèn luyện loại Tốt. Loại Xuất sắc: cao hơn Giỏi, yêu cầu ĐTBCHTB và rèn luyện đều Xuất sắc | `luatvietnam-scholarship-levels` — điều khoản phân loại học bổng Khá/Giỏi/Xuất sắc                                                 |
| 4   | Học bổng Chắp Cánh Ước Mơ của RMIT dành cho đối tượng nào? (Cần lọc metadata `category=scholarship-admission` hoặc `department=scholarships-office`) | Dành cho sinh viên khuyết tật và/hoặc có hoàn cảnh khó khăn không có điều kiện theo học chương trình đại học                                                                  | `rmit-vn-undergrad-scholarships-2026` — mục "Học bổng Chắp cánh ước mơ"                                                            |
| 5   | Đại học Đà Nẵng trao học bổng Nâng bước sinh viên 2025 với giá trị bao nhiêu và bao nhiêu sinh viên?                                                 | 60 sinh viên có hoàn cảnh khó khăn, mỗi suất 5 triệu đồng; tổng giá trị khen thưởng và học bổng gần 740 triệu đồng                                                            | `udn-nang-buoc-scholarship-2025` — đoạn "60 sinh viên có hoàn cảnh khó khăn nhận Học bổng Nâng bước sinh viên (5 triệu đồng/suất)" |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| #   | Câu hỏi                                            | Chiến lược tốt nhất cho câu này                                     | Có chunk liên quan trong top-3? | Ghi chú                                                |
| --- | -------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------- | ------------------------------------------------------ |
| 1   | RMIT trao tổng giá trị học bổng bao nhiêu?         | RecursiveChunker / QAChunker                                        | ✅ Có (top-1)                   | Đoạn ngắn, dễ match bất kỳ chiến lược                  |
| 2   | Điều kiện học bổng khuyến khích học tập?           | RecursiveChunker (separators mở rộng)                               | ✅ Có (top-2)                   | Cần chunk tách đúng điều khoản, FixedSize thường bỏ lỡ |
| 3   | Khác nhau giữa học bổng Giỏi và Xuất sắc?          | QAChunker / SentenceChunker (2 câu)                                 | ✅ Có (top-3)                   | Hai điều khoản liền kề, cần chunk đủ lớn hoặc overlap  |
| 4   | Học bổng Chắp Cánh Ước Mơ dành cho ai? (filter)    | RecursiveChunker + metadata filter `category=scholarship-admission` | ✅ Có (top-1)                   | Metadata filtering lọc đúng tài liệu RMIT undergrad    |
| 5   | ĐH Đà Nẵng trao bao nhiêu suất học bổng Nâng bước? | SentenceChunker (3 câu) / RecursiveChunker                          | ✅ Có (top-1)                   | Thông tin nằm trong một đoạn văn bản liên tục          |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Metadata filtering giúp ích rõ rệt nhất ở Câu hỏi 4: khi hỏi về "Học bổng Chắp Cánh Ước Mơ" mà không lọc, store có thể trả về chunk từ tài liệu ĐH Đà Nẵng hoặc LuatVietnam (cũng nhắc đến sinh viên khó khăn) thay vì tài liệu RMIT undergrad. Bằng cách thêm filter `{"category": "scholarship-admission", "department": "scholarships-office"}`, kết quả top-1 chính xác 100%.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

> - **Insight 1:** MockEmbedder (hash-based) không phân biệt được câu đồng nghĩa trong tiếng Việt — cần real multilingual embedding model để RAG học bổng hoạt động thực tế; demo so sánh trực tiếp score của MockEmbedder vs. MiniLM trên cùng 5 cặp câu.
> - **Insight 2:** Tài liệu học bổng có hai loại cấu trúc hoàn toàn khác nhau: (a) văn bản pháp quy (điều khoản bullet, cần RecursiveChunker/QAChunker), (b) bài báo tin tức (đoạn văn liên tục, SentenceChunker hiệu quả hơn) — không có chiến lược "one-size-fits-all".
> - **Insight 3:** Metadata filtering là công cụ mạnh khi hỏi về học bổng theo đối tượng (sinh viên tương lai vs. sinh viên hiện tại) — lọc `audience=applicant` loại bỏ ~60% chunk không liên quan và tăng precision top-3 đáng kể.

**Bài học rút ra khi so sánh trong nhóm:**

> Cùng bộ tài liệu học bổng nhưng các chiến lược chunking cho kết quả truy xuất rất khác nhau: QAChunker tùy chỉnh đạt 9/10 trong khi FixedSizeChunker chỉ đạt 6/10, cho thấy việc thiết kế chunker phù hợp với cấu trúc nội dung quan trọng hơn là tối ưu tham số. SentenceChunker với 2 câu/chunk tốt cho tài liệu pháp quy (điều khoản ngắn) nhưng lại tệ với bài báo tin tức, chứng minh không có chiến lược nào tối ưu cho tất cả loại tài liệu.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> Nhóm sẽ phân loại tài liệu thành hai pipeline chunking riêng biệt ngay từ bước ingest: (1) tài liệu pháp quy/quy định → QAChunker hoặc RecursiveChunker với separators tùy chỉnh; (2) tài liệu tin tức/thông báo → SentenceChunker. Ngoài ra sẽ bổ sung metadata `document_type: regulation|news|website` để routing tự động chiến lược chunking và lọc kết quả truy xuất chính xác hơn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                 | Điểm tự đánh giá |
| ---------------------------------------- | ---------------- |
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10          |
| Thiết kế chiến lược (Strategy Design)    | 14 / 15          |
| Chất lượng truy xuất (Retrieval Quality) | 9 / 10           |
| Thuyết trình (Demo)                      | 4 / 5            |
| **Tổng phần nhóm**                       | **37 / 40**      |
