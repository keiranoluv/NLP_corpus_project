# Đề tài số 35

## Danh sách học viên

* 24C11021 – Lê Minh Phục (Nhóm trưởng)
* 24C11035 – Nguyễn Thế Vinh
* 25C15034 – Trần Ngọc Bảo
* 25C15062 – Nguyễn Đăng Thới Toàn

## Ghi chú về dữ liệu đầu ra

### Quy ước đánh số câu

Chỉ số câu trong các file kết quả tách câu và gán nhãn thực thể được đánh số bắt đầu từ `0`.

Ví dụ:

```text
HCH_009_001_000000
HCH_009_001_000001
HCH_009_001_000002
```

### Các quyển không có nội dung ngữ liệu

Một số quyển trong dữ liệu nguồn chỉ chứa tiêu đề, liên kết dự án liên quan, thông tin bản quyền hoặc siêu dữ liệu, không có nội dung sử liệu để thực hiện tách câu và gán nhãn thực thể.

#### HCH_009 – Kim Sử – 金史

Quyển 61 và quyển 62 không có nội dung tác phẩm để xử lý. Nội dung nguồn chỉ gồm:

```text
# 61卷

姊妹计划 : 数据项


# 卷62

姊妹计划 : 数据项
```

Vì vậy, hai quyển sau không có dữ liệu đầu ra cho bước tách câu và NER:

```text
HCH_009_061
HCH_009_062
```

#### HCH_012 – Minh Sử – 明史

Các quyển 101, 102, 110 và 112 không có nội dung sử liệu phù hợp để xử lý. Nội dung nguồn chủ yếu là liên kết dự án liên quan, thông tin bản quyền hoặc siêu dữ liệu.

Ví dụ, quyển 101 có nội dung:

```text
# 卷101

姊妹计划 : 数据项
本清朝作品在全世界都屬於公有領域，因為作者逝世已經超過100年。
Public domain Public domain false false
```

Nội dung trên có thể tạm dịch là:

> Tác phẩm thời nhà Thanh này thuộc phạm vi công cộng trên toàn thế giới vì tác giả đã qua đời hơn 100 năm.

Đây là thông tin bản quyền, không phải nội dung ngữ liệu lịch sử. Vì vậy, các quyển sau không có dữ liệu đầu ra cho bước tách câu và NER:

```text
HCH_012_101
HCH_012_102
HCH_012_110
HCH_012_112
```

Tổng cộng có 6 quyển không có nội dung ngữ liệu hợp lệ để xử lý.
