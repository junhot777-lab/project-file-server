import os
from uuid import uuid4
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash

app = Flask(__name__)

# ======================
# 기본 설정
# ======================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.secret_key = "super-secret-key-change-this"  # 필요하면 바꿔도 됨

# 업로드 비밀번호 (업로드 보호용)
UPLOAD_PASSWORD = "Philia096"

# 허용 확장자 (.exe, .zip 포함)
ALLOWED_EXTENSIONS = {
    "txt", "pdf", "png", "jpg", "jpeg", "gif",
    "zip", "rar", "7z",
    "mp4", "mp3",
    "xlsx", "xls",
    "doc", "docx",
    "ppt", "pptx",
    "exe"
}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ======================
# 메인 페이지
# ======================
@app.route("/", methods=["GET"])
def index():
    files = []

    for stored_name in os.listdir(UPLOAD_FOLDER):
        if "__" in stored_name:
            _, original_name = stored_name.split("__", 1)
        else:
            original_name = stored_name

        files.append({
            "stored_name": stored_name,
            "original_name": original_name
        })

    # 최신 업로드 순으로 정렬
    files.sort(
        key=lambda f: os.path.getctime(os.path.join(UPLOAD_FOLDER, f["stored_name"])),
        reverse=True
    )

    return render_template("index.html", files=files)


# ======================
# 업로드 처리 (비번 체크 포함)
# ======================
@app.route("/upload", methods=["POST"])
def upload_file():
    # 비밀번호 검증
    password = request.form.get("password", "")
    if password != UPLOAD_PASSWORD:
        flash("❌ 비밀번호가 틀렸습니다.")
        return redirect(url_for("index"))

    if "file" not in request.files:
        flash("파일이 전송되지 않았습니다.")
        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":
        flash("선택된 파일이 없습니다.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("허용되지 않는 확장자입니다.")
        return redirect(url_for("index"))

    original_name = file.filename
    unique_name = f"{uuid4().hex}__{original_name}"
    save_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(save_path)

    flash(f"✅ 업로드 성공: {original_name}")
    return redirect(url_for("index"))


# ======================
# 다운로드
# ======================
@app.route("/download/<path:stored_name>", methods=["GET"])
def download_file(stored_name):
    return send_from_directory(
        UPLOAD_FOLDER,
        stored_name,
        as_attachment=True
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
