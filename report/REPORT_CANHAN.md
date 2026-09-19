# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Văn An - 2A202602776
**Nhóm:** G04
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> Độ tương tự cosine cao (tiến gần về 1.0) thể hiện hai vector embedding chỉ về cùng một hướng trong không gian vector đa chiều, đồng nghĩa với việc hai đoạn văn bản có sự tương đồng rất lớn về ngữ nghĩa và chủ đề, không phụ thuộc vào độ dài câu.

**Ví dụ có độ tương tự CAO:**

- Câu A: Machine learning là một nhánh quan trọng của trí tuệ nhân tạo.
- Câu B: Học máy là một phân ngành cốt lõi thuộc lĩnh vực AI.
- Tại sao tương đồng: Cả hai câu sử dụng các từ đồng nghĩa và diễn đạt cùng một định nghĩa ngữ nghĩa về machine learning và AI.

**Ví dụ có độ tương tự THẤP:**

- Câu A: Thuật toán tìm kiếm theo chiều sâu duyệt qua toàn bộ cây đồ thị.
- Câu B: Hôm nay thời tiết Hà Nội rất đẹp và trời nhiều mây.
- Tại sao khác: Hai câu thuộc hai ngữ cảnh hoàn toàn không liên quan (khoa học máy tính vs thời tiết đời sống), các từ vựng và vector ngữ nghĩa phân bố ở các hướng khác nhau trong không gian vector.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> Khoảng cách Euclid phụ thuộc trực tiếp vào độ lớn (magnitude) của vector, vốn dễ bị thay đổi do độ dài văn bản khác nhau. Cosine similarity chuẩn hóa độ dài vector và chỉ đo góc định hướng giữa hai vector, do đó phản ánh chính xác sự tương đồng về ngữ nghĩa độc lập với độ dài văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> _Trình bày phép tính:_ `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.111...) = 23`
> _Đáp án:_ 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> Khi overlap tăng lên 100, số lượng chunk sẽ là `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25` chunks (tăng 2 chunks). Cần tăng độ chồng chéo để duy trì tính liên tục và bảo toàn ngữ cảnh ở ranh giới giữa các chunk, tránh hiện tượng thông tin hoặc câu văn quan trọng bị cắt đôi làm suy giảm chất lượng truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> Sử dụng regex lookbehind `r'(?<=[.!?])\s+|\.\n'` để phân tách ranh giới câu mà không làm mất dấu kết thúc câu, sau đó gom `max_sentences_per_chunk` câu vào từng chunk và strip khoảng trắng. Đã nhận diện edge case: các từ viết tắt (`TS.`, `v.v.`) hoặc số thập phân (`3.14`) có thể bị cắt nhầm ranh giới câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> Thuật toán kết hợp hai chiều: đệ quy xuống sâu theo danh sách separator ưu tiên `["\n\n", "\n", ". ", " ", ""]` khi đoạn văn bản vượt quá `chunk_size`, và gom các đoạn nhỏ liền kề lại cho tới sát `chunk_size` để tránh phân mảnh chunk vụn. Base cases xử lý dừng khi văn bản rỗng, văn bản `<= chunk_size`, hoặc khi hết separator thì fallback cắt theo ký tự.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> Lưu trữ in-memory danh sách bản ghi gồm `id`, `content`, `metadata` (chuẩn hóa luôn có `doc_id`), và `embedding`. Khi tìm kiếm, tính tích vô hướng (dot product) giữa query embedding và các stored embeddings (tương đương cosine do vector đã chuẩn hóa), sắp xếp giảm dần và lấy top-k, đồng thời loại bỏ trường embedding ở kết quả trả về.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> Tiền lọc (pre-filter) các bản ghi theo `metadata_filter` trước rồi mới thực hiện similarity search để tránh làm mất các ứng viên hợp lệ trong top-k. Xóa bằng cách lọc bỏ toàn bộ các chunk có `metadata['doc_id'] == doc_id` hoặc `id == doc_id`, trả về `True` nếu số lượng phần tử giảm đi.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> Truy xuất top-k chunk từ store, kiểm tra an toàn nếu store rỗng thì phản hồi ngay. Dựng prompt RAG có cấu trúc đánh số `[1]`, `[2]` kèm nguồn (source) để đảm bảo khả năng truy vết (traceability), yêu cầu LLM chỉ trả lời dựa trên ngữ cảnh được cung cấp trước khi gọi `llm_fn`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> Sử dụng `MockEmbedder` (64-d hash-based deterministic embeddings) để tính `compute_similarity()` trên 5 cặp câu liên quan đến chủ đề học bổng.

| Cặp | Câu A                                          | Câu B                                              | Dự đoán | Điểm thực tế | Đúng? |
| --- | ---------------------------------------------- | -------------------------------------------------- | ------- | ------------ | ----- |
| 1   | Học bổng toàn phần dành cho sinh viên xuất sắc | Học bổng 100% học phí cho sinh viên giỏi           | cao     | 0.0248       | ❌    |
| 2   | Điều kiện xét học bổng: GPA từ 3.2/4.0         | Tiêu chí được học bổng: điểm trung bình 8.0/10     | cao     | -0.0182      | ❌    |
| 3   | Sinh viên có hoàn cảnh khó khăn được hỗ trợ    | Học bổng khuyến khích học tập cho sinh viên giỏi   | thấp    | 0.0214       | ✅    |
| 4   | Học bổng RMIT Việt Nam năm 2026                | Thời tiết Hà Nội hôm nay có mưa                    | thấp    | -0.1866      | ✅    |
| 5   | Hạn nộp hồ sơ học bổng là ngày 31/03/2026      | Hạn chót nộp đơn xin học bổng: 31 tháng 3 năm 2026 | cao     | -0.0463      | ❌    |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Bất ngờ nhất là Cặp 5: hai câu có nghĩa hoàn toàn đồng nhất (chỉ khác cách diễn đạt ngày tháng) nhưng MockEmbedder cho điểm âm (-0.0463), còn Cặp 1 (đồng nghĩa gần) cũng chỉ đạt 0.0248 rất thấp. Điều này cho thấy MockEmbedder là hash-based (dùng MD5) không hiểu ngữ nghĩa, nên không phân biệt được câu đồng nghĩa và câu không liên quan — đây là lý do trong RAG thực tế về học bổng tiếng Việt phải dùng real embedding model như `paraphrase-multilingual-MiniLM-L12-v2`.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

> Chiến lược cá nhân: **RecursiveChunker** (`chunk_size=300`, separators mặc định `["\n\n", "\n", ". ", " ", ""]`). Lý do: tài liệu học bổng có cấu trúc phân đoạn rõ (tiêu đề mục, điều khoản, bullet), RecursiveChunker tôn trọng ranh giới đoạn văn và điều khoản — tránh cắt đứt giữa điều kiện xét học bổng.

| #   | Câu hỏi (Query)                                          | Top-1 Chunk truy xuất được (tóm tắt)                                                                                         | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt)                                                     |
| --- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------ | ----------------------------------------------------------------------------------- |
| 1   | RMIT trao học bổng tổng giá trị bao nhiêu?               | "trường đã trao các học bổng với tổng giá trị hơn 613 tỉ đồng cho hơn 1.900 bạn trẻ"                                         | 0.18       | ✅ Có                          | RMIT VN đã trao hơn 613 tỉ đồng cho hơn 1.900 sinh viên trên toàn Việt Nam          |
| 2   | Điều kiện nhận học bổng khuyến khích học tập là gì?      | "kết quả học tập, rèn luyện từ loại Khá trở lên, không bị kỷ luật từ mức khiển trách trở lên"                                | 0.15       | ✅ Có                          | Sinh viên cần đạt học tập loại Khá trở lên và không bị kỷ luật trong kỳ xét         |
| 3   | Mức học bổng loại Giỏi là bao nhiêu?                     | "Mức học bổng cao hơn loại khá do hiệu trưởng quy định đối với người học có điểm trung bình chung đạt loại Giỏi"             | 0.14       | ✅ Có                          | Mức học bổng loại Giỏi cao hơn loại Khá, do hiệu trưởng quy định cụ thể từng trường |
| 4   | Sinh viên có hoàn cảnh khó khăn được nhận học bổng gì?   | "Học bổng Chắp cánh ước mơ dành cho những sinh viên khuyết tật và/hoặc có hoàn cảnh khó khăn"                                | 0.13       | ✅ Có                          | Học bổng "Chắp cánh ước mơ" (RMIT) và "Nâng bước sinh viên" (ĐH Đà Nẵng)            |
| 5   | Học bổng STEM dành cho nữ sinh RMIT gồm những ngành nào? | "Học bổng STEM dành cho nữ: khuyến khích các bạn sinh viên nữ theo học các ngành thuộc khoa Khoa học, Kỹ thuật và Công nghệ" | 0.12       | ✅ Có                          | Áp dụng cho tất cả ngành thuộc khoa STEM tại RMIT Nam Sài Gòn và Hà Nội             |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Qua demo nhóm, tôi học được rằng chiến lược SentenceChunker tuy tạo ít chunk hơn nhưng mỗi chunk giữ ngữ cảnh hoàn chỉnh hơn theo đơn vị câu — đặc biệt hữu ích với tài liệu quy định pháp lý học bổng, nơi mỗi câu có thể là một điều khoản độc lập. Nhóm khác cũng chỉ ra rằng metadata filtering rất quan trọng khi hỏi về học bổng dành riêng cho đối tượng cụ thể — nếu không lọc theo `audience` hoặc `category`, RAG có thể trả về chunk từ tài liệu sai đối tượng.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                        | Điểm tự đánh giá |
| ----------------------------------------------- | ---------------- |
| Khởi động (Warm-up)                             | 5 / 5            |
| Hướng tiếp cận của tôi (My Approach)            | 10 / 10          |
| Hoàn thiện code (Core Implementation — tests)   | 30 / 30          |
| Dự đoán độ tương tự (Similarity Predictions)    | 5 / 5            |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10          |
| **Tổng phần cá nhân**                           | **60 / 60**      |
