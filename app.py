from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# 1. Danh sách dữ liệu sách (>= 4 cuốn)
BOOKS = [
    {"id": 1, "title": "Lập trình Python cơ bản", "author": "Nguyễn Văn A", "year": 2021, "category": "Lập trình", "available": True},
    {"id": 2, "title": "Flask Web Development", "author": "Miguel Grinberg", "year": 2018, "category": "Lập trình", "available": False},
    {"id": 3, "title": "Cơ sở dữ liệu SQL", "author": "Trần Thị B", "year": 2020, "category": "Cơ sở dữ liệu", "available": True},
    {"id": 4, "title": "Nhập môn AI & Machine Learning", "author": "Lê Văn C", "year": 2023, "category": "Trí tuệ nhân tạo", "available": True}
]

# Khung HTML + CSS màu sắc phong cách sinh viên
BASE_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #f0f2f5; margin: 0; padding: 20px; color: #333; }
        .wrapper { max-width: 900px; margin: 0 auto; background: #fff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        
        /* Navbar màu sắc */
        nav { background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; }
        nav a { color: white; text-decoration: none; font-weight: bold; margin-right: 20px; transition: 0.3s; }
        nav a:hover { color: #ffdd59; }

        /* Dashboard trang chủ */
        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
        .stat-card { padding: 20px; border-radius: 8px; text-align: center; color: white; font-weight: bold; }
        .bg-blue { background: linear-gradient(135deg, #36d1dc, #5b86e5); }
        .bg-green { background: linear-gradient(135deg, #11998e, #38ef7d); }
        .stat-card h3 { margin: 0; font-size: 32px; }

        /* Thanh lọc thể loại */
        .filter-bar { margin-bottom: 15px; background: #eef2f5; padding: 10px; border-radius: 6px; }
        .btn-tag { display: inline-block; padding: 6px 12px; margin: 3px; background: #fff; color: #333; text-decoration: none; border-radius: 20px; font-size: 13px; font-weight: 500; border: 1px solid #ddd; transition: 0.2s; }
        .btn-tag:hover, .btn-tag.active { background: #ff4757; color: #fff; border-color: #ff4757; }

        /* Bảng danh sách */
        table { width: 100%; border-collapse: collapse; margin-top: 10px; overflow: hidden; border-radius: 8px; }
        th { background: #2f3542; color: white; padding: 12px; text-align: left; }
        td { padding: 12px; border-bottom: 1px solid #f1f2f6; }
        tr:hover { background-color: #f8f9fa; }
        
        /* Trạng thái */
        .badge { padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; display: inline-block; }
        .badge-success { background: #eccc68; color: #2f3542; }
        .badge-available { background: #2ed573; color: white; }
        .badge-danger { background: #ff4757; color: white; }

        /* Card chi tiết */
        .detail-card { background: #f8f9fa; border-left: 5px solid #2a5298; padding: 20px; border-radius: 6px; margin-top: 15px; }
        .detail-card p { margin: 10px 0; font-size: 16px; }
        .btn-back { display: inline-block; margin-top: 15px; padding: 8px 16px; background: #2f3542; color: white; text-decoration: none; border-radius: 5px; }
        .btn-back:hover { background: #57606f; }

        /* Thông báo 404 */
        .error-box { background: #ffeaa7; border-left: 5px solid #fdcb6e; padding: 15px; border-radius: 6px; color: #d63031; }
    </style>
</head>
<body>
    <div class="wrapper">
        <nav>
            <a href="{{ url_for('index') }}">🏠 Trang chủ</a>
            <a href="{{ url_for('book_list') }}">📚 Danh sách sách</a>
        </nav>
        {{ body | safe }}
    </div>
</body>
</html>
"""

# HTML Trang chủ
INDEX_HTML = """
<h2>📌 Thống kê thư viện</h2>
<div class="stats-grid">
    <div class="stat-card bg-blue">
        <p>Tổng số đầu sách</p>
        <h3>{{ total }}</h3>
    </div>
    <div class="stat-card bg-green">
        <p>Sách sẵn sàng mượn</p>
        <h3>{{ available }}</h3>
    </div>
</div>
"""

# HTML Danh sách sách
BOOKS_HTML = """
<h2>📚 Danh sách sách</h2>

<div class="filter-bar">
    <b>🔍 Lọc theo thể loại:</b>
    <a href="{{ url_for('book_list') }}" class="btn-tag {% if not selected_cat %}active{% endif %}">Tất cả</a>
    {% for cat in categories %}
        <a href="{{ url_for('book_list', category=cat) }}" 
           class="btn-tag {% if selected_cat.lower() == cat.lower() %}active{% endif %}">
           {{ cat | e }}
        </a>
    {% endfor %}
</div>

<table>
    <thead>
        <tr>
            <th>ID</th>
            <th>Tên sách</th>
            <th>Tác giả</th>
            <th>Năm XB</th>
            <th>Thể loại</th>
            <th>Trạng thái</th>
        </tr>
    </thead>
    <tbody>
        {% for book in books %}
        <tr>
            <td><b>#{{ book.id | e }}</b></td>
            <td><a href="{{ url_for('book_detail', book_id=book.id) }}" style="color: #1e3c72; text-decoration: none; font-weight: bold;">{{ book.title | e }}</a></td>
            <td>{{ book.author | e }}</td>
            <td>{{ book.year | e }}</td>
            <td><span class="badge badge-success">{{ book.category | e }}</span></td>
            <td>
                {% if book.available %}
                    <span class="badge badge-available">Sẵn sàng</span>
                {% else %}
                    <span class="badge badge-danger">Đã mượn</span>
                {% endif %}
            </td>
        </tr>
        {% else %}
        <tr>
            <td colspan="6" style="text-align: center; color: #a4b0be;">Không tìm thấy sách nào thuộc thể loại này.</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
"""

# HTML Chi tiết sách
DETAIL_HTML = """
<h2>📖 Thông tin chi tiết</h2>
<div class="detail-card">
    <p><b>Mã sách (ID):</b> #{{ book.id | e }}</p>
    <p><b>Tên sách:</b> <span style="color: #1e3c72; font-weight: bold;">{{ book.title | e }}</span></p>
    <p><b>Tác giả:</b> {{ book.author | e }}</p>
    <p><b>Năm xuất bản:</b> {{ book.year | e }}</p>
    <p><b>Thể loại:</b> <span class="badge badge-success">{{ book.category | e }}</span></p>
    <p><b>Trạng thái:</b> 
        {% if book.available %}
            <span class="badge badge-available">Sẵn sàng cho mượn</span>
        {% else %}
            <span class="badge badge-danger">Đã được mượn</span>
        {% endif %}
    </p>
</div>
<a href="{{ url_for('book_list') }}" class="btn-back">⬅ Quay lại danh sách</a>
"""

# HTML Lỗi 404
ERROR_404_HTML = """
<div class="error-box">
    <h3 style="margin: 0 0 10px 0;">⚠️ Lỗi 404</h3>
    <p style="margin: 0;">{{ message | e }}</p>
</div>
<a href="{{ url_for('book_list') }}" class="btn-back">⬅ Quay lại danh sách</a>
"""

def render_page(title, template, **kwargs):
    content = render_template_string(template, **kwargs)
    return render_template_string(BASE_HTML, title=title, body=content)

# 1. Trang chủ /
@app.route('/')
def index():
    total = len(BOOKS)
    available = sum(1 for b in BOOKS if b["available"])
    return render_page("Trang chủ - LibraryMS", INDEX_HTML, total=total, available=available)

# 2. Trang danh sách sách /books
@app.route('/books')
def book_list():
    selected_cat = request.args.get('category', '').strip()
    categories = list(set(b["category"] for b in BOOKS))
    
    if selected_cat:
        filtered = [b for b in BOOKS if b["category"].lower() == selected_cat.lower()]
    else:
        filtered = BOOKS
        
    return render_page("Danh sách sách", BOOKS_HTML, books=filtered, categories=categories, selected_cat=selected_cat)

# 3. Trang chi tiết sách /books/<id>
@app.route('/books/<int:book_id>')
def book_detail(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        msg = f"Không có sách với ID = {book_id}"
        return render_page("404 Not Found", ERROR_404_HTML, message=msg), 404
    return render_page(f"Chi tiết - {book['title']}", DETAIL_HTML, book=book)

# 4. Route API JSON
@app.route('/api/books')
def api_books():
    return jsonify(BOOKS)

@app.route('/api/books/<int:book_id>')
def api_book_detail(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": f"Không có sách với ID = {book_id}"}), 404
    return jsonify(book)

# Custom 404
@app.errorhandler(404)
def page_not_found(e):
    return render_page("Trang không tồn tại", ERROR_404_HTML, message="Trang bạn tìm kiếm không tồn tại."), 404

if __name__ == '__main__':
    app.run(debug=True)